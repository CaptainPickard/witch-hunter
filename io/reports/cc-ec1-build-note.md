# CC-EC1 Build Note — Coven Acolyte (doc-34 enemy caster + magicDefense hook activation)

Round: CC-EC1 · 2026-11-06 · Builder: Devbot (gate step 3)
Worktree: /tmp/wh-worldfeat (branch feat/world-visuals) · Spec: io/specs/cc-ec1-coven-acolyte-spec.md · Valspec: io/specs/cc-ec1-coven-acolyte-valspec.md
Art anchor: **art-direction/concepts/char-09-coven-wizard.png** (+web twin; char-02-thrall.png secondary) — charcoal/deep-teal robes, ONE cyan accent per frame (0x4fd8c8 family), NO red/orange on the acolyte or its bolt.

## Touched file set (R1)

| File | Change shape |
|---|---|
| prototype/js/CONFIG.js | + coven enemy row (after wolf, sibling), + top-level enemySpell.covenBolt sibling of spell.*, bodyByType/animVariantByType extensions, + kill_coven: 30, + 2 APPEND-ONLY regionC rows (indices 50/51) |
| prototype/js/assets.js | + MANIFEST covenBody row, + CHARACTERS covenBody: 6 |
| prototype/js/enemy.js | + coven cast branch (FSM attack), + keep-distance override in attack-hold, + cast glow presentation, + faceYawToward helper, ctor fields, + Enemy.onEnemyBolt hook |
| prototype/js/spells.js | + WH_CovenBolt class, + WH_SPELLS.spawnEnemyBolt registry helper |
| prototype/js/game.js | + game.enemyBolts init, + onEnemyBolt wiring, + enemy-bolt update loop with the magicDefense call site |
| prototype/builds/v8-playable.html | rebuild artifact |

Diff character in the 5 source files: **additions only** except three rows extended in place by appending a key
(bodyByType / animVariantByType / CHARACTERS — each is one pre-existing row extended with `coven: 'covenBody'` /
`coven: 'bandit'` / `covenBody: 6`). No `{type:` row anywhere in CONFIG.js was deleted, modified, or reordered
(git diff `^-.*type:` count = 0 — V3.1 holds byte-strict, including the last CC-C6 Charlie bandit row, which stays
byte-identical; the coven rows join the array via a comma-first continuation line `, { type: 'coven', ...`).

## Deviations against valspec §4 (all expected-class, all sanctioned)

- **ED-1** — covenBody = `elf-dawn-refuser-male.rigged.glb`. `test -f` performed BEFORE writing the row:
  human-female-caster.rigged.glb does not exist on disk; the elf fallback does (verified again this build).
  Placeholder robe palette acknowledged (raw 2048 JPEG; accent law governs the bolt + cast glow).
- **ED-2** — BODY_PNG row OMITTED for covenBody: no pixelated bake exists for the elf rig and no
  races_regen/rspec/ directory exists. Body renders raw-texture. BODY_PNG block otherwise untouched.
- **ED-3** — NO pooled light consumed for coven bolts. The covenBolt CONFIG `light` / `projectileLight` rows land
  verbatim per spec but stay inert (no code reads them this round); the player-firebolt projectileLight pool and
  light.js are untouched (`git diff -- prototype/js/light.js` = EMPTY).
- **ED-4** — valspec census corrections C1–C5 honored: player.radius pre-exists = 0.7 (CONFIG ~1569) and is reused
  live, NOT added; body/PNG tables live in assets.js MANIFEST/BODY_PNG, not CONFIG.assets; regionC array end is the
  CC-C6 Charlie row, coven rows appended at indices 50/51; CHARACTERS.covenBody: 6 added per C5 (clip-capture +
  per-instance skeleton-clone requirement).
- **ED-5** — ~5 benign `[WH anim] missing … falling back` warns per coven body expected: animVariantByType.coven =
  'bandit' over the elf's 6 universal clips (Idle/Walk/Run/Attack1/Hit/Death; valspec census parsed exactly 6);
  death IS the universal WH_Death. CharacterAnim construction rides the existing machinery (no new clip-capture
  path needed).
- **ED-6 — melee active-window choice = (b)**: the coven gate inside FSM 'attack' skips the shared attack-phase
  branch entirely — `canDamagePlayer` is NEVER called for a coven (not even with attackDamage = 0). The
  windup/active/recover/hitArcDec/trackDegPerSec numbers are preserved on the row and drive the cast clock; the
  0.12s 'active' window is presentation-only (spell release). No code path applies nonzero coven melee damage.

## RegionC clearance table (A12 / §V10 — computed pre-insertion, re-run post-insertion, unchanged)

