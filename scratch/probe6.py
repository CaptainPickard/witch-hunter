#!/usr/bin/env python3
"""E2E with a minted session: create_session inside the container, hit
/playtest-feat/ + assets with the cookie, grep 10-04 markers in SERVED bytes."""
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

mint = exec_in(
    "cd /app && python3 -c \""
    "import sys;sys.path.insert(0,'/app');"
    "from api import auth;"
    "import inspect;"
    "print(inspect.signature(auth.create_session))\"")
print("create_session sig:", mint)

minted = exec_in(
    "cd /app && python3 -c \""
    "import sys;sys.path.insert(0,'/app');"
    "from api import auth;"
    "import inspect,json;"
    "sig=inspect.signature(auth.create_session);"
    "kw={};"
    "for n,p in sig.parameters.items():"
    "  if p.default is inspect._empty and n!='self': kw[n]=({};"
    "print(json.dumps(list(sig.parameters)))\"")
print("params:", minted)