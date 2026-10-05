#!/usr/bin/env python3
"""Flip the inverted oak/ash ground-sink signs (Nicko 10-04 tree float report).
Positive y LIFTS (buildRegion: position.y = p.y) - sinks must be NEGATIVE.
Per-row sink = -0.16 x scale (oak, trunk-base holes) / -0.10 x scale (ash)."""
import re

p = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
cfg = open(p).read()

def rescale_sink(m):
    asset, x, z, rot, sc, y = m.groups()
    sc = float(sc)
    frac = 0.16 if asset == 'livingOak' else 0.10
    sink = -frac * sc
    return ("      { asset: '%s', x: %s, y: %s, z: %s, rotY: %s, scale: %s }," %
            (asset, x, ('%.2f' % sink), z, rot, '%.2f' % sc))

pat = re.compile(
    r"      \{ asset: '(livingOak|youngAsh)', x: (-?[\d.]+), y: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+) \},")
rows, n = [], 0
for m in pat.finditer(cfg):
    rows.append((m.group(1), m.group(3)))
    n += 1
cfg = pat.sub(rescale_sink, cfg)
open(p, 'w').write(cfg)
print('sink rows fixed:', n, rows[:4])
bad = re.findall(r"\{ asset: '(livingOak|youngAsh)'[^}]*y: (\d[\d.]*)", cfg)
assert not bad, 'positive sinks remain: %s' % bad
print('no positive sinks remain OK')
import subprocess
print(subprocess.run(['python3', '-c', 'import esprima; esprima.parseScript(open("%s").read()); print("syntax OK")' % p],
                     capture_output=True, text=True).stdout.strip())