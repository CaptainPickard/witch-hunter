# CC-H4 SPEC — The Scar-Reader, delve strata V3 boss-warden at the Spire Approach

Autopilot round 2026-11-07 (wake 22). Source: doc 47 §"Veil strata" V3 THE
PACT-SCAR + §"Veil boss-warden concepts" #2 THE SCAR-READER (witch-fauna boss
nesting in the pact-scar, doc 04 signature tier, two kit verbs re-costed from
the scar pools) + doc 47 sec "boss remix" law (same pool stats, size factor
3.0, kit verbs re-costed) + wake-21 GOALS line ("delve strata V3 hang point now
= the Spire Approach; boss space reserved, no boss yet"). This is an ENEMY +
BOSS ROUND (new boss type + generic second-lair support), the direct successor
of CC-C7 (the rot mother) and CC-H3 (the space).

## 0. Design summary (the Nicko-facing one-liner)

At the head of the Spire Approach, under the spire-root, the pact-scar has
opened into a crimson wound in the floor: THE SCAR-READER nests there — the
first warden of the Veil delve — a low-slung scar-crawler who slams the ground
in crimson venom and calls ghouls up out of the wound. Kill her and the wound
goes dark until a later In-game day raises her again.

## 1. Art anchors (Nicko law: anchor BEFORE build)

- concept-08-veil-spire.png (viewed this wake, vision_analyze): obsidian/
  charcoal primaries, CRIMSON/vermillion fissure-glow as the sole accent,
  under-lighting from ground-level glows, needle/jagged silhouette language.
  Carried into this round: the nest's scar-pool dressing + boss slam cue are
  CRIMSON (regionJ's existing red blightcap + lantern family extends; the ONE
  accent family per frame law is preserved — sources multiply inside the same
  crimson family).
- scene-02-swamp-ghouls.png (viewed this wake, vision_analyze): witch-fauna
  silhouette law = low-slung, bottom-heavy, elongated claws, ragged edges;
  wound/pact-scar detailing glows (spectral accent against muted body).
  Carried into this round: boss anim variant = the rotspawn crawler RIGID_CLIPS
  variant (the engine's low crawler grammar), body scale 3.0 (doc 47 remix law).

## 2. Engine decision (the round's central call)

SECOND boss-slam lair via the EXISTING generic machinery, with three small
generalizations so the second type coexists byte-compatibly with the rot
mother. New-script-file ban holds: CONFIG rows + small patches in enemy.js
only, exactly like CC-C7.

1. SAVE KEY generalization: `rotmother_cleared_<region>` is hardcoded today
   (Enemy.lairOnDeath / lairFlag / restoreLairs). LAIR_STATE entries gain an
   optional `prefix` field; save flag = `(prefix || 'rotmother') + '_cleared_'`
   + letter. The rot mother's keys stay BYTE-EQUAL (old saves round-trip; her
   row needs no edit). The scar-reader's key = `scarreader_cleared_J`.
2. CUE COLOR per boss: buildSlamCue's shared CUE_DARK/CUE_HOT (0x101a08 /
   0xa8d84a sickly green) become the DEFAULT pair; a CONFIG row may carry
   `cueDark` / `cueHot` which slamCueShow reads per-instance (fallback to the
   shared constants when absent — rot mother path byte-equal).
