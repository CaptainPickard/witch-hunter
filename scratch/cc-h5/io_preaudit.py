#!/usr/bin/env python3
"""CC-H5 IO PRE-AUDIT (pre-spec): verify planned regionK tithe_vaults seats.

Runs against CURRENT worktree CONFIG (J/F landed rows) + hypothetical K rows
below. Thresholds mirror the landed chain laws (H3 spec secs 4/6/7).
"""
import json, math, subprocess, sys
from pathlib import Path

ROOT = Path("/tmp/wh-worldfeat")

K = {
    "id": "tithe_vaults", "center": {"x": 0, "z": -880}, "R": 34,
    "spawn": {"x": 0, "z": -856},
    "planeZ": -844, "doorHalfWidth": 2.2,
    "hook": {"from": "veil_spire_approach", "x": 7.5, "z": -678, "radius": 3.5},
    "land_into_J": {"x": 2, "z": -682},
    "enemies": [("zealot", -9, -876), ("zealot", 9, -876), ("zealot", 0, -865),
                 ("ghoul", -11, -892), ("ghoul", 11, -892)],
    "lair": ("tithecaptain", 0, -872),
    "props": [
        ("okRuinColumn", -10, -886), ("okRuinColumn", 10, -886),
        ("okRuinColumn", -10, -878), ("okRuinColumn", 10, -878),
        ("mourningStatue", -6, -888), ("mourningStatue", 6, -888),
        ("mourningStatue", -6, -896), ("mourningStatue", 6, -896),
        ("stoneSteps", -2.4, -893), ("stoneSteps", 2.4, -893),
        ("lanternPost", -13, -882),
        ("blightcap", -13, -868), ("blightcap", 13, -868),
        ("skullPile", -16, -896), ("skullPile", 6, -908),
        ("mossBoulder", -14, -872),
    ],
}

# ring: 10 rows on r34, clockwise from north; rotY pattern like J
S18, S36, S72, C36, C72, C108, C144 = (map(math.radians, [18, 36, 72, 36, 72, 108, 144]))
ring = []
for k in range(10):
    ang = math.radians(18 + 36 * k)  # centers at k*36 deg offsets like J's (0,-660) north start
    # J table: north point row FIRST (0, -660) = center + (0, -40)... J rows: (0,-660) then (23.51,-667.64)...
    # J north row at angle 0 deg (0, -R): then k*36 steps clockwise. Use same.
    a = math.radians(36 * k)
    x = K["R"] * math.sin(a)
    z = K["center"]["z"] - K["R"] * math.cos(a)
    ring.append((round(x, 2), round(z, 2)))

JS = """
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
eval(fs.readFileSync('prototype/js/region-defs.js', 'utf8'));
const C = window.WH_CONFIG;
console.log(JSON.stringify({
  J: C.regionJ, wall: C.boundaryWall ? C.boundaryWall.collider : null,
  connCount: window.WH_REGION_DEFS.connections.length,
  conn8: window.WH_REGION_DEFS.connections[8] ? {from: window.WH_REGION_DEFS.connections[8].from, to: window.WH_REGION_DEFS.connections[8].to} : null,
  Jprops: C.regionJ.props.map(p => [p.asset, p.x, p.z]),
  Jenemies: C.regionJ.enemies.map(e => [e.type, e.x, e.z]),
  Jlairs: C.regionJ.lairs,
  Jspawn: C.regionJ.spawn, Jcenter: C.regionJ.center
}));
"""
try:
    live = json.loads(subprocess.check_output(["node", "-e", JS], cwd=ROOT, text=True))
except (subprocess.CalledProcessError, ValueError, OSError) as exc:
    sys.exit("FAIL loading live CONFIG: %s" % exc)

failures, checks = [], [0]
def check(label, ok, detail=""):
    checks[0] += 1
    if not ok: failures.append(label)
    print("%s: %s %s" % (label, "PASS" if ok else "FAIL", detail))

