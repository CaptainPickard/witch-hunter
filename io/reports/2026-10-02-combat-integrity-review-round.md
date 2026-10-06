# Witch Hunter — combat integrity review round (2026-10-02, IO)

Independent integrity review + implement/refactor executed by Claude Code
(Opus, effort max) as an uncommitted working tree on dev @ 8f777bb, gated by
IO review, rulings A-1/A-2 applied by IO, full validation ladder re-run, then
committed. Source deliverables (four files, verbatim below this preamble):
/tmp/cc_review_summary.md, /tmp/cc_review_findings.md,
/tmp/cc_review_refactor.md, /tmp/cc_review_results.md.

## IO addendum (post-review)

- Rulings: A-1 APPROVED (toggleLoadout calls endCombo(); spec-literal
  "recoverFullyElapsed=false" vacated — full text in the ds1 spec AMENDMENT
  A1+A2) and A-2 APPROVED as half-angle (hitArcDeg 50 applies as ±50°,
  Math.PI/180 at the active-entry gate). Both one-liners landed AFTER the
  reviewer's ladder, bundle rebuilt (9f31418367dc2511…, 2,417,818 B), and
  the FULL four-suite ladder was re-run on the post-ruling tree — results
  below.
- Deferred amendments: A-3 (corpse sink; must ship together with the
  wh_world_r1 A3 precise-box reader change), A-4 (spell hit-stagger scope;
  IO interim call: no hit-stagger from spells — Round B spec), A-5 (cast vs
  toggle/roll fizzle; IO interim call: in-flight casts survive — Round B
  spec).
- Post-ruling verification ladder (proc run 2026-10-02, /tmp/io_ladder_2.log):
  see the LADDER RERUN section at the end of cc_review_results.md below.

## LADDER RERUN (post-ruling, IO, 2026-10-02, /tmp/io_ladder_2.log)

| Suite | Result |
|---|---|
| ds1 wh_combat_ds1_validation.py | 17/18 then rerun 18/18 PASS (A1-4 yawAgree sampled-equality flicker, harness-env class per D2/D3; worstPair 0.0000 and 4/4 identical in both runs, rerun green, 0 crashes, no harness edit) |
| weave wh_v7_weave.py | V7 WEAVE: PASS (18/18, regress=True) |
| wh_v2_verify.py | V2 VERIFY: PASS |
| wh_v3_anim_probes.py | V3 ANIM PROBES: PASS (8791 and 8792 both ALL PROBES: PASS) |

Bundle after rulings: sha256 9f31418367dc251141243cff0017d6f5f0cc2a506258ae604cf28d8ae5abef89, 2,417,818 bytes.

---


## VERBATIM: /tmp/cc_review_summary.md

# CC review — executive summary (Witch Hunter combat surface)

Independent integrity review + implementation pass by Claude Code (Opus) on
/workspace/witch-hunter, branch dev, HEAD 8f777bb. Changes are left
**uncommitted** in the working tree for IO review: no commit, push, stash,
clean or restore.

## Starting state (recorded at session start)

- HEAD 8f777bb4b987; `git status --porcelain` outside io/ debris: **0
  entries**, so there were no pre-existing modifications to preserve. The 49
  untracked io/ debris entries were left untouched (still 49 at the end).

## Findings by severity

31 findings + 4 INFO (no-defect) review notes. Full table:
/tmp/cc_review_findings.md.

| Severity | Total | Fixed | Amendment proposed | WONTFIX (reasoned) |
|---|---|---|---|---|
| BLOCKER | 1 | 1 | 0 | 0 |
| MAJOR | 6 | 4 | 2 | 0 |
| MINOR | 14 | 5 | 3 | 6 |
| NIT | 10 | 4 | 0 | 6 |

Every BLOCKER and MAJOR was either fixed or, where the fix would change a
spec-literal value, recorded as an amendment proposal. Every fixed
behavioural finding was reproduced *before* the fix and re-verified *after*
it with an organic Playwright probe: real mouse and keyboard input, the real
enemy AI, WH_DEBUG writes only as setup.

## What shipped (uncommitted)

