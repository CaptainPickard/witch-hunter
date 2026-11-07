# CC-H1a — Door-Plane & Sides Correction (SPEC, one round)

Author: IO (CaptainPickard). Date: 2026-11-07. Art anchor: NONE consumed this
round (pure mechanics correction; no new area/enemy/scene/mechanic — the art
law does not bind a data fix; recorded disclosure).

## 0. The finding (two landed bugs, one round)

FINDING-1 (P0, blocks play): conn[4] E->F and conn[5] C->G fire an instant
bounce-back. Probed on the REAL RegionManagerLogic
(scratch/cc-h1a/sides_law_probe.js): first tick at F spawn/land (0,-650) or
G spawn/land (0,-711) = action 'cross' back to the parent. The player can
never stand in the Galleries or Lord's Hold. Cause per the engine law
`sideIn(R) == sideOfPlane(R's interior reading at the rows the conn serves)`:
the two landed sides tables carry the POCKET's sign flipped for the plane
seats they landed. D/E (the working doors) match the law.

FINDING-2 (the geometry the tables actually encoded): F's door plane
CFG.regionF.door.planeZ = -640 is F's DISC CENTER, not a mouth. F's disc
straddles its own plane (disc z -666..-614). The sides tables (E -1, F +1)
are the CORRECT signs for a SOUTH-RIM mouth at z -662 (D-mouth grammar:
plane 4 m inside the rim; disc fully north of it, pocket side +1). The plane
seat, not the table, is the landed error for F. G's plane -700 is a correct
south-face gate seat (G span -948..-696: fully south of -700), so G's table
sign IS flipped: G = -1 / C = +1 is the law-correct table for plane -700.

## 1. The fix (exact, minimal, 3 lines + comments)

EDIT-1 CONFIG.js regionF.door.planeZ:
  FIND:  planeZ: -640,                       // the galleries mouth plane
  SET:   planeZ: -662,                       // the galleries mouth plane (CC-H1a:
                                             // south-rim grammar, 4 m inside the
                                             // r26 south rim -666)
  (only the planeZ value + its trailing comment; doorX/halfWidth/land/sides
  untouched.)

EDIT-2 region-defs.js conn[5] sides:
  FIND:
    connections[5].sides[CFG.regionC.id] = -1;
    connections[5].sides[CFG.regionG.id] = 1;
  SET:
    connections[5].sides[CFG.regionC.id] = 1;
    connections[5].sides[CFG.regionG.id] = -1;
  (+ rewrite the two comment lines above them: C interior reads z > -700 ->
  +1; G interior z -711 < -700 -> -1. The "(unlike conn[4] no flip needed...)"
  clause is stale and goes.)

EDIT-3 (NO-OP by law): conn[4].sides stay E -1 / F +1 — with plane -662 the
signs are already law-correct (verified below).

NOT TOUCHED: enemy rows (F's ghouls against the corrected hold line for
plane -662 with sideIn(F)=+1: lim = -662 + 1*1.5 = -660.5... hs=+1 -> lim =
planeCoord + hs*margin = -660.5; clamp fires for z < -660.5. F's ghouls at
-636/-635.5 are NORTH of -660.5: NO clamp. NO relocation needed. F's spawn
(0,-650) and land (0,-650) are also north of -660.5: no clamp on the player
(the player plane clamp only engages for conn[0] members) — verified).

## 2. Verified behavior post-fix (IO probe output, real engine code)

- F spawn (0,-650): prewarm (no cross) PASS
- F deep (0,-640): prewarm PASS
- F walk-back exit (0,-662.5): cross -> veil_crypt, mapped (0,-604) PASS
- F walk-back inside (0,-661.5): prewarm PASS
- forceCross E->F at the west-aisle hook: cross -> veil_galleries land
  (0,-650) PASS
- sideIn(F)=+1 == sideOfPlane(land -650)=+1 PASS
- G probes (sides flipped per EDIT-2): spawn (0,-711) no cross; walk-back
  (0,-699.5) x-window -> cross to forest. land (0,-711) == sideOfPlane
  (-711 < -700) = -1 == sideIn(G)=-1 PASS.
- D/E unchanged and passing (regression).

## 3. Acceptance criteria (Testerbot)

- A-1 diff limited to: CONFIG.js (1 line + comment), region-defs.js (2 lines
  + comment), prototype/builds/v8-playable.html, scratch/cc-h1a/,
  io/specs/cc-h1a* — nothing else. game.js diff EMPTY (A-2, hard).
- A-3 scratch/cc-h1a/sides_law_probe.js updated by IO post-fix exits 0
  (ALL CONSTRAINTS: PASS). The probe file IS the executable valspec body;
  Testerbot re-derives 3 checks independently: (i) F plane == -662 in
  CONFIG; (ii) conn[5] sides == C +1 / G -1 parsed from region-defs.js;
  (iii) own-probe: F spawn/land no cross, F walk-back (0,-663) crosses to
  veil_crypt, G spawn/land no cross, G walk-back (0,-699) x 0 crosses to
  forest_of_the_old_king.
- A-4 F enemy seats unchanged at (-6,-636)/(6.5,-635.5) (the no-relocation
  claim) and no clamp simulation: sideIn(F)=+1 lim -660.5 > both seats'
  z: PASS by inspection+probe.
- A-5 build v8 via tools/build_v8.py exit 0, bundle sha CHANGES, rebuild
  identical (determinism), marker veil_galleries >= 8.
- A-6 NO logic files touched: region-manager.js, enemy.js, game.js, save.js,
  daynight.js byte-identical to HEAD.
- A-7 G land row (0,-711) with sideIn(G) = -1 sits on G's home side:
  -711 <= -700 PASS (probe).

## 4. IO close-out per RUNBOOK

commit 1 (code+artifacts) -> build -> commit 2 (stamp) -> release flip ->
served-bytes verify (sha + both fixed values grep) -> doc 64 note row ->
GOALS change log -> journal. NO-GIT for children; IO sole push.

## 5. Record for doc 66 / recipe amendment (IO writes post-landing)

Recipe amendment candidate (doc 66 sec 2 door law): "planeZ = the pocket's
SOUTH MOUTH: 4 m inside the disc's south rim (D grammar), plane side signs
follow sideIn(R) == sideOfPlane(R interior): a pocket whose disc lies
z <= plane reads -1, z >= plane reads +1." The H2 spec copies this law;
doc 64 H2 row note gains the same line.
