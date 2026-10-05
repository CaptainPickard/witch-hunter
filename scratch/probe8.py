#!/usr/bin/env python3
"""E2E attempt 2: same but write-out fixed + root page served check."""
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

tok = exec_in("cat /tmp/e2e_cookie.txt").strip().splitlines()[-1]

def served(path):
    cmd = (f"curl -s -m 8 -H 'Cookie: hermes_session={tok}' "
           f"http://127.0.0.1:8787{path}")
    return exec_in(cmd)

# served CONTENT checks
p1 = served("/playtest-feat/prototype/js/player.js")
print("served player leftHand:", p1.count("leftHand"))
print("served player stow:", p1.count("stowToShield"))
s1 = served("/playtest-feat/prototype/js/spells.js")
print("served spells Radiance:", s1.count("Radiance"))
hdr = served("/playtest-feat/")
print("root page served head:", hdr[:40].strip())
print("root has build marker:", "Pixel fidelity" in hdr or "wh-res-tuner" in hdr)
# status code for root
cmd = (f"curl -s -m 8 -o /dev/null -w CODE:%{{http_code}} -H 'Cookie: hermes_session={tok}' "
       "http://127.0.0.1:8787/playtest-feat/")
print("root status:", [l for l in exec_in(cmd).split("\n") if "CODE:" in l][-1:])