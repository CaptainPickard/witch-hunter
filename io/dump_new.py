#!/usr/bin/env python3
"""Emit the CURRENT tests/wh_combat_ds1_validation.py code-object dump set into
/tmp/new_dump/ in the same format as /tmp/pyc_dump/ (per code object, with
varnames + instructions), so the two dump sets can be diffed file-by-file."""
import dis
import marshal
import os

SRC = "/workspace/witch-hunter/tests/wh_combat_ds1_validation.py"
OUT = "/tmp/new_dump"

os.makedirs(OUT, exist_ok=True)
with open(SRC) as f:
    text = f.read()
root = compile(text, SRC, "exec")


def walk(co, seen):
    key = "%d_%s" % (co.co_firstlineno, co.co_name.replace("<", "_").replace(">", "_"))
    path = os.path.join(OUT, key + ".txt")
    with open(path, "w") as f:
        f.write("name=%s firstlineno=%d argcount=%d nlocals=%d\n" % (
            co.co_name, co.co_firstlineno, co.co_argcount, co.co_nlocals))
        f.write("varnames=%r\n" % (co.co_varnames,))
        for ins in dis.get_instructions(co):
            line = "%5d %-20s %s" % (ins.offset, ins.opname,
                                     "" if ins.argrepr == "" else ins.argrepr)
            if ins.opname in ("IS_OP", "CONTAINS_OP", "COMPARE_OP"):
                line = "%5d %-18s arg=%d" % (ins.offset, ins.opname, ins.arg)
            f.write(line + "\n")
    seen.append(key)
    for c in co.co_consts:
        if hasattr(c, "co_code"):
            walk(c, seen)


seen = []
walk(root, seen)
print("dumped %d files to %s" % (len(seen), OUT))
for k in seen[:5]:
    print(" ", k)