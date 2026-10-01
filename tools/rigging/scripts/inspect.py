import bpy, sys
from mathutils import Vector
for o in bpy.data.objects:
    print("OBJ", o.name, o.type, o.parent.name if o.parent else None, tuple(round(x,3) for x in o.location), tuple(round(x,3) for x in o.rotation_euler), tuple(round(x,3) for x in o.scale))
    if o.type=='MESH':
        me=o.data
        print(" verts",len(me.vertices),"polys",len(me.polygons),"tris",sum(len(p.vertices)-2 for p in me.polygons))
        ws=[o.matrix_world@v.co for v in me.vertices]
        mn=Vector((min(v[i] for v in ws) for i in range(3))); mx=Vector((max(v[i] for v in ws) for i in range(3)))
        print(" bounds",tuple(round(x,3) for x in mn),tuple(round(x,3) for x in mx))
        print(" mats",[m.name for m in me.materials], "uvs",[u.name for u in me.uv_layers], "vgroups", len(o.vertex_groups))
for i in bpy.data.images: print("IMG",i.name,i.size[:],i.packed_file is not None)
for m in bpy.data.materials:
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE': print("TEXNODE",m.name,n.image.name if n.image else None,n.interpolation)
print("ACTIONS",[a.name for a in bpy.data.actions])
