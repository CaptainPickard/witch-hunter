# CC-AE1 — NIGHT RAIDS · TESTERBOT VALSPEC (node-only)

Round: CC-AE1 · Worktree: /tmp/wh-worldfeat · branch feat/world-visuals · HEAD ba813ac
Author: Testerbot · IO spec: io/specs/cc-ae1-night-raids-spec.md (sections cited per case)
Valspec version: 1.0

## 0. LAWS THAT BIND THE VALIDATOR

- **NO-GIT**: Testerbot never runs any git command in round CC-AE1.
- **Node only**: no browser, no headless smoke tests, no harness runs, no
  playtest claims (IO spec "Validation guidance to Testerbot"; A-3).
- **Harness pattern proven on this box** (scratch/cc-c5/loops_probe.js,
  scratch/cc-ae1/node_probe.js): `globalThis.window = globalThis; globalThis.self = globalThis;`
  then require, in order:
  1. `prototype/vendor/three.classic.js`
  2. `prototype/js/CONFIG.js`
  3. `prototype/js/wh-ground.js`
  4. `prototype/js/ambush.js` *(may be required before CONFIG's `raid:` block exists
     only if it guards; the spec contract is that ambush.js reads only
     `window.WH_CONFIG` at load — after the round lands, `WH_CONFIG.raid` MUST
     exist at load time; V-A01 asserts it does)*
  5. `prototype/js/region-manager.js` *(needed only for V-A25, which drives the
     REAL `WH_RegionManager.RegionManager.prototype.updateEnemies` dead-record loop
     against a stubbed enemy list; all other cases use a mock region manager)*
- **Deep-freeze before ticks**: every case that calls `tick()`/`pickRaidSeat()`
  deep-freezes `window.WH_CONFIG` first (case V-A30 pattern). Any mutation fails.
- **Mock objects, record-only stub**: drive `WH_AMBUSH` with a mock `game`
  (fake dayNight {dormant, phase}, player {pos, yaw, state}, regionManager
  {logic.activeId, enemies[raid.regionId], scene}, inventoryUI {toast recorder}).
  Stub `window.WH_Enemy` as a record-only construct (no Enemy physics — the
  stock FSM is landed code). Restore the real object after each case if loaded.
- **Seeded determinism**: seat law cases seed Math.random per case
  (`require('../..')`-free; use a simple mulberry32 injected onto
  Math.random, restored in finally). pickRaidSeat may only call Math.random
  INSIDE its own body (contract, IO spec §Files-2).
- **Art law line for prompt text** (IO spec "Devbot guidance"): pixelated
  everything, darkwood palette, one accent per frame — applied to warn-cue
  copy checks (V-A14): the warn toast is the round's accent; validator
  enforces no new materials/models/light-sources by confirming no art-file
  edits in the byte-sacred check V-A23 only (node cannot verify rendering).

## 1. BASELINES PINNED THIS WAKE (Testerbot evidence, NO-GIT re-derive allowed)

SHA-256 of JSON.stringify over live CONFIG objects (deep-freeze target), taken
pre-landing (`raid:` absent, verified `WH_CONFIG.raid === undefined`):

```
CONFIG.roads                      bcddc7d587d9e981c4cb5d8118db56fc7ba2ceec22580e622b55fd67c7f700d8
CONFIG.enemy.wolfPacks            057397ad1d78170d177036414f50891507ebaf02e2fa3ae2adc1c471791c3947
CONFIG.regionA.enemies            b5669f0ec712b17d0b89a35e462ade4eca19bdeab264d5e7a5ebdd07ae7cf45e
CONFIG.regionA.props              8518111a8fe6608476ce060052f165dcba85895084ed8e324f66f6e707317578
CONFIG.regionB.enemies            98fe6d963156468e3b7d0a1ba4c4ecf9935da362fb6fb41d8b64b599ef3c3ebe
CONFIG.regionB.props              64f2682af5b1041fdbe9c7b2f50f51aa42b0edc10ec927a4e12402b913dfb11a
CONFIG.regionC.enemies            cec5daf9d7e4d2b8a8b09c2be92254239eae1d2c75ca715cd61eac368eec8b49
CONFIG.regionC.props              7c8a5e469b0aef677cce40b6711e53c4c369c1cda2525d977aef08d592b77155
CONFIG.regionD.enemies            4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945
CONFIG.regionD.props              ab5ae3f271f1919761dd6070632aecb64989e54103b53655cd86deae9615c329
CONFIG.regionE.enemies            708a03a773b074547d0d70e74509d1fee6544b4f0f46c90e68b71fa69009fc2a
CONFIG.regionE.props              af14b557747d0e9b0608906927d564f43d36a6960a22deddd8068b77a74eaebf
CONFIG.enemy stat rows {bandit,ghoul,wolf,coven,rotmother,rotspawn}
                                  aa43438614187fa84b6e1f748a9ee97c801bec3e28abbc274263e6f5e019d897
```

