#!/usr/bin/env python3
"""Decode the encoding-constant situation in the bundled three.js r147."""
import re
spike = open("/workspace/witch-hunter/art-direction/3d-spike/gravedigger-equip-demo-v2.html").read()
# constants block: 'at=3e3,ot=3001' etc (from earlier grep: at=3e3, ot=3001)
m = re.search(r"\bat=3e3\b", spike)
print("at=3e3 (LinearEncoding) found:", bool(m))
m2 = re.search(r"\bot=3001\b", spike)
print("ot=3001 (sRGBEncoding) found:", bool(m2))
# renderer default
m3 = re.search(r"this\.outputEncoding=(\w+)", spike)
print("renderer default outputEncoding var:", m3.group(1))
# is there any assignment of renderer.outputEncoding = sRGBEncoding in app code?
i = spike.find("THREE.WebGLRenderer({canvas")
app = spike[i:]
print("app sets outputEncoding:", bool(re.search(r"outputEncoding\s*=", app[:5000])))