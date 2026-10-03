# WITCH HUNTER — NEW SESSION BRIEF: playtest-driven development era
# (paste everything below the line into a fresh IO session)

You are IO. I am switching this project to PLAYTEST-DRIVEN development: no more
automated harness runs unless I explicitly order one. I play the game, give you
deliberate instructions on what to add or change, and you implement + commit.
Keep reading the repo state before each change, but never propose "running the
validation suite" as a step again unless I say so. Dev work can still be
dispatched, but its acceptance bar is ME playing it, not a robot.

## WHERE THE GAME IS
- Repo: /workspace/witch-hunter (branch: dev for landed work; the world-visuals
  work through 2026-10-02 lives on branch feat/world-visuals as commits up to
  b751212: R2 relight 0406e64, R3 pixelation cce06eb, R4 pixel bodies 818d8bc,
  R5 collision/bounds b751212 marked WIP - all mechanics validated, only the
  final verdict run was skipped at my stop order).
- The running playtest copy I have is SERVED FROM THE dev CHECKOUT at
  http://localhost:8791/ (server pid stays up; do not kill it). That copy is
  the OLD pre-world-visuals look. The NEW look (what this brief describes)
  plays from branch feat/world-visuals in /tmp/wh-worldfeat - if /tmp was
  wiped, recreate: cd /workspace/witch-hunter && git worktree prune && git
  worktree add /tmp/wh-worldfeat feat/world-visuals
- FIRST ACTION: serve the feat/world-visuals tree so I can play it. Prefer a
  static server on a port that MY web UI exposes (ask me which URL form to
  use if unsure, or start it on 8793: cd /tmp/wh-worldfeat/prototype && python3
  server.py 8793 - keep this server running after the session).
- Also: merge feat/world-visuals into dev AFTER I confirm I like the build
  (my call, not automatic; this session's ruling: no harness gates on merge).

## WHAT THE CURRENT BUILD CONTAINS (feat/world-visuals @ b751212)
Base game (all validated pre-10-02):
- Three.js r185 vanilla-JS prototype. Witch Hunter: dark-souls-like night hunts
  in a pixel-art 3D wood. Regions A (Hold Outskirts) and B (darkwood_edge),
  one chokepoint crossing at z=-25. HUD: HP/stamina/focus bars, belt slots.
- Combat: 3-hit sword combo (LMB), lock-on (existing), roll, guard/parry,
  guard-break, finisher windows. Bandits + ghouls with FSM AI (idle/aggro/
  chase/attack), corpses sink and settle.
- Anim: rigged GLB bodies (human hunter player, orc bandit, ghoul) with
  AnimationMixer state machine, 6 clips each, skinned instancing.
- Movement: walk/sprint/roll, souls-style auto-follow camera.

NEW from 10-02 (what I want to playtest):
1. R2 LIGHTING: no ambient light; hemisphere-only fill + cool blue moonlight
   directional from the north; a warm amber hip-lantern ON MY CHARACTER that
   follows me and flickers (two-sine wobble); fixed pool of 4 dynamic lights
   that hand off to the nearest socket: lantern posts in A + campfire and
   lantern waymarker in B; firebolts carry their own light.
2. R3 PIXEL-LOOK: the game renders internally at HALF RESOLUTION (960x540 in
   a 1920x1080 window) with image-rendering pixelated upscale - big chunky
   texels, matches the pixelated prop textures. (CONFIG.renderer
   .internalResDiv=2 is the knob: 1=full res, 4=quarter.)
3. R4 PIXELATED CHARACTERS: player/bandit/ghoul bodies now use committed 512px
   pixelated atlases (posterized colors, chunky look) instead of the smooth
   painterly ones. Kill-switch CONFIG.assets.pixelatedBodies (true=pixelated).
4. R5 COLLISION + BOUNDS (validated mechanics, WIP-marked only because the
   final verdict run was skipped): I collide with props (trunk-radius circles
   for trees - canopies are brushable, posts/stones/boulders are solid full
   footprint); I cannot walk off the world disc (radial clamp, radius 88.5,
   margin 1.5); camera never goes under the ground (min y 0.4) and pulls closer
   as I pitch up (max dist = 14 * (1 - 0.35*sin(pitch))); B spawn tree overlap
   resolved; boot-time spawn validator logs 0 violations.
5. R6 (NOT built yet, spec staged in io/specs/devbot-spec-wh-world-r5/6 files
   and docs/planning/61-world-audit.md): region-crossing GPU-spike fix
   (shared template geometry, dispose only per-region overlays, prewarm with
   renderer.compile) - the audit's P0-6. That is the LAST audit P0 item.

## HOW I WANT TO WORK NOW
- I play at the URL you set up, then message you things like "the campfire
  looks too dim", "add a rest point at the campfire", "make the toggle feel
  faster". You treat each as a work order: read the relevant code, implement
  (yourself or dispatched), commit. Small deliberate changes, one at a time.
- Do NOT run any automated tests/harnesses. My playtest IS the test.
- Art law of the project stays: pixelated everything (512px NEAREST +
  5-bit posterize), raw meshes, dark darkwood palette, ONE accent per frame
  (cyan magic/amber human fire/red pact).
- Copy/player-facing: no the word "free"; no hardcoded agent names.
- Keep committing to feat/world-visuals (or a new branch I order). Merge to
  dev only when I say the build is right.
- Do not send me long design docs for small changes; just do it and tell me
  what changed and where to look.

FIRST MESSAGE BACK TO ME (no work yet): confirm repo + branch + head, start
the playtest server from /tmp/wh-worldfeat/prototype (port 8793 or tell me
which), verify it serves CONFIG with pixelatedBodies + internalResDiv keys,
and give me the exact URL to play. Then ask what my first change order is.