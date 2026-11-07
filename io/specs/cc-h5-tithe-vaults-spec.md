# CC-H5 — THE TITHE VAULTS (delve strata V4) — IO spec

Round: delve strata V4, doc 47 STRATA V4 THE TITHE VAULTS. Chained off the
Spire Approach (regionJ, landed CC-H3/H4). Art anchor (art law): inherited
chain anchors concept-08-veil-spire.png + char-04-bannerman-dark.png, viewed
2026-11-07 this wake. The 36-set has no tithe-vault frame; a NEW piece was
planned but the image provider is hard-blocked this wake (image_generate ->
HTTP 400 "gpt-5.5 not supported when using Codex with a ChatGPT account";
was HTTP 401 on wake 22; no alternative image credential on the box, no
local diffusion stack). Art-block ruling: the Veil delve chain inherits its
ancestors' anchors (same spire, same crimson accent family, same zealot
family per char-04). New-frame generation stays a separate lane when the
provider is fixed.

## 1. Scope (the two-file law, mirroring CC-H3)

Files changed: prototype/js/CONFIG.js + prototype/js/region-defs.js ONLY.
No engine files (enemy.js consumes new CONFIG rows generically: cfgFor
falls through any CONFIG row; bodyByType / animVariantByType map the body).
No assets. No CSS/html. Traps-as-authored-hazards (doc 47 V4 perils) are
OUT of this round (needs a new hazard primitive) — future lane CC-H5b.

## 2. CONFIG.js — CONFIG.enemy additions (append after the scarreader row)

### 2.1 zealot (Veil Faithful trash pack; bandit chassis + guard grammar)

    zealot: {
      // doc 47 V4: "Veil Faithful zealot packs defending the devotion they
      // welcome" (doc 04 pack grammar via the bandit chassis ai1; doc 34
      // soldier guard verbs). Bandit baseline, leaner hp (fasting fanatics).
      // All PROPOSED, Nicko tunes.
      hpMax: 60.0,
      moveSpeed: 3.6,
      chaseSpeed: 5.0,
      attackDamage: 12.0,
      attackRange: 2.4,
      attackCooldown: 1.4,
      sightRadius: 16.0,
      leashRadius: 34.0,
      staggerTime: 0.4,
      radius: 0.7,
      aggroPingInterval: 0.2,
      attackPhase: { windup: 0.7, active: 0.12, recover: 0.8,
        hitArcDeg: 50, trackDegPerSec: 180 },        // bandit's values verbatim
      ai1: { decisionSeconds: 0.4, alwaysKnowsRadius: 4.0,
        strafeBandInner: 3.4, strafeBandOuter: 7.0, strafeSpeedMult: 0.75,
        strafeDirFlipSeconds: 1.8, attackRadius: 2.4, attackBias: 0.55,
        guardChance: 0.45, guardRespondRadius: 6.0, guardSecondsMax: 1.6,
        guardArcDeg: 50, guardDamageMult: 0.5 }      // bandit's ai1 verbatim
        // == the parry/discipline grammar comes from the landed AI1 guard
        // machinery; no engine edits (enemy.js ai1For reads cfg.ai1).
    },

### 2.2 tithecaptain (THE TITHE CAPTAIN — the vault-gate warden)

