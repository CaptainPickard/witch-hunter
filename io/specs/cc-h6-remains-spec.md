# CC-H6 — The Remains (delve strata V5 / region L) — IO SPEC

Issued by IO, 2026-11-07 wake 25. Worktree: /tmp/wh-worldfeat, branch
feat/world-visuals, baseline HEAD e20f61d. Doc 66 recipe round (instanced
pocket via door). All tunables PROPOSED (Nicko tunes).

## 0. Gate + identities + laws

- Gate order: IO spec (this file) -> Testerbot validation spec (BEFORE
  Devbot starts) -> Devbot build -> Testerbot independent verdict -> IO
  commit + push. Children NEVER push (NO-GIT in every dispatch). IO is the
  sole git gatekeeper; identity CaptainPickard <pickard.nicko@gmail.com>.
- Build law: bundle via the newest tools/build_vX.py in the worktree AFTER
  the final code state; commit happens only after PASS verdict (IO).
- Acceptance bar stays Nicko's playtest. Testerbot verdict is code QA only.
- No harness runs, no headless browser smoke tests.

## 1. Art anchor (law 1)

Primary: concept-08-veil-spire.png (the spire-as-drain grammar viewed this
wake): obsidian + ash base, blood-sulphur crimson as the ONLY warm, void
purple cold shadow, ONE blinding accent for the working's focal point.
Chamber grammar: "Decadent Brutalism," melt-dripped stone, hooded sentinel
statues flanking the processional, the working's remains as the focal
object. Faction anchor for the boss: char-04-bannerman-dark.png (viewed
this wake): Rules of Red (crimson only on sigils/glow), Decay (nothing
clean), Verticality (banner/tall axis), Material Contrast (hard plate vs
tattered cloth). No new accent colors anywhere else. Palette continuation
per stratum: K groundColor 0x0b0d12 -> L 0x090b10 (one step colder).

## 2. CONFIG.js — regionL row (shape on regionK's key set)

New row `regionL` in prototype/js/CONFIG.js after regionK's block. Key-set
law: L carries NO traps block and NO rotLair (deviations cites: doc 47 S5
"the chamber is a duel, not a gauntlet" + "the chamber is clean" - traps
belong to the machine Vaults V4, a debris pool contradicts the clean
chamber). Every other K key carried with new values:

```js
regionL: {
  id: 'the_remains',
  name: 'The Remains',
  center: { x: 0, z: -1064 },   // 184 m deeper than K (0,-880): one stratum
                                // gap; K south rim -914 vs L north rim -1034
                                // = 120 m unrendered dark (conn[9] pattern)
  groundRadius: 30,             // PROPOSED (duel chamber: smaller than K 34)
  groundY: 0,                   // flat disc
  groundColor: 0x090b10,        // one step colder than K 0x0b0d12
  groundColor2: 0x0c0e11,
  groundSeed: 559043117,        // FRESH: differs from every landed seed
  scatter: false,               // hand rows only (D/E/F/I/J/K law)
  spawn: { x: 0, z: -1044 },    // 8 m SOUTH of the walk-back plane -1036
                                // (conn[9] ADJ-E mirror: crossing cannot
                                // re-trigger); landing row = spawn row
  gravityY: -22,                // every landed region's value
  fogColor: 0x090710,           // the veil fog family, one step deeper
  fogDensity: 0.17,             // d95 = 1.7306/0.17 = 10.18 m: one stratum
                                // quieter than K (0.16 -> 10.82)
  ambientLightLevel: 0.04,      // K is 0.045; L one step deeper
  door: { ... see below ... },
  enemies: [],                  // doc 47 S5: the chamber holds no trash pool
  lairs: [ { type: 'lastchancel', x: 0, z: -1060 } ],
  //   ^ the CC-H5 note applies verbatim: the row CARRIES x/z and the NEST
  //   derives from CONFIG.enemy.lastchancel.lair via lairNest - two agree.
  //   K-MIRROR SPACING: the seat sits 16.0 m south of the landing row
  //   (0,-1044), matching K's landed edge (landing 16 == aggro 16: no
  //   instant aggro on arrival).
  props: [ ... see sec 2b ... ]
}
```

