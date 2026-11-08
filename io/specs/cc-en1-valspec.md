# CC-EN1 VALSPEC — Wilderness Encounter Tables V1 (Testerbot validation spec)

Written by Testerbot (independent validator), 2026-11-08. Validates the Devbot
build of round CC-EN1 against the IO spec of record
`io/specs/cc-en1-spec.md`. Gate order: this spec → Devbot build → Testerbot
re-runs every check below independently → verdict
`io/reports/cc-en1-verdict.md` → IO commit. NO-GIT holds for every child
(including me): no add/commit/push. Law 2: NO browser smokes — static analysis
+ node harness only.

## 0. Pre-build baselines (PINNED — probed this wake on CONFIG.js sha
`20ec2045b3d77ab4cbb234a66a5d30b845bbe909fb2bad882b7eddd54cef549b`,
game.js `c6e5f74f319c8273bcc5814cb21867769d9e2e9f96cf36fa32f0a9d12a59c1d1`,
region-manager.js `c7e31520f775b2e07388db710d079be35a3810b5ab104e90ab64cd8bfe1bc2ee`,
index.html `cca80541825d139f394ad29d37a1b8cfdf544fec9e68871ac4d5ef0d539e46ec`,
HEAD `45c0299`, branch feat/world-visuals)

These numbers were captured live via `node scratch/cc-en1-probe/probe_config_baseline.js`
(three.classic.js + CONFIG.js + wh-ground.js loaded in node, no browser). The
post-build census re-runs the SAME probe with arg `post` and the deltas must be
exactly as stated. Pre-build state: `WH_ENCOUNTERS` undefined, `CFG.encounters`
absent, `WH_AMBUSH` defined-when-ambush.js-loads (`typeof window.WH_AMBUSH ===
'object'` after loading ambush.js in the harness — in the bundle it loads after
enemy.js, tag 29 of 33).

| pinned quantity | value (pre-build) | post-build must be |
|---|---|---|
| CONFIG.world.groundRadius | 90 | 90 (untouched) |
| CONFIG.world.playerMargin | 1.5 | 1.5 (untouched) |
| playableR for regionB | 90 - 1.5 = **88.5** | 88.5 (p5/p6 use it) |
| CONFIG.boundary.z | -25 | -25 (untouched) |
| CONFIG.scatter.clear.nodeM | 2.5 | 2.5 (nodeM probe echoes this) |
| CONFIG.scatter.clear.enemyM | 4 | 4 (roster clearance echoes 5 from director separately) |
| CONFIG.scatter.keepOut regionB row | `{ x: 0, z: -58, rx: 21, rz: 12.5 }` (darkwood_edge) | unchanged (p1 predicate uses it) |
| CONFIG.regionB.props.length | 76 | 76 (byte-sacred) |
| CONFIG.regionB.nodes.length | 9 (5 graveMoss + 4 bonePile) | 9 (byte-sacred) |
| CONFIG.regionB.enemies.length | 3 (ghoul,ghoul,bandit) | 3 (byte-sacred) |
| regionB banditCampfire rows | 1, at (2.5, -52) | 1 (g5/p3 anchor) |
| regionB spawn row | (0, -45) — B-side of plane -25 | unchanged |
| live-kit types | bandit ✓ ghoul ✓ wolf ✓ coven ✓ (rotspawn also exists; encounters use ONLY the four) | same |
| doc 51 §2.1 families on darkwood_edge night | none (no CONFIG.encounters) | 1,2,3,5,8 |
| CFG.raid block | 22 keys, debugForce=false, debugMute=false | unchanged |

Byte-sacred rows (A2): regionB props/nodes/enemies, regionC props/enemies,
CONFIG.enemy stat rows, CONFIG.roads, CONFIG.raid — the post-build diff of
`git show HEAD:<file>` against HEAD pins must be EMPTY for every line not
inside the new `encounters:` block (CONFIG.js may ONLY gain that block).

## 1. Checks (map onto A1..A10; "re-run" columns state Testerbot's independent
post-build procedure — every check re-executable without Devbot's help)

