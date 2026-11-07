#!/usr/bin/env python3
"""CC-H2 Devbot build step 2: append the regionH block to CONFIG.js after the
regionG closing brace. RING ROWS pasted verbatim from seat_scan_output.txt;
props + door keys byte-shaped per io/specs/cc-h2-garrison-spec.md secs 2-3.
Run: python3 scratch/cc-h2/append_regionH.py   (from the worktree root)
"""
from pathlib import Path

ROOT = Path('/tmp/wh-worldfeat')
p = ROOT / 'prototype/js/CONFIG.js'
src = p.read_text()

# ---- 1. RING ROWS: verbatim from the frozen seat scan (48 rows) ----
seat = (ROOT / 'scratch/cc-h2/seat_scan_output.txt').read_text()
segi = seat.index('RING ROWS')
seg = seat[segi:]
ring_rows = [ln for ln in seg.splitlines() if ln.strip().startswith('{ asset')]
assert len(ring_rows) == 48, 'ring rows found: %d' % len(ring_rows)
ring_lines = ['      ' + ln.strip() + ',' for ln in ring_rows]

# ---- 2. props rows: the spec sec 3 manifest (16) + 2 flankers ----
PROP_ROWS = [
    "{ asset: 'whTent', x: 44, z: -1058, rotY: 5.75, scale: 1 },",
    "{ asset: 'whCampkit', x: 38, z: -1052, rotY: 0.5, scale: 1 },",
    "{ asset: 'whCampkit', x: 41, z: -1064, rotY: 1.2, scale: 1 },",
    "{ asset: 'okRuinColumn', x: 52, z: -1050, rotY: 5.9, scale: 1.4 },",
    "{ asset: 'stoneSteps', x: -46, z: -1064, rotY: 1.57, scale: 1.3 },",
    "{ asset: 'skullPile', x: -50, z: -1050, rotY: 4.4, scale: 1 },",
    "{ asset: 'b6Bones', x: -42, z: -1076, rotY: 2.4, scale: 1 },",
    "{ asset: 'rubblePile', x: -34, z: -1072, rotY: 5.8, scale: 1.1 },",
    "{ asset: 'stoneSteps', x: 0, z: -1097, rotY: 0, scale: 1.4 },",
    "{ asset: 'torch', x: 4, z: -1093, rotY: 0, scale: 1 },",
    "{ asset: 'torch', x: -4, z: -1093, rotY: 0, scale: 1 },",
    "{ asset: 'banditCampfire', x: 0, z: -990, rotY: 0, scale: 1.8 },",
    "{ asset: 'lanternPost', x: 6.5, z: -954, rotY: 4.72, scale: 2.535 },",
    "{ asset: 'mossBoulder', x: 26, z: -1000, rotY: 2, scale: 2 },",
    "{ asset: 'mossBoulder', x: -24, z: -1030, rotY: 4.9, scale: 2.2 },",
    "{ asset: 'rubblePile', x: 58, z: -992, rotY: 3.62, scale: 1.1 },",
    "{ asset: 'okFenceStonewall', x: 10, z: -968, rotY: 0, scale: 1.2 },",
    "{ asset: 'okFenceStonewall', x: -10, z: -968, rotY: 0, scale: 1.2 }",
]
assert len(PROP_ROWS) == 18

