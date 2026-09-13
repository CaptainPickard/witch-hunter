#!/usr/bin/env python3
"""Build bisect page: 4 configs (raw/pix x nearest/linear) of human-hunter-male side by side."""
import base64, sys
from pathlib import Path
ROOT = "/workspace/witch-hunter"
three, gltf = None, None
spike = open(ROOT + "/art-direction/3d-spike/gravedigger-equip-demo-v2.html").read()
blocks = []
i = 0
while True:
    i = spike.find("<script>", i)
    if i < 0: break
    j = spike.find("</script>", i)
    blocks.append(spike[i+len("<script>"):j])
    i = j
three = next(b for b in blocks if "Three.js Authors" in b)
gltf = next(b for b in blocks if "THREE.GLTFLoader = GLTFLoader" in b)
tpl = open(ROOT + "/art-direction/3d/bisect.template.html").read()
html = tpl.replace("/*THREE_JS_PLACEHOLDER*/", three).replace("/*GLTF_LOADER_PLACEHOLDER*/", gltf)
glbs = {}
for key, path in [
    ("raw_nearest", ROOT + "/art-direction/3d/assets/races/human-hunter-male.glb"),
    ("raw_linear",  ROOT + "/art-direction/3d/assets/races/human-hunter-male.glb"),
    ("pix_nearest", ROOT + "/art-direction/3d/assets/races/human-hunter-male-pixelated.glb"),
    ("pix_linear",  ROOT + "/art-direction/3d/assets/races/human-hunter-male-pixelated.glb"),
]:
    glbs[key] = base64.b64encode(open(path, "rb").read()).decode()
inject = "window.__GLBS__ = " + repr(glbs).replace("'", '"') + ";"
html = html.replace("<script>\nvar results", "<script>\n" + inject + "\nvar results")
out = ROOT + "/art-direction/3d/bisect.html"
open(out, "w").write(html)
print("built", out, len(html)//1024, "KB")