door (ONE-SIDED walk-back plane; conn[7]/[8]/[9] grammar):

```js
door: {
  planeZ: -1036,                // 2 m inside the north rim -1034 (mirror law:
                                // every landed plane sits INSIDE its disc)
  doorX: 0,
  doorHalfWidth: 2.2,           // the F/J/K tomb-mouth lane
  suspendDepthM: 0, wallGapPadM: 0,
  walkFrom: 'the_remains',      // ONE-SIDED: plane crosses ONLY from L
  interact: { from: 'tithe_vaults', x: 7.5, z: -854, radius: 3.5 },
  //   ^ the K-side hook, east of K's mouth lane, INSIDE K's interior;
  //   probe: >= 4.0 m from every K collider (candidates: dais colonnade,
  //   statues, vents, zealots, the vault ring; ALSO >= 2.0 m outside the
  //   captain's lairRadius 16 circle about (0,-872): dist 19.5 m).
  land: {
    tithe_vaults:  { x: 2, z: -858, faceX: 0, faceZ: -880 },
    //   walk back INTO K beside the hook, facing the vault dais; >= 8 m
    //   south of K's plane -848, on K's home side (z <= -848). 6.8 m from
    //   the hook (J's landed mirror figure: no instant re-prompt, the
    //   E-zone is 3.5 m).
    the_remains:   { x: 0, z: -1044, faceX: 0, faceZ: -1060 }
    //   INTO L = the spawn row, facing the chancel / boss nest (16 m off:
    //   the K edge - no instant aggro on the landing fade).
  },
  fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
  text: { prompt: 'E - Descend into the remains' }
}
```

## 2b. regionL.props (ring first, identity, dressing)

RING (K's 10-row closure on r30; chord = 2*30*sin(18 deg) = 18.541;
scale = chord/1.899 = 9.763; law: rows re-derived to the strict 2dp circle
- the valspec pins rho == 30.0 +- 0.05 and chord uniformity <= 0.02, the
literal table is context per the CC-H5 SPEC-FIG FIX):

- Formula: row k of 10: x_k = 30*sin((180-36k) deg), z_k = -1064 -
  30*cos((180-36k) deg), rotY_k = 3.14 + 0.6283*k, wallA/B alternating
  starting A, sy 11.69 (A) / 11.55 (B), sz 2.40, y -0.2, wall 10. NO
  omission (K law: the ring is closed behind the plane). Resulting rows:

```js
{ asset: 'whWallA', x:   0.00, z: -1034.00, rotY: 3.14, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallB', x:  17.63, z: -1039.73, rotY: 3.77, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallA', x:  28.53, z: -1054.73, rotY: 4.40, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallB', x:  28.53, z: -1073.27, rotY: 5.03, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallA', x:  17.63, z: -1088.27, rotY: 5.65, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallB', x:   0.00, z: -1094.00, rotY: 6.28, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallA', x: -17.63, z: -1088.27, rotY: 6.91, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallB', x: -28.53, z: -1073.27, rotY: 7.54, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallA', x: -28.53, z: -1054.73, rotY: 8.17, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
{ asset: 'whWallB', x: -17.63, z: -1039.73, rotY: 8.80, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 }
```

- Lane: the walk-OUT plane -1036 clears the north-point row (0,-1034)
  colliders by 2.00 - 0.45 = 1.55 m edge distance - the K landed figure
  carried by the mirror geometry (the governing >= 1.0 m lane clearance).
- NO mouth gap: the plane crosses INSIDE the closed ring (K precedent).

IDENTITY + DRESSING (assets from the EXISTING manifest only):

