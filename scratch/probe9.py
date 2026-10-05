#!/usr/bin/env python3
"""E2E attempt 3: create the session in the SAME process context as the server
(sessions live in STATE_DIR/.sessions.json; the exec python may write a
DIFFERENT STATE_DIR than the serve process). Compare: read the serve proc's
env STATE_DIR from its /proc, then write the session file there directly,
or use the server's own login endpoint with the operator password? Simplest
true-path: check whether HERMES_WEBUI_AUTH is even enabled; if auth is
DISABLED (is_auth_enabled False), the 302 means something else entirely."""
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

print("auth enabled?:", exec_in(
    "cd /app && python3 - <<'PYEOF'\n"
    "import sys; sys.path.insert(0,'/app')\n"
    "from api import auth\n"
    "print('IS_AUTH_ENABLED', auth.is_auth_enabled())\n"
    "print('STATE_DIR', auth.STATE_DIR)\n"
    "print('sessions file exists:', auth._SESSIONS_FILE.exists())\n"
    "PYEOF").strip())
print("server proc env:", exec_in(
    "cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n' | grep -i 'HERMES' | head -8"))
print("auth state file:", exec_in(
    "ls -la /home/hermeswebui/.hermes/.sessions.json /data/.sessions.json 2>/dev/null | head -3; "
    "find / -maxdepth 4 -name '.sessions.json' 2>/dev/null | head -3"))