Files: prototype/js/player.js, enemy.js, game.js, anim.js, CONFIG.js
(comment only) and the rebuilt prototype/builds/v7-playable.html. Not
touched: assets.js, spells.js, moveset.js, region-manager.js, vendor/*, GLBs,
tests/, tools/, docs/, sui/.

1. **F-01 BLOCKER — organic guard break restored.** The v6 block path read
   `takeDamage()`'s "hp applied" return as "died", so guard break could never
   trigger in real play (broken since d06f659). Blocking at 0 stamina
   absorbed hits forever, and the weave rule "guard break clears armed" only
   held through debug hooks. The block path now uses the `guardBreak()` choke
   point; `WH_DEBUG.forceGuardBreak` delegates to it too (3 copies → 1).
2. **F-02 MAJOR — animation hit-latch.** A hit clip superseded by a swing
   never emitted `finished`, so locomotion froze and the player glided in the
   attack end pose. Fixed in `CharacterAnim.transition`.
3. **F-03 MAJOR — armed-finisher weapon pulse.** It was dead code because
   `p.sword` is a holder `Group` with no material. It now pulses every mesh
   material of the sword (weave §5 HUD requirement).
4. **F-04 MAJOR — comboIndex 3 leak.** A windup roll-cancel and a respawn
   after dying mid-chain produced comboIndex 3 with chainHits 3 (a single
   land armed the finisher), and on the stand-in path a TypeError every frame
   that skipped enemy update and render. New `endCombo()` closes the chain on
   those exits; the spec-literal fallback formula is untouched.
5. **F-05 MAJOR — stand-in strike sweep vs the D2 bound.** The strike
   progress formula ran over [-0.6, 0.4), so `atkYawOffset` reached
   -2.30 rad (theoretically -5.03) against the D2 item 6 bound ±1.2217 rad.
   It is now computed from the FSM clock: offsets +0.342/+1.124, max 0.78
   rad/frame. The skinned path holds `atkYawOffset ≡ 0`, so the D2 ruling now
   holds everywhere.
6. MINOR fixes:
   - F-08: a hit-stagger no longer leaves a stale `attackPhase`.
   - F-09: restored corpses no longer replay `WH_Death` after a region
     rebuild.
   - F-11: a refused low-stamina roll no longer cancels the swing.
   - F-12: one NaN position no longer poisons every enemy in the region
     through `separateFrom` (shown live on HEAD: all 3 enemies).
   - F-13: a missing death clip falls back to the rigid fall instead of
     throwing every frame.
7. Low-risk refactors (/tmp/cc_review_refactor.md): `endCombo`,
   `applyStrikeLunge` (2 copies → 1), stage progress from one `elapsed`, the
   guard-break choke point, angle-wrap helpers (5 loops), dead code
   (`pendingArmedMult`, `pushedBy` branch, identical ternary), and stale
   comments. Net lines: player +4, enemy +4, game -5, anim +4, CONFIG +2.

**Spec-pinned numbers: all preserved.** The FSM windows 0.7/0.12/0.8 and
0.45/0.12/0.5, hitArcDeg 50, track 180, 720/240, the 0.3/0 movement locks,
lunge 0.25, 1.5×/2.0×, 3.5 s armed, 0.8 s toggle, tax 1.25, dmg 12, heal 40
and cap 3 are unchanged. `WH_CONFIG` is JSON-identical to the pre-edit dump.
No harness edits (no HARNESS-FIX was needed), no vendored files, no GLBs, no
clip data.

## Verification (my runs; details in /tmp/cc_review_results.md)

| Suite (in order) | Result | Exit |
|---|---|---|
| wh_combat_ds1_validation.py | `total=18 pass=18 fail=0 crashes=0`, ZERO CRASHES: YES | 0 |
| wh_v7_weave.py | `V7 WEAVE: PASS (18/18 checks pass, regress=True)` | 0 |
| wh_v2_verify.py | `V2 VERIFY: PASS` (both origins, 26/26 GLB 200 each) | 0 |
| wh_v3_anim_probes.py | `V3 ANIM PROBES: PASS` (both origins) | 0 |
| build_v7.py ×3 | byte-identical e1240f8f5aea…, 2,417,454 B; CharacterAnim ×11; intake hook present; 13/13 inlined sources == dev sources | – |

- All green on the first attempt, no reruns and no adjudications needed.
- The bundle was rebuilt *before* the suites (ds1 and weave load it). The
  8791/8792 origins are pre-existing external servers (PIDs 614 and 6247,
  not started or stopped by me); I verified both serve this working tree
  byte-for-byte.
- Optional extra: wh_whanim3 (`WH_AC_SKIP_REGRESS=1`) passed AC1 (blade
  axis min +0.5164, unchanged from its round report), AC2, AC3 and AC5. Its
  AC6 scope census fails **by design**: that round forbids edits to
  CONFIG/game/anim, and it also flags the pre-existing `io/cc_opus_prompt.md`
  debris.

## Deliberately left (WONTFIX, reasons in the table)

- Round-B scope:
  - multi-enemy `chainHits` arming (P0-7);
  - windup/strike press buffer (P0-5).
- Outside the 8-file surface (world-R1 owned):
  - `disposeRegion` frees template-shared GPU resources and leaks skeleton
    bone textures;
  - a separation index skew.
- Stand-in-only cosmetics:
  - walk layers clobbered; the yaw term is now pinned by the D2 contract.
- Data-contract changes:
  - unused CONFIG/moveset keys (referenced by Round B/P2 plans).
- Presentation nits:
  - sprint clip on empty stamina;
  - 25 ms player clip-contact lead (changing it would invalidate the
    whanim3 mount measurement).
- Low-value robustness:
  - CSP header probe scope;
  - silent blob-fetch fallback;
  - lunge after the bounds clamp.

## Proposed amendments needing an IO ruling (not implemented)

- **A-1 (F-06, MAJOR):** `toggleLoadout` sets `recoverFullyElapsed=false`
  (spec-literal: weave FILE PLAN §3; ds1 P0-3 item 6 "keep as-is"). An idle
  toggle therefore starts the next chain at **m2** with chainHits 1, so the
  finisher re-arms after 2 lands. A toggle mid-swing gives m1, which is
  inconsistent. Probed on HEAD and on the fixed tree.
  Proposal: `endCombo()` in toggleLoadout. Weave AC6 reads only
  `{index, queued}`, so it is unaffected.
- **A-2 (F-07, MAJOR):** `hitArcDeg: 50` is applied as a full arc (±25°).
  The audit of record specified `arcHalfDeg 50` (±50°); D1 only renamed the
  key. Rule half vs full. A half-angle means `/360 → /180` in enemy.js:194;
  A3-6 is unaffected.
- **A-3 (F-10, MINOR):** skinned corpses sink 13–14 cm, because
  `corpseFinalY` uses the SkinnedMesh's cached bind-pose box. The precise
  fix must ship together with an IO-owned update of wh_world_r1 A3, which
  reads the same stale box and would otherwise go red.
- **A-4 (F-16, MINOR):** "no stagger from spells in this slice" vs
  `takeDamage` always hit-staggering. Every Firebolt staggers, so spam-casting
  can lock a bandit out of its windup. Clarify whether hit-stagger is
  excluded.
- **A-5 (F-15, MINOR, clarification):** a cast windup accepted before Q or
  Space still fires during the toggle busy window or the roll. Should
  toggle/roll fizzle an in-flight cast?

## Hygiene at hand-off

- HEAD 8f777bb unchanged, nothing staged, stash empty.
- Modified: exactly the 5 JS files plus the rebuilt bundle; tests/ is clean.
- Probe scripts and logs are in /tmp/cc_probe and /tmp/cc_review_*.log
  (outside the repo).


## VERBATIM: /tmp/cc_review_findings.md

# CC review — Phase 1 findings (Witch Hunter combat surface)

Reviewer: Claude Code (Opus), independent pass. Repo /workspace/witch-hunter,
branch dev, HEAD 8f777bb. **All file:line references are at HEAD 8f777bb**
(pre-edit). Severity: BLOCKER (core specced mechanic dead in real play) /
MAJOR (wrong behaviour on a reachable path, spec drift, or crash in a fallback
path) / MINOR (edge-case defect, hygiene with real effect) / NIT (comments,
dead code, style). Class numbers follow the assignment: 1 spec correctness,
2 structural integrity, 3 dead code / stale comments / duplication / unused
keys, 4 robustness, 5 refactor.

Evidence column: "probe" = organic Playwright probe on a private port (8797;
scripts in /tmp/cc_probe/, outside the repo). Acts were real mouse/keyboard
events and the real enemy AI; WH_DEBUG writes (teleport, setCameraYaw,
setStamina, killPlayer, stamina/armed levels right before a hit) were setup
only. Every FIXED row was re-probed on the fixed source with the same script.

## Summary counts

| Severity | Count | FIXED | AMENDMENT-PROPOSED | WONTFIX |
|---|---|---|---|---|
| BLOCKER | 1 | 1 | 0 | 0 |
| MAJOR | 6 | 4 | 2 | 0 |
| MINOR | 14 | 5 | 3 | 6 |
| NIT | 10 | 4 | 0 | 6 |
| INFO (reviewed, no defect) | 4 | – | – | – |

## Findings table

| ID | file:line (HEAD) | Sev | Class | Finding | Evidence | Verdict |
|---|---|---|---|---|---|---|
| F-01 | player.js:507-524 | **BLOCKER** | 1, 3 | **Organic guard break is unreachable.** The block branch stores `takeDamage(chip)` in `dead` and gates the break on `!dead`, but `takeDamage` returns *true when hp was applied* (it has since v1), so with chip applied the guard break never fires: blocking continues forever at 0 stamina. The inline break also skipped the weave rule "GUARD BREAK clears armedTimer/crossArmed" (only the debug paths went through `Player.guardBreak()`). Broken since v6 (d06f659). The weave AC9 only passed because it calls `P.guardBreak()` directly ("not reachable headless"). | probe (Q→loadout II, F lock, RMB hold, real bandit swings): 2 blocked hits drove stamina 4→0 (chip 2.4 hp), `guardBroken` false, 16 frames blocking at 0 stamina. After fix: same act → `guardBroken` true, blocking false, armed 2.95→0, cross true→false. | **FIXED** — block path calls the `guardBreak()` choke point when the post-hit state is alive and stamina is 0. |
| F-02 | anim.js:45-64 (+36-41, 73) | MAJOR | 2 | **Hit-reaction latch freezes locomotion.** If a `hit` clip is superseded (an attack starts, or the player swings while hit), the hit action fades out *disabled* and never emits `finished`, so `hitActive` stays true and `setLocomotion` never transitions again: the body glides in the clamped `WH_Attack1` end pose while walking, until some later hit plays out uninterrupted. Very common in play (trade hits, retaliating swings). | probe (real bandit hit during/just before real swings, then real W hold 2.5 s): 29 walking frames with `clip='attack'`, `hitActive=true`, all clip weights 0. After fix: `clip='walk'`, `hitActive=false`, then `WH_Idle` weight 1. | **FIXED** — `transition()` releases the latch whenever it moves to a non-hit state. |
| F-03 | game.js:202-223 | MAJOR | 1, 3 | **Armed-finisher weapon pulse never runs.** `p.sword` is the assets.js ground-align holder `Group`; it has no `.material`, so the weave §5 HUD item "weapon mesh emissive pulse while armedTimer>0" is dead code. The player gets no cue that the finisher is armed. | live: `sword.type='Group'`, `sword.material` undefined. probe (real 3-hit chain on the locked bandit, armed 10 frames): sword emissive `000000@1.00` throughout. After fix: `ff7722` pulsing 0.40→1.28. | **FIXED** — pulse the emissive of every mesh material under the holder (collected once, base restored on disarm). |
| F-04 | player.js:262-271, 959-988 (via 563-566) | MAJOR | 1, 2, 4 | **comboIndex escapes 0..cap-1.** A windup roll-cancel and a respawn after dying mid-swing both left `recoverFullyElapsed=false` and the old `comboIndex`, so the next press took the spec-literal fallback `min(comboIndex+1, cap)` → **3** from m3. `chainHits` is then pre-synced to 3, so the next *single* land arms the finisher. On the rigid stand-in path `[m1,m2,m3][3]` is undefined → `TypeError: reading 'windup'` every frame of that swing; `player.update` throws before enemies, sweep and render run. Violates ds1 §2 P0-3 item 5 ("comboIndex is now always 0..2 by construction") and the D1 index rule. | probe both mounts: after roll-cancel in the m3 windup and after respawn-from-mid-m3, the next press gave `ci 3 / chainHits 3`; stand-in run logged 5+ pageerrors. After fix: `ci 0 / chainHits 0 / recoverFullyElapsed true`, zero pageerrors. | **FIXED** — new `endCombo()` (same bookkeeping as the unchained full recover) is called on windup roll-cancel and in `respawnAt`; `respawnAt` also clears `attackTimer/attackDidHit/lungeLeft`. The spec-literal fallback formula itself is untouched. |
| F-05 | player.js:839-845 (+869-873) | MAJOR | 1, 2 | **Stand-in strike progress formula is wrong (D2 sweep bound violated).** `sp = (windupEnd + strikeSpan - attackTimer) / strikeSpan` equals real strike progress only if 2·windupFrac+strikeFrac = 1. With the configured 0.30/0.25 it runs over [-0.6, 0.4). So `atkYawOffset` sweeps -5.03..+0.34 rad (sampled -2.30 at 20 fps) against the D2 item 6 bound ±½·strikeYawSweepDeg = ±1.2217 rad (the "1.2 rad" entry step), recover entry jumps -0.34→+1.18, and the strike keyframe is never reached (`interpPose` clamps at 0.64). Present since v3 (5fe91c7, same fractions). Rigid stand-in path only; the skinned path holds `atkYawOffset≡0`, so D2 holds there trivially. | probe (player GLB route-aborted → stand-in): strike offsets -2.2969 / -0.3421, max per-frame Δ 2.30 rad. After fix: +0.342 / +1.124 (inside ±1.2217), continuous into recover (+1.18→0), max Δ 0.78. | **FIXED** — all three stage progresses are computed from FSM `elapsed` on `getAttackStage()`'s boundaries. Windup/recover expressions are operand-for-operand identical; sweep angle math and the 140° value are unchanged. |
| F-06 | player.js:331-342 | MAJOR | 1 | **An idle loadout toggle starts the next chain at m2.** `toggleLoadout` sets `recoverFullyElapsed=false`, so the first post-toggle press is `comboIndex 1` with `chainHits` pre-synced to 1. The finisher re-arms after 2 lands instead of 3, and the result is inconsistent with a toggle *during* a swing (the swing end sets the flag true, giving m1). This contradicts "toggle resets the chain" and the 3-hit arming rule, but the flag value is spec-literal (weave FILE PLAN §3 "recoverFullyElapsed=false"; ds1 P0-3 item 6 "keep as-is (verify only)"). | probe on both pristine HEAD and the fixed tree (identical, since toggleLoadout is untouched): after a full swing (`ci 0, rfe true`), a real Q toggle gives `getCombo()={0,false}` with `rfe=false`; the first real LMB after the busy window → `comboIndex 1, chainHits 1`. | **AMENDMENT-PROPOSED (A-1)** — set `recoverFullyElapsed=true` (+`chainHits=0`), i.e. call `endCombo()`, in `toggleLoadout`. Weave AC6 reads only `{index, queued}`, so it is unaffected. |
| F-07 | enemy.js:194 | MAJOR | 1 | **Enemy hit-cone semantics drift.** The code treats `hitArcDeg: 50` as a *full* arc (\|Δ\| ≤ 25°). The audit of record (doc 60 L221) specified `arcHalfDeg (50)`, i.e. ±50°. D1 only renamed the key to match the frozen harness, and ds1 §2 P0-6 says "inside `hitArcDeg` of `this.yaw`". The effective enemy hit cone is half of what the audit specified. | code + spec text. A3-6 (teleport *behind*) passes under either reading. | **AMENDMENT-PROPOSED (A-2)** — IO to rule. If a half-angle was meant: `Math.PI / 360` → `Math.PI / 180`. The value 50 is spec-pinned, so this was not changed unilaterally. |
| F-08 | enemy.js:397-419 | MINOR | 2 | `takeDamage` → stagger/death left `attackPhase/attackPhaseT` stale (`'windup'` while `fsm='stagger'`), unlike `enterStagger` (ds1 P0-6 item 7 "no phase leak"). Gameplay is gated on `fsm`, but harness and debug readers saw a phantom windup. | probe: hit during the real windup → `stagger/windup`. After fix: `stagger/idle`. | **FIXED** |
| F-09 | anim.js:89-98, 140-142; enemy.js:90 | MINOR | 2 | **Restored corpses replay their death.** On a region rebuild, region-manager restores dead enemies with `deadFall=1`, but `death(alreadyDead)` had no caller, so the corpse stood up and replayed `WH_Death` in front of the player. | probe (kill bandit-0, v2's teleport round-trip A→B→A): death clip time 0.2→1.15 replayed. After fix: 1.2 (clip end) from the first frame. A fresh kill still plays from 0.05. | **FIXED** — restored corpses pass `alreadyDead`; zero-fade jump to the end. |
| F-10 | enemy.js:93-100 | MINOR | 2 | **Skinned corpses sink 13–14 cm.** `corpseFinalY` uses the non-precise `Box3`, which for a SkinnedMesh reuses the cached bind-pose box (r185 `expandByObject` plus `SkinnedMesh.copy` cloning it). Every skinned corpse therefore gets 0.01 while its true skinned min Y is negative. | probe: bandit `corpseFinalY 0.01`, precise skinned min Y -0.144; ghoul 0.01 / -0.132. | **AMENDMENT-PROPOSED (A-3)** — the precise fix would lift corpses about 0.15 m, and wh_world_r1 A3 "corpse ground-align" reads the *same stale* box (\|minY\| ≤ 0.05), so it would go red. Ship together with an IO-owned move of that reader to a precise box. |
| F-11 | player.js:262-271 | MINOR | 1 | `tryRoll` cancelled the windup *before* checking roll stamina, so a refused roll (<25) still threw away the swing (no roll, lost attack and stamina). | code path. After fix, probe: stamina 2.4, Space in windup → `attacking` true, `rolling` false. | **FIXED** (gates reordered) |
| F-12 | enemy.js:423-440 | MINOR | 4 | `separateFrom` let one NaN position (the historical dy/dz harness poke; D3 H1 traced NaN writers to this function) spread to every neighbour, because a NaN `d2` passes both guards. Also a dead `o.pushedBy` branch (nothing sets it). | probe (setup: bandit-0 `pos.z = NaN`, bandit-1 placed beside it): on pristine HEAD, within 2.5 s **all three** region enemies had NaN x and z, because a NaN distance also skips the "too far" early-out, so even the distant ghoul was poisoned. Fixed tree: only bandit-0 z is NaN; bandit-1 and the ghoul stay finite. | **FIXED** — `!(d2 > 0 && d2 < minDist²)` (identical for finite input); dead branch removed. |
| F-13 | enemy.js:93 | MINOR | 4 | `updateDeathVisual` dereferenced `anim.actions.death` unconditionally. A rig without `WH_Death` (CharacterAnim only warns) would throw every frame, so the loop would skip render. Latent: the frozen GLBs carry all 6 clips. | code | **FIXED** — falls back to the rigid fall. |
| F-14 | player.js:884-890 | MINOR | 2, 3 | Stand-in walk layers (lean, counter-roll, yaw-osc, sway) from `setBodyBob` are zeroed every frame by the not-attacking reset branch; only the vertical bob survives. Pre-existing since v3. | probe (stand-in, real W): bx/bz/by/px all exactly 0 over 14 walk frames. | **WONTFIX** — stand-in-only cosmetics. The yaw term is now what D2 item 6 pins (`body.rotation.y == atkYawOffset`), and the v3 suite retired procedural-bob evidence (D-A12-1). |
| F-15 | game.js:676-689; player.js:262, 331 | MINOR | 1 | A cast windup accepted *before* Q or Space still completes during the toggle busy window or the roll (bolt spawns, focus spent). The weave spec gates only cast *entry*. | code | **AMENDMENT-PROPOSED (A-5, clarification)** — should toggle/roll fizzle an in-flight windup (no focus spent)? |
| F-16 | spells.js:69; enemy.js:397-419 | MINOR | 1 | "No stagger from spells in this slice" (weave FILE PLAN 4, spells.js header) vs `Enemy.takeDamage`, which always enters the hit-stagger state with knockback. Every Firebolt staggers (0.4 s bandit), and a 0.55 s cast cycle can keep a bandit out of its 0.7 s windup. The spec may have meant only the v6 parry stagger (`enterStagger`, which spells never trigger). | code | **AMENDMENT-PROPOSED (A-4)** — IO to rule. If hit-stagger is excluded, add a no-stagger option for spell damage. |
| F-17 | game.js:743-746 | MINOR | 1 | `chainHits` increments per *enemy* hit, so one swing hitting 3 enemies arms the finisher. | code; ds1 §8.6 | **WONTFIX** — known, Round B P0-7 (hitSet) scope per ds1 §8.6. |
| F-18 | region-manager.js:371-390 | MINOR | 4 | `disposeRegion` disposes geometry/materials/textures shared with the asset templates (props `clone(true)`, characters `SkeletonUtils.clone`), forcing re-upload and recompile for the surviving region's instances. Skinned skeleton bone textures are never disposed (small GPU leak per rebuild). | code | **WONTFIX** — outside the 8-file combat surface (world-R1 owned; its suite asserts disposal). Recommend template-aware/refcounted disposal plus `skeleton.dispose()`. |
| F-19 | anim.js:135 | MINOR | 2 | `setLocomotion` gets `player.sprinting` (Shift held), not the effective sprint, so with empty stamina it plays a slow-motion `WH_Run` at walk speed. | code | **WONTFIX** — presentation-only; would need a new player→anim field; v3 owns locomotion bars. |
| F-20 | CONFIG.js:230, 320/340, 325/345, 389, 392, 439, 450-451; moveset.js:3-40 | MINOR | 3 | Unused config/moveset data: `anim.attack.windupSwordRaise/strikeSwordSweepDeg`, `enemy.*.aggroPingInterval`, `enemy.*.attackCooldown` (legacy since P0-6), `loop.fixedTickHz`, `moveset.banditStageMult/enemyWeapon`, `player.hpRegenPerSec`; moveset `m4/claw`, per-move `recover/bodyLean/crouch/lunge`, `WH_MOVESET.chainCap`. Non-combat: `boundary.xMin/xMax/wallHeight`, `chokepoint.markerScale`, `hud.deathFadeSeconds`, `world.fogNear/FarFactor`. | static scan (no reader in js/ or tests/) | **WONTFIX** — the audit and the Round B (P0-2) / P2-1 plans reference them, so removal is a data-contract change, not a review fix. |
| F-21 | assets.js:166-176 | MINOR | 4 | The CSP probe reads only `connect-src` (no `default-src` fallback, no `<meta>` CSP) and GETs the whole page (2.4 MB for the single-file build) just for headers. | code | **WONTFIX** — no tested route is affected (8787 sends `connect-src`; 8791/8792 send none). A default-src-only policy would block `data:` images as well, so a fallback alone wouldn't help; HEAD risks servers without HEAD support. |
| F-22 | player.js:1-6, 116-118, 316-317, 606-608; game.js:642; enemy.js:132-135; CONFIG.js:381-382 | NIT | 3 | Stale comments: "hard yaw track", "assets are unrigged", "inner holder", "hit lands midway", guardBreak "called via onGuardBreak", "register the sword so attack stages drive its pose", callback "returns true if it landed". | code | **FIXED** |
| F-23 | player.js:551 | NIT | 3 | Dead field `pendingArmedMult` (written, never read). | grep | **FIXED** (removed) |
| F-24 | enemy.js:216-219 | NIT | 3 | Identical-branch ternary (`'idle' ? 'aggro' : 'aggro'`) and an empty `else if`. | code | **FIXED** |
| F-25 | player.js:485-490, 859-866 & 893-899; enemy.js:179-192; game.js:315-318, 726-729, 509-519 | NIT | 3, 5 | Duplicated logic: angle-wrap loops (player.js re-implements `shortestAngle` in the same file), lunge math ×2, guard-break block ×3, chain-reset bookkeeping. | code | **FIXED** (refactor, see cc_review_refactor.md) |
| F-26 | game.js:493 | NIT | 3 | `WH_DEBUG.getCurrentMove` keeps the `\|\| MS.m1` fallback, which masked the comboIndex-3 state in debug reads. | code | **WONTFIX** — debug-hook compatibility; comboIndex is now 0..2 by construction. |
| F-27 | enemy.js:308-310 | NIT | 3 | Stand-in visual: `body.rotation.y = 0` is overwritten 30 lines later, and `if (this.fsm !== 'dead')` is always true there. | code | **WONTFIX** — cosmetic, stand-in path. |
| F-28 | player.js:754-780 | NIT | 2 | During strike/recover with a move key held, speed is 0 but `moveDirWorld` still updates, so camera auto-follow keeps orbiting a frozen body. | code | **WONTFIX** — camera feel; P0-4 pins movement only. |
| F-29 | player.js:893-899 | NIT | 4 | The strike lunge is applied after `clampToBounds`, so it can sit up to one step (≤0.1 m) past the boundary for a frame. | code | **WONTFIX** — pre-existing order that the A4-2 lunge/freeze bars were validated against; kept exactly. |
| F-30 | anim.js:100-108 | NIT | 2 | The player clip seek is linear (clip 0.5 s = attackDuration), so `WH_Attack1` contact (strike fraction 0.25 → 0.125 s) leads the FSM strike start (0.15 s) by 25 ms. Enemies use the per-phase seek. | code | **WONTFIX** — changing it would invalidate the whanim3 measured mount (AC1 blade-axis bars). |
| F-31 | assets.js:214; region-manager.js:430-439 | NIT | 4 | (a) The permissive-origin `fetch(blob)` failure falls back to FileReader silently. (b) The circle list skips dead enemies but self-exclusion splices `k+1`, so with a dead lower-index enemy one neighbour pair separates one-sided. | code | **WONTFIX** — (a) designed fallback with an identical result; (b) outside the combat surface. |
| I-1 | player.js:128-161; enemy.js:49-84 | INFO | 2 | Dual weapon paths reviewed. Skinned (R_Hand socket, `weaponPivot` undefined, `resetWeaponPose` no-op, mount quaternion computed once from the rest hand) and stand-in (pivot under `yawFrame`) are mutually exclusive by `this.anim`. A rig with clips but no R_Hand gets an un-posed pivot (acceptable). The bandit axe on the socket is verified-correct (whanim3 AC2) and untouched. | code + live (`anim:true, hand:true, pivot:false`) | no change |
| I-2 | player.js:532-540, 700-716 | INFO | 4 | Combo-buffer race review. DOM-event presses read the last update's stage. Recover presses are consumed on every recover frame including the final one. Windup/strike presses are dropped by spec (Round B P0-5 TTL buffer). A chain point short on stamina retries until the swing ends, then drops. Toggle clears `comboQueued`. No new race found. | code + ds1 A2-1/A2-2 | no change |
| I-3 | all 8 files + region-manager | INFO | 4 | NaN / cfg-key audit. Every CONFIG key path read by the code resolves in the live `WH_CONFIG` dump (static extractor vs live JSON). All physics divisions are guarded or use constant denominators. The ds1 harness `run_sampler` maps `dy`→`dz`, and every JS-read cfg key (`displace/dx/dz/yawSweep/yawRate`) is provided. | /tmp/cc_probe/keycheck.py | no defect beyond F-12 |
| I-4 | player.js:643-716, 772-780; enemy.js:173-213 | INFO | 1 | Spec-number audit (unchanged by this pass). bandit 0.7/0.12/0.8, ghoul 0.45/0.12/0.5, hitArcDeg 50, track 180; 720 windup turn / 0 strike-recover; lock 240 windup-only; move ×0.3 windup / ×0 strike-recover; lunge 0.25 velocity model; 1.5×/2.0×; armed 3.5 s; toggle 0.8 s; tax 1.25; dmg 12; heal 40; cap 3 — all match the specs. `WH_CONFIG` post-edit is JSON-identical to the pre-edit dump. | live config diff | no change |


## VERBATIM: /tmp/cc_review_refactor.md

# CC review — refactor log (within-file consolidation only)

Rules followed: each change stays inside one file (one-line call-site
adjustments in anim.js/enemy.js for F-09 are fixes, not architecture). No
spec-pinned timing or math value changed. `WH_CONFIG` after the edits is
JSON-identical to the pre-edit dump (live check). Vanilla-JS law: IIFE +
window globals, `var`, function expressions; a scan of added lines found no
`=>`, `?.`, `??`, `let`, `const` or `class`.

## Ranked refactor opportunities (value / risk) and disposition

| Rank | Refactor | Value | Risk | Done? |
|---|---|---|---|---|
| R1 | player.js: `Player.prototype.endCombo()` — one chain-close routine (recoverFullyElapsed=true, comboIndex=0, chainHits=0, comboQueued=false) used by the unchained full recover, windup roll-cancel and `respawnAt` | High: the copy that was missing from two exit paths caused F-04 | Low: same assignments, same order as the existing full-recover block | **Yes** |
| R2 | player.js: `resolveIncomingHit` uses the `guardBreak()` choke point; game.js `WH_DEBUG.forceGuardBreak` delegates to it (3 copies → 1) | High: the inline copy is where F-01 lived, and it skipped the armed clear | Low: `guardBreak()` makes the same writes in the same order, plus the weave-mandated armed/cross clear | **Yes** |
| R3 | player.js: `Player.prototype.applyStrikeLunge(dt)` — the velocity-model lunge was written twice (stand-in strike branch + clip path). One helper, one call site after the pose block | Medium | Low: identical arithmetic; both old copies already ran after `clampToBounds`, and the pose block never reads `pos` | **Yes** |
| R4 | player.js: stand-in pose block computes `elapsed / windupEnd / strikeEnd` once; windup, strike and recover progress all derive from them | Medium: removes the third formula variant that hid F-05 | Low: windup/recover expressions are operand-for-operand identical; only the (wrong) strike progress changes | **Yes** |
| R5 | Angle wrap: player.js `resolveIncomingHit` re-implemented `shortestAngle` (same file); enemy.js ×2 → local `wrapAngle`; game.js ×2 → local `wrapAngle` | Low–medium | Low: same `while` loops; `deg2rad(x)` is the same `x*PI/180` expression | **Yes** |
| R6 | Dead-code removal: `pendingArmedMult` (player.js), `o.pushedBy` branch (enemy.js `separateFrom`), identical ternary + empty `else if` (enemy.js) | Low | None | **Yes** |
| R7 | Collapse the duplicated idle pose (`WH_MOVESET.idle` vs `CONFIG.moveset.idlePose`, `WH_MOVESET.chainCap` vs `CONFIG.moveset.comboChainCap`) | Low | Medium: cross-file; harnesses and debug read both | No (cross-file data contract) |
| R8 | Remove unused CONFIG/moveset keys (F-20) | Low | Medium: audit and Round B/P2 plans reference them | No |
| R9 | Remove the always-true `if (fsm !== 'dead')` in the enemy stand-in visual block (F-27) | Very low | Low, but it re-indents ~55 lines for nothing | No |
| R10 | Template-aware/refcounted disposal in region-manager (F-18) | Medium | Medium: region-manager.js is outside the combat surface, and the world-r1 suite asserts disposal | No |

## Before / after line counts (wc -l)

| File | Before (8f777bb) | After | Δ | git numstat |
|---|---|---|---|---|
| prototype/js/player.js | 990 | 994 | +4 | +64 / -60 |
| prototype/js/enemy.js | 443 | 447 | +4 | +25 / -21 |
| prototype/js/game.js | 783 | 778 | -5 | +34 / -39 |
| prototype/js/anim.js | 189 | 193 | +4 | +6 / -2 |
| prototype/js/CONFIG.js | 452 | 454 | +2 | +4 / -2 (comment only) |
| prototype/js/assets.js | 317 | 317 | 0 | untouched |
| prototype/js/spells.js | 97 | 97 | 0 | untouched |
| prototype/js/moveset.js | 48 | 48 | 0 | untouched |

Net code size is roughly flat. The refactors removed about 40 lines of
duplicated logic (two lunge copies, three guard-break copies, five wrap
loops, chain-reset copies, dead branches), and the fixes plus their
explanatory comments added back about the same.

## Per-file notes

- player.js: R1, R2, R3, R4, R5, R6 plus fixes F-01, F-04, F-05, F-11 and
  stale comments (F-22).
- enemy.js: R5, R6 plus fixes F-08, F-09 (call site), F-12, F-13 and the
  callback-contract comment.
- game.js: R2 (debug-hook delegation), R5, plus fix F-03 (armed pulse over
  the holder's mesh materials, collected once and restored on disarm) and a
  boot comment.
- anim.js: fixes F-02 (latch release in `transition`) and F-09 (zero-fade
  `alreadyDead` path, `syncEnemy` passes the restored-corpse marker).
- CONFIG.js: comment-only change (stale "assets are unrigged" note). No
  value edited.


## VERBATIM: /tmp/cc_review_results.md

# CC review — verification results (my own runs, 2026-10-02)

Tree under test: HEAD 8f777bb plus this review's uncommitted edits
(player.js, enemy.js, game.js, anim.js, CONFIG.js [comment only] and the
rebuilt prototype/builds/v7-playable.html). Full logs:
/tmp/cc_review_{ds1,weave,v2,v3,whanim3}.log.

## Ordering note

ds1 and weave load `builds/v7-playable.html`, so the bundle was rebuilt
(`python3 tools/build_v7.py`) after the last source edit and BEFORE the
suites ran; otherwise they would have tested the pre-fix code. After the
suites I re-ran the build twice to prove byte-identity (see below).

## Environment note (serving origins)

8791 and 8792 were already being served by long-running external processes
that I did not start and did not stop:

- PID 614 `python3 prototype/server.py 8791` (since 03:11)
- PID 6247 `/tmp/tb_start_8792.py` (since 03:47; the weave harness's own
  `start_proxy_server`)

The harnesses' own server spawns fall back to these by design. Both
processes have cwd `/workspace/witch-hunter` and read from disk per request.
Verified by hashing the served bytes against the working tree:
`builds/v7-playable.html` e1240f8f5aea, js/player.js 32c6a42e5b7d,
js/anim.js 4eaff96ef99d, js/game.js 4faf8c8ca31a, js/enemy.js d6992e61c15d.
All MATCH on both origins, so every suite exercised this review's code. My
own probe server (8797) was used only for probes and is shut down.

## Step 1 — py_compile

`python3 -m py_compile tests/wh_combat_ds1_validation.py tests/wh_v7_weave.py
tests/wh_v2_verify.py tests/wh_v3_anim_probes.py tests/wh_whanim3_validation.py
tools/build_v7.py` → OK (exit 0), run both before and after the suites. I
edited no Python file in the repo; the touched files are JS, verified by
runtime boot instead.

JS syntax/runtime check: the source `index.html` and the rebuilt bundle both
boot in headless chromium with zero pageerrors and zero console errors.
`WH_CONFIG` after the edits is JSON-identical to the pre-edit dump, and a
scan of added lines finds no `=>`, `?.`, `??`, `let`, `const` or `class`.

## Step 2 — the four required suites, IN ORDER (all green, first attempt, no reruns)

| # | Suite | Summary line (verbatim) | Exit | Wall |
|---|---|---|---|---|
| 1 | `python3 tests/wh_combat_ds1_validation.py` | `COMBAT-DS1-A SMOKE SUMMARY  total=18 pass=18 fail=0 crashes=0` / `ZERO CRASHES: YES` | **0** | 4m14s |
| 2 | `python3 tests/wh_v7_weave.py` | `V7 WEAVE: PASS (18/18 checks pass, regress=True)` (its AC14 ran v2 exit 0 "V2 VERIFY: PASS" and v3 exit 0) | **0** | 6m30s |
| 3 | `python3 tests/wh_v2_verify.py` | `V2 VERIFY: PASS` (root and proxy: 9/9 checks each; ASSET AUDIT 26 glb fetches, non-200 [] on both) | **0** | 0m56s |
| 4 | `python3 tests/wh_v3_anim_probes.py` | `V3 ANIM PROBES: PASS` (8791 ALL PROBES: PASS, 8792/witchhunter ALL PROBES: PASS) | **0** | 3m26s |

Selected per-AC evidence lines (from the logs):

- ds1 A1-1 maxDyaw 0.2095, no jump. A1-2 maxDrift 0.0000. A1-3
  maxBodyDelta 0.0000. A1-4 worstPair 0.0000, offsets 4/4. A2-1 [0,1,2].
  A2-2 [0,1,2,0], no requeue. A2-3/A2-4 ci 0. A3-1 first drop at active
  entry. A3-2 periods 30,33 frames. A3-3 hpDrops=2. A3-4 arc 2.741, mono.
  A3-5 hp unchanged through active. A3-6 no rear-arc damage. A4-1 srDrift
  0.0000. A4-2 windupDist 0.270, recFrozen 0.00000. A4-3 in-swing drift
  0.0000. A4-4 720/240/attackPhase exact.
- weave AC3 spent=10.00 (8×1.25), dmg=12.0. AC6 combo {0,false}, armed
  survives, busy refused. AC7 timer 3.10, ratio 1.50. AC8 xratio 2.00
  consumed. AC9 {timer 0, cross False}. AC10 heal 40.0. AC13 console=[]
  page=[].

Adjudications needed: **none**. No failure occurred, so no harness-artifact
or regression adjudication was required, and no harness file was edited.

## Step 3 — build byte-identity (`python3 tools/build_v7.py`)

| Run | When | sha256 | Bytes |
|---|---|---|---|
| pre-review (HEAD) | before edits | 864d0d5bb294… | 2,416,462 |
| build 1 | after the last source edit, before the suites | e1240f8f5aea44745e123af545aab3b642294bd9fde88e4a0b73bf3930a9dad9 | 2,417,454 |
| build 2 | after all four suites | e1240f8f5aea44745e123af545aab3b642294bd9fde88e4a0b73bf3930a9dad9 | 2,417,454 |
| build 3 | immediate rerun | e1240f8f5aea44745e123af545aab3b642294bd9fde88e4a0b73bf3930a9dad9 | 2,417,454 |

- Byte-identity with itself on rerun: **YES** (3/3 identical; also
  independently confirmed by wh_whanim3 AC5-ident: on-disk ==
  scratch-rebuild e1240f8f5aea4474).
- Contains `CharacterAnim.prototype` ×11, and the intake hook
  `setURLModifier` sits inside the WHGLTFLoader/WH_ASSETS context (plugin
  `WH_embedded_image_data` ×1). Markers present: startAttack ×3,
  attackPhase ×49, endCombo ×4, applyStrikeLunge ×2, swordEmissives ×5.
- All 13 inlined `<script>` blocks are byte-equal to the dev sources
  (index.html script order). Title "Witch Hunter v7 - Weave Slice".

## Extra (not required): wh_whanim3_validation.py, `WH_AC_SKIP_REGRESS=1`

`WHANIM3 SMOKE SUMMARY  total=5 pass=4 fail=1 crashes=0`, exit 1 (its AC4
regression floor = the four suites above, run directly instead).

- AC1 blade orientation PASS: axisDot min +0.5164, mean +0.6381, tip leads,
  idle 17.6°. These are the same numbers the whanim3 round report recorded,
  so the mount is unaffected.
- AC2 bandit axe PASS (entryHeadDot 0.3239, telegraph 0.868→0.608 mono).
- AC3 8787 CSP intake PASS (cspErrors 0, map 2048, zero stand-ins).
- AC5 build freshness PASS.
- AC6 scope-drift FAIL **by design, not a regression**: that round's census
  hard-fails any edit to CONFIG.js / game.js / anim.js ("ZERO edits ... for
  whanim3"). This review was assigned exactly those files. The census also
  lists `io/cc_opus_prompt.md`, which was pre-existing untracked io/ debris
  at session start (not created by me).

## Organic probe evidence (before → after, /tmp/cc_probe/*.py)

| Finding | Before (HEAD) | After (fixed) |
|---|---|---|
| F-01 guard break | stamina 4→0 on a blocked hit, guardBroken false, 16 frames blocking at 0 stamina | guardBroken true, blocking false, armed 2.95→0, cross→false |
| F-02 hit latch | 29 walk frames in clip `attack`, hitActive true | clip `walk`, hitActive false, idle weight 1 |
| F-03 armed pulse | emissive 000000@1.00 while armed | ff7722 @ 0.40–1.28 pulsing |
| F-04 comboIndex | roll-cancel/respawn → ci 3, chainHits 3; stand-in TypeError ×5+ | ci 0, chainHits 0, no pageerrors |
| F-05 stand-in sweep | strike offsets -2.2969/-0.3421, maxΔ 2.30 rad | +0.342/+1.124 (≤1.2217), maxΔ 0.78 |
| F-08 enemy phase | `stagger/windup` | `stagger/idle` |
| F-09 restored corpse | death clip replays t 0.2→1.15 | t = 1.2 from the first frame; fresh kills still play from 0.05 |
| F-11 refused roll | (code path) | stamina 2.4 + Space in windup → swing kept, no roll |
| F-12 NaN spread | one NaN → all 3 region enemies NaN | contained to the poisoned enemy |
| F-06 (amendment) | idle Q toggle → first press ci 1 / chainHits 1 | unchanged (spec-literal, not edited) |
| F-10 (amendment) | skinned corpses: corpseFinalY 0.01 vs true min Y -0.144 / -0.132 | unchanged (would flip world-r1 A3) |

