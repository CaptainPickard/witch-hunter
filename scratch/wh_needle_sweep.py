#!/usr/bin/env python3
"""Pre-dispatch needle sweep over io/specs/mouse-bind-cam-spec.md (gate skill law)."""
import re, sys

SPEC = "/workspace/witch-hunter/io/specs/mouse-bind-cam-spec.md"
pjs = "/workspace/witch-hunter/prototype/js/player.js"
text = open(SPEC).read()
fails = []

# 1. AC id coverage: N1..N10 and P1..P8 each defined and cross-referenced
for i in range(1, 11):
    for pat in (r"\bN%d\b" % i,):
        if not re.search(pat, text):
            fails.append("missing AC id %s" % i)
for i in range(1, 9):
    if not re.search(r"\bP%d\b" % i, text):
        fails.append("missing floor id P%d" % i)

# 2. Config/identifier consistency
for needle in ["CFG.mouse", "pointerLockSensMult", "autoBindOnCanvasClick",
               "wh-mouse-chip", "Backquote", "tools/build_v8.py",
               "io/specs/mouse-bind-cam-valspec.md",
               "tests/wh_mousebind_validation.py",
               "v8-playable.html", "Witch Hunter v8 - Mouse Bind Cam",
               "requestPointerLock", "pointerlockchange", "exitPointerLock",
               "movementX", "applyCamDelta", "syncMouseChip", "toggleMouseBind",
               "bindMouse", "unbindMouse", "mouseBound", "lastManualCamT"]:
    c = text.count(needle)
    if c == 0:
        fails.append("needle absent: %s" % needle)

# 3. No em dashes (Nicko law, enforced on specs too)
if "\u2014" in text or "\u2013" in text:
    fails.append("em/en dash found in spec")

# 4. Unbalanced code fences
if text.count("```") % 2 != 0:
    fails.append("unbalanced triple-backtick fences")

# 5. Anchor sanity: verify cited line numbers against live tree
lines = open(pjs).read().split("\n")
checks = [
    (100, "camYaw"), (269, "mousedown"), (297, "mousemove"),
    (304, "camYaw -="),
]
for ln, needle in checks:
    if needle not in lines[ln - 1]:
        fails.append("anchor drift player.js:%d lacks %r" % (ln, needle))

cfg = open("/workspace/witch-hunter/prototype/js/CONFIG.js").read().split("\n")
for ln, needle in [(582, "mouseSensDegPerPx"), (589, "},")]:
    if needle not in cfg[ln - 1]:
        fails.append("anchor drift CONFIG.js:%d lacks %r" % (ln, needle))

html = open("/workspace/witch-hunter/prototype/index.html").read().split("\n")
if "wh-lock-reticle" not in html[27]:
    fails.append("anchor drift index.html:28 lacks wh-lock-reticle")

print("SPEC SIZE:", len(text), "chars,", text.count("\n") + 1, "lines")
print("FAILS:", len(fails))
for f in fails:
    print("  -", f)
print("SWEEP", "PASS" if not fails else "FAIL")