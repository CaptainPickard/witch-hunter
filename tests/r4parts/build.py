"""Assemble the R4 harness build artifact (HANDOFF law 8): byte-for-byte
`cat tests/r4parts/part01.py .. part08.py > tests/wh_world_r4_validation.py`,
then py_compile + shadowed-duplicate-def check.
Usage: python3 tests/r4parts/build.py"""
import os
import py_compile
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "wh_world_r4_validation.py")
buf = b""
for i in range(1, 9):
    with open(os.path.join(HERE, "part%02d.py" % i), "rb") as f:
        buf += f.read()
with open(OUT, "wb") as f:
    f.write(buf)
py_compile.compile(OUT, doraise=True)
names = re.findall(r"^def ([A-Za-z0-9_]+)", buf.decode(), re.M)
dups = sorted({n for n in names if names.count(n) > 1})
if dups:
    print("DUPLICATE DEFS: %s" % dups)
    sys.exit(1)
print("assembled %d bytes, compiled OK, no duplicate defs" % len(buf))
