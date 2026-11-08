# ASTRABOT MISSION BRIEF - Order E: lock-on camera reframe + light-gated targeting
2026-10-05, from IO. Nicko's orders (10-05, D batch approved playtest):
- "When I lock on, the camera zooms into the enemy, going above the player, the
  player character nearly goes out of camera view. It would be great if the
  player character stayed in view and this zooming in didn't happen."
- "I want to make the lockon something that only can happen in light. So light
  radius should have a part to play in whether or not you can even lock onto an
  enemy. If you can't see them, then they shouldn't be anticipated or targeted."
- After this order: stage 2 (enemy drops + world gathering).

You are Astrabot, Claude Code print-mode agent, worktree /tmp/wh-worldfeat
(branch feat/world-visuals). Commits + pushes per sub-block as usual.

## 0. LAWS (hard)
- NO automated harness or headless-browser runs of any kind. Nicko's playtest
  is the ONLY acceptance test.
- One order at a time. Every tunable from CONFIG. No new assets/Meshy/Blender.
- Block/parry mechanics and Order D clips: DO NOT TOUCH.
- Magic canon + light canon stand (earned light only; light.js exists).

## 1. NICKO'S RULINGS (10-05, binding - IO defaults, form timed out)
1. CAMERA: locked camera anchors BEHIND THE PLAYER at the normal orbit
   distance/pose (unlocked framing); lock changes ONLY the yaw aim so the
   enemy stays ahead of you in frame. NO midpoint re-anchor, NO extra zoom
   (camExtraDistance retired from the orbit path), player stays in view
   exactly like unlocked play. Pitch stays whatever the player had.
2. Moonlight does NOT enable lock. Only REAL light: player hand lights
   (firebolt binding), Radiance cast follow-lights, and WORLD FIRE lights
   (braziers/lantern posts/fireplace pool - the R2 flame-card lights).
3. Lock BREAKS immediately when the target leaves your light (same path as
   the distance break). No grace period.
4. The gate is one-directional: unlit enemies still track/attack you normally.
   Enemy AI NOT changed, stealth not built.

## 2. Current mechanics (verified by IO - do not re-research)
- CONFIG.lockOn (CONFIG.js:632): maxDistance 18, hysteresis 1.25,
  facingConeDeg 140 (around CAMERA forward), camLerp 6, trackWindupDegPerSec
  240, camExtraDistance 3.5, reticleOffsetY 0.9.
- player.js updateCamera (~1500): lock branch re-anchors target to the
  MIDPOINT between player/enemy with offset distance midDist +
  camExtraDistance - the midDist term is the zoom-above-player bug.
- game.js: setLockTarget (~532-548) picks target (nearest-in-cone logic),
  breakLockOn, reticle positioning (554+), break on player death (488).
- light.js (WH_PlayerLight): per-hand binding lights + projectile pool;
  game.radiances[] = cast follow-lights (60s, fade); R2 flame-card pool =
  4 fixed PointLights at world fire props. NO unified "lights registry" yet.
- The walking-latch bug class: any new gating MUST be re-checked against
  syncPlayer starvation patterns (no latch flags; D9 discipline).

## 3. WORK ORDER E1 - camera reframe (player.js)
Replace the lock camera branch: anchor = player pos + camHeight as normal;
yaw = aim at the enemy (smooth via the existing lerp); distance/pitch =
EXACTLY the unlocked orbit path (reuse the same clamp code incl. the R5
pitch-distance cap + ground floor). camExtraDistance: move to
CONFIG.lockOn.camExtraDistance with value 0 and a comment (legacy key kept),
or delete if cleaner - your call, report it. Reticle positioning stays
(554+ still frames the enemy). Verify the enemy stays IN FRAME: at max
locking distance (18m) with default pitch, the enemy must be visible -
add a CONFIG.lockOn.frameCheckNote in comments, playtest is the real gate
(AC E2).

## 4. WORK ORDER E2 - light registry + lock gate (light.js/game.js)
1. light.js: add a LIGHTS registry (static, rebuilt on demand):
   collectLockLights() returns live light sources as {x, z, radius, kind}:
   - kind 'spell': per-hand binding lights when ON (radius = light.distance
     * CONFIG.light.lockRadiusFactor, default such that firebolt's distance
     12 maps to a sensible lock radius ~9-10m; tunable)
   - kind 'radiance': each live game.radiances[] light (radius from its
     CONFIG radius * factor)
   - kind 'world': R2 flame pool lights when lit + any def-based world fire
     lights (braziers, lantern posts) - read their current intensity/burning
     state (region manager holds these).
2. isInLitArea(x, z): point-in-any-light test (spell + radiance + world).
3. setLockTarget gating: a candidate is lockable ONLY if
   isInLitArea(enemy.x, enemy.z) is true. Show the standard refusal (reticle
   blink/hud note - reuse the empty-feedback path if one exists; else a
   brief 'Too dark to target' HUD note, CONFIG string).
4. Lock maintenance: each frame while locked, if
   !isInLitArea(target.x, target.z) -> breakLockOn() (immediate, no grace).
5. Performance: collectLockLights is a small array rebuild (few dozen
   entries max) - recompute each frame is fine on swiftshader, but if the
   pool/fade paths make it chatty, cache per 0.25s (CONFIG.lockOn.
   lightCheckIntervalSec, default 0 for every frame). Keep it simple.

## 5. ACCEPTANCE CRITERIA (Nicko playtests)
| AC | Test |
|---|---|
| E1 | Lock-on: camera swings to keep the enemy ahead of you, but YOUR camera distance/height/pitch feel IDENTICAL to unlocked play - you stay framed (no zoom-above) |
| E2 | Enemy at 18m still in frame while locked |
| E3 | Lock attempt on a lit enemy (your firebolt hand lights them or near a brazier): locks and holds |
| E4 | With NO glove (dark, only moon): lock-on refuses everywhere |
| E5 | Near a brazier/lantern (world fire): lock works there without any glove |
| E6 | Radiance cast (light on you): lock works while the light lives; refuses again after it fades |
| E7 | Locked enemy steps out of your light: lock breaks immediately |
| E8 | Retreat: break distance (hysteresis) still works as before |
| E9 | No locomotion starvation anywhere (walk/cast/attack all resume normally after locks/breaks) |
| E10 | Combat unchanged: trackWindup turn rate during attacks unchanged |

## 6. Tunables (all CONFIG)
- CONFIG.lockOn: lightRadiusFactor (~0.8 of light.distance),
  lightCheckIntervalSec (0), 'too dark' toast string + duration;
  camExtraDistance = 0 (or removed).
- CONFIG.light.lockRadiusFactor as the global factor knob.

## 7. Report
scratch/astrabot_orderE_lockon_light_report.md (committed): flows, anchors,
judgment calls (the reticle path, light collection structure), tunables,
AC notes. Final chat: commits with shas, AC table, knobs, undone items.