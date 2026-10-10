#!/usr/bin/env python3
"""Reconstruct the frozen module layout from the .pyc.

Prints, for the module code object:
  A. every string constant (module-level) in order
  B. every string constant inside EVERY code object, prefixed by its owner
so we can see which lines the D2 sampler edits touched and in what order.
"""
import dis, marshal

path = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
with open(path, "rb") as f:
    f.read(16)
    code = marshal.load(f)


def strings_of(c, prefix=""):
    out = []
    for k in c.co_consts:
        if isinstance(k, str):
            s = k if len(k) <= 95 else k[:92] + "..."
            out.append("%s%r" % (prefix, s.replace("\n", " | ")))
        elif hasattr(k, "co_code"):
            out.extend(strings_of(k, prefix + "  [" + k.co_name + "] "))
    return out


print("=== A) MODULE-LEVEL string constants ===")
for s in strings_of(code):
    print(s)

print("\n=== B) MODULE bytecodes (all) ===")
for i in dis.get_instructions(code):
    print("%5d %-20s %s" % (i.offset, i.opname, i.argrepr))