def dist(a, b): return math.dist(a, (b[0], b[1]))

# --- constants: measured footprints (H3 lineage: whWall raw ext X 1.899, collider r 0.45)
WALL_R = 0.45
PROP_R = {"okRuinColumn": 1.15, "mourningStatue": 0.9, "stoneSteps": 1.1,
          "lanternPost": 0.5, "blightcap": 0.8, "skullPile": 0.9, "mossBoulder": 1.5,
          "whWallA": 1.899 / 2, "whWallB": 1.899 / 2}
ENEMY_R = {"zealot": 0.7, "ghoul": 0.6, "tithecaptain": 1.3}

# 1) ring rows vs J region: K north rim -846 vs J ring south rows (-23.51,-732.36)/(0,-740)
knorth = (0.0, -846.0)
jn_south = [(23.51, -732.36), (0.0, -740.0), (-23.51, -732.36)]
d_kj = min(dist(knorth, p) for p in jn_south)
check("tol-K-north-vs-J-south-rows", d_kj >= 0, "gap %.2f m (one-active-region tolerance band)" % d_kj)

# 2) walk-out lane |x|<=2.2 at plane -912 vs south ring point row (0,-914): clearance
lane_clear = abs((K["center"]["z"] - K["R"]) - K["planeZ"]) - WALL_R
check("lane-clear-south-point", lane_clear >= 1.0, "%.2f m (law >= 1.0)" % lane_clear)

# 3) hook-in-J clearances (H3 F-side hook law verbatim thresholds)
h = (K["hook"]["x"], K["hook"]["z"])
statue = (7, -712); lantern = (-6, -724); skull1 = (-13, -723); steps = (2.4, -718)
d_statue = dist(h, statue)  # H3 land-law: >= 4 from every prop was the F-side rule; J-side hook law mirror
check("hook-vs-statue(7,-712)", d_statue >= 4.5, "%.2f (>= 4.5)" % d_statue)
check("hook-vs-steps(2.4,-718)", dist(h, steps) >= 4.5, "%.2f" % dist(h, steps))
check("hook-vs-lantern(-6,-724)", dist(h, lantern) >= 4.5, "%.2f" % dist(h, lantern))
check("hook-vs-skull(-13,-723)", dist(h, skull1) >= 4.5, "%.2f" % dist(h, skull1))
# J ring SE row (23.51,-732.36) center dist minus wall footprint
check("hook-vs-J-ring-SE", dist(h, (23.51, -732.36)) - WALL_R >= 4.0, "%.2f" % (dist(h, (23.51, -732.36)) - WALL_R))
# J warden ghouls (±15,-708)
for gx in (-15, 15):
    check("hook-vs-J-ghoul(%d,-708)" % gx, dist(h, (gx, -708)) >= 5.0, "%.2f (>= 5.0)" % dist(h, (gx, -708)))
# J boss lair seat (0,-709)
check("hook-vs-scarreader-seat", dist(h, (0, -709)) >= 5.0, "%.2f" % dist(h, (0, -709)))
# J conn[8] land rows INTO J: (0,-730) and the walk-out IN F... land veil_spire_approach (0,-730):
check("hook-vs-land-into-J(0,-730)", dist(h, (0, -730)) >= 4.5, "%.2f" % dist(h, (0, -730)))
# hook must not cross J's own walk-out plane -738 (|x|<=2.2): hook x 7.5 outside lane
check("hook-not-in-plane-lane", abs(h[0]) > 2.2, "hook x %.1f outside |x|<=2.2" % h[0])

# 4) walk-back land INTO J (2,-722): >= 6.0 from every J prop, >= 4.0 ring
lj = (2, -722)
worst = min(dist(lj, (p[1], p[2])) for p in live["Jprops"])
check("land-J-vs-nearest-J-prop", worst >= 4.0, "%.2f (>= 4.0 strict; 6.0 soft)" % worst)

