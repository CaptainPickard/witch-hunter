# CC-H2 SPEC — Garrison Keep courtyard, chained off the Lord's Hold

Sources: doc 64 slot H2 row; doc 66 recipe secs 2-4 + sec 10 (2026-11-07 sides law);
CC-H1/AD2 landed specs; engine truth censused 2026-11-07 (region-manager
tickTransition/clampEnemyToHomeSide/inOpenDoorBand, region-defs sideOfPlane/
sideIn/planeIn). Worktree: /tmp/wh-worldfeat, branch feat/world-visuals,
HEAD 24a6e95. Build: tools/build_v8.py (newest; build-tool drift law).

Art law (Nicko standing order): anchor set = art-direction/concepts/
concept-06-siege-council.png (war-table focal point, oppressive formal
mood, cold stone #3A424D / warm torch #D97B26 / gilded #F2C97D accents) +
char-04-bannerman-dark.png (blackened garrison steel, crimson banner accent
LAW: sparing crimson, weathered plate). The courtyard carries ONE warm amber
family (2 sockets); crimson appears NOWHERE this round.

## 0. Summary

regionH = fort_garrison, the garrison courtyard layer under the lord's hold
(doc 64 slot H2): flat disc r 80 centered (0, -1024), chained FURTHER -z off
regionG (the E/F chain pattern stepped by one link: E<-F became G<-H). The
door is a TWO-SIDED WALK-THROUGH BREACH in G's south curtain (B/C grammar:
physical plane on both sides, no walkFrom, no interact hook, no fade-through
interact) — the mouth is the erased pole-pair flank rows of the landed
curtain (E->F parent-aperture pattern, doc 66 sec 3). 2 bandit sentries
patrol the yard; armory/dungeon-mouth/war-table dressing frames the second
stratum. All numbers below FROZE from scratch/cc-h2/seat_scan.py +
scratch/cc-h2/props_scan.py (both ALL PASS, 29 + 100+ checks) — Devbot
re-probes, never re-derives.

## 1. THE G APERTURE — parent-region edit (2 verbatim deletions)

In CONFIG.js regionG props, delete EXACTLY these two landed rows (the south
pole flank pair of the 89-segment curtain):
  { asset: 'whWallA', x: 4.4, z: -947.92, rotY: 6.25, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
  { asset: 'whWallB', x: -4.4, z: -947.92, rotY: 0.03, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },

- NOTHING ELSE in regionG moves: the remaining 87 curtain rows, all 24
  dressing rows, the door row, spawn, land — byte-identical.
- Comment law (doc 66 sec 3 amendment-comment style): directly ABOVE the
  first remaining row (where the pair was), insert ONE comment block
  (BV-002 clarification 2026-11-07: "one comment block" = the THREE `//`
  lines below pasted as a unit; nothing else):
    // CC-H2 (doc 64 slot H2): the two south-pole flank rows ERASED 2026-11-07
    // — the garrison breach; the plane rides z -948 (regionH door row), the
    // aperture lane stays |x| <= 4 (probe: scratch/cc-h2/seat_scan.py).
- The breach leaves a 12.68 m chord gap in the curtain (the erased pair span
  x -9.35..+9.35 at z -947.92 incl. their 2.40 m thickness); its flanks taper
  naturally — no filler rows, no parapets ON G's ring line (a parapet there
  blocks the lane; props_scan shows flank rows 2.5 m off the surviving ring
  are geometrically unavoidable, so the flank dressing lives INSIDE H2, sec 3).

## 2. SPEC — regionH CONFIG row (shape on the landed sibling block)

Append AFTER the closing `},` of regionG (and before whatever follows its
block in CONFIG.js), one blank line then `regionH: { ... }` — the block
carries a sec 2-style comment header:
  // ============================== CC-H2 GARRISON KEEP ==============================
  // CC-H2 (doc 64 slot H2; doc 66 sec 2-8 recipe instance): the garrison
  // courtyard layer chained off the lord's hold (G <- H, the E/F chain
  // stepped one link). First H-chain TWO-SIDED door: the breach in G's south
  // curtain is a physical plane on BOTH sides (B/C grammar, no walkFrom/no
  // interact; suspendDepthM 4 lifts BOTH disc clamps — H1a lesson: with 0 the
  // plane sits outside both playable rims and the breach dies one-way).
  // Art anchors: concept-06-siege-council + char-04-bannerman-dark (cold
  // stone #3A424D, ONE amber family; crimson banned this round).
