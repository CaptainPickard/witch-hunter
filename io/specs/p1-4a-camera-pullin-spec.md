# P1-4a — Camera Pull-In (doc 61 P1-4, camera half)

IO spec, wake 39 (2026-11-08). Worktree /tmp/wh-worldfeat, branch feat/world-visuals.
Build tool: tools/build_v8.py (newest). Art anchor: art-direction/concepts/concept-01-darkwood.png
+ concept-05-night-ambush.png (IO view, this wake).

## Problem

Doc 61 P1-4 (region-manager.js:287 "R5 P0-5: world bounds + prop colliders") is
HALF-landed. Player prop collision is live. The second half — camera collision
and occluder fade — is not: `Player.prototype.updateCamera` (player.js ~2227)
builds `want = target + offset` at the orbit distance and lerps to it with ZERO
obstruction awareness. Inside region B's forest the camera regularly sinks into
tree trunks / passes through the boundary wall and arch stones: the frame fills
with bark, the player vanishes from view. Confirmed ground truth this wake:
- Collider table: `RegionManager.propColliders(regionId)` (region-manager.js
  ~1676) — cached `{circles:[{index,name,x,z,r}], exempt:[...]}` built by
  `whPropColliders` from CONFIG props (+ scatter plan trees + wall plan
  circle rows). Trunk-class assets carry r = footprint/2 * 0.25
  (TRUNK_RATIO, C14 law); solid assets (walls r 0.45/seg, arch legs r 0.6,
  plugs 0.5, stones/boulders) carry full-footprint circles.
- Camera path: player.js 2242-2270 — yaw/pitch offset -> `want`, then
  `camera.position.lerp(want, lerp2)`, y floor, `lookAt(target)`.

## Design (bind to existing laws; no new taxonomy)

1. **Which circles occlude.** Reuse the EXISTING C14 classification:
   vegetation-class (TRUNK_ASSETS set + the /tree|oak|birch|sapling|bush|
   bramble|fern|shrub|stump/i regex in colliderRadius) are trunk-dominant —
   canopy leaves are BRUSHABLE by design, so their occluder top is the trunk
   only: `h = nativeHeight * scale * 0.45` (new CFG const TRUNK_TOP_FRAC).
   Every other circle is solid mass: `h = nativeHeight * scale`.
   Wall-plan rows (whWallA/whWallB segments + b3Gate legs/plugs/chord) get
   `h = CFG.boundaryWall.heightM` (7.2 m full-height design law, Round G).
2. **Foot y.** Each circle row gains `fy` (ground y at the prop seat).
   Regions A/B: fy = 0. Region C (terrain): fy = WH_GROUND.footY(activeId,
   x, z, terr propFootR) at BUILD time, guarded the way computeFireSockets
   already guards groundHas() in game.js; if the terrain table is not ready,
   fy = 0 and the row is still pushed (acceptable; foot error < 1 m).
3. **Where the fields are attached.** In `whPropColliders` + `whWallPlan`
   (region-manager.js) at circle-construction time so the fields ride the
   EXISTING cache (`this.colliders` / `wallPlanCache`) — boot-time only, no
   per-frame getMeta/name lookups. Circle rows become
   `{index, name, x, z, r, h, fy}` (h/fy added; existing fields unchanged).
   Consumer default: missing h/fy treated as h = 12 (big), fy = -6 (low) so an
   unmapped row still occludes conservatively.