```js
// THE REMAINS: the working's shell at the chamber's south center
{ asset: 'stoneSarcophagus', x: 0, z: -1078, rotY: 0.00, scale: 1.60 },
// melted colonnade flank pair (K dais grammar carried down one stratum)
{ asset: 'okRuinColumn', x: -7, z: -1064, rotY: 0.30, scale: 1.40 },
{ asset: 'okRuinColumn', x:  7, z: -1064, rotY: 5.98, scale: 1.40 },
// hooded sentinels flanking the chancel approach (H3/H5 processional)
{ asset: 'mourningStatue', x: -4, z: -1052, rotY: 4.00, scale: 0.60 },
{ asset: 'mourningStatue', x:  4, z: -1052, rotY: 5.28, scale: 0.60 },
// approach steps
{ asset: 'stoneSteps', x: -2.4, z: -1068, rotY: 0.60, scale: 1.10 },
{ asset: 'stoneSteps', x:  2.4, z: -1068, rotY: 5.68, scale: 1.10 },
// erasure scatter (J/K grammar)
{ asset: 'skullPile', x: -14, z: -1076, rotY: 4.40, scale: 1.00 },
{ asset: 'skullPile', x:  12, z: -1084, rotY: 3.60, scale: 1.00 },
{ asset: 'mossBoulder', x: -13, z: -1052, rotY: 2.00, scale: 2.20 },
// the ONE crimson family (lamp + caps; K's family continued)
{ asset: 'lanternPost', x: -13, z: -1058, rotY: 5.20, scale: 1 },
{ asset: 'blightcap', x: -13, z: -1046, rotY: 3.62, scale: 0.90 },
{ asset: 'blightcap', x:  13, z: -1046, rotY: 0.63, scale: 0.90 }
```

Floor-law check (the re-derive duty, K SPEC-FIG FIX precedent): nearest
sarcophagus edge to the seat = 18.0 - mapRadius 2.1 = 15.9 >= 6.0 (the
nearest prop edge: colonnades (±7,-1064) = 9.30 m edge >= 2.0 mutual);
mourning (±4,-1052) = 10.77 m edge, nearest neighbor steps (-2.4,-1068)
edge = 4.28 >= 2.0; skulls/boulder caps >= 2.0; seat face view target
(0,-1060), steps at -1068, shell at -1078: ONE dais walk path.

## 3. Parent-region edit: NONE

Entry to L is the E-hook inside K (config lives in L's door.interact.from
= 'tithe_vaults'); K's closed vault ring stays byte-identical. Spec
asserts: diff of CONFIG.js shows regionK row UNTOUCHED; the only parent
interaction is the probe's hook-clearance check (sec 2 door.interact).

## 4. region-defs.js — registration + conn[10] (canonical block)

After K's block (regions[CFG.regionK.id] at line ~311, conn[9] sides at
~334-335), append EXACTLY (nothing else in region-defs.js):

```js
  // CC-H6 the_remains: plane-0 convention only; K-side portal is an
  // interact hook, L-side mouth is a walk-back plane (conn[9] precedent).
  regions[CFG.regionL.id] = makeRegion(CFG.regionL, -1);
  var LD = CFG.regionL.door;
  connections.push({
    from: CFG.regionK.id,
    to: CFG.regionL.id,
    axis: 'z',
    planeCoord: LD.planeZ,
    sides: {},
    door: {
      doorX: LD.doorX, doorHalfWidth: LD.doorHalfWidth,
      suspendDepthM: LD.suspendDepthM, wallGapPadM: LD.wallGapPadM,
      arch: null, gatedTo: null,
      walkFrom: CFG.regionL.id,
      interact: { from: CFG.regionK.id, x: LD.interact.x, z: LD.interact.z, radius: LD.interact.radius },
      land: LD.land,
      fadeIn: LD.fadeIn, fadeOut: LD.fadeOut, exitFadeOut: LD.exitFadeOut,
      text: LD.text                       // AMENDMENT A: the portal prompt + fades ride the conn
    }
  });
  // E-mirror: K's plane is underground/inactive for this conn; L's interior
  // is SOUTH of its walk-back plane (-1044 < -1036). K-side value follows
  // the geometry (K's interior sits NORTH of -1036), L follows sideOfPlane.
  connections[10].sides[CFG.regionK.id] = +1;
  connections[10].sides[CFG.regionL.id] = -1;
```

