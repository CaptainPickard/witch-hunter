# Witch Hunter Combat: Technical Audit Against Dark Souls

**Scope:** static read of `prototype/js/*` (player, enemy, moveset, CONFIG, game, assets, region-manager), `docs/planning/04-combat-system.md`, `art-direction/3d/meshy_driver.py`, `tests/wh_v7_weave.py`. No files were modified.

**Headline findings, for the gate:**
1. **The weapon doesn't turn with the player.** The pivot is a child of `player.root`, and nothing in `prototype/js` ever rotates `root`. So the sword and axe poses stay fixed to world axes; they only look right when the player faces yaw ≈ 0. (High confidence from the code; check it in play by facing 180° and swinging.)
2. **Organic combo chaining appears broken.** A buffered press never starts the next swing, and the next press resets the chain to 0. Tests set `comboIndex` directly, so the natural path isn't covered.
3. **Enemies hit on the first frame of their attack state, with no windup.** The axe visual plays *after* the damage. That makes parry and roll timing a guess, not a read.
4. **Two poise problems.** Every enemy is fully staggered by every hit. The player can never be flinched.
5. **Commitment is low.** A swing lasts 0.5 s, turning is 720°/s during the swing, and lock-on keeps perfect tracking during the active frames.

---

## 1. INVENTORY (as it exists)

### Load order
`index.html:27-37`: three → gltf-loader → `moveset.js` → `CONFIG.js` → region-defs → assets → spells → `player.js` → `enemy.js` → region-manager → `game.js`.

### `prototype/js/CONFIG.js`: all tunables
| Block | Lines | Contents |
|---|---|---|
| `player` | 211-249 | walk 6 / sprint 10 m/s; sprint drain 18/s; roll speed 14, duration 0.45 s, i-frames 0.35 s, cost 25; attack duration 0.5 s, cost 15, range 3.2, arc half-angle 70°, damage 34; stamina 100, regen 28/s after 0.6 s delay; turn 720°/s; camera params |
| `block` | 293-309 | parry window 0.25 s, parry cost 5, absorb 0.8, stamina drain mult 0.9, arc ±90°, move mult 0.5, regen mult 0.5, guard-break stun 0.8 s, min stamina to re-block 30, riposte mult 1.75, riposte stagger 1.25 s |
| `enemy.bandit` / `enemy.ghoul` | 313-338 | hp, speeds, damage, range, `attackCooldown` 1.4 / 1.0, `staggerTime` 0.4 / 0.35. `aggroPingInterval` is declared but never used |
| `lockOn` | 349-356 | 18 m range, 1.25× hysteresis, 140° cone, cam lerp 6, extra distance 3.5 |
| `anim.attack` | 361-371 | windup fraction 0.30, strike fraction 0.25 (recover gets the remaining 0.45) → **windup 0.15 s, strike 0.125 s, recover 0.225 s**. `windupSwordRaise` and `strikeSwordSweepDeg` are unused (no reference in `js/`) |
| `anim.stagger` / `death` / `shake` / `ghoulHop` | 395-411 | procedural feel values |
| `loop` | 414-417 | `maxDt` 1/20. `fixedTickHz` 60 is **unused** (the loop is variable-dt, `game.js:660`) |
| `moveset` | 424-429 | idle pose, `comboChainCap` 3. `banditStageMult` is unused |

### `prototype/js/moveset.js`: weapon keyframes (`window.WH_MOVESET`)
- Poses m1 slash-l2r, m2 slash-r2l, m3 overhead, m4 thrust and claw, each as `{windup, strike, recover}` with pos/rot Euler triples (`moveset.js:3-39`).
- `interpPose` (`moveset.js:41-48`) is a **linear lerp of Euler angles**. There's no quaternion slerp and no easing.
- Unused data:
  - the per-move `bodyLean`, `crouch` and `lunge` fields;
  - every `recover` keyframe (the recover stage blends strike→idle, `player.js:833`);
  - `m4` and `claw` (the selector is `[m1,m2,m3]`, `player.js:780`);
  - `WH_MOVESET.chainCap` (`:40`; the code reads `CONFIG.moveset.comboChainCap` instead).

### `prototype/js/player.js`: player controller
- **State fields** (`:31-105`):
  - timers and flags: `stamina`, `staminaRegenBlock`, `iframes`, `rolling`/`rollTimer`, `attacking`/`attackTimer`/`attackDidHit`, `lungeLeft`;
  - combo: `comboIndex`, `comboQueued`, `recoverFullyElapsed`;
  - defence: `blocking`, `parryTimer`, `guardBroken`, `guardBreakTimer`;
  - v7 weave: focus, loadout, cast, belt, armed;
  - camera and lock: `camYaw`/`camPitch`, `lockTarget`.
