# Witch Hunter — Blender Rigging Runbook (Meshy GLB → rigged, animated GLB)

Audience: an AI agent team that is **not** Blender-expert. Follow the steps in order.
Every step is tagged **VERIFIED** (run on `human-hunter-male.glb` in this container on
2026-10-01 with Blender 4.3.2 headless) or **UNVERIFIED** (with the exact failure).

Deliverables in this folder:

| Path | Purpose |
|---|---|
| `scripts/bl.sh` | Headless Blender wrapper with the two environment fixes (use it for EVERY call) |
| `scripts/inspect.py` | Step 2 inspection: objects, bounds, tris, images, texture interpolation |
| `scripts/rig_wh_humanoid.py` | The whole pipeline: import → landmarks → rig → weights → clips → export |
| `scripts/verify_wh_glb.py` | Validator + headless preview renderer (see `VERIFY.md`) |
| `VERIFY.md` | Validator checklist |
| `out/human-hunter-male.rigged.glb` | Reference output for the sample (6 clips, VERIFY PASS) |
| `out/rig.log`, `out/verify.log` | Logs of the reference run |
| `previews/final/*.png` | Reference preview frames (front + side) |

---

## 0. Prerequisites and environment quirks

| Item | Value / action | Status |
|---|---|---|
| Blender | 4.3.2 from apt (`/usr/bin/blender`). If missing: `DEBIAN_FRONTEND=noninteractive apt-get install -y blender python3-numpy` | VERIFIED present |
| numpy | apt `python3-numpy` 2.2.4 in `/usr/lib/python3/dist-packages` (needed by the glTF importer) | VERIFIED |
| **Quirk 1: sqlite** | `/usr/local/lib/libsqlite3.so.0` shadows the system lib → `blender: symbol lookup error: /lib/x86_64-linux-gnu/libgdal.so.36: undefined symbol: sqlite3_column_table_name`. Fix: `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libsqlite3.so.0` | VERIFIED (fails without, works with) |
| **Quirk 2: wrong Python (new finding)** | `~/.local/bin` contains a uv-managed `python3.13` that comes first on `PATH`. Blender then uses it as its interpreter, can't see apt numpy, and every GLB import fails with `ModuleNotFoundError: No module named 'numpy'`. `PYTHONPATH` does **not** help (Blender ignores it). Fix: run Blender with `PATH=/usr/sbin:/usr/bin:/sbin:/bin` | VERIFIED |
| Wrapper | `scripts/bl.sh` applies both fixes and runs `blender -b --factory-startup "$@"`. **Always call Blender through it.** | VERIFIED |
| Render engine | `BLENDER_EEVEE_NEXT` renders headless (it prints harmless `EGL Error (0x3009): EGL_BAD_MATCH` lines). `CYCLES` fails with `Failed to denoise, build has no OpenImageDenoise support`. Workbench works but shows no texture by default | VERIFIED |

The raw call, if you can't use the wrapper:

```sh
PATH=/usr/sbin:/usr/bin:/sbin:/bin \
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libsqlite3.so.0 \
blender -b --factory-startup --python scripts/rig_wh_humanoid.py -- IN.glb OUT.glb
```

**CLI form (binding):** `blender -b <in.glb> --python ...` does **NOT** work. Blender
tries to open the GLB as a .blend file: `Error: File format is not supported in file
".../human-hunter-male.glb"` (VERIFIED). Pass input and output after `--`:

```sh
scripts/bl.sh --python scripts/rig_wh_humanoid.py -- IN.glb OUT.glb [options]
```

---

## 1. One-shot pipeline (what you normally run)

```sh
cd /tmp/opus-rigging
scripts/bl.sh --python scripts/rig_wh_humanoid.py -- human-hunter-male.glb out/human-hunter-male.rigged.glb
scripts/bl.sh --python scripts/verify_wh_glb.py   -- out/human-hunter-male.rigged.glb human-hunter-male.glb --render previews/final
```

