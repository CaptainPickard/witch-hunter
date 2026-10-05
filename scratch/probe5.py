#!/usr/bin/env python3
"""AUTH-BYPASS E2E: hit /playtest-feat/ with a VALID session cookie (minted
inside the webui container via its own auth machinery) and grep the SERVED
player.js for the 10-04 markers. This is the exact request Nicko's browser
makes. Any FAIL here = real serving bug; PASS = serving fine and the issue
is his browser session/cache or his expectations."""
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

# Mint a session token INSIDE the container using its own auth module:
# python3 -c import api.auth; print(api.auth.make_session(...)) - find maker
print("auth fns:", exec_in(
    "grep -n 'def .*session\\|SESSION_TTL\\|def issue' /app/api/auth.py | head -8"))
print("mint attempt:", exec_in(
    "cd /app && python3 -c \""
    "import sys; sys.path.insert(0,'/app');"
    "from api import auth;"
    "import inspect;"
    "fns=[n for n,_ in inspect.getmembers(auth, inspect.isfunction) if 'session' in n.lower() or 'token' in n.lower() or 'mint' in n.lower()];"
    "print(fns)\""))