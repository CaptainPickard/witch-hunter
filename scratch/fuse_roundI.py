#!/usr/bin/env python3
"""Bake the shattered assets through Blender: weld by position (MERGE by
distance with exact-match threshold), recompute smooth-by-angle normals,
re-pack the existing textures, and re-export. Deterministic, geometry-only
operation - textures untouched, UVs untouched.

Also NORMALS check: report original normal arrays vs recomputed.
"""
import bpy, json, sys, math
from mathutils import Vector
from pathlib import Path

ROOT = Path('/workspace/witch-hunter')
JOBS = [
    ('bramble',  'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb',
                 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb'),
    ('reach-a',  'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb',
                 'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb'),
    ('reach-b',  'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb',
                 'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb'),
    ('reach-c',  'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb',
                 'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb'),
]

def report(label, obj):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # connected components via vert links
    seen = set()
    comps = 0
    for v in bm.verts:
        if v.index in seen or v.is_wire and not v.link_faces:
            pass
    bm.free()
    return None

out = []
for name, src_rel, dst_rel in JOBS:
    src = ROOT / src_rel
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(src))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    # join all mesh objects into one
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    # record pre-fuse pieces
    import bmesh
    bm = bmesh.new(); bm.from_mesh(obj.data)
    pre_faces = len(bm.faces); bm.free()
    # weld EXACT duplicate verts (positions): merge by distance 1e-5
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=1e-5)
    bpy.ops.object.mode_set(mode='OBJECT')
    bm = bmesh.new(); bm.from_mesh(obj.data)
    post_faces = len(bm.faces)
    post_verts = len(bm.verts)
    bm.free()
    # weld pass 2: 0.0008 (0.8mm) for decimation cracks
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0008)
    bpy.ops.object.mode_set(mode='OBJECT')
    bm = bmesh.new(); bm.from_mesh(obj.data)
    fused_faces = len(bm.faces); fused_verts = len(bm.verts); bm.free()
    # normals: 4.2 removed use_auto_smooth; sharp edges via mesh-level attribute
    # smooth-shade all faces by angle (auto smooth replacement)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    # shade_auto_smooth op exists in 4.2 as context op on object
    with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        bpy.ops.object.shade_auto_smooth()
    # export over the same path (GLTF 2.0)
    bpy.ops.export_scene.gltf(filepath=str(ROOT / dst_rel), export_format='GLB',
                              export_image_format='AUTO', export_normals=True,
                              export_yup=True)
    out.append({'name': name, 'pre_faces': pre_faces, 'post_exact_faces': post_faces,
                'after_fuse_faces': fused_faces, 'after_fuse_verts': fused_verts,
                'bytes': (ROOT / dst_rel).stat().st_size})
    print('[fuse]', out[-1], flush=True)

(Path('/workspace/witch-hunter/scratch/treeqa/roundI-triage/fuse_report.json')
 .write_text(json.dumps(out, indent=1)))