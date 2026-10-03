# Astrabot report: chain-attack animation clips (headless Blender)

Brief: `io/missions/2026-10-04-astrabot-chain-clips-brief.md` (Nicko 10-04 order: pose variety).
Branch `feat/world-visuals`, worktree `/tmp/wh-worldfeat`. No browser was run at any point.
Acceptance is Nicko's playtest.

## Assets

| file | sha256 | note |
|---|---|---|
| `art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.glb` | `9658044ff5961ffe9d171597016edb3df9a2ea12f7d8d5b1a9c9513076b41401` | ORIGINAL, same hash before and after all Blender work |
| `art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb` | `9ca71111937cf8bfeb1e167d7f17ff42fe07c26a578d95844ad76aaed13f9d3f` | copy + 3 chain clips (4.54 MB) |

Rebuild from source (deterministic):

```sh
R=art-direction/3d/assets/races_regen/rigged
cp $R/human-hunter-male.rigged.glb $R/human-hunter-male.combat-chain.glb
/opt/blender-4.5.4-linux-x64/blender --background --factory-startup \
  --python scratch/blender_chain_clips.py -- \
  $R/human-hunter-male.combat-chain.glb $R/human-hunter-male.combat-chain.glb --log /tmp/solve.json
python3 scratch/verify_chain_clips.py $R/human-hunter-male.rigged.glb $R/human-hunter-male.combat-chain.glb
# optional QA renders (Cycles CPU; EEVEE needs libEGL, which this host lacks):
/opt/blender-4.5.4-linux-x64/blender --background --factory-startup \
  --python scratch/blender_chain_clips.py -- $R/human-hunter-male.combat-chain.glb --preview /tmp/prev
```

The script refuses input that already has more than the 6 original clips, so it cannot double-author.

## Method

- Blender 4.5.4 LTS glTF import of the copy, then three new actions. Every bone, including Root,
  gets T/R/S keys on every 24 fps frame. That gives 60 channels, the same layout as the existing clips.
  Each action gets its own muted NLA track, next to the 6 imported tracks.
- Key poses use the rig script's convention (`tools/rigging/scripts/rig_wh_humanoid.py`):
  rotations are about the armature axes in the parent's posed frame. Torso, legs and left arm are
  authored by hand. The **right arm is solved** with a small Nelder-Mead over UpperArm/Forearm/Hand.
  The R_Hand socket goes to an authored position, and the hand-local +Z axis goes to an authored
  blade direction. In-game, +Z is the axis `player.js setWeapon` maps the longsword tip onto,
  so the tip follows the arc by construction. A Blender pose-evaluation cross-check guards the
  solver's forward kinematics (asserted at every integer phase key).
- Interpolation uses cubic Hermite per channel. Extreme keys (guard, windup, follow-through, thrust
  hold) have zero tangents, which gives the ease-in-out. The mid-strike contact key on the slashes
  passes through (Catmull-Rom tangent), so the blade doesn't stop at contact. The result is baked
  LINEAR on every frame, plus the exact phase-boundary subframes.
- Phase keys sit at the CONFIG stage proportions, so anim.js can seek per-move clips proportionally:
  - slashes 0.14/0.20/0.30 s: 15 frames = **0.625 s**. Windup ends at frame 3.28, strike ends at
    7.97. Strike is **31 %** of the clip.
  - thrust 0.16/0.14/0.40 s: 16 frames = **0.667 s**. Windup ends at frame 3.66, strike ends at
    6.86, and the extension is held to 9.14. Strike is **20 %** of the clip (the brief said ~22 %;
    20 % is exactly 0.14/0.70).
- Export: `export_force_sampling=False`. Re-sampling at the 24 fps scene rate would have changed the
  30 fps originals: WH_Run went 0.600 to 0.583 s, WH_Death 1.200 to 1.167 s, and WH_Attack1 drifted
  by up to 0.075. Unsampled export keeps them exact, and the new clips are already baked.

## Round-trip verification (`scratch/verify_chain_clips.py`, plain struct/json + numpy FK)

- animations (9): WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run, **WH_SlashL2R, WH_SlashR2L,
  WH_Thrust**, WH_Walk. The original 6 are all present.
- skin joints: **20**, same order. Single mesh node WH_Body.
- bone rest TRS: max diff 5.2e-06. Inverse binds: max diff 1.1e-05. So the R_Hand weapon socket
  basis (weaponMount) is unchanged.
- embedded image `Image_0` (jpeg) is byte-identical (sha256 5128640c3c3e...). Material names are unchanged.
- original 6 clips: 60 channels each, durations 0.5/1.2/0.333/2.0/0.6/1.0 s, max diff 1.2e-05.
- new clips: 60 channels each, LINEAR, Root static (no root motion), and each starts and ends in guard.
- result: `VERIFY PASS`.

### R_Hand samples per clip (glTF/game model space: +Z forward, -X character's right, +Y up)

Blade = hand-local +Z (the weapon-tip axis). Rest guard: pos (-0.415, 0.042, 0.108), blade (0.06, 0.18, 0.98).

**WH_SlashR2L** (0.625 s): cocked high back-right, flat sweep through the front, follow-through left.

| key | t (s) | R_Hand pos | blade |
|---|---|---|---|
| first (guard) | 0.0000 | (-0.415, 0.042, 0.108) | (0.061, 0.182, 0.981) |
| windup end | 0.1367 | (-0.502, 0.801, -0.118) | (-0.523, 0.604, -0.601) up/back-right |
| mid strike (contact) | 0.2344 | (-0.118, 0.499, 0.503) | (-0.018, 0.092, 0.996) forward |
| strike end | 0.3320 | (0.322, 0.419, 0.299) | (0.924, -0.074, 0.376) out left |
| last (guard) | 0.6250 | (-0.415, 0.042, 0.108) | (0.061, 0.182, 0.981) |

