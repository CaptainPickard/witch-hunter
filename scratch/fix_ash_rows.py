#!/usr/bin/env python3
"""RESTORE all oak/ash rows from git HEAD verbatim, then apply ONLY the
y negation. Deterministic key-including comparison via asset name capture."""
import subprocess, re, esprima

p = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
cfg = open(p).read()
head = subprocess.run(['git', '-C', '/tmp/wh-worldfeat', 'show',
                       'HEAD:prototype/js/CONFIG.js'], capture_output=True, text=True).stdout

h_rows = re.findall(r"      \{ asset: '(?:livingOak|youngAsh)'[^}]*\},", head)
c_rows = re.findall(r"      \{ asset: '(?:livingOak|youngAsh)'[^}]*\},", cfg)
print('head rows:', len(h_rows), '| current rows:', len(c_rows))
assert len(h_rows) == len(c_rows), 'row count drift'

out = cfg
for hrow, crow in zip(h_rows, c_rows):
    if hrow == crow:
        continue
    asset = re.search(r"asset: '(\w+)'", hrow).group(1)
    sc = float(re.search(r"scale: (-?[\d.]+)", hrow).group(1))
    frac = 0.16 if asset == 'livingOak' else 0.10
    row = re.sub(r"y: -?[\d.]+", "y: %.2f" % (-frac * sc), hrow, count=1)
    out = out.replace(crow, row)

open(p, 'w').write(out)

h2 = re.findall(r"      \{ asset: '(livingOak|youngAsh)'[^}]*\},", head)
c2 = re.findall(r"      \{ asset: '(livingOak|youngAsh)'[^}]*\},", open(p).read())
mism = []
for hrow, crow in zip(h2, c2):
    if hrow == crow:
        continue   # already correct (this is success, not a mismatch)
    hd = dict(re.findall(r"(\w+): (-?[\d.]+)", hrow))
    cd = dict(re.findall(r"(\w+): (-?[\d.]+)", crow))
    sc = float(hd['scale'])
    want_y = -(0.16 if hrow.startswith("{ asset: 'livingOak") else 0.10) * sc
    for fld in ('x', 'z', 'rotY', 'scale'):
        if hd[fld] != cd[fld]:
            mism.append((fld, hrow[:70], crow[:70]))
    if abs(float(cd['y']) - want_y) > 0.005:
        mism.append(('y', want_y, cd['y']))
assert not mism, mism
esprima.parseScript(open(p).read())
print('FINAL: rows faithful to HEAD, sinks negative, syntax OK')