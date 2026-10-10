"""IO harness-repair: replace the mangled sampler boundary with a clean
single window-buffer rAF sampler. Idempotent and self-verifying."""
import hashlib
import pathlib
import re

P = pathlib.Path('/workspace/witch-hunter/tests/wh_combat_ds1_validation.py')
t = P.read_text()
lines = t.split('\n')
lo = 268
hi = min(len(lines), 272)
for i in range(lo, hi):
    print(i, '>', lines[i])
print('TOTAL', len(lines))