#!/usr/bin/env python3
"""Precise per-object diff between frozen /tmp/pyc_dump listings and fresh
disassembly of the rebuilt harness. Matches by (name, varnames, instr count,
order tiebreak). Reports aligned replace/delete/insert blocks via difflib on
(offset, opname) tuples. Output to /tmp/cocode_diff.txt."""
import dis
import difflib
import os
import re

FROZEN = "/tmp/pyc_dump"
OUT = "/tmp/cocode_diff.txt"
TRUNC = {"CALL_INTRINSIC_": "CALL_INTRINSIC_1"}


def frozen_entries():
    out = []
    for ff in sorted(os.listdir(FROZEN)):
        text = open(os.path.join(FROZEN, ff)).read()
        mt = re.search(r"name=(\S+) firstlineno=(\d+)", text)
        mv = re.search(r"varnames=\((.*?)\)(?:\n|$)", text, re.S)
        seq = []
        for line in text.splitlines():
            m = re.match(r"\s*(\d+)\s+([A-Z_]+)", line)
            if m:
                op = TRUNC.get(m.group(2), m.group(2))
                seq.append((int(m.group(1)), op))
        out.append({"file": ff, "name": mt.group(1),
                    "varnames": mv.group(0) if mv else "?",
                    "seq": seq})
    return out


def new_entries():
    with open("/workspace/witch-hunter/tests/wh_combat_ds1_validation.py") as f:
        co = compile(f.read(), "harness", "exec")
    out = []

    def walk(c):
        seq = []
        for i in dis.get_instructions(c):
            if i.opname == "RESUME":
                continue
            if i.opname == "NOP" and not seq:
                continue
            seq.append((i.offset, TRUNC.get(i.opname, i.opname)))
        out.append({"name": c.co_name, "varnames": repr(c.co_varnames),
                    "seq": seq})
        for k in c.co_consts:
            if hasattr(k, "co_code"):
                walk(k)
    walk(co)
    return out


lines = []
fz = frozen_entries()
nw = new_entries()
pool = list(nw)
matched, problems = 0, []
for e in fz:
    cands = [p for p in pool if p["name"] == e["name"]
             and len(p["seq"]) == len(e["seq"])
             and p["varnames"].replace(" ", "") == e["varnames"].replace(" ", "")]
    hit = next((p for p in cands if p["seq"] == e["seq"]), None)
    if hit is not None:
        pool.remove(hit)
        matched += 1
        continue
    tag = "%s [%s]" % (e["file"], e["name"])
    if not cands:
        loose = [p for p in pool if p["name"] == e["name"]]
        if loose:
            cands = [min(loose, key=lambda p: abs(len(p["seq"]) - len(e["seq"])))]
        else:
            problems.append("NO OBJECT AT ALL: %s" % tag)
            continue
    p = cands[0]
    pool.remove(p)
    sm = difflib.SequenceMatcher(a=e["seq"], b=p["seq"], autojunk=False)
    lines.append("=== %s frozen=%d new=%d ===" % (tag, len(e["seq"]), len(p["seq"])))
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            continue
        lines.append("  %s frozen[%d:%d] vs new[%d:%d]" % (op, a1, a2, b1, b2))
        for t in e["seq"][a1:a2]:
            lines.append("    F %5d %s" % t)
        for t in p["seq"][b1:b2]:
            lines.append("    N %5d %s" % t)
open(OUT, "w").write("\n".join(lines) + "\n")
leftover = [(p["name"], len(p["seq"])) for p in pool]
print("frozen=%d matched=%d leftover_new=%s" % (len(fz), matched, leftover))
for p in problems:
    print("PROBLEM:", p)
print("diff blocks written:", len(lines), "lines ->", OUT)