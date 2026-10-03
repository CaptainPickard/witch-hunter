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

## Astrabot findings (2026-10-03, weapon mount)

Root cause confirmed at 6cb9092: feat player.js setWeapon() attached the
longsword to the R_Hand bone (whanim2 runtime was present) but with a stale
pre-whanim3 static orientation - mesh.rotation.set(0, 0, Math.PI) in hand
space, not dev's measured mount quaternion. Hand-tuned static rotation in a
skinned bone socket tips the blade backward, so the hilt faces the enemy;
scales were hardcoded 0.9/0.8 (sword/axe), both ~1.8-2.0m assets.

Changes (ONE commit, feat/world-visuals, no pushes):
- prototype/js/player.js:135-149 - ported dev 8f777bb measured mount verbatim:
  rest-socket hand quaternion, oldTipWorld=(0,1,0)*q, cant=(+0.12x,+0.12z),
  desiredWorld=oldTip.negate()+cant, setFromUnitVectors((0,-1,0), desiredLocal)
  -> mesh.quaternion. Blade tip (-Y of GLB) leads strikes; pommel below the
  fist; follows the hand through idle/walk/all 3 combo stages because it is
  parented to the animated R_Hand bone.
- prototype/js/CONFIG.js:501-507 - CONFIG.assets.weaponScaleEnabled=true,
  weaponTargetHeight {longsword: 1.05m, handAxe: 0.6m} (soul-like hand-held
  vs the 1.8m player).
- prototype/js/assets.js:186-198, 401 - WH_ASSETS.weaponScale(name):
  target / MEASURED GROUND_META height of the loaded GLB (all weapon GLBs are
  uniform-axis, identity node transform, single mesh, so box height IS
  blade+grip+pommel length); kill switch + no-table/no-meta -> 1.
- prototype/js/game.js:755-758 - sword.setScalar(hardcoded 0.9) ->
  weaponScale('longsword').
- prototype/js/enemy.js:60-77 - bandit handAxe: hardcoded 0.8 ->
  weaponScale('handAxe') + same measured mount quaternion (hand-axe GLB is
  also blade-up/-tip-Y along Y). Stand-in pivot fallback kept as-is.

Measured GLB dimensions (glTF POSITION accessor min/max, pixelated variants
byte-identical bounds to raw): longsword Y-length 1.9881m, X 0.4593, Z 0.1401;
handAxe Y-length 2.0040m, X 0.7346, Z 0.2456. Derived scales: longsword
1.05/1.9881 = 0.5281 (in-game blade length 1.05m vs 1.79m before); handAxe
0.6/2.0040 = 0.2994 (in-game 0.60m vs 1.60m before). weaponScale computes
these at boot from GROUND_META, so a future remesh re-derives automatically.

Not ported / notes: player.js keeps feat's whanim2 setWeapon skeleton (socket
path + pivot fallback) - only the orientation inside the socket path changed;
resetWeaponPose and the rigid stand-in pivot table are untouched. The bandit
axe previously had NO orientation call (it rode the GLB identity - the blade
looked OK only by luck); it now shares the sword's measured cant.

Validation per Nicko's hard laws: no harness/automated runs; esprima
parseScript passed on all five edited files; no servers touched; no pushes.
Nicko should see (8793 reload): at rest the sword hangs from the right fist
pommel-down, blade pointing out/forward-ish, hand visually on the grip; the
tip swings ahead of the fist through all 3 combo swings; sword reads ~1.05m,
about hip-height-of-player; bandit axes read short (~0.6m) and bit-first.

Commit amended in place on feat/world-visuals (by construction the
brief cannot hold its own final hash - git log -1 on the branch is
authoritative; no push, IO pushes).
