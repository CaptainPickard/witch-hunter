"""Build bone-name mapping + retarget ONE probe clip to the WH 20-bone rig. Proves the loop."""
import bpy, os, json, sys

AXE = "/workspace/witch-hunter/scratch/mixamo-fbx/axepack/crouch idle.fbx"
TARGET = "/workspace/witch-hunter/art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.glb"
OUTGLB = "/workspace/witch-hunter/scratch/mixamo-fbx/probe_axe_retarget.glb"

# import target first
bpy.ops.import_scene.gltf(filepath=TARGET)
arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
print("TARGET ARMATURES:", [a.name for a in arms], [len(a.data.bones) for a in arms])
target = max(arms, key=lambda a: len(a.data.bones))
print("TARGET BONES:", sorted([b.name for b in target.data.bones]))

# import mixamo fbx
before_objs = {o.name for o in bpy.data.objects}
before_acts = set(bpy.data.actions.keys())
bpy.ops.import_scene.fbx(filepath=AXE)
src = None
for o in bpy.data.objects:
    if o.name not in before_objs and o.type == 'ARMATURE':
        src = o
        break
print("SRC ARM:", src.name if src else None, len(src.data.bones) if src else 0, "bones")
print("SRC BONE NAMES:", sorted([b.name for b in src.data.bones]))
print("SRC ACTIONS:", [a for a in bpy.data.actions.keys() if a not in before_acts])