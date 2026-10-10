#!/usr/bin/env python3
"""Structured disassembly of the harness .pyc (code objects only, no strings)."""
import dis, marshal, importlib.util, sys

path = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
with open(path, "rb") as f:
    f.read(16)  # 3.12 header is 16 bytes
    code = marshal.load(f)

def walk(c, depth=0):
    co = c.co_code
    consts = [x for x in c.co_consts if hasattr(x, "co_code")]
    print("  " * depth + "%s (def at line %d, %d consts, %d instrs)" % (
        c.co_name, c.co_firstlineno, len(c.co_consts), len(co) // 2))
    for k in consts:
        walk(k, depth + 1)

print("module co_firstlineno=%d" % code.co_firstlineno)
names = [x.co_name for x in code.co_consts if hasattr(x, "co_code")]
print("top-level defs found:", names)

walk(code)

# locate the last function code object and dis assemble its tail
def find_last(c):
    best = c
    for k in [x for x in c.co_consts if hasattr(x, "co_code")]:
        cand = find_last(k)
        if cand.co_firstlineno >= best.co_firstlineno:
            # prefer highest line
            if cand.co_firstlineno > best.co_firstlineno or (
                    cand.co_firstlineno == best.co_firstlineno):
                best = cand
    return best

last = find_last(code)
print("\n=== LAST code object: %s firstlineno=%d" % (last.co_name, last.co_firstlineno))
dis.dis(last)
print("\n=== MODULE TAIL BYTECODE (last 60 instrs) ===")
insns = list(dis.get_instructions(code))
for i in insns[-60:]:
    print("%5d %-22s %s" % (i.offset, i.opname, i.argrepr))