Hand x sweeps -0.50 to +0.32 (0.82 wide). Torso yaw goes -38 to +42 deg (split Hips/Spine/Chest).

**WH_SlashL2R** (0.625 s): coiled low-left, rising diagonal, finish high right.

| key | t (s) | R_Hand pos | blade |
|---|---|---|---|
| first (guard) | 0.0000 | (-0.415, 0.042, 0.108) | (0.061, 0.182, 0.981) |
| windup end | 0.1367 | (0.201, 0.042, 0.222) | (0.589, -0.721, -0.365) down/left |
| mid strike (contact) | 0.2344 | (-0.119, 0.359, 0.502) | (-0.315, 0.545, 0.777) forward-up-right |
| strike end | 0.3320 | (-0.411, 0.673, 0.204) | (-0.610, 0.792, 0.021) up-right |
| last (guard) | 0.6250 | (-0.415, 0.042, 0.108) | (0.061, 0.182, 0.981) |

Hand x sweeps +0.20 to -0.41 while rising y 0.04 to 0.67. Torso yaw goes +34 to -40 deg, with a
crouch in the windup (Hips -0.06, knees bent). It reads differently from R2L (low start, diagonal
rise) and from WH_Attack1, which is an overhead chop (see `scratch/chain-clips-qa/sheet_WH_Attack1.png`).

**WH_Thrust** (0.667 s): chamber at the right hip, straight lunge, short hold, back to guard.

| key | t (s) | R_Hand pos | blade |
|---|---|---|---|
| first (guard) | 0.0000 | (-0.415, 0.042, 0.108) | (0.061, 0.182, 0.981) |
| windup end | 0.1524 | (-0.361, 0.299, -0.201) | (0.041, 0.059, 0.997) cocked, aimed forward |
| mid strike | 0.2190 | (-0.410, 0.309, 0.318) | (0.022, 0.434, 0.901) |
| strike end | 0.2857 | (-0.112, 0.391, 0.675) | (-0.114, 0.253, 0.961) forward |
| last (guard) | 0.6667 | (-0.415, 0.042, 0.108) | (0.061, 0.182, 0.981) |

Hand z goes -0.20 to +0.68 (0.88 forward travel) with the blade forward throughout. Lunge step:
R_Thigh -42 deg with the knee bent 40, the left leg extended behind, Hips -0.07. Root stays at
the origin; the game-side lunge (CONFIG lunge 1.4) moves the player.

Solver residuals per key are in `scratch/chain-clips-qa/solve-log.json`. Most keys are within
0.4 cm / 5 deg. Exceptions:
- L2R windup is 2.9 cm off.
- L2R follow-through is 4.7 cm off (a straight arm at full reach).
- The thrust extension and hold are about 3.7 cm / 13 deg off. The wrist limit leaves the blade
  tipped about 13 deg upward, aimed at chest height.

QA contact sheets (front / side / top, red bar = blade proxy on R_Hand +Z) are in
`scratch/chain-clips-qa/sheet_*.png`.
- Mesh: 32835 triangles in both files. The exporter split 25805 vertices into 25812. Every
  triangle's position+UV matches the original within 1.0e-05 (KD-tree, cyclic vertex order), so
  the R4 pixelated atlas still lines up. `swapBodyMap` keys `BODY_PNG` by the logical name
  `playerBody` and swaps whatever `m.map` it finds, so it is path-independent and needs no change.

## Wiring (step c, minimal diff)

- `prototype/js/assets.js`: `playerBody` now points to `human-hunter-male.combat-chain.glb`. A
  comment keeps the rollback path (`human-hunter-male.rigged.glb`). `BODY_PNG.playerBody` is unchanged.
- `prototype/js/anim.js` follows the file's own convention, a name table next to `NAMES`:
  - new `MOVE_NAMES = { slashR2L: 'WH_SlashR2L', slashL2R: 'WH_SlashL2R', thrust: 'WH_Thrust' }`.
    The constructor builds LoopOnce/clamp actions only for clips the body actually has, so enemies
    and the old GLB stay silent.
  - `syncPlayer` passes `player.attackMoveId` into `playerAttack(..., moveId)`. That picks the
    per-move action, and falls back to `'attack'` (WH_Attack1) for handAxe hack/chop, any unmapped
    move, or a body without the clip. A chain step onto a different clip crossfades over
    `oneShotFadeSeconds`. Repeats of the same clip re-seek without a self-crossfade, as before.
  - `seekAttack(seg, t, durations, key)`: the shared WH_Attack1 keeps the
    `attackClipStrikeFraction` segmentation (enemies and handAxe behave exactly as before).
    Per-move clips take their segment edges from the move's own CONFIG
    windup / windup+strike fractions, which is where the clip keys were authored.
  - `getState()` also reports the per-move clip name and its weight.
- CONFIG: untouched. No new knobs; the weaponMount numbers and all combat/enemy logic are unchanged.
- Static check: `esprima.parseScript` passes for anim.js and assets.js. No browser or headless smoke run.

## Left for Nicko's playtest

- Read of the three swings in motion: blade arc, the 0.08 s crossfade between chain steps, and the
  thrust's upward blade tilt (about 13 deg) at full extension.
- Pose tuning lives in `scratch/blender_chain_clips.py` `KEYS` (hand target, blade direction and
  torso twist per key). Rerun the rebuild block above and the verifier.