Raw-byte SHA-256 of files that must be UNTOUCHED (IO spec §Files-5):

```
prototype/js/save.js              823fad17167c3bff2a5663bd3ba510867cdeb2bfe3a0682352492f1609574e11
prototype/js/enemy.js             1ba01dad279132f7692b9d69226fecdaa4c96b91b52ab46de132e4baeb707004
prototype/js/daynight.js          e59b5d2166d6ec5412ce2acacf54adbf24d952f064dcefb3cbe022280541ddb7
prototype/js/wh-ground.js         f9775cb00f03ae36d5cd15c870de02b73f2ce46bcb34467fa230d4b0500aacb5
```

Config facts verified this wake (drive fixtures for seat cases):

- Roads WITH points in forest_of_the_old_king: kingsRoad, stoneApproach,
  northRoad, eastRoad, westRoad, northNotch, eastNotch, westNotch.
  Seat-eligible rows ONLY: kingsRoad, northRoad, eastRoad, westRoad (IO
  spec §Files-2); stone + notch rows EXCLUDED for seats.
- Branch roads for notch-mouth arcs: northNotch, eastNotch, westNotch.
  Branch terminal points in their notch arcs: north (0,-596), east (240,-366),
  west (-240,-366) (IO spec §Files-1 CONFIG.raid comment); kingsRoad exempt.
- banditCampfire rows in regionC.props (x,z): (-60,-186) (95,-236) (-140,-506)
  (-106.1,-472.1) (118,-448.6) (-207.8,-246) (144.2,-536.9) — 7 rows.
- Stone ring anchor: (0, -366) (IO spec §Files-1 stoneRingExclusionR comment).
- daynight: `WH_DAYNIGHT.DayNight` boots `dormant=true`, `phase = D.startPhase`
  = CFG.dayNight.startPhase = 'night', clock frozen (daynight.js lines 12, 17,
  125-134; CONFIG.js line 3205). Dawn = phase leaves 'night'.
- A-1 probe lock-law results reproduced this wake by rerunning
  scratch/cc-ae1/node_probe.js: kingsRoad 90.2% maxRun 8 / northRoad 93.5% 6 /
  eastRoad 95.4% 1 / westRoad 96.3% 6 — all PASS (IO spec §A-1).

## 2. CONFIG BLOCK VALUES UNDER TEST (from IO spec §Files-1; all PROPOSED, Nicko tunes)

```
raid: {
  regionId: 'forest_of_the_old_king',
  warnSec: 2.0,
  warnLine: 'Something stalks the road behind you.',
  party: { banditCount: 2, wolfCount: 1 },
  spawnBandM: [14, 17.5],
  roadSeekRadiusM: 25,
  rearSpreadDeg: 60,
  seatSlideM: 6,
  seatRetries: 3,
  seatMaxSlopeTan: 0.45,          // <= 24.0 deg
  seatMinPropM: 3.0,
  nearFireExclusionM: 50,         // unified player gate AND seat gate
  notchMouthExclusionM: 26,       // branch roads' terminal arcs; kingsRoad exempt
  stoneRingExclusionR: 40,        // around (0,-366)
  checkSec: 20,
  triggerChance: 0.25,
  partiesPerNightMax: 2,
  cooldownSec: 180,
  debugForce: false,
  debugMute: false
}
```

The validator must read these FROM CONFIG (`CFG.raid.*`) and treat hard-coded
numbers ONLY as cross-checks: a threshold changed by Nicko at IO must still
pass with the CONFIG value (law thresholds below say "CFG.raid.X" and pin the
spec value as the expected default).

## 3. SEAT LAW THRESHOLDS (lock law, IO spec §A-1 "Lock law" + §Files-2)

Per road (kingsRoad, northRoad, eastRoad, westRoad), over ELIGIBLE seats only
(notch-mouth-excluded seat candidates are counted separately, NOT as fails):