**VERIFIED**: rigging takes about 5 s, validation about 2 s, and EEVEE previews a few seconds per frame. Outputs:
`OUT.glb` (4.46 MB), `OUT.blend` (editable source, keep it next to the GLB), and logs.

Options of `rig_wh_humanoid.py`:

| Option | Default | Use |
|---|---|---|
| `--clips WH_Idle,WH_Walk,...` | all six | generate a subset |
| `--fps N` | 30 | clip sampling rate |
| `--hip-ratio F` | 0.52 | hip-joint height as a fraction of the mesh height (lower it for short-legged or hunched characters) |
| `--knee-ratio F` | 0.28 | knee height fraction |
| `--save-blend PATH` | `OUT.blend` | where to save the rigged .blend |
| `--clips-only` | off | IN is a rigged `.blend` from an earlier run: only (re)generate the listed clips and re-export (§8) |

The rest of this runbook explains each stage, what to check, and how to fix it.

---

## 2. Import and inspect — VERIFIED

```sh
scripts/bl.sh --python-expr "import bpy;bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath='IN.glb')" --python scripts/inspect.py
```

Facts measured on the sample (expect similar values on other Meshy exports):

| Property | Sample value | Notes |
|---|---|---|
| Objects | 1 mesh `Mesh_0`, identity transform, no armature, no animations | |
| Vertices / triangles | 25 745 / **32 835** | triangle count is the invariant we check later |
| Bounds (Blender, Z up) | x ±0.477, y ±0.346, z −1.0…+1.0 | height H = 2.0; glTF Y-up becomes Blender Z-up on import |
| Facing | character faces **−Y** in Blender (= +Z in glTF/Three.js) | character's left = +X |
| Pose | **A-pose**: arms about 19° from vertical (script prints `arm angle from vertical`) | 0° = arms down, about 90° = T-pose |
| Texture | **one 2048×2048 JPEG** embedded, sampler **LINEAR / LINEAR_MIPMAP_LINEAR** | ⚠ the brief said "512px NEAREST". On this sample the pixelation is baked into a 2048 JPEG with linear filtering. The pipeline keeps whatever the source has; a NEAREST variant was also tested (§6) |
| Material | 1 material, doubleSided, metallic 0, roughness 0.8 | |
| Geometry | open shells, about 35 coincident duplicate vertices | Bone Heat fails on it as-is (§4) |

**Check**: exactly one mesh, a plausible height, arm angle printed between 0 and 60 (A-pose) or about 90 (T-pose).
A T-pose works with the same script, but its clips were not tested.

---

## 3. Landmarks and rig construction — VERIFIED

`detect_landmarks()` measures the mesh, so bulkier orcs and hunched ghouls get bones that
fit them. It uses no hard-coded coordinates. Everything is a fraction of the mesh height
H above the floor `z0`:

| Joint | How it is found |
|---|---|
| Shoulder top | scanning down from the head, the first 1.25%-H slice whose 99th-percentile half-width reaches 75% of the widest upper-torso slice (0.70–0.85 H). Sample: 0.813 H |
| Shoulder joint | 0.75 × torso half-width at the shoulder, 0.035 H below the shoulder top |
| Hand | centroid of the most lateral vertices (within 0.03 H of max \|x\|) in the arm band 0.35 H … shoulder−0.08 H. The wrist and hand tip lie ±0.035 H along the shoulder→hand direction |
| Elbow | midpoint of shoulder→wrist, pushed 0.015 H backward so the bend direction is defined |
| Feet / ankles | the boot blobs below 0.12 H (under the cloak hem) give foot x, ankle y and the toe tip (2nd-percentile y) |
| Hip joints | height `--hip-ratio` (0.52); x = 0.75 × foot x, clamped to 0.04–0.08 H |
| Knees | `--knee-ratio` (0.28), halfway between hip x and foot x, 0.015 H forward |
| Spine / chest / neck / head | x = 0; y = mid-depth of the central body slice (handles hunched characters); heights between hips and shoulder top; head tail = mesh top |