4. **Per-frame test (player.js, inside updateCamera, between `want` build and
   the `want.y < floorY` clamp).** Sample the segment target->want at
   N = CFG.player.cameraPull.samples (6) evenly spaced t in
   [1/N .. 1.0] — WAKE-39 AMENDMENT 1 (IO, post-verdict): BLESSED K/N grid. For each circle of the ACTIVE region's table
   (propColliders(activeId).circles ONLY — `exempt` rows never occlude; this
   inherits the corridor-exemption law: gate corridor stays camera-clean):
   - broadphase: skip circle if |centerXZ - segment midpointXZ| >
     (segmentLen/2 + r + R + skin) (single sqrt),
   - then for each sample: 2D dist sample->circle center <= r + R + skin AND
     y_s within [fy - 0.25, fy + h] -> blocked.
   - R = CFG.player.cameraPull.camRadiusM, skin = cameraPull.skinM.
   If ANY blocked sample: pull the camera IN — the pull target distance is
   one sample spacing back: tClear = max(0, (i_first-1)/N) where i_first is
   the first blocked sample's index base in candidates; then a bounded
   verification loop (max 2 shrink steps, step factor 0.85): point-check the
   want' at tClear against all circles (2D dist <= r + R + skin AND y in
   band) — while violated, tClear = tClear - 0.15 (>= 0). Final
   `want = target + normalized(offset) * max(camMinDistance, tClear * effDist)`.
   The existing lerp then GLIDES the camera to it (no snap).
5. **Exact preservation otherwise**: offset vector formula, effDist cap
   (camPitchDistShrink), wheel camDist state, LOCK.camLerp yaw aim, lerp2,
   both y floors, lookAt target — all unchanged. The only edits: the
   pull-in block inserted between `var want = ...` and the `want.y < floorY`
   clamp. cameraGroundFloor() (game.js) and applyCameraShake untouched.
6. **Flag + observability.** `CFG.player.cameraPull = { enabled: true,
   camRadiusM: 0.45, skinM: 0.30, samples: 6, trunkTopFrac: 0.45,
   minFloor: 0.0 }` added beside the existing cam* keys (CFG.player,
   CONFIG.js ~2939-2947). `enabled: false` must reproduce the pre-change math
   exactly (single early-out, no allocation). While enabled, the player
   instance records the last pull for validation: `player.lastCameraPull =
   { blocked: bool, wantDist: pulled, effDist: uncapped-want-dist, t: tClear,
   circles: n }` — updated EVERY frame while enabled (plain object, reused,
   no allocation); Testerbot reads it via window.WH_DEBUG.game.player.
7. **No new script file; no scene-graph or three.js version changes;
   region-manager.js edits are boot-time only (no per-frame cost added
   there). No per-frame allocation in player.js pull path (reuse module-scope
   scratch; the pool law pattern).**

## Files

- prototype/js/CONFIG.js — CFG.player.cameraPull block.
- prototype/js/region-manager.js — h/fy on circle rows (whPropColliders,
  whWallPlan rows).
- prototype/js/player.js — pull-in in updateCamera + lastCameraPull record.

## Acceptance criteria (Testerbot verifies code; NO playtest harness)

A1. `node --check` passes on all three touched files.
A2. Diff of player.js is confined to: the pull-in block between the offset/want
    build and the first floor clamp, plus the lastCameraPull record, plus the
    module-scope scratch vars. Orbit math lines otherwise byte-identical.
A3. Diff of region-manager.js confined to h/fy attach points in
    whPropColliders (props, wall rows, scatter) and whWallPlan-produced
    colliders; no logic change to radii/r/exempt behavior.
A4. CFG keys exist exactly as spec'd; enabled:false path = exact legacy math
    (code-read: the entire pull block is behind one enabled check).
A5. Exempt inheritance: pull test iterates table.circles only; exempt rows
    are structurally excluded (code-read) — corridor camera behavior preserved.
A6. Zero per-frame allocation: no `new`/`[]`/`{}` inside the pull block;
    lastCameraPull object is reused (mutated), not reallocated.
A7. Band edge cases handled: y_s above fy+h -> no block (bushes never pull the
    camera in); y_s below fy-0.25 -> no block; missing h/fy -> conservative big
    occluder (defaults in code, not crash).
A8. Pull result geometry (pure-function read of the code): want' distance =
    max(camMinDistance, tClear*effDist); verification loop terminates <= 2
    shrinks; never below camMinDistance; lookAt target unchanged.

## Boundaries

- NO git commands of any kind (children NEVER push; IO is the sole
  gatekeeper). Do not commit.
- NO playtest harness, no browser automation of gameplay. Nicko is the playtest.
- Prototype convention: IIFE + window globals only (no ES modules, no import
  in js/); keep code style EXISTING (var, no arrow functions in js/ files).
- Build + flip are IO steps, not Devbot steps.
