#!/usr/bin/env python3
"""Comparator v2: match frozen /tmp/pyc_dump code objects to the rebuilt
harness by (name, varnames) with order tiebreak; compare (offset, opname)
sequences positionally. Constants already verified separately."""
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
                seq.append((int(m.group(1)), m.group(2)))
        out.append({"file": ff, "name": mt.group(1), "line": int(mt.group(2)),
                    "varnames": mv.group(0) if mv else "", "seq": seq})
    return out


def new_entries():
    with open("/workspace/witch-hunter/tests/wh_combat_ds1_validation.py") as f:
        co = compile(f.read(), "harness", "exec")
    out = []

    def walk(c):
        seq = [(i.offset, i.opname) for i in dis.get_instructions(c)]
        out.append({"name": c.co_name, "varnames": repr(c.co_varnames),
                    "seq": seq, "co": c})
        for k in c.co_consts:
            if hasattr(k, "co_code"):
                walk(k)
    walk(co)
    return out


fz = frozen_entries()
nw = new_entries()
pool = list(nw)
problems = []
matched = 0
for e in fz:
    want_seq = e["seq"]
    cands = [p for p in pool if p["name"] == e["name"]
             and len(p["seq"]) == len(want_seq)]
    hit = None
    for p in cands:
        if p["seq"] == want_seq:
            hit = p
            break
    if hit is None and cands:
        # show first diff for closest candidate
        p = cands[0]
        for a, b in zip(e["seq"], p["seq"]):
            if a != b:
                problems.append("SEQ DIFF %s: frozen@%d %s vs new@%d %s" % (
                    e["file"], a[0], a[1], b[0], b[1]))
                break
        pool.remove(p)
        continue
    if hit is None:
        problems.append("NO MATCH for %s (name=%s len=%d)" % (
            e["file"], e["name"], len(want_seq)))
        continue
    pool.remove(hit)
    matched += 1
leftover = [(p["name"], len(p["seq"])) for p in pool]
print("frozen=%d matched=%d leftover_new=%s" % (len(fz), matched, leftover))
for p in problems:
    print(p)
print("PROBLEMS=%d" % len(problems))