**Bone topology (binding, 20 bones; 19 deform + non-deforming Root):**

```
Root (at the floor, never animated, use_deform=False)
└─ Hips
   ├─ Spine ─ Chest ─┬─ Neck ─ Head
   │                 ├─ L_Shoulder ─ L_UpperArm ─ L_Forearm ─ L_Hand
   │                 └─ R_Shoulder ─ R_UpperArm ─ R_Forearm ─ R_Hand
   ├─ L_Thigh ─ L_Shin ─ L_Foot
   └─ R_Thigh ─ R_Shin ─ R_Foot
```

- `L_` = **character's** left (+X in Blender). Use **no dots**: Three.js `PropertyBinding.sanitizeNodeName`
  strips `.` so `Shoulder.L` would become `ShoulderL` and break name lookups.
- Pose bones use quaternion rotation mode.
- Future characters must use exactly these names and this parenting. The script asserts the set.

**Check** (in `out/rig.log`): the `[WH] bounds … shoulder_top=…H arm angle …` line looks plausible.
Then look at the REST preview (§7): the bones are not drawn in renders, so judge from how the
WH_Walk and WH_Attack1 frames bend. If the knees bend in the wrong place, adjust `--knee-ratio`. If the
pelvis or crotch tears, adjust `--hip-ratio`.

---

## 4. Skinning (automatic weights) — VERIFIED, with a required workaround

| Attempt | Result (sample) |
|---|---|
| `parent_set(type='ARMATURE_AUTO')` directly on the Meshy mesh | ❌ `Bone Heat Weighting: failed to find solution for one or more bones`, **25 745 / 25 745 vertices unweighted** |
| Weld the proxy by distance (0.002 H) | ❌ all unweighted |
| Voxel-remeshed proxy (0.006–0.01 H), at 1× or 10× scale | ❌ all unweighted |
| Original mesh scaled 10× | ❌ all unweighted |
| **Welded proxy (0.002 H) and 10× scale (proxy + temporary armature copy)** | ✅ 20 / 16 251 proxy vertices unweighted |

So `skin()` does this:

1. Copy the mesh into a **throw-away proxy**, weld it by distance, scale it and a temporary armature copy ×10, run Bone Heat, then scale the proxy back.
2. Transfer weights to the **real, untouched** mesh with a `DATA_TRANSFER` modifier
   (`VGROUP_WEIGHTS`, `POLYINTERP_NEAREST`). Sample: 108 vertices left unweighted.
3. **Arm radius clamp.** Heat weights leak from the hand and forearm into the cloak hanging
   beside them (seen in previews: the cloak "flew" with the arms in WH_Hit and spread like wings in WH_Death).
   Weights farther than 0.07 H (UpperArm) or 0.06 H (Forearm, Hand) from the bone are removed
   (23 216 weights removed; Hand influence dropped from about 8 300 to about 470 vertices per side). Constants: `ARM_RADIUS`.
4. Nearest-bone fill for the remaining unweighted vertices (it respects the arm radius limits).
5. Bind with `parent_set(type='ARMATURE')`. This adds the Armature modifier and keeps the vertex groups.
6. Clean (<0.01), limit to 4 influences (glTF/Three.js limit), normalize.
7. Assert that a hash of the vertex coordinates is unchanged. **Geometry is never modified.**

**Check**: the log shows `final weights: 0 unweighted` and every one of the 19 deform bones has
a vertex count above 0. Known coarse areas: the cloak follows the thighs (it swings with the legs), and
`L_Hand` also holds the lantern. Both are acceptable for the game's camera distance.

---

## 5. Procedural clips — VERIFIED (all six generated, exported, re-imported, rendered)

All clips are **in place**: `Root` is never keyed, Hips only bob vertically (and pitch/yaw), loops
end on the exact first pose, and the glTF animations are sampled LINEAR at 30 fps.

