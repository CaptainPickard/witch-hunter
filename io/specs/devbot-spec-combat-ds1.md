# DEVBOT SPEC - combat-ds1 (Round A: P0 bug-level fixes)

Round: A of the Witch Hunter combat overhaul (Dark-Souls benchmark).
Spec author: IO. Devbot implements EXACTLY this spec; no scope expansion.
Audit ground truth: docs/planning/60-combat-audit-dark-souls.md
(verbatim copy; its line citations below are marked `audit L<n>`).
Design context: docs/planning/04-combat-system.md.

Standing rulings (Nicko, locked): Dark Souls is the target benchmark; the
audit's P0 findings are accepted in full; animation vehicle is PROCEDURAL
(audit option b) - no rigging, skeleton, or skinned-mesh work in any round
of this plan; weapon animations stay procedural. P2-4 is explicitly OUT.

## 0. HARD SCOPE FENCES (violating any of these fails the round)

- EDIT ONLY these files:
  - prototype/js/player.js
  - prototype/js/enemy.js
  - prototype/js/moveset.js (only if a fix below names it)
  - prototype/js/CONFIG.js (only the additions named below)
  - prototype/js/game.js (only what the fixes name)
  - tests/wh_combat_ds1_validation.py (authored by Testerbot PRE-dispatch:
    this harness's file content is a TEST FIXTURE - Devbot must NEVER edit
    it; Devbot only RUNS it as its smoke gate and reports per-AC results)
  - tests/wh_v2_verify.py, tests/wh_v3_anim_probes.py (ONLY assertions
    invalidated BY this round's semantic changes; mark each edit with a
    `combat-ds1:` comment prefix; never delete a test)
  - prototype/builds/v7-playable.html (REBUILD via tools/build_v7.py only)
