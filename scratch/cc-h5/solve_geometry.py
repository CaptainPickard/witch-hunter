#!/usr/bin/env python3
"""CC-H5 live CONFIG/region-defs geometry + wiring audit. Run from worktree root.

Mirrors the cc-h3 lineage: everything is evaluated from the LANDED JS source,
never copied from spec quotes. Ring rows are re-derived against the r34 circle
(valspec V-3/N-2 law); the boss-seat circle uses the valspec's fixed asset
footprint map AND the h3 per-row width*scale/2 map (both disclosed).

Spec-figure corrections the live build carries (disclosed in the build note):
  - planeZ -848 (spec sec 3's -844 sat 2 m OUTSIDE the north rim -846; every
    landed plane sits 2 m inside its rim), spawn/land pair unchanged.
  - zealot flanks (+-15,-863) (spec's (+-9,-876) sat 4.12 m from the dais
    colonnade, below the >= 5.0 enemy-vs-prop law).
  - root colossus (0,-880) (spec's (0,-876) bound the boss-seat circle at
    2.85 m, below the 6.0 AMEND-1 law; relocated seat binds at 6.85 m).
  - ring rows re-derived at strict 2dp (spec literals drifted up to 2.01 m;
    valspec correction ledger (a): rho-on-r34 is the law).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEAD = "1f7f904"

JS = r"""
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
eval(fs.readFileSync('prototype/js/region-defs.js', 'utf8'));
const C = window.WH_CONFIG, D = window.WH_REGION_DEFS;
const conn = D.connections[9];
const seeds = [];
(function walk(o, path) {
  for (var k in o) {
    var v = o[k];
    if (v !== null && typeof v === 'object') walk(v, path.concat(k));
    else if (/groundSeed|textureSeed/.test(k)) seeds.push(path.concat(k).join('.') + '=' + v);
  }
})(C, []);
const census = {};
Object.keys(C).filter(function (k) { return /^region/.test(k); }).forEach(function (k) {
  var r = C[k];
  var z = (r.enemies || []).filter(function (e) { return e.type === 'zealot'; }).length;
  census[k] = z;
});
console.log(JSON.stringify({
  K: C.regionK, J: C.regionJ, F: C.regionF,
  c: conn, count: D.connections.length,
  wall: C.boundaryWall ? C.boundaryWall.collider : null,
  forward: D.connectionBetween(C.regionJ.id, C.regionK.id) === conn,
  reverse: D.connectionBetween(C.regionK.id, C.regionJ.id) === conn,
  sideInK: D.sideIn(conn, C.regionK.id),
  sideOfPlaneK: D.sideOfPlane(conn, C.regionK.spawn.z),
  sideInJ: D.sideIn(conn, C.regionJ.id),
  planeInJ: D.planeIn(conn, C.regionJ.id),
  planeInK: D.planeIn(conn, C.regionK.id),
  zealot: C.enemy.zealot, cap: C.enemy.tithecaptain,
  bbZ: C.enemy.bodyByType.zealot, bbT: C.enemy.bodyByType.tithecaptain,
  avZ: C.enemy.animVariantByType.zealot, avT: C.enemy.animVariantByType.tithecaptain,
  seeds: seeds, census: census, hasCoin: !!C.items.stolenCoin,
  coinName: C.items.stolenCoin ? C.items.stolenCoin.name : null
}));
"""

try:
    data = json.loads(subprocess.check_output(["node", "-e", JS], cwd=ROOT, text=True))
except (subprocess.CalledProcessError, ValueError, OSError) as exc:
    sys.exit("FAIL loading live CONFIG/region-defs: %s" % exc)

failures = []
checks = 0


def check(label, passed, detail=""):
    global checks
    checks += 1
    if not passed:
        failures.append(label)
    print("%s: %s %s" % (label, "PASS" if passed else "FAIL", detail))


def floor(label, value, limit):
    check(label, value + 1e-8 >= limit, "%.4f >= %.4f" % (value, limit))


def point(row):
    return (row["x"], row["z"])


def distance(a, b):
    return math.dist(a, b)


def block_bytes(text, opener):
    """Valspec V-4/V-7 extraction: opener line through the first '^  },' line."""
    lines = text.split("\n")
    i0 = lines.index(opener)
    for i in range(i0 + 1, len(lines)):
        if lines[i] == "  },":
            return ("\n".join(lines[i0:i + 1]) + "\n").encode()
    raise ValueError("block close not found after " + opener)


def git_show(path):
    return subprocess.check_output(["git", "show", "%s:%s" % (HEAD, path)],
                                   cwd=ROOT, text=True)


K, J = data["K"], data["J"]
c = data["c"]
fail = failures.append

# ---------------------------------------------------------------- ground truth
WR = data["wall"]["r"]
# Valspec boss-seat footprint map (fixed asset radii, disclosed).
FIXED_R = {"mourningStatue": 0.9, "stoneSteps": 1.1, "okRuinColumn": 1.15,
           "lanternPost": 0.5, "blightcap": 0.8, "skullPile": 0.9,
           "mossBoulder": 1.5}
# h3-lineage measured raw GLB X extents (per-row radius = width*scale/2).
WIDTH = {"whWallA": 1.899, "whWallB": 1.899, "mourningStatue": 1.862,
         "stoneSteps": 1.94825, "okRuinColumn": 0.957085, "blightcap": 1.692074,
         "lanternPost": 0.585384, "skullPile": 2.0, "mossBoulder": 1.897361}


def rings(region):
    return [p for p in region["props"] if p["asset"] in ("whWallA", "whWallB")]


def colliders(region):
    result = []
    for row in rings(region):
        length = WIDTH[row["asset"]] * row["scale"]
        ax, az = math.cos(row["rotY"]), -math.sin(row["rotY"])
        for k in range(row["wall"]):
            t = ((k + 0.5) / row["wall"] - 0.5) * length
            result.append((row["x"] + ax * t, row["z"] + az * t, WR, row))
    return result


def nearest(p, circles):
    return min(distance(p, (x, z)) - r for x, z, r, _ in circles)


kw, jw = colliders(K), colliders(J)
krows = [p for p in K["props"] if p not in rings(K)]
jrows = [p for p in J["props"] if p not in rings(J)]
kc, jc = point(K["center"]), point(J["center"])
spawn = point(K["spawn"])
hook = point(K["door"]["interact"])
landj = point(K["door"]["land"]["veil_spire_approach"])
landk = point(K["door"]["land"]["tithe_vaults"])
kenemies = [point(e) for e in K["enemies"]]
jLairs = [point(e) for e in J["lairs"]]

# -------------------------------------------------------------------- V-0/V-5
check("V-0 CONFIG parses", True, "node eval + JSON round-trip")
KEYS = ["id", "name", "center", "groundRadius", "groundY", "groundColor",
        "groundColor2", "groundSeed", "scatter", "spawn", "gravityY", "fogColor",
        "fogDensity", "ambientLightLevel", "door", "enemies", "lairs",
        "rotLair", "props"]
check("V-0 regionK key set exact", sorted(K.keys()) == sorted(KEYS),
      "extra=%s missing=%s" % (sorted(set(K) - set(KEYS)), sorted(set(KEYS) - set(K))))
Z_KEYS = ["hpMax", "moveSpeed", "chaseSpeed", "attackDamage", "attackRange",
          "attackCooldown", "sightRadius", "leashRadius", "staggerTime", "radius",
          "aggroPingInterval", "attackPhase", "ai1"]
C_KEYS = ["name", "hp", "dmg", "speed", "aggro", "pattern", "slamRadius",
          "slamArcDeg", "slamWindup", "slamActive", "slamRecover", "slamCooldown",
          "slamTrackDegPerSec", "engageRange", "cueDark", "cueHot", "scale",
          "lair", "lairRadius", "rearm", "loot", "minions", "radius",
          "corpseLingerSec", "maxCorpses", "riseSec", "barLiftM", "ai1"]
check("V-0 zealot keys exact", data["zealot"] and sorted(data["zealot"]) == sorted(Z_KEYS),
      "extra=%s missing=%s" % (sorted(set(data["zealot"]) - set(Z_KEYS)),
                               sorted(set(Z_KEYS) - set(data["zealot"]))))
check("V-0 tithecaptain keys exact", data["cap"] and sorted(data["cap"]) == sorted(C_KEYS))
z, cap = data["zealot"], data["cap"]
check("V-0 zealot spot hpMax 60.0", z["hpMax"] == 60.0)
check("V-0 zealot spot sightRadius 16.0", z["sightRadius"] == 16.0)
check("V-0 zealot ai1 guardArcDeg 50", z["ai1"]["guardArcDeg"] == 50)
check("V-0 captain pattern boss-slam", cap["pattern"] == "boss-slam")
check("V-0 captain slamArcDeg 100", cap["slamArcDeg"] == 100)
check("V-0 captain slamTrack 110", cap["slamTrackDegPerSec"] == 110)
check("V-0 captain scale 2.1", cap["scale"] == 2.1)
check("V-0 captain ai1 guardArcDeg 45", cap["ai1"]["guardArcDeg"] == 45)
check("V-0 captain cueHot 0xd84a4a", cap["cueHot"] == 0xD84A4A)
check("V-0 bodyByType zealot/tithecaptain banditBody",
      data["bbZ"] == "banditBody" and data["bbT"] == "banditBody")
check("V-0 animVariant zealot/tithecaptain bandit",
      data["avZ"] == "bandit" and data["avT"] == "bandit")
check("V-5 groundSeed 448271909", K["groundSeed"] == 448271909)
seed_vals = [s.split("=")[1] for s in data["seeds"]]
kseed_hits = [s for s in data["seeds"] if s.split("=")[1] == "448271909"
              and not s.startswith("regionK.groundSeed")]
check("V-5 groundSeed unique across all ground/texture seeds", not kseed_hits,
      "%d seed lines; hits=%s" % (len(data["seeds"]), kseed_hits))
check("V-5 groundY/scatter/gravityY", K["groundY"] == 0 and K["scatter"] is False
      and K["gravityY"] == -22)
print("V-5 seed inventory (record): %s" % "; ".join(data["seeds"]))

# ----------------------------------------------------------------- V-1/V-2/V-7
rd = (ROOT / "prototype/js/region-defs.js").read_text()
check("V-1 conn count 10", data["count"] == 10)
check("V-1 endpoints J->K axis z", c["from"] == J["id"] and c["to"] == K["id"]
      and c["axis"] == "z")
check("V-1 planeCoord == K.door.planeZ == -848", c["planeCoord"] == K["door"]["planeZ"])
check("V-1 doorX/halfWidth/suspend/wallGap", c["door"]["doorX"] == 0
      and c["door"]["doorHalfWidth"] == 2.2 and c["door"]["suspendDepthM"] == 0
      and c["door"]["wallGapPadM"] == 0 and c["door"]["arch"] is None
      and c["door"]["gatedTo"] is None)
check("V-1 walkFrom = tithe_vaults (one-sided)", c["door"]["walkFrom"] == K["id"])
check("V-1 interact from J (7.5,-678) r3.5", c["door"]["interact"] == K["door"]["interact"]
      and c["door"]["interact"]["from"] == J["id"] and c["door"]["interact"]["x"] == 7.5
      and c["door"]["interact"]["z"] == -678 and c["door"]["interact"]["radius"] == 3.5)
check("V-1 land deep-equals K door.land", c["door"]["land"] == K["door"]["land"])
check("V-1 fades 0.3/0.5/0.8", c["door"]["fadeIn"] == 0.3 and c["door"]["fadeOut"] == 0.5
      and c["door"]["exitFadeOut"] == 0.8)
check("V-1 prompt verbatim K", c["door"]["text"]["prompt"]
      == "E - Descend into the tithe vaults")
check("V-1 prompt differs from conn[8]",
      c["door"]["text"]["prompt"] != "E - Descend toward the spire")
check("V-1 makeRegion(K,-1) exactly once", rd.count("makeRegion(CFG.regionK, -1)") == 1)
check("V-2 sides[J]=+1 sides[K]=-1", c["sides"].get(J["id"]) == 1
      and c["sides"].get(K["id"]) == -1)
check("V-2 sideIn(K)==sideOfPlane(K spawn)==-1", data["sideInK"] == data["sideOfPlaneK"] == -1)
check("V-2 sideIn(J)==+1", data["sideInJ"] == 1)
check("V-2 planeIn J false / K true", not data["planeInJ"] and data["planeInK"])
check("V-2 forward==reverse==conn[9]", data["forward"] and data["reverse"])
check("V-2 source sides lines exactly once each (conn[9])",
      rd.count("connections[9].sides[CFG.regionJ.id] = +1;") == 1
      and rd.count("connections[9].sides[CFG.regionK.id] = -1;") == 1)
check("V-2 conn[8] precedent pair intact (source)",
      rd.count("connections[8].sides[CFG.regionF.id] = -1;") == 1
      and rd.count("connections[8].sides[CFG.regionJ.id] = +1;") == 1)

# V-7 byte-identity: regionI + conn span 0..8
head_cfg = git_show("prototype/js/CONFIG.js")
head_rd = git_show("prototype/js/region-defs.js")
check("V-7 regionI block byte-identical",
      block_bytes(head_cfg, "  regionI: {") == block_bytes((ROOT / "prototype/js/CONFIG.js").read_text(), "  regionI: {"))
check("V-7 regionJ block byte-identical (V-4)",
      block_bytes(head_cfg, "  regionJ: {") == block_bytes((ROOT / "prototype/js/CONFIG.js").read_text(), "  regionJ: {"))


def conn_span(text):
    i = text.index("connections.push")
    m = text.index("connections[8].sides[CFG.regionJ.id] = +1;")
    return text[i:m + len("connections[8].sides[CFG.regionJ.id] = +1;")].encode()


check("V-7 conn[0..8] span byte-identical",
      conn_span(head_rd) == conn_span(rd))
check("V-7 makeRegion(J/I) one hit each, unchanged",
      rd.count("makeRegion(CFG.regionJ, -1)") == 1
      and rd.count("makeRegion(CFG.regionI, -1)") == 1)

# V-8 surface discipline
status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
allowed = ("prototype/js/CONFIG.js", "prototype/js/regions-defs.js",
           "prototype/js/region-defs.js", "io/", "scratch/")
dirt = [ln[3:] for ln in status.splitlines() if ln.strip()]
bad = [p for p in dirt if not (p in allowed or p.startswith(("io/", "scratch/")))]
check("V-8 dirty set within the allowed paths", not bad, "outside=%s" % bad)
no_touch = ["prototype/js/enemy.js", "prototype/js/game.js", "prototype/js/save.js",
            "prototype/js/region-manager.js", "prototype/js/daynight.js",
            "prototype/index.html"]
diff = subprocess.run(["git", "diff", HEAD] + no_touch, cwd=ROOT,
                      capture_output=True, text=True)
check("V-8 no-touch engine files byte-identical to HEAD", diff.stdout == "")
haz_head = subprocess.run(["bash", "-c", "git show %s:prototype/js/CONFIG.js | grep -c hazard" % HEAD],
                          cwd=ROOT, capture_output=True, text=True)
haz_now = subprocess.run(["grep", "-c", "hazard", str(ROOT / "prototype/js/CONFIG.js")],
                         capture_output=True, text=True)
check("V-8 hazard count unchanged from HEAD",
      haz_now.stdout.strip() == haz_head.stdout.strip(),
      "HEAD %s vs live %s" % (haz_head.stdout.strip(), haz_now.stdout.strip()))

# ------------------------------------------------------------------ V-3 ring
ring = rings(K)
check("V-3 K ring 10 rows A/B alternating", len(ring) == 10
      and [r["asset"] for r in ring] == ["whWallA" if k % 2 == 0 else "whWallB"
                                         for k in range(10)])
check("V-3 K ring row constants", all(r["wall"] == 10 and r["scale"] == 11.067
      and r["sy"] == (11.69 if r["asset"] == "whWallA" else 11.55)
      and r["sz"] == 2.40 and r["y"] == -0.2 for r in ring))
check("V-3 K ring 100 colliders r %.2f" % WR, len(kw) == 100)
rhos = [distance(point(r), kc) for r in ring]
check("V-3 ring rho == 34.0 +-0.05 all rows (strict 2dp re-derivation, NOT sec-3 literals)",
      all(abs(v - 34.0) <= 0.05 for v in rhos),
      "rho spread %.4f..%.4f" % (min(rhos), max(rhos)))
check("V-3 north row (0,-846) and south row (0,-914) exact",
      point(ring[0]) == (0.0, -846.0) and point(ring[5]) == (0.0, -914.0))
chords = [distance(point(ring[k]), point(ring[(k + 1) % 10])) for k in range(10)]
check("V-3 inter-row chord uniformity within 0.02 (target 21.0136)",
      max(chords) - min(chords) <= 0.02,
      "chords %.4f..%.4f" % (min(chords), max(chords)))
rots = [r["rotY"] for r in ring]
check("V-3 rotY = 3.14 + k*0.6283 monotonic (N->E->S->W law)",
      all(abs(rots[k] - (3.14 + 0.6283 * k)) <= 0.01 and rots[k] < rots[k + 1]
          for k in range(9)),
      "rotY[0]=%.2f rotY[9]=%.2f" % (rots[0], rots[9]))
check("V-3 x-sign north->east positive (clockwise law)",
      all(ring[k]["x"] * 34 * math.sin(math.radians(36 * k)) >= 0 for k in range(10)),
      "x %s" % [r["x"] for r in ring])

# ------------------------------------------------------------------ V-3 lane
plane = K["door"]["planeZ"]
lane_edge = min(math.hypot(max(abs(x) - 2.2, 0), z - plane) - r for x, z, r, _ in kw)
floor("V-3 lane collider-edge clearance >= 1.0", lane_edge, 1.0)
hits = [(x, z) for x, z, r, _ in kw
        if math.hypot(max(abs(x) - 2.7, 0), max(abs(z - plane) - 0.5, 0)) <= r]
check("V-3 lane window (|x|<=2.7, |z-plane|<=0.5) zero overlap", not hits,
      "hits=%d" % len(hits))
rim_north = kc[1] + K["groundRadius"]
check("V-3 plane 2m inside the north rim (J conn-law, SPEC FIX)",
      abs(plane - (rim_north - 2)) < 1e-9,
      "rim %.0f plane %.0f vs J pairs (-662/-660, -738/-740)" % (rim_north, plane))
check("V-3 spawn 8m south of plane (walk-EXIT faces south, ADJ-E geometry)",
      abs(spawn[1] - plane) == 8.0, "spawn %.0f plane %.0f" % (spawn[1], plane))

# ------------------------------------------------------------- V-3 K enemies
check("V-3 K enemies = 3 zealot + 2 ghoul",
      sum(1 for e in K["enemies"] if e["type"] == "zealot") == 3
      and sum(1 for e in K["enemies"] if e["type"] == "ghoul") == 2)
for i in range(len(kenemies)):
    for k in range(i + 1, len(kenemies)):
        floor("V-3 K enemy%d-%d mutual" % (i, k), distance(kenemies[i], kenemies[k]), 12.5)
for i, g in enumerate(kenemies):
    floor("V-3 K enemy%d to spawn" % i, distance(g, spawn), 8.0)
    check("V-3 K enemy%d to landK (same seat as spawn)" % i,
          landk == spawn, "land rows share the spawn seat by coordinate")
    floor("V-3 K enemy%d ring walk-clear" % i, K["groundRadius"] - distance(g, kc), 4.45)
    floor("V-3 K enemy%d wall edge" % i, nearest(g, kw), 4.0)
    floor("V-3 K enemy%d vs nearest prop (raw center)" % i,
          min(distance(g, point(r)) for r in krows), 5.0)

# ------------------------------------------------------------- V-3 K props
tallest = min((distance(point(a), point(b))
               for i, a in enumerate(krows) for b in krows[:i]),
              default=99.0)
floor("V-3 K props mutual (universal law, ADJ-A)", tallest, 4.0)
for n, row in enumerate(krows):
    floor("V-3 K prop%d %s ring walk-clear" % (n, row["asset"]),
          K["groundRadius"] - distance(point(row), kc), 4.0)
    floor("V-3 K prop%d %s to spawn/land" % (n, row["asset"]),
          distance(point(row), spawn), 5.0)

# ---------------------------------------------------------- boss-seat circle
nest_lair = cap["lair"]
nest = (K["center"]["x"] + nest_lair["x"], K["center"]["z"] + nest_lair["y"])
seat = nest  # V-10: the seat IS the engine-derived nest (also == lairs row)


def clear_circle(center, radii_of):
    obstacles = [(distance(center, point(row)) - radii_of(row),
                  "%s at (%.2f,%.2f)" % (row["asset"], row["x"], row["z"]))
                 for row in krows]
    obstacles += [(distance(center, (x, z)) - r, "wall at (%.2f,%.2f)" % (x, z))
                  for x, z, r, _ in kw]
    obstacles += [(distance(center, g), "enemy at (%.2f,%.2f)" % g) for g in kenemies]
    return min(obstacles)


clear_fixed, bind_fixed = clear_circle(seat, lambda row: FIXED_R[row["asset"]])
clear_row, bind_row = clear_circle(seat, lambda row: WIDTH[row["asset"]] * row["scale"] / 2)
print("V-3 boss-seat (nest=row %s) fixed-map clear %.4f m binding %s" % (seat, clear_fixed, bind_fixed))
print("V-3 boss-seat per-row-map clear %.4f m binding %s" % (clear_row, bind_row))
floor("V-3 boss-seat clear circle (fixed footprints, valspec map)", clear_fixed, 6.0)
floor("V-3 boss-seat clear circle (per-row width*scale/2 map)", clear_row, 6.0)
check("V-3 boss-seat binding is the relocated root pillar (0,-880), not a zealot",
      ("(0.00,-880.00)" in bind_fixed) or ("(0.00,-880.00)" in bind_row), "binding=%s" % bind_fixed)

# ------------------------------------------------------------- J-side seats
floor("V-3 J hook nearest prop (live regionJ)", min(distance(hook, point(r)) for r in jrows), 4.5)
floor("V-3 J hook nearest ring collider", nearest(hook, jw), 4.0)
floor("V-3 J hook nearest enemy", min(distance(hook, point(e)) for e in J["enemies"]), 5.0)
floor("V-3 J hook vs lair rows", min(distance(hook, p) for p in jLairs), 5.0)
floor("V-3 J hook vs J land rows", min(distance(hook, point(r))
      for r in J["door"]["land"].values()), 4.5)
floor("V-3 J land-in (2,-682) nearest prop (live margin, NOT the 6.32 quote)",
      min(distance(landj, point(r)) for r in jrows), 6.0)
floor("V-3 J land-in nearest ring collider", nearest(landj, jw), 4.0)
floor("V-3 J land-in nearest enemy", min(distance(landj, point(e)) for e in J["enemies"]), 5.0)
check("V-3 J land-in inside J disc with margin",
      distance(landj, jc) <= J["groundRadius"] - 1.5,
      "rho %.2f <= %.2f" % (distance(landj, jc), J["groundRadius"] - 1.5))
check("V-3 J land-in |dz| == 20 from J's own walk-out plane -662 (correction (c))",
      abs(landj[1] - (-662)) == 20.0, "dz %.1f" % abs(landj[1] - (-662)))
for pz, tag in ((J["door"]["planeZ"], "conn[8] far-wall -738"), (-662, "conn[7] mouth -662")):
    inlane = abs(hook[0]) <= 2.2 and abs(hook[1] - pz) <= 0.5
    inlane2 = abs(landj[0]) <= 2.7 and abs(landj[1] - pz) <= 0.5
    check("V-3 hook outside %s lane window" % tag, not inlane)
    check("V-3 landJ outside %s lane window" % tag, not inlane2,
          "|dx| %.1f |dz| %.0f" % (abs(landj[0]), abs(landj[1] - pz)))

# -------------------------------------------------- land INTO K + tol band
floor("V-3 walk-out land K nearest prop (law floor 5.0)",
      min(distance(landk, point(r)) for r in krows), 5.0)
whole32 = min(distance(landk, point(r)) for r in krows)
print("V-3 informational (correction (b)): whole K prop min from landK = %.2f m "
      "(sec-5's '>= 32' is summary-only; nearest prop sits 20 m south by design)" % whole32)
floor("V-3 walk-out land K nearest ring collider (correction (d) >= 9)", nearest(landk, kw), 9.0)
check("V-3 K-tol band: K north rim vs J ring south point (0,-740) == 106 +-0.5",
      abs(abs(rim_north - (-740.0)) - 106.0) <= 0.5)
k_zmax = max(max(e["z"] for e in K["enemies"]), max(r["z"] for r in krows))
j_zmin = min(min(e["z"] for e in J["enemies"]), min(r["z"] for r in jrows))
check("V-12 K rows all z <= -846, J rows all z >= -740 (structural tol band)",
      k_zmax <= -846 + 1e-9 and j_zmin >= -740 - 1e-9,
      "K max z %.2f, J min z %.2f" % (k_zmax, j_zmin))

# ------------------------------------------------------------------- V-6/V-9
tally = {}
for r in krows:
    tally[r["asset"]] = tally.get(r["asset"], 0) + 1
expect_tally = {"mourningStatue": 4, "stoneSteps": 2, "okRuinColumn": 3,
                "lanternPost": 1, "blightcap": 2, "skullPile": 2, "mossBoulder": 1}
check("V-6 non-ring tally exact", tally == expect_tally, str(tally))
check("V-6 15 non-ring + 10 ring = 25 rows", len(krows) == 15 and len(ring) == 10
      and len(K["props"]) == 25)
check("V-6 ONE crimson family: lanternPost x1 + blightcap x2",
      tally["lanternPost"] == 1 and tally["blightcap"] == 2)
rl = K["rotLair"]
check("V-6 rotLair crimson dressing", rl["light"]["color"] == 0xD85050
      and rl["pool"]["color"] == 0x1A0F12 and rl["pool"]["color2"] == 0x2A1116
      and rl["pool"]["speck"] == 0x5A2028 and rl["pool"]["radius"] == 8
      and rl["pool"]["rings"] == 5 and rl["fog"]["showWithinM"] == 70
      and rl["cullM"] == 170)
print("V-5 record: K pool textureSeed %s vs J pool textureSeed %s (J/K pair for IO)"
      % (rl["pool"]["textureSeed"], J["rotLair"]["pool"]["textureSeed"]))
check("V-9 zealot truthy, NO pattern, NO slam keys (cfgFor fall-through)",
      bool(z) and "pattern" not in z and not [k for k in z if k.startswith("slam")])
check("V-9 zealot ai1 survives intact (guardArcDeg 50)",
      z["ai1"]["guardArcDeg"] == 50)

# --------------------------------------------------------------------- V-10
check("V-10 lair.region K + flagPrefix tithecaptain",
      nest_lair["region"] == "K" and nest_lair["flagPrefix"] == "tithecaptain")
row = [l for l in K["lairs"] if l["type"] == "tithecaptain"]
check("V-10 nest == engine formula == lairs row (0,-872)",
      nest == (0.0, -872.0) and len(row) == 1
      and (row[0]["x"], row[0]["z"]) == nest,
      "nest %s row %s" % (nest, [(r["x"], r["z"]) for r in row]))
check("V-10 nest-vs-spawn 16.0 +-0.5", abs(distance(nest, spawn) - 16.0) <= 0.5,
      "%.2f" % distance(nest, spawn))
check("V-10 minions zealot cap2 int7 range5 dieOnMaster",
      cap["minions"]["asset"] == "zealot" and cap["minions"]["cap"] == 2
      and cap["minions"]["interval"] == 7.0 and cap["minions"]["range"] == 5.0
      and cap["minions"]["dieOnMasterDeath"] is True)
check("V-10 loot stolenCoin [1,3] + CFG.items.stolenCoin",
      {"mat": "stolenCoin", "n": [1, 3]} in cap["loot"] and data["hasCoin"],
      "item %s" % data["coinName"])
check("V-10 rearm 3/proximity/14 + lairRadius 16",
      cap["rearm"]["days"] == 3 and cap["rearm"]["trigger"] == "proximity"
      and cap["rearm"]["radius"] == 14 and cap["lairRadius"] == 16)

# --------------------------------------------------------------------- V-11
d95 = math.sqrt(-math.log(0.05)) / K["fogDensity"]
check("V-11 K fogDensity 0.16", K["fogDensity"] == 0.16)
check("V-11 d95 in [10.77, 10.87]", 10.77 <= d95 <= 10.87, "d95 %.4f" % d95)
jd95 = math.sqrt(-math.log(0.05)) / J["fogDensity"]
print("V-11 record: J density %.2f -> d95 %.4f (chain comparison)"
      % (J["fogDensity"], jd95))
check("V-11 ambient chain 0.045 < 0.05 < 0.055 strict",
      K["ambientLightLevel"] < J["ambientLightLevel"] < data["F"]["ambientLightLevel"],
      "%.3f < %.3f < %.3f" % (K["ambientLightLevel"], J["ambientLightLevel"],
                              data["F"]["ambientLightLevel"]))
check("V-11 fogColor veil family 0x0a0810 == J's", K["fogColor"] == 0x0A0810
      == J["fogColor"])

# --------------------------------------------------------------------- V-12
check("V-12 zealot census: exactly 3 in regionK, 0 everywhere else",
      data["census"].get("regionK") == 3
      and all(v == 0 for rk, v in data["census"].items() if rk != "regionK"),
      str(data["census"]))
check("V-12 region-defs carries NO zealot string", rd.count("zealot") == 0)
zc = subprocess.run(["grep", "-c", "zealot", str(ROOT / "prototype/js/CONFIG.js")],
                    capture_output=True, text=True)
print("V-12 record: grep -c zealot CONFIG.js = %s (3 enemy rows + zealot row key "
      "+ body/variant maps + minion asset)" % zc.stdout.strip())

# -------------------------------------------------------------- BV-6 bundle
v8 = ROOT / "prototype/builds/v8-playable.html"
print("BV-6 record: %s" % ("pre-built bundle exists (%d tithe markers)"
      % (v8.read_text(encoding="utf-8", errors="ignore").count("tithe_vaults"))
      if v8.exists() else
      "no pre-built bundle at verdict time - IO builds at close-out"))

print("\n--- %d checks; %d failures ---" % (checks, len(failures)))
for label in failures:
    print("FAIL: " + label)
sys.exit(1 if failures else 0)