| Action (exact name) | Length | Loop | Content |
|---|---|---|---|
| `WH_Idle` | 2.0 s (61 keys) | yes | breathing: chest/spine pitch, shoulder lift, 0.002 H hip settle, slight head sway |
| `WH_Walk` | 1.0 s (31) | yes | thigh ±24°, swing knee up to 44°, compensated feet, counter arm swing, 2 bobs per cycle (0.01 H) |
| `WH_Run` | 0.6 s (19) | yes | thigh ±38°, knee 89°, elbows 65°, lean 12°, bob 0.022 H |
| `WH_Attack1` | 0.5 s (16) | no | 0–0.15 s windup (right arm overhead, chest twist back) → 0.25 s strike (arm forward-down, lunge) → hold → recover by 0.5 s |
| `WH_Hit` | 0.33 s (11) | no | flinch back (spine, chest, head), arms up, recover |
| `WH_Death` | 1.2 s (37) | no | knees buckle (0.36 s) → falls backward to the floor (0.9 s) → holds the rest pose. Hips drop to 0.07 H above the floor (computed from the landmarks) |

**How poses are authored:** a clip is a function `pose(t)`, where t = 0..1 over the clip. It returns
`{bone: {"rx","ry","rz": degrees, "lx","ly","lz": units of H}}`. Rotations are about
**armature axes** (X = character-left, −Y = forward, Z = up), applied in each bone's parent frame and
converted to bone-local quaternions by conjugating with the rest orientation (`to_local_quat`).
This makes clips **independent of bone roll and of the character's proportions**, so the same clip code
works on every character with the WH topology. Sign cheat-sheet:

- `rx > 0`: an up-pointing bone (spine) leans **forward**; a down-pointing bone (thigh, upper arm) swings **back**, and shins bend the knee.
- `rx < 0` on a thigh or arm = swing **forward**. Forearm `rx < 0` = bend the elbow.
- `ry`: side bend. For L limbs `ry < 0` raises the arm outward; for R use the opposite sign (`S(side)` helper).
- `rz`: yaw. On the chest, `rz < 0` turns the right shoulder back.

Helpers: `keyposes([(t, pose), ...])` gives smoothstep blends between key poses (attack, hit, death);
`gait()` is the shared walk/run cycle.

`bake_clip()` keys every frame (rotation for all bones except Root, plus location for Hips), puts each
action on its **own muted NLA track** with a fake user (the exporter needs this, see §6), then clears the active action.

**Check:** the log has one `clip WH_x: N keys @ 30 fps` line per clip, and the validator reports `loop closes` and
`Root static` for every clip (VERIFY.md §5).

---

## 6. Export — VERIFIED

```python
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB",
    export_animation_mode="ACTIONS", export_skins=True, export_def_bones=False,
    export_apply=False, export_image_format="AUTO", export_yup=True,
    export_force_sampling=True, export_optimize_animation_size=False,
    export_anim_slide_to_zero=True, export_reset_pose_bones=True,
    export_cameras=False, export_lights=False, export_extras=False)
```

Measured on the sample output:

| Property | Result |
|---|---|
| Structure | scene root `WH_Armature` → 20 joint nodes + skinned mesh node `WH_Body` (1 skin, 1 primitive, `JOINTS_0`/`WEIGHTS_0`) |
| Animations | exactly `WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run, WH_Walk`; 60 channels each (T/R/S × 20 bones); LINEAR |
| Texture | **JPEG bytes bit-identical** (sha256 match). Sampler preserved (LINEAR source → LINEAR). A NEAREST source (sampler patched to 9728/9984) → output 9728/9984, also bit-identical |
| Triangles | 32 835 = source |
| Vertices | 25 805 vs 25 745 (+60, 0.23%). The exporter splits a few vertices whose per-loop custom normals round-trip with tiny float differences. The distinct (position, uv) set is **identical** (25 710 = 25 710); bind-pose bounds are identical |
| Material | doubleSided true, metallic 0, roughness 0.8 (unchanged) |
| Size | 4.46 MB (source 3.9 MB; the extra is skin and animation data) |