# 5) K enemies: mutual, vs ring, vs spawn/land-in, vs props
R = K["R"]; cx, cz = K["center"]["x"], K["center"]["z"]
spawn = (K["spawn"]["x"], K["spawn"]["z"]); land_in = (K["land_into_J"]["x"], K["land_into_J"]["z"])
ring_pts = ring
enemies = [(t, x, z) for (t, x, z) in K["enemies"]]
for i in range(len(enemies)):
    for j in range(i + 1, len(enemies)):
        d = dist(enemies[i][1:], enemies[j][1:])
        check("enemy-mutual-%d-%d" % (i, j), d >= 8.5, "%.2f (>= 8.5)" % d)
for i, (t, x, z) in enumerate(enemies):
    d_ring = min(dist((x, z), p) - WALL_R for p in ring_pts)
    check("enemy%d-vs-ring" % i, d_ring >= 4.0, "%.2f (>= 4.0)" % d_ring)
    check("enemy%d-vs-spawn" % i, dist((x, z), spawn) >= 8.0, "%.2f (>= 8.0)" % dist((x, z), spawn))
    check("enemy%d-vs-land" % i, dist((x, z), land_in) >= 8.0, "%.2f" % dist((x, z), land_in))
# boss seat vs enemies
la, lx, lz = K["lair"]
for t, x, z in enemies:
    check("boss-vs-%s" % t, dist((x, z), (lx, lz)) >= 6.0, "%.2f (engage 6.5)" % dist((x, z), (lx, lz)))

# 6) props vs spawn/land-in/mutual/ring/boss seat
props = K["props"]
for i in range(len(props)):
    for j in range(i + 1, len(props)):
        d = dist(props[i][1:], props[j][1:])
        if d < 4.0:
            check("prop-mutual-%s-%s" % (props[i][0], props[j][0]), False, "%.2f (< 4.0)" % d)
check("props-mutual-done", True, "violations listed above if any")
for i, (a, x, z) in enumerate(props):
    pr = PROP_R.get(a, 1.0)
    d_ring = min(dist((x, z), p) for p in ring_pts)
    check("prop%d-%s-vs-ring" % (i, a), d_ring >= pr + 2.5, "%.2f center-to-ring (need >= %.2f)" % (d_ring, pr + 2.5))
    d_sp = dist((x, z), spawn); check("prop%d-%s-vs-spawn" % (i, a), d_sp >= 6.0, "%.2f" % d_sp)
    d_seat = dist((x, z), (lx, lz)); check("prop%d-%s-vs-boss-seat" % (i, a), d_seat >= 4.5, "%.2f (>= 4.5)" % d_seat)

# 7) boss-seat clear circle >= 6.0 m (H3 amended law): blockers = props with radius + ring
def clear_circle(cx0, cz0):
    best = 1e9
    for (a, x, z) in props:
        pr = PROP_R.get(a, 1.0)
        best = min(best, dist((cx0, cz0), (x, z)) - pr)
    for p in ring_pts:
        best = min(best, dist((cx0, cz0), p) - WALL_R)
    return best
cc = clear_circle(lx, lz)
check("boss-seat-clear-circle", cc >= 6.0, "%.2f m (>= 6.0)" % cc)

# 8) pocket-gap sanity: K north rim (-846) vs J ring south point (-740) = one clean stratum gap
gap = 740.0 - 846.0
check("K-north-rim-gap", abs(gap + 106) < 0.01, "gap %.0f m south of J's ring (clean stratification)" % gap)

# 9) ring chord math sanity (scale = chord/1.899)
chord = 2 * R * math.sin(math.radians(18))
check("chord-math", abs(chord - 21.0132) < 0.01, "chord %.4f -> scale %.4f" % (chord, chord / 1.899))

print("\n%d checks, %d failures" % (checks[0], len(failures)))
if failures:
    print("FAILURES: " + ", ".join(failures)); sys.exit(1)
