#!/usr/bin/env python3
"""Debug: compare hp() frozen dump vs fresh disassembly side by side."""
import dis

with open("/workspace/witch-hunter/tests/wh_combat_ds1_validation.py") as f:
    co = compile(f.read(), "harness", "exec")

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

h = find("hp")
print("FRESH hp:")
for i in dis.get_instructions(h):
    print("%5d %s" % (i.offset, i.opname))