## 5. CONFIG.enemy.lastchancel + tables (boss-slam chassis, soldier-tuned)

THE LAST CHANCEL (doc 47 V5 warden concept 3: Veil Faithful zealot-captain
boss at the remains' threshold; doc 04/34 faction-soldier grammar at boss
scale, parry-capable, disciplined reads). ENGINE LAW (enemy.js:152): lair
machinery attaches only to pattern 'boss-slam' rows - the captain's
precedent carries verbatim: boss-slam chassis TUNED SOLDIER-DISCIPLINED
(the narrow fast-tracked shock-slam = the disciplined shield-wall read),
guard ai1 rides ALONGSIDE. All PROPOSED:

```js
lastchancel: {
  name: 'The Last Chancel', hp: 400, dmg: 24, speed: 4.2, aggro: 18,
  pattern: 'boss-slam',
  slamRadius: 4.6, slamArcDeg: 100, slamWindup: 0.8, slamActive: 0.18,
  slamRecover: 0.85, slamCooldown: 3.4, slamTrackDegPerSec: 120,
  engageRange: 4.6,
  cueDark: 0x1a0508, cueHot: 0xd84a4a,        // the chain's ONE crimson family
  scale: 2.3,                                 // soldier boss one step over K's 2.1
  lair: { x: 0, y: 4, region: 'L', flagPrefix: 'lastchancel' },
  //   world seat (0,-1060); save key lastchancel_cleared_L (letter derivation
  //   via lairFlag machinery is region-letter-generic: K precedent). y 4
  //   derives the nest from regionL center (0,-1064): nest = center + y
  //   (K law: y 8 on center -880 gave seat -872) = (0,-1060) - the lairs row,
  //   this derivation, and the K-mirror 16.0 m landing spacing all agree.
  lairRadius: 16,
  rearm: { days: 3, trigger: 'proximity', radius: 14 },
  loot: [{ mat: 'stolenCoin', n: [2, 5] }],   // the LAST tithe
  // SOLO-DUEL LAW + CENSUS FINDING: lairTick reads M.interval from
  // cfg.minions UNGUARDED (enemy.js ~1275-1282) - a boss row with NO
  // minions block crashes every lairTick. Engine edit REJECTED (all-config
  // law): the row carries the cap-0 no-spawn minions row instead:
  minions: { asset: 'zealot', cap: 0, interval: 999.0, range: 5.0 },
  //   cap 0: alive(0) < cap(0) is false EVERY tick - the spawner never
  //   fires (doc 47 S5: the chamber is the duel, not a gauntlet).
  radius: 1.0,
  corpseLingerSec: 10, maxCorpses: 8,
  riseSec: 1.4,
  barLiftM: 2.4,
  ai1: { decisionSeconds: 0.35, alwaysKnowsRadius: 5.0,
    strafeBandInner: 4.0, strafeBandOuter: 8.2, strafeSpeedMult: 0.75,
    strafeDirFlipSeconds: 1.8, attackRadius: 4.6, attackBias: 0.55,
    guardChance: 0.65, guardRespondRadius: 6.0, guardSecondsMax: 1.9,
    guardArcDeg: 42, guardDamageMult: 0.5 }   // smaller window: captain 45
},
```

Body tables (CONFIG rows, symmetry law): bodyByType.lastchancel =
'banditBody'; animVariantByType.lastchancel = 'bandit'.

## 6. Clearance laws (the probe enforces EVERY one)

