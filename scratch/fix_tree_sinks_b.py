#!/usr/bin/env python3
"""Flip inverted sinks region B (y before z, feat 23-row swap format)."""
import re, esprima

p = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
cfg = open(p).read()

def rescale_sink(m):
    asset, y, x, rot, z, sc = m.groups()
    sc = float(sc)
    frac = 0.16 if asset == 'livingOak' else 0.10
    sink = -frac * sc
    return ("      { asset: '%s', y: %s, x: %s, rotY: %s, z: %s, scale: %s }," %
            (asset, ('%.2f' % sink), x, rot, z, '%.2f' % sc))

pat = re.compile(
    r"      \{ asset: '(livingOak|youngAsh)', y: (-?[\d.]+), x: (-?[\d.]+), rotY: (-?[\d.]+), z: (-?[\d.]+), scale: (-?[\d.]+) \},")
n = len(pat.findall(cfg))
cfg = pat.sub(rescale_sink, cfg)
open(p, 'w').write(cfg)
print('regionB rows fixed:', n)
bad = re.findall(r"\{ asset: '(livingOak|youngAsh)'[^}]*y: (?!-)[\d.]+", cfg)
assert not bad, 'positive sinks remain: %s' % bad
print('no positive sinks remain OK')
esprima.parseScript(open(p).read())
print('syntax OK')