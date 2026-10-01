# VERIFY — validator checklist for a rigged Witch Hunter GLB

Run (automates §1–§6 and renders §7):

```sh
cd /tmp/opus-rigging
scripts/bl.sh --python scripts/verify_wh_glb.py -- RIGGED.glb SOURCE_MESHY.glb \
    [--require WH_Idle,WH_Walk,WH_Run,WH_Attack1,WH_Hit,WH_Death] [--fps 30] \
    [--render previews/<char> --frames REST:1,WH_Idle:31,WH_Walk:8,WH_Walk:23,WH_Attack1:5,WH_Attack1:9,WH_Hit:4,WH_Death:36]
```

- `scripts/bl.sh` = `PATH=/usr/sbin:/usr/bin:/sbin:/bin LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libsqlite3.so.0 blender -b --factory-startup`.
- Pass: last line `VERIFY PASS`, exit code 0. Fail: one `VERIFY FAIL <check>` line per failure, then `VERIFY FAILED (n checks)`, exit code 1.
- **VERIFIED** on `out/human-hunter-male.rigged.glb`: 43/43 checks pass (`out/verify.log`, `out/verify.summary.txt`). It also passed on the
  NEAREST-sampler variant and on a rig whose clips were added later with `--clips-only`.

Layer A reads the raw glTF JSON and binary buffer, which is what Three.js `GLTFLoader` sees. Layer B re-imports the file into Blender.

## 1. Structure and bones

| # | Check | Expected | Layer |
|---|---|---|---|
| 1.1 | meshes | exactly 1 | A |
| 1.2 | skins | exactly 1 | A |
| 1.3 | skin joints | exactly these 20: `Root Hips Spine Chest Neck Head L_Shoulder L_UpperArm L_Forearm L_Hand R_Shoulder R_UpperArm R_Forearm R_Hand L_Thigh L_Shin L_Foot R_Thigh R_Shin R_Foot` | A |
| 1.4 | primitives | 1, with `JOINTS_0` + `WEIGHTS_0` | A |
| 1.5 | Blender objects | 1 armature + 1 skinned mesh with an Armature modifier (the importer's hidden bone-shape icosphere is ignored) | B |
| 1.6 | armature bones | the same 20 names | B |

## 2. Vertex-group coverage

| # | Check | Expected |
|---|---|---|
| 2.1 | `WEIGHTS_0` row sums | every vertex 0.99–1.01 (no zero rows). Sample: min = max = 1.0000 |
| 2.2 | vertex groups | one per deform bone (19; Root is non-deforming) |
| 2.3 | unweighted vertices | 0 |
| 2.4 | per-bone coverage (weight > 0.05) | every deform bone > 0 vertices. Sanity on the sample: Hand about 450–480, Thigh about 14 400 (cloak), Head about 1 500. A Hand count in the thousands means weights leaked into the cloak (lower `ARM_RADIUS`) |

## 3. Geometry untouched

| # | Check | Expected |
|---|---|---|
| 3.1 | triangle count (glTF indices / 3, and Blender re-import) | == source (sample 32 835) |
| 3.2 | vertex count | source ≤ out ≤ source × 1.005 (sample 25 805 vs 25 745: the exporter splits vertices on tiny normal differences) |
| 3.3 | distinct (position, uv) pairs | **identical** to the source (sample 25 710) |
| 3.4 | bind-pose bounds | equal to the source within 1e-4 |

## 4. Texture intact (pixel look preserved)

| # | Check | Expected |
|---|---|---|
| 4.1 | image count / mimeType | same as the source |
| 4.2 | image bytes | **sha256 identical** to the source (no re-encode, no resize) |
| 4.3 | sampler magFilter | same as the source (9728 NEAREST stays NEAREST; 9729 LINEAR stays LINEAR) |
| 4.4 | sampler minFilter | printed as `note` if it differs (it did not differ in either tested variant) |

## 5. Clips and in-place-ness

| # | Check | Expected |
|---|---|---|
| 5.1 | glTF animation names | include every `--require` name **exactly** (Three.js uses these) |
| 5.2 | Root channels | every Root output key equal to its first key (Root static) in every clip |
| 5.3 | loop closure (WH_Idle/Walk/Run) | Hips translation last key == first key (drift < 1e-4) |
| 5.4 | Root world position (Blender evaluation, every frame) | drift < 1e-5 |
| 5.5 | Hips returns to start (loops) | < 1e-3 |
| 5.6 | Hips horizontal sway (loops) | < 0.05 units (sample: 0.000; Hips only bob vertically) |
| 5.7 | durations (printed) | Idle 2.0, Walk 1.0, Run 0.6, Attack1 0.5, Hit 0.333, Death 1.2 s |

Blender names re-imported actions `WH_Idle_WH_Armature` etc. The validator maps them back. This is not a defect.

## 6. Manual JSON spot-checks (optional, no Blender)

```sh
python3 - <<'EOF'
import json,struct; d=open('RIGGED.glb','rb').read(); n=struct.unpack('<I',d[12:16])[0]; j=json.loads(d[20:20+n])
print([a['name'] for a in j['animations']]); print(len(j['skins'][0]['joints'])); print(j['samplers'], j['materials'])
print(j.get('extensionsUsed'))   # expected: None (no extensions)
EOF
```

## 7. Render preview (eyeball QA)

`--render DIR --frames CLIP:FRAME,...` writes `DIR/<CLIP>_f<FRAME>_{front,side}.png` (EEVEE, 384², ortho, sun light).
`REST:1` = bind pose. Frames are re-imported frames: **frame = 30 × seconds**, starting at 0; frames past the end hold the last pose.
Front camera looks along +Y at the character's face; side camera looks from +X (character faces left).

| Frame | Look for |
|---|---|
| `REST:1` | identical to the source mesh, texture sharp (not blurrier than the source) |
| `WH_Idle:31` | almost identical to rest (breathing is subtle) |
| `WH_Walk:8`, `WH_Walk:23` (side) | legs in opposite stride phases, knee bent on the swing leg, arms counter-swinging, feet not under the floor |
| `WH_Run:5` (side) | forward lean, high knee, bent elbows |
| `WH_Attack1:5` (front) | right arm raised overhead (windup) |
| `WH_Attack1:9` (side) | arm swung forward/down, torso twisted, slight lunge |
| `WH_Hit:4` (side) | upper body and head snapped back; **cloak must hang down, not lift with the arms** |
| `WH_Death:12` / `WH_Death:36` | knees buckling → body flat on its back at floor level; **no cloak "wings"** |
| everywhere | no exploding vertices or spikes (weights on the wrong bone), no texture swimming |

Reference frames for the sample are in `previews/final/`.

## 8. Not covered (do in the Three.js phase)

- Loading in the real classic `GLTFLoader` + `AnimationMixer` (no node/npm here: **UNVERIFIED** in this container).
- Visual check at the game's camera distance and 1.8-unit scale, and cross-fades between clips.