- passPct >= 90 over eligible offset-seats
- max consecutive eligible-fail run <= 16 offset-seats
- offset-seat grid: centerline samples every 4 m per road segment; offsets
  14.0, 14.9, 16.0, 17.5 m, both sides (probe's proven grid — reuse it)
- seat pass predicates (ALL must hold):
  - slope: WH_GROUND.slopeTan(region, x, z) <= CFG.raid.seatMaxSlopeTan (0.45 ≈ 24.0°)
  - props: distance to every CONFIG.regionC.props row with .x >= CFG.raid.seatMinPropM (3.0)
  - fire: distance to nearest banditCampfire row >= CFG.raid.nearFireExclusionM (50, unified)
  - stone: distance to (0,-366) >= CFG.raid.stoneRingExclusionR (40)
- notch-mouth exclusion: no eligible seats within CFG.raid.notchMouthExclusionM (26)
  of a branch road's terminal point in its notch arc; kingsRoad exempt (0 excluded
  on kingsRoad, 56 on each branch road in the probe — matches spec A-1 v3 numbers)

Implementation-agnostic rule for Devbot's build: the validator tests the
BEHAVIOR of pickRaidSeat's returned seats against these predicates across >=
100 seeded player poses per road — it must not import Devbot's internal
helper functions; only the public `window.WH_AMBUSH` surface (init/tick/
state/pickRaidSeat) is driven.

## 4. debugMute HARNESS CONTRACT (IO spec §Files-2 "Warn cue" + §Validation guidance)

- When `CFG.raid.debugMute === true`, WH_AMBUSH MUST suppress ALL ambush
  toasts (warn cue and any state toasts). The harness sets debugMute=true
  via a pre-tick CONFIG clone for every tick-driven case EXCEPT V-A14
  (warn-order) so that recorders stay clean unless a case explicitly tests
  the cue.
- When debugMute === false, the warn cue is
  `game.inventoryUI.toast(CFG.raid.warnLine, CFG.raid.warnSec + 0.6)` at warn
  start — asserted exactly (line copy from CFG, duration = warnSec + 0.6).
- debugMute must not alter state-machine timing (warnT still 2.0 s, spawns
  still resolve): V-A16 asserts parity with the unmuted run.
- debugForce bypasses ONLY the triggerChance roll at check time (IO spec
  gates note); debugForce must NOT relax seat validation — V-A21.

## 5. CASE LIST

Setup shared by tick cases (referenced below as SHARED-SETUP): node harness
per §0; CONFIG loaded; `raid` deep-frozen (V-A30 freeze pattern applies to
every tick case); mock game:

```
game = {
  dayNight: { dormant: false, phase: 'night' },   // controllable per case
  player:   { pos: new THREE.Vector3(px, 0, pz), yaw: <case>, state: 'alive' },
  regionManager: { logic: { activeId: 'forest_of_the_old_king' },
                   enemies: { 'forest_of_the_old_king': [] }, scene: {} },
  inventoryUI: { toast: recorder }                // recorder = [] of {msg, dur}
}
window.WH_AMBUSH.init(game);
```

`WH_Enemy` stub (record-only): constructor records {type, sx, sz, order} on a
case-scoped log and exposes `setFsm`, `setBody`, `terrainHome=null`,
`pos`, `groundY`, `root={position: new Vector3()}`, `yawFrame={rotation:{y:0}}`
sufficient for the spawn grammar lines in IO spec §Files-2 "Spawn mechanics"
to execute without error. `makeBody` records type. The harness restores any
pre-existing `window.WH_Enemy` between cases.

### A. Structure & surface (A-2)

- **V-A01 · CONFIG raid block shape** — Setup: SHARED-SETUP minus mocks; just
  CONFIG. Action: check `CFG.raid` exists and carries every field of §2 with
  spec-default values where stated (read FROM CONFIG, compare against §2
  table). Assertion: all fields present; regionId 'forest_of_the_old_king';
  spawnBandM [14,17.5]; nearFireExclusionM === notchMouth-unified 50; kingsRoad
  is not hard-coded in ambush.js as the ONLY road set (block reads regionId).
  Spec: §Files-1, §V1 scope.
- **V-A02 · ambush.js window surface** — Action: require ambush.js post-CONFIG;
  assert `window.WH_AMBUSH` exposes exactly init, tick, state, pickRaidSeat
  (all functions); IIFE, 'use strict', `var CFG = window.WH_CONFIG` pattern
  allowed; module does not touch DOM, document, or requestAnimationFrame at
  load. Assertion: 4 keys, typeof function ×4; no DOM access at load (module
  loads under node with no browser shims beyond the window=globalThis shim).
  Spec: §Files-2, §Validation guidance.
- **V-A03 · game.js call sites** — Action: text scan (fs.readFileSync, no
  git) of prototype/js/game.js: exactly one `window.WH_AMBUSH.init(game);`
  and exactly one `window.WH_AMBUSH.tick(dt);`; the tick call sits AFTER the
  `rm.updateEnemies(` call (nearest preceding match at the call site); the
  init call sits in the same construction block as other init hooks. Assertion:
  counts === 1 each, order verified by character offsets. Spec: §Files-3.