HEADER = (
    "\n"
    "  // ============================== CC-H2 GARRISON KEEP ==============================\n"
    "  // CC-H2 (doc 64 slot H2; doc 66 sec 2-8 recipe instance): the garrison\n"
    "  // courtyard layer chained off the lord's hold (G <- H, the E/F chain\n"
    "  // stepped one link). First H-chain TWO-SIDED door: the breach in G's south\n"
    "  // curtain is a physical plane on BOTH sides (B/C grammar, no walkFrom/no\n"
    "  // interact; suspendDepthM 4 lifts BOTH disc clamps - H1a lesson: with 0 the\n"
    "  // plane sits outside both playable rims and the breach dies one-way).\n"
    "  // Art anchors: concept-06-siege-council + char-04-bannerman-dark (cold\n"
    "  // stone #3A424D, ONE amber family; crimson banned this round).\n"
    "  regionH: {\n"
    "    id: 'fort_garrison',\n"
    "    name: 'Garrison Keep',\n"
    "    center: { x: 0, z: -1024 },\n"
    "    groundRadius: 80,                 // playRadius 78.5 (r 80 minus playerMargin 1.5)\n"
    "    groundY: 0,                       // flat disc (one-active-region law)\n"
    "    groundColor: 0x33363c,            // garrison slate: one step COLDER than G's 0x2f3339 (H2 = service stratum)\n"
    "    groundColor2: 0x2a2d33,           // shadow secondary\n"
    "    groundSeed: 1662061651,           // FRESH - differs from every landed seed (1217/1218/1219/1329/1440)\n"
    "    scatter: false,                   // hand rows only\n"
    "    spawn: { x: 0, z: -955 },         // just past the breach, inside the mouth throat\n"
    "    gravityY: -22,                    // every landed region's value\n"
    "    // sec DARKNESS: density 0.068 -> d95 = sqrt(-ln 0.05)/0.068 ~ 25.4 m; the\n"
    "    // courtyard reads across its whole yard. Shared day/night clock (NO\n"
    "    // constantPhase row - surface-adjacent hold stratum, doc 66 sec 2 law).\n"
    "    fogColor: 0x7d8289,\n"
    "    fogDensity: 0.068,\n"
    "    ambientLightLevel: 0.09,\n"
    "    // G<->H door (region-defs connections[6]). Shape: the CC-C2 B/C row for\n"
    "    // the CONNECTION KEYS (two-sided physical plane, no walkFrom, no\n"
    "    // interact), the landed E/F/H1 door rows for every DATA key (door-window\n"
    "    // lane, land rows, fades). planeZ -948 = 4 m inside the H2 rim (-944),\n"
    "    // 1.5 m inside G's playable south rim (-946.5): reachable BOTH ways with\n"
    "    // suspendDepthM 4 (inOpenDoorBand lifts both disc clamps inside the\n"
    "    // window). Arch: null (open breach). gatedTo: null (dormant-clock law\n"
    "    // does not apply). NO text row (B/C precedent: no interact = no prompt).\n"
    "    door: {\n"
    "      planeZ: -948,\n"
    "      doorX: 0,\n"
    "      doorHalfWidth: 4.0,             // the breach lane |x| <= 4\n"
    "      suspendDepthM: 4,               // CRITICAL: both-side reach (H1a trap)\n"
    "      wallGapPadM: 0,\n"
    "      land: {\n"
    "        fort_garrison: { x: 0, z: -955, faceX: 0, faceZ: -1100 },   // land INTO H2 = the spawn row, facing the war-table heart\n"
    "        lords_hold:    { x: 0, z: -941, faceX: 0, faceZ: -822 }     // walk-back INTO G, facing the hold heart\n"
    "      },\n"
    "      fadeIn: 0.3,\n"
    "      fadeOut: 0.5,\n"
    "      exitFadeOut: 0.8\n"
    "    },\n"
    "    // 2 bandit sentries (the garrison lives HERE - doc 64 H1 note law).\n"
    "    // >= 8.0 m from spawn/land, mutual 21.0, >= 4.45 m walk-clear of the ring\n"
    "    // (both ~30.0), every prop >= 5.0 m clear (props_scan.py).\n"
    "    enemies: [\n"
    "      { type: 'bandit', x: -10, z: -975 },\n"
    "      { type: 'bandit', x: 11, z: -976 }\n"
    "    ],\n"
    "    props: [\n"
    "      // -- CC-H2 DRESSING (scratch/cc-h2/props_scan.py, ALL PASS; every row >= 4.0 m\n"
    "      //    raw of BOTH rings, >= 6.0 m from spawn/land rows, >= 4.0 m mutual,\n"
    "      //    >= 5.0 m from both sentries, rho <= 78.5)\n"
    "      // -- armory corner (east); the 2 whCampkit rows CARRY LIGHT (lightSockets.\n"
    "      //    whCampkit is LIVE: hf 0.25, intensity 3.2 - BV-001 IO adjudication\n"
    "      //    2026-11-07, option b: the light law is ONE warm FAMILY, not a socket\n"
    "      //    count - H1 Amendment B precedent), so the amber family is FOUR sockets:\n"
    "      //    lanternPost 9.0 + banditCampfire 3.2 + whCampkit 3.2 x2.\n"
)

