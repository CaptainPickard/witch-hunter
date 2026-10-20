#!/usr/bin/env python3
"""CC-C17v2 step 6 LEDGER (v2 brief): the region-C 2M drawn-tri worst case at BOTH
probe centres (0,-366) and (-175,-266), R 170, 2 m grid - PASS = both <= 1,980,000.
Engine = scratch/cc-c17/ledger2_probe.js (the CC-C8 repo-stub probe: window stub +
three.classic + CONFIG + wh-ground + region-defs + region-manager, real
WH_ScatterPlan cells) with the tri table extended by the 4 C13b kit rows the C8
table missed (churchArchway 4000 / churchCornerButtress 2000 / stoneSteps 5000 /
stoneCrossTilted 4000) and the 10 CC-C17 assets at max(IO table, GLB header).
Also prints a whole-disc scan (R 280) and the CC-C17 added-row tally.
usage: python3 scratch/cc-c17/ledger2.py [repoRoot]"""
import json, subprocess, sys, os, re
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '/tmp/wh-worldfeat')
HERE = os.path.dirname(os.path.abspath(__file__))
CAP = 1980000
def run(lx, lz, r):
    return json.loads(subprocess.check_output(['node', os.path.join(HERE, 'ledger2_probe.js'), ROOT, str(lx), str(lz), str(r)]))
src = open(os.path.join(HERE, 'ledger2_probe.js')).read()
T = {k: int(v) for k, v in re.findall(r'"?(\w+)"?: (\d{3,})', src[src.index('const T = {'):src.index('const M = {')])}
cfg = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'dump_cfg.js'), ROOT]))
cfgsrc = open(os.path.join(ROOT, 'prototype/js/CONFIG.js')).read()
# the C17 block = every regionC row appended after the C16b fires
props = cfg['props']; i0 = max(i for i, p in enumerate(props) if p['asset'] == 'banditCampfire') + 1
c17 = props[i0:]
tally = {}
for p in c17: tally[p['asset']] = tally.get(p['asset'], 0) + 1
tris = sum(T[a] * n for a, n in tally.items())
print('CC-C17 rows appended to regionC.props: %d  (%s)' % (len(c17), ', '.join('%s x%d' % kv for kv in sorted(tally.items()))))
print('CC-C17 added tris (sum, before cull): %d' % tris)
print('giant rows with cullM 140 (CC-C17 shape):', cfgsrc.count('cullM: 140 },   // CC-C17 shape'))
print('C13b kit rows counted: churchArchway 4000 churchCornerButtress 2000 stoneSteps 5000 stoneCrossTilted 4000')
ok = True
for lx, lz in ((0, -366), (-175, -266)):
    r = run(lx, lz, 170)
    v = 'PASS' if r['worst'] <= CAP and not r['missing'] else 'FAIL'
    ok &= v == 'PASS'
    print('LEDGER centre (%g,%g) R 170: worst %d = %.2f%% of 2M at (%g,%g)  missing %s  -> %s' % (lx, lz, r['worst'], r['pct'], r['at'][0], r['at'][1], r['missing'] or 'none', v))
r = run(0, -366, 280)
print('whole disc (0,-366) R 280 (info): worst %d = %.2f%% at (%g,%g)' % (r['worst'], r['pct'], r['at'][0], r['at'][1]))
print('LEDGER', 'PASS' if ok else 'FAIL', '(cap %d)' % CAP)
sys.exit(0 if ok else 1)
