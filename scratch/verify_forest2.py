#!/usr/bin/env python3
"""Verify order 3 + wiring in the worktree (static analysis + geometry)."""
import re, math, esprima

cfg = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
am = open('/tmp/wh-worldfeat/prototype/js/assets.js').read()
ok = lambda c, msg: print(('PASS ' if c else 'FAIL ') + msg)

esprima.parseScript(cfg); esprima.parseScript(am)
print('esprima OK')

ra = cfg[cfg.index('regionA: {'):cfg.index('regionB: {')]
rb = cfg[cfg.index('regionB: {'):cfg.index('boundary: {')]

# species counts
def count(span, asset):
    return len(re.findall(r"asset: '%s'" % asset, span))
print('A yew=%d oak=%d witch=%d ash=%d dead=%d' % (
    count(ra, 'yewTree'), count(ra, 'livingOak'), count(ra, 'witchwoodTree'),
    count(ra, 'youngAsh'), count(ra, 'deadTree')))
print('B yew=%d oak=%d witch=%d dead=%d' % (
    count(rb, 'yewTree'), count(rb, 'livingOak'), count(rb, 'witchwoodTree'),
    count(rb, 'deadTree')))

# parse all props of region A, check: none inside yard polygon; enemies count
rows = re.findall(r"\{ asset: '(\w+)', x: (-?[\d.]+), (?:y: (-?[\d.]+), )?z: (-?[\d.]+), rotY: (-?[\d.]+), scale: ([\d.]+)", ra)
def in_yard(x, z):
    if -1 <= z <= 24 and abs(x) <= 21: return True
    if 24 < z <= 32.5 and abs(x) <= 4: return True
    return False
trees = [r for r in rows if r[0] in ('yewTree', 'livingOak', 'witchwoodTree', 'youngAsh', 'deadTree')]
viol = [t for t in trees if in_yard(float(t[1]), float(t[3]))]
ok(not viol, 'no trees inside graveyard (%d tree rows scanned)' % len(trees))
sinkbad = [t for t in rows if t[0] in ('livingOak', 'youngAsh') and not t[2]]
ok(not sinkbad, 'all oak/ash rows carry y-sink')
print('y-sink examples:', [r[2] for r in rows if r[0] == 'livingOak'][:3])

en = re.findall(r"\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+) \}", ra)
print('regionA enemies: %d' % len(en))
ok(len(en) == 11, 'enemy count 3+8=11')

lan = re.findall(r"\{ asset: 'lanternPost', x: (-?[\d.]+), z: (-?[\d.]+)", ra)
lan_zs = sorted(float(z) for _, z in lan)
ok(sorted(lan_zs) == [-2.0, 30.0, 39.5, 51.0, 62.0],
   'lanterns = path-span chain + 2 canon yard posts: %s' % lan_zs)

dp = re.search(r'dirtPath: \{[^}]*\}', cfg, re.S).group(0)
ok("zTo: 32.0" in dp, 'dirtPath ends at yard fence (zTo 32.0)')

# manifest paths exist on disk
import os
missing = []
for name, path in re.findall(r"(\w+): 'art-direction/([^']+\.glb)'", am):
    if not os.path.exists('/tmp/wh-worldfeat/art-direction/' + path):
        missing.append((name, path))
ok(not missing, 'manifest GLB paths exist on disk (%s)' % (missing or 'clean'))