doc 47 V4 warden: "a zealot-captain warden at the vault gate
(faction-soldier boss: doc 04/34 soldier grammar, parry-capable, smaller
readable window than the player's)". ENGINE LAW (enemy.js:152): the lair
machinery (save flag / 3-day re-arm / minions) attaches only to
pattern 'boss-slam' rows — the captain therefore rides a boss-slam chassis
TUNED SOLDIER-DISCIPLINED (the CC-H4 precedent: the Scar-Reader rode the
same chassis): a narrow, fast-tracked shock-slam = the disciplined shield-
wall read, NOT a wild AoE. Guard ai1 (parry-capable, smaller window than
the bandit's) rides ALONGSIDE the slam (ai1For reads cfg.ai1 independent of
pattern). All PROPOSED, Nicko tunes.

    tithecaptain: {
      name: 'The Tithe Captain', hp: 320, dmg: 20, speed: 4.2, aggro: 16,
      pattern: 'boss-slam',
      slamRadius: 4.2, slamArcDeg: 100, slamWindup: 0.85, slamActive: 0.18,
      slamRecover: 0.9, slamCooldown: 3.8, slamTrackDegPerSec: 110,
      engageRange: 4.2,
      cueDark: 0x1a0508, cueHot: 0xd84a4a,        // the chain's crimson cue family
      scale: 2.1,                                  // soldier boss vs the 3.0 beast tier
      lair: { x: 0, y: 8, region: 'K', flagPrefix: 'tithecaptain' },
                                                   // world (0,-872), key tithecaptain_cleared_K
      lairRadius: 16,
      rearm: { days: 3, trigger: 'proximity', radius: 14 },
      loot: [{ mat: 'stolenCoin', n: [1, 3] }],    // THE TITHE: the collection itself
      minions: { asset: 'zealot', cap: 2, interval: 7.0, range: 5.0,
                 dieOnMasterDeath: true },         // his gate guard answers him
      radius: 1.0,
      corpseLingerSec: 10, maxCorpses: 8,
      riseSec: 1.4,
      barLiftM: 2.2,
      ai1: { decisionSeconds: 0.4, alwaysKnowsRadius: 4.5,
        strafeBandInner: 3.6, strafeBandOuter: 7.5, strafeSpeedMult: 0.7,
        strafeDirFlipSeconds: 2.0, attackRadius: 4.2, attackBias: 0.5,
        guardChance: 0.6, guardRespondRadius: 6.0, guardSecondsMax: 1.8,
        guardArcDeg: 45, guardDamageMult: 0.5 }    // smaller readable window: 45 vs 50 deg
    },

NOTE: deriveCfg (enemy.js) maps hp/dmg/speed/aggro -> engine keys for any
pattern row and rewrites attackRange/attackPhase from the slam keys for
boss-slam; cfg.ai1 survives. CFG.items.stolenCoin exists (IO verified by
node eval: stolenCoin item present).

### 2.3 CONFIG.enemy body map additions

    bodyByType:       + zealot: 'banditBody'
    animVariantByType: + zealot: 'bandit'
(the captain wears NO row: an unknown type falls back to ghoulBody/'bandit'
— but ADD explicit rows for him too, symmetry law:
      bodyByType + tithecaptain: 'banditBody'; animVariantByType + tithecaptain: 'bandit')

## 3. CONFIG.js — regionK (THE VAULTS pocket, the J-mirror)

Append after regionJ's closing brace, var-shape identical (id, name,
center, groundRadius, groundY, groundColor, groundColor2, groundSeed,
scatter, spawn, gravityY, fogColor, fogDensity, ambientLightLevel, door,
enemies, lairs, rotLair, props).

  regionK: {
    id: 'tithe_vaults',
    name: "The Tithe Vaults",
    center: { x: 0, z: -880 },        // 180 m deeper than J's center (0,-700): one clean
                                      // stratum gap; K's north rim -846 vs J's ring south
                                      // point -740 = 106 m of unrendered dark (the
                                      // one-active-region law makes the gap invisible)
    groundRadius: 34,                 // PROPOSED (I's 18 x1.9, below J's boss-tier 40)
    groundY: 0,                       // flat disc
    groundColor: 0x0b0d12,            // one step colder than J's 0x0d0f15
    groundColor2: 0x0e1013,
    groundSeed: 448271909,            // FRESH: differs from every landed seed
                                      // (1217/1218/1219/1329/1440/1651/1654/1662061763)
    scatter: false,                   // hand rows only (D/E/F/I/J law)
    spawn: { x: 0, z: -856 },         // 12 m inside the NORTH rim (the J-mirror: you
                                      // descend from the approach, the walk-back plane
                                      // is BEHIND you at the north rim)
    gravityY: -22,
    // sec DARKNESS: density 0.16 -> d95 = sqrt(-ln 0.05)/0.16 = 10.82 m:
    // one stratum quieter than J's 11.61. Region row fog/fill/ambient only.
    fogColor: 0x0a0810,               // the veil fog family
    fogDensity: 0.16,
    ambientLightLevel: 0.045,         // J is 0.05; K is one step deeper
    door: {
      planeZ: -844,                   // 2 m north of the north rim -846, INSIDE the disc
                                      // boundary; the walk-back lane exits through it
      doorX: 0,
      doorHalfWidth: 2.2,             // the F/J tomb-mouth lane
      suspendDepthM: 0,
      wallGapPadM: 0,
      walkFrom: 'tithe_vaults',       // ONE-SIDED: the plane crosses ONLY from K
                                      // (conn[8] grammar: J keeps no walkFrom)
      interact: {
        from: 'veil_spire_approach',  // the J-side hook (conn[8] F-side pattern)
        x: 7.5, z: -678, radius: 3.5  // 7.5 m NE of the spire-root colonnade approach,
                                      // INSIDE J's north half; probe-verified clear of
                                      // every J row (nearest: mossBoulder 9.60 m)
      },
      land: {
        veil_spire_approach: { x: 2, z: -682, faceX: 2, faceZ: -700 },
                                      // walk back INTO J beside the hook, facing the
                                      // spire root hall
        tithe_vaults:  { x: 0, z: -856, faceX: 0, faceZ: -880 }
                                      // INTO K = the spawn row, facing the vault gate
      },
      fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
      text: { prompt: 'E - Descend into the tithe vaults' }
    },
    // THE ZEALOT PACKS + the drifted dead (doc 47 V4 encounters; doc 34):
    // zealots defend the vault's north approach, ghouls drift the deeper
    // coin rows. Distances: zealots 14.2/18.0/14.2 apart? (SEE SEC 6 for the
    // audited numbers; >= 12.5 m mutual law). Each >= 8 m from spawn/land-in.
    enemies: [
      { type: 'zealot', x: -9, z: -876 },
      { type: 'zealot', x:  9, z: -876 },
      { type: 'zealot', x:  0, z: -865 },
      { type: 'ghoul',  x: -11, z: -892 },
      { type: 'ghoul',  x:  11, z: -892 }
    ],
    // CC-H5: the captain nests at the vault gate dais (0,-872), 12 m south
    // of the spawn row, inside the ring. x/z CARRIED (regionJ legacy shape:
    // the Enemy constructor consumes row x/z for the BODY; lairNest consumes
    // .lair for nest/dressing/save letter 'K').
    lairs: [
      { type: 'tithecaptain', x: 0, z: -872 }
    ],
    // The debt-glow pool at the gate (the H4 scar-pool pattern; the ONE
    // crimson family's engine half — colors chosen inside the 0xd85050
    // crimson family; textureSeed FRESH vs 20261012/20261107).
    rotLair: {
      pool: { radius: 8, segments: 40, rings: 5, lift: 0.08,
        color: 0x1a0f12, color2: 0x2a1116, speck: 0x5a2028, textureSeed: 448271910,
        edgeFeather: 0.22 },
      light: { height: 1.3, intensity: 1.6, color: 0xd85050 },
      fog: { cards: 8, radiusMin: 2.0, radiusMax: 7.0, heightMin: 0.4, heightMax: 1.4,
        width: 3.2, height: 1.3, opacity: 0.15, color: 0x8a4550, driftSpeed: 0.12,
        showWithinM: 70 },
      cullM: 170
    },
    props: [
      // -- THE VAULT GATE: mourning-statuette guards watching the dais
      //    (the J gauntlet family continues; the processional ends here)
      { asset: 'mourningStatue', x: -6, z: -888, rotY: 4.00, scale: 1.00 },
      { asset: 'mourningStatue', x:  6, z: -888, rotY: 5.28, scale: 1.00 },
      { asset: 'mourningStatue', x: -6, z: -896, rotY: 4.00, scale: 1.00 },
      { asset: 'mourningStatue', x:  6, z: -896, rotY: 5.28, scale: 1.00 },
      { asset: 'stoneSteps',     x: -2.4, z: -893, rotY: 0.60, scale: 1.10 },
      { asset: 'stoneSteps',     x:  2.4, z: -893, rotY: 5.68, scale: 1.10 },
      // -- the vault-gate colonnade: the dais trio flanking the captain's seat
      { asset: 'okRuinColumn', x: -8, z: -872, rotY: 0.30, scale: 1.40 },
      { asset: 'okRuinColumn', x:  8, z: -872, rotY: 5.98, scale: 1.40 },
      { asset: 'okRuinColumn', x:  0, z: -876, rotY: 0.00, scale: 2.40 },
      // -- the ONE crimson family (lamp + caps; the pool is its engine half)
      { asset: 'lanternPost', x: -13, z: -882, rotY: 5.20, scale: 1 },
      { asset: 'blightcap',   x: -13, z: -868, rotY: 3.62, scale: 0.90 },
      { asset: 'blightcap',   x:  13, z: -868, rotY: 0.63, scale: 0.90 },
      // -- erasure scatter (J's grammar): 2 skull piles, 1 moss boulder
      { asset: 'skullPile',   x: -16, z: -896, rotY: 4.40, scale: 1.00 },
      { asset: 'skullPile',   x:   6, z: -908, rotY: 3.60, scale: 1.00 },
      { asset: 'mossBoulder', x: -14, z: -872, rotY: 2.00, scale: 2.20 },
      // -- CC-H5 VAULT RING: full 10-row closure, the J ring math on
      //    groundRadius 34: chord 21.0136 = 2*34*sin(18 deg) =>
      //    scale 11.067 = chord/1.899; centers k*36 deg on the r34 circle,
      //    clockwise from north (x = 34 sin a, z = -880 - 34 cos a),
      //    rotY = 3.14 + k*0.6283. NO omission: the ring is closed behind
      //    the plane. The walk-back lane (|x| <= 2.2 at the plane -844)
      //    clears the north-point row (0,-846) colliders by 2.00 - 0.45
      //    = 1.55 m -- the governing >= 1.0 m lane clearance (the J/I figure).
      { asset: 'whWallA', x:   0.00, z: -846.00, rotY: 3.14, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:  19.98, z: -852.78, rotY: 3.77, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x:  32.34, z: -867.48, rotY: 4.40, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:  32.34, z: -892.52, rotY: 5.03, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x:  19.98, z: -907.22, rotY: 5.65, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:   0.00, z: -914.00, rotY: 6.28, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x: -19.98, z: -907.22, rotY: 6.91, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x: -32.34, z: -892.52, rotY: 7.54, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x: -32.34, z: -867.48, rotY: 8.17, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x: -19.98, z: -852.78, rotY: 8.80, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 }
    ]
  },

