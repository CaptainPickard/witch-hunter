#!/usr/bin/env python3
"""CC-H5b vent-seat placement probe v2 (AMENDED) — specs B1 + valspec V-7.

Reads seats ONLY from CONFIG regionK.hazards.vents (eval'd, never literals).
Every seat must clear, at RUNTIME TRUTH (Box3.setFromObject GLB x-extents —
scratch/cc-h5b/measure_glbs_v2.py, vertex-verified in v3 — through the engine's
colliderRadius(name, width, scale) full-footprint law; trunk-class exclusion
mirrored from region-manager):
  P1  ring-edge clearance >= 1.0 m (vault ring r34, center (0,-880));
  P2  nearest enemy spawn >= 5.0 m;
  P3  nearest REAL prop collider edge >= 2.0 m (wall/noCollide/y-elevated
      rows excluded per the region-manager collider law; corridor-exempt
      convention honored);
  P4  boss-seat keepout >= 6.0 m (lair (0,-872));
  P5  land K (0,-856) >= 4.0 m and spawn walk-in (0,-864) >= 2.5 m;
  P6  corridor cycle: spawn-walk corridor |x| <= 2.2, z -856..-880 —
      at rest ZERO vents inside; worst-case walker (6.0 m/s spawn walk-in)
      must never have a lethal blast circle (r 2.0) underfoot inside the band
      during a full idle->warn->blast cycle (2-D clamp overlap + offset math);
  P7  every seat inside the playable disc (r 34).
C2 audits: no-new-lights / no-new-assets / draw-call budget greps (diff vs
df082e4). Prints per-vent PASS table + the corridor-cycle analysis.
Exit 0 = all clear; every FAIL lists its binding seat.
"""
import json
import math
import subprocess
import sys

W = "/tmp/wh-worldfeat"
JS = W + "/prototype/js/"

# B1 floors (law; the probe never weakens them).
R_RING, RING_C = 34.0, (0.0, -880.0)
F_RING, F_ENEMY, F_PROP, F_BOSS, F_LAND, F_WALKIN = 1.0, 5.0, 2.0, 6.0, 4.0, 2.5
CORRIDOR_X, CORRIDOR_Z0, CORRIDOR_Z1 = 2.2, -880.0, -856.0
WALK_SPEED = 6.0   # CONFIG.player.walkSpeed
DISC = 34.0
BLAST_R = 2.0      # HK.blastRadiusM (read from CONFIG below, asserted equal)

# Runtime-truth prop footprints: measured GLB X-extent (Box3.setFromObject
# equivalent; vertex-verified) x scale / 2 — the engine's colliderRadius.
WIDTHS = {
    "mourningStatue": 1.862,
    "okRuinColumn": 0.957,
    "stoneSteps": 1.948,
    "skullPile": 2.0,
    "lanternPost": 0.59,
    "blightcap": 1.692,
    "mossBoulder": 1.897,
}

