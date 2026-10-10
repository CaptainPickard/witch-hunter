#!/usr/bin/env python3
"""Answer the ac_a1_4 question from source (frozen pyc gone):
is `have` (comprehension over offsets, skipping falsy `o`) CELL or LOCAL
in the rebuild? And confirm MAKE_CELL presence in the preserved dump."""
import re
import dis

src = open("/workspace/witch-hunter/tests/wh_combat_ds1_validation.py").read()
co = compile(src, "harness", "exec")
def find(name):
    def walk(c):
        if c.co_name == name:
            return c
        for k in c.co_consts:
            if hasattr(k, "co_code"):
                r = walk(k)
                if r is not None:
                    return r
    return walk(co)
a14 = find("ac_a1_4")
print("ac_a1_4 in rebuild:")
print("  cellvars =", a14.co_cellvars)
print("  freevars =", a14.co_freevars)
print("  varnames =", a14.co_varnames)
print("  nlocals  =", a14.co_nlocals)
# frozen facts from preserved dump
txt = open("/tmp/pyc_dump/496_ac_a1_4.txt").read()
print("frozen dump: nlocals=%s" % re.search(r"nlocals=(\d+)", txt).group(1))
print("frozen MAKE_CELL lines:", [l.strip() for l in txt.splitlines() if "MAKE_CELL" in l])
print("frozen cellvar STOREs mentioned in dump:",
      [l.strip() for l in txt.splitlines() if "STORE_DEREF" in l])
print("frozen LOAD_DEREF targets:", sorted(set(
    l.strip().split()[-1] for l in txt.splitlines() if "LOAD_DEREF" in l)))