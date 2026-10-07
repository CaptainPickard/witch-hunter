# AI1 - ENEMY COMBAT LOGIC DEPTH (change order, 2026-10-07)

Status: BRIEF - DO NOT START until Nicko's explicit go.
CLARIFY LOCKED by Nicko 2026-10-07: Q1 real mitigation 0.5x (melee AND
firebolt, front-arc, drops on stagger/parry). Q2 real spell guard - the bolt
is guarded when the bandit faces its incoming direction (single takeDamage
choke, no spells.js edit). Q3 dark-sense kept: engage inside 4m in pitch
dark; light-law (lockOn.lightRadiusFactor) governs sight only at range.
Builder: Claude Code print-mode, model opus, allowedTools Read/Write/Edit/Bash,
--max-turns 80, cwd /tmp/wh-worldfeat, env HOME=/home/hermeswebui/.hermes/
profiles/io/home + PATH=$HOME/.local/bin, identity CaptainPickard
<pickard.nicko@gmail.com>.
Law: NO harness runs, NO headless browser runs. Nicko's playtest is the only
acceptance test. Syntax checks on edited JS only.

## 1. DESIGN INTENT (Nicko's words, verbatim)

1. BANDIT gets smart: lock-on (properly engages and tracks the player),
   strafe (circles and keeps spacing instead of running straight in), and a
   decision loop: attack when it has an opening, BLOCK when the player is
   attacking it.
2. GHOUL STAYS DUMB - zombie run-and-attack is correct and is its charm.
   ZERO behavior change intended; do not regress it.
3. NO perception model, NO detection meters, NO pack logic, NO new enemy
   families this round. Doc 34-enemy-ai-and-bestiary.md is FEEL reference
   only this round; its full scope is a LATER order.
4. All new behavior numbers = PROPOSED rows in CONFIG.enemy, marked
   "PROPOSED, Nicko tunes" - he tunes by playtest.
5. Must not break: L1 XP-on-kill hooks, corpse/loot flow, EPR1 combat
   values, camp/rest/save flows.

## 2. LOCKED RULINGS (decided in census; not open for reinterpretation)

R1. Bandit only. The ghoul's guardMode=0 row makes every new branch skip.
    Ghoul code paths are byte-identical in behavior (see AC-G).
R2. "Lock-on" for the enemy is face-awareness, not the player lockOn system:
    the bandit always knows the player when (player in sightRadius) OR
    (dist < ai1.alwaysKnowsRadius). Inside alwaysKnowsRadius it engages
    even in darkness. No meters, no detection curve (law 3).
R3. Strafe = spacing. In the strafe band the bandit circles tangentially
    around the player and matches spacing; it does NOT stand still and does
    NOT run straight in. Closing from far away uses the EXISTING chase path
    and chaseSpeed. Strafe direction is one persistent orbit direction,
    flipped by a timer or after an attack/guard - no per-tick jitter.
R4. Decision loop: a simple tick timer (ai1.decisionSeconds) evaluated while
    in the strafe band. Branches (in priority order):
      a. Staggered/deflected/guarding -> keep current phase, skip tick.
      b. Player is "attacking it" and guard roll succeeds -> enter guard.
      c. Opening exists (see R5) or attack bias roll succeeds while inside
         attackRadius -> EXISTING setFsm('attack') phase FSM. No new strike
         code of any kind.
      d. Otherwise adjust strafe (circle, correct range).
R5. "Opening" definition (all cheap reads, no new state): player.guardBroken
    true, OR player mid-attack-recover (getAttackStage() === 'recover')
    while inside attackRadius, OR the ai1.attackBias roll.
R6. Guard trigger read: player.attacking with getAttackStage() in
    ('windup','strike') (not 'recover'), OR a cast windup running
    (player.cast.right.windup > 0 || player.cast.left.windup > 0) while
    dist < ai1.guardRespondRadius. Guard lasts until the player returns to
    no-attack/no-cast, capped at ai1.guardSecondsMax. Guard chance rolls
    once per decision tick while the trigger holds (ai1.guardChance).
