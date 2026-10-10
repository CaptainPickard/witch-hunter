#!/usr/bin/env python3
"""Print opname + RAW ARG for IS_OP, CONTAINS_OP, COMPARE_OP, LOAD_FAST_CHECK
occurrences in every code object of the frozen harness pyc."""
import dis, marshal

path = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
with open(path, "rb") as f:
    f.read(16)
    code = marshal.load(f)

WANT = {"IS_OP", "CONTAINS_OP", "LOAD_FAST_CHECK"}


def walk(c, path_name):
    out = []
    for i in dis.get_instructions(c):
        if i.opname in WANT:
            out.append("  off=%d %s arg=%s argrepr=%r" % (i.offset, i.opname, i.argval, i.argrepr))
    if out:
        print("== %s" % path_name)
        for o in out:
            print(o)
    for k in c.co_consts:
        if hasattr(k, "co_code"):
            walk(k, path_name + "/" + k.co_name)


walk(code, "module")