- **V-A04 · index.html script order** — Action: text scan of prototype/index.html.
  Assertion: exactly one `<script src="js/ambush.js"></script>`, positioned
  AFTER the wolf-debug script line and BEFORE the game.js script line (regex
  on the three script tags in order: wolf-debug < ambush < game).
  Spec: §Files-4.
- **V-A05 · region-manager guard line** — Action: text scan of
  prototype/js/region-manager.js dead-record loop. Assertion: the line
  `if (list[m].fsm === 'dead') st.enemies[m] = 'dead';` is replaced by
  `if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead';`
  (comment marker `CC-AE1` accepted as disclosure); NO other behavioral edit
  in updateEnemies (the guard line is the ONLY difference in that function's
  body vs the pre-landing copy Testerbot pinned in scratch/cc-ae1-val/).
  Spec: §Files-5.
- **V-A06 · touched-file set** — Action: compare byte digests (sha256) of the
  five listed prototype files vs baseline set: CONFIG.js, ambush.js (new),
  game.js, index.html, region-manager.js MUST differ-or-new; save.js, enemy.js,
  daynight.js, wh-ground.js MUST match §1 raw-byte digests exactly. Assertion:
  4 byte-sacred files unchanged; exactly the 5-file surface changed/added;
  no new files elsewhere under prototype/js/ related to this round (only
  ambush.js added). Spec: §Files, §Files-5 "NOT touched".

### B. Gates (A-3 gate matrix)

Each block-alone case (V-A07..V-A13): SHARED-SETUP; debugMute=true; ONE gate
broken, all others green; run `WH_AMBUSH.tick(CFG.raid.checkSec + 1)` ~6
frames; assert mode stays 'idle', no WH_Enemy constructed, toast recorder
empty, nightParties === 0. Then heal the gate and verify the trigger path can
fire (with debugForce=true for determinism) — proving the harness itself is
sensitive (not vacuously passing).

- **V-A07 · g1 dormant blocks** — player alive, region ok, phase 'night',
  g1 false (dn.dormant true). Spec: §Files-2 Gates g1, §V1 scope (dormant boot
  gate reads dn.dormant === false).
- **V-A08 · g2 phase gate** — dormant false, phase 'day' blocks. Spec: §Files-2
  Gates g2, §V1 scope ('night' phase, clock FREE-RUNNING).
- **V-A09 · g3 player-alive gate** — player.state 'dead' blocks. Spec: §Files-2 g3.
- **V-A10 · g4 region gate** — rm.logic.activeId 'regionB' blocks. Spec: §Files-2 g4.
- **V-A11 · g5 fire gate (unified 50 m)** — player within CFG.raid.
  nearFireExclusionM of a banditCampfire row blocks. Fixture: player at a
  seeded pose 40 m from the Bravo fire row used by probe v1 (-60,-186 fire;
  probe kingsRoad@(-15.3,-164.8) fire 49.5 evidence). Assertion additionally:
  the SAME threshold rejects a seat 50 m-ε from a fire row inside pickRaidSeat
  (case V-A19 cross-checks independently). Spec: §Files-1 CONFIG comment
  "one number everywhere: player-check gate AND seat gate (A-1 evidence)",
  §Files-2 g5.
- **V-A12 · g6 cooldown blocks** — cooldownT > 0 at tick. Spec: §Files-2 g6,
  cooldown paragraph; cooldownSec 180 per §2.
- **V-A13 · g7 night cap** — nightParties === CFG.raid.partiesPerNightMax (2)
  blocks. Spec: §Files-1 CONFIG comment "1-2 concurrent per region; V1 = 2
  max, 1 alive at a time", §Files-2 g7, §V1 scope "capped at 1 alive / 2 per
  night".

### C. Trigger / warn / spawn order (A-3)

- **V-A14 · warn-order: cue BEFORE any enemy construct** — SHARED-SETUP with
  debugMute=false, debugForce=true, player on kingsRoad mid-forest.
  Drive: one eligible gate-true frame, then tick frames of dt = 0.25 s across
  the warn window. Assertion: recorder receives
  {msg: CFG.raid.warnLine, dur: CFG.raid.warnSec + 0.6} FIRST; the WH_Enemy
  stub construct log records the FIRST of exactly 3 entries (2 bandit, 1 wolf
  in order [bandit, bandit, wolf]) strictly AFTER warnT reaches 0, i.e. no
  construct during 'warn'. Elapsed warn frames total dt >= CFG.raid.warnSec
  (2.0 s) between cue and first spawn. Spec: §Files-2 state machine 'warn',
  §Files-2 Spawn mechanics, §V1 scope "2.0 s warning HUD cue".