3. BODY registration path (no new clips, no new rig): assets registry name
   `scarreaderBody` points at the EXISTING rotmother glb
   (art-direction/3d/assets/races/rotmother-pixelated.glb — an unrigged body,
   so setBody's RIGID_CLIPS path applies; variant via rigidAnimByType).
   OPTIONAL disclosed step (skip if shared-material risk found, and say so in
   the build note): a `tintMaterial` CONFIG flag that clones the body's first
   MeshStandardMaterial and multiplies its color by `tint` 0x4a5a6a. Clone, not
   mutate: THREE clones share material references, and the registry template is
   reused by every instance of both boss types — an uncloned tint would paint
   the rot mother too. If Devbot cannot prove isolation, SKIP the tint and
   disclose (the crimson cue + scar pool carry the art accent; the body stays
   the pale rot chassis).

## 3. CONFIG rows (exact literals)

### 3a. CFG.enemy.scarreader (place AFTER the rotspawn block, one blank line)

    scarreader: {
      name: 'The Scar-Reader', hp: 400, dmg: 22, speed: 4.8, aggro: 16,
      pattern: 'boss-slam',
      slamRadius: 7.5, slamArcDeg: 210, slamWindup: 1.05, slamActive: 0.22,
      slamRecover: 1.15, slamCooldown: 5.5, slamTrackDegPerSec: 70,
      engageRange: 7.5,
      poison: { dps: 4.0, duration: 5.0, slow: 0.5 },   // scar venom (poison-lite v1)
      poisonText: 'Scar venom burns in the wound',
      slamKnockbackM: 6.0, slamKnockbackSec: 0.32,
      cueDark: 0x1a0508, cueHot: 0xd84a4a,              // crimson slam telegraph
      scale: 3.0,                                        // doc 47 size-factor law
      // OPTIONAL (see sec 2.3): tintMaterial: true, tint: 0x4a5a6a,
      lair: { x: 0, y: -9, region: 'J', flagPrefix: 'scarreader' },   // world (0,-709)
      lairRadius: 16,
      rearm: { days: 3, trigger: 'proximity', radius: 14 },
      loot: [{ mat: 'rot-silk', n: [2, 4] }, { mat: 'rot-gland', n: [1, 2] }],
      minions: { asset: 'ghoul', cap: 2, interval: 7.0, range: 5.0,
                 dieOnMasterDeath: true },               // undead drawn to the wound
      radius: 1.3,
      corpseLingerSec: 10, maxCorpses: 12,
      riseSec: 1.4
    }

Derivation notes (the remix law applied, all PROPOSED, Nicko tunes): pool =
ghoul (45 hp / 8 dmg) x boss weights ~ rot-mother precedent shifted one step
faster and lighter: hp 400 (x8.9 pool), dmg 22 (x2.75), wider arc (210 vs 180),
faster track (70 vs the mother's), venom dps 4.0 vs her 3.5. Minions are ghouls
(doc 47 V3 encounter grammar: "undead drawn to the wound") — NO new minion
type this round; the scarlings-as-new-type design belongs to a later delve
round if Nicko wants them.

### 3b. regionJ.lairs (new key INSIDE the regionJ block, after the enemies array)

    // CC-H4: the Scar-Reader nests at the wake-21-reserved boss space (0,-709),
    // 9.0 m south of the spire-root column (its collider), inside the vault ring.
    lairs: [
      { type: 'scarreader' }        // CONFIG.enemy.scarreader.lair carries the seat
    ]

NOTE + ENGINE FACT: region-manager (line ~1909) instantiates
`regionCfg.enemies.concat(regionCfg.lairs || [])` and Enemy derives the seat
from `CONFIG.enemy[type].lair` via lairNest — the lairs ROW needs no x/z (unlike
regionD's row which duplicates them for legacy reasons). If the current
Enemy constructor path requires x/z on the row itself, Devbot MAY add
`x: 0, z: -709` to the row to match regionD's shape and MUST disclose which
shape the live code consumed. Do not rewire region-manager for this.

### 3c. regionJ.rotLair (new key INSIDE the regionJ block; the nest dressing)

    rotLair: {
      pool: { radius: 9, segments: 40, rings: 5, lift: 0.08,
        color: 0x1a0f12, color2: 0x2a1116, speck: 0x5a2028, textureSeed: 20261107,
        edgeFeather: 0.22 },
      light: { height: 1.3, intensity: 1.7, color: 0xd85050 },
      fog: { cards: 8, radiusMin: 2.0, radiusMax: 7.0, heightMin: 0.4, heightMax: 1.4,
        width: 3.2, height: 1.3, opacity: 0.15, color: 0x8a4550, driftSpeed: 0.12,
        showWithinM: 70 },
      cullM: 170
    }

Crimson family (concept-08 anchor): pool dark scar-tissue maroon, light +
fog red. textureSeed 20261107 is FRESH (not equal to the landed den's seed
20261012 or any seed in CONFIG: grep-verify before commit).

### 3d. Registries (one-line edits each)

- CONFIG.enemy.bodyByType: append `scarreader: 'scarreaderBody'`.
- CONFIG.enemy.rigidAnimByType: append `scarreader: 'rotspawn'` (the crawler
  variant per the scene-02 anchor).
- assets.js manifest: `scarreaderBody: 'art-direction/3d/assets/races/
  rotmother-pixelated.glb'` (same file as rotmotherBody, separate key; the
  unrigged CHARACTERS clip-count map needs NO new entry).
- CONFIG.deeds: append `kill_scarreader: 8` (the hunter's trade against the
  Fall's machinery; PROPOSED, Nicko tunes).
- CONFIG.leveling.xpSources: append `kill_scarreader: 200` (the ~0.5 x hpMax
  law, same as the mother's 240/460).
- WH_ENEMY_TYPES (enemy.js last line): append `scarreader`.

## 4. enemy.js small patches (the three generalizations, keep-alive callouts)

1. lairFlag / LAIR_STATE prefix:
   - LAIR_STATE entries: `{ cleared, day, prefix? }` — lairOnDeath writes
     `prefix: this.cfg.lair.flagPrefix`.
   - captureLairs: flag = `(st.prefix || 'rotmother') + '_cleared_' + letter`.
   - restoreLairs: regex `/^([a-z][a-z0-9]*)-cleared-([A-Z])$/` in UNDERSCORE
     form /^( [a-z][a-z0-9]*)_cleared_([A-Z])$/ storing both prefix and letter;
     old keys match (their capture group 1 = 'rotmother').
   - Keep-alive: every LAIR_STATE read site (`st.cleared` / `st.day`) keeps
     working with plain entries restored from old saves.
2. slamCueShow color override: per-instance colors from this.cfg.cueDark /
   cueHot falling back to the shared CUE_DARK/CUE_HOT constants. The
   buildSlamCue shared-constant lazy-init line stays; a row without cueDark
   renders the EXACT current colors (rot mother byte-equal).
3. OPTIONAL tint hook (sec 2.3): in setBody, if `this.cfg.tintMaterial`,
   traverse the body for the first mesh material, clone it, multiply color by
   this.cfg.tint, assign. Absent flag = byte-equal path. SKIP + DISCLOSE if
   isolation cannot be proven.

Keep-alive callouts: deriveCfg's boss-slam mapping, lairTick, spawnMinion,
pruneMinions, buildLair, lairSockets stay UNCHANGED (they are already generic
over boss-slam rows; lairSockets picks up the new row automatically via its
CFG loop — verify it does not double-light J in the probe).

## 5. Placement law (the numbers this round must move)

- Boss nest world (0,-709): 21 m north of J's spawn row (0,-730), 9.0 m south
  of the spire-root column center (0,-700), 30+ m from both ghouls (±15,-708).
- lairRadius 16 = minions spawn only after the player walks deeper than ~16 m
  toward the nest (landing at 21 m: two strides of approach before the pack
  wakes). rearm.radius 14 matches the den's grammar.
- Probe (new scratch/cc-h3/scc_lair_probe.py, CONFIG-parsed, run from the
  worktree root — reuse the cc-h3 solve_geometry.py collider footprint table):
  (a) nest parses to world (0,-709) exactly;
  (b) clear circle centered AT the nest >= 6.0 m (the wake-21 V-9 ruling: the
  root column + statues are intended blockers; the boss reads around them);
  (c) every OTHER J prop edge >= 4.0 m off the nest's slam reach circle r 7.5
  where physically possible — list the violators instead of failing them (the
  colonnade rows are inside the reach by design; the probe REPORTS them);
  (d) ghouls >= 8.0 m from the nest;
  (e) lairSockets census: exactly ONE scar-reader socket for regionJ (no
  duplicate rotLair@ keys); regionD still yields exactly one rot-mother socket;
  (f) textureSeed 20261107 appears nowhere else in CONFIG.js.

## 6. Acceptance criteria (letter families, numbered under each)

- A (CONFIG boss row): A1 scarreader row contains every field from sec 3a
  with the exact literal values; A2 the row sits after rotspawn and before
  whatever follows CONFIG.enemy; A3 derivation comments present (remix-law
  note + minions note).
- B (regionJ rows): B1 lairs row per sec 3b (disclosed shape from the Engine
  FACT note); B2 rotLair block per sec 3c byte-matching the literals; B3 no
  other regionJ key changed (grep diff: prop rows, enemies, door, ground).
- C (registries): C1 bodyByType + rigidAnimByType rows; C2 assets manifest
  scarreaderBody entry; C3 CHARACTERS map UNCHANGED (no new clip count);
  C4 deeds + xpSources rows with exact values 8 / 200; C5 WH_ENEMY_TYPES
  gained 'scarreader'.
- D (save generalization): D1 prefix write in lairOnDeath; D2 captureLairs
  prefix fallback 'rotmother'; D3 restoreLairs accepts BOTH key shapes and
  preserves the rotmother byte-equality (a literal 'rotmother_cleared_C' key
  round-trips through the new regex); D4 no LAIR_STATE read site broken
  (list each site: lairTick, lairDressingTick, lairSockets, captureLairs,
  restoreLairs — all compile-path consistent).
- E (cue override): E1 slamCueShow reads per-instance cfg colors with the
  shared-constant fallback; E2 the CUE_DARK init line survives unchanged;
  E3 a row lacking cueDark would render the old colors (reason, not runtime
  proof).
- F (probe): F1 scc_lair_probe.py exists in scratch/cc-h3/, runs clean from
  the worktree root, prints (a)-(f) with PASS/REPORT lines; F2 no browser, no
  harness, no build_vX run, no commit, no push.
- G (build note): G1 io/reports/2026-11-07-cc-h4-scar-reader-build.md with:
  the lairs-row shape consumed by live code (sec 3b note), the tint decision
  (landed + isolation proof OR skipped + reason), any deviation list, and the
  probe's actual numeric outputs (nest distance, clear-circle value, ghoul
  distances, socket censuses).

## 7. Build law

Devbot builds in the worktree /tmp/wh-worldfeat on feat/world-visuals; NO
build_vX run, NO commit, NO push (children never push; IO builds/commits after
the verdict). Probe = scratch/cc-h3/scc_lair_probe.py (Python, CONFIG-parsed,
static; no THREE render, no browser). No harness runs, no headless browser
smoke tests; Nicko's playtest is the acceptance bar. NO-GIT clause: children
never stage, commit, or push anything; IO is the sole gatekeeper.

## 8. Amendment log

(none yet — Testerbot AMBs get ruled here; numbered, dated, inline.)

## 8. Amendment log

- AMENDMENT R1 (2026-11-07, IO): cue-color fallback ruled PER-ELEMENT (a row
  with cueDark but no cueHot uses the shared CUE_HOT for the hot color and
  vice versa) — refines sec 2.2. All other Testerbot AMB-1..8 rulings recorded
  in the valspec's AMENDMENT R1 block; none change implementation literals.