MID1 = (
    "      // -- dungeon mouth corner (west)\n"
    "      { asset: 'stoneSteps', x: -46, z: -1064, rotY: 1.57, scale: 1.3 },\n"
    "      { asset: 'skullPile', x: -50, z: -1050, rotY: 4.4, scale: 1 },\n"
    "      { asset: 'b6Bones', x: -42, z: -1076, rotY: 2.4, scale: 1 },\n"
    "      { asset: 'rubblePile', x: -34, z: -1072, rotY: 5.8, scale: 1.1 },\n"
    "      // -- war-table hub (the H1 dais trick: no table asset in the manifest - the\n"
    "      //    dais + torch pair carry the tableau v1)\n"
    "      { asset: 'stoneSteps', x: 0, z: -1097, rotY: 0, scale: 1.4 },\n"
    "      { asset: 'torch', x: 4, z: -1093, rotY: 0, scale: 1 },\n"
    "      { asset: 'torch', x: -4, z: -1093, rotY: 0, scale: 1 },\n"
    "      // -- the mid-yard sentry brazier + gate lantern + armory campkits: THE ONE\n"
    "      //    AMBER FAMILY, FOUR sockets total (lightSockets.banditCampfire hf 0.55\n"
    "      //    intensity 3.2 + lightSockets.lanternPost hf 0.76 intensity 9.0 +\n"
    "      //    lightSockets.whCampkit hf 0.25 intensity 3.2 x2 - one warm FAMILY,\n"
    "      //    H1 Amendment B law; BV-001 resolved option b 2026-11-07). Crimson\n"
    "      //    banned (art anchors this round). NOTE: 'torch' has NO lightSockets\n"
    "      //    row - pure dressing.\n"
    "      { asset: 'banditCampfire', x: 0, z: -990, rotY: 0, scale: 1.8 },\n"
    "      { asset: 'lanternPost', x: 6.5, z: -954, rotY: 4.72, scale: 2.535 },\n"
    "      // -- yard scatter\n"
    "      { asset: 'mossBoulder', x: 26, z: -1000, rotY: 2, scale: 2 },\n"
    "      { asset: 'mossBoulder', x: -24, z: -1030, rotY: 4.9, scale: 2.2 },\n"
    "      { asset: 'rubblePile', x: 58, z: -992, rotY: 3.62, scale: 1.1 },\n"
    "      // -- breach throat flankers (INSIDE H2, flanking the mouth lane; every row\n"
    "      //    >= 4.0 m raw of EVERY remaining G ring collider, >= 16.0 m off H2's own\n"
    "      //    ring, >= 4.0 m mutual from the manifest above)\n"
)

CLOSE = (
    "    ]\n"
    "  },\n"   # trailing comma: scatter block follows regionH
)

lines = []
lines += HEADER.splitlines(True)
# armory corner rows 1-4
for row in PROP_ROWS[:4]:
    lines.append('      ' + row + '\n')
lines += MID1.splitlines(True)
# remaining prop rows 5-18 (last one without trailing comma)
for row in PROP_ROWS[4:17]:
    lines.append('      ' + row + '\n')
lines.append('      ' + PROP_ROWS[17] + '\n')
lines += CLOSE.splitlines(True)
# ring wall rows go LAST inside props (after the flankers comment says they
# frame the throat; the ring is the courtyard's own wall). Per spec sec 3 the
# manifest prints in this order: 16 manifest rows then 2 flankers; the ring
# rows are separate (region ring), appended after the flankers.
# NOTE: spec sec 2 prints '# props: sec 3 block below verbatim' -> the sec 3
# block IS the props array; the RING ROWS are the courtyard wall (sec 3's
# '(48 rows pasted verbatim from seat_scan_output.txt)') and belong AFTER the
# flankers, each line byte-shaped exactly as the scan printed it.
lines += [ln + '\n' for ln in ring_lines]

block = ''.join(lines)

anchor = "      { asset: 'lanternPost', x: 6.5, z: -706, rotY: 4.72, scale: 2.535 }\n    ],\n  },\n"
assert src.count(anchor) == 1, 'regionG tail anchor not found exactly once'

# Insert after regionG's closing brace: blank line separates the blocks
new_src = src.replace(anchor, anchor + '\n' + block, 1)
p.write_text(new_src)
print('regionH block appended: %d ring lines, 18 prop rows, %d total lines now'
      % (len(ring_lines), new_src.count('\n')))