R7. Guard is a POSTURE: root halts, body turns to face the player. It uses
    the existing block/deflect vocabulary - no new animation system. It is
    REAL MITIGATION (Nicko Q1): while guardActive, any incoming damage whose
    fromDir is inside the bandit's facing arc takes 0.5x (melee AND
    firebolt - both routes already pass fromDir into Enemy.takeDamage, so
    the multiplier is ONE insertion at the top of takeDamage; no spells.js
    edit, the bolt "is guarded" when the bandit faces its travel direction).
    Entering stagger (enterStagger) or deflect always clears guard. Parry/
    riposte/XP paths untouched: a riposte against a guard-cleared stagger
    still works via the existing riposteArmed machinery.
R8. EPR1 rows are FROZEN: hpMax, moveSpeed, chaseSpeed, attackDamage,
    attackRange, attackPhase{}, staggerTime, radius, leashRadius. AI1 adds
    an `ai1:` sub-object only; nothing existing is edited or deleted.
R9. The bandit circles inside the player's lock-on light envelope
    (CONFIG.lockOn.lightRadiusFactor math) - no lighting or lock-on changes.
R10. No new enemy state in save/persistence: guard/strafe/orbit state is
     ephemeral. Enemy persistence stays {type, state, x, z, loot}.

## 3. STATE BLOCK (verified census, 2026-10-07, container-side)

- Worktree /tmp/wh-worldfeat = git worktree of /workspace/witch-hunter
  (gitdir .git/worktrees/wt-new - valid), branch feat/world-visuals,
  HEAD 4695aa9 == origin/feat/world-visuals (pushed). Clean except untracked
  scratch/ files (campkit_id.py, campkit_sheet.py, io_icons512/ - leave them).
- Serving: 8793 host-side share /tmp/wh-playtest-share, releases/4695aa9,
  current -> releases/4695aa9, host md5 == worktree bundle md5 ffb87e82
  (L1.1 markers: WH_LEVEL 53, Dexterity 1, xpFrac 4). 8787 /playtest-feat/
  serves the worktree LIVE (auth-gated; anonymous curls get the Vault page -
  that is expected, not an error).
- Other session: /workspace/witch-hunter main checkout is on
  feat/mouse-bind-cam (0d48bb6) - that is the other lane, do not touch it.
  No checkout-under-serve: the worktree stays on feat/world-visuals.

## 4. SCOPE CONTRACT (real anchors from this census)

Files touched:
- prototype/js/CONFIG.js - enemy rows at lines 823-867. Add `ai1:` blocks to
  CONFIG.enemy.bandit (line 825) and CONFIG.enemy.ghoul (line 845). Nothing
  else in CONFIG changes.
- prototype/js/enemy.js - 547 lines total. The FSM lives in
  Enemy.prototype.update (line 177, signature: update(dt, playerPos,
  playerAlive, canDamagePlayer, boundary, regionManager)); FSM states
  idle/aggro/chase/attack/stagger/dead via this.fsm, setFsm at line 433;
  attack phase FSM (windup/active/recover via this.cfg.attackPhase) at lines
  233-261; strafe/guard/decision logic goes between the chase branch and the
  attack branch, reading the same locals (dist, dx/dz). Existing helpers to
  reuse AS-IS: wrapAngle (line 14), cfgFor (line 20), enterStagger (line
  442), deflect (line 455), isStaggered (line 490), takeDamage (line 494),
  separateFrom (line 529) untouched. yawFrame (line 40) owns facing.
- prototype/js/player.js - READ-ONLY anchors the enemy logic reads:
  this.attacking (line 68), getAttackStage (line 1675 ->
  'windup'|'strike'|'recover'|null), isBlocking (line 669), this.cast.right /
  .cast.left .windup (>0 = casting, tryCast at 1381), this.guardBroken /
 guardBreakTimer (set in resolveIncomingHit, line ~1538).
 The mitigation is ONE insertion at the top of Enemy.prototype.takeDamage
 (enemy.js line 494), BEFORE the existing flow: if this.ai1GuardActive &&
 fromDir within the bandit's facing arc -> amount *= ai1.guardDamageMult
 (fromDir convention verified identical both routes: melee = direction
 player->enemy, firebolt = bolt travel direction, spells.js line 68-69
 passes it through to takeDamage - so the SAME check guards bolts with no
 spells.js edit; knockback leans along fromDir, so arc math must reuse
 wrapAngle exactly as the knockback does, sign-for-sign).

