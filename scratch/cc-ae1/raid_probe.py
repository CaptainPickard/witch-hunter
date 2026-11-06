"""CC-AE1 raid seat probe v3 (final law): proves the AMENDED seat law.

Amendment A (v1 evidence, disclosed in the spec): notch-mouth exclusion
(terminal 26 m of branch roads), fire gate unified 50 m.
Amendment B (v2 evidence): exclusion-zone seats count SEPARATELY (not as
fails); slide-cover law = no consecutive eligible-fail run longer than
16 offset-seats (2 centerline samples = 8 m of road; slide depth 18 m
covers it with margin). passPct law >= 90% of eligible seats.

Run from /tmp/wh-worldfeat: python3 scratch/cc-ae1/raid_probe.py
"""
import json
import subprocess
import sys

ROOT = '/tmp/wh-worldfeat'
NODE_CHILD = r'''
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const C = window.WH_CONFIG, G = window.WH_GROUND;
const RID = 'forest_of_the_old_king';
const SEAT_ROADS = ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'];
const roads = C.roads.filter(r => r.regionId === RID && r.points &&
  SEAT_ROADS.includes(r.id));
const props = C.regionC.props.filter(p => p.x !== undefined);
const fires = C.regionC.props.filter(p => p.asset === 'banditCampfire')
  .map(p => [p.x, p.z]);
const stone = { x: 0, z: -366 };
const OFFSETS = [14.0, 14.9, 16.0, 17.5];
const STEP = 4;
const out = {};
for (const rd of roads) {
  const pts = rd.points;
  const centers = [];
  for (let i = 0; i + 1 < pts.length; i++) {
    const a = pts[i], b = pts[i + 1];
    const segLen = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const dx = (b[0] - a[0]) / segLen, dz = (b[1] - a[1]) / segLen;
    const n = Math.ceil(segLen / STEP);
    const px = -dz, pz = dx;
    for (let j = 0; j <= n; j++) {
      const t = Math.min(segLen, j * STEP);
      centers.push({ x: a[0] + dx * t, z: a[1] + dz * t, px, pz,
        mouthEnd: rd.id !== 'kingsRoad' && i === pts.length - 2 && t >= segLen - 26 });
    }
  }
  const cs = centers.filter((c, i) => i === 0 ||
    Math.hypot(c.x - centers[i - 1].x, c.z - centers[i - 1].z) > 0.4);
  let pass = 0, fail = 0, excl = 0, maxRun = 0, run = 0, worst = '';
  const reasons = {};
  for (const c of cs) {
    for (const off of OFFSETS) for (const side of [1, -1]) {
      const x = c.x + c.px * off * side, z = c.z + c.pz * off * side;
      if (c.mouthEnd) { excl++; run = 0; continue; }
      const slopeDeg = Math.atan(G.slopeTan(RID, x, z)) * 180 / Math.PI;
      let pd = 1e9, pn = '';
      for (const p of props) { const d = Math.hypot(p.x - x, p.z - z); if (d < pd) { pd = d; pn = p.asset; } }
      let fd = 1e9;
      for (const f of fires) { const d = Math.hypot(f[0] - x, f[1] - z); if (d < fd) fd = d; }
      const sd = Math.hypot(stone.x - x, stone.z - z);
      const ok = slopeDeg <= 24.0 && pd >= 3.0 && fd >= 50.0 && sd >= 40.0;
      if (ok) { pass++; run = 0; }
      else { fail++; run++; maxRun = Math.max(maxRun, run);
        const why = slopeDeg > 24 ? 'slope' : pd < 3 ? 'prop' : fd < 50 ? 'fire' : 'stone';
        reasons[why] = (reasons[why] || 0) + 1;
        if (!worst) worst = `${rd.id}@(${x.toFixed(1)},${z.toFixed(1)}) ${why} ${why === 'slope' ? slopeDeg.toFixed(1) + 'deg' : why === 'prop' ? pd.toFixed(1) + ' ' + pn : why === 'fire' ? fd.toFixed(1) : sd.toFixed(1)}`; }
    }
  }
  out[rd.id] = { eligible: pass + fail, excluded: excl, pass, fail,
    passPct: +(100 * pass / (pass + fail)).toFixed(1), maxRun, reasons, worst };
}
console.log(JSON.stringify(out));
'''

def main():
    with open(ROOT + '/scratch/cc-ae1/node_probe.js', 'w') as f:
        f.write('const R = process.argv[2];\n' + NODE_CHILD)
    r = subprocess.run(['node', ROOT + '/scratch/cc-ae1/node_probe.js', ROOT],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print('NODE FAIL', r.stderr[-2000:])
        sys.exit(1)
    data = json.loads(r.stdout.strip())
    print(json.dumps(data, indent=1))
    ok = True
    for rid, d in data.items():
        road_ok = d['passPct'] >= 90.0 and d['maxRun'] <= 16
        print(f"{rid}: {'PASS' if road_ok else 'CHECK'} passPct {d['passPct']} maxRun {d['maxRun']} excl {d['excluded']} reasons {d['reasons']} worst={d['worst']}")
        ok = ok and road_ok
    print('OVERALL', 'PASS' if ok else 'NEEDS-REVIEW')

main()
