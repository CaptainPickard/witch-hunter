#!/usr/bin/env python3
"""Round I6 proof: one shot for roundH_proof_render.py (reused as-is), built on
roundI_proof_scene.py (run via runpy for its ALL/near/shot helpers + night rig).
  roundI6_proof_scene.py <repo-root> <scatter-plan.json> <out-shots.json> [player_z]
Shot 04-path-corridor: the player at the region-A spawn (2.5, 74) facing down the dirt path
        (-z, toward z 32), the game's chase rig (camDistance/camHeight, 20 deg pitch) and the
        game's 60 deg vertical FOV (1024x640 -> 19.5 mm on the 36 mm sensor).
"""
import json, math, runpy, sys, tempfile
from pathlib import Path

root, plan_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
pz = float(sys.argv[4]) if len(sys.argv) > 4 else None
here = Path(__file__).resolve().parent
sys.argv = [str(here.parent / 'roundI_proof_scene.py'), root, plan_p, tempfile.mktemp(suffix='.json')]
G = runpy.run_path(sys.argv[0], run_name='roundI_scene')

RA = G['RA']
px = RA['spawn']['x']
pz = RA['spawn']['z'] if pz is None else pz
lens = 18.0 / math.tan(math.atan(math.tan(math.radians(30)) * 1024 / 640))
s = G['shot']('04-path-corridor', px, pz, (G['path_x'](pz - 20), pz - 20), round(lens, 2),
              G['near'](px, pz - 25, 75))
I6 = [p for p in RA['props'] if p['asset'].startswith('reachTree') and 32 <= p['z'] <= 70 and abs(p['x']) < 14]
s['i6Trees'] = [{'asset': p['asset'], 'x': p['x'], 'z': p['z']} for p in I6]
json.dump([s], open(out_p, 'w'))
print(s['stem'], 'cam', [round(v, 2) for v in s['cam']], 'aim', [round(v, 2) for v in s['aim']],
      'lens', s['lens'], 'objects', len(s['objects']), 'i6', len(I6))
