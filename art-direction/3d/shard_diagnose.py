#!/usr/bin/env python3
"""Count disconnected face components in each race glb (raw + pixelated)."""
import json, sys
import numpy as np, trimesh
from collections import Counter

sys.path.insert(0, "/workspace/witch-hunter/art-direction/3d")

def face_components(mesh):
    # union-find over face adjacency via shared edges
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(len(mesh.faces)))
    adj = mesh.face_adjacency
    g.add_edges_from(map(tuple, adj))
    comps = list(nx.connected_components(g))
    out = []
    for c in comps:
        faces = np.array(sorted(c))
        sub = mesh.submesh([faces], append=True, repair=False)
        com = sub.bounds.mean(axis=0)
        centroid = sub.vertices.mean(axis=0)
        dist = float(np.linalg.norm(centroid))
        out.append({"faces": len(c), "centroid": [round(float(x), 3) for x in centroid],
                    "dist_from_origin": round(dist, 3),
                    "ext": [round(float(x), 4) for x in (sub.bounds[1]-sub.bounds[0])]})
    out.sort(key=lambda d: -d["faces"])
    return out

def main():
    import glob, os
    d = "/workspace/witch-hunter/art-direction/3d/assets/races"
    report = {}
    for path in sorted(glob.glob(os.path.join(d, "*-pixelated.glb"))):
        name = os.path.basename(path)
        m = trimesh.load(path, force="mesh")
        comps = face_components(m)
        tiny = [c for c in comps if c["faces"] < 10]
        tiny_far = [c for c in tiny if c["dist_from_origin"] > 1.0]
        report[name] = {"total_components": len(comps), "total_faces": len(m.faces),
                        "tiny_lt10": len(tiny), "tiny_far_gt1": len(tiny_far),
                        "components": comps if len(comps) <= 15 else comps[:15]}
        print(f"{name}: comps={len(comps)} tiny(<10f)={len(tiny)} tiny&far(>1.0)={len(tiny_far)} total_faces={len(m.faces)}")
        for c in comps[:8]:
            print(f"   faces={c['faces']:6d} centroid={c['centroid']} dist={c['dist_from_origin']}")
    with open("/workspace/witch-hunter/art-direction/3d/shard_report.json", "w") as f:
        json.dump(report, f, indent=1)
    print("wrote shard_report.json")

if __name__ == "__main__":
    main()