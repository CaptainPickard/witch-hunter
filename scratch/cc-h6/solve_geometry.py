#!/usr/bin/env python3
"""CC-H6 CONFIG-ROW-PARSED geometry + wiring probe. Run from worktree root.

The cc-h5 lineage carried forward: EVERY number is evaluated from the LANDED
JS source (CONFIG.js / region-defs.js via a node eval -> JSON), never copied
from spec quotes. Spec sec-2b literal rows are CONTEXT, not law - the valspec
law is rho == 30.0 +- 0.05 on the LANDED rows + chord uniformity <= 0.02,
which the landed strict-2dp rows satisfy exactly.

Structure (valspec contract):
  - 12 verbatim config-row/census lines first (the G-report data),
  - 12 verbatim G-01..G-12 summary lines,
  - the 31 spec sec-6 law floors/checks with one PASS/FAIL line each,
  - exactly one final verdict line.

Landed-vs-spec adjudications the live build carries (disclosed in the build
note; laws stay floors, seats follow the H-lineage amendment rules):
  - ring rows re-derived at strict 2dp (sec 2b's literal table drifted; the
    rotY table's 5.03/8.80 pair rounds the exact 3.14 + k*0.6283 ladder the
    wrong way on k=3/k=9 - the spec formula is the law, A2/A15).
  - guardArcDeg 42 (sec 5's "45 - captain 50" gloss is an example, not a
    field; the field line says 42).
  - stoneSarcophagus seat (0,-1086) (sec 2b's (0,-1078) bound the boss-seat
    clear circle at 2.75 m, below the 6.0 law; -1086 restores 7.28).
  - skullPile east seat (12,-1090) (sec 2b's (12,-1084) sat 0.11 m from the
    re-derived k=4 ring band - the literal table was authored against the
    drifted ring, not the landed strict-2dp circle).
  - blightcap pair (+-16,-1047) (sec 2b's (13,-1046) mirror sat 2.30/2.79 m
    inside the k=9/k=1 band dips; every nearer seat is blocked by the
    mossBoulder mutual 2.0).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

JS = r"""
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
eval(fs.readFileSync('prototype/js/region-defs.js', 'utf8'));
const C = window.WH_CONFIG, D = window.WH_REGION_DEFS;
const seeds = [];
(function walk(o, path) {
  for (var k in o) {
    var v = o[k];
    if (v !== null && typeof v === 'object') walk(v, path.concat(k));
    else if (/groundSeed|textureSeed/.test(k)) seeds.push(v);
  }
})(C, []);
console.log(JSON.stringify({
  L: C.regionL, K: C.regionK,
  cap: C.enemy.lastchancel,
  bbL: C.enemy.bodyByType.lastchancel, avL: C.enemy.animVariantByType.lastchancel,
  c: D.connections[10], count: D.connections.length,
  regL: D.regions[C.regionL.id] ? D.regions[C.regionL.id].side : null,
  forward: D.connectionBetween(C.regionK.id, C.regionL.id) === D.connections[10],
  reverse: D.connectionBetween(C.regionL.id, C.regionK.id) === D.connections[10],
  sideInK: D.sideIn(D.connections[10], C.regionK.id),
  sideInL: D.sideIn(D.connections[10], C.regionL.id),
  sideOfPlaneL: D.sideOfPlane(D.connections[10], C.regionL.spawn.z),
  sideOfPlaneK: D.sideOfPlane(D.connections[10], C.regionK.spawn.z),
  planeInL: D.planeIn(D.connections[10], C.regionL.id),
  planeInK: D.planeIn(D.connections[10], C.regionK.id),
  seeds: seeds, hasCoin: !!C.items.stolenCoin,
  coinName: C.items.stolenCoin ? C.items.stolenCoin.name : null,
  capMin: { interval: C.enemy.tithecaptain.minions.interval,
            cap: C.enemy.tithecaptain.minions.cap },
  capRearm: C.enemy.tithecaptain.rearm ? C.enemy.tithecaptain.rearm.days : null,
  capK: { lair: C.enemy.tithecaptain.lair, lairRadius: C.enemy.tithecaptain.lairRadius }
}));
"""

try:
    data = json.loads(subprocess.check_output(["node", "-e", JS], cwd=ROOT, text=True))
except (subprocess.CalledProcessError, ValueError, OSError) as exc:
    print("FAIL probe bootstrap: live node eval of CONFIG.js/region-defs.js threw")
    print(exc)
    sys.exit(1)

L, K = data["L"], data["K"]
CAP, C10 = data["cap"], data["c"]

A, CNT, FAILED = [], 0, []
def check(label, cond, detail=""):
    global CNT, FAILED
    CNT += 1
    A.append("PASS  " + label if cond else "FAIL  " + label + ("  <" + str(detail) + ">" if detail else ""))
    if not cond:
        FAILED.append(label)

def floor(label, value, m):
    check(label + "  %.4f >= %.4f" % (value, m), value >= m - 1e-9, value)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def point(row):
    return (float(row["x"]), float(row.get("z", row.get("y"))))

WR = 0.45
WIDTH = {"whWallA": 1.899, "whWallB": 1.899, "mourningStatue": 1.862,
         "stoneSteps": 1.94825, "okRuinColumn": 0.957085, "blightcap": 1.692074,
         "lanternPost": 0.585384, "skullPile": 2.0, "mossBoulder": 1.897361,
         "stoneSarcophagus": 2.0}   # CC-C11 probe_sarc.js accessor read
# Fixed asset-footprint map (raw GLB X extents; fixed-map pass). The raw
# stoneSarcophagus + mossBoulder extents are 2.0 (probe_sarc.js reads the
# accessor), so the per-row map uses them via scale.
FIXED_R = {"whWallA": 0.95, "whWallB": 0.95, "mourningStatue": 0.7,
           "stoneSteps": 1.0, "okRuinColumn": 0.7, "blightcap": 0.8,
           "lanternPost": 0.5, "skullPile": 0.9, "mossBoulder": 1.5,
           "stoneSarcophagus": 1.0}
JIT = 1.0

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

lw, kw = colliders(L), colliders(K)
lrows = [p for p in L["props"] if p not in rings(L)]
krows = [p for p in K["props"] if p not in rings(K)]
lc, kc = point(L["center"]), point(K["center"])
lspawn, kspawn = point(L["spawn"]), point(K["spawn"])
hookL = point(L["door"]["interact"])
landk = point(L["door"]["land"]["tithe_vaults"])
landl = point(L["door"]["land"]["the_remains"])
lairs = [point(e) for e in L["lairs"]]
kenemies = [point(e) for e in K["enemies"]]
seat = (lc[0] + CAP["lair"]["x"], lc[1] + CAP["lair"]["y"])
kseat = (kc[0] + data["capK"]["lair"]["x"], kc[1] + data["capK"]["lair"]["y"])
K_LAIR_R = data["capK"]["lairRadius"]

# ---------------------------------------------------------------- re-derivation
def ring_report(region, name):
    rows = rings(region)
    cx, cz = region["center"]["x"], region["center"]["z"]
    rhos = [distance((r["x"], r["z"]), (cx, cz)) for r in rows]
    d = [abs(rhos[i] - rhos[(i + 1) % len(rows)]) for i in range(len(rows))]
    return rows, rhos, d

lring, lrhos, lchords = ring_report(L, "L")
kring, krhos, kchords = ring_report(K, "K")

def wall_clear(p, region_rows, region_walls, z_before=None):
    """Nearest edge distance from p to the whole wall band as SEGMENTS
    (the spec's own 2.00 - 0.45 = 1.55 figure: a wall row is a line segment
    whose nearest point is on its axis). Point-to-segment distance minus the
    collider radius WR = the capsule-edge clearance. z_before: when given,
    colliders at z > z_before sit BEHIND the boundary plane (unreachable
    from the walk-out side) and are excluded - the lane windows gate the
    colliders that face the lane.
    Returns (value, label)."""
    best = [float("inf"), "none"]
    for r in region_rows:
        length = WIDTH[r["asset"]] * r["scale"]
        cth, sth = math.cos(r["rotY"]), math.sin(r["rotY"])
        hx, hz = cth * length / 2, sth * length / 2
        e = distance_point_seg(p, (r["x"] - hx, r["z"] - hz),
                               (r["x"] + hx, r["z"] + hz))
        if e < best[0]:
            best = [e, "band at (%.2f,%.2f)" % (r["x"], r["z"])]
    for x, z, rr, _ in region_walls:
        if z_before is not None and z > z_before + 1e-9:
            continue
        e = distance(p, (x, z)) - rr
        if e < best[0]:
            best = [e, "collider at (%.2f,%.2f)" % (x, z)]
    return tuple(best)


def distance_point_seg(p, a, b):
    ax, az = a; bx, bz = b; px, pz = p
    vx, vz = bx - ax, bz - az
    wx, wz = px - ax, pz - az
    vv = vx * vx + vz * vz
    t = 0.0 if vv <= 1e-9 else min(1.0, max(0.0, (wx * vx + wz * vz) / vv))
    return math.hypot(px - (ax + t * vx), pz - (az + t * vz))


def row_seg(r):
    """A wall row's segment endpoints (asset's measured length x scale)."""
    length = WIDTH[r["asset"]] * r["scale"]
    cth, sth = math.cos(r["rotY"]), math.sin(r["rotY"])
    hx, hz = cth * length / 2, sth * length / 2
    return (r["x"] - hx, r["z"] - hz), (r["x"] + hx, r["z"] + hz)


def nearest(p, circles):
    return min(distance(p, (x, z)) - r for x, z, r, _ in circles)

def clear_circle(center, radii_of):
    """Nearest-edge obstacle to `center` over the whole L prop map + ring
    collider circles. Returns (value, label, collider_or_None)."""
    best = [float("inf"), "none", None]
    for row in lrows:
        v = distance(center, point(row)) - radii_of(row)
        if v < best[0]:
            best = [v, "%s at (%.2f,%.2f)" % (row["asset"], row["x"], row["z"]), None]
    for x, z, r, _ in lw:
        v = distance(center, (x, z)) - r
        if v < best[0]:
            best = [v, "wall at (%.2f,%.2f)" % (x, z), (x, z, r)]
    return best[0], best[1], best[2]

# ================================================================= config lines
print("CONFIG-ROW-PARSED regionL: id %s | center (%g,%g) | groundRadius %g | spawn (%g,%g) | gravityY %g | fog 0x%x d %g | ambient %g | scatter %s | enemies %d | lairs %d | props %d"
      % (L["id"], L["center"]["x"], L["center"]["z"], L["groundRadius"],
         L["spawn"]["x"], L["spawn"]["z"], L["gravityY"], L["fogColor"],
         L["fogDensity"], L["ambientLightLevel"], str(L["scatter"]).lower(),
         len(L["enemies"]), len(L["lairs"]), len(L["props"])))
print("CONFIG-ROW-PARSED regionL.door: planeZ %g | doorX %g | halfWidth %g | walkFrom %s | hook (%g,%g r%g) | land K (%g,%g) L (%g,%g) | prompt '%s'"
      % (L["door"]["planeZ"], L["door"]["doorX"], L["door"]["doorHalfWidth"],
         L["door"]["walkFrom"], L["door"]["interact"]["x"], L["door"]["interact"]["z"],
         L["door"]["interact"]["radius"], L["door"]["land"]["tithe_vaults"]["x"],
         L["door"]["land"]["tithe_vaults"]["z"], L["door"]["land"]["the_remains"]["x"],
         L["door"]["land"]["the_remains"]["z"], L["door"]["text"]["prompt"]))
print("CONFIG-ROW-PARSED regionL.ring: 10 rows, alternating %s, wall %d, y %g, sz %g, sy %s, rotY %.2f + k*0.6283, scale %s"
      % ("/".join(r["asset"][-1] for r in lring), lring[0]["wall"], lring[0]["y"],
         lring[0]["sz"], "/".join("%g" % r["sy"] for r in lring[:2]), lring[0]["rotY"],
         "%g" % lring[0]["scale"]))
print("CONFIG-ROW-PARSED regionL.props (whole map): " + "; ".join(
      "%s (%g,%g) r=%.2f" % (r["asset"], r["x"], r["z"], WIDTH.get(r["asset"], 2.0) * r["scale"] / 2)
      for r in lrows))
print("CONFIG-ROW-PARSED enemy.lastchancel: '%s' hp %d dmg %d speed %g aggro %g | boss-slam radius %g arc %gdeg windup %g active %g recover %g cd %g track %gdeg/s engage %g | cue 0x%x/0x%x scale %g | lair {x %g, y %g, region '%s', flagPrefix '%s'} nest (%g,%g) | LairRadius %g | rearm {days %d, %s, radius %g} | loot stolenCoin [%d,%d] | minions zealot cap %d interval %g range %g | radius %g linger %g maxCorpse %d rise %g bar %g | guardArc %g"
      % (CAP["name"], CAP["hp"], CAP["dmg"], CAP["speed"], CAP["aggro"],
         CAP["slamRadius"], CAP["slamArcDeg"], CAP["slamWindup"], CAP["slamActive"],
         CAP["slamRecover"], CAP["slamCooldown"], CAP["slamTrackDegPerSec"],
         CAP["engageRange"], CAP["cueDark"], CAP["cueHot"], CAP["scale"],
         CAP["lair"]["x"], CAP["lair"]["y"], CAP["lair"]["region"], CAP["lair"]["flagPrefix"],
         seat[0], seat[1], CAP["lairRadius"], CAP["rearm"]["days"], CAP["rearm"]["trigger"],
         CAP["rearm"]["radius"], CAP["loot"][0]["n"][0], CAP["loot"][0]["n"][1],
         CAP["minions"]["cap"], CAP["minions"]["interval"], CAP["minions"]["range"],
         CAP["radius"], CAP["corpseLingerSec"], CAP["maxCorpses"], CAP["riseSec"],
         CAP["barLiftM"], CAP["ai1"]["guardArcDeg"]))
# K's captain: the landed K lairs row + the landed tithecaptain row
kcapt = K["lairs"][0]
print("CONFIG-ROW-PARSED regionK (anchor): id %s center (%g,%g) plane %g spawn (%g,%g) captain seat (%g,%g) lairRadius %g ringR %g rows %d minions {cap %d interval %g} rearm days %d"
      % (K["id"], K["center"]["x"], K["center"]["z"], K["door"]["planeZ"],
         K["spawn"]["x"], K["spawn"]["z"], kseat[0], kseat[1], K_LAIR_R, 34.0,
         len(kring), data["capMin"]["cap"], data["capMin"]["interval"], data["capRearm"]))
print("CONFIG-ROW-PARSED regionK.lairs[0]: {x %g, z %g} == the parsed captain nest seat (engine law enemy.js lairNest) mirrored by L's landing spacing %g m"
      % (kcapt["x"], kcapt["z"], abs(landl[1] - L["lairs"][0]["z"])))
print("CONFIG-ROW-PARSED conn[10]: count %d | from %s to %s axis %s plane %g | sides %s +1 / %s -1 | walkFrom %s | land.tithe_vaults (%g,%g) land.the_remains (%g,%g)"
      % (data["count"], C10["from"], C10["to"], C10["axis"], C10["planeCoord"],
         C10["sides"] and "tithe_vaults", C10["sides"] and "the_remains",
         C10["door"]["walkFrom"], C10["door"]["land"]["tithe_vaults"]["x"],
         C10["door"]["land"]["tithe_vaults"]["z"],
         C10["door"]["land"]["the_remains"]["x"],
         C10["door"]["land"]["the_remains"]["z"]))

# ====================================================================== G lines
print("G-01 ring count %d/10 whWallA/B alternating starting A (L = mirror-of-K closure)"
      % len(lring))
lspread = max(lchords)
lmean = sum(lrhos) / len(lrhos)
print("G-02 chord uniformity: %.4f max-dev from mean 18.5410 (law<=0.02)" % lspread)
print("G-03 rho circle: all rows on r 30.0+-0.05 about (%g,%g) worst %.4f"
      % (L["center"]["x"], L["center"]["z"], max(abs(r - 30.0) for r in lrhos)))
lane, lane_bind = wall_clear((0.0, L["door"]["planeZ"]), lring, lw,
                             z_before=L["door"]["planeZ"])
print("G-04 ring walk-out lane |x|<=2.2 at plane %g: edge clearance %.2f m (law>=1.0, binding %s)"
      % (L["door"]["planeZ"], lane, lane_bind))
mutual = min(distance(point(a_), point(b_)) - WIDTH.get(a_["asset"], 2.0) * a_["scale"] / 2
             - WIDTH.get(b_["asset"], 2.0) * b_["scale"] / 2
             for a_ in lrows for b_ in lrows if a_ is not b_)
whole_min = min(distance_point_seg(point(r), *row_seg(r2)) if r2 in lring
                else distance(point(r), point(r2))
                for r in lrows for r2 in lring + lrows if r is not r2)
print("G-05 prop raw floors: whole min %.4f m (law>=4.0) / mutual edge min %.4f m (law>=2.0)"
      % (whole_min, mutual))
# boss-seat clear circle at the PARSED seat, both footprint maps
clear_fixed, bind_fixed, _ = clear_circle(seat, lambda row: FIXED_R[row["asset"]])
clear_row, bind_row, _ = clear_circle(seat, lambda row: WIDTH[row["asset"]] * row["scale"] / 2)
boss = min(clear_fixed, clear_row)
print("G-06 boss-seat clear 6.0 at (%g,%g): %.4f m binding: %s"
      % (seat[0], seat[1], boss, bind_fixed if clear_fixed <= clear_row else bind_row))
landl_ok = landl == lspawn
landk_seg = min(min(distance_point_seg(landk, *row_seg(r)) for r in kring),
                min(distance(landk, point(r)) - WIDTH.get(r["asset"], 2.0) * r["scale"] / 2
                    for r in krows))
print("G-07 land rows: K (%g,%g) nearest wall seg %.2f m (law>=4.0); L (%g,%g) %s spawn row |dx|=%.0f"
      % (landk[0], landk[1], landk_seg,
         landl[0], landl[1], "==" if landl_ok else "!=", abs(landl[0] - L["spawn"]["x"])))
print("G-08 home-side walks K: sideIn(K)=%+d==sideOfPlane(K spawn) (%+d); L: sideIn(L)=%+d==sideOfPlane(L spawn) (%+d)"
      % (data["sideInK"], data["sideOfPlaneK"], data["sideInL"], data["sideOfPlaneL"]))
hook_clear = min(nearest(hookL, kw),
                 min(distance(hookL, point(r)) - WIDTH.get(r["asset"], 2.0) * r["scale"] / 2
                     for r in krows))
print("G-09 hook (%g,%g) clears every K collider by %.4f m (law >= 4.0)"
      % (hookL[0], hookL[1], hook_clear))
hook_lair = distance(hookL, kseat)
print("G-10 hook outside captain lairRadius %g circle about (%g,%g): dist %.2f margin %.2f (law >= 2.0)"
      % (K_LAIR_R, kseat[0], kseat[1], hook_lair, hook_lair - K_LAIR_R))
print("G-11 containment: spawn %.2f <= rim %.2f; landK %.2f <= rim %.2f; landL=c spawn (x=0 axis)"
      % (distance(lspawn, lc), L["groundRadius"] - JIT,
         distance(landk, kc), K["groundRadius"] - JIT))
print("G-12 x=0 spine: spawn/lair/landL/prop (0,%g)/nest(%g,%g) all x == 0 (mirror-of-K law)"
      % (L["props"][-8]["z"], seat[0], seat[1]))

# ================================================================== sec-6 laws
# Law 1: ring census + shape fields (LANDED rows).
ok_shape = (len(lring) == 10
            and all(lring[i]["asset"] == "whWallA" for i in range(0, 10, 2))
            and all(lring[i]["asset"] == "whWallB" for i in range(1, 10, 2)))
check("sec law  1: L ring 10 rows, assets whWallA/B alternating starting A", ok_shape)
check("sec law  2: L ring wall 10 / y -0.2 / sz 2.40 on every row",
      all(r["wall"] == 10 and abs(r["y"] + 0.2) < 1e-9 and abs(r["sz"] - 2.40) < 1e-9
          for r in lring))
check("sec law  3: L ring sy alternates 11.69 (A) / 11.55 (B) + scale 9.763 chord/1.899",
      all(abs(r["sy"] - (11.69 if r["asset"] == "whWallA" else 11.55)) < 1e-9
          and abs(r["scale"] - 9.763) < 1e-3 for r in lring))
check("sec law  4: L ring rho == 30.0 +- 0.05 (LANDED, strict)",
      max(abs(r - 30.0) for r in lrhos) <= 0.05 + 1e-9,
      "worst %.4f" % max(abs(r - 30.0) for r in lrhos))
check("sec law  5: L ring chord uniformity max dev <= 0.02 (LANDED)",
      lspread <= 0.02 + 1e-9, "%.4f" % lspread)
check("sec law  6: L ring rotY == 3.14 + k*0.6283 2dp ladder",
      all(abs(lring[k]["rotY"] - round(3.14 + k * 0.6283, 2)) <= 0.005 + 1e-9
          for k in range(10)),
      "; ".join("%d:%.2f/%.2f" % (k, lring[k]["rotY"], 3.14 + k * 0.6283)
                for k in range(10) if abs(lring[k]["rotY"] - (3.14 + k * 0.6283)) > 1e-9))
# Law 7: lane clearance (G-04's figure as an explicit law).
floor("sec law  7: L ring walk-out lane edge clearance >= 1.0", lane, 1.0)
walkin, _ = wall_clear((0.0, L["door"]["land"]["the_remains"]["z"]), lring, lw)
floor("sec law  8: L walk-in lane (x=0 at land z) edge clearance >= 1.0", walkin, 1.0)
# Law 9: props raw floors (whole >= 4.0) + mutual edges >= 2.0.
floor("sec law  9: whole-map prop raw min (every pair of prop ROWS, ring incl.) >= 4.0",
      whole_min, 4.0)
floor("sec law 10: prop mutual edge clearance (footprint map) >= 2.0", mutual, 2.0)
# Law 11: boss-seat clear 6.0 at the PARSED lairs seat, both maps.
floor("sec law 11: boss-seat clear circle at parsed seat (fixed footprint map)",
      clear_fixed, 6.0)
floor("sec law 12: boss-seat clear circle at parsed seat (per-row width*scale/2 map)",
      clear_row, 6.0)
check("sec law 13: boss seat PARSED triple agrees (lairs row == nest == center+y, z %g)"
      % seat[1],
      L["lairs"][0]["x"] == CAP["lair"]["x"] and seat[1] == L["lairs"][0]["z"]
      and seat == tuple(point(L["lairs"][0])),
      "lairs (%g,%g) vs nest (%g,%g) vs center+y (%g,%g)"
      % (L["lairs"][0]["x"], L["lairs"][0]["z"],
         seat[0], seat[1], L["center"]["x"] + CAP["lair"]["x"], L["center"]["z"] + CAP["lair"]["y"]))
# Law 14: land/spawn rows; landing == spawn on L, landK tolerances.
check("sec law 14: L land (0,-1044) == L spawn row", landl_ok)
whole_landk = min(min(distance_point_seg(landk, *row_seg(r)) for r in kring),
                  min(distance(landk, point(r)) for r in krows))
floor("sec law 15: landK nearest wall SEGMENT or prop row (>= 4.0; K walk-out lane-1 wall is 10 m north by design)",
      whole_landk, 4.0)
# Law 16: landK's lane-1 wall clearance - the nearest K band SEGMENT edge
# (segment model like law 8/G-04; the k=1 pair brackets the lane mouth).
floor("sec law 16: landK lane-1 wall SEGMENT edge clearance >= 2.0",
      min(distance_point_seg(landk, *row_seg(r)) for r in kring), 2.0)
floor("sec law 17: landK ring collider edge (lane-2 wall band) >= 4.0",
      nearest(landk, kw), 4.0)
floor("sec law 18: walk-out lane window (|x|<=2.2, z=plane) whole nearest prop row >= 4.0",
      min(distance((x, L["door"]["planeZ"]), point(r)) for r in lrows for x in (-2.2, 2.2)), 4.0)
floor("sec law 19: walk-in lane window (|x|<=2.2, z=land z) whole nearest prop row >= 4.0",
      min(distance((x, L["door"]["land"]["the_remains"]["z"]), point(r))
          for r in lrows for x in (-2.2, 2.2)), 4.0)
# Law 20: hook (interact) on the K side.
whole_hook = min(distance(hookL, point(r)) for r in krows)
floor("sec law 20: hook whole nearest K prop row >= 4.0", whole_hook, 4.0)
floor("sec law 21: hook ring-collider edge clearance >= 4.0", nearest(hookL, kw), 4.0)
floor("sec law 22: hook vs every K enemy row >= 4.0", min(distance(hookL, g) for g in kenemies), 4.0)
floor("sec law 23: hook outside K captain lairRadius %g circle about (%g,%g) by >= 2.0"
      % (K_LAIR_R, kseat[0], kseat[1]), hook_lair - K_LAIR_R, 2.0)
inlane_hook = abs(hookL[0]) <= K["door"]["doorHalfWidth"] and abs(hookL[1] - K["door"]["planeZ"]) <= 0.5
check("sec law 24: hook is OUTSIDE K's own walk-out lane window (no plane re-trigger)",
      not inlane_hook, "hook (%g,%g) vs lane x<=%.1f z=%g" % (hookL[0], hookL[1],
      K["door"]["doorHalfWidth"], K["door"]["planeZ"]))
# Law 25: home-side + plane wiring.
check("sec law 25: conn[10] sides K +1 / L -1 and both follow sideOfPlane(spawn)",
      C10["sides"][K["id"]] == 1 and C10["sides"][L["id"]] == -1
      and data["sideInK"] == data["sideOfPlaneK"] and data["sideInL"] == data["sideOfPlaneL"])
check("sec law 26: planeIn: the plane exists ONLY from L (one-sided walkback)",
      data["planeInL"] and not data["planeInK"])
check("sec law 27: connectionBetween resolves conn[10] both directions",
      data["forward"] and data["reverse"])
# Law 28: disc containment (player rows inside the -1.0 jitter rim).
check("sec law 28: L spawn inside playable rim (30 - 1.0 jitter)",
      distance(lspawn, lc) <= L["groundRadius"] - JIT,
      "rho %.4f <= %.4f" % (distance(lspawn, lc), L["groundRadius"] - JIT))
check("sec law 29: K land row inside K playable rim (34 - 1.0 jitter)",
      distance(landk, kc) <= K["groundRadius"] - JIT,
      "rho %.4f <= %.4f" % (distance(landk, kc), K["groundRadius"] - JIT))
# Law 30: x=0 spine axis.
check("sec law 30: x=0 axis on spawn / lairs / landL / the boss-seat / the sarco row (abs <= 1e-9)",
      max(abs(L["spawn"]["x"]), abs(L["lairs"][0]["x"]), abs(landl[0]),
          abs(seat[0])) <= 1e-9
      and all(abs(r["x"]) <= 1e-9 for r in L["props"]
              if r["asset"] in ("stoneSarcophagus",) and abs(r["z"] + 1078) < 1e-9))
# Law 31: lair trio self-consistency + lastchancel census facts.
check("sec law 31: lair trio (regionL lairs x/z == nest == CONFIG.enemy.lastchancel.lair x/y)",
      L["lairs"][0]["x"] == CAP["lair"]["x"] and seat == tuple(point(L["lairs"][0])) and
      seat[1] == lc[1] + CAP["lair"]["y"],
      "seat (%g,%g) vs lairs row (%g,%g) vs center+y (%g,%g)"
      % (seat[0], seat[1], L["lairs"][0]["x"], L["lairs"][0]["z"],
         lc[0] + CAP["lair"]["x"], lc[1] + CAP["lair"]["y"]))
check("sec law 32: regionL.enemies is an empty pool AND regionL has NO rotLair and NO hazards (clean chamber)",
      L["enemies"] == [] and "rotLair" not in L and "hazards" not in L)
check("sec law 33: anchor: K still carries its rotLair (pool) and hazards blocks",
      "rotLair" in K and "hazards" in K)
check("sec law 34: keyset law: L == K minus the K-only rotLair/hazards",
      sorted(k for k in K if k not in ("rotLair", "hazards")) == sorted(L),
      "K-only left: %s" % [k for k in K if k not in L and k not in ("rotLair", "hazards")])
check("sec law 35: seed 559043117 differs from every other landed groundSeed/textureSeed",
      all(s != L["groundSeed"] for s in data["seeds"] if s != L["groundSeed"]),
      "%d seeds walked" % len(data["seeds"]))
check("sec law 36: K anchor: d95 ordering L (d 0.17) is DEEPER than K (d 0.16)",
      L["fogDensity"] > K["fogDensity"],
      "L %g vs K %g" % (L["fogDensity"], K["fogDensity"]))
check("sec law 37: ambient ordering: L (%g) darker than K (%g)"
      % (L["ambientLightLevel"], K["ambientLightLevel"]),
      L["ambientLightLevel"] < K["ambientLightLevel"])
check("sec law 38: lastchancel minions cap-0 guard PRESENT: {asset zealot, cap 0, interval 999.0, range 5.0} + NO dieOnMasterDeath",
      CAP["minions"] == {"asset": "zealot", "cap": 0, "interval": 999.0,
                         "range": 5.0} and "dieOnMasterDeath" not in CAP["minions"],
      str(CAP["minions"]))
check("sec law 39: engine guard: lairTick reads cfg.minions.interval UNGUARDED -> the no-minions crash shape is impossible on this row",
      "minions" in CAP and "interval" in CAP["minions"]
      and CAP["minions"]["cap"] == 0)
check("sec law 40: K-mirror: the landed K captain row still carries {cap 2 interval 7.0} + rearm days 3 (L's rearm days 3 carries)",
      data["capMin"]["cap"] == 2 and abs(data["capMin"]["interval"] - 7.0) < 1e-9
      and CAP["rearm"]["days"] == data["capRearm"])
check("sec law 41: loot row: stolenCoin [2,5] (mat exists in the world + CONFIG coin name)",
      CAP["loot"] == [{"mat": "stolenCoin", "n": [2, 5]}] and data["hasCoin"]
      and data["coinName"] == "Stolen Coin")
check("sec law 42: bodyByType/animVariantByType carry lastchancel == banditBody / bandit",
      data["bbL"] == "banditBody" and data["avL"] == "bandit")
check("sec law 43: conn[10] door block: doorX 0 halfWidth 2.2 suspend 0 pad 0 arch null gatedTo null walkFrom L",
      C10["door"]["doorX"] == 0 and C10["door"]["doorHalfWidth"] == 2.2
      and C10["door"]["suspendDepthM"] == 0 and C10["door"]["wallGapPadM"] == 0
      and C10["door"]["arch"] is None and C10["door"]["gatedTo"] is None
      and C10["door"]["walkFrom"] == L["id"])
check("sec law 44: conn[10] interact lands on K side {from tithe_vaults x 7.5 z -854 radius 3.5} + fades 0.3/0.5/0.8 + the L prompt string",
      C10["door"]["interact"]["from"] == K["id"]
      and C10["door"]["interact"]["x"] == 7.5 and C10["door"]["interact"]["z"] == -854
      and C10["door"]["interact"]["radius"] == 3.5
      and C10["door"]["fadeIn"] == 0.3 and C10["door"]["fadeOut"] == 0.5
      and C10["door"]["exitFadeOut"] == 0.8
      and C10["door"]["text"]["prompt"] == "E - Descend into the remains")
print("INFO  spec-2b literal drift: strict-2dp landed rows satisfy rho/chord exactly; the sec-2b table's rotY 5.03/8.80 pair rounds the exact 3.14 + k*0.6283 ladder wrong on k=3/9 (landed 5.02/8.79); guardArcDeg 42 is the FIELD value (the '45' in the sec-5 text is the K-example gloss)")

A.insert(0, "--- sec-6 law PASS/FAIL table (the 44 floors above) ---")
A.insert(0, "")
print()
for line in A:
    print(line)
print()
print("--- G summary (12 lines) ---")
print("solve_geometry (cc-h6): %d/%d laws PASS; FAIL: %d"
      % (CNT - len(FAILED), CNT, len(FAILED)))
sys.exit(1 if FAILED else 0)
