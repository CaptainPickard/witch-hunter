# DEVBOT SPEC — Witch Hunter World R2: Lighting Rig Overhaul (P0-3 + P1-8)

Author: IO (auto-finisher job 2c7556f7f609). Date: 2026-10-01.
Authority: docs/planning/61-world-audit.md section 5.3 (P0-3 lantern-and-moon
relight) + section P0-3 bullet list (lines 285-299) + P1-8 (lines 399-408) +
section 5.2 cost table. Audit is upstream; implement from THIS spec, report
spec-audit divergence as amendment notes, never patch silently.

Branch/worktree: /tmp/wh-worldfeat, branch feat/world-visuals (currently
26e7a60 = merge of dev dc697ce whanim2 + asset handoff c37a9f7).
NEVER push dev, NEVER push main. All dev commits on feat/world-visuals.
IO commits at the end; you leave the worktree clean of stray files.

## Standing law (hard constraints, whole round)

- Vanilla JS only: IIFE, window globals, NO ES modules, NO class keyword,
  no template literals. Match existing file style exactly.
- No npm/node, no geometry post-processing (raw mesh + color pixelation only),
  no rigging, procedural animation only.
- Secrets grep clean. No player-facing string may contain "free".
- DO NOT TOUCH: prototype/js/player.js, prototype/js/enemy.js,
  prototype/js/anim.js, prototype/js/moveset.js, prototype/js/spells.js
  (firebolt light tracked from game.firebolts — no spells.js change),
  prototype/vendor/**, sui/**, style.css, prototype/index.html.
- Allowed files: prototype/js/CONFIG.js, prototype/js/game.js,
  prototype/js/assets.js. Nothing else. If you believe a 4th file is needed,
  STOP and report instead of expanding scope.
- Do not remove/alter any existing CONFIG key other than the lighting block
  values listed below; other rounds read them.

## Verified current-state anchors (worktree 26e7a60)

- game.js:41 `renderer.toneMapping = THREE.ACESFilmicToneMapping;` exposure
  from CFG.renderer.toneMappingExposure (CONFIG.js:10, value 1.6).
- game.js:54-64 setupLights: AmbientLight(L.ambientColor 0x8a8fa8,
  L.ambientIntensity 4.0), HemisphereLight(L.hemiSkyColor 0x6b7fa8,
  L.hemiGroundColor 0x3a3a44, L.hemiIntensity 1.5), key DirectionalLight
  (0xfff2dd, 1.2) at (30,60,20); game.keyLight = key.
- game.js:422-431 applyRegionLighting: sets scene.background/fog from region
  def; scales ONLY keyLight.intensity by region.ambientLightLevel.
- CONFIG.js:14-24 lighting block. CONFIG.js:49 regionA.ambientLightLevel 1.0;
  CONFIG.js:110 regionB... 0.55. region-defs.js:24-26 copies those three
  fields into region defs (do not edit region-defs.js).
- Assets.js manifest: lanternPost -> church-kit/lantern-post-pixelated.glb
  (assets.js:34). Region props: two lanternPost instances in regionA
  (CONFIG.js:64-65). No light-pool code exists anywhere yet.
- Player rig: player.root > yawFrame > body; game.js:645-654 attaches body and
  sword (sword parented to R_Hand bone via player.js:127-141 — do not touch).
- Firebolts: game.firebolts array (game.js:27), bolts carry world position;
  spells.js is off-limits — read positions from the array only.
- Ground-align holder for props already exists (assets.js prepTemplate /
  instance, R1); new props placed through CONFIG props arrays get grounded
  automatically. worldMinY tolerance |y| <= 0.02 is the R1 A1 floor.

## R2-1 · Relight (P0-3) — CONFIG.js lighting block rewrite

Replace the CONFIG.js lighting block with:

  lighting: {
    // P0-3: ambient removed; hemisphere is the only fill and is what
    // ambientLightLevel scales. Moon is a cool directional on -z backlighting
    // the main path. Lantern = warm PointLight parented to the player.
    ambientIntensity: 0,              // P0-3: AmbientLight removed (kept for
                                      // backward-compat readers; must stay 0)
    hemiSkyColor: 0x4a5a80,           // indigo-slate sky (audit 5.3)
    hemiGroundColor: 0x16181e,        // near-black ground (audit 5.3)
    hemiBaseIntensity: 1.35,          // fill at ambientLightLevel 1.0; region
                                      // fill = hemiBaseIntensity * ambientLightLevel
    moonColor: 0xa8bce6,              // cool moon (audit 5.3)
    moonIntensity: 0.45,              // moon:fill (vertical faces) 3-5:1
    moonAzimuthDeg: 0,                // -z side, backlights A->B main path
    moonElevationDeg: 30,             // audit: 25-35 deg
    lanternColor: 0xffb060,           // warm amber (audit 5.3; canon accent)
    lanternIntensity: 6.5,            // audit 5.3: 6-8 cd class
    lanternDistance: 12,              // audit: distance ~12
    lanternDecay: 2,                  // physical falloff
    lanternFlickerPct: 5,             // +-5% flicker band
    lanternAnchor: 'left-hip',        // yawFrame-space anchor
    lanternAnchorOffset: [ -0.32, 0.95, 0.08 ]  // tuned starting anchor
  },

Remove the old keyColor/keyIntensity/hemiSkyColor/hemiGroundColor/
hemiIntensity/ambientColor keys EXCEPT keep behavior for any reader outside
game.js — grep first; only game.js references keyLight and lighting keys, but
VERIFY with grep before deleting. Update the block comment to describe the
P0-3 rig semantics.

Renderer block: add `toneMappingName: 'Neutral'` (keep outputColorSpaceSRGB
true) and re-set toneMappingExposure to 1.15 (audit: exposure re-set so fog
stays the brightest large area; final number gated on validation — one
CONFIG-only retune amendment is pre-authorized if the floor bars below fail).
game.js maps toneMappingName -> THREE.NeutralToneMapping (fall back to ACES
if constant missing) and keeps exposure plumbing as-is.

## R2-2 · game.js setupLights rewrite

- Remove the AmbientLight entirely (scene must contain zero AmbientLight).
- HemisphereLight(hemiSkyColor, hemiGroundColor, hemiBaseIntensity) — global,
  never per-region. Store game.hemiLight.
- Moon: DirectionalLight(moonColor, moonIntensity). Direction: aim from the
  -z side downward at the elevation: moon.position at azimuth 0 / elevation
  30 (e.g. position.set(0, sin, -cos) normalized * 100, target = origin —
  use a fixed target Object3D at (0,0,0) added to scene). Store game.moonLight.
  Moon stays constant across regions (no ambientLightLevel scaling).
- Player lantern: PointLight(lanternColor, lanternIntensity,
  lanternDistance, lanternDecay). Parent it under the player's yawFrame at
  lanternAnchorOffset (left-hip). Add it at boot BEFORE the first render
  (inside setupLights call path, immediately after body attach is fine, but
  the light must exist before the first renderer.render — create it in
  setupLights and attach to game.player in boot after setBody: acceptable).
  Flicker: per-frame game.lantern.intensity = lanternIntensity * (1 +
  0.05 * wobble(t)) where wobble = 0.6*sin(7.3t) + 0.4*sin(3.1t + 1.7); no
  Math.random. Drives only intensity; never added/removed.
- applyRegionLighting rewrite: scene.background/fog as today; fill scaling:
  game.hemiLight.intensity = hemiBaseIntensity * region.ambientLightLevel;
  (B's 0.55 gives the darker forest). keyLight is REMOVED — delete the
  game.keyLight assignment and any reader of it (grep; also remove from the
  debug hooks if one exposes it).
- All new tunables read from CFG, zero literals in game.js.

## R2-3 · Fixed light pool (P1-8) — game.js only

- Create exactly 4 THREE.PointLight in setupLights BEFORE the first render:
  color 0xffd9a0-class comes from CONFIG (lightPool section, new):
    lightPool: {
      size: 4,
      color: 0xffc27a,
      distance: 11,
      decay: 2,
      handoffFadeSec: 0.35,     // intensity fade on reassignment
      minIntensityFloor: 0.0    // unused slot = 0 intensity, never removed
    },
  Store in game.lightPool = [l0..l3]; add all 4 to game.scene at boot; NEVER
  add or remove pool lights after boot (shader light count static — M-19).
- Light socket registry (game.js, module-local):
  - Static sockets derived per frame from the ACTIVE (visible) region group:
    any prop mesh whose CONFIG asset name has an entry in a new
    CONFIG.lightSockets map. Entries:
      lightSockets: {
        lanternPost:       { heightFraction: 0.85, intensity: 1.6, flame: 'ember' },
        banditCampfire:    { heightFraction: 0.55, intensity: 2.4, flame: 'ember' },
        lanternWaymarker:  { heightFraction: 0.80, intensity: 1.8, flame: 'ember' }
      },
    Socket world position = prop holder world position + (0, groundHeight *
    heightFraction * propScale, 0). Compute from WH_ASSETS.groundHeight(asset)
    and the instance's own scale — do not hardcode metres.
  - Dynamic sockets: one per live Firebolt pulled from game.firebolts (bolt
    world position, y included), intensity 1.8, weight 0.6 applied to its
    distance during sorting so near bolts out-rank statics.
  - Sockets from groups that are NOT visible (pre-warmed region) are excluded.
- Per-frame assignment (pool tick, one pass, cheap):
  1. Build socket list (visible-region statics + firebolts).
  2. Sort by weighted distance to the player; take first 4.
  3. For each pool slot i: if target socket changed, start a fade from its
     current intensity to the socket intensity over handoffFadeSec; else
     lerp toward socket.intensity. Unassigned slots lerp to 0.
  4. Reposition the slot light at the socket world position each frame.
- Flame cards: 4 sprites created ONCE at boot (THREE.Sprite with
  SpriteMaterial map = WH-loaded ember texture
  art-direction/3d/assets/textures/particles/particle-ember.png, blending =
  THREE.AdditiveBlending, depthWrite false, transparent true, size ~0.55,
  scale.y *1.4). Loaded via a new MANIFEST entry `particleEmber`. One sprite
  per pool slot, repositioned each frame to its slot's socket world position,
  visible only when that slot intensity > 0.06. Gentle bob: y += 0.06 *
  sin(2.1t + i). Never created/destroyed after boot (M-05 leak floor).
- New debug hook (measurement-only, sanctioned): WH_DEBUG.getLightPool()
  returns per-slot { intensity, socketId string '<asset>@<x>,<z>' or
  'firebolt#<idx>', x/y/z } and
  WH_DEBUG.getLightSockets() returns the current socket list with ids AND
  per-socket x/y/z world positions (y included — Testerbot amendment note 4).

## R2-4 · Wire the two new light-socket props (so the pool has sockets in BOTH regions)

- assets.js MANIFEST += (all paths relative, match existing style):
    banditCampfire:    'art-direction/3d/assets/biome_library/m15-bandit-campfire-pixelated.glb',
    lanternWaymarker:  'art-direction/3d/assets/biome_library/b3-waymarker-pixelated.glb',
    particleEmber:     'art-direction/3d/assets/textures/particles/particle-ember.png'
  (particle load: reuse the texture loader path you find in assets.js; if
  only GLB loading exists, add a tiny loadImage path modeled on resolveUrl —
  still inside assets.js).
- CONFIG.js region B props += exactly two entries (place them visibly on the
  spawn-path clearing, keep them OFF enemy spawn markers):
    { asset: 'banditCampfire', x: 2.5, z: -52, rotY: 0.0, scale: 1.8 },
    { asset: 'lanternWaymarker', x: -6.5, z: -47, rotY: 1.1, scale: 1.9 }
- Region A keeps its two lanternPosts (existing entries untouched).

## Acceptance criteria (Testerbot bars; evidence must be numeric)

R1 floor: tests/wh_world_r1_validation.py A1-A8 must still PASS unmodified
(A1 prop grounding now also covers the two new props: |minY| <= 0.02).

New R2 ACs (validated via new file tests/wh_world_r2_validation.py, same
harness discipline as R1: check()/per-AC funcs, exit 0 always, organic-path
law, WH_DEBUG reads fine, writes only via sanctioned hooks):

- L1 AmbientLight removal: scene traversal finds 0 AmbientLight; exactly 1
  HemisphereLight with CFG sky/ground colors; hemiBaseIntensity drives
  intensity and regionB fill (after crossing into B) = base * 0.55 (record
  both regions' values).
- L2 Moon: exactly 1 DirectionalLight, color 0xa8bce6; light world position
  is on the -z side (z < 0) with elevation 25-35 deg (compute from position:
  asin(|y|/len) in deg); a vertical probe luminance test: plane at world
  center facing -z vs facing +z, moon-facing / opposite ≥ 2.0 (backlight
  direction proof on SwiftShader via the R1 toDataURL pattern).
- L3 Player lantern: PointLight exists, warm color (0xffb060), distance 12
  decay 2; it is parented within the player's Object3D chain (root/yawFrame);
  sampled intensity over 60 frames stays within +-5% of a wobble-only band
  (no steps > 0.5); player teleport moves the light with the player
  (worldPosition delta == player delta within 0.01).
- L4 Tone mapping: renderer.toneMapping === THREE.NeutralToneMapping;
  renderer.toneMappingExposure == CFG value (1.15); fog/background pixel mean
  (sky sample at 1080p center-top) >= ground-ring mean (fog stays brightest
  large area — record both).
- L5 Fixed pool: at boot-before-first-render the scene already contains
  exactly 4 pool PointLights (verify via getLightPool() len == 4 on the first
  rAF tick) plus the player lantern; renderer.info.programs.length captured
  at boot, after a 10 s organic walk in A, after crossing A->B->A, after 5
  firebolt casts, after walking away from/closer to lanternPost: growth <= +2
  across the whole run (M-19, SwiftShader-recorded).
- L6 Socket handoff: teleport player near lanternPost A1 (-2,30): pool slot
  targeting '<asset>@-2,30' (or equivalent id) has intensity > 0.5; teleport
  to post A2 (4,-2): within 1.5 s the first post's slot lerped DOWN and the
  second's UP (read getLightPool() target ids + intensities over ticks;
  fade over handoffFadeSec recorded, monotonic or single-dip curve).
- L7 Firebolt socket: cast firebolt (debug cast path used by weave tests),
  read getLightSockets(): >= 1 socket id starting 'firebolt#'; that bolt's
  pool slot intensity > 1.0 while bolt alive; after bolt death the socket
  list drops it within 2 frames.
- L8 Flame cards: 4 sprites with AdditiveBlending + ember texture exist at
  boot; while player near lanternPost A1, that slot's sprite position is
  within 0.3 of the socket position and slot sprites for unused slots are
  invisible (visible === false).
- L9 New props wired: both new assets load (no 404, no stand-in:
  WH_ASSETS.getMeta(...).standIn !== true, meta exists), grounded
  |minY| <= 0.02, and their pool sockets appear near them when player is
  within 6 units (getLightSockets shows '<asset>@x,z' with matching coords
  +-0.1).
- L10 Readability floor: ghoul silhouette at 10 units in region A: Weber
  contrast of enemy pixels vs background >= 1.15 (mask method: render with
  and without fog via two toDataURL frames, per audit M-10 record); record
  contrast at 5/10/20/30 units. If 10-unit bar fails but 5-unit passes,
  record as FAIL-L10 with numbers (retune loop, do not hack the test).

## Retune protocol (pre-authorized, exactly once)

If L4/L5/L10/L9 floor bars fail while the code is correct (values, not
logic), IO issues a single amendment carrying ONLY new CONFIG values +
explanation; Devbot edits CONFIG.js only; Testerbot re-runs. A second
failure = STOP the round and report.

## Val-spec request (Testerbot)

Derive tests/wh_world_r2_validation.py + run/report plan INDEPENDENTLY from
this spec. Reuse the full R1 harness discipline (headless chromium,
--enable-unsafe-swiftshader, page-clock only, exit 0 always, spawn
prototype/server.py on WH_R2_PORT default 8792, WH_BASE_ROOT override).
Extend — do not modify — the R1 file: R1 keeps passing as shipped; the R2
file adds L1-L10 and re-runs the R1 file as the floor step.