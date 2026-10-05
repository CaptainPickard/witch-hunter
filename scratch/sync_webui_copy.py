#!/usr/bin/env python3
"""Sync the webui container's private /tmp/wh-worldfeat to feat/world-visuals.

The webui container has NO /tmp bind (verified): its /tmp/wh-worldfeat is a
filesystem-private copy, so /playtest-feat/ keeps serving whatever it held
last. Refresh = git archive extract of the branch over the copy (idempotent,
exact, preserves the container's .git layout choice)."""
import json, subprocess, time

SOCK = ["curl", "-s", "--unix-socket", "/var/run/docker.sock"]

def api(method, path, data=None):
    cmd = SOCK + ["-X", method, f"http://localhost{path}"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    return json.loads(out) if out.strip() else {}

cid = None
for c in api("GET", "/containers/json"):
    if "webui" in c["Names"][0]:
        cid = c["Id"]
print("webui cid:", cid[:12])

def exec_in(cmd, timeout=120):
    e = api("POST", f"/containers/{cid}/exec", {
        "AttachStdout": True, "AttachStderr": True,
        "Cmd": ["/bin/sh", "-c", cmd]})
    eid = e["Id"]
    # Detach:false STREAMS raw multiplexed output as the response body
    raw = subprocess.run(SOCK + ["-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"Detach": False, "Tty": False}),
        f"http://localhost/exec/{eid}/start"],
        capture_output=True, timeout=timeout)
    out = raw.stdout.decode("utf-8", "replace")
    txt = []
    for line in out.split("\n"):
        if len(line) > 8 and line[0] in "\x01\x02":
            line = line[8:]
        txt.append(line)
    return "".join(txt)

# 1) current state inside webui
print("before:", exec_in("git -C /tmp/wh-worldfeat rev-parse HEAD 2>/dev/null; ls /tmp/wh-worldfeat/prototype/js | head -2"))
# 2) archive-extract the feat branch (from the mounted repo checkout) over the copy
cmd = ("cd /workspace/witch-hunter && "
       "git fetch origin feat/world-visuals >/dev/null 2>&1; "
       "git archive origin/feat/world-visuals | tar -x -C /tmp/wh-worldfeat && "
       "echo EXTRACTED")
print(exec_in(cmd))
# 3) verify key markers inside the webui now
print("after:", exec_in(
    "grep -c leftHand /tmp/wh-worldfeat/prototype/js/player.js; "
    "grep -c Radiance /tmp/wh-worldfeat/prototype/js/spells.js; "
    "grep -c radiance /tmp/wh-worldfeat/prototype/js/CONFIG.js; "
    "grep -c 'FULL camera decoupling' /tmp/wh-worldfeat/prototype/js/player.js"))
# 4) HTTP check from inside its OWN netns (what Nicko's browser hits)
print("http:", exec_in(
    "wget -q -O - http://localhost:8787/playtest-feat/prototype/js/player.js 2>/dev/null | grep -c leftHand; "
    "wget -q -O - 'http://localhost:8787/playtest-feat/' 2>/dev/null | head -c 60"))
# 5) also confirm 8793 host container already serves current (control)
# (checked separately by IO)