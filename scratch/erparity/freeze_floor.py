#!/usr/bin/env python3
"""Freeze the E2 floor: run the four remaining baseline suites against the
origin/dev worktree server (8794 -- the worktree's own server; 8793 serves the
tainted main checkout). Write e2_floor.json with per-AC verdicts.
Suite list and tags must match the E2 probe in wh_erparity_validation.py."""
import json, os, subprocess, sys

ROOT = "/workspace/wh-erparity-test"
OUT = "/workspace/witch-hunter/scratch/erparity/e2_floor.json"
LOGD = "/workspace/witch-hunter/scratch/erparity/floor"
BASE = "http://127.0.0.1:8794/"

SUITES = [
    ("tests/wh_combat_ds1_validation.py", "combat-ds1-A", "ds1_floor.log"),
    ("tests/wh_v7_weave.py", "weave", "weave_floor.log"),
    ("tests/wh_v2_verify.py", "v2-assets", "v2_floor.log"),
    ("tests/wh_v3_anim_probes.py", "v3-anim", "v3_floor.log"),
    # mousebind suite excluded: exists only on feat/mouse-bind-cam, not on
    # origin/dev (see IO recovery note in wh_erparity_validation.py E2).
]


def harvest(text):
    per_ac = {}
    start = text.rfind('{"round"')
    if start < 0:
        start = text.rfind('{\n')
    if start >= 0:
        try:
            blob = json.loads(text[start:])
            for item in blob.get("per_ac", []):
                per_ac[item["id"].replace("AC-", "")] = item["verdict"]
            if per_ac:
                return per_ac, blob
        except Exception:
            pass
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("AC-") and "=> " in s:
            i = s[3:].split()[0].rstrip(":")
            per_ac[i] = "PASS" if "=> PASS" in s else "FAIL"
    return per_ac, None


floor = {}
summary = {}
for rel, tag, logname in SUITES:
    p = os.path.join(ROOT, rel)
    logp = os.path.join(LOGD, logname)
    if not os.path.isfile(p):
        print("SKIP missing: %s" % rel)
        continue
    if os.path.isfile(logp) and os.path.getsize(logp) > 0:
        txt = open(logp).read()
        print("reuse %s (%d bytes)" % (logname, len(txt)))
    else:
        env = dict(os.environ)
        env["WH_BASE_ROOT"] = BASE
        env["WH_MB_ROOT"] = BASE
        env.pop("WH_BASE_PROXY", None)
        print("running %s ..." % tag, flush=True)
        try:
            r = subprocess.run([sys.executable, p], cwd=ROOT, capture_output=True,
                               text=True, timeout=1500, env=env)
            txt = r.stdout + "\n" + r.stderr
            open(logp, "w").write(txt)
            print("  exit=%d bytes=%d" % (r.returncode, len(txt)))
        except subprocess.TimeoutExpired:
            print("  TIMEOUT")
            open(logp, "w").write("TIMEOUT")
            continue
    per_ac, blob = harvest(txt)
    floor[tag] = per_ac
    summary[tag] = {"total": len(per_ac),
                    "pass": sum(1 for v in per_ac.values() if v == "PASS"),
                    "fail": sum(1 for v in per_ac.values() if v == "FAIL")}

json.dump(floor, open(OUT, "w"), indent=1)
print()
print(json.dumps(summary, indent=1))
print("floor written to %s" % OUT)
