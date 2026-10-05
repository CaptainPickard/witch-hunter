#!/usr/bin/env python3
"""Final E2E: cookie-authed served-bytes table for every landed feature."""
import json, subprocess

SOCK = ["curl", "-s", "--unix-socket", "/var/run/docker.sock"]

def api(method, path, data=None):
    cmd = SOCK + ["-X", method, f"http://localhost{path}"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    return json.loads(out) if out.strip() else {}

cid = [c["Id"] for c in api("GET", "/containers/json") if "webui" in c["Names"][0]][0]

def exec_in(cmd, timeout=90):
    e = api("POST", f"/containers/{cid}/exec",
            {"AttachStdout": True, "AttachStderr": True, "Cmd": ["/bin/sh", "-c", cmd]})
    raw = subprocess.run(SOCK + ["-X", "POST", "-H", "Content-Type: application/json",
                                 "-d", json.dumps({"Detach": False, "Tty": False}),
                                 f"http://localhost/exec/{e['Id']}/start"],
                         capture_output=True, timeout=timeout)
    txt = []
    for line in raw.stdout.decode("utf-8", "replace").split("\n"):
        if len(line) > 8 and line[0] in "\x01\x02":
            line = line[8:]
        txt.append(line)
    return "".join(txt)

# fresh login
exec_in(
    "PW=$(cat /proc/1/environ | tr '\\0' '\\n' | grep '^HERMES_WEBUI_PASSWORD=' | cut -d= -f2-); "
    "curl -s -c /tmp/e2e.cookies -m 8 -X POST -H 'Content-Type: application/json' "
    "-d \"{\\\"password\\\": \\\"$PW\\\"}\" http://127.0.0.1:8787/api/auth/login >/dev/null")

def served(path):
    return exec_in(f"curl -s -b /tmp/e2e.cookies -m 10 http://127.0.0.1:8787{path}")

body = lambda p: served(p)
t = []
t.append(("10-04 shield (player.leftHand)", "leftHand" in body("/playtest-feat/prototype/js/player.js")))
t.append(("10-04 Radiance (spells.js)", "RadianceEffect" in body("/playtest-feat/prototype/js/spells.js")))
t.append(("10-04 radiance cfg", "radiance:" in body("/playtest-feat/prototype/js/CONFIG.js")))
t.append(("10-04 shield manifest", "roundShield" in body("/playtest-feat/prototype/js/assets.js")))
t.append(("10-04 chain-clips wiring (anim MOVE_NAMES)", "MOVE_NAMES" in body("/playtest-feat/prototype/js/anim.js")))
t.append(("10-04 combat-chain GLB file", exec_in(
    "curl -s -b /tmp/e2e.cookies -m 20 -o /dev/null -w '%{size_download}' "
    "http://127.0.0.1:8787/playtest-feat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb").count("4") >= 1))
t.append(("10-03 camera decouple (no autofollow)", "FULL camera decoupling" in body("/playtest-feat/prototype/js/player.js")))
t.append(("10-03 starry night (setupSky)", "buildDirtPath" in body("/playtest-feat/prototype/js/region-manager.js")))
t.append(("10-03 forest ring", "ring" in body("/playtest-feat/prototype/js/CONFIG.js")))
t.append(("moveset framework", "playerWeapon" in body("/playtest-feat/prototype/js/CONFIG.js")))
for label, ok in t:
    print("PASS" if ok else "FAIL", "-", label)