"""Witch Hunter World R2 validation harness (IO-authored under Nicko's 09-25
lane ruling after Testerbot authoring lane death #9; Testerbot authored the
valspec of record io/specs/testerbot-spec-wh-world-r2.md and REVALIDATES this
harness when the lane recovers - no silent fallback).

Validates ACs L1-L10 + FLOOR + SCOPE of io/specs/devbot-spec-wh-world-r2.md
against the LIVE tree (prototype/index.html via prototype/server.py).
Playwright sync API, headless chromium (--enable-unsafe-swiftshader),
page-clock timing only. WH_BASE_ROOT / WH_R2_PORT env overrides;
WH_SMOKE=1 short mode; WH_R2_FLOOR=0 skips the R1 floor subprocess.

Exit code is ALWAYS 0 - failures are data (final stdout line is JSON).
"""
from playwright.sync_api import sync_playwright
import base64
import fnmatch
import json
import math
import os
import re
import struct
import subprocess
import sys
import time
import urllib.request
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
BASE_ROOT = os.environ.get("WH_BASE_ROOT", "http://localhost:8792/")
PORT = int(os.environ.get("WH_R2_PORT", "8792"))
SMOKE = os.environ.get("WH_SMOKE", "0") == "1"
FLOOR = os.environ.get("WH_R2_FLOOR", "1") != "0"

# Dispatch-time preservation floors (A6 re-baseline per IO ruling 2026-10-01):
# old R1 constants (d2893c23.../9093216d...) DRIFT because the combat
# (02ca0ac) and anim (f881dac/d c697ce) rounds validated NEW harness files;
# drift traces to those validated rounds, never to R2 interference.
FLOOR_WEAVE = {
    "path": "tests/wh_v7_weave.py",
    "sha256": "f07dec10e58f3ea34bb3967bb29250a031b6ae76f345fbebdcba49233c1f8a13",
}
FLOOR_DS1 = {
    "path": "tests/wh_combat_ds1_validation.py",
    "sha256": "254c323132b8aaeb95c3fe95b19e690fe0a9e9407e83f56dc1bfd403f7934178",
}

RESULTS = []
FLAKES = []


def check(ac, name, ok, detail="", verdict=None):
    """One check = one AC-line. verdict may be PASS/FAIL/RECORD."""
    ok = bool(ok)
    v = verdict or ("PASS" if ok else "FAIL")
    RESULTS.append({"id": ac, "name": name, "ok": ok, "verdict": v,
                    "detail": str(detail)})
    print("AC-%s %-38s => %s  %s" % (ac, name, v, detail))
    return ok


def sha256_file(path):
    import hashlib
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return "ERR:%r" % e