Checker: scratch/cc-ec1/clearance.py (123 check-set members: 22 camp guards + 10 CC-C6 rows + regionC wolf rows,
4 banditCampfire props, 64 wolfPacks waypoints, den door interactAt). Spec coords KEPT (no adjustment needed).

| Coven row | Overall min | nearest set member | camp guard | CC-C6 row | campfire | wolf row | wolf waypoint | den door |
|---|---|---|---|---|---|---|---|---|
| 1 `(-118.4, -238.2)` | **38.4 m** | sw pack waypoint `-112.5,-276.1` | 67.0 | 67.0 | 78.3 | 52.2 | 38.4 | 57.4 |
| 2 `(-99.2, -249.1)` | **30.1 m** | sw pack waypoint `-112.5,-276.1` | 62.3 | 62.3 | 74.3 | 33.0 | 30.1 | 79.3 |

All mins > 25.0 m → CLEAR as-is (matches Testerbot's reference values 38.4 / 30.1).

## Behavior specifics Testerbot asked to be stated (V5.5, V8.2)

- **Dead-player handling** (V8.2): the enemy-bolt loop runs the bolt's own update (movement/flash) unconditionally;
  the DAMAGE call is not separately gated by an alive check — the damage flows through
  `damagePlayerFromEnemy(reduced, attacker)` → `player.resolveIncomingHit`, whose first line
  (`if (this.state !== 'alive') return false`, player.js:1600, untouched) discards hits on a dead player. A spent
  bolt still dies on its 0.15s hitFlash and can never hit twice (spent flag is set in the bolt on contact,
  independent of the damage route).
- **One-hit guarantee**: WH_CovenBolt.update sets `spent = true` + `hitFlash = 0.15` exactly when the circle test
  first passes; during flash it neither moves nor collides; game.js fires the damage call exactly once (the frame
  spent flips) then keeps the bolt only for the flash.

## Build output (A10 / V11)

- Tool: `python3 tools/build_v8.py` (confirmed newest build_vX; v7 also present)
- Exit code: **0**, no tracebacks
- Bundle: prototype/builds/v8-playable.html — 3,324,761 bytes, written 2026-11-06 (this session)
- Marker: `grep -c coven prototype/builds/v8-playable.html` = **50** (≥ 4 required)
- Build diff note: the committed bundle in HEAD pre-dated 0cd0ba0's current sources (stale inline playerBody
  still read `human-hunter-male.combat-sword.glb` and the spliced CHARACTERS `43` row) — the rebuild inlines the
  CURRENT sources; the only `-` lines in the build diff are that pre-existing staleness plus inline mirrors of the
  three sanctioned row-extensions. No unrelated source drift.

## magicDefense choke (V7)

- Applied EXACTLY ONCE at the game.js enemy-bolt call site:
  `var reducedEB = Math.round(dmgEB * (1 - window.WH_LEVEL.magicDefense()));` then
  `damagePlayerFromEnemy(reducedEB, { isSpell: true, pos: {x,y,z of the bolt} })`.
- player.js is byte-untouched (verify: `git diff -- prototype/js/player.js` EMPTY). resolveIncomingHit keeps
  parry/block/iframes semantics over the ALREADY-REDUCED amount.
- Parry safety: the attacker literal carries only isSpell + pos — no methods, in particular no `enterStagger`, so
  the parry branch (player.js:1619 tester `attacker.enterStagger &&`) can never fire. Verified zero
  `new THREE.PointLight` and zero enterStagger additions in the whole round's diff.
- `WH_LEVEL.magicDefense()`: hook is LIVE (registry sums equipped-hands item stats.magicDefense) but INERT in v1 —
  no item carries stats.magicDefense, so reduced = round(14 × 1) = 14 always (NE-3, intended activation state).

## Discoveries

1. **Append-only law + JS syntax collision**: appending rows after an array whose last pre-existing row has no
   trailing comma normally forces an edit to that row. Fixed with a comma-first continuation line
   (`, { type: 'coven', …`) so the CC-C6 Charlie row stays byte-identical and V3's `^-.*type:` grep stays 0.
2. **The committed bundle was stale** relative to 0cd0ba0's sources (pre-gear-splice playerBody inline). Rebuild
   aligned it; flagged here so Testerbot's build-diff sweep does not misread the 4 `-` lines as regressions.
3. Valspec V3's visual-hunk sweep language ("additions only") is satisfied in spirit and letter for the three
   row-extensions by reading them as single-row appends of a new key — recorded here so the adjudication step
   (§6.12) has the reasoning on record.

## Gate trail

IO spec → Testerbot valspec (C1–C5 binding) → **Devbot build (this note)** → Testerbot independent validation →
IO commit+push. NO-GIT clause honored: never pushed, never touched origin refs or any branch other than the
checked-out feat/world-visuals HEAD. Identity: CaptainPickard <pickard.nicko@gmail.com>.
