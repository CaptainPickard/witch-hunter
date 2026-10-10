#!/usr/bin/env python3
"""Assemble the rebuilt harness from numbered part files (their *_PART strings,
in order) and write tests/wh_combat_ds1_validation.py. Run once via terminal."""
import re
import sys

# io/rebuild_part1.py is the direct header source (not a string holder); others
# carry the payload in a ''' block.
SPECIALS = {"io/rebuild_part1.py"}
PARTS = ["io/rebuild_part2.py", "io/rebuild_part3a.py",
         "io/rebuild_part3b.py", "io/rebuild_part3c.py", "io/rebuild_part4.py",
         "io/rebuild_part5a.py", "io/rebuild_part5b.py", "io/rebuild_part5c.py",
         "io/rebuild_part5d.py", "io/rebuild_part6.py", "io/rebuild_part7.py"]
OUT = "tests/wh_combat_ds1_validation.py"


def extract_direct(path):
    src = open(path).read()
    # skip the module docstring, take the rest verbatim minus trailing marker
    m = re.search(r'"""Witch Hunter.*?"""\n', src, re.S)
    if not m:
        raise SystemExit("bad header %s" % path)
    return src[m.end():].replace(
        "\n# --- placeholder: remainder restored in next chunks ---\n", "\n")


def extract(path):
    src = open(path).read()
    m = re.search(r"'''(.*?)'''", src, re.S)
    if not m:
        raise SystemExit("no triple-single-quoted block in %s" % path)
    return m.group(1)


chunks = [extract_direct("io/rebuild_part1.py")]
chunks += [extract(p) for p in PARTS]
body = "\n\n".join(chunks).rstrip() + "\n"
open(OUT, "w").write(body)
print("wrote %s: %d lines, %d chars" % (OUT, body.count("\n") + 1, len(body)))