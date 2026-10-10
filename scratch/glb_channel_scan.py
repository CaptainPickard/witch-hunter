"""Inspect GLB animation channels: which nodes/paths each clip targets."""
import struct, json, sys

p = sys.argv[1] if len(sys.argv) > 1 else "/workspace/witch-hunter/art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.glb"
data = open(p, 'rb').read()
jl, = struct.unpack_from('<I', data, 12)
j = json.loads(data[20:20+jl])

nodes = j.get('nodes', [])
anims = j.get('animations', [])
print("CLIPS:", len(anims), [a.get('name') for a in anims])
for a in anims[:2]:
    channels = a.get('channels', [])
    by_path = {}
    node_names = set()
    for ch in channels:
        t = ch.get('target', {})
        path = t.get('path')
        nidx = t.get('node')
        nname = nodes[nidx].get('name') if nidx is not None and nidx < len(nodes) else '?'
        by_path[path] = by_path.get(path, 0) + 1
        node_names.add(nname)
    print(f"--- {a.get('name')}: {len(channels)} channels, paths={by_path}")
    print("   nodes:", sorted(node_names))
# rest pose: check scene root node transforms (units)
mesh_nodes = [n.get('name') for n in nodes if 'skin' in n or 'mesh' in n]
print("mesh nodes:", mesh_nodes[:4])