# R4 bake: all 3 in-manifest bodies (player/bandit/ghoul).
from PIL import Image
import os

RD = "/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged"
OUT = "/tmp/wh_r4_atlas"
BODIES = ["human-hunter-male.rigged.glb",      # playerBody
          "orc-male-warrior.rigged.glb",       # banditBody
          "undead-ghoul-male.rigged.glb"]      # ghoulBody

for g in BODIES:
    p = os.path.join(RD, g)
    base = g.replace(".glb", "")
    if not os.path.exists(p):
        print("MISSING:", g)
        continue
    with open(p, "rb") as f:
        blob = f.read()
    # extract jpeg (ffd8..ffd9) from GLB bin chunk
    s = blob.find(b"\xff\xd8\xff")
    e = blob.rfind(b"\xff\xd9")
    img = Image.open(__import__("io").BytesIO(blob[s:e + 2])).convert("RGB")
    out = os.path.join(OUT, base + "-pixelated.png")
    small = img.resize((512, 512), Image.NEAREST).point(
        lambda v: (v >> 3) << 3)
    small.save(out, "PNG")
    print(base, img.size, "->", os.path.getsize(out), "bytes")