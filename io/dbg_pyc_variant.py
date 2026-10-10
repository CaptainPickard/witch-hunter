#!/usr/bin/env python3
"""Identify the frozen pyc variant: read the CURRENT pyc's embedded filename +
mtime header, and compare against what we know (current pyc = 16:02 rebuild).
Also parse /tmp/pyc_dump/75_wait_ready.txt structure vs the fresh wait_ready to
see exactly where they diverge (try/except layout)."""
import dis
import marshal
import re
import struct
import time

PYC = "/workspace/witch-hunter/tests/__pycache__/wh_combat_ds1_validation.cpython-312.pyc"
with open(PYC, "rb") as f:
    data = f.read()
magic = data[:4]
flags = struct.unpack("<I", data[4:8])[0]
stamp = struct.unpack("<I", data[8:12])[0]
root = marshal.loads(data[16:])
print("pyc filename:", root.co_filename)
print("pyc header stamp:", time_str(stamp) if False else stamp,
      "=", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(stamp)))

# fresh wait_ready instructions
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


wr = find("wait_ready")
print("\nFRESH wait_ready count:", len(list(dis.get_instructions(wr))))
frozen = open("/tmp/pyc_dump/75_wait_ready.txt").read()
fcount = len([l for l in frozen.splitlines()
              if re.match(r"\s*\d+ [A-Z]", l)])
print("FROZEN wait_ready instr count:", fcount)