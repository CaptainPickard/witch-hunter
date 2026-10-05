#!/usr/bin/env python3
"""Probe the LIVE webui container: does its routes.py have /playtest-feat/,
and what does its 8787 answer (route vs stale image)?"""
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
                                 f"http://localhost/exec/{e['Id']}/start"],
                         capture_output=True, timeout=timeout)
    txt = []
    for line in raw.stdout.decode("utf-8", "replace").split("\n"):
        if len(line) > 8 and line[0] in "\x01\x02":
            line = line[8:]
        txt.append(line)
    return "".join(txt)

# 1) find the container's own routes.py (NOT the bind) and grep it
print("routes.py locations:",
      exec_in("ls /opt/hermes/api/routes.py /app/api/routes.py 2>/dev/null; "
              "readlink -f /workspace/hermes-webui/api/routes.py 2>/dev/null; "
              "head -1 /proc/1/cmdline | tr '\\0' ' '"))
print("feat-handler count in live file:",
      exec_in("for f in /opt/hermes/api/routes.py /app/api/routes.py; do "
              "[ -f $f ] && grep -c playtest-feat $f; done 2>/dev/null | head -2"))
# 2) is /workspace bind-mounted INTO the container (AGENTS.md earlier said yes)?
print("bind check:", exec_in("ls /workspace/witch-hunter/prototype/js/CONFIG.js 2>/dev/null && echo BIND-OK || echo NO-BIND"))
# 3) 8787 inside the container's netns: answer code for /playtest-feat/
print("http 8787:", exec_in(
    "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:8787/playtest-feat/ ; echo; "
    "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:8787/health"))