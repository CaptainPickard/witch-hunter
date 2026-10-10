# ROUND D2 CONTRACT: lantern light fix (IO -> Claude Code)

You are implementing IO-approved Round D2 in /workspace/witch-hunter: make the
world fire props actually illuminate the ground beneath them, and move each
prop's light INTO the lantern object instead of floating beside it. Follow this
contract EXACTLY. NO harness runs, no headless browser game sessions, no
contact-sheet QA loops - Nicko playtests. Static probes, Blender stills and
syntax checks only. Commit early and often. All measurements you need are IN
THIS CONTRACT - ZERO research beyond the listed steps.

## Repo state (verified 2026-10-05 by IO)

- Repo /workspace/witch-hunter = dev checkout (origin/dev @ 896ee87, local dev
  @ 896ee87). feat/world-visuals = git worktree /tmp/wh-worldfeat (local
  @ a02ab8a = origin). Round D (Mixamo chain attacks) just landed on both.
- The worktree's scratch/ is a SEPARATE checkout (not shared with the main
  dir) - write scratch files in BOTH checkouts when both need them, and
  commit each branch's own copies.
- Blender: /opt/blender-4.5.4-linux-x64/blender. Still-render pattern to adapt:
  scratch/roundD_proof_render.py; requires live Xvfb :99 (the container
  usually has it; if DISPLAY=:99 fails, start your own Xvfb on :99).
- Serve law: commit on BOTH branches, run tools/build_v7.py IN the worktree
  only, build commit on feat, IO pushes (do NOT push), IO refreshes the host
  and curls.

## Root cause (measured, baking these numbers in)

Light plumbing: game.js poolTick -> computeSockets -> computeFireSockets
places one of 4 pooled PointLights at each lit prop's socket:
    x = p.x, y = groundHeight(asset) * p.scale * heightFraction, z = p.z
1. LATERAL: the socket math has NO lateral offset - the light sits on the
   prop's center column. GLB vertex measurement (scratch/lantern_head_probe.py,
   committed by you) shows the lantern-post HEAD hangs at glTF-local
   x = -0.05..-0.11 (bands 65-85% of height; the post column itself is at
   x = +0.15). At scale 2.4 that is ~0.15-0.25m off the visible lantern head.
   The b3-waymarker head hangs at glTF-local z = +0.18..+0.30 (top bands).
   -> Nicko sees the light outside the lantern object.
2. INTENSITY: the light pool is CONFIG.lightPool {distance 11, decay 2} with
   socket intensities 1.6/1.8/2.4. With physical falloff (decay 2), a light
   3.5-4m above its ground pool reads ~0.1-0.6 illuminance - basically dark,
   while the player torch reads ~2-3 because its intensity is 10.5.
   -> Nicko sees no ground illumination under lanterns.

## Changes (both branches: dev in /workspace/witch-hunter, feat in /tmp/wh-worldfeat)

1. CONFIG.js lightSockets - add lateral offset (glTF-local, pre-rotY, pre-scale)
   and raise intensities (torch-parity ground pool):
       lanternPost:     { heightFraction: 0.85, intensity: 9.0,
                          offset: [-0.06, 0.0] },
       banditCampfire:  { heightFraction: 0.55, intensity: 3.2,
                          offset: [0.0, 0.0] },
       lanternWaymarker:{ heightFraction: 0.80, intensity: 9.5,
                          offset: [-0.03, 0.24] },
   Update the adjacent comment: offsets are measured from GLB vertex bands
   (scratch/lantern_head_probe.py), intensities matched to the player torch
   (10.5) for ground-pool parity with physical decay 2.
2. game.js computeFireSockets - apply the offset with rotation + scale:
   read sd.offset (default [0,0]); rotate by the prop's rotY
   (ox' = ox*cos(rotY) - oz*sin(rotY); oz' = ox*sin(rotY) + oz*cos(rotY));
   world x = p.x + ox' * p.scale, world z = p.z + oz' * p.scale; y unchanged
   (heightFraction path untouched). All current CONFIG props have rotY 0, so
   no visual change beyond the intended offsets - the rotation is future-proofing.
   Keep computing h exactly as today.
3. NOTHING else changes: no GLB bytes, no light.js (lock-light 'world' radius
   is intensity-independent), no region-manager.js, no flame-card logic (the
   card already follows tgt, so it will sit in the head automatically).

## Verification (all static/cheap)

- Parse check the two edited files on both branches (python3 esprima; no node
  on this box).
- grep each branch's CONFIG.js for '9.0'/'9.5'/'3.2' + 'offset: [-0.06, 0.0]';
  grep feat game.js for 'sin(rotY)' or equivalent rotation code.
- Blender stills (exactly 3, into scratch/roundD2-proof/, 1024px, adapt
  scratch/roundD_proof_render.py): each = the prop GLB alone + one warm
  PointLight placed at the NEW socket position (rotY 0 -> local*scale) + one
  small emissive sphere at the light position as the flame stand-in:
    01-lantern-post.png: lantern-post GLB, scale 2.4, light at measured local
      head position (x -0.05..-0.11 band 65-85%, at the head's height) - the
      light/sphere must land INSIDE the hanging head geometry, warm pool
      visible on the ground beneath.
    02-waymarker.png: b3-waymarker GLB - same test with z offset.
    03-campfire.png: m15-bandit-campfire GLB - light centered, low.
  Vision-check each yourself in the render loop (do NOT ping-pong through IO).

## Commits (git identity CaptainPickard <pickard.nicko@gmail.com>)

Per branch (dev first, then the worktree), one commit each:
    feat(world): lantern socket offsets into the head + torch-parity ground light (Round D2)
Files on dev: prototype/js/CONFIG.js, prototype/js/game.js,
scratch/lantern_head_probe.py. Files on feat: prototype/js/CONFIG.js,
prototype/js/game.js, scratch/lantern_head_probe.py,
scratch/lantern_head_probe.py copy in the worktree scratch/, PLUS the build:
then run tools/build_v7.py in the worktree and commit
    build: v7 bundle with lantern socket offsets + stronger fire light (Round D2)
(also git add scratch/roundD2-proof/*.png if you produce them in the worktree;
the stills render in whichever checkout you run Blender from - render them
from the worktree so their git add lands in the feat commit).
Do NOT push. Do NOT touch main, light.js, region-manager.js, any GLB.
NEVER read/move/commit scratch/.mixamo-credentials.txt or
scratch/.mixamo-storage.json.

## Report back (final message)

Per-step real outputs: commit SHAs both branches, parse/parse results, grep
counts, the render PNG paths, and any deviation (with reason) or FAILED step
(exact error, tried twice max). Zero-research discipline: never web-search,
never open the Mixamo site, never run the game.