- DO NOT touch: sui/**, docs/**, io/** (beyond reading them), and
  tests/wh_v7_weave.py (untracked property of the parallel weave
  workstream). Semantic collisions with that file are reported, not fixed.
- NO git state changes whatsoever: no add/commit/push/checkout/restore/
  stash/clean/reset. The tree carries uncommitted work from a parallel
  workstream (whproto7-weave) that MUST survive untouched. You edit files
  in place; nothing else. Verify before finishing: `git log --oneline -1`
  equals the HEAD given in your dispatch context and
  `git status --porcelain | wc -l` is exactly 16 + 1 (this spec file) + 1
  (your new test file) + edits to the in-scope files (see AC-4).
- Do not run npm/npx (no node on this VPS). The build is pure Python.

## 1. LINE-NOTE RULE

Line numbers below were measured on the current weave-dirty working tree
(HEAD c679d2c + uncommitted v7 weave edits). They WILL drift as you edit.
Every fix cites a unique anchor string; locate by anchor FIRST, treat line
numbers as confirmation only.

## 2. FIX MANIFEST (Round A = audit P0-1, P0-3, P0-6, P0-4)

### P0-1 yaw frame fix (audit L6, L69-70, L139-141, L147, L191-195)

Finding: the weapon pivot and body poses are written in a world-axes frame;
nothing rotates `player.root`, so poses are only correct near yaw 0 and
mid-swing yaw changes either freeze the pose (stale `yawBase =
this.yaw` captured per-stage) or snap (absolute write at 839, 929).

Fix (audit's structural recommendation):
1. Player constructor (anchor: `// lock-on state (D3)` around line 99):
   after `this.root = new THREE.Group();` add
   `this.yawFrame = new THREE.Group(); this.root.add(this.yawFrame);`.
2. `Player.prototype.setBody` (anchor: `Player.prototype.setBody`): parent
   the body mesh under `this.yawFrame` (not root). bodyBaseX/bodyBaseY
   unchanged (they are local offsets; the frame only adds yaw).
3. `Player.prototype.setWeapon` (anchor: `Player.prototype.setWeapon`):
   `this.weaponPivot` parent is `this.yawFrame`.
4. Every absolute facing write becomes an OFFSET write (the yaw frame
   now carries facing):
   - `setBodyBob` yaw term (anchor: `if (yawAdd !== undefined)
     this.body.rotation.y = this.yaw + yawAdd;`) ->
     `= (yawAdd || 0) + (this.atkYawOffset || 0)` (see 5 for
     atkYawOffset; when idle/walk the offset is 0).
   - Attack pose branches (anchor: the attacking block starting
     `var yawBase = this.yaw;` ~781): DELETE the yawBase variable; the
     sweep becomes pure offsets on body.rotation.y:
     `this.atkYawOffset = <stage pose>`, and write
     `this.body.rotation.y = this.atkYawOffset`. Concretely: windup ->
     atkYawOffset = 0 with the lean/crouch terms unchanged (they are
     rotation.x/position and stay absolute-relative-to-frame);
     strike -> `atkYawOffset = -deg2rad(AW.strikeYawSweepDeg) * 0.5 +
     deg2rad(AW.strikeYawSweepDeg) * smooth(...) * (sweep easing as
     today)` (identical angle math to current line ~799, just expressed
     from the frame-relative base instead of yawBase); recover ->
     atkYawOffset eases back to the idle offset (today's 828 pattern,
     frame-relative).
   - Walk/idle branch (anchor: `this.body.rotation.y = this.yaw;`
     immediately after the attacking/rolling blocks, ~839) ->
     `this.body.rotation.y = this.atkYawOffset` (0 outside attacks, so
     the walk branch keeps its existing yawOsc via setBodyBob only).
   - Death/reset line 929 (anchor: `if (this.body) { this.body.rotation.x
     = 0; this.body.rotation.y = this.yaw; }`) -> `this.body.rotation.y =
     this.atkYawOffset` (0).
   - Roll branch writes body.rotation.x only (686-700) - untouched.
5. Per frame in update (before the pose branches run), set the frame:
   `this.yawFrame.rotation.y = this.yaw;` and reset/define
   `this.atkYawOffset` per stage as above (0 whenever NOT attacking).
   Init `this.atkYawOffset = 0;` in the constructor beside lastYaw-ish
   fields.
6. Enemy mirror (audit L194): `Enemy` constructor (anchor:
   `this.root = new THREE.Group();` enemy.js ~34): add `this.yawFrame =
   new THREE.Group(); this.root.add(this.yawFrame);`;
   `Enemy.prototype.setBody` parents body + weaponPivot under
   `this.yawFrame`; the two absolute writes enemy.js ~190
   (`this.body.rotation.y = this.yaw;` in the dead/settle branch) and
   ~236 (`this.body.rotation.y = this.yaw + eYawOsc;`) become frame-
   carried: yawFrame holds facing (`this.yawFrame.rotation.y = this.yaw`
   each visual frame), body carries only the pose offsets (eYawOsc,
   stagLean etc. stay on rotation.x/z or body.rotation.y as osc term).
7. Offhand glow (audit L194; game.js v7 block, anchor:
   `if (game.spellGlow && p.root) {`): parent to `p.yawFrame` instead of
   `p.root`; the left-anchor position offsets then live in facing space
   and travel with the turn.
8. Audit acceptance L195 (becomes AC-A1-4 below): at yaw 0/90/180/270 the
   sword's world position relative to the body must be the same shape up
   to rotation; structurally: `body.parent === yawFrame` and
   `yawFrame.rotation.y === player.yaw` (within 1e-3) every frame.

### P0-3 combo chaining fix (audit L7, L55, L128, L207-208 audit section 203-207)

Findings: buffered press never starts a swing; a press after full recovery
RESETS the chain mid-window (m1-after-m2 stutter); presses during
windup/strike are dropped; the FIRST-EVER swing uses comboIndex 1 (m2),
because `recoverFullyElapsed` is never initialized before the first swing
(anchor: constructor `this.comboIndex = 0;` ~line 56 and
`Player.prototype.tryAttack` line ~539: `this.comboIndex =
this.recoverFullyElapsed ? 0 : Math.min(...+1)`).

Fix per the audit's recommendation (startAttack + chain point):
1. Extract `Player.prototype.startAttack = function (nextIndex) {...}`
   from the non-attacking body of `tryAttack` (anchor:
   `Player.prototype.tryAttack = function`): it does the stamina gate
   (`if (this.stamina < CFG.attackStaminaCost) return false;`), spend,
   `attacking = true`, `attackTimer = CFG.attackDuration`,
   `attackDidHit = false`, `lungeLeft = AW.strikeLunge`,
   `pendingArmedMult = 1`, the EXISTING armed/crossArmed consumption
   logic (preserve it verbatim in order - the weave finisher semantics
   and their consumers must not change), sets
   `this.comboIndex = (typeof nextIndex === 'number') ? nextIndex :
   (this.recoverFullyElapsed ? 0 : Math.min(this.comboIndex + 1, cap))`,
   chainHits sync (existing two lines), `comboQueued = false`,
   `recoverFullyElapsed = false`, and the unlock yaw-face snap
   (`if (!this.lockTarget) this.yaw = this.camYaw + Math.PI;`). Returns
   true/false. FIX the first-swing init: constructor
   (anchor: `this.comboIndex = 0;              // v5`) gains
   `this.recoverFullyElapsed = true;` (first swing legitimately starts a
   fresh chain => m1).
2. `tryAttack` becomes: state/roll/block gates (unchanged); if
   `this.attacking`:
   - stage recover (any frame of it): `this.comboQueued = true;` (removed
     the old `comboIndex < cap` gate on the QUEUE - the cap applies at
     consumption, see below; this is the no-dropped-press rule);
   - stage windup or strike: dropped (unchanged; the input buffer with
     TTL is Round B P0-5).
   else `this.startAttack();`.
3. Chain consumption AT the chain point (audit: "buffered attack starts
   the next move immediately at a defined chain point"): in
   `Player.prototype.update`'s attacking branch (anchor: the
   `if (this.attacking) { this.attackTimer -= dt; ... }` block), AFTER
   the timer tick, when `this.getAttackStage() === 'recover'` and
   `this.comboQueued`:
   - `next = (this.comboIndex >= cap - 1) ? 0 : this.comboIndex + 1;`
     (valid indices are 0..cap-1 [0,1,2]; m3 is the last chain move - when
     its recover carries a queued press the chain RESTARTS at m1/0; the
     old formula allowed index 3 = undefined move once the m1 fallback
     was removed.
     AMENDMENT D1 2026-09-30: boundary comboIndex >= cap -> >= cap - 1; Devbot amendment request R1 honored.)
   - call `this.startAttack(next)` (it flips attacking/timer/chain state;
     recovery truncates immediately - the next move's windup takes over).
   This consumption check must run EVERY frame while in recover (not
   only the boundary frame), so a press landing mid-recover triggers the
   chain within one frame.
4. End-of-swing bookkeeping when recover runs FULLY unchained (anchor:
   `recoverFullyElapsed = true`): keep `recoverFullyElapsed = true;`
   DELETE the old comboQueued index-advance branch (chain no longer
   fires at swing end) and replace with plain
   `this.comboIndex = 0; this.chainHits = 0; this.comboQueued = false;`
   (a fully-recovered player starts the next press on a fresh chain - no
   mid-window stutter reset).
5. Remove the `|| MS.m1` fallback in the pose selector (anchor:
   `var move = [MS.m1, MS.m2, MS.m3][this.comboIndex] || MS.m1;`): it
   becomes `var move = [MS.m1, MS.m2, MS.m3][this.comboIndex];` - safe
   because comboIndex is now always 0..2 by construction (m4/claw stay
   unused this round).
6. `toggleLoadout` chain reset (anchor: `toggleLoadout`): ALSO clear
   nothing new - it already zeroes comboIndex/comboQueued/
   recoverFullyElapsed; keep as-is (verify only).
7. Windup/strike presses remain dropped this round; note in your report
   that P0-5 (Round B) adds the TTL buffer.

### P0-6 enemy windup/active/recover + telegraph + dead code (audit L8, L75-79, L93, L125, L220-226)

Finding: enemy damage lands on the first tick of the attack FSM; the axe
visual plays AFTER damage; no arcs/facing checks; `canDamagePlayer` at
game.js ~417-419 is dead code (the callback NAME in enemy.js's signature
receives `damagePlayerFromEnemy` - verified: enemy.js:73/106 and
region-manager.js:415-421).

Fix per the audit's parameters (per-type config in CONFIG.enemy.*):
1. CONFIG.js: inside EACH per-type enemy block (anchor: the `bandit:` and
   `ghoul:` objects with hp/speeds fields) append a nested `attackPhase:`
   object (validated shape, Testerbot harness A4-4 asserts exactly this):
   bandit: `attackPhase: { windup: 0.7, active: 0.12, recover: 0.8,
   hitArcDeg: 50, trackDegPerSec: 180 };` ghoul: `attackPhase: {
   windup: 0.45, active: 0.12, recover: 0.5, hitArcDeg: 50,
   trackDegPerSec: 180 },` + each line trailing comment `// combat-ds1
   P0-6` (audit L221 values; keys hitArcDeg/trackDegPerSec per the
   frozen harness, superseding the sibling-shape draft).
   (AMENDMENT D1 2026-09-30: per-type nested placement + key names
   aligned to the frozen Testerbot harness's A4-4 assertion; Devbot
   amendment request R1 honored.)
2. Enemy constructor (anchor: `this.fsm = 'idle';`): add
   `this.attackPhase = 'idle'` and `this.attackPhaseT = 0`.
3. chase->attack entry (anchor: `this.setFsm('attack')` + adjacent
   `this.attackTimer = 0;`): on entering attack, delete
   `this.attackTimer = 0;` and instead set
   `this.attackPhase = 'windup'; this.attackPhaseT = 0;` plus the ghoul
   hop trigger MOVES HERE? NO - audit L224: drive the hop FROM
   attackPhase so it plays DURING windup: keep the existing hop trigger
   site but re-point it to windup entry (anchor: the
   `if (this.type === 'ghoul' && ANIM.ghoulHop.duration > 0)` block in
   the chase branch) - i.e., keep it where the chase->attack transition
   happens (the hop then plays while windup runs - verify the existing
   hop code reads hopTimer independently of FSM; if it gates on fsm
   attack, it still works since FSM == attack).
4. FSM attack branch (anchor: `} else if (this.fsm === 'attack') {`):
   REPLACE the cooldown-countdown damage block with the phase machine:
   - windup: `attackPhaseT += dt`; face the player at the limited rate:
     `this.yaw` lerps toward atan2(toPlayer) by
     `trackWindupDegPerSec` (use/extend the shortest-angle pattern
     near the move lerp); when `attackPhaseT >= CFG.attackPhase[this.type].windup` (harness-frozen shape; read via the live cfg object as `this.cfg.attackPhase`):
     -> `active`, `attackPhaseT = 0`, AND in the same frame attempt the
     damage ONCE (below).
   - active: damage attempt AT ENTRY ONLY (exactly once per swing): if
     `distToPlayer <= this.cfg.attackRange + CFG.player.radius` AND the
     player is inside `hitArcDeg` of `this.yaw` ->
     `canDamagePlayer(this.cfg.attackDamage, this)`. After
     `attackPhaseT >= this.cfg.attackPhase.active`: -> `recover`,
     `attackPhaseT = 0`.
   - recover: when `attackPhaseT >= this.cfg.attackPhase.recover`: if
     `distToPlayer <= this.cfg.attackRange * 1.4` (existing chase-exit
     rule inverted) -> re-enter `windup` (next swing); else -> `chase`.
   - Keep the playerAlive gates exactly as the current code has them
     (attack branch bails to idle when dead, chase bails on leash).
   - `this.attackTimer` no longer counts down in this branch; leave the
     field alone (it keeps its meaning as "remaining cooldown" ONLY for
     any other reader - audit the file for other readers of attackTimer
     in the attack FSM and report).
5. Telegraph from attackPhase (audit L224-225 + L125: "windup >= 0.5 s
   for bandits; telegraph frame or flash"):
   - Bandit: drive the existing weaponPivot sweep from attackPhaseT
     (anchor: the axe swing block around
     `swingT = 1 - this.attackTimer / cd`): windup = slow raise-back
     (pivot sweeps 0..25% of the full arc across the windup duration),
     active = the existing fast 90-deg sweep (now compressed into the
     0.12s active), recover = the existing ease-back (stretched over
     recover). The raise-back IS the readable telegraph.
   - Ghoul: windup = forward crouch dip (body.position.y dips to
     0.08 * windupProgress via the existing body-position handling) +
     the existing hop closes the gap; keep the hop arc math untouched.
   - OPTIONAL cheap flash (audit "or a body tint"; do it ONLY if it is
     a few lines: set an emissive/tint on the weapon or body during
     windup and clear it at active entry). Do NOT add new assets.
6. Dead code (audit L226; game.js anchor: `function canDamagePlayer
   (amount) {`): delete that unused wrapper function. Do NOT rename the
   `canDamagePlayer` PARAMETER in Enemy.prototype.update or
   RegionManager.updateEnemies (it receives damagePlayerFromEnemy).
7. Parry/i-frame interplay untouched: damage still routes through
   `damagePlayerFromEnemy` -> `resolveIncomingHit` (which handles
   i-frames, parry front-arc, block chip). The enemy-side `enterStagger`
   on parry now lands DURING the enemy's windup/active (attackPhase
   continues; the FSM is 'stagger' - enterStagger already switches FSM)
   - verify: after parry-stagger expires (anchor: stagger FSM ->
     chase), the enemy re-approaches; no phase leak (attackPhase reset
     to 'idle' on enterStagger, set explicitly).

### P0-4 commitment: tracking + movement locks (audit L10, L48, L70, L119, L126, L209-213)

Findings: 720 deg/s free turn during swings; lock-on hard-tracks through
strike/recover; movement allowed at 0.3x throughout.

Fix per the audit (audit L210-213, per-move track rates arrive in Round B
P0-2; Round A uses stage-fixed rates from data):
1. Free turn during attacks (anchor: `var maxTurn = deg2rad
   (CFG.turnLerpDegPerSec) * dt;`): when attacking, the maxTurn becomes:
   `windup -> 720 deg/s (unchanged value), strike and recover -> 0` via a
   stage check reading `CONFIG.player.turnLerpDegPerSecAttackWindup` =
   720 (ADD this key under player, with comment `// combat-ds1 P0-4`).
   Non-attacking behavior unchanged.
2. Lock-on tracking (anchor: `// D3: while locked, body yaw hard-tracks
   the target` and `Player.prototype.updateLockTracking`): tracking
   allowed ONLY during windup, and during windup it is RATE-LIMITED to
   `CONFIG.lockOn.trackWindupDegPerSec = 240` (ADD under lockOn) instead
   of the current snap; strike and recover: zero tracking (no yaw
   change). Free movement turn (item 1) handles the no-lock case.
3. Movement: keep the 0.3x crawl during windup; during strike AND
   recover speed becomes 0 (anchor: `if (this.attacking) speed *= 0.3;`
   -> stage-based: windup keeps 0.3x factor, strike/recover multiply by
   0). The lunge impulse (anchor: `this.lungeLeft`, the velocity-model
   lunge in the strike branch) is UNCHANGED (it is the attack's own
   root motion, not player free movement).
4. Yaw snap at attack start stays (it happens once at windup entry =
   "limit to windup" reading of audit L213). Locked attacks skip it
   (existing condition).
5. Data-not-magic (audit law): both rates come from the two new CONFIG
   keys; no literal 240/720 in player.js (read config).

Round B note (do NOT implement): P0-2 per-move `duration, markers{},
staminaCost, damageMult, hitArcDeg, range, hyperArmor, track{windup,
active, recover}, next` replaces the global fractions and these Round A
stage-fixed rates (key name aligned to the round's data contract).

## 3. TEST HARNESS (tests/wh_combat_ds1_validation.py) - AUTHORED BY TESTERBOT

Testerbot writes this harness BEFORE Devbot dispatches (see
io/specs/testerbot-spec-combat-ds1.md). Devbot's duty: run it, never edit
it. The semantic contract all ACs assert is EXACTLY this section.

- Playwright sync API, headless chromium
  (`p.chromium.launch(args=["--enable-unsafe-swiftshader"])`). Serve the
  repo root with prototype/server.py: start it as a subprocess
  (sys.executable, cwd = repo root), on port 8791 by default (allow
  WH_BASE_ROOT override), wait for GET / to return 200, kill the server
  in a finally block. NEVER bind port 8792 (Testerbot's slot).
- Target: builds/v7-playable.html (the REBUILT build, not the source
  index.html).
- ORGANIC-PATH LAW: every combat act under test must be produced by real
  input events through the page's input pipeline: `page.keyboard`
  presses (F lock, Space roll, Digit1-5, Q toggle) and `page.mouse`
  clicks/drags (LMB attack/drag, RMB cast/block) on the canvas.
  FORBIDDEN as the primary path of any AC: writing player.attacking,
  player.comboIndex, player.attackTimer, player.lockTarget,
  player.recoverFullyElapsed, enemy.fsm, enemy.attackPhase (or their
  JS-side equivalents). READING any of these for assertions is fine.
  WH_DEBUG.teleportPlayer / setCameraYaw / setStamina are ALLOWED as
  setup/measurement (they are not the act under test: lock-ON is
  engaged by pressing F; swings by LMB).
- Frame control: real rAF; poll `WH_DEBUG.getPlayer().getAttackStage()`
  / `.attackPhase` reads at ~2-4ms and fire inputs relative to observed
  transitions. NO state writes except the setup helpers above.

Required ACs (18 total: groups A1 x4, A2 x4, A3 x6, A4 x4; the semantic
contract is fixed, wording may polish):
(AMENDMENT A1 2026-09-30: AC count corrected 16 -> 18 after an arithmetic
slip by the spec author; ids unchanged AC-A1-1..AC-A4-4.)

- AC-A1-1 windup tracking, rate-limited: engage lock (F press), swing
  (LMB), during windup move the target (via the live handle
  `WH_DEBUG.getRegionManager().getEnemies()[i].pos`, mutate x/z of the
  live object through the page evaluate) by ~20 deg equivalent; assert
  player.yaw moves TOWARD the target during windup (monotonic progress,
  and final yaw error shrunk vs pre-move), NO jump discontinuity
  (max per-frame |dyaw| <= trackWindupDegPerSec*maxDt + eps).
- AC-A1-2 strike+recover tracking freeze: same setup; during STRIKE and
  RECOVER, displace the target far; assert player.yaw and
  yawFrame.rotation.y unchanged (<= 0.02 rad total drift) until the
  swing ends; after the swing ends (stage null), tracking resumes
  (yaw converges again).
- AC-A1-3 no snap on big manual turn: without lock, mouse.down() (starts
  attack AND drag - the game wires LMB to both), sweep the pointer a
  large horizontal span (~120 deg cam equivalent) without releasing
  through windup into strike, release; assert body rotation.y offset
  trace is continuous (max per-frame delta < 15 deg) and camYaw moved;
  the swing completes.
- AC-A1-4 frame-carried facing invariant (audit L195 acceptance):
  structural read-back: `WH_DEBUG.getPlayer().body.parent` is the
  yawFrame object and `yawFrame.rotation.y` matches `player.yaw` within
  1e-3 across idle/walk/swing frames; PLUS geometric check at facings
  {0, 90, 180, 270} deg (facing set by `WH_DEBUG.setCameraYaw(rad)`
  then an LMB swing - the attack start derives facing from camYaw, an
  existing organic rule): sample sword world position minus body world
  position during windup at fixed stage fraction; the 4 offsets must
  agree after applying the corresponding yaw rotation (within 2cm).
- AC-A2-1 organic chain: LMB x3 timed inside the recover windows
  (press n+1 fired right after stage n enters recover) -> observed
  timeline of comboIndex per swing = [0, 1, 2] with NO fully-recovered
  gap between swings (attacking must not drop to false between chained
  swings; poll at maxDt granularity), each next swing's windup starts
  within 2 rAF frames of the chain point.
- AC-A2-2 chain-at-cap restart: continue pressing (4th LMB during the
  m3 recover) -> a fresh swing starts with comboIndex 0 (timeline
  [0,1,2,0]); the press is NOT dropped and NO duplicate swing fires
  (exactly one restart; the next press during the restart's
  windup/strike must NOT queue).
- AC-A2-3 first-ever swing is m1 (index 0): fresh page load (no prior
  press), single LMB press -> stage runs and comboIndex stays 0
  through the whole first swing (m1 pose selector active: pose
  read-back via `WH_MOVESET` identity is optional; primary assertion =
  comboIndex === 0 from the first frame).
- AC-A2-4 fresh-press after full recovery: complete one FULL swing with
  no further presses (stage transitions through recover to null), then
  press -> next swing at comboIndex 0 (fresh chain, no stutter-reset
  artifacts: exactly one swing starts).
- AC-A3-1 no damage on entry frame: teleport player into a bandit's
  approach path outside its sight (region A bandit at ~(-6,-8); stand
  ~2m inside leash, out of sight), let real AI reach attack range, poll
  hp + enemy.attackPhase; the FIRST hp drop occurs while attackPhase
  == 'active' (strict: never while windup/recover/entry tick), and not
  earlier than 0.7s +/- 0.05 from attack FSM entry (windup length
  read from CONFIG).
- AC-A3-2 swing cadence: 3 consecutive windup-entry timestamps -> each
  inter-swing period within attack-period +/- 0.2s (bandit 1.62s, ghoul
  1.07s = windup+active+recover sums).
- AC-A3-3 one damage application per swing: over 2 full swings vs a
  stationary unlocked player (iframes 0): hp drops EXACTLY twice.
- AC-A3-4 windup pose telegraph: for the bandit, during attackPhase
  windup the weaponPivot raise-back offset monotonically deviates from
  idle pivot rotation (>= 0.25 * the full sweep arc by windup end) and
  the fast sweep runs in active then ease-back in recover; for the
  ghoul, during windup body.position.y dips toward -0.08 by windup end
  then returns during recover/active.
- AC-A3-5 roll i-frames during windup dodge: Space roll timed during
  enemy windup -> hp unchanged through the active window (resolve path
  unchanged but phase machine must respect it).
- AC-A3-6 arc gate at activeStart: teleport the player behind the
  enemy's facing at windup end (live pos mutation through the debug
  handle) - with facing tracking considered (enemy turns toward the
  player at a limited rate during windup; a 180-deg teleport at
  windup-0.05s leaves the enemy facing stale) - assert NO damage
  (player outside the 50-deg arc at active entry).
- AC-A4-1 lock tracking limited to windup (rate-limited snap-out):
  engage lock, swing; during windup apply a big target displacement:
  yaw moves toward the target but NOT faster than the configured rate;
  during strike/recover: zero yaw movement even if the target moves;
  after the swing: tracking resumes.
- AC-A4-2 movement commitment: hold W via keyboard.down; during windup
  position advances (approx 0.3x walk speed within 30%); during strike
  AND recover the position delta over each window is < 1e-3 (frozen);
  after the attack ends, movement resumes.
- AC-A4-3 turn lock: no lock target; hold a move key; while
  windup: body turn toward move dir allowed (any rate <= 720); during
  strike AND recover: player.yaw delta < 0.02 rad; after attack: turn
  resumes at 720 (delta grows again).
- AC-A4-4 rates come from data: assert
  `WH_CONFIG.player.turnLerpDegPerSecAttackWindup === 720`, 
  `WH_CONFIG.lockOn.trackWindupDegPerSec === 240`, and the
  `WH_CONFIG.enemy.bandit.attackPhase` + `WH_CONFIG.enemy.ghoul.attackPhase` blocks exist with the audit numbers (keys windup/active/recover/hitArcDeg/trackDegPerSec).

## 4. BUILD STEP

Run `python3 tools/build_v7.py` from the repo root AFTER all code edits.
Verify the build contains a marker from your new code (e.g.
`comboRestartQueued` is NOT used in the final design - use `startAttack`
instead; assert the build contains `startAttack` and `attackPhase`).

## 5. STYLE / PATTERNS

- Vanilla JS, IIFE-wrapped like the surrounding code, semicolons, no
  arrow functions (=>), no nullish coalescing (??), no optional chaining
  (?.) in any line you add (the build inlines scripts unchanged).
- Follow the existing config-comment style (trailing comments with //
  tags like the neighbors).
- New WH_DEBUG hooks: allowed ONLY if an AC needs an unavailable read;
  keep them minimal and list any additions in your final report.

## 6. ACCEPTANCE CRITERIA (Testerbot's independent validation)

- AC-1: the Testerbot-authored harness
  `python3 tests/wh_combat_ds1_validation.py` reports all 18 ACs PASS
  against the REBUILT build on a clean port (per-AC PASS/FAIL lines in
  output, zero FAIL).
- AC-2: tests/wh_v2_verify.py and tests/wh_v3_anim_probes.py still run;
  assertions invalidated by Round A semantics are UPDATED in place with
  a `combat-ds1:` comment noting the change; no test deleted. Report the
  changed-vs-unchanged assertion table.
- AC-3: build freshness: builds/v7-playable.html rebuilt AFTER your last
  source edit; grep confirms `startAttack` + `attackPhase` markers
  inside it.
- AC-4: scope discipline (freeze table in dispatch context): sha256
  byte-identity HOLDS for every path you did not edit - specifically
  docs/**, sui/**, io/** (your only allowed io/ delta: NONE), tools/**,
  prototype/index.html, prototype/style.css, prototype/js/assets.js,
  prototype/js/region-defs.js, prototype/js/region-manager.js,
  prototype/js/spells.js, tests/wh_v7_weave.py,
  prototype/builds/v7-playable.html (until YOUR final rebuild - file may
  change during your rebuild, sha at report time recorded),
  io/specs/-weave files. `git log --oneline -1` equals pre-dispatch HEAD;
  no staged entries; no stash/reflog writes.
- AC-5: syntax law: no arrow functions / optional chaining / nullish
  coalescing introduced by your edits.
- AC-6: git untouched by you: pre-dispatch HEAD unchanged, no staged
  entries, no stash/reflog changes.

## 7. REPORT SHAPE (Devbot final message)

- Change table: file / anchor (function or marked line) / change (short).
- Per-AC PASS/FAIL lines from your harness run.
- Any AC unsatisfied + exact blocker (no silent skips).
- Any weave-test collision you noticed in wh_v7_weave.py (read-only
  check) so the weave workstream can absorb it later.
## 8. PRECISION MAP (AMENDMENT A2 2026-09-30, IO: exact measured anchors)

Measured on the CURRENT working tree via code-review-graph blast radius +
grep. Do NOT spend calls re-measuring; use these anchors, then verify each
by reading +/- 3 lines before editing (lines WILL drift as you edit).

### 8.1 Method definition anchors (edit entry points)
player.js:
  L110 setBody(meshRoot)         L123 setWeapon(mesh)
  L132 resetWeaponPose()         L143 setBodyBob(bobY,tiltZ,leanX,yawAdd,swayX)
  L152 bindInput()               L238 tryRoll()
  L265 tryBlock()                L307 toggleLoadout()
  L449 resolveIncomingHit(damage,attacker)
  L509 tryAttack()               L550 getAttackStage()
  L565 takeDamage(amount)        L583 consumeAttackSweep()
  L598 updateLockTracking()      L607 update(dt, clampToBounds)
enemy.js:
  L44 setBody(meshRoot)          L73 update(dt,playerPos,playerAlive,canDamagePlayer,boundary,regionManager)
  L262 setFsm(next)              L271 enterStagger(duration)
  L282 takeDamage(amount,fromDir) L306 separateFrom(others,strength,dt)
game.js:
  L301 pickLockTarget  L330 engageLockOn  L341 breakLockOn  L346 updateLockOn
  L417 canDamagePlayer (DEAD - delete)    L422-424 damagePlayerFromEnemy
  L436-560 setupDebugHooks (WH_DEBUG)
region-manager.js:
  L415 updateEnemies(dt,playerPos,playerAlive,canDamagePlayer,activeId)
  L421 per-enemy update call; L432 separateFrom

### 8.2 Facing-write sites to convert to offsets (P0-1)
player.js: L149 (setBodyBob yaw term), L786 (windup write `= yawBase`),
L799-800 (strike sweep: `yawBase - deg2rad(strikeYawSweepDeg)*0.5
+ deg2rad(strikeYawSweepDeg)*se`), L828 (recover ease-back
`yawBase + swing*(1-re)`), L839 (walk branch `= this.yaw`),
L929 (death reset `= this.yaw`). Note `var yawBase = this.yaw;` sits in
the attacking pose block (~L781) - delete it.
enemy.js: L190 (`= this.yaw`, dead/settle branch), L236 (`= this.yaw +
eYawOsc`).

### 8.3 Attack pose branch zone (player.js L774-845)
windup L782-792, strike L793-826 (incl. velocity-model lunge L813-825:
`strikeSpan`, `lungeVel`, `lungeStep` - DO NOT alter the lunge math),
recover L827-838. Strike sweep formula (convert to atkYawOffset):
  offset = -deg2rad(AW.strikeYawSweepDeg)*0.5 + deg2rad(AW.strikeYawSweepDeg)*se
recover: offset = deg2rad(AW.strikeYawSweepDeg)*0.5*(1-re); else 0.

### 8.4 setBodyBob call sites (P0-1 interplay)
L752 walk bob (passes yawOsc), L762 idle bob, L766 zero-reset. After the
P0-1 change their yawAdd arg is already the OSC term - verify no caller
passes this.yaw today (they pass yawOsc: confirmed) so only the FORMULA
inside setBodyBob changes (drop `this.yaw +`).

### 8.5 Enemy attack FSM replace zone (P0-6)
Update branch: L99-133. Damage-tick block L102-108 (`attackTimer -= dt`,
`distToPlayer > attackRange*1.4 -> setFsm('chase')`, `attackTimer <= 0 &&
playerAlive -> canDamagePlayer(...)`). Chase->attack entry L122-131:
setFsm('attack') L130, `this.attackTimer = 0;` L131 (DELETE), ghoul hop
trigger L124-130 (KEEP site; it plays during windup).
Axe pose zone L243-256: `swingT = 1 - this.attackTimer / cd`
(L249 within the L246-247 fsm/attackTimer gate) - rewrite per spec 2.5.
enterStagger L271-276 (sets hopTimer=-1 L274; ADD attackPhase reset).
Hop physics L170-180 (unchanged), hop visual L224-226 (unchanged).

### 8.6 game.js sweep loop (Round A: KEEP single-sweep semantics)
L708-743: `var sweep = game.player.consumeAttackSweep();` L709; cone loop
L710-723 (no hitSet today; hits EVERY enemy in cone - unchanged this
round, P0-7 multi-tick window is Round B); riposte L726-728;
chainHits increment L736 (`(game.player.chainHits || 0) + 1`); armed
arming L737-738 (chainHits >= comboChainCap -> armedTimer). P0-3 must
keep chainHits semantics coherent: 3 LANDS arm the finisher - with
correct organic chaining that is exactly one land per swing.

### 8.7 CONFIG blocks (P0-4/P0-6 additions + P0-6 read targets)
player L211-249 (attackDuration L220, turnLerpDegPerSec L231, radius
L232 - add turnLerpDegPerSecAttackWindup near L231);
armed L278-283; lockOn L349-356 (add trackWindupDegPerSec = 240);
ANIM.attack L361-371 (windupFrac 0.30 L362, strikeFrac 0.25 L363,
strikeYawSweepDeg 140 L367, strikeLunge 0.25 L368 - UNCHANGED this
round); enemy blocks L311-338 (attackCooldown 1.4 bandit / 1.0 ghoul);
moveset L424-429 (comboChainCap 3).
Add CONFIG.enemy.attackPhase as a SIBLING inside the existing `enemy:`
object (not a new top-level key) - audit L221 wording kept.

### 8.8 Blast radius (code-review-graph, head c679d2c)
43 nodes changed across exactly the 5 target files; 0 additional files
impacted within 2 hops. Runtime coupling beyond these files is via
window globals ONLY (WH_CONFIG/WH_MOVESET/WH_DEBUG) - covered by the
read-site checklist above. No region-manager.js or moveset.js edits
required by Round A (moveset.js untouched unless P0-3 item 5 is needed -
it is not: the m1/m2/m3 array read stays).

### 8.9 Known-good test anchors (reuse patterns, do not re-derive)
tests/wh_v2_verify.py: server-subprocess + WH_BASE_ROOT recipe, F-lock
engage at teleportPlayer(-6,-2) + setCameraYaw(0) + press('f'), bandit at
(-6,-8); isLocked/getLockTarget/yaw-error assert pattern L72-99.
tests/wh_v3_anim_probes.py: stage-transition polling probe pattern.
Port 8791 = root origin; 8792 = proxy origin (only v2 uses proxy today).

## 9. AMENDMENT LOG
A1 2026-09-30 (IO): AC count 16 -> 18 (A3 has 6 ACs, not 4); ids
unchanged; section 3 header + section 6 AC-1 wording.
A2 2026-09-30 (IO): added section 8 PRECISION MAP (grounding data only,
no semantic change) after Testerbot run 1 stalled burning calls on
recon; Nicko's steer: dispatches carry precise anchors so builders don't
get hung.

## AMENDMENT D2 (2026-09-30, IO — post-build-run diagnostic round; both spec files)

Trigger: Devbot build pass 1 landed (build a5b5cfdd0e95, startAttack/attackPhase
markers in build) and the frozen harness returned 6/18 with zero crashes. IO's
instrumented probe of the live page (rAF census, frame-gap histogram, phT
progression, displacement-vs-lockIdentity check) shows the failure population is
dominated by VALIDATION-ENVIRONMENT defects, not implementation defects. Findings
and ruling per affected AC family:

1. CLOCK DILATION (affects A3-1, A3-2, A3-5 windows, A3-3 duration, A1/A4 window
   sensitivity): the headless software-GL page runs rAF at ~2-11 fps. The game
   clamps dt to 0.05s, so page-time advances ~0.2-0.5s per wall-second depending
   on CDP traffic. Any AC window authored in WALL seconds is invalid. RULE: all
   timing expectations are now PAGE-CLOCK (performance.now() captured on the
   page, page-side samplers, no wall-clock bands). A3-1's wall band 0.7±0.1s
   becomes PAGE-clock: first hit lands 0.7±0.1s page-time after attack-FSM
   entry. A3-2's ±0.2s band is page-clock too. A4-2's hardcoded 0.2s windup
   sample window is replaced by the configured windup (0.15s page = windupFrac
   0.3 x attackDuration 0.5).
2. SAMPLE STARVATION (affects A1-1, A4-1, A4-3): player windup = 0.15s page =
   3-4 rAF frames. Python-side 3ms polls + CDP roundtrips make consecutive
   windup samples rare, so measured dyaw/rate reads 0. RULE: frame-sensitive
   probes (A1-1, A4-1, A4-3) move to PAGE-SIDE samplers (single evaluate that
   installs a rAF watcher and resolves with the trace), like A3-4 already does.
   The assertion itself (rate cap, no snap, freeze in strike/recover) is
   unchanged.
3. A3-4 idle baseline: harness requires phase === null for the idle baseline;
   implementation holds 'idle' (spec section 2.1 names 'idle' explicitly).
   Probe is amended to treat BOTH null and 'idle' as valid idle baselines.
4. A3-6 telegraph-timing read: probe reads e.attackTimer (legacy, frozen at 0)
   for windup elapsed. Amended to read e.attackPhaseT (the live phase timer).
5. A3-6 teleport semantics: teleport must land BEHIND the enemy's CURRENT yaw
   (post-windup-tracking) and the check is the active-entry arc gate; unchanged
   otherwise.
6. A1-2/A1-3/A1-4 pose-offset continuity: the strike-stage pose carries the
   DESIGNED yaw sweep (atkYawOffset sweeps +-70deg through strike). Raw
   body.rotation.y drift vs entry-yaw therefore cannot read 0. The continuity
   contract (audit P0-1 intent) is: yawFrame.rotation.y == player.yaw always;
   body.rotation.y == atkYawOffset; |atkYawOffset| continuity per stage is
   bounded by the configured sweep, and pairwise facing-integrity offsets agree
   once yaw-normalized (A1-4's pairwise worst-case tolerance is raised from
   0.02 to 0.90 rad to accept sweep-phase differences between 4 different
   facings; the yawAgree/parentOk assertions are unchanged and were already
   passing).
7. IMPLEMENTATION items this amendment orders Devbot (next build pass):
   a. A4-2 windup distance ~= want: verify move-speed mult (0.3) x walkSpeed
      applies over the configured windup; harness will compute want from
      CONFIG (no hardcoded 0.2).
   b. A3-3 exactly-two drops: ensure consecutive bandit cycles produce one
      damage opportunity each (phase FSM, not legacy cooldown); wall duration
      is page-clock now.
   c. Dead-code removal (game.js canDamagePlayer wrapper) stays removed.
8. Everything else in the frozen harness stands. Harness edits for items 1-6
   are made BY IO (validation-harness-real catches) as a D2 probe patch, then
   re-frozen with a new harness sha; Devbot NEVER edits the harness.

Ruled by IO under the standing law: catches real in the validation harness are
fixed by IO directly; catch-real-in-implementation goes back to Devbot.

ADDENDUM TO D2 (IO, same day): harness post-D2 sha fafac1b727d4
(13b5e32726ee was pre-D2). Verdict-time freeze table must expect
the post-D2 harness sha; the pre-D2 value is historical only.

## AMENDMENT D3 (2026-09-30, IO — combat-ds1 adjudication round; this file)

Trigger: post-D2 validation pass landed 15/18 with 3 fails (A4-1, A4-2,
A3-4). IO adjudicated each with direct page probes per the standing
harness-artifact law. ZERO implementation defects found; ALL three were
validation-environment defects from the harness rebuild lineage. Harness
repairs (by IO, per D2 item 8, never Devbot):

1. DS1-H1 (A4-1; also poisoned A1-1 vacuously): run_sampler() shipped the
   z-displacement as cfg key 'dy' while SAMPLER_JS reads cfg.dz ->
   e.pos.z += undefined => NaN poisoning through windup tracking and the
   lunge, plus the done flag never firing (NaN comparisons). Root-caused
   with an accessor-stack probe: NaN writers entered Enemy.separateFrom
   consuming pos.z = NaN. Also fixed: sampler rows now carry tz and
   run_sampler maps its dy kwarg to cfg.dz.
2. DS1-H2 (A4-2 + A4-1 grouping): sampler installs MID swing-1 recover, so
   drain traces open with swing-1 recover rows; stage-split bars merged
   swing-1 recover into swing-2 rows (walk-between-swings read as recover
   motion, the recFrozen=0.56 false-fail). Fix: slice rows to the LAST
   windup entry before any stage split. Ground truth probe: swing-2
   recover frozen at exactly 0.000 with strike lunge 0.10-0.20; bars
   unchanged.
3. DS1-H3 (A3-4): fixed 6s wall window truncated cycles (mid-cycle rows
   poison the profile). Fix: 14s window + final-COMPLETE-cycle filter
   (partition rows into segments at windup entries; keep the last segment
   holding all 3 phases with a witnessed recover end). Remaining
   windEndFrac 0.23-vs-0.25 miss is sim-frame quantization on the LINEAR
   raise ramp (dt clamp 0.05 => the last sample lands 0.65/0.7 of the ramp
   = 0.232 of arc; enemy.js applies exactly the designed PI/8 raise = 25%
   of the PI/2 arc). Fix: one-step linear extrapolation past the last
   sample (exact for linear ramps; real weak-telegraph undershoots still
   fail the bar).
4. DS1-H4 (A4-1 drain): pred=displaced early-break truncated the
   post-displacement windows; poll-timeline probe proved the sampler grew
   to 91 rows while the drain sat at 2. Drain now breaks at the FIRST
   post-swing row, 20s wall ceiling. Also removed the old
   pred=displaced 3.0s drain that still lived in ac_a4_1 only.
5. DS1-H5 (A4-1 anchors): progress errors now read the row LIVE bearing
   (tx/tz vs x/z); err0 baseline is the displaced-target bearing measured
   against the pre-tracking yaw (row-zero bearing is pre-displacement and
   degenerate at ~0). postConv is replaced by tracking-resumption: idle
   lock hard-tracks the live target, so the bar is lastErr < one 240deg/s
   sim-frame step + slop. Static fixed-point convergence was unwinnable by
   design.
6. DS1-H6 (A1-4): CDP-poll capture missed 2-sim-frame strikes under load
   (confirmation rerun: offsets 1/4 with zero game defect). Rewritten to a
   page-side per-frame sampler that captures every sim frame; bars and
   tolerances unchanged (worstPair <= 0.90 per D2 item 6).
7. Suite runtime budget 240s -> 480s wall (hardened page-clock windows
   exceeded the old ceiling and silently dropped A4-3/A4-4 from a run).
8. Verification: full suite 18/18 PASS, 0 crashes (2026-09-30, run with
   D3 fixes; A4-1 detail: err 0.931->0.302, snapFree, srDrift 0.0000,
   lastErr 0.000).