### V-1 (A1) — Syntax law: node --check passes on all touched files
- **HOW**: run, from the worktree root, in ONE shell block:
  `node --check prototype/js/CONFIG.js && node --check prototype/js/encounters.js && node --check prototype/js/game.js`
  Expected total: zero non-zero exits. `encounters.js` must exist (A2 proves it
  does, this proves it parses).
- **RE-RUN (Testerbot)**: same three `node --check` invocations, no tooling
  beyond node ≥ 18 (the box runs node v22.22.3, verified this wake).
- **PASS**: every `node --check` exits 0 and prints nothing.

### V-2 (A2) — Engine edit surface: 2 game.js hook lines + 1 index.html tag + 0 other engine files
- **HOW**:
  `git diff HEAD -- prototype/js/game.js` yields EXACTLY two added `window.WH_ENCOUNTERS` lines (init-site hook + tick-site hook) and nothing else (no deletions beyond context moves), verifiable by:
  `git diff HEAD -- prototype/js/game.js | grep -c '^+.*WH_ENCOUNTERS' # == 2`
  `git diff HEAD -- prototype/index.html | grep -c '^+.*encounters.js'  # == 1`
  `git diff HEAD --stat -- prototype/js/ | grep -v encounters.js | grep -v CONFIG.js | grep -v game.js | grep -v region-manager.js | wc -l # == 0`
  The ONLY files whose diff may be non-empty: CONFIG.js (the `encounters:` block), encounters.js (new file), game.js (the 2 hook lines), index.html (the 1 tag). region-manager.js diff vs HEAD must be EMPTY (its guard was landed by AE1 at HEAD and must not move):
  `diff <(git show HEAD:prototype/js/region-manager.js) prototype/js/region-manager.js  # empty`
- **RE-RUN (Testerbot)**: same three `git diff`/`diff` invocations post-build,
  from the worktree root, no other tools.
- **PASS**: counts exactly 2 / 1 / 0; region-manager diff empty.

