#!/usr/bin/env python3
"""Second-opinion probe: what does Nicko's browser ACTUALLY get from
/playtest-feat/? wget inside the webui netns WITHOUT -q so redirects show;
also check which sha the served player.js corresponds to."""
import json, subprocess

SOCK = ["curl", "-s", "--unix-socket", "/var/run/docker.sock"]

def api(method, path, data=None):
    cmd = SOCK + ["-X", method, f"http://localhost{path}"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    return json.loads(out) if out.strip() else {}

cid = [c["Id"] for c in api("GET", "/containers/json") if "webui" in c["Names"][0]][0]

def exec_in(cmd, timeout=60):
    e = api("POST", f"/containers/{cid}/exec", {
        "AttachStdout": True, "AttachStderr": True, "Cmd": ["/bin/sh", "-c", cmd]})
    raw = subprocess.run(SOCK + ["-X", "POST", "-H", "Content-Type: application/json",
        "-d", json.dumps({"Detach": False, "Tty": False}),
        f"http://localhost/exec/{e['Id']}/start"], capture_output=True, timeout=timeout)
    txt = []
    for line in raw.stdout.decode("utf-8", "replace").split("\n"):
        if len(line) > 8 and line[0] in "\x01\x02":
            line = line[8:]
        txt.append(line)
    return "".join(txt)

# direct file read (no http) - what the ROUTE will read
print("route-source player.js leftHand count:",
      exec_in("grep -c leftHand /tmp/wh-worldfeat/prototype/js/player.js"))
print("route-source sha stamp:",
      exec_in("cat /tmp/wh-worldfeat/prototype/js/player.js | md5sum | head -c 8"))
# http from inside with cookie-less (should be login redirect)
print("http (no auth):", exec_in(
    "wget -S -O /dev/null http://localhost:8787/playtest-feat/prototype/js/player.js 2>&1 | head -4"))
# what sha does /playtest-feat/ index.html reference? (build hash marker?)
print("index head:", exec_in(
    "head -c 120 /tmp/wh-worldfeat/prototype/index.html"))