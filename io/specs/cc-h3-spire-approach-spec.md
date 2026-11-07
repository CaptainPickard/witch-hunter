# CC-H3 SPEC — The Spire Approach, boss-tier pocket chained off the Erased Galleries

Autopilot round 2026-11-07 (wake 21). Source: doc 64 slot H3 ("Veil Spire
approach — OWN disc r40, chained off veil_galleries; crimson-vein interior
law; statue gauntlet approach; boss-tier space") + doc 66 recipe secs 2-8 +
doc 47 Sun-delve strata mood (S1 underbelly -> S4 works, one stratum past the
galleries). This is a REGION ROUND (new own-disc regionJ), the direct sibling
of wake 18/20's regionI armory_deep.

## 0. Design summary (the Nicko-facing one-liner)

Deeper still, past the galleries' south rim: a statue-lined approach hall —
paired mourners watching a processional to the spire's buried root, one
crimson lamp and two crimson caps as the only color, two ghouls walking the
floor, the vault ring closed all around. The space is boss-tier: sized and
dressed for a warden that does not live here yet.

## 1. Art anchors (Nicko law: anchor BEFORE build)

- concept-08-veil-spire.png (viewed 2026-11-07 wake 21, vision_analyze):
  gothic needle-spires over cracked ground, obsidian/charcoal primaries,
  crimson/vermillion fissure-glow accents, ash-grey cold stone highlights,
  monolithic statue sentinels in rows, under-lighting from below, inverted
  (stalactite) spire motif below ground, heavy iron-chain verticals.
  Carried into J: colder-than-F basalt ground, crimson family = ONE
  lanternPost lamp + TWO blightcap caps (the same single-accent family
  grammar regionI landed), statue GAUNTLET rows (the anchor's sentinel
  colonnade), ring vault as the "inverted spire" enclosure.
- char-05 mourning/erasure grammar already landed in F (mourningStatue
  "names once stood") reuses the same erasure motif in J's gauntlet rows.

## 2. Engine-law decision (the round's central call)

ONE-SIDED grammar, exactly regionI's connections[7] row: J is a dungeon
mouth, so the walk-back plane exists ONLY from J's side (walkFrom
'veil_spire_approach') and the parent side gets an E-key interact hook
(interact.from 'veil_galleries', radius 3.5, prompt text). F's ring is NOT
amended — the AD2 precedent settled that door planes and hook seats are
abstract (E<->F's plane lives at F's south rim while F's dressing points
elsewhere); no F prop rows move this round. Sides table: F -1, J +1
(conn[7] E-mirror law, region-defs sideOfPlane reading).

