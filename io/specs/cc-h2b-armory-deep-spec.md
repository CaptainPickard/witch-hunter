# CC-H2b SPEC — The Armory Deep, pocket interior chained off the Garrison Keep

Autopilot round 2026-11-07 (wake 18). Source: doc 64 slot H2b note ("armory/
dungeon-mouth dressing = H2b content scope") + doc 66 recipe secs 2-8. This
is a CHAMBER ROUND, not a new region claim: regionH stays the parent; the
pocket is a D/E/F-style own-disc region REGISTRY-LEDGED as H2b inside slot
H2's round arc (doc 64 ledger flip: a 'H2b' LIVE line in the slot H2 notes
column, NOT a new numbered slot — numbered slots H3..H6 keep their reserved
rows).

## 0. Design summary (the Nicko-facing one-liner)

South of the garrison courtyard, past the courtyard's own south curtain
(the r18 inner ring), an armory hall: weapon racks, supply tents, and a
bier dais under one crimson lantern — the dungeon mouth where deeper
delve chains will hang later (V3 hangs here on a future round).

## 1. Art anchors (Nicko law: anchor BEFORE build; generation BLOCKED)

- char-04-bannerman-dark.png (viewed 11-07 wake 18): blackened garrison
  steel + crimson banner accent on obsidian/charcoal, cold moonlight
  palette with ONE blood-red lamp family. Palette for I: charcoal/basalt
  #0A0E14-ish fields, slate #3A424D-ish stone, ONE crimson accent family
  (the blightcap cap + lantern pair below — the same "sparing crimson"
  law H2's spec set for the garrison).
- concept-08-veil-spire.png (viewed 11-07 wake 18): gothic spire over
  cracked ground, achromatic grey with a single crimson accent (the
  fissure glow) — the mood the chamber's ONE red lamp must carry.

## 2. regionI CONFIG row (shape on regionE veil_crypt, the closest sibling)

Append AFTER the regionH block's closing brace, one blank line, then
regionI: { ... } with this exact data (the `#` line below = notation only;
use // comments in the real file):

  id: 'armory_deep',
  name: "The Armory Deep",
  center: { x: 0, z: -1120 },       // 8 m further south than regionH's center (0,-1024); chained pocket
  groundRadius: 18,                 // E is 20; D is 34; the pocket reads one stratum tighter. PROPOSED
  groundY: 0,                       // flat disc (H hidden while I is active: one-active-region law)
  groundColor: 0x101218,            // basalt, one step colder than H2's stone
  groundColor2: 0x14161c,           // shadow secondary
  groundSeed: 1662061654,           // FRESH: must not equal C 1662061217 / D ...218 / E ...219 / F ...1329 / G ...1440 / H ...1651
  scatter: false,                   // hand rows only (D/E/F pattern)
  spawn: { x: 0, z: -1128 },        // the landing row's I end (E-mirror: local (0,-8))
  gravityY: -22,                    // E/D's value
  fogColor: 0x0a0810,               // E's veil fog
  fogDensity: 0.13,                 // E's value (d95 = 13.3 m: the chamber is one black thought)
  ambientLightLevel: 0.07,          // E's value
  door: {
    planeZ: -1136,                  // I-local -16 (E-mirror: 2 m inside the r18 south rim -1138)
    doorX: 0,
    doorHalfWidth: 3.0,             // the E/F grammar (2.4/2.2) widened ONE step for a two-sided breach lane. PROPOSED
    suspendDepthM: 0,               // E/F/D value: the plane sits INSIDE the disc; no clamp lift needed
    wallGapPadM: 0,
    walkFrom: 'armory_deep',        // ONE-SIDED: the plane crosses ONLY from the I side (C/E grammar: H keeps no walkFrom)
    interact: {
      from: 'fort_garrison',        // the H-side hook (E's C-side notch-mouth pattern)
      x: -7.5, z: -1088.5, radius: 3.5
    },
    land: {
      fort_garrison: { x: 0, z: -1084, faceX: 0, faceZ: -1097 },   // walk back INTO H, facing H2's war-table dais
      armory_deep:   { x: 0, z: -1128, faceX: 0, faceZ: -1120 }    // INTO I = the spawn row, facing the bier hall
    },
    fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
    text: { prompt: 'E - Descend into the armory' }
  },

### 2b. Why one-sided (the engine-law reading this round commits to)

H2's door is TWO-SIDED (B/C grammar: no walkFrom, no interact) because both
sides of that breach are OPEN YARD on the same courtyard level. H2b is a
DUNGEON MOUTH: the grammar E and F landed (walk-back plane + interact hook,
their `connections[3]`/`connections[4]` rows) — the courtyard side gets an
E-key prompt like the notch mouth did; the interior side walks back out.
This is the SAME choice AD1 made for the crypt (an interior pocket off an
open area). The spec carries it as the round's central engine-law decision;
Testerbot adjudicates it against region-manager before Devbot builds.

## 3. regionI enemies — the garrison's dead (2 rows, ghoul grammar)

E/F used coven/ghoul pairs. The armory keeps doc 34's undead grammar: no
dodge, no parry, relentless walkers.

  enemies: [
    { type: 'ghoul', x: -6.3, z: -1117 },
    { type: 'ghoul', x: 6.3, z: -1117 }
  ],

Pre-verified (probe re-run mandatory, F-grammar: the AD1 prop->coven
5.0 law does NOT apply to undead wardens — F landed ghouls with no
prop->enemy constraint): each 12.68 m from the spawn/land rows (>= 8.0),
12.6 mutual (>= 12.5), ring margin 11.02 (>= 4.45). Spec rows x -6.3 /
+6.3, z -1117.

## 4. regionI props — the armory hall (13 rows, ONE tableaux exemption)

The south band stays EMPTY (the 8 m threshold between landing and plane:
land, read the room, walk in). The hall rows: bier dais center-north +
flank rows. BIER GROUP (sarcophagus + 2 steps) = ONE tableaux: mutual
distances inside the group are EXEMPT (E landed its sarc/steps plinth at
2.06 m mutual; the exemption is the E precedent, documented here).

  props: [
    // -- the bier dais (E's albetar plinth pattern, hall center-north)
    { asset: 'stoneSarcophagus', x: 0, z: -1118.5, rotY: 0.00, scale: 1.20 },
    { asset: 'stoneSteps',       x: -2.4, z: -1115.7, rotY: 0.60, scale: 1.10 },
    { asset: 'stoneSteps',       x: 2.4, z: -1115.7, rotY: 5.68, scale: 1.10 },
    // -- supply yard west: campkit + tent + fence + the crimson lantern
    { asset: 'lanternPost',      x: 6.4, z: -1127.2, rotY: 5.2, scale: 1 },
    { asset: 'skullPile',        x: -6.9, z: -1127.2, rotY: 4.4, scale: 1 },
    { asset: 'whCampkit',        x: -9.9, z: -1123.6, rotY: 0.3, scale: 1 },
    { asset: 'whCampkit',        x: 9.9, z: -1123.0, rotY: 5.9, scale: 1 },
    { asset: 'whTent',           x: -12.1, z: -1120.6, rotY: 1.2, scale: 1 },
    { asset: 'whTent',           x: 12.1, z: -1120.0, rotY: 5.2, scale: 1 },
    // -- the crimson pair: 2 blightcap caps (the ONE accent family;
    //    'blightcap' has NO lightSockets key: dark flowers by design)
    { asset: 'blightcap',        x: -12.4, z: -1117.6, rotY: 3.62, scale: 0.90 },
    { asset: 'blightcap',        x: 12.4, z: -1117.3, rotY: 0.63, scale: 0.90 },
    // -- ruined columns flanking the hall's north wall
    { asset: 'okRuinColumn',     x: -9.4, z: -1117.5, rotY: 5.9, scale: 1.4 },
    { asset: 'okRuinColumn',     x: 9.4, z: -1117.0, rotY: 5.9, scale: 1.4 },
    // -- CC-H2b CAVERN RING: full 10-row closure (the D/E/F closed-cavern
    //    law; the plane exits THROUGH the ring's south point -1138 which
    //    backs the door like E's -612/-614 pair). scale = chord/1.899
    //    (chord 11.12 = 2*18*sin(18 deg) => 5.8581); centers k*36 deg;
    //    rotY = bearing + PI. NO omission, NO window probe: the ring is
    //    closed behind the plane like E's crypt mouth; the door lane
    //    (|x|<=3 at z -1136) clears the NEAREST ring collider (the
    //    south-point row (0,-1138)) by ~1.55-1.60 m — the governing
    //    >= 1.0 m lane clearance (BV-002, Testerbot 11-07: my earlier
    //    5.85 'nearest' figure named the wrong rows; geometry unchanged).
    { asset: 'whWallA', x: 0, z: -1102, rotY: 3.14, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallB', x: 10.58, z: -1105.44, rotY: 3.77, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallA', x: 17.12, z: -1114.44, rotY: 4.4, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallB', x: 17.12, z: -1125.56, rotY: 5.03, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallA', x: 10.58, z: -1134.56, rotY: 5.65, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallB', x: 0, z: -1138, rotY: 6.28, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallA', x: -10.58, z: -1134.56, rotY: 6.91, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallB', x: -17.12, z: -1125.56, rotY: 7.54, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallA', x: -17.12, z: -1114.44, rotY: 8.17, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
    { asset: 'whWallB', x: -10.58, z: -1105.44, rotY: 8.8, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 }
  ],

## 5. Clearance law the probes must PASS (tolerances per recipe sec 6)

- spawn + landI inside groundRadius 18 (rows at rho 8.0 / 8.0 with margin).
- landH (0,-1084) inside H's r80 (60.0 with margin), on H's home side
  (z -1084 north of the I plane -1136: the H-side clamps never reach the
  plane — C/E law 'the line runs underground'), 11.0 clear of H2's dais
  trio (13.0 raw - 2.0), 8.85 clear of both H2 torches (recompute 9.85,
  BV-003), 14.7 m from the G
  pole flank pair. The H-side interact hook = (-7.5,-1088.5) radius 3.5:
  5.7 clear of torchL, 9.3 of the dais, 64.9 rho (limit 78.5; BV-003,
  Testerbot 11-07 recompute: torchL raw 5.70, playRadius 78.5).
- enemies >= 8.0 from spawn/land, >= 12.5 mutual, >= 4.45 ring-clear.
- props (NON-group, E-law set: scratch/cc-ad1/solve_geometry.py's
  landed checks): >= 4.0 raw of every ring collider; >= 4.0 ring walk-clear
  (18 - rho); >= 6.0 from spawn/land rows. NO prop-mutual law (E/F landed
  precedent: AD1's enforced set has none; E landed skull-rubble pairs at
  4.03/4.24 raw). The bier group mutual = tableaux-exempt (E 2.06).
- Ring: the 10 row centers' colliders (r 0.45) — door lane |x| <= 3 at
  z -1136 clears EVERY ring collider by >= 1.0 m (the nearest is the
  south-point row (0,-1138) at ~1.55-1.60; BV-002, Testerbot 11-07);
  zero colliders inside the lane window within 0.5 m radius. NO other
  machinery (no parent erasures anywhere - regionH loses NOTHING this
  round).
- conn sanity: from: 'fort_garrison', to: 'armory_deep',
  axis z, planeCoord -1136, walkFrom armory_deep, interact H-side,
  land rows both.

## 6. region-defs.js registration (connections[7])

 regions[CFG.regionI.id] = makeRegion(CFG.regionI, -1);   // plane-0 convention only (comment)
 var ID = CFG.regionI.door;
 connections.push({
   from: CFG.regionH.id,
   to: CFG.regionI.id,
   axis: 'z',
   planeCoord: ID.planeZ,
   sides: {},
   door: {
     doorX: ID.doorX, doorHalfWidth: ID.doorHalfWidth,
     suspendDepthM: ID.suspendDepthM, wallGapPadM: ID.wallGapPadM,
     arch: null, gatedTo: null,
     walkFrom: CFG.regionI.id,
     interact: { from: CFG.regionH.id, x: ID.interactAt.x, z: ID.interactAt.z, radius: ID.interactM },
     land: ID.land,
     fadeIn: ID.fadeIn, fadeOut: ID.fadeOut, exitFadeOut: ID.exitFadeOut,
     text: ID.text                       // AMENDMENT A: the portal prompt + fades ride the conn
   }
 });
 // SIDES TABLE (E-mirror): regionH z <= -1136?? NO: H interior (-1024) is
 // NORTH of the plane: -1024 > -1136 = +1 = sideIn(fort_garrison);
 // regionI interior (-1120) = -1120 > -1136 = +1 TOO?? BOTH +1 is impossible
 // for a valid two-region side pair on one plane. THE GEOMETRY: the plane
 // -1136 lies INSIDE BOTH discs by design (H's r80 south rim = -1104; the
 // plane -1136 is 32 m BEYOND H's playable rim). H's interior contains the
 // plane?? The H2 landing's conn[6] plane -948 sits BETWEEN G -822 and H
 // -1024 (outside both discs: G rim -946.5/H rim -944.5). For I: H rim
 // -1104, I spans -1102..-1138: the plane -1136 lies outside H's disc
 // entirely (beyond its south rim) and inside I's. This is EXACTLY the E-C
 // geometry (E's plane -612 = beyond C's playable band, inside E's disc:
 // 'in C the line runs underground: no crossing, no clamp'). The side
 // reading (E's C0-3 law): sideOfBoundary(H, conn7) = -1 (H lies z <= plane
 // side... E: 'E occupies z <= planeZ (D-symmetry). E side +1, C side -1'
 // with E's interior NORTH of the plane (E center -596 > -612): E's row sets
 // sides[C] = -1, sides[E] = +1 where +1 = z > plane. Mirror EXACTLY:
 //   connections[7].sides[CFG.regionH.id] = -1;   // H interior reads the C-side (-1) here: the line runs underground for H
 //   connections[7].sides[CFG.regionI.id] = +1;   // I interior z > plane (E-mirror)
 // The interact/land sides stay E-shaped; sideIn(R) == sideOfPlane(R
 // interior) asserted by the valspec probe both ways (H1a lesson: the
 // sides table is where landings have died).

## 7. save.js, validRegion, daynight

- save.js validRegion: rides free (regionId generic). NO new machinery.
- daynight constantPhases: NO row (E/F precedent: region fog + ambient
  only). A-9 surface discipline.
- Scatter: regionI scatter:false (hand rows only).

## 8. Acceptance criteria (A-1..A-9, recipe skeleton)

- A-1 CONFIG.regionI exists with the exact key set of sec 2 (shape on E);
  groundSeed 1662061654 (fresh, no collision).
- A-2 regionH UNCHANGED byte-identical (NO parent aperture this round:
  the hook is an interact row, the aperture machinery does not exist
  here). regionI appended after regionH, before whatever follows.
- A-3 region-defs: registration + conn[7] (WITH the AMENDMENT A text/fade
  carries — the portal-prompt law) + sides table per sec 6. conn[2]..conn[6]
  MUST NOT gain keys this round (the landed latent crash-class is a
  separate disclosed micro-round, NOT this blast radius).
- A-4 game.js diff EMPTY; no unrelated diffs anywhere else; daynight.js
  byte-identical.
- A-5 solve_geometry.py re-run against landed rows: ALL CONSTRAINTS: PASS
  (I-side + the H-side hook/land clearances of sec 5).
- A-6 build: python3 tools/build_v8.py exit 0; marker count of
  'armory_deep' >= 8 in the bundle; rebuild sha256-identical.
- A-7 save roundtrip THREE-free node probe: capture/restore with
  regionId 'armory_deep' rides through + unknown-id fallback still
  returns the old activeId (scratch/cc-h2b/save_roundtrip.js, pattern
  scratch/cc-ad1/).
- A-8 chain-walk semantics: connectionBetween('fort_garrison',
  'armory_deep') finds conn[7]; walkFrom-armory_deep + H-side interact
  + land rows home-side (probe asserts the E-grammar fields exist and
  the H2 two-sided conn[6] is untouched byte-identical).
- A-9 surface discipline: files touched = prototype/js/CONFIG.js,
  prototype/js/region-defs.js, prototype/builds/v8-playable.html,
  scratch/cc-h2b/*, io/specs+reports. NOTHING else.
- Gate: IO commit 1 (code + spec/valspec/verdict + doc 64 H2b ledger
  line + GOALS tick) then build_v8 -> commit 2 (stamp) -> flip ->
  serve-verify -> journal. NO-GIT children; IO sole pusher.

## 9. Open items parked (NOT this round)

- Dungeon-mouth interactivity (a interact prompt on the I-side 'the deep'
  future stratum) = future content round.
- Bestiary row for the garrison's dead (ghouls ride existing grammar; no
  new enemy type).
