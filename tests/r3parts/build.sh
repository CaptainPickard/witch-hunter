#!/bin/sh
# Assemble the R3 harness build artifact from its parts (HANDOFF law 8:
# edit parts, re-cat, check shadowed duplicate defs before every run).
set -e
cd "$(dirname "$0")/../.."
cat tests/r3parts/part01.py tests/r3parts/part02.py tests/r3parts/part03.py \
    tests/r3parts/part04.py tests/r3parts/part05.py tests/r3parts/part06.py \
    tests/r3parts/part07.py tests/r3parts/part08.py tests/r3parts/part09.py \
    tests/r3parts/part10.py > tests/wh_world_r3_validation.py
python3 -m py_compile tests/wh_world_r3_validation.py
dups=$(grep -oE '^def [A-Za-z0-9_]+' tests/wh_world_r3_validation.py | sort | uniq -d)
if [ -n "$dups" ]; then echo "DUPLICATE DEFS: $dups"; exit 1; fi
echo "assembled + compiled OK, no duplicate defs"
