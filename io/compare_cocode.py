#!/usr/bin/env python3
"""co_code comparison: compile the rebuilt harness from disk and compare each
nested code object byte-for-byte with the frozen pyc.

Usage: python3 io/compare_cocode.py
Prints OK/MISMATCH per function with the first differing offset."""
import marshal
import dis

SRC = "/workspace/witch-hunter/tests/wh_combat_ds1_validation.py"
PYC = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"


def load_frozen():
    with open(PYC, "rb") as f:
        f.read(16)
        return marshal.load(f)


def collect(obj, out=None):
    if out is None:
        out = {}
    if hasattr(obj, "co_consts"):
        for c in obj.co_consts:
            if hasattr(c, "co_code"):
                collect(c, out)
    out[obj.co_name + "@" + str(obj.co_firstlineno)] = obj
    return out


def main():
    frozen = collect(load_frozen())
    with open(SRC, "r") as f:
        text = f.read()
    rebuilt = collect(compile(text, SRC, "exec"))
    ok = True
    for key in sorted(frozen):
        fz = frozen[key]
        rb = rebuilt.get(key)
        if rb is None:
            print("MISSING in rebuild: %s" % key)
            ok = False
            continue
        if rb.co_code != fz.co_code:
            a = dis.get_instructions(fz)
            b = dis.get_instructions(rb)
            diff = None
            for ia, ib in zip(a, b):
                if ia.opname != ib.opname or ia.argval != ib.argval:
                    diff = (ia.offset, ia.opname, ia.argval,
                            ib.opname, ib.argval)
                    break
            print("MISMATCH %s  frozen@%s rebuilt@%s" % (
                key, diff[1:4] if diff else "?", diff[4:]))
            ok = False
    if ok:
        print("ALL CO_CODE IDENTICAL (%d code objects)" % len(frozen))
    return 0 if ok else 1


if __name__ == "__main__":
    sys_exit = main()
    raise SystemExit(sys_exit)