"""2D orthographic silhouette projection of a mesh for QA (front + side).

Usage: ortho_preview.py mesh.ply|glb out-front.png out-side.png
"""
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


def to_flat(path):
    obj = trimesh.load(path, force='scene')
    if isinstance(obj, trimesh.Scene):
        meshes = []
        for name, g in obj.geometry.items():
            m = g.copy()
            try:
                T = obj.graph.get(name)[0]
                m.apply_transform(T)
            except (ValueError, KeyError):
                pass
            meshes.append(m)
        return trimesh.util.concatenate(meshes)
    return obj


def vert_colors(M, scene=None):
    """Texture sampled at UVs, else vertex colors, else flat gray."""
    vc = getattr(M.visual, 'vertex_colors', None)
    if vc is not None and len(vc) == len(M.vertices):
        return np.array(vc)[M.faces].mean(axis=1).astype(float)
    tex = getattr(getattr(M.visual, 'material', None), 'baseColorTexture', None)
    uv = getattr(M.visual, 'uv', None)
    if tex is not None and uv is not None and len(uv) == len(M.vertices):
        arr = np.array(tex.convert('RGB'))
        h, w = arr.shape[:2]
        px = np.clip((np.asarray(uv)[:, 0] * w).astype(int), 0, w - 1)
        py = np.clip(((1 - np.asarray(uv)[:, 1]) * h).astype(int), 0, h - 1)
        vcol = arr[py, px]
        return vcol[M.faces].mean(axis=1).astype(float)
    return np.full((len(M.faces), 4), [110, 110, 110, 255], dtype=float)


from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def ortho2d(mesh, out, axis, tex=None):
    """True 3D render (matplotlib) with flat-ish view; axis 'z' = front, 'x' = side."""
    fig = plt.figure(figsize=(6, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    fc = vert_colors(mesh)[:, :3] / 255.0
    M = mesh.copy()
    if axis == 'x':   # rotate 90 about Y so side faces camera
        M.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0]))
    pc = Poly3DCollection(M.triangles, facecolors=fc, edgecolors='none')
    ax.add_collection3d(pc)
    b = M.bounds
    c = b.mean(axis=0)
    r = (b[1] - b[0]).max() * 0.55
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=0, azim=-90)
    plt.tight_layout(pad=0)
    fig.savefig(out, facecolor='#c8c8c8')
    plt.close(fig)


def main(src, out_front, out_side):
    m = to_flat(src)
    if len(m.faces) > 8000:
        import fast_simplification as fs
        vn, fn = fs.simplify(m.vertices, m.faces, target_count=8000)
        old_v = m.vertices
        from scipy.spatial import cKDTree
        _, idx = cKDTree(vn).query(old_v, k=1)
        vcol = None
        if getattr(m.visual, 'kind', None) == 'texture' and m.visual.uv is not None and getattr(m.visual.material, 'baseColorTexture', None) is not None:
            tex = m.visual.material.baseColorTexture.convert('RGB')
            uv = np.clip(np.array(m.visual.uv), 0, 1)
            arr = np.array(tex)
            h, w = arr.shape[:2]
            px = np.clip((uv[:, 0] * w).astype(int), 0, w - 1)
            py = np.clip(((1 - uv[:, 1]) * h).astype(int), 0, h - 1)
            vcol = arr[py, px]
        vc = getattr(m.visual, 'vertex_colors', None)
        if vc is not None and len(vc) == len(old_v):
            vcol = np.array(vc)
        m = trimesh.Trimesh(vn, fn, process=False)
        if vcol is not None:
            m.visual = trimesh.visual.ColorVisuals(mesh=m, vertex_colors=vcol[idx])
    # game meshes are Y-up; matplotlib is Z-up: rotate -90 about X
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0]))
    ortho2d(m, out_front, 'z')
    ortho2d(m, out_side, 'x')
    print('ortho previews saved:', out_front, out_side)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])