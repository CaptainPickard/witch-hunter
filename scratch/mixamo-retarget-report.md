# Mixamo retarget bake delivery

## Result

- `art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb`: six original clips + seven new bandit clips.
- `art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.mixamo.glb`: six original clips + seven new ghoul clips.
- Every new clip: 200 baked fcurves, 60 exported channels (20 bones x translation/rotation/scale), dense 30 fps keys starting at zero.
- `scratch/mixamo-fbx/reports/verification.json`: combined machine-readable proof, hashes, per-clip curves/channels/durations, canonical identity, render inventory and regression results.
- `scratch/mixamo-fbx/qa/{bandit,ghoul}/`: 28 mid/end PNGs, eight labelled contact sheets, per-body render/geometry JSON.
- Eight regression tests passed; opposite two-clip bake orders have identical ordered sampler bytes.
- Ground checks on all 1,308 sampled frames passed at 0.1 mm tolerance; only the actual skinned body was measured.
- No failed bakes. No modifications to `prototype/` or canonical `.rigged.glb` files. Raw FBX and account/storage files are NOT committed.

## Important content caveat

`WH_Death_Zombie` is sourced from `zombie agonizing.fbx`, the staged pack's agony clip. **Unwired by Nicko decision 2026-10-05:** the agony clip ends standing; ghoul keeps the existing rigid-fall death in `enemy.js`. Keep the baked clip in the GLB. Runtime wiring remains out of scope.

`WH_Attack_Zombie` uses the explicitly requested `singles/Zombie_Attack.fbx`; the remaining ghoul names are mapped in `scratch/mixamo_ghoul.json`.

## Root cause and evidence

`bpy.ops.nla.bake` uses `context.selected_editable_objects`, not just the active object. Each FBX import selects its source and deselects the target. The supplied script only set `view_layer.objects.active = target` and consequently baked the wrong rig, leaving its handmade target action empty. Cold reproduction gave zero target curves in both clips. Adding only explicit deselect-all/select-target changed those same clips to 200 curves each (`e20d68d`). The earlier observation of one working clip depended on selection state, not an inherent second-action limitation.

The final loop isolates every clip: reset frame range/fps after FBX import, clear active action, reset pose channels, mute NLA tracks, explicitly assign the new action/slot, select only the target, visually bake into that action, assert 200 dense fcurves, attach a muted per-clip NLA strip with its slot, and remove source data. Original actions/strips are retained in memory. The manual constraint-result fallback was not needed.

## Corrections to hand-off assumptions

- The live WH rig has **both Root and Hips**; the brief's listed map omitted Hips. Root is held still; Hips carries rotation and proportion-scaled vertical motion. Horizontal displacement is removed.
- Source armatures have a 90-degree object rotation and 0.01 scale. Raw POSE-to-POSE copy is not coordinate-compatible. WORLD-space constraints reconcile those spaces; parented source helper bones provide calibrated target bone-roll offsets. New helper edit bones need nonzero head/tail before assigning matrices.
- `use_current_action=True` works with explicit target selection and action_slot. Recovering actions with `bpy.data.actions[-1]` is unsafe: the collection is not a creation-order stack.
- Blender re-export cannot guarantee original animation byte identity. Blender exports to a temporary GLB; `scratch/glb_append_clips.py` appends only new animation data to the untouched original JSON/BIN. Every original entry and the entire original BIN prefix are preserved. Bone rest-frame compatibility is checked before remapping new channels by name.
- The supplied verifier had an undefined `jl`, omitted the BIN chunk's eight-byte header, and contained an invalid offset expression. The replacement verifies ordered accessor bytes, byteStride, prefix equality, original JSON entries, expected clip names, 60 unique bone/path channels, finite values, unit quaternions, non-frozen rotations, 30 fps keys, and a static Root.
- Positive action starts were not reliably shifted by `export_anim_slide_to_zero`. Baked keys are explicitly shifted to zero before export.
- The glTF importer creates a hidden Icosphere bone-display mesh; measuring every mesh masks character bounds. Both baking and QA now measure only meshes skinned to the target armature.

## Pose review

Every mid/end frame was reviewed through the labelled contact sheets. All 14 clips passed rigging/deformation review. Two coarse contact-sheet flags on ghoul walk-end and attack-mid were checked at full resolution: walk-end is a hunched asymmetric gait, not waist collapse; attack-mid boots are intact and the full-range skinned-vertex measurements rule out meaningful floor penetration. The death-source semantic caveat above is retained rather than hidden by a technical PASS.

## Reproduce

From `/workspace/witch-hunter`, with Blender 4.5.4:

```sh
/opt/blender-4.5.4-linux-x64/blender -b --factory-startup --python-exit-code 1 --python scratch/mixamo_retarget.py -- art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.glb art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb --clips scratch/mixamo_bandit.json --log scratch/mixamo-fbx/reports/bandit-bake.json
/opt/blender-4.5.4-linux-x64/blender -b --factory-startup --python-exit-code 1 --python scratch/mixamo_retarget.py -- art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.rigged.glb art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.mixamo.glb --clips scratch/mixamo_ghoul.json --log scratch/mixamo-fbx/reports/ghoul-bake.json
```

With a live Xvfb display `:99`:

```sh
DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=1 /opt/blender-4.5.4-linux-x64/blender -b --factory-startup --python-exit-code 1 --python scratch/rt_render_qa.py -- art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb --clips scratch/mixamo_bandit.json --out scratch/mixamo-fbx/qa/bandit
DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=1 /opt/blender-4.5.4-linux-x64/blender -b --factory-startup --python-exit-code 1 --python scratch/rt_render_qa.py -- art-direction/3d/assets/races_regen/rigged/undead-ghoul-male.mixamo.glb --clips scratch/mixamo_ghoul.json --out scratch/mixamo-fbx/qa/ghoul
python3 scratch/mixamo_contact_sheets.py
python3 scratch/mixamo_order_regression.py
python3 scratch/verify_mixamo_batch.py
python3 -m unittest discover -s scratch -p test_mixamo_retarget.py -v
```

The two manifests enumerate every delivered clip and its exact source path. The combined verification JSON enumerates absolute PNG paths and hashes; per-body bake and verification JSON files are also committed beside it.
