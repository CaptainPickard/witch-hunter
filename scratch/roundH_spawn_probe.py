#!/usr/bin/env python3
"""Round H: compute the region-A player spawn from CONFIG and run its safety checks.

Rule (io/missions/2026-10-05-cc-roundH-tone.md section 1):
  wallPoint    = the south wall ring point on the dirt-path centerline. The path
                 only spans z in [zTo, zFrom], so z = min(ringRadius, zFrom) and
                 x = path centerline x(z) = swayAmp * sin(2pi (z - zFrom) / swayPeriod).
  firstLantern = the regionA lanternPost prop nearest to wallPoint.
  spawn        = midpoint(wallPoint, firstLantern), rounded to 0.5 m.
Checks: >= 3 m from every CONFIG prop collider centre (region A), outside the
hold_outskirts keepOut ellipse, and no enemy spawn within 12 m. If an enemy is
within 12 m, nudge 0.5 m along the path toward the lantern until clear. With
--scatter plan.json it also reports clearance to the scatter-plan trees.
CONFIG is read through wall_mirror (esprima literals). Footprints and collider
radii are measured the way the game measures them.

  roundH_spawn_probe.py <repo-root> [--scatter plan.json] [--json out.json]
Exits non-zero if any check fails. Signed: Claude Code (Round H), 2026-10-05.
"""
import json, math, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
args = sys.argv[2:]
sys.argv = [sys.argv[0], str(root)]
sys.path.insert(0, str(Path(__file__).parent))
import wall_mirror as WM   # noqa: E402  (module reads sys.argv[1] = repo root)

CFG = WM.CFG
A = CFG['regionA']
DP = CFG['world']['dirtPath']
ringR = CFG['boundaryWall']['radius']


def path_x(z):
    return DP['swayAmp'] * math.sin(2 * math.pi * (z - DP['zFrom']) / DP['swayPeriod'])


def r05(v):
    return math.floor(v * 2 + 0.5) / 2


zw = min(ringR, DP['zFrom'])
wall = (path_x(zw), zw)
posts = [p for p in A['props'] if p['asset'] == 'lanternPost']
lantern = min(posts, key=lambda p: math.hypot(p['x'] - wall[0], p['z'] - wall[1]))
lp = (lantern['x'], lantern['z'])
spawn = (r05((wall[0] + lp[0]) / 2), r05((wall[1] + lp[1]) / 2))

# enemy nudge (toward the lantern along the wall->lantern line, 0.5 m steps)
nudges = 0
ux, uz = lp[0] - wall[0], lp[1] - wall[1]
ul = math.hypot(ux, uz); ux, uz = ux / ul, uz / ul
def near_enemy(s):
    return [e for e in A['enemies'] if math.hypot(e['x'] - s[0], e['z'] - s[1]) < 12]
while near_enemy(spawn) and nudges < 40:
    nudges += 1
    spawn = (r05(spawn[0] + ux * 0.5), r05(spawn[1] + uz * 0.5))

checks = {}
props = []
for p in A['props']:
    m = WM.meta(p['asset'])
    r = WM.collider_radius(p['asset'], m['width'], p['scale']) if m else 0.0
    d = math.hypot(p['x'] - spawn[0], p['z'] - spawn[1])
    props.append((d, d - r, p['asset'], p['x'], p['z'], round(r, 2)))
props.sort()
checks['nearest_prop_center_m'] = round(props[0][0], 2)
checks['nearest_prop'] = props[0][2:]
checks['min_prop_edge_gap_m'] = round(min(p[1] for p in props), 2)
checks['prop_center_ge_3m'] = props[0][0] >= 3.0
checks['prop_edge_clear'] = min(p[1] for p in props) > 0
ko = [k for k in CFG['scatter']['keepOut'] if k['regionId'] == A['id']][0]
dko = math.hypot((spawn[0] - ko['x']) / ko['rx'], (spawn[1] - ko['z']) / ko['rz'])
checks['keepOut_norm_dist'] = round(dko, 3)
checks['outside_keepOut'] = dko > 1
en = sorted((math.hypot(e['x'] - spawn[0], e['z'] - spawn[1]), e['type'], e['x'], e['z']) for e in A['enemies'])
checks['nearest_enemy_m'] = round(en[0][0], 2)
checks['nearest_enemy'] = en[0][1:]
checks['enemy_clear_12m'] = en[0][0] >= 12
checks['enemy_nudges'] = nudges
checks['path_center_x_at_spawn_z'] = round(path_x(spawn[1]), 3)
checks['off_path_center_m'] = round(abs(spawn[0] - path_x(spawn[1])), 3)
checks['on_path_ribbon'] = abs(spawn[0] - path_x(spawn[1])) <= DP['halfWidth']
checks['inside_wall_ring'] = math.hypot(*spawn) < CFG['boundaryWall']['minRadius']
if '--scatter' in args:
    plan = json.load(open(args[args.index('--scatter') + 1]))
    trees = plan[A['id']]['trees']
    tt = sorted((math.hypot(t['x'] - spawn[0], t['z'] - spawn[1]) - t['r'], t['asset']) for t in trees)
    checks['nearest_scatter_tree_edge_gap_m'] = round(tt[0][0], 2) if tt else None
    checks['scatter_tree_clear'] = (not tt) or tt[0][0] > 0

out = {'wallPoint': [round(wall[0], 3), round(wall[1], 3)], 'ringRadius': ringR, 'pathZFrom': DP['zFrom'],
       'firstLantern': list(lp), 'spawn': list(spawn), 'checks': checks}
print(json.dumps(out, indent=1))
if '--json' in args:
    Path(args[args.index('--json') + 1]).write_text(json.dumps(out, indent=1) + '\n')
must = ['prop_center_ge_3m', 'prop_edge_clear', 'outside_keepOut', 'enemy_clear_12m', 'inside_wall_ring']
if '--scatter' in args:
    must.append('scatter_tree_clear')
if not all(checks[k] for k in must):
    sys.exit('SPAWN CHECK FAILED: ' + ', '.join(k for k in must if not checks[k]))
