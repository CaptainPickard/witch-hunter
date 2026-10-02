"""Witch Hunter World R3 validation harness - internal-res pixelation (P0-4).

Devbot-authored (gate step 3) from the valspec of record
io/specs/testerbot-spec-wh-world-r3.md (Testerbot authored the valspec of
record and REVALIDATES this harness on lane recovery - no silent fallback).
Implements AC-P1..P6 + amendments A1-A9 against the LIVE tree
(prototype/index.html via prototype/server.py). Playwright sync API,
headless chromium --enable-unsafe-swiftshader, page-clock timing only.

Env: WH_BASE_ROOT (reuse candidate, identity-checked incl. CONFIG byte
equality), WH_W3_PORT (0 = ephemeral self-spawn), WH_SMOKE=1 (P2 reps 1),
WH_W3_FLOOR=0 (skip P3+P4 subprocesses -> SKIP-NOTED), WH_W3_DIVS (1,2,4),
WH_W3_PRE_TRIS (optional pre-impl triangle count; else measured live on a
git-archive copy of the base tree).

Assembled build artifact: cat tests/r3parts/part01..10.py (see
tests/r3parts/build.sh). Exit code is ALWAYS 0 - failures are data; the
final stdout line is one JSON verdict object.
"""
from playwright.sync_api import sync_playwright
import fnmatch
import hashlib
import io
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
BASE_ROOT = os.environ.get("WH_BASE_ROOT", "")
PORT = int(os.environ.get("WH_W3_PORT", "0"))
SMOKE = os.environ.get("WH_SMOKE", "0") == "1"
FLOOR = os.environ.get("WH_W3_FLOOR", "1") != "0"
DIVS = [int(x) for x in os.environ.get("WH_W3_DIVS", "1,2,4").split(",")
        if x.strip()]
PRE_TRIS_ENV = os.environ.get("WH_W3_PRE_TRIS", "")
FORBIDDEN_PORT = 8791           # landed-work server: never touched
BASE_COMMIT = "0406e64"         # R2 marker = R3 code base (valspec header)
DISPATCH_DIV = 2                # AC-P6 bar at dispatch (retune moves it)
VIEW_W, VIEW_H = 1920, 1080
# prototype/index.html pin — IO AMENDMENT A10 (ruling 6474019): pinned to
# the R3 CODE BASE 0406e64, not R1's stale freeze (the file is unchanged
# since base; the old cec75217... pin pre-dated anim/combat).
INDEX_FREEZE_SHA256 = ("9ad39b809bc413c723f3cefd5728dfc1d5179f083c01f2846ed"
                       "f36806055dc32")
# P5 allowed surface (valspec AC-P5)
P5_SURFACE = ["prototype/js/game.js", "prototype/js/CONFIG.js",
              "prototype/style.css", "io/specs/*-r3*", "io/reports/*r3*",
              "tests/wh_world_r3_validation.py", "tests/r3parts",
              "tests/r3parts/*"]

RESULTS = []
FLAKES = []
EXTRA = {"floor": {"r1": {}, "r2": {}}, "p2_table": [], "notes": []}


class InfraError(Exception):
    """Infra-shaped failure (flake rule: retried up to 2x with reload)."""


def check(ac, name, ok, detail="", verdict=None):
    """One AC = one recorded line. verdict overrides PASS/FAIL (RECORD,
    WAIVED, SKIP-NOTED, FAIL-RETUNE-PENDING)."""
    ok = bool(ok)
    v = verdict or ("PASS" if ok else "FAIL")
    RESULTS.append({"id": ac, "name": name, "ok": ok, "verdict": v,
                    "detail": str(detail)})
    print("AC-%s %-34s => %s  %s" % (ac, name, v, detail))
    sys.stdout.flush()
    return ok


def sha256_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return "ERR:%r" % e


def in_surface(path, pats=None):
    return any(fnmatch.fnmatch(path, p) for p in (pats or P5_SURFACE))


def git(*args, timeout=60):
    return subprocess.run(["git"] + list(args), cwd=REPO_ROOT,
                          capture_output=True, text=True,
                          timeout=timeout).stdout or ""