- **Input** `bindInput` (`:152-222`): Space → `tryRoll`; F → `onLockToggle`; Q → `toggleLoadout`; 1-5 belt; R/T consumables; LMB → `tryAttack` and camera drag; RMB → `tryCast` (loadout 1) or `tryBlock` (loadout 2) (`:189-194`); RMB up → `endBlock`. Inputs act immediately on the DOM event. The only buffer is `comboQueued`.
- **Movement** (`update`, `:701-770`): camera-relative WASD (`:717-726`); sprint drains stamina (`:708-714`); speed ×0.3 while attacking (`:715`); body turns toward the move direction at 720°/s **including while attacking** when not locked (`:731-736`).
- **Walk and idle animation** (`:737-768`): layered sine bob, lean, sway and yaw oscillation through `setBodyBob` (`:143-150`).
- **Stamina**: `spendStamina` (`:560-563`); regen with delay, halved while blocking, **still active while attacking** (`:619-626`). Roll and attack need the full cost up front (`:247`, `:519`). There's no stamina-break state.
- **Attack timing**:
  - `tryAttack` (`:509-547`) spends stamina, sets `attackTimer = attackDuration`, applies the armed multiplier, computes `comboIndex`, and snaps yaw to the camera when unlocked (`:546`).
  - `getAttackStage` (`:550-558`) derives windup/strike/recover from **global** fractions, so every move has the same timing.
  - Combo rules: a press during recover sets `comboQueued` (`:513-516`); presses during windup or strike are dropped (`:512-517`).
  - End of swing (`:663-677`): sets `recoverFullyElapsed = true`; if `comboQueued`, it increments `comboIndex` but **starts no attack**.
- **Cancel windows**: a roll cancels during windup only (`:240-246`); strike and recover can't be cancelled. A cast is allowed during windup (`:351`). Block is refused during any attack stage (`:266`).
- **Dodge roll**: `tryRoll` (`:238-260`) gives i-frames 0.35 s starting at t = 0 and goes in the input direction, or facing when idle. The roll body (`:686-700`) moves at constant speed with a smoothstep 360° tumble on `body.rotation.x`. There's no recovery stage and no stamina/equip-load scaling.
- **Block and parry**:
  - `tryBlock` (`:265-271`) opens `parryTimer` on press. `endBlock` (`:273-276`). Guard break (`:294-302`, and inline at `:489-495`).
  - `resolveIncomingHit` (`:449-504`), in order: i-frames → parry (front arc; staggers the attacker via `enterStagger`; sets `riposteArmed`) → block (chip damage plus stamina drain, then guard break) → full damage.
  - **Blocking has no pose**: the not-attacking branch resets the weapon pose (`:837-843`).
- **Taking damage**: `takeDamage` (`:565-578`) subtracts hp and fizzles a cast. **No hitstun, flinch or knockback**, and an attack in progress keeps going.
- **Hit output**: `consumeAttackSweep` (`:583-595`) returns a single cone `{origin, dir(yaw), range 3.2, halfAngle 70°}` **once**, on the first tick where the stage is `strike`. The comment says "midway", but it actually fires at the start of strike.
- **Attack animation** (`:774-845`): three hand-written branches.
  - windup: lean back plus crouch; weapon idle→windup through smoothstep;
  - strike: body yaw sweep 140°, ease-out; weapon windup→strike; velocity-model lunge 0.25 m (`:813-820`);
  - recover: yaw returns to neutral; weapon strike→idle.
  - This is time-sampled pose lerping written as imperative code. There's no clip abstraction or mixer.
- **Weapon attach**: `setWeapon` (`:123-130`) creates `weaponPivot` as a child of **`this.root`**. `root` only ever receives position (`:847`). Facing lives on `body.rotation.y` (`:786`, `:799`, `:828`, `:839`). A grep for `root.rotation` across `js/` finds nothing.
- **Lock-on**: `updateLockTracking` (`:598-605`) sets yaw to the target every frame, **including during strike and recover**. Lock camera (`:861-884`): yaw lerp to behind-player-toward-target, midpoint framing, fixed pitch.
- **Free camera**: auto-follow while moving (`:886-899`).

