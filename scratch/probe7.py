#!/usr/bin/env python3
"""E2E: mint session, hit /playtest-feat assets, grep markers in SERVED bytes."""
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

MINT = ("cd /app && python3 - <<'PYEOF'\n"
        "import sys; sys.path.insert(0, '/app')\n"
        "from api import auth\n"
        "tok = auth.create_session(auth_type='password', username='io-e2e')\n"
        "open('/tmp/e2e_cookie.txt', 'w').write(tok)\n"
        "print('MINTED')\n"
        "PYEOF")
print("mint:", exec_in(MINT).strip()[:20])

# save the minted token OUT via exec output (re-read it)
tok = exec_in("cat /tmp/e2e_cookie.txt").strip().splitlines()[-1]
print("token len:", len(tok))

# E2E: served bytes with the cookie
req = (f"curl -s -m 8 -H 'Cookie: hermes_session={tok}' "
       "http://127.0.0.1:8787/playtest-feat/prototype/js/player.js | grep -c leftHand; "
       "curl -s -m 8 -H 'Cookie: hermes_session={tok}' "
       "http://127.0.0.1:8787/playtest-feat/prototype/js/spells.js | grep -c Radiance; "
       "curl -s -m 8 -o /dev/null -w '%{{http_code}}' -H 'Cookie: hermes_session={tok}' "
       "http://127.0.0.1:8787/playtest-feat/")
print("e2e served:", exec_in(req.format(tok=tok) if '{}' in req else req))