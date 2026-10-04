#!/usr/bin/env python3
"""Round F: warm amber emissive glass for wh-lantern-hang-pixelated.glb.

Pixelation-pass add-on (after tree_bake.py): the emissive map is the baked
512 5-bit base map masked to its warm amber pixels (the glass panels), all
other texels black, so only the glass glows. emissiveFactor [1, 1, 1].
GLTFLoader maps it to MeshStandardMaterial.emissiveMap; prepTemplate leaves
emissive untouched. Re-exports in place (raw/<id>.glb and <id>.glb untouched).

  lantern_emissive.py [glb]
"""
import sys
import numpy as np
import trimesh
from PIL import Image
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import export

p = sys.argv[1] if len(sys.argv) > 1 else 'art-direction/3d/assets/biome_library/wh-lantern-hang-pixelated.glb'
m = trimesh.load(p, force='mesh')
base = m.visual.material.baseColorTexture.convert('RGB')
a = np.asarray(base).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
amber = (r >= 150) & (r - b >= 70) & (g >= b) & (r >= g)
em = np.where(amber[..., None], a, 0).astype(np.uint8)
em = (em >> 3) << 3
mat = m.visual.material
mat.emissiveTexture = Image.fromarray(em, 'RGB')
mat.emissiveFactor = [1.0, 1.0, 1.0]
m.vertex_normals
export(p, m, m.visual.material.baseColorTexture)
print(p, 'amber texels', int(amber.sum()), 'of', amber.size, '(%.1f%%)' % (100.0 * amber.mean()))