### `prototype/js/enemy.js`: bandit and ghoul FSM
- States (`:25`): `idle | aggro | chase | attack | stagger | dead`, plus a separate `riposteStaggerTimer` lockdown (`:89-98`).
- **Attack** (`:101-109`): on entering attack, `attackTimer = 0` (`:131`). The next tick fires `canDamagePlayer` right away (`:105-106`), then repeats every `attackCooldown`. The only condition is distance ≤ 1.4× range (`:103`). **No windup, no active window, no facing or arc check.**
- In attack state yaw is frozen, because it only updates while moving (`:162`, `:154-157`).
- **Telegraph**:
  - ghoul hop, 0.25 s, fires on the same transition as the damage tick (`:124-130`, `:170-180`);
  - bandit axe sweep is driven by the cooldown countdown, i.e. it plays **after** damage (`:245-253`).
- **Hit reaction**: `takeDamage` (`:282-302`) sets `fsm = 'stagger'` on **every** hit (`:300`) plus a 0.15 s lean and knockback. After `staggerTime` it goes to chase (`:100`), then attack with an instant hit.
- **Parry stagger**: `enterStagger` (`:271-276`) freezes the enemy for 1.25 s.
- Weapon pivot is also a child of `root` (`:55-56`), so the same world-axis bug applies.
- Separation: `separateFrom` (`:306-323`), called from `region-manager.js:415-433`.

### `prototype/js/game.js`: orchestration and hit resolution
- `loop` (`:655-752`), variable dt clamped: player update → cast tick → projectiles → region transition → `rm.updateEnemies` (enemy damage goes through `damagePlayerFromEnemy` → `resolveIncomingHit`, `:422-424`, `:704-706`) → **player sweep resolution** (`:709-743`) → lock-on → camera → shake → HUD.
- **Sweep resolution** (`:709-743`):
  - distance to the enemy **centre** ≤ 3.2 (enemy radius ignored) and |angle to player yaw| ≤ 70°;
  - hits **every** enemy in the cone;
  - riposte = ×1.75 on any hit against a staggered enemy with `riposteArmed` (`:726-729`);
  - `chainHits` counts per enemy hit (`:736`) and arms the finisher at ≥ 3 (`:737-739`);
  - shake only when locked on (`:741`).
- `canDamagePlayer` (`:417-419`) is dead code; it would bypass block and parry if anything called it.
- **Lock-on**:
  - `pickLockTarget` (`:301-323`): nearest enemy in the camera cone;
  - `engageLockOn` (`:330-339`), `breakLockOn` (`:341-343`);
  - `updateLockOn` (`:346-363`) breaks on death, range or region change;
  - screen-space reticle div (`:366-381`);
  - **no target switching**.
- Hit feedback: `triggerShake` / `applyCameraShake` (`:401-415`); flash overlays through `onParry`/`onBlock`/`onGuardBreak` (`:604-619`); armed emissive pulse on the sword (`:202-222`). **No hitstop.**
- Boot (`:623-636`): player body = `human-hunter-male.glb` scaled to 1.8 m; `longsword` at ×0.9, attached to `root` first and then moved into the pivot by `setWeapon`.

### `prototype/js/assets.js`: asset pipeline
- Manifest: `playerBody` → `races_regen/human-hunter-male.glb` (`:44`); `longsword-pixelated.glb` and `hand-axe-pixelated.glb` (`:48-50`). No shield or greatsword is loaded, although `weapons/greatsword*.glb` and `round-shield*.glb` exist.
- `loadOne` keeps only `gltf.scene`; **`gltf.animations` is discarded** (`:159-162`).
- `instance` uses `clone(true)` (`:191-195`). That is **unsafe for SkinnedMesh**, and SkeletonUtils isn't vendored (the only files in `prototype/vendor/` are `three.classic.js` and `gltf-loader.classic.js`). `AnimationMixer` and KeyframeTracks do exist in `three.classic.js`.
- `groundAlign` (`:110-120`): Meshy meshes ship with centred pivots, and the code corrects this by bounding box. Weapons therefore have **no authored grip origin**.
- Asset source: `art-direction/3d/meshy_driver.py:13` uses Meshy **image-to-3d** only, with remesh (`:32`). There's no rig or animation step and no Blender tooling in the repo.

### Tests
`tests/wh_v7_weave.py:231`, `:308`, `:341` set `comboIndex` directly. No test drives an organic LMB→LMB→LMB chain.

---

## 2. GAP ANALYSIS vs Dark Souls