solve_geometry.py pattern: scratch/cc-h6/solve_geometry.py, CONFIG-ROW-
PARSED (parse regionL's live rows from CONFIG.js, region-defs.js - no
hard-coded spec constants for the NEW rows). Asserts:

1. Ring: rho == 30.0 +- 0.05 on all 10 landed rows; chord uniformity
   <= 0.02; zero colliders inside the plane window x in [-2.2, 2.2] at
   z = -1036 within 1.0 m; north-point row edge clearance >= 1.0 m from
   the plane (spec figure 1.55).
2. Prop floors: every prop >= 4.0 m raw from every ring collider; mutual
   prop edges >= 2.0 m; BOSS-SEAT clear circle 6.0 m at (0,-1060) (AMEND-1
   law: nearest prop footprint edge >= 6.0).
3. Spawn/land: L landing/spawn row (0,-1044) >= 8.0 m south of plane
   -1036 and on L's home side; K land row (2,-858) >= 8.0 m south of
   K's plane -848, inside K's disc, on K's home side.
4. Hook: (7.5,-854) >= 4.0 m from every K collider; >= 2.0 m outside the
   captain lair circle (lairRadius 16 about (0,-872)).
5. Disc: L landing row inside the r30 disc; every prop inside the disc
   (raw position + map radius vs r30, jitter margin per K probe).
6. Chain: geometry walk K center (0,-880) -> plane -1036/2 m-inside rim
   -1034 -> L center (0,-1064) all x=0 (Z-HARD-CODED engine law).

save_roundtrip.js pattern: THREE-free node eval CONFIG -> region-defs ->
save.js (stubbed game surface, scratch/cc-ad1 precedent). Asserts:
capture rides regionId 'the_remains' through save; restore gates +
teleports back; negative control (unknown id falls back); AND a lair-state
shape check: a { lastchancel_cleared_L: dayOfDeath } block round-trips
through the save block parser (enemy.js ~1691-1702 regex accepts the
prefix).

## 7. Engine census (record-only findings; NO code changes)

- One-active-region + neighbor prewarm: unchanged machinery; L inherits.
- wh-ground: L reads the flat groundY 0 disc (A/B/D/E/F/I/J/K law).
- save.js: additive regionId blocks ride validRegion() with NO edit.
- daynight.js: NO constantPhases.the_remains (E/F/K precedent: region
  fog/ambient suffices).
- scatter gate: regionL carries scatter: false -> excluded.
- prompt chain: 'E - Descend into the remains' rides conn.door.text.
- LAIR FINDING (sec 5): unguarded cfg.minions in lairTick - recorded, not
  touched; the cap-0 row is the all-config remedy.

## 8. Deliverables (Devbot)

1. prototype/js/CONFIG.js: regionL row (sec 2/2b), lastchancel enemy row +
   bodyByType/animVariantByType carries (sec 5). NOTHING ELSE.
2. prototype/js/region-defs.js: sec 4 block only.
3. scratch/cc-h6/solve_geometry.py + save_roundtrip.js + build-note.md
   (files touched, deviations + adjudication, probe output digest, build
   sha). Probe output verbatim in the build note.
4. Bundle build via the newest tools/build_vX.py AFTER final code state;
   build note carries the served-title stamp line.
5. NO-GIT: no commit, no push, no staging by the child. IO commits after
   the verdict.
6. Doc 64 slot-row flip RESERVED -> LIVE + doc 66 citation row + GOALS.md
   tick: PROPOSE in build-note.md as the registry-flip patch; IO applies
   the doc edits at commit time (the same-commit slot law).

Acceptance: every sec-6 probe assertion PASS on the landed rows; probes
CONFIG-ROW-PARSED (parse, don't hard-code); build succeeds; worktree git
status shows exactly the four intended paths (CONFIG.js, region-defs.js,
scratch/cc-h6/*, prototype/builds/v8-playable.html artifact).