Do not:
- set `export_apply=True` (it bakes the Armature modifier and ships a frozen mesh),
- enable Draco or mesh optimisation, or set `export_image_format` to WEBP/JPEG (that re-encodes the texture),
- leave actions only in `bpy.data`. With `ACTIONS` mode, an action that is neither active nor on an NLA track is not exported.

---

## 7. Verify the export — VERIFIED

```sh
scripts/bl.sh --python scripts/verify_wh_glb.py -- OUT.glb SOURCE.glb \
   --render previews/<char> --frames REST:1,WH_Idle:31,WH_Walk:8,WH_Walk:23,WH_Attack1:5,WH_Attack1:9,WH_Hit:4,WH_Death:36
```

The validator prints `VERIFY PASS` and exits 0 (sample: 43 checks pass). See `VERIFY.md` for every check and
what to look for in the previews. Frame numbers are frames of the **re-imported** GLB: clips start at frame 0, so frame = 30·t (t in seconds). Frames past the end hold the last pose.

---

## 8. Adding a new clip later — VERIFIED (`--clips-only` path)

1. In `scripts/rig_wh_humanoid.py`, write `def pose_myclip(t): return {...}` (or build one with `keyposes`).
2. Register it: `CLIPS["WH_MyClip"] = (lambda L: pose_myclip, duration_s, loop_bool)`.
   Use `(factory_using_L, …)` if the clip needs landmarks, as `WH_Death` does.
   Names must start with `WH_` and are case-sensitive in Three.js.
3. Then use **either**:
   - **Full rebuild** (deterministic; recommended): rerun §1 on the original Meshy GLB.
   - **Append to an existing rig**, without re-rigging or re-weighting:
     ```sh
     scripts/bl.sh --python scripts/rig_wh_humanoid.py -- out/char.rigged.blend out/char.rigged.glb \
         --clips-only --clips WH_MyClip
     ```
     Existing actions in the .blend are kept. Clips listed with `--clips` are regenerated (replaced).
     VERIFIED: a 3-clip rig plus `--clips-only --clips WH_Run,WH_Hit,WH_Death` gave 6 clips, VERIFY PASS.
4. Rerun the validator with `--require` listing all expected clips, and add the new clip to
   `ALL_CLIPS` / `LOOPS` in `verify_wh_glb.py`.

Do **not** build new clips on a re-imported GLB. The importer renames actions (`WH_Idle` →
`WH_Idle_WH_Armature`) and changes bone rolls ("Blender" bone-direction heuristic). Always keep the
`.blend` that the rig step saves.

---

## 9. Per-stage checklist

| Stage | Pass criteria | Where to look |
|---|---|---|
| Env | `scripts/bl.sh --python-expr "import numpy"` prints no error | console |
| Import | 1 mesh, H > 0, triangle count recorded | `inspect.py` |
| Landmarks | `shoulder_top` 0.75–0.88 H; arm angle 0–60° (A) or about 90° (T); L/R angles within 5° of each other | `[WH] bounds` line |
| Rig | 20 bones with the exact names (asserted in the script) | script would raise |
| Weights | proxy heat weights mostly OK (proxy unweighted < 1%); `final weights: 0 unweighted`; every deform bone > 0 | `[WH] heat…`, `[WH] final weights` |
| Geometry | no `mesh geometry changed` assertion | script would raise |
| Clips | 6 `[WH] clip` lines with the expected durations | log |
| Export | file written, size about 1.1–1.2× the source | `[WH] exported` |
| Validation | `VERIFY PASS`, exit 0 | `verify_wh_glb.py` |
| Eyeball | previews: walk legs alternate (front/side), attack arm overhead then forward, death body flat on the floor, cloak not "winged" | `previews/<char>/` |