| DS pillar | State | Evidence | What "resembling DS" requires |
|---|---|---|---|
| **Commitment / weight** | Partial (weak) | 0.5 s total swing (`CONFIG.js:220`, `:362-363`); turning at 720°/s during swings (`player.js:731-736`); movement allowed at 0.3× (`:715`); lock hard-tracks during strike (`:598-605`, `:680`) | Per-move durations (2H light ≈ 1.0-1.2 s, heavy ≈ 1.4-1.8 s, as starting targets); tracking limited to windup, zero in active and recover; no free movement (root-motion lunge only) |
| **Stamina economy** | Partial | Full-cost gate (`player.js:247`, `:519`); regen continues during attacks (`:619-626`); 0.6 s delay (`CONFIG.js:228`) against the doc's ~1 s (`04:139`); no stamina-break (`04:137-138` intent) | Act on any stamina > 0 and floor at 0; no regen during attack active/recover; stamina-break at 0; block drain already exists |
| **I-frames** | Present (basic) | `rollIFrameWindow` 0.35 of 0.45 s from t = 0 (`player.js:251`); checked at a single instant (`:451`, `:566`) | I-frames starting a few ms in; a roll recovery stage with no i-frames; equip-load roll tiers (`04:143-146`); roll-cancel from late recover; input buffer |
| **Hyperarmor / poise** | Absent (inverted) | Enemy: every hit → `stagger` (`enemy.js:300`). Player: can't be flinched (`player.js:565-578`) | Poise pools on both sides (`04:106-119`); stagger only on poise break; per-move hyperarmor on heavies and 2H active frames; flinch otherwise |
| **Parry window** | Partial | 0.25 s from RMB press (`player.js:270`, `CONFIG.js:294`); resolves against instant enemy hits (`enemy.js:105-106`) | Mechanically fine, but meaningless without enemy windup/active frames; needs a parry pose and animation plus a recovery punish on a whiff |
| **Riposte / backstab** | Partial / Absent | Riposte = ×1.75 on the next ordinary swing (`game.js:726-729`); no backstab code anywhere | Dedicated critical input when close to a staggered enemy in front or an unaware enemy from behind; paired animation; i-frames and position snap during the crit; big damage multiplier |
| **Readable telegraphs** | Absent | Damage on the first attack-state tick (`enemy.js:131`, `:105`); axe animation plays after damage (`:245-253`); ghoul hop at the same moment as the hit (`:124-130`) | Enemy windup → active → recover sub-states, with windup ≥ 0.5 s for bandits; telegraph frame or flash (`04:487-489`); a real hit test at active start |
| **Lock-on framing** | Present (partial) | Engage and break (`game.js:301-363`); camera midpoint framing (`player.js:861-884`); no target switching; fixed pitch | Target switching (`04:42`); pitch that frames tall targets; tracking rate limit during attacks; strafe-facing already present |
| **Animation-driven hit timing** | Absent | Stage from global fractions (`player.js:550-558`); one-tick cone at strike start (`:583-595`); the weapon pose has no role in collision | One frame-data table per move shared by animation and gameplay; multi-tick active window; blade-segment or tuned cone test; hit-once set |
| **Combo chain** | Broken (likely) | Buffered press only increments the index (`player.js:669-671`) and the next press resets it (`:539-540` with `:667`); first-ever swing uses index 1 (`:58` + `:540`); index 3 falls back to m1 (`:780`) | Buffered press auto-starts the next move at a defined chain point; explicit per-move `next` |
| **Hit feedback (weight)** | Partial | Shake only when locked (`game.js:741`); knockback 0.18 m (`CONFIG.js:400-402`); no hitstop | 60-100 ms hitstop on connect, per weapon class (`04:492-494` intent) |
| **Block** | Partial | Mechanics exist (`player.js:483-500`); no pose (`:837-843`); only in loadout 2, which has no shield mesh (`assets.js:48-50`) | Guard pose, shield mesh, block reaction animation, chip poise (`04:118`) |
| **Enemy verbs** | Absent | FSM only has chase and instant hit (`enemy.js:99-133`) | Doc 04:148-157 wants bandits to have sloppy roll/block; at minimum spacing, strafing and 2-3 attacks with variable timing |

---

## 3. WEAPON ANIMATION PLAN

### Constraints taken from the code
- The body is **one rigid mesh**. Everything today is whole-body transforms on `body` (`player.js:785-835`) plus a separate `weaponPivot` (`:123-137`).
- The pivot is in world-axis space (P0-1 below), so the current keyframes are only correct at yaw ≈ 0.
- The pipeline is Meshy image-to-3d (`meshy_driver.py:13`) with no rigging stage. The loader drops animations (`assets.js:159`), and `clone(true)` breaks skinned meshes (`assets.js:194`).
- Weapon GLBs have centred pivots (`assets.js:104-109`), so grip and tip points have to be authored as offsets.

### Options compared

