# Astrabot Mission Brief - weapon placement, rotation, scale (2026-10-03)

Nicko change order (verbatim): "weapon placement, rotation and size. Currently,
the sword is backwards, the hilt is facing the enemy, making it seem as if the
player is holding the blade of the sword. Also weapons in general need to be
scaled down, they are comically large and not placed well to seem like it's
being held by a hand."

Baseline: feat/world-visuals @ b2b627e in worktree /tmp/wh-worldfeat (loading
screen + spawn-facing + retry all confirmed working by Nicko). NO harness runs
- his playtest is the bar. esprima syntax checks only. ONE commit to
feat/world-visuals IN THE WORKTREE, then append "## Astrabot findings" to this
file and amend (message starts "fix: weapon mount"). NO pushes (IO pushes).
Do not touch /workspace/witch-hunter working tree, other branches, servers,
io/specs, docs/planning, art-direction GLB binaries.

## IO diagnosis (do not re-derive, but DO verify the files)
- Feat tree mounts the player's sword via a STATIC pivot: Player.setWeapon()
  adds mesh to a weaponPivot Group parented to yawFrame (prototype/js/player.js
  ~128-152; pose from a CONFIG pos/rot table applied in resetWeaponPose()), and
  game.js ~755 hardcodes sword.scale.setScalar(0.9). A static yawFrame pivot
  does not follow the hand bone through skeletal swing animations - the arm
  animates, the sword does not, and the rest pose is hand-tuned (backwards).
- Dev ALREADY solved this: dev commits whanim2 (dc697ce, bone-socket weapons)
  and whanim3 (8f777bb, "longsword mounts on the R_Hand socket with measured
  orientation - strike axisDot min +0.5164 / mean +0.6381 tipLeads=True;
  pre-build pommel-first, Nicko-reported hilt-first contact"). The feat branch
  forked BEFORE these - that is why the problem is back here.
- Manifest weapons: longsword + handAxe (prototype/js/assets.js MANIFEST).
  Check who wields handAxe (bandit?) and where its mount happens.

## Your task
A) Port dev's bone-socket weapon mount to the feat tree: read how dev does it
   (`git show 8f777bb -- prototype/js/player.js prototype/js/anim.js
   prototype/js/CONFIG.js` from /workspace/witch-hunter, and read dev's current
   prototype/js/player.js weapon-mount sections as reference), then implement
   the socket attach in the FEAT tree's player.js (it has the skinning/anim
   runtime from whanim2, so socket bones exist). The sword must:
   - hang from the R_Hand socket with dev's measured orientation (port the
     constants/approach; do not re-invent),
   - follow the hand through idle, walk, and all 3 combo swing stages,
   - grip at the hilt (hand on grip, blade outward, pommel below the fist).
B) Scale all manifest weapons to hand-held, soul-like proportions derived from
   MEASURED model bounds (assets.js GROUND_META machinery measures loaded GLBs):
   longsword total length ~1.0-1.1m vs the ~1.8m player; hand-axe ~0.55-0.65m;
   scale computed from the measured GLB bound - not magic constants - and
   applied per weapon with CONFIG data (e.g. CONFIG.assets.weaponScale or a
   per-weapon table), default on.
C) Leave stand-in/retry/loading-screen/spawn-facing work untouched. No changes
   to vendor/, server.py, index.html (except nothing needed), art GLBs.
D) Keep the diff tight (~120 lines max incl. CONFIG data). If a needed dev-side
   helper is too entangled with combat-ds1 to port cleanly, implement the
   socket attach minimally in feat's own style and say so in your findings.

## Acceptance (Nicko plays and confirms)
- Hilt in hand at rest and through swings; blade leads strikes (no pommel-first).
- Weapons proportionate to hands/bodies; nothing comically large.
- Placement plausible at the hand with no gross clipping through leg/ground
  at rest.

## Player copy law: never "free"; no hardcoded agent names.