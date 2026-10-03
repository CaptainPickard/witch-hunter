"""Witch Hunter World R4 validation harness - pixelated character bodies (P0-7
re-scoped: offline-baked 512px atlas PNGs swapped onto the rigged bodies).

Devbot-authored (gate step 3) from the valspec of record
io/specs/testerbot-spec-wh-world-r4.md (Testerbot authored the valspec of
record and REVALIDATES this harness on lane recovery - no silent fallback).
Implements AC-R4-1..R4-5 + PRES + PNG proof + amendments B1-B9 against the
LIVE tree (prototype/index.html via prototype/server.py). Playwright sync
API, headless chromium --enable-unsafe-swiftshader, page-clock timing only.

Env: WH_BASE_ROOT (reuse candidate, identity-checked incl. CONFIG byte
equality + pixelatedBodies), WH_W4_PORT (0 = ephemeral self-spawn),
WH_SMOKE=1 (1 settle-rep; subprocesses still run), WH_W4_FLOOR=0 (skip
R4-4 + R4-5 subprocesses -> SKIP-NOTED, never PASS), WH_W4_PRE_A2 (optional
JSON of pre-R4 A2 numbers; else tests/artifacts/r4-pre-a2.json; else
measured live on a git-archive copy of the pre-Devbot tree).

Assembled build artifact: cat tests/r4parts/part01..NN.py (see
tests/r4parts/build.py). Exit code is ALWAYS 0 - failures are data; the
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
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
BASE_ROOT = os.environ.get("WH_BASE_ROOT", "")
PORT = int(os.environ.get("WH_W4_PORT", "0"))
SMOKE = os.environ.get("WH_SMOKE", "0") == "1"
FLOOR = os.environ.get("WH_W4_FLOOR", "1") != "0"
PRE_A2_ENV = os.environ.get("WH_W4_PRE_A2", "")
FORBIDDEN_PORT = 8791           # landed-work server: never touched
BASE_COMMIT = "cce06eb"         # R3 marker = R4 CODE base (valspec header)
PNG_COMMIT = "8bd137a"          # PNGs + spec committed (pre-Devbot tree)
VIEW_W, VIEW_H = 1920, 1080
ATLAS = 512
BODIES = ["playerBody", "banditBody", "ghoulBody"]
STEMS = {"playerBody": "human-hunter-male", "banditBody": "orc-male-warrior",
         "ghoulBody": "undead-ghoul-male"}
RIGGED_DIR = "art-direction/3d/assets/races_regen/rigged/"
PNG_PATHS = {b: RIGGED_DIR + STEMS[b] + ".rigged.pixelated.png" for b in BODIES}
GLB_PATHS = {b: RIGGED_DIR + STEMS[b] + ".rigged.glb" for b in BODIES}
ART_DIR = os.path.join(REPO_ROOT, "tests", "artifacts")
PRE_A2_FILE = os.path.join(ART_DIR, "r4-pre-a2.json")
PRE_OFF_FILE = os.path.join(ART_DIR, "r4-pre-off.json")
# prototype/index.html pin = cce06eb blob (valspec header 9ad39b809bc4...)
INDEX_FREEZE_SHA256 = ("9ad39b809bc413c723f3cefd5728dfc1d5179f083c01f2846ed"
                       "f36806055dc32")
# AC-PRES allowed set (valspec, exactly)
PRES_SURFACE = ["prototype/js/assets.js", "prototype/js/CONFIG.js",
                PNG_PATHS["playerBody"], PNG_PATHS["banditBody"],
                PNG_PATHS["ghoulBody"], "io/specs/*-r4*", "io/reports/*r4*",
                "tests/wh_world_r4_validation.py", "tests/r4parts",
                "tests/r4parts/*", "tests/artifacts/r4-*"]
FORBIDDEN_PROTO = ["prototype/index.html", "prototype/js/player.js",
                   "prototype/js/game.js", "prototype/js/enemy.js",
                   "prototype/js/anim.js", "prototype/js/region-manager.js",
                   "prototype/style.css"]

RESULTS = []
FLAKES = []
REQ8791 = []                    # any ':8791' URL seen in any request log
EXTRA = {"kill_switch": {"on": [], "off": [], "rewrite_count": None},
         "mem_table": [], "floor": {"r1": {}, "anim": {}}, "notes": []}


class InfraError(Exception):
    """Infra-shaped failure (flake rule: retried up to 2x with reload)."""


def check(ac, name, ok, detail="", verdict=None):
    """One AC = one recorded line. verdict overrides PASS/FAIL (RECORD,
    WAIVED, SKIP-NOTED, BLOCK, FAIL-RETUNE-PENDING)."""
    ok = bool(ok)
    v = verdict or ("PASS" if ok else "FAIL")
    RESULTS.append({"id": ac, "name": name, "ok": ok, "verdict": v,
                    "detail": str(detail)})
    print("AC-%s %-30s => %s  %s" % (ac, name, v, detail))
    sys.stdout.flush()
    return ok


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    try:
        with open(path, "rb") as f:
            return sha256_bytes(f.read())
    except Exception as e:
        return "ERR:%r" % e


def in_surface(path, pats=None):
    return any(fnmatch.fnmatch(path, p) for p in (pats or PRES_SURFACE))


def git(*args, timeout=60):
    return subprocess.run(["git"] + list(args), cwd=REPO_ROOT,
                          capture_output=True, text=True,
                          timeout=timeout).stdout or ""


def git_blob(rev, path):
    """Raw bytes of path at rev (None if absent)."""
    p = subprocess.run(["git", "show", "%s:%s" % (rev, path)], cwd=REPO_ROOT,
                       capture_output=True, timeout=120)
    return p.stdout if p.returncode == 0 else None


def save_json(path, obj):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
    except Exception as e:
        print("[diag] artifact write failed %s %r" % (path, e))


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


# ------------------------------------------------- server + page plumbing ----
def _served(base, rel):
    with urllib.request.urlopen(base.rstrip("/") + "/" + rel,
                                timeout=5.0) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def _identity_ok(base):
    """Law 5 + R3 signature + B9 pixelatedBodies + A1 byte equality."""
    if (":%d" % FORBIDDEN_PORT) in base:
        return False            # never touch the landed-work server
    try:
        _s, _ct, src = _served(base, "js/CONFIG.js")
        with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js"),
                  "rb") as f:
            mine = f.read()
        return (b"lightPool" in src and b"ambientIntensity: 0" in src
                and b"internalResDiv" in src and b"pixelatedBodies" in src
                and src == mine)
    except Exception:
        return False


def _served_ok(base):
    """Self-spawn readiness: CONFIG served byte-equal to our worktree (the
    pre-Devbot tree lacks pixelatedBodies, so identity can never hold
    there; byte equality still proves the server is OUR tree)."""
    if (":%d" % FORBIDDEN_PORT) in base:
        return False
    try:
        _s, _ct, src = _served(base, "js/CONFIG.js")
        with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js"),
                  "rb") as f:
            return src == f.read()
    except Exception:
        return False


def _free_port():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    p = sock.getsockname()[1]
    sock.close()
    return p


def spawn_server(root, port=0, ident=None):
    """Spawn <root>/prototype/server.py on port (0 = ephemeral); poll until
    ident(base) (default: HTTP 200). Returns (proc, base) or (proc, None)."""
    port = port or _free_port()
    if port == FORBIDDEN_PORT:
        port = _free_port()
    base = "http://localhost:%d/" % port
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py", str(port)],
            cwd=os.path.join(root, "prototype"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        print("[diag] server spawn failed %r" % e)
        return None, None
    deadline = time.time() + 15.0
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        try:
            if ident is not None:
                if ident(base):
                    return proc, base
            else:
                with urllib.request.urlopen(base, timeout=1.0) as r:
                    if r.status == 200:
                        return proc, base
        except Exception:
            pass
        time.sleep(0.3)
    print("[diag] server on %d never came up" % port)
    return proc, None


def start_server():
    """Reuse WH_BASE_ROOT only with full identity; else self-spawn from
    REPO_ROOT on WH_W4_PORT / ephemeral. Returns (proc, how, identity)."""
    global BASE_ROOT, PORT
    if BASE_ROOT and _identity_ok(BASE_ROOT):
        PORT = int(BASE_ROOT.rstrip("/").rsplit(":", 1)[1].split("/")[0])
        return None, "reused %s" % BASE_ROOT, True
    refused = BASE_ROOT or "none"
    proc, base = spawn_server(REPO_ROOT, PORT, ident=_served_ok)
    if base:
        BASE_ROOT = base
        PORT = int(base.rsplit(":", 1)[1].strip("/"))
        return (proc, "reuse-refused(%s) self-spawn port %d" % (refused, PORT),
                _identity_ok(base))
    return proc, "self-spawn FAILED", False


def stop_server(proc):
    if proc is None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


READY_JS = ("(function(){try{return typeof window.WH_DEBUG==='object' && "
            "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
            "!!window.WH_DEBUG.getPlayerPosition() && !!window.WH_GAME && "
            "!!window.WH_GAME.renderer && !!window.WH_ASSETS;}"
            "catch(e){return false;}})()")

FRAMES_JS = ("function(n){return new Promise(function(res){var k=n;"
             "function f(){if(--k<=0)res(true);else requestAnimationFrame(f);}"
             "requestAnimationFrame(f);});}")


def wait_frames(page, n):
    """Wall-generous rAF wait (law 1: SwiftShader 1-3fps)."""
    page.evaluate(FRAMES_JS, n)


def new_errs():
    return {"console": [], "page": [], "resp": [], "req": [], "png": []}


def new_page(browser, errs, dsf=1):
    """Context + page with full request log (8791 BLOCK + PNG counts).
    Returns (ctx, page)."""
    ctx = browser.new_context(viewport={"width": VIEW_W, "height": VIEW_H},
                              device_scale_factor=dsf)
    page = ctx.new_page()

    def on_req(r):
        errs["req"].append(r.url)
        if (":%d" % FORBIDDEN_PORT) in r.url:
            REQ8791.append(r.url)

    def on_resp(r):
        if r.status >= 400:
            errs["resp"].append({"url": r.url, "s": r.status})
        if r.url.endswith(".pixelated.png"):
            errs["png"].append({"url": r.url, "s": r.status,
                                "ct": r.headers.get("content-type", "")})
    page.on("pageerror", lambda e: errs["page"].append(str(e)))
    page.on("console", lambda m: errs["console"].append(m.text)
            if m.type == "error" else None)
    page.on("request", on_req)
    page.on("response", on_resp)
    return ctx, page


def load_index(page, base=None, path=""):
    page.goto((base or BASE_ROOT) + path, wait_until="load", timeout=60000)
    deadline = time.time() + 60.0
    while time.time() < deadline:
        try:
            if page.evaluate(READY_JS):
                page.wait_for_timeout(1500)
                wait_frames(page, 6)     # law 3: camera settle at spawn
                return True
        except Exception:
            pass
        page.wait_for_timeout(250)
    print("[diag] WH_DEBUG never ready")
    return False


def decode_image(data):
    """PNG bytes or data URL -> PIL RGB image (PIL 12.3 on the box)."""
    from PIL import Image
    import base64
    if isinstance(data, str) and data.startswith("data:"):
        data = base64.b64decode(data.split(",", 1)[1])
    return Image.open(io.BytesIO(data)).convert("RGB")


def is_degenerate(img):
    """All-zero / single-colour frame = SwiftShader degenerate (flake)."""
    return all(lo == hi for lo, hi in img.getextrema())