| | (a) Full rig + keyframed clips | (b) Procedural / programmatic in Three.js | (c) Hybrid (recommended end state) |
|---|---|---|---|
| **What** | Rig `human-hunter-male.glb` (Meshy auto-rig / Mixamo / Blender), author or retarget clips, play them through `AnimationMixer` | Keep rigid meshes. Turn `moveset.js` keyframes into `THREE.AnimationClip`s with `QuaternionKeyframeTrack` / `VectorKeyframeTrack` targeting named Object3Ds (`yawFrame`, `body`, `weaponPivot`), played by `AnimationMixer`. The mixer drives any Object3D; no skinning needed | Rig the player body only (about 22 bones). Weapon parented to a hand socket bone. Clips for body motion, procedural additive layers for lean, lock twist and hit-react. Enemies stay on (b) until later |
| **DS feel ceiling** | Highest (anticipation, overlap, two-handed grip, paired crits) | Medium. Timing and weight can be sold by body lean/crouch/yaw and weapon arcs, but limbs don't move. Readable at a pulled-back camera; the stiffness shows up close | High for the player; medium for enemies |
| **Pipeline changes** | Rigging step per race GLB (10 races under `races_regen/`); keep `gltf.animations` in `loadOne`; vendor `SkeletonUtils.clone`; animation retarget or naming standard | None for assets. Code: a new clip builder in `moveset.js`, mixer in `Player` and `Enemy` | (a)'s pipeline for one character plus (b)'s code path |
| **Hit-sync fit** | Excellent: markers are clip times | Excellent: same marker scheme | Excellent |
| **Effort** | **L** (rig ×N characters, ~15 clips for 2H, loader/clone work, per-race retarget QA) | **S-M** (M if the roll, block and parry clips are included) | **M-L** (L across all races; M for the player-only slice) |
| **Risk** | Meshy auto-rig quality on stylised or pixelated meshes is unverified; the whole art pipeline has to change; doc 04:31-33 still assumes "no 3D skeleton" or sprites, so the direction needs a ruling | Rigid look; Euler lerp artifacts if the current `interpPose` is kept (use quaternions) | Two animation systems in parallel; a skinned player next to rigid enemies looks inconsistent |

**Recommendation:** ship **(b) now** as the P0 vehicle, because it fixes timing and commitment with the assets we have. Design its data contract (clip plus markers, below) so that **(c)** swaps skinned clips in without touching gameplay code.

### Minimum viable animation set: two-handed sword baseline
The asset exists: `art-direction/3d/assets/weapons/greatsword-pixelated.glb`. Add it to the manifest next to `longsword` at `assets.js:49`.

The core required set is **idle / windup / strike / recover**, laid out as one clip per move with markers:

| Clip | Loop | Proposed starting timings (tune in play) | Notes |
|---|---|---|---|
| `2h_idle` | yes | 1.2 s breath (reuse `anim.walk.idlePeriod`) | Blade low-guard, both hands on the grip |
| `2h_light_1` (windup → strike → recover) | no | windup 0.40, active 0.15, recover 0.50 = **1.05 s** | Diagonal right-to-left. Markers: `activeStart` 0.40, `activeEnd` 0.55, `comboOpen` 0.55, `comboClose` 0.90, `rollCancel` 0.75, `end` 1.05 |
| `2h_light_2` | no | 0.35 / 0.15 / 0.55 | Return swing; chains from light_1's `comboOpen` |
| `2h_heavy` | no | 0.70 / 0.18 / 0.70 | Overhead; `hyperArmor` over [0.35, 0.88] |
| `2h_run` carry (additive on walk bob) | yes | follows `bobPhase` | Blade on shoulder |

For DS parity, add next: `roll` (replacing the tumble at `player.js:691-694`), `guard` (hold), `parry` (0.25 s active, then ~0.4 s whiff recovery), `flinch` (0.3 s), `stagger` (1.0-1.25 s), `guard_break` (0.8 s = `guardBreakStun`), `riposte`/`backstab` (paired attacker + victim, ~1.5 s), `death`.

### Skeleton requirements for (a) and (c)
- Humanoid, Y-up, metres. Height normalised to `CONFIG.world.characterHeight` 1.8 (`CONFIG.js:39`). Rest pose A-pose. Feet at y = 0, so `groundAlign` becomes a no-op.
- Bones (~22), Mixamo-compatible names for retargeting: root, hips, spine, spine1, chest, neck, head; clavicle/upperarm/forearm/hand ×2; thigh/calf/foot/toe ×2.
- **Sockets** (extra bones or empties): `socket_weapon_R` (grip, weapon +Y along the blade), `socket_offhand_L` (spell glow / shield, replacing the mirrored-idle hack at `game.js:263-264`), `socket_2h_L` (pommel target for the left hand, IK optional).
- Weapon GLB: origin at the grip, plus a `tip` empty node, or a per-weapon config `{gripOffset, bladeLength}` if re-exporting isn't practical.