- **V-A15 · spawn mechanics transcript** — same run continued. Assertion per
  stub record: `raidMember === true`; `setFsm('chase')` called before
  `rm.enemies[regionId].push(e)` (mock array length grows by 1 per member,
  final 3); `e.yaw` set from atan2(px - sx, pz - sz) at spawn coordinates and
  within ±60° of (P.yaw + PI) modulo wrap (rear arc, jitter law; deviates
  unconditionally at spawn time per §V1 scope Rear-arc law V1); raiders carry
  NO packId (`e.packId === undefined`) and are not present in any CONFIG row
  scan. Spec: §Files-2 Spawn mechanics, §V1 scope Rear-arc law V1, §Files-2
  "raiders carry NO packId".
- **V-A16 · party seats on ONE locked seat; seat locked at warn time** —
  same run. Assertion: all 3 stubs share the seat {x, z} captured at warn
  start; moving game.player.pos between warn start and spawn does NOT change
  the spawn coordinates (player pos at WARN TIME is locked). Spec: §Files-2
  'idle' bullet "pick seat ONCE (locked through the raid)", Spawn mechanics
  "player pos AT WARN TIME, locked".

### D. Seat law over the grid (A-1 lock law)

Grid method (shared by V-A17..V-A20): reuse the PROVEN probe grid — centerline
samples every 4 m along each of the four seat roads' CONFIG point arrays;
offsets 14.0 / 14.9 / 16.0 / 17.5 m both sides (8 seats per sample). For each
road, >= 100 seeded player poses (mulberry32, seed recorded in the report)
near that road convert pose -> rear anchor (pos + (sin,cos)(P.yaw+PI) at 12 m)
-> call WH_AMBUSH.pickRaidSeat() with debugForce semantics (no trigger roll)
and assert the returned seat against the §3 predicates. pose seeds fixed per
case so Devbot re-runs are comparable.

- **V-A17 · seat band + road-row exclusion + road-seek** — over all poses all
  roads: returned ok-seats have perpendicular distance to the claimed roadId's
  centerline within [CFG.raid.spawnBandM[0], CFG.raid.spawnBandM[1]] (14.0–17.5);
  roadId is ALWAYS one of kingsRoad/northRoad/eastRoad/westRoad; no
  northNotch/eastNotch/westNotch/stoneApproach row is ever claimed; poses whose
  rear anchor sits > CFG.raid.roadSeekRadiusM (25 m) from every seat-road
  sample return {ok:false, why:'no-road'}. Spec: §Files-2 pickRaidSeat
  contract (band, seek radius, excluded rows), §3 thresholds table.
- **V-A18 · seat clearance predicates (slope/prop/fire/stone)** — same run
  continued: every ok seat satisfies slopeTan <= CFG.raid.seatMaxSlopeTan
  (cross-check atan <= 24.0°), min prop distance >= CFG.raid.seatMinPropM,
  nearest-fire distance >= CFG.raid.nearFireExclusionM, Stone distance >=
  CFG.raid.stoneRingExclusionR. Re-measure ALL four predicates independently
  from CONFIG + WH_GROUND (validator's own math, not ambush's). Spec: §3
  thresholds, §Files-2 pickRaidSeat seat-validation list.
- **V-A19 · seat fire gate is the unified 50 m law** — targeted poses within
  50–55 m of each of the 7 campfire rows near seat roads never yield an ok
  seat firing < 50 m (probe v1 king evidence: 49.5 m Bravo-fire seat MUST be
  rejected); one pose pair at 50.0 m boundary checks the >= direction (50.0
  passes). Spec: §Files-1 nearFireExclusionM comment (unified), §3 fire line.