(whWall ring coordinates: x = 34*sin(k*36deg) rounded to 2dp; z = -880 -
34*cos(k*36deg) rounded to 2dp. Devbot's probe RE-DERIVES all ten rows
CONFIG-parsed and asserts the chord/radius math live — hard-coded ring rows
in this section are the SPEC AUTHOR'S arithmetic, the probe is the truth.)

## 4. region-defs.js conn[9] (append after the connections[8] sides rows)

Mirror conn[8] EXACTLY (the conn[7]/conn[8] chain law: fades + prompt text
ride the conn):

  // CC-H5 tithe_vaults: plane-0 convention only; J-side portal is an
  // interact hook, K-side mouth is a walk-back plane (conn[7] precedent).
  regions[CFG.regionK.id] = makeRegion(CFG.regionK, -1);
  var KD = CFG.regionK.door;
  connections.push({
    from: CFG.regionJ.id,
    to: CFG.regionK.id,
    axis: 'z',
    planeCoord: KD.planeZ,
    sides: {},
    door: {
      doorX: KD.doorX, doorHalfWidth: KD.doorHalfWidth,
      suspendDepthM: KD.suspendDepthM, wallGapPadM: KD.wallGapPadM,
      arch: null, gatedTo: null,
      walkFrom: CFG.regionK.id,
      interact: { from: CFG.regionJ.id, x: KD.interact.x, z: KD.interact.z, radius: KD.interact.radius },
      land: KD.land,
      fadeIn: KD.fadeIn, fadeOut: KD.fadeOut, exitFadeOut: KD.exitFadeOut,
      text: KD.text                       // AMENDMENT A: the portal prompt + fades ride the conn
    }
  });
  // E-mirror: J's plane is underground/inactive for this conn; K's interior
  // is SOUTH of its walk-back plane (-880/-856 < -844). The J-side table
  // value follows the geometry (J's interior sits NORTH of -844 too), the
  // K side follows sideOfPlane.
  connections[9].sides[CFG.regionJ.id] = +1;
  connections[9].sides[CFG.regionK.id] = -1;

Probe asserts (the H3 V-2 law adapted): sideIn(connections[9],
CFG.regionK.id) === sideOfPlane(connections[9], CFG.regionK.spawn.z) === -1,
and sideIn(connections[9], CFG.regionJ.id) === +1.

## 5. Pre-verified seats (IO pre-audit this wake: scratch/cc-h5/io_preaudit.py,
95 checks 0 failures; Devbot's live probe re-derives ALL of them from CONFIG
+ region-defs and adds the ring/footprint math)