### How hit timing keys off animation sync
1. **A single time source.** Each attack is `{clip, markers, gameplay}` in `moveset.js`. Gameplay stage is read from `action.time`, **never** from a separate `attackTimer`. `getAttackStage` (`player.js:550`) becomes a marker lookup, so render and gameplay can't drift apart.
2. **Marker events.** Three.js has no clip events. Detect crossings each tick with `prev < marker <= action.time` and dispatch to `onActiveStart`, `onActiveEnd`, `onComboOpen` and so on.
3. **Active window, not a single tick.** Between `activeStart` and `activeEnd`, run the hit test every tick with a per-swing `hitSet`, replacing the single `attackDidHit` (`player.js:584-586`). Test: the blade segment (grip→tip from `weaponPivot.matrixWorld`), swept from the previous tick to this one, against an enemy cylinder of `cfg.radius`. The cheap fallback is today's cone with a per-move arc and enemy radius added to range.
4. **Hitstop via mixer.** On connect, set `mixer.timeScale = 0` for the attacker and victim for about 80 ms. Gameplay timers must also pause, which is why point 1 matters.
5. **Enemies use the same contract.** Enemy damage fires at `activeStart` inside `resolveIncomingHit`, so parry and i-frame checks line up with a visible frame.

---

## 4. COMBAT RECOMMENDATIONS (dev-spec input)

### P0: correctness and core commitment

**P0-1: Put weapon and offhand into the facing frame.** Size **S**, risk **low**.
- In the `Player` constructor (`player.js:103`), add `this.yawFrame = new THREE.Group()` under `root`.
- `setBody` (`:110-119`) and `setWeapon` (`:123-130`) parent to `yawFrame`.
- Each frame, set `yawFrame.rotation.y = this.yaw` and make every `body.rotation.y = …` write (`:149`, `:786`, `:799`, `:828`, `:839`, `:929`) an **offset** (the yaw-oscillation and sweep terms only).
- Do the same in `Enemy.setBody` (`enemy.js:44-67`, `:190`, `:236`) and for `spellGlow` (`game.js:256`).
- Acceptance: at yaw 0, 90, 180 and 270 the sword's world position relative to the body is identical under rotation.

**P0-2: Per-move frame data.** Size **M**, risk **medium** (weave tests touch the chain).
- Extend each move in `moveset.js` with `duration, markers{activeStart, activeEnd, comboOpen, comboClose, rollCancel}, staminaCost, damageMult, poiseDmg, arcHalfDeg, range, hyperArmor:[t0,t1], track{windup, active, recover} (deg/s), next`.
- Replace the global `CFG.attackDuration`/`AW.*Frac` use in `getAttackStage` (`player.js:550-558`) and in the pose branches (`:781-836`).
- Delete the unused `recover` keyframes, or wire them in as the recover blend.
- Add `2h_*` moves and load `greatsword-pixelated.glb` (`assets.js:49`).

**P0-3: Fix combo chaining.**
- Pull out `startAttack(moveId)` from `tryAttack` (`player.js:519-546`).
- In `update` (`:663-677`), when a buffered attack exists and the clip reaches `comboOpen`…`end`, call `startAttack(current.next)` immediately. Stop setting `recoverFullyElapsed` in that case.
- Initialise so that the first swing is index 0 (`:58`, `:539-540`). Remove the `|| MS.m1` fallback at `:780` by driving from `next`.
- Add an organic test: LMB×3 → moves m1, m2, m3 observed, and `armedTimer > 0` after 3 hits on **one** enemy. The per-enemy increment at `game.js:736` currently arms on a single swing that hits 3 enemies.

**P0-4: Commitment (tracking and movement locks).** Size **S**, risk **low**.
- While `attacking`, replace the free turn at `player.js:731-736` with `maxTurn = move.track[stage] * dt`.
- In `updateLockTracking` (`:598-605`), rate-limit to the same `move.track[stage]` instead of snapping.
- Set speed to 0 during active and recover (`:715`), keeping only the lunge (`:813-820`).
- Remove the yaw snap to the camera at `:546`, or limit it to windup.

