#!/usr/bin/env python3
"""Flip ALL remaining positive oak/ash sinks regardless of key order."""
import re, esprima

p = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
cfg = open(p).read()

pat = re.compile(r"\{ asset: '(livingOak|youngAsh)'([^}]*)\}")
def fix(m):
    asset, rest = m.group(1), m.group(2)
    sc = float(re.search(r"scale: (-?[\d.]+)", rest).group(1))
    frac = 0.16 if asset == 'livingOak' else 0.10
    sink = -frac * sc
    # replace only the y: value, keep everything else byte-identical
    rest2, n = re.subn(r"y: -?[\d.]+", "y: %.2f" % sink, rest, count=1)
    if n == 0:  # no y at all -> insert one
        rest2 = " y: %.2f," % sink + rest2
    return "{ asset: '%s'%s}" % (asset, rest2)

cfg2, nn = pat.subn(fix, cfg)
open(p, 'w').write(cfg2)
print('rows matched:', nn)
bad = re.findall(r"\{ asset: '(livingOak|youngAsh)'[^}]*y: (?=-)", cfg2)
assert not bad, 'positive remain'
esprima.parseScript(open(p).read())
print('all sinks negative, syntax OK')