- Hook (7.5,-678) in J: mossBoulder (0,-672) 9.60 (>= 4.5), blightcap
  (12,-692) 14.71, skullPile (-5,-668) 16.01, okRuinColumn (8,-696) 18.01,
  ring J SE row 19.07, J's whWallA (0,-660) 19.50, J ghouls 30.92/37.50
  (>= 5.0), scar-reader seat 31.89, J land-in (0,-730) 52.54; hook x 7.5
  outside J's own plane lane (|x| <= 2.2).
- Land-into-J (2,-682): nearest J prop mossBoulder 6.32 (>= 6.0), nearest
  J enemy 32.70 (>= 5.0); 20 m north of J's own walk-out plane (-662).
- K ring lane: north-point row (0,-846) colliders at -846, plane -844:
  clearance 1.55 m (>= 1.0).
- K enemies: spawn (0,-856) to nearest zealot (0,-865) 9.0 (>= 8); to
  ghouls 40+; enemy mutual >= 14.2 (>= 12.5); ring-edge clear >= 4.45
  (probe re-derives); nearest K prop to any enemy seat per probe (>= 5).
- K props mutual: tightest pair >= 4.0 (>= 4.0 universal law, NO exemption;
  the lanternPost (-13,-882) sits 5.0+ from every other row after the
  pre-audit nudge).
