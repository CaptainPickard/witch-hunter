# CC-C2 · Region C Shell — Forest of the Old King (doorway · gate · boundary · stub ground · tree scatter)

Change-order brief, written 2026-10-07 by IO from docs/planning/62 (design)
and docs/planning/63 (CC-C2 block). Base commit a1c258d (CC-C1 spike
landed), branch feat/world-visuals, worktree /tmp/wh-worldfeat. ONE order
at a time. Merge to dev/main = Nicko explicit call only. Always English.

## 0. WHY THIS ORDER

The doorway + gate + boundary + stub ground + tree scatter are the walkable
shell. After this order Nicko can walk from Region B through a doorway on
B's far north edge into an empty forest (Region C, "Forest of the Old
King") and playtest traversal — gated until the first Save-and-Heal.

## 1. LOCKED RULINGS (clarify form 2026-10-07, docs 62 §R-62.x)

- R-62.1 HEIGHTFIELD: real heightfield comes in CC-C4 (spike verdicts banked:
  B-TRI sampler, S=140 ~39.2k tris ~2% of budget, climb 0.6). THIS ORDER
  ships a FLAT stub ground — no heightfield code anywhere in this order.
- R-62.2 SCALE: Region C playable radius **280** (band 250-300; C center
  (0,-366); doc 62 §1 arithmetic: doorway plane z=-86, C spans z -646..-86).
- Tutorial law (binding): js/daynight.js boots DORMANT (frozen, day 0,
  daynight.js:126). The FIRST Save-and-Heal at a camp is the ONLY caller of
  beginCycle() (daynight.js:152-154; js/camp.js owns the menu). Later rests
  call nextDawn() (daynight.js:165). ANY first-sleep-gated content uses the
  same predicate !dayNight.dormant — the B/C doorway gate is exactly that,
  NO new state.
- Save law (C4): save.js WH_SAVE, CONFIG.save lsKey wh-save-v1, schema v1,
  additive blocks only. VERIFIED GENERIC: player.regionId is already saved
  (save.js:73), restored via validRegion() registry check (save.js:39-41,
  :263-264 hooks.switchRegion), the death respawn crosses regions
  (game.js:907-915: if cr.regionId !== rid switchRegion(cr.regionId)).
  restoreClock restores dormant faithfully (save.js:141-158) so the gate
  state itself survives save+load with ZERO new state. If registerRegion()
  accepts the C region, save/load of "in region C" follows FOR FREE — the
  builder must VERIFY this on the actual code and fix anything missing in
  the allowed files.
- Enemies never cross (D2 law): C's future enemies clamp to C's side of the
  B/C plane exactly as B's enemies do today (clampEnemyToHomeSide,
  region-manager.js:124-143 — this order generalizes it to the table).
- Nothing destructive: A/B keep working identically. A's boundary rows
  byte-identical. Merge to dev/main only on Nicko's call.

## 2. VERIFIED STATE BLOCK (census @ a1c258d, line anchors drift - RE-GREP)

- Regions: regionA hold_outskirts CONFIG.js:157; regionB darkwood_edge
  CONFIG.js:368 (spawn z=-45, boundary plane z=+25 SOUTH, gateM/arch params
  nearby regionB rows). region-defs.js:18-36 makeRegion + regions registry;
  adjacency at region-defs.js:37+.
- Boundary machinery: WH_REGION_DEFS.connections[0] is the ONLY connection
  (region-defs.js ~:43-47: axis 'z', planeCoord CFG.boundary.z). Clamp:
  clampPlayerPlane region-manager.js:99-121 reads connections[0] + homeSide
  (+1 A / -1 B via DEFS.regions[id].side). Radial: whClampRadial +
  whPlayRadius (region-manager.js:134-143, CFG.world.groundRadius 90
  CONFIG.js:120, playerMargin 1.5 CONFIG.js:124 — both GLOBAL today).
  Enemy hold: clampEnemyToHomeSide region-manager.js:124-143 (also uses
  CFG.regionA.id / margins). Cross mapping ~:57-72 (z placed across the
  plane). Prewarm: region-manager.js:39-86 (preWarmDistance).
- Ground: active region renders CircleGeometry(whVisualGroundRadius,
  48) at region-manager.js:1213 (flat, y=0); per-region ground texture
  canvas + repeat scaling at region-manager.js:391 (whVisualGroundRadius);
  whVisualGroundRadius = max(groundRadius, playRadius + fogMult*d95)
  region-manager.js:150-154.
