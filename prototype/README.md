# Witch Hunter - Playable Concept Prototype v1

Three.js playable concept proving two things: third-person action combat feel
(walk, attack, roll) and the instance-regions-with-gated-boundary-crossings
answer to open-world scope.

## Run

```
python3 server.py
# open http://localhost:8791/
```

server.py is a stdlib-only http.server (port 8791, binds 0.0.0.0). It serves
the repo root so GLB assets resolve at absolute URLs under /art-direction/...
(the page itself is served from prototype/ via a path remap, so /index.html,
/js/..., /vendor/..., /style.css all work).

## Controls

- WASD: move (camera-relative)
- Shift: sprint (drains stamina)
- Space: roll (i-frames during the roll window)
- LMB (click): basic attack (swing arc); LMB drag: rotate camera
- Mouse wheel: zoom

## Architecture

```
index.html (classic scripts, no modules)
  vendor/three.classic.js        vendored Three.js r185, window.THREE
  vendor/gltf-loader.classic.js  classic GLTFLoader, window.WHGLTFLoader
  js/CONFIG.js                   ALL tunables
  js/region-defs.js              region layout + boundary/chokepoint data
  js/assets.js                   GLB manifest + loading + stand-ins
  js/player.js                   third-person controller
  js/enemy.js                    bandit/ghoul FSMs
  js/region-manager.js           region lifecycle (the core system)
  js/game.js                     loop, camera, HUD, WH_DEBUG hooks
```

Region lifecycle (text diagram):

```
                 distance-to-boundary <= preWarm.distance
  ACTIVE A  ------------------------------->  A active + B pre-warmed
  (visible)                                   (B built, visible=false)
     ^                                               |
     | player turns back                             | player crosses plane
     | beyond preWarm + hysteresis                   v
     +------ dispose pre-warm <-------  CROSS: B revealed instantly,
             (B removed, disposed)      A group removed + disposed,
                                        player position mapped across
                                        (normal delta flips, tangent kept)
```

Only one region is active and visible at any time. Per-region state (enemy
dead/alive) persists per session keyed by region id: dead stay dead when you
leave and re-enter. The boundary is blocked everywhere except the single
chokepoint corridor; enemies never cross (they hold at a margin on their home
side). The region-manager transition core (WH_RegionManagerLogic) is
THREE-free and testable with plain mocks.

## GLB route approach

server.py serves the repo root, so assets are referenced as absolute paths
like /art-direction/3d/assets/graveyard/gravestone-obelisk-pixelated.glb.
Pixelated variants are preferred for props; races_regen characters have no
pixelated variants, raw meshes are used for player/bandit/ghoul.

Render settings carried over from validated Witch Hunter 3D work:
SRGBColorSpace output, NearestFilter on pixelated textures, DoubleSide
materials, high ambient fill with moderate keys and lifted exposure for dark
albedo.

## Build

builds/v1-playable.html inlines all js/css (GLTFLoader included) and keeps
GLB references as absolute /art-direction/... URLs, so it must be served by
server.py (open http://localhost:8791/builds/v1-playable.html).

## Explicitly v1-rough

- Procedural transform-only animation (bob, swing, tumble); assets are
  unrigged, no skeletal animation
- Single boundary pair (A<->B) with one chokepoint; no region C, no chained
  crossings
- No audio, no shadows (swiftshader software rendering), no UI menus
- Combat feel is POC-scaled, not doc-33 exact; enemy senses are POC values
- Circle push-out is positional only, no physics solver