- **V-A20 · notch-mouth exclusion 26 m, kingsRoad exempt** — poses near the
  branch terminals: no ok seat within CFG.raid.notchMouthExclusionM (26) of
  north (0,-596), east (240,-366), or west (-240,-366) computed along the
  BRANCH road terminal arcs as the probe's mouthEnd defines them (terminal 26 m
  of branch roads); kingsRoad never reports mouth exclusion (0 excluded seats;
  seats near kingsRoad's own terminal are legal). Spec: §Files-1
  notchMouthExclusionM comment, §3 thresholds, §A-1 Amendment A.
- **V-A21 · seat validation survives debugForce + slide/retry honesty** —
  debugForce=true: seat predicates STILL enforced (IO gates note). Then a
  synthetic hostile-seam pose (rearmost legal anchor on westRoad with props
  seeded 2 m off candidate offsets, reproducing probe v2's mossBoulder@0.4 m
  fixture class) asserts the slide path: pickRaidSeat retries the seat
  CFG.raid.seatRetries (3) times max, sliding CFG.raid.seatSlideM (6 m) per
  retry toward the rear anchor's road-projection, and EITHER returns an ok seat
  satisfying §3 or {ok:false, ...} with a why — never an ok seat violating any
  predicate; `slide` field reports the count actually taken (probe fix line:
  slide depth 18 m covers a 16-seat fail run). Spec: §Files-2 pickRaidSeat
  (slide clauses), §Files-1 seatSlideM/seatRetries comments, §A-1 lock law.
- **V-A22 · lock law per road (passPct >= 90, maxRun <= 16)** — aggregate
  V-A17..V-A19 pass/fail counts per road over eligible offset-seats (excluded
  mouth seats counted separately, not as fails). Assertion (IO spec §A-1
  "Lock law (validated by Testerbot, same thresholds)"): per road passPct >=
  90 AND max consecutive eligible-fail run <= 16; kingsRoad additionally
  reports notchMouth excluded === 0 (exempt); each branch road reports
  excluded > 0 (= 56 in the probe grid — tolerance: exactly the probe grid's
  excluded count when the same 4 m sampling is used). Spec: §A-1, §3.

### E. Persistence / lifecycle (A-3, §Files-5 rationale)

- **V-A23 · byte-sacred CONFIG rows** — after all other cases (CONFIG never
  mutated post-freeze): re-digest roads/wolfPacks/all regions'
  enemies+props/enemy stat rows live against §1 digests. PASS requires
  equality (A-2 "diff = empty" in node-digest form). Spec: §Files-1
  "Byte-sacred", §Acceptance A-2.
- **V-A24 · cooldown mechanics end-to-end** — wipe path: mark all 3 stubs
  fsm 'dead' via mock; tick -> mode 'idle', cooldownT === CFG.raid.cooldownSec
  (180), party == []; gates stay closed for ticks < 180 s; at 180 s gates
  reopen (debugForce fires again OR seats refuse if pose moved off-road —
  either is a pass, gate-open is the assertion). Also the leash path: all 3
  fsm 'idle' -> same cooldown transition. Spec: §Files-2 'live' -> end bullet,
  'idle'+cooldown bullet, §V1 scope "180 s cooldown after a raid ends".
- **V-A25 · raidMember corpses never enter regionStates (REAL updateEnemies)** —
  require region-manager.js; construct the real
  WH_RegionManager.RegionManager.prototype.updateEnemies path only as far as
  the dead-state record loop needs (stub enemy objects {fsm:'dead',
  raidMember:true/false, pos, cfg.radius, separateFrom noop}), logic stub with
  stateFor(...) returning {enemies:{}}; run the loop. Assertion: CONFIG-roster
  non-raid dead enemies ARE recorded 'dead'; raidMember dead enemies are NOT
  recorded; knownEnemies is not inflated by raid stubs. Spec: §Files-5
  (guarded line + rationale), §V1 scope "PARTIES are TRANSIENT (never saved,
  never in regionStates)".
- **V-A26 · dawn cancel on 'warn'** — mode 'warn' (cue fired, no spawn yet);
  flip dayNight.phase to 'day'; tick once. Assertion: no WH_Enemy constructed,
  nightParties refunded to 0, mode 'idle', no cooldown T set (no raid
  happened). Then a full night cycle (phase back to 'night') allows trigger
  again. Spec: §Files-2 Dawn bullet, §V1 scope.
- **V-A27 · live raid finishes naturally after dawn** — mode 'live'; flip
  phase 'day'; tick: no NEW spawns (stub count stays 3), party runs until
  fsm-wipe leash logic ends it. Spec: §Files-2 Dawn bullet "A 'live' raid
  finishes naturally (leash does the work); no new spawns after dawn".
- **V-A28 · per-night counter resets at new night** — after nightParties hits
  partiesPerNightMax and cooldown expires, simulate dawn passage (phase
  'day' -> 'night'): nightParties === 0. Spec: §Files-2 Dawn bullet
  "nightParties = 0", §V1 scope cap.
- **V-A29 · end-silently on region rebuild / boundary exit** — a 'live' raid
  where all stubs leave rm.enemies[regionId] (mock splice) ends silently:
  mode 'idle', cooldownT set, NO toast emitted (recorder empty after the
  cue). Spec: §Files-2 'live' end bullet "(region rebuild / boundary crossing
  -> end silently, no toast)".

### F.CONFIG purity & knobs (A-3, §Validation guidance)

