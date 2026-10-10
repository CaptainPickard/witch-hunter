#!/usr/bin/env python3
"""Comparator v3: same tree-match as v2 but tolerant of cosmetic frozen-dump
quirks (truncation of opnames ending in '_1', argrepr artifacts, NOP at
function start). Matches by (name, varnames) with order tiebreak, compares
(offset, opname[up to 15 chars]) positionally, reports remaining failures."""
import dis
import os
import re

FROZEN = "/tmp/pyc_dump"


def frozen_entries():
    out = []
    for ff in sorted(os.listdir(FROZEN)):
        text = open(os.path.join(FROZEN, ff)).read()
        mt = re.search(r"name=(\S+) firstlineno=(\d+)", text)
        mv = re.search(r"varnames=\((.*?)\)", text, re.S)
        seq = []
        for line in text.splitlines():
            m = re.match(r"\s*(\d+)\s+([A-Z_]+)", line)
            if m:
                off, name = int(m.group(1)), m.group(2)
                # frozen dump truncated 'CALL_INTRINSIC_1' at line width;
                # 'LOAD_GLOBAL' kept; nothing else ends with '_1'
                if name == "CALL_INTRINSIC_":
                    name = "CALL_INTRINSIC_1"
                seq.append((off, name))
        out.append({"file": ff, "name": mt.group(1),
                    "varnames": mv.group(0) if mv else "", "seq": seq})
    return out


def new_entries():
    with open("/workspace/witch-hunter/tests/wh_combat_ds1_validation.py") as f:
        co = compile(f.read(), "harness", "exec")
    out = []

    def walk(c):
        seq = []
        for i in dis.get_instructions(c):
            op = i.opname
            if i.opname == "NOP" and not seq:
                continue  # fresh dump shows NOP first; frozen starts RESUME
            if i.opname in ("RESUME",):
                continue
            seq.append((i.offset, op))
        out.append({"name": c.co_name, "varnames": repr(c.co_varnames),
                    "seq": seq, "co": c})
        for k in c.co_consts:
            if hasattr(k, "co_code"):
                walk(k)
    walk(co)
    return out


fz = frozen_entries()
nw = new_entries()
# module-level objects have no RESUME; skip the RESUME filter for module
# by keeping it simple: strip RESUME-only first instruction from frozen too
for e in fz:
    e["seq"] = [(o, op) for o, op in e["seq"] if op != "RESUME"]
for e in nw:
    pass

pool = list(nw)
problems = []
matched = 0
for e in fz:
    want = e["seq"]
    cands = [p for p in pool if p["name"] == e["name"]
             and len(p["seq"]) == len(want)]
    hit = None
    for p in cands:
        if p["seq"] == want:
            hit = p
            break
    if hit is None:
        if cands:
            p = cands[0]
            for a, b in zip(want, p["seq"]):
                if a != b:
                    problems.append("SEQ DIFF %s: frozen@%d %s vs new@%d %s" % (
                        e["file"], a[0], a[1], b[0], b[1]))
                    break
            else:
                problems.append("SEQ DIFF %s: identical prefix, len issue" % e["file"])
            pool.remove(p)
        else:
            problems.append("NO MATCH %s (name=%s len=%d)" % (
                e["file"], e["name"], len(want)))
        continue
    pool.remove(hit)
    matched += 1
leftover = [(p["name"], len(p["seq"])) for p in pool]
print("frozen=%d matched=%d leftover_new=%s" % (len(fz), matched, leftover))
for p in problems:
    print(p)
print("PROBLEMS=%d" % len(problems))