### V-3 (A3) — Table completeness: fam 1,2,3,5,8 night + fam-3 day + F4/F6/F7 pending + regionC live-F4
- **HOW**: run the census probe:
  `node scratch/cc-en1-probe/probe_config_baseline.js post`
  It asserts (and this spec re-asserts as the pass law):
  - `CFG.encounters.biomes.darkwood_edge.night` carries family numbers
    sorted == `[1, 2, 3, 5, 8]` (exactly 5 rows; family 4 is NOT in regionB's
    night array — doc 51 §2.1 F4 is a *pending note* for regionB, not a row).
  - `CFG.encounters.biomes.darkwood_edge.day` carries exactly ONE row,
    family 3 (WAYFINDING day pair = bandit x2).
  - `.pending` object keys pin the pending-rows story at the FAMILY-NAME level:
    the spec's §1 literal pins TWO keys (`F1-lair-pair` on regionC,
    `F2-tainted-glade-wailcaster` on regionB); ≥ 1 pending key must exist on
    each biome that maps §2.1 rows this round cannot compose, AND the pending
    VALUES (not just keys) must carry the §2.1 family story: grep pending note
    text for `F4` (road life, live via cc-ae1 on regionC / deferred-note on
    regionB), `F6` (riches), `F7` (one-off wanderers), case-insensitive. Each
    pending note must name the doc-51 source (e.g. `doc 51 1.4`) so the note is
    auditable back to §2.1. (Defect §2.4: A3's "F4/F6/F7 pending notes" and
    §1's two-key literal cannot both be literal; the valspec pins note-TEXT
    coverage — if IO intends three literal `F4/F6/F7` keys, that is a declared
    deviation, not a silent FAIL.)
  - Every comp entry `(type, n)` in every darkwood night+day row: type ∈
    `{bandit, ghoul, wolf, coven}` (the live kit — verified this wake: all
    four exist under `CFG.enemy`), 1 <= n <= 3 (doc 34 pack grammar band).
  - `CFG.encounters.biomes.forest_of_the_old_king.night` carries exactly one
    row: family 4 (night roads, LIVE via cc-ae1), `live: 'cc-ae1'`, comp
    [bandit x2, wolf x1] — and NO day array (AE1 is night-only; if a day
    array crept in, that's a scope violation to flag).
- **doc 51 mapping (pinning the §2.1 read this valspec is enforcing)**:
  fam 1 = dens/lairs (night wolf pack — here the regionB graveyard-edge lair
  stand-in), fam 2 = hidden holy/tainted (bound thralls on the bandit
  chassis, pending Wail-Caster kit), fam 3 = wayfinding, fam 5 = ruins/grave
  ghouls, fam 8 = war scars (bandit looters); F4/F6/F7 = pending notes
  (§2.1 F4's smuggler column can't exist: no smuggler chassis; F6's claim
  jumpers and F7's hand-authored wanders similarly deferred). regionC's F4
  row is the LIVE AE1 data-record (not a second director — the note text
  says so; `grep -c "no second director"` in the biome note ≥ 1).
- **RE-RUN (Testerbot)**: the probe once more + the greps
  `grep -c "family: 1" prototype/js/CONFIG.js` (must count BOTH regionB's
  night row 1 AND other CONFIG family rows that pre-date this round —
  baseline 2 pre-build, post-build ≥ 2), and a direct
  `node -e` read of `CFG.encounters.biomes.*` printing family arrays for
  manual confirmation. Two independent readers, one number set.
- **PASS**: census probe exits 0 with every `chk(...)` line `PASS`; family
  arrays == the pins above; the regionC note mentions cc-ae1 and
  "no second director".

### V-4 (A4) — Weight law: len == night.length+1, sum 1.0 (±1e-9), weights[0] === 0
- **HOW**: `node scratch/cc-en1-probe/probe_weight_law.js`
  (instrument written pre-build: reads CFG.encounters once landed; asserts
  structural law + prints the values; if IO/Nicko amended the pinned values
  [0, 0.28, 0.12, 0.15, 0.25, 0.2] the probe does NOT fail the structural
  law but PRINTS the drift — that print, not a silent pass, must appear in
  the verdict). Spec's literal weights are the round's PROPOSED defaults
  (sum exactly 1.0 with `weights[0] === 0` as the 1-based-family spare slot).
  Float law: sum uses reduce over Numbers (0.28+0.12+0.15+0.25+0.2 == 1.0
  within 1e-9 in IEEE — verified by running the same expression in node
  this wake: printed `1`).
- **RE-RUN (Testerbot)**: the probe, plus an independent one-liner:
  `node -e "const c=require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');..."`
  re-summing `CFG.encounters.biomes.darkwood_edge.weights` manually (two
  readers, one number).
- **PASS**: probe prints `WEIGHT-LAW PASS`; any value drift from the
  spec pin is listed in the verdict's deviations section with the values —
  drift alone is not a FAIL unless sum / len / w0 law broke.

### V-5 (A5) — Gate/predicate presence: g1..g8 + p1..p9 anchors in encounters.js
- **HOW**: this is BOTH a grep pass AND the behavioral matrix:
  - grep: `for g in g1 g2 g3 g4 g5 g6 g7 g8; do grep -c "g$g" prototype/js/encounters.js; done`
    each ≥ 1 (the gate comment anchors, per A5's own wording).
    Same loop for p1..p9.
  - BEHAVIORAL matrix (the real teeth): `node scratch/cc-en1-probe/probe_gates_matrix.js`
    The probe (written pre-build, POST-build runnable) loads encounters.js in
    node with the AE1 harness pattern (window shim + three.classic.js +
    CONFIG.js + wh-ground.js; mock game with controllable
    `dayNight.{dormant,phase}`, `player.{state,pos,yaw}`,
    `regionManager.{logic.activeId, scene, enemies[darkwood_edge]}`,
    `inventoryUI.toast` recorder, and a stub `window.WH_Enemy` whose
    `makeBody` is a no-op). It then asserts:
    - happy path: with `CFG.encounters.director.debugForce = true` and a
      player seated far from fire (40,-45) / away from all pinned
      exclusion shapes, the FSM reaches `warn` within checkSec cadence
      (60 ticks at dt 1.0) and the amber toast recorded FIRST
      (`toasts.length >= 1` while mode === 'warn', which proves warn-order
      precedes any WH_Enemy construction).
    - g1 alone blocks: `dormant: true` ⇒ zero state movement across 30 ticks.
    - g2 alone: `phase: 'day'` ⇒ same.
    - g3 alone: `player.state: 'dead'` ⇒ same.
    - g4 alone: `activeId: 'forest_of_the_old_king'` ⇒ same (no cross-region leak).
    - g5 alone: player ON the banditCampfire (2.5, -52) ⇒ same.
    - g6/g7 block via state machine laws the probe drives post-warn
      (cooldown after a live raid ends, party cap after 2 same-night
      parties); the probe asserts at least g6's cooldown gate fires on the
      SECOND reserve attempt within the same night.
    - g8/p1..p9: the seat predicates are exercised by construction — the
      happy-path spawn must have been placed by a seat that satisfies every
      predicate (p1 chapel keepOut ellipse, p2 props ≥ 3 m from all 76 rows
      with .x, p3 fire ≥ 50 m, p4 player ≥ 14 m, p5 slope ≤ 0.45 when
      WH_GROUND has the region — it does NOT for regionB in the node
      harness: `WG.has('darkwood_edge') === false` pre-build, so p5's
      else-pass branch runs — p6 |z-(-25)| ≥ 6, p7 nodes ≥ 2.5 from all 9,
      p8 roster ≥ 5 m from all 3 rows, p9 heightAt read is visual only).
      The probe asserts the spawned positions obey p2/p3/p4/p6/p7/p8
      against the PINNED baseline rows (re-derived inline, not trusted).
      (Pinned keepOut row to test against: `{regionId:'darkwood_edge',
      x:0, z:-58, rx:21, rz:12.5}` — probe re-reads it from CONFIG at
      runtime, not from this table, and the §0 row is the cross-check.)
      g8's own block-alone leg (no seat in 24 attempts) is NOT forced in the
      matrix (seeding a fully-hostile disc would need 76+9+3 hostile rows
      around the whole 88.5 r disc); it is instead pinned by p-law
      arithmetic: with debugForce + predicates unchanged, 200 seat
      opportunities MUST succeed (as the happy-path leg does), proving no
      predicate is unsatisfiable — a hard-unmet p-law would itself be the
      V-5 FAIL.
- **RE-RUN (Testerbot)**: the matrix probe once more from a clean node
  process + one fresh `grep -c` loop (both re-run, not trusted from Devbot).
- **PASS**: probe prints `GATE-MATRIX PASS` (g1..g8 block-alone, warn-order,
  comp match, transient flag, CONFIG purity); the grep loop shows g1..g8 and
  p1..p9 anchors all ≥ 1.

### V-6 (A6) — Transient law: raidMember flagged at spawn; region-manager dead-state guard untouched & effective
- **HOW**: `node scratch/cc-en1-probe/probe_transient_law.js` (instrument
  written and RAN pre-build: engine half asserts NOW, module half asserts
  post-build). It (a) asserts the landed guard line still exists verbatim:
  `grep -n "raidMember" prototype/js/region-manager.js` → line 2468:
  `if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead';`
  (verified line 2468 this wake; ±2 lines accepted — content, not position,
  is the law; probe greps the string, not the line number) with its CC-AE1
  comment; (b) runs the loop's verbatim semantics against
  mock raiders (raidMember flag ON): exactly **0** rows record into
  regionStates; against a stock row (no flag): exactly **1** records (the
  base case the guard must NOT break); (c) asserts
  `encounters.js` assigns `raidMember = true` at spawn (regex). Pre-build
  state verified this wake: probe exits 0 with `TRANSIENT-LAW PASS (engine
  guard landed; module half awaits build)` — this is the A6 half that
  exists before Devbot touches anything.
- **RE-RUN (Testerbot)**: the probe again post-build (both halves live), plus
  the direct grep for the guard line and comment.
- **PASS**: probe prints `TRANSIENT-LAW PASS` with BOTH halves (module
  assigns flag; engine guard landed and behaviorally proven); grep shows the
  region-manager line unchanged (sha pinned in §0). region-manager.js diff
  vs HEAD must remain EMPTY (this overlaps V-2's last clause — same law,
  stated once more for the check A6 names).

### V-7 (A7) — Art law: no new materials/meshes/lights in encounters.js; ONE toast accent
- **HOW**: grep the NEW file only (encounters.js):
  `grep -c "new THREE.PointLight\|MeshStandardMaterial\|new THREE.BoxGeometry\|new THREE.PlaneGeometry\|new THREE.CylinderGeometry\|new THREE.SphereGeometry\|new THREE.BufferGeometry" prototype/js/encounters.js`
  must print **0**. (Body/limb geometry comes from `WH_Enemy.makeBody`, which
  encounters.js calls read-only — same law AE1's ambush.js held: its only
  THREE-ish construction is zero — verified this wake on ambush.js: zero
  `new THREE` lines.)
  Exactly ONE toast accent call: `grep -c "inventoryUI.toast\|\.toast(" prototype/js/encounters.js`
  fires at least once, and every firing funnels through ONE helper —
  `grep -c "function toast" prototype/js/encounters.js` == 1 and
  `grep -c "debugMute" prototype/js/encounters.js` == ≥ 1 (the mute knob is
  the accent's off switch; AE1's toast helper is the pattern to mirror:
  ambush.js lines 343-347, `function toast(text, seconds)
  { if (R.debugMute) return; … S.game.inventoryUI.toast(text, seconds) }`).
  SITE cap: `grep -c "toast(" prototype/js/encounters.js` ≤ 3 (the helper
  definition + the warn-site call + at most one end-of-raid call); a second
  NON-funnelled site or > 3 total is a DEVIATION under §2.2, not a silent
  pass.
- **RE-RUN (Testerbot)**: the same three greps, plus a second pass grep on
  the BUILT bundle `prototype/builds/v8-playable.html` for
  `PointLight` count staying == the pre-build baseline (count this wake in
  the bundle: **62** occurrences of the string `PointLight`, all in existing
  light/socket/hazard code + comments — the post-build count must be EXACTLY
  the same 62, since EN1 adds no lights) and
  `WH_ENCOUNTERS` == ≥ 4 (init + tick + state + pickSeat).
- **PASS**: 0 material/light/geometry-constructor hits in encounters.js;
  exactly one toast helper function + debugMute respected; bundle greps show
  no new light/material constructions (PointLight string-count == 62
  pre-build pin; an increase means a light was added).

### V-8 (A8) — RNG law: Math.random confined to pickSeat + roll bodies
- **HOW**: `grep -n "Math.random" prototype/js/encounters.js` — every hit must
  sit INSIDE the `pickSeat` function body or the roll step of `tick`'s
  `checkSec` branch (AE1's exact law — its module has 4 Math.random: seat
  yaw jitter, side, band magnitude, and tick's trigger roll; encounters.js's
  surface has one more lawful need: the spawn `spacingJitter` bearing per
  §2's "alternating ± offsets along a random bearing" — so the LAW is: all
  Math.random sites lie inside ONLY { pickSeat, spawnMemberSpacing (inside
  spawnParty), tick-roll } functions; never at module top-level, never in
  init/state, never inside predicate walkers p1..p9 (predicates must be
  DETERMINISTIC given (x,z) — seat rejection must not depend on RNG).
  Hard cap: ≤ 4 distinct `Math.random` call SITES (grep-able line count;
  the probe counts occurrences of the string in the file, and the census
  probe asserts ≤ 4).
- **RE-RUN (Testerbot)**: grep, read the enclosing function for each hit
  (one `sed -n` per hit line), and re-run the census probe's `chk` on the
  count. Independent second reader: `awk '/Math.random/ {print NR": "$0}'
  prototype/js/encounters.js` and manually confirm each line's enclosing
  function.
- **PASS**: all Math.random sites inside pickSeat/spawnParty-spacing/tick-roll
  only; total sites ≤ 4; zero RNG in predicates or module top-level.

### V-9 (A9) — Build law: v8 inline bundle carries CC-EN1 + encounters.js; two-run SHA determinism
- **HOW**:
  1. `python3 tools/build_v8.py` from the worktree root (rc 0; writes
     `prototype/builds/v8-playable.html`).
  2. `grep -c "CC-EN1" prototype/builds/v8-playable.html` ≥ 1 (the marker
     rides the CONFIG block) and `grep -c "window.WH_ENCOUNTERS" prototype/builds/v8-playable.html` ≥ 1 (IIFE surface) — build_v8 inlines
     whole files between script tags, so the module body IS in the bundle.
  3. Determinism: `python3 tools/build_v8.py` again, then
     `sha256sum prototype/builds/v8-playable.html` — two runs of the SAME
     worktree state must be byte-identical (the build stamps from HEAD's
     author-time, law pinned in build_v8.py: `DETERMINISTIC-BUILD LAW
     2026-11-06`). Pre-build reference: this wake's two clean runs on the
     UNMODIFIED engine files produced the SAME sha
     `a18ac604a49541f01d3ff6b3e34547fc33232d635885505b763e80b3a4392bc3`
     twice (`run1 == run2 == a18ac604a49541f0…`). NOTE: that sha is the
     STALE pre-EN1 build whose only diff vs HEAD's committed bundle is the
     title stamp line (HEAD commit `45c0299` carries
     `c32c0f18ca89caf9c1b9c6b3fef6b2514bcb7c7b6c3ad859c9606f9b08380f01`;
     the worktree build stamp reflects HEAD `45c0299`'s author time — this
     is EXPECTED and is not a determinism failure; the determinism law
     compares the two POST-build runs against EACH OTHER, not against HEAD's
     committed artifact).
- **RE-RUN (Testerbot)**: run build twice from a clean worktree state (no
  git ops), sha both, compare; run both greps.
- **PASS**: rc 0 both runs; identical sha256 across the two post-build runs;
  marker + module greps ≥ 1 each; `node --check` NOT required on the bundle
  (it is an HTML file, A1 does not name it).

### V-10 (A10 + close-out) — Serving law: build artifact is committed BEFORE any playable claim (IO's half; Testerbot verifies state)
- **WHAT**: A10's law lives on IO's commit step, not Devbot's. Testerbot's
  post-build duty: verify the worktree is in the expected pre-commit state —
  exactly these modified/untracked paths exist and NOTHING is staged:
  `git status --short` shows `M prototype/js/CONFIG.js`, `?? prototype/js/encounters.js`,
  `M prototype/js/game.js`, `M prototype/index.html`, `M prototype/builds/v8-playable.html`,
  `?? io/specs/cc-en1-*`, `?? scratch/cc-en1-probe/`, `?? io/reports/cc-en1-verdict.md`
  (verdict file written LAST, after this list is checked — the verdict's own
  write must not precede the check that the round's code surface is exactly
  the spec's file list; if anything else is M/??, it's a defect to name).
- **HOW**: `git status --short` + `git diff --stat HEAD` and compare with the
  spec's file list; the committed-vs-worktree check for A10 itself is IO's
  gate (Testerbot can only assert the pre-commit shape + that the LAST
  commit reachable without staging contains the round once IO commits).
- **RE-RUN (Testerbot)**: `git status --short` + `git diff --stat HEAD` and
  manual comparison against the pinned surface (V-2's file list).
- **PASS**: the worktree's M/?? set == the spec's surface set (± the
  valspec/verdict/scratch files, which are Testerbot's own); nothing staged;
  any EXTRA modified file not in the spec's surface = FAIL with the path
  named in the verdict (NO-GIT means Testerbot does not clean it, only
  names it).

### V-11 — region-manager dead-state guard byte-stability (A6's engine half + V-2 overlap, split for a clean per-check verdict line)
- **HOW**: `diff <(git show HEAD:prototype/js/region-manager.js) prototype/js/region-manager.js`
  must be EMPTY; `sha256sum prototype/js/region-manager.js` must equal the
  §0 pin `c7e31520f775b2e07388db710d079be35a3810b5ab104e90ab64cd8bfe1bc2ee`.
- **RE-RUN (Testerbot)**: same diff + sha.
- **PASS**: diff empty AND sha matches the §0 pin.

## 2. Spec defects caught during pre-build probing (declared to IO; these are
IO's to adjudicate — Devbot still builds to spec unless IO amends)

1. **A5's gate-comment wording is loose about the roll vs the seat RNG**: A5
   says "greps per gate comment g1..g8 / p1..p9" as if comments carry the
   proof; the REAL assertions needed are behavioral (V-5's matrix). The
   valspec keeps the grep but subordinates it to the matrix.
2. **A7's "exactly one toast accent call" is ambiguous about helper-vs-site
   count**: AE1's pattern is one helper function (`function toast(...)`)
   plus one call site inside tick's warn branch. The valspec pins "one
   helper + all sites funnel through it" so a defensive second call site
   (e.g. an abort toast) would be a DEVIATION to declare, not a silent
   structural miss.
3. **A8's "2 call sites max" contradicts the spec's own §2 seat/roll/spawn
   text**: §2 says pickSeat uses Math.random (angle) + a per-member random
   spacing bearing + tick's roll, i.e. 3 function bodies. The valspec
   interprets A8 as "call SITES inside exactly the {pickSeat,
   spawnParty-spacing, tick-roll} bodies, ≤ 4 sites total" and treats a
   literal 2-site reading as an IO adjudication item (if Nicko wants the
   spacing jitter deterministic, the CONFIG key spawnSpacingM would need a
   law note).
4. **A3's wording "darkwood_edge … + F4/F6/F7 pending notes" is
   mechanically ambiguous**: §1's pinned `pending` object has ONE key
   (`F2-tainted-glade-wailcaster`). A3's F4/F6/F7 phrasing (the spec is the
   doc-51 mapping, not the CONFIG literal). The valspec enforces the §2.1
   F4/F6/F7 story via the pending NOTES grep (≥ 1 pending key + note text
   mentioning F4/F6/F7) rather than three literal keys — Devbot is told
   (by this valspec, not the IO spec) that pending note TEXT must carry the
   F4/F6/F7 family names so the doc-51 rows stay visible. If IO intends
   three literal `pending` keys F4/F6/F7, the verdict will name the
   divergence and IO adjudicates.
5. **§2 SPAWN's `x + i*spacingJitter, z + j` is malformed pseudo-code** (the
   `+ j` has no definition; `j` never bound). The valspec does not enforce
   the literal text — it enforces the LAW the text is reaching for: members
   of one party offset from each OTHER (p2/p8 clearances still hold at the
   worst 5-member case), and the spawn positions stay inside the pinned
   clearances. Devbot implementing the text literally would fail V-5's
   predicate assertions on multi-member spawn; that is the DESIRED
   outcome (the text law is the seat-clearance law).
6. **§2 p6's self-correcting text ("for A-side... B occupies...")
   contradicts itself mid-line** and lands on the right law (|z - (-25)| ≥
   boundaryBandM, B side z < -25) but the wording "for A-side" before the
   correction is a spec-text defect; the valspec enforces ONLY the final
   form (the plane predicate, band ≥ 6 off the plane).
7. **A9's "two runs sha-equal" needs the §0-vs-HEAD build-sha caveat** to be
   usable (a naive reading — post-build sha == HEAD's committed bundle sha —
   would FAIL for the title-stamp reason documented in V-9's HOW). The valspec
   pins the comparison as post-build-run-A vs post-build-run-B.
8. **§3 "game.js hooks (3 one-line edits …)" miscounts**: the section lists
   TWO game.js lines (init-site hook + tick-site hook) — the third edit in its
   list is the index.html tag, which is a different FILE and already counted
   separately ("index.html: ONE script tag"). A2 pins exactly 2 game.js lines
   + 1 index.html tag; this valspec enforces A2's count and treats §3's stray
   "3" as scoped-to-game.js arithmetic slop, not a third hook law.
9. **§1 director comments cite CONFIG paths that do not exist as named**:
   `nodeM: 2.5, // gather-node clearance (scatter.nodeM)` — the live path is
   `CONFIG.scatter.clear.nodeM` (CONFIG.js line 2650, value 2.5 ✓); and
   `enemyRowM: 5, // … (gather.placement.enemyM)` — there is no `gather:`
   parent block holding an `enemyM`; the 5 lives in the nodes-placement block
   `placement.enemyM` (CONFIG.js line 4945, value 5 ✓). Values match the live
   CONFIG; names drift. The valspec pins LIVE paths + values (§0 table); the
   comments-as-written are not enforced.

## 3. Report format — `io/reports/cc-en1-verdict.md`

The verdict file MUST contain, exactly:

1. Header: `# CC-EN1 Testerbot VERDICT` + one line stating worktree, branch
   (`feat/world-visuals`), HEAD sha at build time, valspec path, IO spec path.
2. Result line: `## Result: PASS — 0 blocking` or `## Result: FAIL — N
   blocking` (or `BLOCKED` per-check, e.g. a check whose instrument could
   not run because a REQUIRED pre-state was violated).
3. Per-check table: one row per check V-1..V-n (n = 11 here), columns
   `check | verdict | evidence`. Verdict ∈ {PASS, FAIL, BLOCKED}. Evidence
   = an ACTUAL observed output line (a grep count, a sha, a probe print), NOT
   a description — e.g. `V-4 | PASS | sum 1.0 w0 0 len 6 tail maps rows`,
   `V-2 | PASS | diff --stat: 4 files + encounters.js new`, `V-9 | PASS |
   sha A == sha B == <16-char prefix>`.
4. A `BLOCKED` row MUST state the missing pre-state (e.g. "encounters.js
   absent — build did not land" or "node harness require failed: …").
5. Defects/deviations section: `## Deviations` listing EVERY check whose
   observed behavior differs from the valspec's pinned expectation but does
   not block (e.g. weight-value drift with the new values printed; an extra
   toast site pending IO adjudication per §2-item-2; an F4/F6/F7 pending-key
   shape different from §2-item-4's interpretation). Each deviation names
   the valspec defect number (§2.1..§2.9) it falls under or `ad hoc`.
6. Pinned post-build numbers section: the sha256 of the two post-build
   bundle runs, the census probe's printed lines verbatim, and the final
   `git status --short` snapshot (V-10's evidence).
7. NO-GIT reminder footer: "Testerbot wrote io/reports/cc-en1-verdict.md
   only; no git operations performed."

## 4. Instrument inventory (all Testerbot-written, all PRE-BUILD)

- `scratch/cc-en1-probe/probe_config_baseline.js` — §0 baselines + post-build
  census (V-3, V-4 second reader, V-8 count). RAN this wake (pre-build leg
  exits 0 asserting WH_ENCOUNTERS/CFG.encounters absent).
- `scratch/cc-en1-probe/probe_gates_matrix.js` — V-5's behavioral matrix +
  seat-law spawn assertions + CONFIG purity + warn-order. POST-build runnable
  (requires encounters.js to exist).
- `scratch/cc-en1-probe/probe_weight_law.js` — V-4 (structural + drift note).
  Pre-build exits 1 with FAIL (encounters absent) — correct; POST-build
  exits 0 on law pass.
- `scratch/cc-en1-probe/probe_transient_law.js` — V-6 (guard line verbatim +
  loop-shape behavior). RAN this wake: exits 0 pre-build.

## 5. Line-count law: this spec stays under 500 lines (self-check:
`wc -l io/specs/cc-en1-valspec.md` < 500; current: 433).

## 6. IO instrument repair (2026-11-08 wake 47, post-build)

Pre-Devbot instruments encoded pre-amendment law; three minimal repairs by IO
(wake-43 precedent), Devbot code untouched, Testerbot re-runs all four fresh:
- probe_config_baseline.js: regionC pending check `== 1 && startsWith F1` ->
  `>= 1 && join includes F1` (EN1-4 added F6/F7 keys AFTER these probes were
  written 10:55; the valspec's own V-3 normative law is >= 1 + family-story).
- probe_gates_matrix.js: happy-path player (40,-45) -> (55,-70) — the old seat
  sat 38.15 m from the campfire, inside the 50 m g5 exclusion V-5 itself pins
  ("p3 fire >= 50 m"); (55,-70) is 67.6 m off.
- probe_gates_matrix.js compOk: per-comp-entry equality -> per-TYPE sums
  (doc 51 rows split one type across entries: fam 1 wolf 2+1, fam 8 bandit 2+1;
  debugForce deterministic pick = last row = fam 8).
- probe_gates_matrix.js (#4, post-verdict flake): happy + E6 legs budgeted
  60/200 ticks = ~3/~10 reserve attempts, but Testerbot measured the probe
  flaking ~70% (debugForce happy leg) — root cause: pickSeat ok-rate in this
  harness is 5-15%/attempt (IO one-off io_seatrate.js: 1-9 of 60 over 6 runs;
  50 m fire disc + 76 prop rows = tight lawful seat space, per design). The
  valspec's own V-5 p-law paragraph pins "200 seat opportunities MUST
  succeed" -> both legs now 4400 ticks = 220 attempts; label updated.
