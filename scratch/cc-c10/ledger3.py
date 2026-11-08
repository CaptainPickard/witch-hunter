#!/usr/bin/env python3
"""CC-C10 LEDGER3 (valspec A7 / B7): a copy of scratch/cc-c17/ledger2.py (left
byte-identical) on scratch/cc-c10/ledger3_probe.js - the region-C 2M drawn-tri
worst case, R 170, 2 m grid, at THREE centres: (0,-366), (-175,-266) and the
homestead (150.5,-256.7). PASS = worst <= 1,980,000 at all three + missing empty.
T gains okFarmBarn (max(29500, GLB header)) and farmerBody (GLB header); the
farmer (CONFIG.regionC.npc, not a props row) rides the probe's argv[6]
extra-rows hook as one pseudo-row at its x/z with its cullM.
Also prints a whole-disc scan (R 280) and the CC-C10 added-row tally.
usage: python3 scratch/cc-c10/ledger3.py [repoRoot]"""
import json, subprocess, sys, os, re
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '/tmp/wh-worldfeat')
HERE = os.path.dirname(os.path.abspath(__file__))
CAP = 1980000
NPC_ROWS = os.path.join(HERE, 'ledger3_npc_rows.json')
def run(lx, lz, r):
    return json.loads(subprocess.check_output(['node', os.path.join(HERE, 'ledger3_probe.js'), ROOT, str(lx), str(lz), str(r), NPC_ROWS]))
src = open(os.path.join(HERE, 'ledger3_probe.js')).read()
T = {k: int(v) for k, v in re.findall(r'"?(\w+)"?: (\d{3,})', src[src.index('const T = {'):src.index('const M = {')])}
cfg = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'dump_cfg.js'), ROOT]))
npc = cfg['npc']
json.dump([{'asset': npc['asset'], 'x': npc['x'], 'z': npc['z'], 'cullM': npc['cullM']}], open(NPC_ROWS, 'w'))
props = cfg['props']
c10 = [p for p in props if p['asset'] == 'okFarmBarn'] + [{'asset': npc['asset']}]
tally = {}
for p in c10: tally[p['asset']] = tally.get(p['asset'], 0) + 1
tris = sum(T[a] * n for a, n in tally.items())
print('CC-C10 rows: %d  (%s; farmer via the argv[6] hook at (%g,%g) cullM %g)' % (len(c10), ', '.join('%s x%d' % kv for kv in sorted(tally.items())), npc['x'], npc['z'], npc['cullM']))
print('CC-C10 added tris (sum, before cull): %d' % tris)
ok = True
for lx, lz in ((0, -366), (-175, -266), (150.5, -256.7)):
    r = run(lx, lz, 170)
    v = 'PASS' if r['worst'] <= CAP and not r['missing'] else 'FAIL'
    ok &= v == 'PASS'
    print('LEDGER centre (%g,%g) R 170: worst %d = %.2f%% of 2M at (%g,%g)  missing %s  -> %s' % (lx, lz, r['worst'], r['pct'], r['at'][0], r['at'][1], r['missing'] or 'none', v))
r = run(0, -366, 280)
print('whole disc (0,-366) R 280 (info): worst %d = %.2f%% at (%g,%g)' % (r['worst'], r['pct'], r['at'][0], r['at'][1]))
print('LEDGER', 'PASS' if ok else 'FAIL', '(cap %d)' % CAP)
sys.exit(0 if ok else 1)