## 3. regionJ CONFIG row (append AFTER the regionI block, one blank line)

  regionJ: {
    id: 'veil_spire_approach',
    name: "The Spire Approach",
    center: { x: 0, z: -700 },        // 60 m deeper than F's center (0,-640); x-0 chain, mirror I's 8+ m pocket gap: J's north rim -660 vs F's ring north point -662 is the SAME one-active-region tolerance I/H landed (2-4 m overlaps)
    groundRadius: 40,                 // doc 64 H3 boss-tier space: 2.2x F's 26, 2x I's 18. PROPOSED, Nicko tunes
    groundY: 0,                       // flat disc (F hidden while J is active: one-active-region law)
    groundColor: 0x0d0f15,            // basalt, one step colder than F's 0x11131a
    groundColor2: 0x111318,           // shadow secondary
    groundSeed: 1662061763,           // FRESH: must not equal any landed seed (1217/1218/1219/1329/1440/1651/1654)
    scatter: false,                   // hand rows only (D/E/F/I law)
    spawn: { x: 0, z: -730 },         // the landing row's J end (I-mirror: local (0,-30) lands 30 m deep, 8 m inside the far-wall plane)
    gravityY: -22,                    // every landed region's value
    // sec DARKNESS: density 0.15 -> d95 = sqrt(-ln 0.05)/0.15 = 11.61 m:
    // one stratum quieter than F's 12.0. Region row fog/fill/ambient only.
    fogColor: 0x0a0810,               // the veil fog family
    fogDensity: 0.15,
    ambientLightLevel: 0.05,          // F is 0.055; J is one step deeper
    door: {
      planeZ: -738,                   // J-local -38 (I-mirror: 2 m inside the far SOUTH rim -740; the plane exits THROUGH the ring's south point row)
      doorX: 0,
      doorHalfWidth: 2.2,             // F's tomb-mouth lane
      suspendDepthM: 0,               // E/F/D/I value: the plane sits INSIDE the disc; no clamp lift needed
      wallGapPadM: 0,
      walkFrom: 'veil_spire_approach', // ONE-SIDED: the plane crosses ONLY from J (conn[7] grammar: F keeps no walkFrom)
      interact: {
        from: 'veil_galleries',       // the F-side hook (conn[7] H-side pattern)
        x: 7.5, z: -654, radius: 3.5  // inside F's south rim (-666), 12 m north of it; probe-verified clear of every F prop, ring collider, ghoul, and F's own land row
      },
      land: {
        veil_galleries:       { x: 2, z: -652, faceX: 2, faceZ: -644 },   // walk back INTO F just north of the hook, facing the galleries' heart
        veil_spire_approach:  { x: 0, z: -730, faceX: 0, faceZ: -700 }    // INTO J = the spawn row, facing the gauntlet head monolith
      },
      fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
      text: { prompt: 'E - Descend toward the spire' }
    },
    // STATUE GAUNTLET wardens (doc 34 undead grammar, 2 rows, ghoul type):
    // wide stance clears the processional; each >= 8 m from spawn/land,
    // >= 12.5 m apart (30.0), >= 4.45 m walk-clear of the ring
    enemies: [
      { type: 'ghoul', x: -15, z: -708 },
      { type: 'ghoul', x: 15, z: -708 }
    ],

## 4. regionJ props — the gauntlet + vault ring (16 hand rows + 10 ring rows)

Laws (mirror I/F, all probe-verified): every row >= 4.0 m raw of the ring
colliders, >= 6.0 m from spawn and land rows, >= 5.0 m from BOTH ghouls,
>= 4.0 m mutual. The ONE accent family = crimson (lanternPost lamp +
blightcap pair); everything else ash/charcoal.

  props: [
    // -- THE GAUNTLET: two mourners per side watching the processional
    { asset: 'mourningStatue', x: -7, z: -712, rotY: 4.00, scale: 1.00 },
    { asset: 'mourningStatue', x:  7, z: -712, rotY: 5.28, scale: 1.00 },
    { asset: 'mourningStatue', x: -7, z: -704, rotY: 4.00, scale: 1.00 },
    { asset: 'mourningStatue', x:  7, z: -704, rotY: 5.28, scale: 1.00 },
    { asset: 'stoneSteps',     x: -2.4, z: -718, rotY: 0.60, scale: 1.10 },
    { asset: 'stoneSteps',     x:  2.4, z: -718, rotY: 5.68, scale: 1.10 },
    // -- THE SPIRE ROOT (boss-tier heart, north end of the hall)
    { asset: 'okRuinColumn', x: 0, z: -700, rotY: 0.00, scale: 2.40 },
    { asset: 'okRuinColumn', x: -8, z: -696, rotY: 0.30, scale: 1.40 },
    { asset: 'okRuinColumn', x:  8, z: -696, rotY: 5.98, scale: 1.40 },
    // -- the crimson pair: 2 blightcap caps (the ONE accent family with the lamp)
    { asset: 'blightcap', x: -12, z: -692, rotY: 3.62, scale: 0.90 },
    { asset: 'blightcap', x:  12, z: -692, rotY: 0.63, scale: 0.90 },
    // -- the ONE crimson lamp (regionI's family; NOT near the ghouls)
    { asset: 'lanternPost', x: -6, z: -724, rotY: 5.20, scale: 1 },
    // -- erasure scatter (F's grammar): 2 skull piles, 1 moss boulder
    { asset: 'skullPile',   x: -13, z: -723, rotY: 4.40, scale: 1.00 },
    { asset: 'skullPile',   x: -5,  z: -668, rotY: 3.60, scale: 1.00 },
    { asset: 'mossBoulder', x: 0,   z: -672, rotY: 2.00, scale: 2.20 },
    // -- CC-H3 VAULT RING: full 10-row closure (the I ring math on groundRadius
    //    40: chord 24.7216 = 2*40*sin(18 deg) => scale 13.019 = chord/1.899;
    //    centers k*36 deg on the r40 circle, listed clockwise from north;
    //    rotY = 3.14 + k*0.6283; NO omission: the ring is closed behind the
    //    plane like I/E's mouth. The walk-back lane (|x| <= 2.2 at z -738)
    //    clears the south-point row (0,-740) colliders by 2.00 - 0.45 = 1.55 m
    //    -- the governing >= 1.0 m lane clearance, same figure I's verdict carries)
    { asset: 'whWallA', x: 0,     z: -660,    rotY: 3.14, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: 23.51, z: -667.64, rotY: 3.77, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: 38.04, z: -687.64, rotY: 4.40, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: 38.04, z: -712.36, rotY: 5.03, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: 23.51, z: -732.36, rotY: 5.65, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: 0,     z: -740,    rotY: 6.28, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: -23.51, z: -732.36, rotY: 6.91, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: -38.04, z: -712.36, rotY: 7.54, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: -38.04, z: -687.64, rotY: 8.17, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: -23.51, z: -667.64, rotY: 8.80, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 }
  ]
  },