Must-not-break census (verify against, do not modify):
- game.js line 1454: window.WH_Enemy.onKilled = storeCorpseLoot.
- game.js lines 1609-1612: storeCorpseLoot -> corpseLoot.attach +
  WH_LEVEL.awardXP('kill_' + type) + WH_LEVEL.discover('foe', type).
  XP still fires exactly once per kill because kill routing through
  takeDamage -> stage 2 -> onKilled is untouched (AI1 changes WHERE the
  bandit stands and WHEN it swings, not how it dies).
- game.js lines 2290-2334: player attack sweep (riposte, Long Blade mult,
  Dexterity crit roll, chainHits) - untouched.
- player.js resolveIncomingHit (line 1497): parry -> attacker.enterStagger +
  riposteArmed; block chip + guard break - untouched (R7).
- region-manager.js updateEnemies (line 1378) + separateFrom loop (line
  1395) - signature and behavior unchanged; AI1 logic lives inside
  Enemy.update only.
- save/persistence: game.js line 1868 enemy snapshot {type,state,x,z,loot};
  region-manager.js lines 1397-1400 dead-state recording - untouched (R10).

## 5. PROPOSED CONFIG ROWS (all marked "PROPOSED, Nicko tunes" in comments)

CONFIG.enemy.bandit.ai1 = {
  decisionSeconds: 0.4,        // decision loop cadence while in the strafe band
  alwaysKnowsRadius: 4.0,      // engages even in darkness inside this range
  strafeBandInner: 3.4,        // inside this -> give ground (back out)
  strafeBandOuter: 7.0,        // outside this -> close (existing chase path)
  strafeSpeedMult: 0.75,       // x moveSpeed while circling
  strafeDirFlipSeconds: 1.8,   // orbit direction flips at most this often
  attackRadius: 2.4,           // == attackRange on purpose; do not drift
  attackBias: 0.55,            // per decision tick, chance to press the attack
  guardChance: 0.45,           // per decision tick while player attacks it
  guardRespondRadius: 6.0,     // must be this close to react at all
  guardSecondsMax: 1.6,        // guard posture hard cap
  guardDamageMult: 0.5         // locked by Nicko Q1: real mitigation, melee
                               // AND firebolt (fromDir arc in takeDamage)
};
CONFIG.enemy.ghoul.ai1 = { guardMode: 0 };   // zombie stays a zombie

## 6. COMMIT UNITS (one builder run, commit after each unit, push after
##    every commit; if the builder hits --max-turns, resume by rerunning the
##    same brief - work is additive and each unit lands complete)

- S1: CONFIG ai1 rows (PROPOSED comments) + enemy.js decision loop
  (lock-on awareness R2, strafe band + orbit R3, decision tick R4-R5,
  attack via EXISTING setFsm('attack')) + ghoul skip wiring + bundle.
- S2: guard posture (R6-R7: raise/hold/drop + 0.5x front-arc mitigation in
  takeDamage covering melee AND firebolt) + bundle.

Build command after each unit: python3 tools/build_v8.py (from repo root).
Syntax check: parse each edited js file (python -c compile / esprima-style
check or node --check if available in the builder env; NO game run).
Commit message style: feat(ai1): S1 ... / feat(ai1): S2 ...; push to
feat/world-visuals after each commit (git push origin feat/world-visuals).

## 7. ACCEPTANCE CRITERIA (static + Nicko playtest)

Static (builder self-check, report in return):
- AC-S1: bandit ai1 rows exist, every new number commented "PROPOSED,
  Nicko tunes"; EPR1 rows byte-identical (diff shows no other CONFIG edits).
- AC-S2: enemy.js changes are additive branches reading existing fields;
  ghoul takes zero ai1 branches (guardMode 0) - grep shows no ghoul path
  references ai1 rows other than the guardMode gate.
- AC-S3: bundle rebuilt; greps: 'ai1' count > 6, 'strafeBand' >= 2,
  'guardChance' >= 1, 'WH_LEVEL' count unchanged (53), 'Dexterity' = 1.
- AC-S4: XP hooks untouched: storeCorpseLoot body and onKilled assignment
  unchanged in the diff (git diff shows no edits in those hunks).