The row (every key byte-exact):
  regionH: {
    id: 'fort_garrison',
    name: 'Garrison Keep',
    center: { x: 0, z: -1024 },
    groundRadius: 80,                 // playRadius 78.5 (r 80 minus playerMargin 1.5)
    groundY: 0,                       // flat disc (one-active-region law)
    groundColor: 0x33363c,            // garrison slate: one step COLDER than G's 0x2f3339 (H2 = service stratum)
    groundColor2: 0x2a2d33,           // shadow secondary
    groundSeed: 1662061651,           // FRESH - differs from every landed seed (1217/1218/1219/1329/1440)
    scatter: false,                   // hand rows only
    spawn: { x: 0, z: -955 },         // just past the breach, inside the mouth throat
    gravityY: -22,                    // every landed region's value
    // sec DARKNESS: density 0.068 -> d95 = sqrt(-ln 0.05)/0.068 ~ 25.4 m; the
    // courtyard reads across its whole yard. Shared day/night clock (NO
    // constantPhase row - surface-adjacent hold stratum, doc 66 sec 2 law).
    fogColor: 0x7d8289,
    fogDensity: 0.068,
    ambientLightLevel: 0.09,
    // G<->H door (region-defs connections[6]). Shape: the CC-C2 B/C row for
    // the CONNECTION KEYS (two-sided physical plane, no walkFrom, no
    // interact), the landed E/F/H1 door rows for every DATA key (door-window
    // lane, land rows, fades). planeZ -948 = 4 m inside the H2 rim (-944),
    // 1.5 m inside G's playable south rim (-946.5): reachable BOTH ways with
    // suspendDepthM 4 (inOpenDoorBand lifts both disc clamps inside the
    // window). Arch: null (open breach). gatedTo: null (dormant-clock law
    // does not apply). NO text row (B/C precedent: no interact = no prompt).
    door: {
      planeZ: -948,
      doorX: 0,
      doorHalfWidth: 4.0,             // the breach lane |x| <= 4
      suspendDepthM: 4,               // CRITICAL: both-side reach (H1a trap)
      wallGapPadM: 0,
      land: {
        fort_garrison: { x: 0, z: -955, faceX: 0, faceZ: -1100 },   // land INTO H2 = the spawn row, facing the war-table heart
        lords_hold:    { x: 0, z: -941, faceX: 0, faceZ: -822 }     // walk-back INTO G, facing the hold heart
      },
      fadeIn: 0.3,
      fadeOut: 0.5,
      exitFadeOut: 0.8
    },
    // 2 bandit sentries (the garrison lives HERE - doc 64 H1 note law).
    // >= 8.0 m from spawn/land, mutual 21.0, >= 4.45 m walk-clear of the ring
    // (both ~30.0), every prop >= 5.0 m clear (props_scan.py).
    enemies: [
      { type: 'bandit', x: -10, z: -975 },
      { type: 'bandit', x: 11, z: -976 }
    ],
    # props: sec 3 block below verbatim.
  }

NOTE the comment style: CONFIG.js is JS — the `#`-prefixed pseudo-line above
is ONLY a notation for THIS spec; in the real file every comment is `//`.
The sec 3 block replaces that one line.

## 3. SPEC — regionH props (verbatim manifest, props_scan.py)