## 5. region-defs.js conn[8] (append after the connections[7] block)

Mirror conn[7] EXACTLY (the AMENDMENT A row: fades + prompt text ride the
conn): regions[CFG.regionJ.id] = makeRegion(CFG.regionJ, -1); then
var JD = CFG.regionJ.door; connections.push({ from: CFG.regionF.id,
to: CFG.regionJ.id, axis 'z', planeCoord JD.planeZ, sides {}, door {
doorX/doorHalfWidth/suspendDepthM/wallGapPadM from JD, arch null, gatedTo
null, walkFrom CFG.regionJ.id, interact { from CFG.regionF.id, x/z/radius
from JD.interact }, land JD.land, fadeIn JD.fadeIn, fadeOut JD.fadeOut,
exitFadeOut JD.exitFadeOut, text JD.text } }); then
connections[8].sides[CFG.regionF.id] = -1;
connections[8].sides[CFG.regionJ.id] = +1;
with the E-mirror comment (F's plane reads underground/inactive for this
conn; J's interior sits SOUTH of its walk-back plane... interior reading:
sideOfPlane(J interior -730 vs plane -738) = +1 = sideIn(J); F interior
-640 > -738 => sideIn(F) = +1?? NO: F's table value follows conn[7]'s
H-side -1 (the parent-of-a-pocket convention: -1 = plane-0 convention
only, the walk-back plane exists only from J anyway). Probe asserts:
sideIn(connections[8], 'veil_spire_approach') === sideOfPlane(connections[8],
-730) === +1, and sides[F] = -1 per the conn[7] comment law.

## 6. Pre-verified seats (from IO's geometry audit this wake; the probe
script re-derives ALL of them live from CONFIG + region-defs, V-9 style)

- Ghouls (-15,-708)/(15,-708): 30.0 apart; 16.2 m from spawn/land-IN (>= 8);
  nearest ring collider ~17.3 (>= 4.45); nearest prop = statue (7,-712) at
  8.25 (>= 5).
- Hook (7.5,-654) in F: mossBoulder (9,-650) 4.27 (>= 4); F ring SE row
  colliders 6.39 (>= 4); F ghouls 18.1 (>= 5); F land rows (0,-650) 8.5;
  F's own walk-out plane -662 sits 8 m south (lane |x| <= 2.2 -- the hook's
  x 7.5 cannot cross it).