- **V-A30 · CONFIG purity under deep-freeze** — every V-A07..V-A29 case is
  run with window.WH_CONFIG recursively deep-frozen (Object.freeze walk done
  BEFORE init/tick; V-A01..V-A06 read-only too). Harness fails the case if
  any write occurs (freeze throws TypeError in strict mode; ambush.js
  'use strict' would surface it). Additionally a dedicated case: call
  init/tick/pickRaidSeat once each with freeze on and CONFIG digest before ==
  after. Spec: §Validation guidance "CONFIG purity (deep-freeze WH_CONFIG
  before tick; any mutation fails the case)", §Files-1.
- **V-A31 · debugForce bypasses ONLY the trigger roll** — debugForce=true
  with an illegal seat (fixture: pose whose rear anchor projects onto a road
  segment failing slope) still yields no spawn (g8 refuses); with a legal
  seat, debugForce fires WITHOUT waiting for the 25% chance roll (one check
  frame suffices). Spec: §Files-2 gates note, §Files-1 debugForce comment.
- **V-A32 · debugMute harness contract** — with debugMute=true, the warn cue
  is NOT recorded while the state machine still advances identically (same
  warnT resolution, same spawn frame as an unmuted replay of the same seed):
  assert recorder empty AND tick transcripts equal to the debugMute=false
  run on the SAME seed. Spec: §Files-2 Warn cue "debugMute suppresses ALL
  ambush toasts (validator harness uses it)", §4 debugMute contract.
- **V-A33 · deterministic seat RNG law** — with seeded Math.random, two
  consecutive pickRaidSeat calls with IDENTICAL game state (same pose, yaw,
  random seed reset) return the SAME seat {x, z, roadId} (deterministic given
  game state + its own Math.random calls); Math.random is never called
  outside the pickRaidSeat body during the call (harness counts Math.random
  invocations from init/tick paths = 0 when debugForce=true and check rolls
  are bypassed). Spec: §Files-2 pickRaidSeat "no RNG misuse" parenthetical.

## 6. SELF-CHECK: acceptance-criterion coverage (IO spec §Acceptance criteria)

| Criterion | Covered by |
|---|---|
| A-1 probe report exists + lock law validated | V-A22 (per-road locked thresholds), §3 grid method, probe evidence re-verified this wake (§1 last bullet). NOTE: the probe itself was DONE by IO before the spec froze; the valspec VALIDATES the lock law on Devbot's implementation, it does not re-run the A-1 report. |
| A-2 5-file surface exact + byte-sacred rows | V-A06 (file set), V-A23 (CONFIG digest law), V-A01 (raid block), V-A03/A04/A05 (call sites), plus §1 raw-byte digests for save/enemy/daynight/wh-ground. |
| A-3 node validation harness green (NO browser/harness/playtest) | V-A07..V-A33 — all cases in §0 node harness; no browser step; §5 gate-matrix/seat/persistence/knobs are the A-3 case body. |
| A-4 build_v8 exit 0 + round marker | V-A34 (runner case below). |
| A-5 Testerbot independent verdict PASS -> IO commit | Out of valspec scope: the verdict is GIVEN by Testerbot running these cases; no case can assert a commit. Coverage = the verdict checklist in §7. |

- **V-A34 · build law** — run `python3 tools/build_v8.py` from the worktree
  root; assert exit 0 and grep -c 'CC-AE1' v8-playable.html > 0.
  Spec: §Acceptance A-4. (Build tool invocation is NOT a harness run; it is
  the IO-specified build check.)

## 7. VERDICT CHECKLIST (Testerbot's A-5 input)

PASS requires: every V-case green in a SINGLE node run over the landed
worktree; V-A06 and V-A23 report zero drift; V-A22 shows all four roads
holding passPct >= 90 and maxRun <= 16; any single red case = verdict NEEDED
(with the case ID + transcript in the report file). No playtest language, no
browser claims, no git state claims in the report — evidence is node output
digests and console transcripts only.

## 8. RISK NOTES

- CONFIG.raid values are PROPOSED and Nicko-tunes them (IO spec §Files-1).
  All threshold cases read CFG.raid.* live; if a value changes, the cases
  follow, but V-A22's LOCK LAW thresholds (passPct 90 / maxRun 16) are
  FROZEN evidence (§A-1) — they are NOT tunable without a new IO amendment.
- The seat-law grid is the probe's 4 m/offset grid; a road row edit would
  shift every result. Byte-sacred digests (V-A23) catch any such edit first.
- ambush.js does not exist pre-landing (verified); all WH_AMBUSH cases fail
  loudly (require throws) until Devbot lands — that is correct behavior.
- The mock WH_Enemy stub must be kept record-only; if Devbot's spawn grammar
  starts calling Enemy APIs not in the stub's public surface, the case fails
  with a clear missing-method transcript (desired: it proves non-grammar
  drift), unless IO updates the spawn mechanics contract.
