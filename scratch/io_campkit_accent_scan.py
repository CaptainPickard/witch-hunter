#!/usr/local/bin/python3
"""IO: forbidden-accent scan on the pixelated campkit atlas (cyan/red law)."""
import json, struct
import numpy as np
import io as _io
from PIL import Image

path = '/tmp/wh-worldfeat/art-direction/3d/assets/camp/wh-campkit-pixelated.glb'
b = open(path, 'rb').read()
jl = struct.unpack_from('<I', b, 12)[0]
g = json.loads(b[20:20 + jl])
binoff = 20 + jl + 8
img = g['images'][0]
bv = g['bufferViews'][img['bufferView']]
o = binoff + bv.get('byteOffset', 0)
tex = Image.open(_io.BytesIO(bytes(b[o:o + bv['byteLength']]))).convert('RGB')
arr = np.asarray(tex).astype(int)
r, gg, bb = arr[..., 0], arr[..., 1], arr[..., 2]

cyan = (bb > 140) & (bb > r * 1.3) & (bb > gg)            # magic-cyan forbidden
red = (r > 150) & (r > gg * 1.8) & (r > bb * 1.8)         # pact-red forbidden
magenta = (r > 150) & (bb > 150) & (gg < 100)
print('atlas', tex.size, 'cyan:', int(cyan.sum()), 'red:', int(red.sum()),
      'magenta:', int(magenta.sum()))
if cyan.sum():
    ys, xs = np.nonzero(cyan)
    print('cyan bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
if red.sum():
    ys, xs = np.nonzero(red)
    print('red bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())