- Interact chain: game.js ~1739-1830 (box pickup > corpse > gather > cook
  station). Toast convention: camp ghost refusal style, name the REASON.
- Clock: game.dayNight owned game.js:2070-2071; boots DORMANT.
- Save: player.regionId save.js:72-73, restore hooks.switchRegion wired
  game.c4 game.js:2182-2185, switchRegion game.js:921-927 (lighting + sky
  area + name banner + gate hint), death-respawn game.js:907-915.
- Vendor: prototype/threejs/vendor/three.classic.js (index.html:41); index
  script order game.js LAST (index.html:44-56 family). Bundle: build_v8.py
  concatenates js/ in index order.

## 3. SCOPE CONTRACT

TOUCH (the ONLY files this order may modify):
- prototype/js/CONFIG.js          — regionC block + boundary table +
                                    per-region groundRadius override +
                                    doorway/gate rows + stub-ground rows
                                    + fog palette rows (all new rows
                                    commented 'PROPOSED, Nicko tunes')
- prototype/js/region-defs.js     — regionC registration in the registry +
                                    the B/C connection row + adjacency +
                                    (side table extension)
- prototype/js/region-manager.js  — clamp/clampEnemyToHomeSide/whPlayRadius
                                    generalization to the connection table
                                    (behavior-preserving for A/B) + C stub
                                    ground build path + per-region tree
                                    scatter pass + doorway arch/gateM
                                    dressing + L0 glade lantern
- prototype/js/game.js            — doorway gate hook (dormant predicate +
                                    locked toast) + wire regionC into
                                    applyRegionLighting/setSkyArea paths +
                                    regionC name banner
- prototype/js/save.js            — ONLY if the generic path needs a fix;
                                    expected: zero changes
- prototype/builds/v8-playable.html — rebuilt bundle via tools/build_v8.py
                                    (ships in the same commit)
