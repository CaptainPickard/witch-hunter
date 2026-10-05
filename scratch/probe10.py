#!/usr/bin/env python3
"""E2E attempt 4: LOGIN via the real /api/auth/login endpoint with the actual
operator password (from container env), then use the ISSUED session cookie
for /playtest-feat/. This is Nicko's exact request path."""
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

# login using env password, store cookie to file
login_sh = (
    "PW=$(cat /proc/1/environ | tr '\\0' '\\n' | grep '^HERMES_WEBUI_PASSWORD=' | cut -d= -f2-); "
    "curl -s -c /tmp/e2e.cookies -m 8 -X POST -H 'Content-Type: application/json' "
    "-d \"{\\\"password\\\": \\\"$PW\\\"}\" http://127.0.0.1:8787/api/auth/login | head -c 120; echo; "
    "grep -c hermes_session /tmp/e2e.cookies")
print("login:", exec_in(login_sh))

# served checks with the cookie jar
def served(path, extra=""):
    return exec_in(
        f"curl -s -b /tmp/e2e.cookies -m 8 {extra} http://127.0.0.1:8787{path}")

body = served("/playtest-feat/prototype/js/player.js")
print("served player leftHand:", body.count("leftHand"))
print("served player stow:", body.count("stowToShield"))
sp = served("/playtest-feat/prototype/js/spells.js")
print("served spells Radiance:", sp.count("Radiance"))
root = served("/playtest-feat/")
print("root page bytes:", len(root), "has tuner marker:", "wh-res-tuner" in root)
code = served("/playtest-feat/", "-o /dev/null -w ':%{http_code}'")
print("root status:", code.strip().split(':')[-1])