props: [
  // -- CC-H2 DRESSING (scratch/cc-h2/props_scan.py, ALL PASS; every row >= 4.0 m
  //    raw of BOTH rings, >= 6.0 m from spawn/land rows, >= 4.0 m mutual,
  //    >= 5.0 m from both sentries, rho <= 78.5)
  // -- armory corner (east); the 2 whCampkit rows CARRY LIGHT (lightSockets.
  //    whCampkit is LIVE: hf 0.25, intensity 3.2 — BV-001 IO adjudication
  //    2026-11-07, option b: the light law is ONE warm FAMILY, not a socket
  //    count — H1 Amendment B precedent), so the amber family is FOUR sockets:
  //    lanternPost 9.0 + banditCampfire 3.2 + whCampkit 3.2 x2.
  { asset: 'whTent', x: 44, z: -1058, rotY: 5.75, scale: 1 },
  { asset: 'whCampkit', x: 38, z: -1052, rotY: 0.5, scale: 1 },
  { asset: 'whCampkit', x: 41, z: -1064, rotY: 1.2, scale: 1 },
  { asset: 'okRuinColumn', x: 52, z: -1050, rotY: 5.9, scale: 1.4 },
  // -- dungeon mouth corner (west)
  { asset: 'stoneSteps', x: -46, z: -1064, rotY: 1.57, scale: 1.3 },
  { asset: 'skullPile', x: -50, z: -1050, rotY: 4.4, scale: 1 },
  { asset: 'b6Bones', x: -42, z: -1076, rotY: 2.4, scale: 1 },
  { asset: 'rubblePile', x: -34, z: -1072, rotY: 5.8, scale: 1.1 },
  // -- war-table hub (the H1 dais trick: no table asset in the manifest — the
  //    dais + torch pair carry the tableau v1)
  { asset: 'stoneSteps', x: 0, z: -1097, rotY: 0, scale: 1.4 },
  { asset: 'torch', x: 4, z: -1093, rotY: 0, scale: 1 },
  { asset: 'torch', x: -4, z: -1093, rotY: 0, scale: 1 },
  // -- the mid-yard sentry brazier + gate lantern + armory campkits: THE ONE
  //    AMBER FAMILY, FOUR sockets total (lightSockets.banditCampfire hf 0.55
  //    intensity 3.2 + lightSockets.lanternPost hf 0.76 intensity 9.0 +
  //    lightSockets.whCampkit hf 0.25 intensity 3.2 x2 — one warm FAMILY,
  //    H1 Amendment B law; BV-001 resolved option b 2026-11-07). Crimson
  //    banned (art anchors this round). NOTE: 'torch' has NO lightSockets
  //    row — pure dressing.
  { asset: 'banditCampfire', x: 0, z: -990, rotY: 0, scale: 1.8 },
  { asset: 'lanternPost', x: 6.5, z: -954, rotY: 4.72, scale: 2.535 },
  // -- yard scatter
  { asset: 'mossBoulder', x: 26, z: -1000, rotY: 2, scale: 2 },
  { asset: 'mossBoulder', x: -24, z: -1030, rotY: 4.9, scale: 2.2 },
  { asset: 'rubblePile', x: 58, z: -992, rotY: 3.62, scale: 1.1 },
  // -- breach throat flankers (INSIDE H2, flanking the mouth lane; every row
  //    >= 4.0 m raw of EVERY remaining G ring collider, >= 16.0 m off H2's own
  //    ring, >= 4.0 m mutual from the manifest above)
  { asset: 'okFenceStonewall', x: 10, z: -968, rotY: 0, scale: 1.2 },
  { asset: 'okFenceStonewall', x: -10, z: -968, rotY: 0, scale: 1.2 }
]
(18 rows total: 16 manifest + 2 flankers. rotY/scale values byte-exact as
printed by props_scan_output.txt — Devbot pastes that block, then runs
props_scan.py against the LANDED rows as its V-gate.)

## 4. SPEC — region-defs.js registration + connections[6] (canonical block)

(a) Registration, appended after the regionG registration line (one new line,
nothing modified):
  regions[CFG.regionH.id] = makeRegion(CFG.regionH, -1);
(side -1 = the plane-0 convention only; H sits on no plane-0 side. C0-7 law:
fort_garrison never lies ON any other connection's plane.)

(b) New connection, appended after the connections[5] block and its sides
table (shaped on the CC-C2 B/C row for the conn keys; the landed AD1/H1 rows
for the door-data keys):
  // CC-H2 garrison_keep: the FIRST TWO-SIDED chained door (B/C grammar: the
  // physical plane exists on BOTH sides - no walkFrom, no interact, no
  // gatedTo). The breach lane rides x 0 across G's erased south-pole flank
  // pair; suspendDepthM 4 lifts BOTH disc clamps (planeZ -948 vs G playable
  // rim -946.5 / H2 playable rim -945.5). Sides table (doc 66 sec 10): BOTH
  // entries LIVE here (the engine reads sideIn from either active region
  // every frame): sideOfPlane(G interior -822) = +1 = sideIn(lords_hold);
  // sideOfPlane(H interior -1024) = -1 = sideIn(fort_garrison). Land rows
  // per destination (x NOT preserved); cross fires both directions
  // (tickTransition walks connectionsOf(activeId) with planeIn true in both).
  var HD = CFG.regionH.door;
  connections.push({
    from: CFG.regionG.id,
    to: CFG.regionH.id,
    axis: 'z',
    planeCoord: HD.planeZ,
    sides: {},
    door: {
      doorX: HD.doorX,
      doorHalfWidth: HD.doorHalfWidth,
      suspendDepthM: HD.suspendDepthM,
      wallGapPadM: HD.wallGapPadM,
      arch: null,
      gatedTo: null,
      land: HD.land
    }
  });
  // SIDES TABLE (CC-H2, doc 66 sec 10 interior law): BOTH entries live.
  // sideOfPlane = z > planeCoord ? 1 : -1 (region-defs). G interior -822:
  // -822 > -948 = +1. H interior -1024: -1. sideIn(R) == sideOfPlane(R
  // interior) for EVERY member - asserted by the valspec probe both sides.
  connections[6].sides[CFG.regionG.id] = 1;
  connections[6].sides[CFG.regionH.id] = -1;

- NO changes to any existing connection. NO helper changes. game.js diff
  MUST be EMPTY (the prompt/forceCross/land/fade machinery is conn-carried;
  the two-sided cross rides tickTransition + mapPositionAcross as-is —
  engine censused 2026-11-07, region-manager lines 44-123 + 248-262).

## 5. Engine census (record-only; NO code changes)

Devbot records in scratch/cc-h2/build-note.md (does NOT change):
  - tickTransition: H walks ONE connection (conn[6], planeIn true: no
    walkFrom). G walks TWO (conn[5] walkFrom G, conn[6] planeIn-both).
  - inOpenDoorBand/holdAtLockedDoor: gatedTo null -> doorLocked always false
    -> no hold path on conn[6].
  - clampEnemyToHomeSide: sentries' home side on conn[6] = -1 (H's sides row)
    -> z -975 <= -948: never clamped.
  - The fade read: game.js line ~3097 rides tr.conn.door.exitFadeOut on the
    walk cross landing (AD1 law); fadeIn/fadeOut consumed by the interact
    path only (unused here but part of the landed field set - keep).
  - Prewarm: G-side players near the south curtain prewarm H2 (conn[6]
    nearest plane); H2-side players prewarm G everywhere in the north band.