NOT TOUCH (read-only): js/daynight.js, js/camp.js (tutorial law), js/player.js,
js/enemy.js (no wolves yet), js/leveling.js, js/icons-data.js, js/assets.js
(load path only if a regionC prop id is missing — prefer not), index.html,
style.css (doorway prompt/toast reuse existing surfaces), tools/*, docs/*,
art-direction/*, io/*, scratch/*.

## 4. CRG IMPACT (run 2026-10-07 @ a1c258d, baked per law)

impact --files CONFIG.js game.js save.js region-defs.js region-manager.js
--depth 2 --max-results 15 → status ok: **161 nodes directly changed, 0
nodes impacted within 2 hops, 0 additional files affected**. Read: the
boundary generalization is contained to the five files above; no enemy /
player / camp code is in the blast radius. Corollary: if the builder finds
itself editing ANY other file, that is a spec violation, not a necessity.

## 5. IMPLEMENTATION CONTRACT

5.1 REGION REGISTRY (region-defs.js):
- Add regionC: id 'forest_of_the_old_king', name 'Forest of the Old King'.
- CONFIG.js regionC block: gravityY -22, fog 'deep-forest' palette
  (#, density ~0.030-0.037 PROPOSED — denser than B's 0.024, hides the
  r-280 edge at fog range), ambientLightLevel 0.5 PROPOSED, spawn
  (0, -96) = 10 units inside C's south rim facing north (the doorway
  deposits at z=-88; spawn is the C-LOCAL walk target), enemies []
  (nothing spawns in CC-C2), props [] for now (dressing below).
- makeRegion already copies cfg fields (region-defs.js:18-36): extend ONLY
  where the new rows need it (no signature change).

5.2 CONNECTION TABLE (region-defs.js):
- Keep connections[0] (A/B) byte-identical in intent: axis 'z',
  planeCoord CFG.boundary.z (=25), regions A side +1 / B side -1.
- Add connections[1] for B/C: axis 'z', planeCoord **-86**,
  conn.sides = { darkwood_edge: +1, forest_of_the_old_king: -1 }
  (B occupies z >= -86 of this plane, C occupies z <= -86 — doc 62 §1
  arithmetic). The connection model must support a region having DIFFERENT
  sides on DIFFERENT planes (B is -1 on plane0 and +1 on plane1; A is +1
  on plane0 and not a member of plane1) — encode sides PER-CONNECTION as
  shown, never a global side per region beyond the existing
  DEFS.regions[id].side used by today's A/B logic.
- Adjacency: B lists C (and A); C lists B. The prewarm machinery keys off
  the adjacency, generalizes unchanged.

5.3 GEOMETRY LAW + DOOR WINDOW (region-manager.js):
- FACTS: B disc center (0,-45) r90, play radius 88.5 → B's playable north
  rim is z=-133.5 at x=0. The B/C plane z=-86 is 47.5 units INSIDE B's
  disc: the point (0,-86) is legal B ground TODAY (distance 41 < 88.5), so
  the radial clamp does NOT block reaching the arch. C disc center (0,-366)
  play radius 278.5 → C's playable span at x=0 is z -87.5..-644.5, i.e.
  from C's side the plane (-86) is 1.5 units BEYOND C's radial disc:
  without help the return crossing can never fire.
- MEANING OF conn[1]: a DOOR, not a wall. The plane only exists as a
  cross-line INSIDE the door window. Outside the window NOTHING changes
  anywhere: B's north strip (z -86..-133.5, |x| > doorHalfWidth) stays
  exactly as walkable as it is today (A4), B's radial clamp unchanged,
  C's radial disc unchanged.
- CONN MODEL (general, per-connection):
  - conn row gains: door { doorX: 0, doorHalfWidth: 4 } for conn[1];
    conn[0] (A/B) gains NO door row — absent door = behavior byte-identical
    to today (wide chokepoint crossing, existing clamp logic untouched).
  - insideDoorWindow(conn, x): |x - doorX| <= doorHalfWidth.
  - Inside the window, the radial clamp is SUSPENDED for this conn's two
    member regions (both sides): this is what lets a C-side player reach
    the plane (C's radial would stop them at z=-87.5). On the B side the
    suspension is harmless (the cross fires at -86 before B's radial
    could ever bind).
  - CROSSING inside the window: crossing the plane northward
    (B side: z goes from > -86 to < -86) fires the standard cross
    convention (region-manager.js:57-72: teleport 2 units past the
    plane, z=-88, region switches to forest_of_the_old_king). Crossing
    southward inside the window (C side: z goes from < -86 to > -86)
    fires the same convention to z=-84, region darkwood_edge.
  - GATE (dormant): while dayNight.dormant is true, the northward cross
    inside the window is BLOCKED: the player is stopped AT the line
    (z=-86.0, crossing-frame hold — NOT a positional yank: a player who
    is already north of the line in B's north strip must never be
    teleported/held by this; the block only engages on the frame the
    player would cross z=-86 south-to-north). Southward movement through
    the line stays free (no dormant pocket). Interacting near the arch
    while dormant gives the reason toast (5.4).
  - clampEnemyToHomeSide: generalize per-conn so future conn rows CAN
    carry enemy home-side rules; for conn[1] in THIS order it is vacuous
    (C spawns no enemies; B's enemies are unstreamed when the region
    switches). Do not change B enemy behavior.
- The A/B side arithmetic above is the law; if the code's actual
  crossing/clamp shape differs from this description in a way that
  changes the intent, obey the code (Section 7).

5.4 THE DOORWAY (region-manager.js dressing + game.js gate):
- Props: reuse the regionB arch/gateM params family (CONFIG.js:368+ rows;
  mirror those rows' shape). Dress the arch at (0, -86) facing north
  (visual only, standing on B's ground; props are walk-through in this
  engine — the gate LOGIC is the door, not collision).
- THE GATE (game.js): the dormant block of 5.3 (stop at the line + no
  cross) implements the door while dormant. Interact near the arch while
  dormant → toast: 'Rest at a camp first - the forest beyond still
  sleeps.' (existing toast convention: name the reason, camp-ghost
  refusal style; reuse the regionB arch prompt surface family). When
  !dormant, crossing works per 5.3.
- THE HINT: setGateHint family (game.js:926) may be extended for the C
  door (PROPOSED); keep surfaces minimal.

5.5 C STUB GROUND (region-manager.js):
- Flat disc: CircleGeometry at y=-0.05 (z-fight avoidance vs B's disc,
  B's is y=0), radius per CONFIG per-region groundRadius: CFG.world has
  groundRadius 90 GLOBAL (CONFIG.js:120) — add CFG.regionC.groundRadius
  280 and make the ground build + whVisualGroundRadius + whPlayRadius read
  the ACTIVE region's groundRadius (A/B read the global default 90;
  behavior-identical). playerMargin 1.5 stays global.
- C-local ground canvas variant (new canvas painter variant, deep-forest
  palette), texture repeat scaling unchanged (region-manager.js:391 uses
  whVisualGroundRadius — verify the repeat math works for r=280; fix in
  the allowed files if the repeat is too dense/sparse at 280).
- Fog: C fog rows in CONFIG (5.1) + applyRegionLighting path (game.js)
  handles C like A/B — add the regionC branch.

5.6 TREE SCATTER FIRST PASS (region-manager.js):
- Assets: yewTree / witchwoodTree / treeStump EXACT ids (typo law), rows
  in CFG.regionC.props PROPOSED list. First pass: ~120 trees + ~20 stumps
  PROPOSED, PROPOSALS hand-placed rows (no runtime random), distance-
  culling: no props beyond ~150 units from C center (beyond fog-opaque =
  not placed; spike finding: fog hides the edge from spawn but not within
  ~60 of it — 150 << 280 keeps the ledger honest; CC-C3 does the full
  pass + ledger).
- L0 glade furniture: lantern post prop at C spawn glade.

5.7 BUNDLE + SERVING (per standing law):
- Rebuild: python3 tools/build_v8.py from repo root; bundle ships in the
  SAME commit as the source.
- Commit (git commit --author='CaptainPickard <pickard.nicko@gmail.com>'):
  'feat(cc-c2): region C shell - B/C doorway on north edge (z=-86 plane),
  tutorial-law gate (!dn.dormant) with reason toast, per-region groundRadius
  (C=280), flat stub ground y=-0.05, first tree scatter, per-conn door
  window clamp generalization (A/B behavior identical)'
  + push origin feat/world-visuals immediately.
- THEN flip 8793: python3 tools/wh_release_flip.py <new-sha> via
  python3 /tmp/dhost.py host_exec, timeout 900 (60s default kills flips
  mid-build). If releases/<sha> lacks prototype/builds/, delete husk,
  re-run. Verify: readlink /tmp/wh-playtest-share/current = RELATIVE
  releases/<sha>; host curl /current/prototype/builds/v8-playable.html =
  200; md5 matches local. Report curl + md5 in the final reply.
- NO harness, NO headless browser, NO game run. Syntax checks only:
  node --check prototype/js/CONFIG.js (and any other edited js; node at
  the playwright driver path).

## 6. ACCEPTANCE CRITERIA (Nicko playtests; A1-A5)

- A1 GATE CLOSED: fresh profile, run north past B's ghouls to the arch —
  (0,-86) is legal B ground today, you reach it without any new clamp.
  Trying to move north through the line inside the window stops you AT
  z=-86 (no cross, no yank; you can step back south freely), and
  interacting near the arch gives the reason toast. The B north strip
  OUTSIDE the window (|x| > 4) remains fully walkable (nothing new there).
- A2 GATE OPENS: first Save-and-Heal → walk into the line inside the
  window → cross fires (teleport to z=-88 C-side) → C name banner
  'Forest of the Old King', C fog/ambient/lighting apply, you stand on
  C's stub ground. Walk back into the line from C → cross south to
  z=-84, region darkwood_edge (the return works, radial suspension). Death in C respawns you correctly (camp respawn
  cross-region machinery, game.js:907-915, must work).
- A3 SAVE/LOAD IN C: save in C, reload, CONTINUE puts you in C (generic
  region restore hooks.switchRegion save.js:263-264). Save BEFORE first
  sleep, reload, gate still locked (restoreClock dormant restore
  save.js:141-158).
- A4 A/B UNCHANGED: A->B->A crossing via the chokepoint works as before;
  B enemies still hold at their boundary; no visual/behavioral change on
  the south edge.
- A5 TRAVERSAL FEEL: tree scatter reads as a sparse forest to fog depth;
  no z-fighting between discs; fps reads fine with ~140 props + ~140
  trees (Nicko eyeballs; CC-C3 does the ledger).

## 7. IF THE SPEC MEETS REALITY AND DISAGREES

Any conflict between this contract and the real code (a line anchor that
moved, machinery that differs from the description): obey the code's
actual shape, land the INTENT, log the deviation in the final report.
Do NOT expand scope to fix unrelated things.