- Boss seat: largest collider-edge clear circle at (0,-872) >= 6.0 m
  (the gate trio + statues are intended blockers; the captain reads around
  them) -- the H3 AMEND-1 threshold, applied at K's dais.
- Walk-out land INTO K (0,-856): every K prop >= 32; ring colliders >= 9.
- tol-K-north-vs-J-south-rows: K's north rim -846 vs J's ring south point
  row (0,-740): 106 m gap (the one-active-region tolerance band swallows it).

## 6. Acceptance criteria (Testerbot independently verifies)

- V-0 CONFIG parses (node --check / eval) and regionK carries every key of
  sec 3; the zealot + tithecaptain rows carry every key of sec 2.
- V-1 conn[9] shape: from J, to K, walkFrom K, interact from J at
  (7.5,-678) r 3.5, land rows per sec 3, text prompt verbatim 'E - Descend
  into the tithe vaults'.
- V-2 sideIn(9, K) === sideOfPlane(9, K spawn -856) === -1; sides[J] = +1;
  connections.length 10; connectionBetween(J,K) === connections[9] both
  directions.
- V-3 K clearance: enemies (mutual >= 12.5, vs ring >= 4.45, vs spawn/land
  >= 8, vs props >= 5), props mutual >= 4.0 (universal), lane >= 1.0,
  hook-in-J >= 4.5 from every J prop, land-into-J >= 6.0 props / >= 5.0
  enemies; boss-seat clear circle >= 6.0 -- ALL from the fresh probe
  (CONFIG-parsed, not hard-coded; V-9 style).