- AC-S5: no new files, no changes to player.js, game.js, region-manager.js,
  moveset.js, spells.js (guard mitigation if chosen lives in enemy.js only).

Playtest (Nicko's verdict is the gate):
- AC-P1 (lock-on): a bandit notices me outside stealth-dark and properly
  tracks me - it turns to face me as I circle it even when I am outside its
  strafe band.
- AC-P2 (strafe): at mid range the bandit circles and keeps spacing instead
  of face-tanking straight in; it does not moonwalk backwards through me.
- AC-P3 (decision loop): it attacks when I finish a swing (recover) or
  when my guard breaks - not metronome-forever, not never.
- AC-P4 (block): when I start swinging at it, it often raises its guard
  posture; when I parry its swing, the old parry -> stagger -> riposte
  x1.75 loop still works on it.
- AC-P5 (guard damage): my swing into its raised guard does about half
  damage; a firebolt into its guarded face is also reduced; guard drops
  when staggered or parried, and the riposte still lands.
- AC-P6 (ghoul charm): ghouls still sprint straight at me and swing with
  zero new polish - they feel identical to before.
- AC-P7 (must-not-break): killing a smart bandit still drops loot, XP pip
  moves, LEVEL gains and save/load flows still work; camp Save-and-Heal
  unaffected.

## 8. HARD LAWS (verbatim repeats)

- NO automated harness or headless browser runs of any kind. Nicko's
  playtest is the only acceptance test. Syntax checks on edited JS only.
- One change order at a time. This brief is the whole order.
- Commit each unit to feat/world-visuals and push immediately (identity
  CaptainPickard pickard.nicko@gmail.com).
- Never checkout-under-serve. The worktree stays on feat/world-visuals.
- Do not touch /workspace/witch-hunter main checkout (other session lane).
- Leave untracked scratch/ files alone.
- ghoul zero-regression is a hard AC, not a nice-to-have.

## 9. OUT OF SCOPE THIS ROUND

Perception/detection meters, pack logic, new enemy families, Rot Wolf /
Rot-Mother meshes, campkit manifest wiring (queued separate small order),
doc-34 full bestiary scope, enemy casters (WH_LEVEL.magicDefense stays
inert), moon azimuth (parked).

## 10. POST-LAND VERIFICATION (IO runs after builder lands)

1. git -C /tmp/wh-worldfeat status (clean), log shows S1+S2 shas.
2. Host-side via dhost (SSH alias host-only, container fetch broken):
   git fetch + rev-parse origin/feat/world-visuals == worktree HEAD.
3. Bundle marker greps per AC-S3 on the worktree bundle.
4. Flip 8793: tools/wh_release_flip.py via dhost host_exec with timeout
   >= 800s (60s default silently kills flips mid-release-build leaving an
   empty husk that 404s). Target MUST be RELATIVE releases/<sha>.
   If releases/<sha> lacks prototype/builds/ -> delete husk, re-run.
5. Verify: host curl 200 on /current/prototype/builds/v8-playable.html +
   marker greps; releases/<sha> present; 8787 /playtest-feat/ serves the
   worktree live by construction.
6. Hand Nicko both URLs + playtest flow keyed to AC-P1..P7.

## 11. CODE-REVIEW-GRAPH IMPACT (fresh run on the updated graph, 2026-10-07)

Baked in per dispatch law (never piped on the command line):
- Command: code-review-graph impact --repo /tmp/wh-worldfeat --files
  prototype/js/enemy.js prototype/js/CONFIG.js (graph alias wh-worldfeat,
  updated first: 28 files, 221 nodes, 3803 edges).
- Result: status ok; 6 nodes directly changed; 0 nodes impacted within 2
  hops; 0 additional files affected; unresolved_call_sites 0. Graph
  limitation noted (#343): window-global cross-file importers (game.js/
  player.js reading WH_Enemy) are not graph-resolvable - covered instead by
  the manual census anchors in section 4.
- Read of the result: AI1 changes are LOCAL to enemy.js + CONFIG.js rows.
  The risk surface is behavioral (FSM branches), not structural - exactly
  why the AC list is playtest-heavy and the must-not-break census is the
  safety net.