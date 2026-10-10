#!/usr/bin/env python3
"""
Compare the 60 frozen per-code-object dumps (/tmp/pyc_dump) with fresh
disassembly of the rebuilt harness, matching function-by-FUNCTION (nested code
tree order + varnames identity), not by firstlineno filename key.

Frozen instruction text (from /tmp/pyc_dump files) has COMPARE_OP printed with
symbolic name (==, <=, ...) while fresh dis prints the raw arg; both are
normalized here to (opname, opname) pairs so only the OPERATION ORDER is
compared positionally, plus argvals where both formats carry them.
"""
import dis
import os
import re

FROZEN = "/tmp/pyc_dump"
NEW = "/tmp/new_dump"


def norm_frozen(text):
    seq = []
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\s+([A-Z_]+)\s*(.*)$", line)
        if not m:
            continue
        off, op, rest = int(m.group(1)), m.group(2), m.group(3).strip()
        seq.append((off, op, rest))
    return seq


def norm_new(text):
    seq = []
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\s+([A-Z_]+)\s*(.*)$", line)
        if not m:
            continue
        off, op, rest = int(m.group(1)), m.group(2), m.group(3).strip()
        # normalize COMPARE_OP forms: frozen kept '==', new dumps keep raw arg
        if op == "COMPARE_OP":
            rest = rest if rest and not rest[0].isdigit() else rest
        seq.append((off, op, rest))
    return seq


def load_new_tree():
    """Fresh nested code tree from the rebuilt source."""
    with open("/workspace/witch-hunter/tests/wh_combat_ds1_validation.py") as f:
        co = compile(f.read(), "harness", "exec")
    tree = []

    def walk(c):
        tree.append(c)
        for k in c.co_consts:
            if hasattr(k, "co_code"):
                walk(k)

    walk(co)
    return tree


def func_key(co):
    return (co.co_argcount, co.co_nlocals, co.co_varnames)


frozen_files = sorted(os.listdir(FROZEN))
new_tree = load_new_tree()
used = set()
problems = []
for ff in frozen_files:
    text = open(os.path.join(FROZEN, ff)).read()
    fseq = norm_frozen(text)
    fvar_match = re.search(r"varnames=\((.*?)\)", text)
    fvar = fvar_match.group(0) if fvar_match else ""
    farg = int(re.search(r"argcount=(\d+)", text).group(1))
    fnloc = int(re.search(r"nlocals=(\d+)", text).group(1))
    # candidate new co: same (argcount, nlocals) and instruction count
    cands = []
    for c in new_tree:
        if id(c) in used:
            continue
        nseq = [(i.offset, i.opname) for i in dis.get_instructions(c)]
        if len(nseq) == len(fseq) and c.co_argcount == farg and c.co_nlocals == fnloc:
            cands.append(c)
    matched = None
    score = None
    for c in cands:
        fs = [(o, op) for o, op, _ in fseq]
        ns = [(i.offset, i.opname) for i in dis.get_instructions(c)]
        same = sum(1 for a, b in zip(fs, ns) if a == b)
        if score is None or same > score:
            score = same
            matched = c
    if matched is None:
        problems.append("NO CANDIDATE for %s (len=%d)" % (ff, len(fseq)))
        continue
    used.add(id(matched))
    ns = [(i.offset, i.opname, "" if i.argrepr == "" else i.argrepr)
          for i in dis.get_instructions(matched)]
    diffs = []
    for a, b in zip(fseq, ns):
        if a[0] != b[0] or a[1] != b[1]:
            diffs.append((a, b))
            break
        # arg compare: skip LOAD_CONST code-object reprs and LOAD_GLOBAL NULL
        if a[2] != b[2] and not (a[2].startswith("<code") or b[2].startswith("<code")):
            # offset reprs and closures differ in format; compare loosely
            if not (a[1] in ("LOAD_GLOBAL",) and a[2].startswith("NULL")
                    and str(b[2]).startswith("NULL")):
                diffs.append((a, b))
                break
    if diffs:
        problems.append("SEQ DIFF %s: frozen=%s new=%s" % (ff, diffs[0][0], diffs[0][1]))
unused = [c.co_name for c in new_tree if id(c) not in used and c.co_name != "<module>"]
print("frozen=%d  matched=%d  unused_new=%s" % (
    len(frozen_files), len(used), unused))
for p in problems:
    print(p)
print("PROBLEMS=%d" % len(problems))