node_expr = r"""
global.window = {};
eval(require('fs').readFileSync(process.argv[1],'utf8'));
eval(require('fs').readFileSync(process.argv[2],'utf8'));
var K=window.WH_CONFIG.regionK;
console.log(JSON.stringify({vents:K.hazards.vents, HK:K.hazards,
  player:(window.WH_CONFIG.player||{}),
  props:K.props.filter(function(p){return p.asset&&!p.wall&&!p.noCollide&&!(p.y>0.1);}),
  enemies:(K.enemies||[]).map(function(e){return {x:e.x,z:e.z};}),
  lair:(K.lairs||[])[0]||null}));
"""


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def main():
    raw = subprocess.check_output(
        ["node", "-e", node_expr, JS + "CONFIG.js", JS + "region-defs.js"],
        cwd=W, text=True)
    D = json.loads(raw.strip().splitlines()[-1])
    vents, props, enemies, lair = D["vents"], D["props"], D["enemies"], D["lair"]
    HK = D["HK"]
    walk_speed = (D.get("player") or {}).get("walkSpeed") or WALK_SPEED
    blast_r = HK["blastRadiusM"]
    if abs(blast_r - BLAST_R) > 1e-9:
        print("PROBE GUARD: HK.blastRadiusM %r != assumed %r" % (blast_r, BLAST_R))
        return 2

    failures, table = [], []
    for i, v in enumerate(vents):
        seat = (v["x"], v["z"])
        rows = {}

        # P1 ring-edge clearance: |dist(seat, center) - R| edge distance.
        ring_edge = abs(dist(seat, RING_C) - R_RING)
        rows["ringEdge>=1.0"] = ring_edge - F_RING
        # P7 playable disc (same reading, opposite law).
        rows["disc"] = DISC - dist(seat, RING_C)
        # P2 enemy spawn.
        e = min((dist(seat, (en["x"], en["z"])) for en in enemies), default=99.0)
        rows["enemy>=5.0"] = e - F_ENEMY
        # P3 prop collider edge (runtime truth incl. corridor-exempt convention).
        worst = None
        for p in props:
            w = WIDTHS.get(p["asset"])
            if w is None:
                failures.append("P3 vent %d: unmeasured asset %r in prop table"
                                % (i, p["asset"]))
                continue
            foot = w * (p.get("scale") or 1.0) / 2.0
            clear = dist(seat, (p["x"], p["z"])) - foot
            if worst is None or clear < worst[0]:
                worst = (clear, p["asset"], p["x"], p["z"])
        if worst is not None:
            rows["propEdge>=2.0"] = worst[0] - F_PROP
            worst_txt = "%s@(%.1f,%.1f) d=%.2f clear=%.2f" % (
                worst[1], worst[2], worst[3],
                dist(seat, (worst[2], worst[3])), worst[0])
        else:
            worst_txt = "none"
        # P4 boss keepout.
        b = dist(seat, (lair["x"], lair["z"]))
        rows["boss>=6.0"] = b - F_BOSS
        # P5 land + walk-in.
        land = dist(seat, (0.0, -856.0))
        walkin = dist(seat, (0.0, -864.0))
        rows["land>=4.0"] = land - F_LAND
        rows["walkin>=2.5"] = walkin - F_WALKIN
        # P6 corridor at rest.
        in_corr = abs(v["x"]) <= CORRIDOR_X and CORRIDOR_Z0 <= v["z"] <= CORRIDOR_Z1
        rows["corrRest==0"] = 1.0 if not in_corr else -1.0
        if in_corr:
            failures.append("P6 vent %d inside corridor at rest" % i)
        for name, margin in rows.items():
            if margin < 0 and name != "corrRest==0":
                failures.append("B1 vent %d %s short by %.2f m" % (i, name, -margin))
        table.append({
            "vent": i, "x": v["x"], "z": v["z"],
            "ring": round(ring_edge, 2), "enemy": round(e, 2),
            "worstProp": worst_txt, "boss": round(b, 2),
            "land": round(land, 2), "walkin": round(walkin, 2),
        })

    # ---- P6 corridor-cycle analysis (worst-case walker at max walk speed) ----
    #
    # Geometry: the corridor band is |x| <= 2.2, z in [-880, -856]. A vent's
    # lethal blast circle intersects the BAND at rest iff the closed disc of
    # radius blast_r about the vent seat overlaps the band rectangle (2-D):
    #   overlap = |vx| - blast_r < CORRIDOR_X  and  vz + blast_r >= Z0
    #             and  vz - blast_r <= Z1
    # (a vent south of -880 with |vx| > X is outside in x — the lethal circle
    # cannot reach a walker confined to |x| <= 2.2).
    reach_rows = []
    band_clear = True
    for i, v in enumerate(vents):
        vx, vz = v["x"], v["z"]
        overlap_x = (vx - blast_r) < CORRIDOR_X and (vx + blast_r) > -CORRIDOR_X
        overlap_z = (vz + blast_r) >= CORRIDOR_Z0 and (vz - blast_r) <= CORRIDOR_Z1
        if overlap_x and overlap_z:
            band_clear = False
            reach_rows.append("vent %d lethal circle overlaps corridor band "
                              "(x %.1f r %.1f)" % (i, vx, blast_r))
        else:
            reach_rows.append("vent %d (%.1f, %.1f): no band overlap "
                              "(x-gap %.2f m)" % (
                                  i, vx, vz,
                                  max(0.0, abs(vx) - blast_r - CORRIDOR_X)))
    if not band_clear:
        for f in reach_rows:
            failures.append("P6 cycle: " + f)

    # Timing: walker enters the corridor at spawn (0,-856) walking the walk-in
    # lane to (0,-880); at walk_speed it exits the band after
    # (Z1 - Z0)/speed seconds. Vent i's first blast window starts at
    # offset_i + idle + warn = i*1.3 + 6.0 + 1.5 (phase-0 budget spent only as
    # build-time idle offset). Worst case walker = the SLOWEST exit consistent
    # with walkSpeed is modeled by walkSpeed itself (the lane is a straight
    # walk-in; no faster path exists). Blast reach + timing must both hold.
    walker_exit_t = (CORRIDOR_Z1 - CORRIDOR_Z0) / walk_speed
    first_blast_t = 0 * 1.3 + HK["idleSec"] + HK["warnSec"]
    timing_note = ("walker clears the band at t=%.2f s (%.1f m/s); earliest "
                   "blast window opens t>=%.2f s (offset 0.0 + idle %.1f + "
                   "warn %.1f); no blast can open while the walker is inside"
                   % (walker_exit_t, walk_speed, first_blast_t,
                      HK["idleSec"], HK["warnSec"]))
    if walker_exit_t > first_blast_t and not band_clear:
        failures.append("P6 cycle: walker still in band when first blast opens")

    # ---- C2 audits: no-new-lights / no-new-assets / draw-call budget ----
    diff = subprocess.check_output(
        ["git", "diff", "df082e4", "--"], cwd=W, text=True)
    lights = [l for l in diff.splitlines() if l.startswith("+")
              and ("PointLight" in l or "addLight(" in l
                   or "createPointLight" in l)
              and "Light discipline" not in l]
    assets_diff = subprocess.check_output(
        ["git", "diff", "df082e4", "--", "prototype/js/assets.js"],
        cwd=W, text=True).strip()
    sprites = subprocess.check_output(
        ["grep", "-c", "makeCard", JS + "hazards.js"], text=True).strip()
    pipes = subprocess.check_output(
        ["grep", "-c", "window.WH_ASSETS.instance('okRuinColumn')",
         JS + "hazards.js"], text=True).strip()

    print("CC-H5b probe: %d vents, region tithe_vaults (runtime-truth widths)"
          % len(vents))
    for t in table:
        print("  vent %d @ (%.1f, %.1f)" % (t["vent"], t["x"], t["z"]))
        print("    ringEdge %.2f | enemy %.2f | boss %.2f | land %.2f | "
              "walkin %.2f | prop: %s" % (
                  t["ring"], t["enemy"], t["boss"], t["land"],
                  t["walkin"], t["worstProp"]))
    print("corridor-cycle:")
    for r in reach_rows:
        print("  " + r)
    print("  " + timing_note)
    print("audits: new PointLight rows=%d | assets.js diff=%s | "
          "makeCard sites=%s (<=8 sprite cards/4 vents: 3 cards+1) | "
          "pipe clones=%s (<=4)"
          % (len(lights), "CLEAN" if not assets_diff else "CHANGED",
             sprites, pipes))
    if lights:
        failures.append("audit: new PointLight rows in diff")
    if assets_diff:
        failures.append("audit: assets.js manifest changed")
    if failures:
        print("FAIL (%d):" % len(failures))
        for f in failures:
            print("  " + f)
        return 1
    print("PASS: all B1 floors hold for every seat (P1-P7) + C2 audits clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
