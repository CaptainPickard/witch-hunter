#!/usr/bin/env python3
"""Dump DISASSEMBLY ONLY (code objects + instructions) of every code object in
the frozen harness pyc into per-function files under /tmp/pyc_dump/.

NO string/numeric constants are dumped (string-only policy for reading).
"""
import dis, marshal, os

path = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
with open(path, "rb") as f:
    f.read(16)
    code = marshal.load(f)

outdir = "/tmp/pyc_dump"
os.makedirs(outdir, exist_ok=True)


def dump(c, stack="module"):
    fn = os.path.join(outdir, "%s_%s.txt" % (c.co_firstlineno, c.co_name.replace('<', '_').replace('>', '_')))
    with open(fn, "w") as f:
        f.write("name=%s firstlineno=%d argcount=%d nlocals=%d\n" % (
            c.co_name, c.co_firstlineno, c.co_argcount, c.co_nlocals))
        f.write("varnames=%r\n" % (c.co_varnames,))
        for i in dis.get_instructions(c):
            f.write("%5d %-20s %s\n" % (i.offset, i.opname, i.argrepr))
    for k in c.co_consts:
        if hasattr(k, "co_code"):
            dump(k, stack + "/" + k.co_name)


dump(code)
print("dumped", len(os.listdir(outdir)), "files to", outdir)