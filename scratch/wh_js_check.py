#!/usr/bin/env python3
"""Syntax-check witch-hunter JS via playwright's bundled node."""
import glob, subprocess, sys

node = None
for pat in ("/usr/local/lib/python3.12/site-packages/playwright/driver/node",
            "/root/.cache/ms-playwright/*/node"):
    hits = glob.glob(pat)
    if hits:
        node = hits[0]
        break
if not node:
    print("NO NODE FOUND")
    sys.exit(1)
for f in ("/workspace/witch-hunter/prototype/js/player.js",
          "/workspace/witch-hunter/prototype/js/CONFIG.js"):
    r = subprocess.run([node, "--check", f], capture_output=True, text=True)
    print(f.split("/")[-1], "OK" if r.returncode == 0 else
          "FAIL\n" + (r.stderr or r.stdout)[-800:])