# Astrabot report - Order E: lock-on camera reframe + light-gated targeting
2026-10-05, branch feat/world-visuals. No harness/headless runs (law 0); there
is also no JS runtime on this box, so nothing was syntax-checked by a tool -
code was re-read by hand. Nicko's playtest is the acceptance gate.

## Commits
- 6899a38 E1 camera reframe (player.js, CONFIG.js)
- a64a0ca E2 light registry + lock gate (light.js, game.js, CONFIG.js, inventory.js)

## E1 - camera (player.js updateCamera)
Flow: if locked && alive -> camYaw lerps (LOCK.camLerp) toward
atan2(target - player) + PI. Then the ONE orbit path runs for both states:
anchor = player pos + camHeight, R5 pitch-distance cap, camMin clamp, ground
floor, position lerp at CFG.camFollowLerp, lookAt the player anchor.
- Midpoint re-anchor and the dist/midDist + camExtraDistance zoom are gone.
- Pitch and wheel distance are untouched by lock (Nicko ruling 1).
- Judgment call: position follow while locked now uses camFollowLerp (same as
  unlocked) instead of LOCK.camLerp, so distance/height read identical; the
  yaw swing is still smoothed by LOCK.camLerp.
- camExtraDistance: kept as a legacy key set to 0 with a RETIRED comment;
  nothing reads it now.
- The engage-time camYaw snap (game.js engageLockOn) is unchanged, and so is
  the disabled mouse orbit while locked.
- Frame check (CONFIG.lockOn frameCheckNote): default orbit = dist 7, pitch
  22deg, camHeight 2.6, fov 60. An enemy at 18m sits about 10deg above screen
  center, so it's in frame. At about 50deg+ pitch an 18m enemy goes off the
  top edge; that's the player's own pitch choice, and the reticle hides when
  the enemy is off-frame.

## E2 - light registry + gate
light.js: `WH_PlayerLight.collectLockLights(player, playerLight, radiances,
worldSockets)` returns `[{x, z, radius, kind}]`. `isInLitArea(lights, x, z)`
tests on the xz plane.
- 'spell': each hand whose `handLightDef` is live (firebolt binding; also
  an items[].light torch later). Position = the hand light's world position,
  or the player position before the light is first hand-anchored.
  radius = def.distance * k (firebolt 12 -> 9.6m).
- 'radiance': each game.radiances entry with active && light.intensity > 0
  (fade-in counts, parked does not). radius = lightDistance * k (14 -> 11.2m).
- 'world': every CONFIG.lightSockets fire prop of the active region
  (lanternPost, lanternWaymarker, banditCampfire). radius =
  lightPool.distance * k (11 -> 8.8m).
- Excluded: moonlight/hemisphere (ruling 2) and projectile bolt lights
  (a passing bolt is a flash, not something you can see a target by).

Judgment call on world lights: I used the static CONFIG sockets, which are
always burning, not the 4-slot render pool. Fire props have no burning
state today. The pool is a render budget: firebolt sockets compete for its
slots, so gating on the pool would make a lantern stop counting whenever you
fire a bolt, and that would break the lock mid-fight. Trade-off: a lantern
beyond the 4 nearest has no flame card drawn but still counts.
game.js: `computeSockets` is split so that `computeFireSockets()` (static
props) is shared by the pool and the lock gate.

game.js gate:
- `lockLights()` rebuilds the registry on every call, or caches it per
  CONFIG.lockOn.lightCheckIntervalSec when that is > 0.
- `pickLockTarget` keeps the old range/cone rules and then requires `isLit(e)`.
  It picks the nearest LIT enemy, so a nearer unlit one does not block it.
- Refusal: there was no existing empty-feedback path (the old code returned
  silently), so I reused the inventory HUD toast with CONFIG.lockOn.tooDarkText.
  The toast shows only when an in-range, in-cone enemy was skipped as unlit.
  With nobody around it stays silent, as before. `InventoryUI.toast` gained an
  optional seconds argument.
- `updateLockOn`: `!isLit(t)` joins dead/region/hysteresis in the same break
  branch. It is immediate, with no grace (ruling 3).
- Enemy AI is untouched (ruling 4).

Starvation check (D9): there are no new flags on the player. A break only nulls
`lockTarget`, the same path as the distance break. Every lockTarget read in
player.js (locomotion yaw, windup tracking, camera, mouse orbit) is
per-frame state.

## Tunables
- CONFIG.lockOn.lightRadiusFactor 0.8 (the single global knob)
- CONFIG.lockOn.lightCheckIntervalSec 0 (rebuild every frame)
- CONFIG.lockOn.tooDarkText 'Too dark to target', tooDarkToastSeconds 1.2
- CONFIG.lockOn.camExtraDistance 0 (retired)
- Not added: CONFIG.light.lockRadiusFactor. CONFIG.light does not exist (the
  block is CONFIG.playerLight), and two factor knobs would conflict, so I kept
  only the lockOn one.

## AC notes (Nicko playtests)
| AC | Expectation |
|---|---|
| E1 | Lock changes only the yaw; distance/height/pitch match unlocked play |
| E2 | 18m enemy is ~10deg above center at default pitch |
| E3 | Firebolt-bound hand (9.6m) or brazier (8.8m): locks and holds |
| E4 | No hand light, no Radiance, away from fire: toast and no lock |
| E5 | Within ~8.8m of a lantern post/waymarker/campfire: locks |
| E6 | Radiance: 11.2m around the orb while lit; refuses after it parks |
| E7 | Target leaves every radius: breaks the same frame |
| E8 | Hysteresis break is unchanged |
| E9 | No latches added |
| E10 | trackWindupDegPerSec is untouched |

Note: firebolt range 9.6m < lock maxDistance 18m, so with just the glove
the effective lock range is ~9.6m (plus the hand offset). Raise
lightRadiusFactor if that feels short.