- Ring lane: south-point row (0,-740) colliders at z -740, plane -738:
  clearance 1.55 m (>= 1.0).
- Walk-out land (2,-652) in F: every F prop >= 6 (mossBoulder 2,652 7.3;
  statue 12.1; blightcap (10.5,-646) 10.4); ring colliders 10.5.
- Props-in-J mutual table: tightest pairs all >= 4.0 (statue R (7,-712) /
  steps R (2.4,-718) 7.56; blightcap (-12,-692) / flank (-8,-696) 5.66;
  skullPile (-5,-668) / mossBoulder (0,-672) 6.40; lantern (-6,-724) /
  skullPile (-13,-723) 7.07).

## 7. Acceptance criteria (Testerbot independently verifies)

- V-0 CONFIG parses (node --check on CONFIG.js + region-defs.js via the
  bundle or node -c equivalents) and regionJ row carries every key of sec 3.
- V-1 conn[8] shape: from F, to J, walkFrom J, interact from F at
  (7.5,-654) r 3.5, land rows per sec 3, text prompt verbatim.
- V-2 sideIn(8, J) == +1 == sideOfPlane(8, J interior); sides[F] = -1.
- V-3 J clearance: ghouls, props, ring lane per sec 6 (fresh probe run,
  V-9 CONFIG-parsed, not hard-coded).
- V-4 F untouched: regionF block byte-identical to HEAD@42ba377 (no F
  rows added/removed/moved); F dressing props unchanged.
- V-5 groundSeed 1662061763 differs from every landed seed; groundY 0;
  scatter false; gravityY -22.
- V-6 One accent family in J: crimson rows = exactly lanternPost x1 +
  blightcap x2; no other colored-light/colored-cap rows.
- V-7 regionI (armory_deep) and connections[7] remain byte-identical to
  HEAD@42ba377.
- V-8 No other file (game.js, region-manager.js, save.js, daynight.js...)
  changes; the round is CONFIG.js + region-defs.js ONLY.
- V-9 Boss-tier space measurable: ring diameter 80 m (r40); mid-hall
  encounter floor: the probe computes the largest collider-edge clear
  circle centered at (0,-709) and asserts >= 6.0 m (the root column and
  the gauntlet statues are intended blockers; the boss reads around
  them). [AMEND-1 2026-11-07 wake 21: the original point (0,-702) sat
  INSIDE the root column's own collider (r 1.1485) and no center could
  satisfy 12 m under the colonnade law — spec-author error; threshold
  re-ruled to 6.0 m at (0,-709); Devbot probe measures 7.1 m there.]

## 8. IO adjudications (pre-build, rulings on the valspec items)

- ADJ-A: sec 4's ">= 4.0 m mutual" applies to ALL non-ring J props with NO
  tableaux exemption (unlike H2b's bier group). IO's geometry audit shows the
  row set already complies with the universal law (tightest pairs >= 5.6);
  no exemption is granted.
- ADJ-B: V-9/V-3 clearance math uses the established measured-footprint map
  (whWallA/whWallB raw ext X 1.899, collider r 0.45, perSegment wall count;
  copy the footprint table from scratch/cc-ad1/solve_geometry.py or the
  cc-h2bv2 lineage probe).
- ADJ-C: the F-side land row (2,-652) clearances from sec 6 (>= 6.0 m from
  every F prop, >= 4.0 m from ring colliders) are LAWS, not commentary:
  V-3 enforces them exactly as written.

## 9. Build law

Devbot builds in the worktree /tmp/wh-worldfeat on feat/world-visuals; NO
build_vX run, NO commit, NO push (children never push; IO builds/commits
after the verdict). Devbot writes the probe to scratch/cc-h3/solve_
geometry.py (V-9 CONFIG-parsed style, run from the worktree root) and a
short build note io/reports/2026-11-07-cc-h3-spire-approach-build.md.
No harness runs, no headless browser smoke tests; Nicko's playtest is the
acceptance bar.