- Known ambiguity: whether WH_AMBUSH exposes state() snapshot before first
  init() — treated as unspecified; the validator calls init before state()
  in every case and does not assert either behavior if init is defensive.
- V-A25 exercises real region-manager.js code paths; if Devbot's edit
  touches neighboring lines beyond the guard, V-A05's body-diff check (vs
  the pre-landing copy pinned in scratch/cc-ae1-val/) catches it.

## 9. AE1-A ADDENDUM (verdict 1 remediation)

Amendment source: io/specs/cc-ae1-night-raids-spec.md, section
"AE1-A amendment (2026-11-06, from Testerbot independent verdict 1: FAIL)".
Two new gates in `CFG.raid`, consumed by js/ambush.js `pickRaidSeat`'s
validation chain (seatWhy), slide law unchanged:

- `seatMinRoadRenderedM: 14` — floor on the distance to the RENDERED road,
  measured by `window.WH_RegionGeom.distToRoad` (region-manager.js's own
  pure helper: whRoadLine Catmull-Rom + sideways sway, exactly the geometry
  the renderer draws). Fallback ONLY when `WH_RegionGeom` is absent
  (harness/node without region-manager.js loaded): the plain polyline
  distance, the old pre-AE1-A law.
- `minPlayerDistM: 14` — straight-line seat-to-player floor (pop-in guard,
  geometry-independent).

- **V-A35 · AE1-A rendered-road floor (real renderer math)** — Devbot
  self-check companion scratch/cc-ae1-dev/cc_ae1_selfcheck.js, case
  V-A35. Loads the CURRENT worktree `prototype/js/region-manager.js` in
  node (window shim only — `WH_RegionGeom` exports pure, no THREE needed)
  so `WH_RegionGeom.distToRoad` is the REAL renderer math, NOT a
  re-implementation. Two assertions:
  (1) The flaw still reproduces raw: every 2 m arc of all 4 seat roads
  (kingsRoad, northRoad, eastRoad, westRoad) × offsets
  14.0/14.9/16.0/17.5 × both sides, with the player standing ON the
  rendered road at the sway displacement (full bulge included) — worst raw
  band seat measures 6.55-7.74 m off its claimed road (kingsRoad 6.86,
  northRoad 6.55, eastRoad 7.74, westRoad 6.81), confirming the verdict-1
  flaw is real and NOT a harness artifact.
  (2) The FIX holds: driving `AMB.pickRaidSeat` from poses ON the rendered
  road across all 4 seat roads — the verdict-1 worst family (k=28,
  mag≈6.5) included — every ok seat's `WH_RegionGeom.distToRoad` to its
  CLAIMED road is >= CFG.raid.seatMinRoadRenderedM, and its straight-line
  distance to the driving pose is >= CFG.raid.minPlayerDistM. Non-compliant
  raw-band candidates either pass at another arc or SLIDE (up to
  seatRetries × seatSlideM) to a compliant seat — the slide law remediates
  the band violations (pickRaidSeat cannot return a seat inside the floor
  when a compliant candidate exists on the road).
- **V-A36 · AE1-A player floor (targeted)** — same harness, case V-A36.
  Pose grid: every 2 m arc of all 4 seat roads projected onto the RENDERED
  centerline (443 poses: kingsRoad 126, northRoad 103, eastRoad 107,
  westRoad 107 — includes full-bulge players). Every ok seat from
  `pickRaidSeat` must satisfy `hypot(seat - pose) >= CFG.raid.minPlayerDistM`
  straight-line. Violations counted: 0.
- **V-A17 semantics update** — from AE1-A, V-A17's band law is measured
  against the RENDERED road (`WH_RegionGeom.distToRoad >=
  seatMinRoadRenderedM`), not the raw CONFIG polyline; verdict 1's raw-band
  fail verdict is superseded by this addendum (the raw band itself still
  violates the floor — confirmed in V-A35 assertion (1) — but pickRaidSeat
  slides to compliance, which is what the verdict now checks).
- **V-A30 adjudication: PASS** (reverses verdict 1's FAIL). The verdict-1
  FAIL was an ORACLE error: the case asserted a strict-mode mutation throw
  that this node build does not produce. The LAW V-A30 binds — CONFIG
  digest unchanged before/after the write attempt with the machine live —
  holds (IO re-ran the purity law directly this wake; Devbot's deep-freeze
  harness run agrees: digest equality, no mutation observed).

Harness tallies after AE1-A (scratch/cc-ae1-dev/cc_ae1_selfcheck.js,
self-check): PASS 172 / FAIL 0 — the original 159 assertions plus V-A01's
AE1-A key checks and the V-A35/V-A36 addendum cases, all green.

