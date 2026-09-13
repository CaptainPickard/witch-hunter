#!/usr/bin/env python3
"""Deeper UV/texture diagnostic for race GLBs (raw + pixelated)."""
import trimesh, numpy as np

def diag(path, label):
    print("=" * 30, label)
    scene = trimesh.load(path)
    print("geometries:", list(scene.geometry.keys()))
    for name, g in scene.geometry.items():
        print("--- geom", name, "verts", len(g.vertices), "faces", len(g.faces),
              "visual", type(g.visual).__name__)
        vis = g.visual
        uv = getattr(vis, "uv", None)
        if uv is None:
            print("   uv: None")
        else:
            uv = np.asarray(uv)
            if uv.ndim != 2:
                print("   uv: not 2D, shape", uv.shape)
            else:
                print("   uv %s  u %.2f..%.2f v %.2f..%.2f  unique %d" % (
                    uv.shape, uv[:,0].min(), uv[:,0].max(), uv[:,1].min(), uv[:,1].max(),
                    len(np.unique(np.round(uv,5), axis=0))))
        mat = getattr(vis, "material", None)
        if mat is not None:
            for tname in ("baseColorTexture", "normalTexture"):
                t = getattr(mat, tname, None)
                if t is not None:
                    a = np.asarray(t.convert("RGB"))
                    print("   %s size=%s meanRGB=%s" % (tname, t.size, a.reshape(-1,3).mean(axis=0).round(1)))
    return scene

if __name__ == "__main__":
    diag("art-direction/3d/assets/races/human-hunter-male.glb", "RAW")
    diag("art-direction/3d/assets/races/human-hunter-male-pixelated.glb", "PIXELATED")