**P0-5: Input buffer and cancel windows.** Size **S-M**, risk **low-medium**.
- Add `this.buffer = {action:'attack'|'roll'|'heavy', t}` with a 0.25 s TTL. `tryRoll` (`:238-260`) and `tryAttack` (`:509-518`) write to the buffer when refused instead of dropping the input.
- Consume the buffer at `rollCancel` (roll) or `comboOpen` (attack), and at roll end (a new `roll.recover` of ~0.12 s with no i-frames, added to the roll branch `:686-700`).
- `comboQueued` becomes redundant.

**P0-6: Enemy windup → active → recover with a real hit test.** Size **M**, risk **medium** (tests depend on enemy damage cadence).
- In `Enemy.update`, replace the attack block (`enemy.js:101-109`) and the entry at `:122-131` with an `attackPhase` state machine. Per-type config in `CONFIG.enemy.*`: `windup` (bandit 0.7, ghoul 0.45), `active` 0.12, `recover` (bandit 0.8, ghoul 0.5), `trackWindupDegPerSec` (180), `arcHalfDeg` (50).
- Face the player during windup at the limited rate, freeze during active and recover.
- At `activeStart`, call `canDamagePlayer` only if distance ≤ `attackRange + player.radius` and the player is in the arc.
- Drive the axe swing (`:245-256`) and the ghoul hop (`:124-130`) from `attackPhase`, so the hop plays during windup.
- Telegraph: emissive flash on the weapon, or a body tint for the ghoul, at `windup − 0.1 s` (doc `04:487-489`).
- Remove the dead `canDamagePlayer` at `game.js:417-419`.

**P0-7: Player hit detection over an active window.** Size **S** (cone) or **M** (blade segment), risk **low**.
- `consumeAttackSweep` (`player.js:583-595`) should return a sweep every tick inside `[activeStart, activeEnd]`, carrying `move.arcHalfDeg`/`range`.
- The `game.js:709-743` loop skips enemies already in `this.hitSet` and adds `e.cfg.radius` to the range check at `:718`.

### P1: DS systems

**P1-1: Poise and hyperarmor.** Size **M**, risk **medium**.
- Add `poise`, `poiseMax`, `poiseRegenDelay` to `CONFIG.enemy.*` and `CONFIG.player`.
- `Enemy.takeDamage(amount, fromDir, poiseDmg)` (`enemy.js:282-302`) enters `stagger` only when poise ≤ 0; otherwise it's a flinch visual only (`staggerTimer`) with no FSM change, and it doesn't interrupt `attackPhase` if the enemy has hyperarmor.
- `Player.takeDamage` (`player.js:565`): if the player isn't in a `hyperArmor` window, cancel the attack and enter a `flinch` state of 0.3 s.
- Blocked hits pass `poiseDmg × chipFrac` (`04:118`) at `resolveIncomingHit` `:483-500`.

**P1-2: Stamina rules.** Size **S**, risk **low**.
- Gate on `stamina > 0` instead of `>= cost` (`:247`, `:519`), flooring at 0.
- Set a `staminaBroken` flag at 0 with a 0.5 s lockout (`04:137`).
- Suppress regen while `attacking` or `rolling` (`:619-626`).
- Move `staminaRegenDelay` toward 1.0 s (`CONFIG.js:228`) to match `04:139`; tune in the playable pass.

**P1-3: Critical attacks (riposte and backstab).** Size **M**, risk **medium**.
- In `tryAttack`, before `startAttack`, check candidates:
  - **riposte**: enemy `isStaggered()` (`enemy.js:278`) and `riposteArmed`, within 1.6 m, in front ±45°;
  - **backstab**: player inside enemy rear ±45° (using `enemy.yaw`), within 1.2 m, enemy not in `attackPhase` active.
- On a match, start a `crit` move: snap both positions, grant player i-frames for the full duration, freeze enemy FSM, and apply damage at the marker with ×3 (riposte) or ×2.5 (backstab), both in `CONFIG.block` or a new `CONFIG.crit`.
- Remove the passive ×1.75 at `game.js:726-729`.

**P1-4: Hitstop.** Size **S**, risk **low**.
- Add `game.hitstop` seconds. In `loop` (`game.js:660`), compute `simDt = hitstop > 0 ? 0 : dt` for the player and the struck enemy only; the camera keeps real `dt`.
- Trigger at `game.js:732` with 0.07 s for light and 0.1 s for heavy.
- Also make the shake at `:741` fire when unlocked, with a smaller amplitude.

**P1-5: Heavy attack verb** (`04:38`). Size **M**, risk **low**.
- Hold LMB for more than 0.3 s → `2h_heavy`. Track `mousedown`/`mouseup` time in `bindInput` (`player.js:179-200`); only the release path calls `startAttack`.

