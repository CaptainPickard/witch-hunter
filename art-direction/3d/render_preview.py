import sys, numpy as np, trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image


def load_flat(glb):
    obj = trimesh.load(glb)
    if isinstance(obj, trimesh.Scene):
        s = obj
        meshes = []
        for name, g in s.geometry.items():
            m = g.copy()
            try:
                T = s.graph.get(name)[0]
                m.apply_transform(T)
            except (ValueError, KeyError):
                pass
            meshes.append(m)
        return trimesh.util.concatenate(meshes), s
    return obj, trimesh.Scene({'m': obj})


def vertex_colors(M, s):
    """Sample the baked texture at vertex UVs -> vertex colors."""
    for name, g in s.geometry.items():
        tex = getattr(g.visual.material, 'baseColorTexture', None)
        if tex is None or not hasattr(M.visual, 'uv') or M.visual.uv is None:
            return None
        uv = np.array(M.visual.uv)
        arr = np.array(tex.convert('RGB'))
        h, w = arr.shape[:2]
        px = np.clip((uv[:, 0] * w).astype(int), 0, w - 1)
        py = np.clip((uv[:, 1] * h).astype(int), 0, h - 1)
        return arr[py, px]
    return None


def render(glb, out, yaw_deg=0.0, elev=5.0):
    M, s = load_flat(glb)
    vc = getattr(M.visual, 'vertex_colors', None)
    if vc is not None and len(vc) == len(M.vertices):
        M.visual.face_colors = np.array(vc)[M.faces].mean(axis=1).astype(np.uint8)
    if len(M.faces) > 8000:
        vn, fn = __import__('fast_simplification').simplify(M.vertices, M.faces, target_count=8000)
        M = trimesh.Trimesh(vn, fn, process=False)
        M.visual.face_colors = np.clip(vc[M.faces].mean(axis=1), 0, 255).astype(np.uint8) if vc is not None else [128,128,128,255]
    M.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0]))
    M.apply_transform(trimesh.transformations.rotation_matrix(np.radians(yaw_deg), [0, 1, 0]))
    fig = plt.figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    pc = Poly3DCollection(M.triangles, facecolors=M.visual.face_colors / 255.0, edgecolors='none')
    ax.add_collection3d(pc)
    b = M.bounds
    c = b.mean(axis=0)
    r = (b[1] - b[0]).max() * 0.6
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_axis_off()
    ax.view_init(elev=elev, azim=0)
    plt.tight_layout(pad=0)
    fig.savefig(out, transparent=False, facecolor='#808080')
    plt.close(fig)
    print('rendered', out)


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.0)