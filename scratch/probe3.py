#!/usr/bin/env python3
"""END-TO-END: hit /playtest-feat through 8787 exactly like Nicko's browser,
with a session bypass via the login-redirect chain... no - instead test the
two parts separately:
 1) route FILE source updated? (done: fde94cd2, 8 leftHand)
 2) does the route serve that file? Need an authed session. Use the
    HERMES cookie from container env if present, else accept 302 as proof
    of routing but verify handler reads NEW bytes by checking the route
    code path: playtest index served = /tmp/wh-worldfeat/prototype/index.html.
Plan: check whether 8787 requires auth for /playtest-feat at all (login wall
applies to everything). Then verify the file mtime + content the handler
reads directly."""
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
    e = api("POST", f"/containers/{cid}/exec",
        {"AttachStdout": True, "AttachStderr": True, "Cmd": ["/bin/sh", "-c", cmd]})
    raw = subprocess.run(SOCK + ["-X", "POST", "-H", "Content-Type: application/json",
        "-d", json.dumps({"Detach": False, "Tty": False}),
        f"http://localhost/exec/{e['Id']}/start"], capture_output=True, timeout=timeout)
    txt = []
    for line in raw.stdout.decode("utf-8", "replace").split("\n"):
        if len(line) > 8 and line[0] in "\x01\x02":
            line = line[8:]
        txt.append(line)
    return "".join(txt)

# does auth wall the /playtest-feat route? check config for public paths
print("auth config:", exec_in(
    "grep -rn 'playtest' /workspace/hermes-webui/auth* /workspace/hermes-webui/*.yaml 2>/dev/null | head -5"))
# what process/port inside the container serves requests? (is 8787 the same proc?)
print("proc:", exec_in("ps | grep -c python; netstat -tlnp 2>/dev/null | head -6"))
# mtime of the file the route reads
print("mtime:", exec_in("stat -c '%y %s' /tmp/wh-worldfeat/prototype/js/player.js"))
print("sha:", exec_in("md5sum /tmp/wh-worldfeat/prototype/js/player.js | head -c 8"))