- V-4 regionJ block + conn[8] byte-identical to HEAD (no J rows added,
  removed, or moved; J's props/enemies/lairs/rotLair untouched).
- V-5 groundSeed 448271909 differs from every other groundSeed/textureSeed
  in CONFIG; groundY 0; scatter false; gravityY -22.
- V-6 ONE accent family in K: crimson rows = lanternPost x1 + blightcap
  x2 + the tithecaptain lair dressing (rotLair light 0xd85050 family, the
  H4 precedent); no other colored-light/colored-cap rows in K.
- V-7 regionI (armory_deep) + connections[7]/[8] remain byte-identical.
- V-8 No other file changes: CONFIG.js + region-defs.js ONLY (io/ and
  scratch/ writes exempt; prototype/ JS/CSS/HTML beyond the two files
  = FAIL).
- V-9 zealot wired engine-side WITHOUT engine edits: CFG.enemy.zealot
  exists; CFG.enemy.bodyByType.zealot === 'banditBody';
  CFG.enemy.animVariantByType.zealot === 'bandit'; a node eval of cfgFor
  logic equivalent (CFG.zealot truthy, no pattern key -> returned as-is)
  holds for zealot.
- V-10 tithecaptain wired: pattern 'boss-slam'; lair.region 'K' →
  lairNest derives (0 + 0, -880 + 8) = (0,-872) matching the lairs row;
  flagPrefix 'tithecaptain' (save key tithecaptain_cleared_K per the
  scarreader_cleared_J pattern); minions asset 'zealot'; loot mat
  'stolenCoin' present in CFG.items; ai1 present (guard machine rides).
- V-11 fog/darkness math: density 0.16 => d95 = 10.82 m (probe computes,
  rounding tolerance 0.05); ambientLightLevel 0.045 < J's 0.05; J's
  ambient 0.05 < F's 0.055 untouched.
- V-12 zealot seats vs J: K's enemies/hooks live only in regionK; no K
  row collides with J's rows (tol band per sec 5's last item).

## 7. IO adjudications (pre-build rulings)

- ADJ-A: sec 5/6 prop-mutual law is UNIVERSAL (>= 4.0 m, every pair) — no
  tableaux exemption in K (unlike H2b's bier dais). The pre-audit seed
  already complies (tightest 5.0+); Devbot's probe enforces it live.
- ADJ-B: footprint map = the measured-footprint table (whWallA/whWallB raw
  ext X 1.899, collider r 0.45, perSegment wall count) — copy from
  scratch/cc-h3/solve_geometry.py lineage (or cc-h2bv2); the probe's ring
  rows must be re-derived from CONFIG, not copied from sec 3's literals.
- ADJ-C: the J-side hook/land clearances (>= 4.5 props hook-side, >= 6.0
  props land-side, >= 5.0 enemies both) are LAWS in V-3, not commentary.
- ADJ-D: the captain is boss-slam BY ENGINE LAW (enemy.js:152 gates the
  lair machinery on the pattern) — this is the CC-H4 precedent, disclosed
  here so the valspec pins it as DESIGN, not deviation. The guard ai1 row
  alongside pattern boss-slam is the parry-capable soldier read; if the
  build shows ai1 dead under boss-slam (any branch that skips ai1For for
  slam patterns), that specific finding is DISCLOSED in the build note and
  adjudicated by IO, never silently dropped.
- ADJ-E: K's spawn/land row (0,-856) pairs with plane -844 (12 m inside
  the north rim): the walk-EXIT faces south into the vault; the J-mirror
  (spawn 30 m deep) is intentionally SHORTENED to 12 m so the zealot
  packs' aggro radii (16 m sight) don't swallow the landing row.

## 8. Build law

Devbot builds in the worktree /tmp/wh-worldfeat on feat/world-visuals; NO
build_vX run, NO commit, NO push (children never push; IO builds/commits
after the verdict). Devbot writes the probe to scratch/cc-h5/
solve_geometry.py (V-9 CONFIG-parsed style, run from the worktree root;
node-based like the h3 probe) and a short build note io/reports/
2026-11-07-cc-h5-tithe-vaults-build.md. No harness runs, no headless
browser smoke tests; Nicko's playtest is the acceptance bar.

Valspec child: write io/specs/cc-h5-tithe-vaults-valspec.md from THIS spec
BEFORE the build dispatch (gate order law). Testerbot validation child:
independent runs of Devbot's probe PLUS its own independent checks against
the valspec; verdict to io/reports/2026-11-07-cc-h5-tithe-vaults-validation.md.