## 10. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `undefined symbol: sqlite3_column_table_name` | /usr/local sqlite shadows the system lib | `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libsqlite3.so.0` (use `bl.sh`) |
| `ModuleNotFoundError: No module named 'numpy'` during GLB import | Blender picked up the uv python3.13 from `~/.local/bin` | `PATH=/usr/sbin:/usr/bin:/sbin:/bin` (use `bl.sh`). PYTHONPATH does not work |
| `File format is not supported` | GLB passed as Blender's main file (`blender -b in.glb`) | pass it after `--` |
| `Failed to denoise, build has no OpenImageDenoise support` | Cycles render | use EEVEE (`BLENDER_EEVEE_NEXT`) |
| `Bone Heat Weighting: failed to find solution…`, all vertices unweighted | open, unwelded Meshy shells and small absolute size | welded ×10 proxy and weight transfer (built into `skin()`). If it still fails on a new asset, raise the weld threshold (0.002 H → 0.004 H) in `heat_weight_proxy` |
| Cloak or robe lifts with the arms | heat weights leak from the arm bones into nearby cloth | lower `ARM_RADIUS` (e.g. Hand 0.05) and re-run |
| Robe splits between the legs while walking | cloth weighted to L_ and R_Thigh | expected with 19 bones. Lower the stride (`gait(stride=…)`) or add a cloth bone later (topology change: needs a team decision) |
| Knees or elbows bend in the wrong place | landmark ratio mismatch (stubby or long-legged character) | `--knee-ratio`, `--hip-ratio` |
| Hands not found (arms tight to the body, or a weapon is the widest point) | the most-lateral-vertex heuristic picks a weapon or cloak | check the arm angle in the log. If it is wrong, restrict the band in `hand()` or pass explicit coordinates (extend the script) |
| Animation missing from the GLB | action not on an NLA track / not active | `bake_clip` pushes each action to an NLA track. Keep that if you write your own |
| Clips play but the mesh doesn't move | exported with `export_apply=True`, or the mesh is not parented to the armature | use the export call in §6. The validator checks for a skin |
| Clip names `WH_Idle_WH_Armature` | looking at a **Blender re-import** (importer renames) | harmless. The glTF names (what Three.js sees) are exact; the validator checks both |
| Loop end on a fractional frame in a Blender re-import | importer uses the scene fps (factory 24) | set `scene.render.fps = 30` before import (the validator does this) |
| Texture looks blurrier in game than the source | the exporter changed the sampler, or the image was re-encoded | the validator compares sha256 and magFilter. Keep `export_image_format="AUTO"` |
| +N vertices vs the source | normal-split on export | OK if ≤ 0.5% and the (position, uv) set is identical (validator) |

## 11. Notes for the Three.js runtime phase

- glTF facing is **+Z** and up is +Y, with the mesh in bind pose roughly y = −1…+1. The engine's height
  normalisation (scale to 1.8) and ground offset should be computed **once at load, in bind pose**, on the
  root object. Don't recompute them per frame from animated bounds (WH_Death moves the body down and back).
- `SkinnedMesh` culling uses bind-pose bounds. Set `frustumCulled = false` on `WH_Body` or enlarge its
  bounding sphere, or a dead body lying backward may pop out of view at screen edges.
- Clip lookup: `THREE.AnimationClip.findByName(gltf.animations, 'WH_Walk')`. Loops: `LoopRepeat`.
  `WH_Attack1`, `WH_Hit`, `WH_Death`: `LoopOnce` with `clampWhenFinished = true` (Death must hold its last frame).
- Every clip has T/R/S tracks for all 20 bones, including the static Root. They fully override each other
  when cross-fading, so `crossFadeTo` between any two clips is safe. Movement stays code-driven: no clip moves Root or the Hips horizontally.
- Loops repeat the first pose at the last key (t = duration). With `LoopRepeat` this gives one duplicated sample per cycle, which is not visible.
- No glTF extensions are used (`extensionsUsed` absent), so a classic (non-ESM) GLTFLoader of any recent version can load it.