**P1-6: Guard pose and shield.** Size **S**, risk **low**.
- Add `roundShield` to the manifest (`assets.js:48-50`) and attach it to the offhand anchor when `offhand === 'shield'`.
- Add a `guard` pose for `weaponPivot` and the shield in the `!attacking` branch (`player.js:837-843`) while `blocking`.
- Make parry a short pose flourish lasting `parryWindow`, plus ~0.35 s of whiff recovery where block can't be re-pressed (a new `parryRecover` timer in `tryBlock` `:265-271`).

**P1-7: Roll feel.** Size **S**, risk **low**.
- Velocity curve (fast start, ease out) at `player.js:689`. `iframes` start after ~0.03 s.
- Equip-load tiers in `CONFIG.player.roll{light,medium,heavy}` (`04:143-146`).
- While locked, roll direction relative to the target (it already uses camera basis, which faces the target; verify).

**P1-8: Lock-on switching and framing.** Size **S**, risk **low**.
- While locked, a horizontal mouse flick of more than N px, or the wheel, calls a new `switchLockTarget(dir)` in `game.js` beside `pickLockTarget` (`:301-323`), choosing the nearest candidate by screen-space angle.
- Raise `camPitch` toward the target's head height when close (`player.js:861-884`).

### P2: robustness and depth

- **P2-1: Fixed-step simulation.** Use `CONFIG.loop.fixedTickHz` (declared, unused) with a 60 Hz accumulator in `loop` (`game.js:655-752`), so frame data is deterministic and testable. Size **M**, risk **medium** (all timing tests).
- **P2-2: Enemy verb set** (`04:148-157`). Bandit: 2-attack string with a delayed second hit, panic roll at low HP, strafe at range. Ghoul: lunge string. New `attackPhase` entries in `CONFIG.enemy.*`. Size **M-L**.
- **P2-3: Frame-data debug overlay.** A `WH_DEBUG.getFrameData()` hook plus an on-screen strip showing stage, markers, i-frames and hyperarmor. Size **S**. Prerequisite for the tuning pass in section 5.
- **P2-4: Rig pipeline spike (option c).** Rig `human-hunter-male.glb`; add `SkeletonUtils` to `vendor/`; in `loadOne` keep `gltf.animations` (`assets.js:159`); in `instance` use `SkeletonUtils.clone` for skinned templates (`:194`). Size **L**. Needs an art-direction ruling, since doc `04:31-33` and `04:482-498` assume sprites or no skeleton.

---

## 5. LIMITS: what static analysis can't verify

**What this read couldn't establish:**
- **Feel.** Whether 1.0 s 2H swings read as weighty or sluggish at this camera distance (`camDistance` 7) with rigid meshes. That needs playtests with the P2-3 overlay.
- **Real frame data.** The loop is variable-dt with a 50 ms clamp (`game.js:660`). Stage boundaries, the one-tick sweep (`player.js:585`) and i-frame edges shift with frame rate. Measure how long each stage actually lasts at 30, 60 and 144 fps.
- **Input latency.** DOM-event-to-state is immediate, but render lags by up to a frame. Measure input→first visible windup pose and parry press→first-tick `parryTimer` from captured timestamps.
- **The P0-1 weapon bug in practice.** Confirm by facing 180° from spawn and swinging (screenshot comparison).
- **The P0-3 combo bug in practice.** Confirm with an organic LMB×3 run logging `getCurrentMove()`.
- **Stunlock dynamics.** Player 0.5 s cadence vs enemy stagger 0.4 s plus an instant hit on re-entering attack. Measure the trade ratio.
- **Meshy auto-rig quality** on the pixelated or remeshed race GLBs. Unknown until a rigging spike.

**What the playable tuning pass must measure** (log with the P2-3 hooks):
1. Per move: windup, active and recover lengths in ms, plus actual combo, roll-cancel and buffer windows.
2. Roll: i-frame start and end in ms, distance, and recovery before the next action.
3. Parry: success rate against bandit and ghoul at the new windups; window 0.25 s vs 0.15-0.2 s.
4. Enemy telegraph read time: first telegraph visual → `activeStart`, which should be ≥ 400 ms for bandits.
5. Stamina: swings per full bar (now 6 at 15 cost; target 4-5 for 2H), regen-to-full time, stamina-break frequency.
6. Poise: hits to stagger each enemy type; whether player flinch feels fair against hyperarmor heavies.
7. Hitstop duration against perceived impact at 60 and 100 ms.
8. Lock camera: target on screen through a roll and strafe circle; switching success rate.