## 6. Acceptance criteria (A-1..A-10)

A-1 regionH block in CONFIG.js: every key byte-exact per secs 2-3; groundSeed
    1662061651; NO constantPhase row; NO terrain row; scatter false.
A-2 G aperture: exactly 2 landed curtain rows deleted (byte-search count:
    regionG props = 87 wall + 24 dressing rows after; the deletion comment
    present); every other regionG row byte-identical (git diff of the regionG
    block shows ONLY the 2 deletions + the comment).
A-3 props: 18 rows pasted byte-exact from props_scan_output.txt; the light
    law asserts (BV-001 resolved option b): lightSockets-carrying props in
    regionH = banditCampfire + lanternPost + the 2 whCampkit rows ONLY —
    ONE warm amber family of 4 sockets; crimson zero.
A-4 region-defs: registration line + connections[6] block + sides table byte-
    shaped per sec 4; connectionsOf('fort_garrison') == [conn[6]];
    connectionBetween(lords_hold, fort_garrison) == conn[6].
A-5 Sides law (sec 10): probed BOTH directions with region-defs live:
    sideOfPlane(conn6, -822) == 1 == sideIn(conn6, 'lords_hold') AND
    sideOfPlane(conn6, -1024) == -1 == sideIn(conn6, 'fort_garrison').
    land rows on home sides: land.fort_garrison -955 <= -948,
    land.lords_hold -941 > -948.
A-6 Ring: 48 wall rows / 384 colliders (wall 8); the ONLY collider-free
    bearing arc is the mouth's (bearing 82.8..97.2 empty; every octant >= 8);
    0 colliders inside the window strip (|x| <= 4, |z + 948| <= 3); lane
    samples >= 1.0 m clear; every row |hypot(x, z + 1024) - 80| <= 0.6.
A-7 G aperture post-erase: 0 remaining G colliders within 1.5 m of the lane
    samples (x -4..4, z -951..-945); the erased pair's byte strings appear
    NOWHERE in CONFIG.js.
A-8 Clearances (props_scan.py re-run against LANDED rows): every prop >= 4.0
    raw of both rings, >= 6.0 spawn/land, >= 4.0 mutual, >= 5.0 sentries,
    rho <= 78.5; flankers >= 16.0 off the H2 ring.
A-9 Enemies: 2 bandit rows exact; mutual 21.0 >= 12.5; spawn-sep >= 8.0;
    walk-clear of the G↔H plane band (neither sentry inside the window lane).
A-10 Build: python3 tools/build_v8.py IN THE WORKTREE; v8-playable.html
    contains a NEW title stamp + the string 'fort_garrison'; children commit
    NOTHING (NO-GIT clause); IO is the sole git gatekeeper.

NO harness runs, NO headless browser smoke tests - Nicko's playtest is the
acceptance bar; Testerbot's verdict is the code-QA gate.

## 7. Notes

- Every dimension NOT printed here is inherited from the landed siblings
  (gravityY -22, fade triple 0.3/0.5/0.8, wall colliders r 0.45).
- PROPOSED tunables for Nicko's playtest: fog density 0.068, sentry seats,
  the flanker seats. All are single-line edits later.
- The breach throat visual: G-side flare (erased 12.68 m chord) + H2-side
  24.8 m arc (i=0/49 omitted) align on x 0; the okFenceStonewall flankers
  frame the throat INSIDE H2.
