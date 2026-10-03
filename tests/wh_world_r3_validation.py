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


# ------------------------------------------------- server + page plumbing ----
def _served_config(base):
    with urllib.request.urlopen(base.rstrip("/") + "/js/CONFIG.js",
                                timeout=2.0) as r:
        return r.read()


def _identity_ok(base):
    """Law 5 + R3 signature + A1 byte equality: the served CONFIG.js must
    carry lightPool, ambientIntensity 0, internalResDiv AND equal the
    worktree's prototype/js/CONFIG.js byte-for-byte."""
    if (":%d" % FORBIDDEN_PORT) in base:
        return False            # never touch the landed-work server
    try:
        src = _served_config(base)
        with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js"),
                  "rb") as f:
            mine = f.read()
        return (b"lightPool" in src and b"ambientIntensity: 0" in src
                and b"internalResDiv" in src and src == mine)
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
    """Reuse WH_BASE_ROOT only with full identity (A1); else self-spawn
    from REPO_ROOT on WH_W3_PORT / ephemeral. Returns (proc, how)."""
    global BASE_ROOT, PORT
    if BASE_ROOT and _identity_ok(BASE_ROOT):
        return None, "reused %s" % BASE_ROOT
    refused = BASE_ROOT or "none"
    proc, base = spawn_server(REPO_ROOT, PORT, ident=_identity_ok)
    if base:
        BASE_ROOT = base
        PORT = int(base.rsplit(":", 1)[1].strip("/"))
        return proc, "reuse-refused(%s) self-spawn port %d" % (refused, PORT)
    return proc, "self-spawn FAILED"


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
            "!!window.WH_GAME.renderer;}catch(e){return false;}})()")

FRAMES_JS = ("function(n){return new Promise(function(res){var k=n;"
             "function f(){if(--k<=0)res(true);else requestAnimationFrame(f);}"
             "requestAnimationFrame(f);});}")


def wait_frames(page, n):
    """Wall-generous rAF wait (law 1: SwiftShader 1-3fps)."""
    page.evaluate(FRAMES_JS, n)


def new_page(ctx_owner, errs, dsf=1):
    """errs = {'console':[], 'page':[], 'resp':[]}. Returns (ctx, page)."""
    ctx = ctx_owner.new_context(viewport={"width": VIEW_W, "height": VIEW_H},
                                device_scale_factor=dsf)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errs["page"].append(str(e)))
    page.on("console", lambda m: errs["console"].append(m.text)
            if m.type == "error" else None)
    page.on("response", lambda r: errs["resp"].append(
        {"url": r.url, "s": r.status}) if r.status >= 400 else None)
    return ctx, page


def load_index(page, base=None, path=""):
    page.goto((base or BASE_ROOT) + path, wait_until="load", timeout=60000)
    deadline = time.time() + 40.0
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


# ----------------------------------------- image decode + block metrics ----
def decode_image(data):
    """PNG bytes or data URL -> PIL RGB image (PIL 12.3 on the box)."""
    from PIL import Image
    import base64
    if isinstance(data, str) and data.startswith("data:"):
        data = base64.b64decode(data.split(",", 1)[1])
    return Image.open(io.BytesIO(data)).convert("RGB")


def is_degenerate(img):
    """All-zero / single-colour frame = SwiftShader degenerate (flake)."""
    ext = img.getextrema()
    return all(lo == hi for lo, hi in ext)


def _eq(a, b):
    return (abs(a[0] - b[0]) <= 2 and abs(a[1] - b[1]) <= 2
            and abs(a[2] - b[2]) <= 2)


def block_metrics(img):
    """A2: block structure on the COMPOSITED display (page.screenshot).
    Band = ground rows [0.72h,0.95h] x cols [0.30w,0.70w]. Phase (0/1)
    auto-detected once from the horizontal aligned-vs-misaligned gap and
    reused for every metric."""
    w, h = img.size
    px = img.load()
    x0, x1 = int(0.30 * w), int(0.70 * w)
    y0, y1 = int(0.72 * h), int(0.95 * h)

    def pair_h(ph):
        eq = n = 0
        for y in range(y0, y1):
            for x in range(x0 + ((ph - x0) % 2), x1 - 1, 2):
                n += 1
                eq += _eq(px[x, y], px[x + 1, y])
        return eq / max(1, n)

    def pair_v(ph):
        eq = n = 0
        for y in range(y0 + ((ph - y0) % 2), y1 - 1, 2):
            for x in range(x0, x1):
                n += 1
                eq += _eq(px[x, y], px[x, y + 1])
        return eq / max(1, n)

    p0, p1 = pair_h(0), pair_h(1)
    phase = 0 if (p0 - p1) >= (p1 - p0) else 1
    aligned_h = p0 if phase == 0 else p1
    misaligned = p1 if phase == 0 else p0
    aligned_v = pair_v(phase)
    # run lengths over 20 sampled rows (truncated first/last run dropped)
    hist = {}
    runs_total = runs_even = 0
    for k in range(20):
        y = y0 + int(k * (y1 - y0 - 1) / 19.0)
        runs = []
        start = x0
        for x in range(x0 + 1, x1):
            if not _eq(px[x, y], px[x - 1, y]):
                runs.append((start, x - start))
                start = x
        runs.append((start, x1 - start))
        for (_s, ln) in runs[1:-1]:
            runs_total += 1
            runs_even += (ln % 2 == 0)
            hist[ln] = hist.get(ln, 0) + 1
    modal = max(hist.items(), key=lambda kv: kv[1])[0] if hist else 0
    top5 = sorted(hist.items(), key=lambda kv: -kv[1])[:5]
    return {"phase": phase, "aligned_h": round(aligned_h, 4),
            "aligned_v": round(aligned_v, 4),
            "misaligned": round(misaligned, 4),
            "gap": round(aligned_h - misaligned, 4),
            # A10 primary bar (was RECORD-only): share of colour edges
            # that fall ON the block grid; bilinear/no-grid ~0.5,
            # pixel-locked -> 1.0
            "edge_on_grid": round((1 - misaligned) / max(
                1e-9, (1 - aligned_h) + (1 - misaligned)), 4),
            "even_frac": round(runs_even / max(1, runs_total), 4),
            "runs": runs_total, "modal_run": modal, "run_top5": top5,
            "band": [x0, y0, x1, y1]}


def block_bars(m):
    """Valspec AC-P1(b) bars per IO ruling A10 (6474019): aligned bars +
    even-run + modal-run unchanged; the scene-flat misaligned control-gap
    bar (0.15) is REPLACED by edge_on_grid >= 0.80 (colour-edge grid
    adjacency: pixel-locked ~1.0, bilinear/no-grid ~0.5)."""
    return (m["aligned_h"] >= 0.90 and m["aligned_v"] >= 0.90
            and m["edge_on_grid"] >= 0.80 and m["even_frac"] >= 0.90
            and m["modal_run"] >= 2)


# ------------------------------------------------------------ AC-P1 --------
SNAP_JS = """(function(){var G=window.WH_GAME, c=G.renderer.domElement;
  G.renderer.render(G.scene,G.camera);     // law 2: render+readback 1 eval
  return {cw:c.width, ch:c.height, dw:c.clientWidth, dh:c.clientHeight,
          ir:getComputedStyle(c).imageRendering,
          pr:G.renderer.getPixelRatio(), dpr:window.devicePixelRatio,
          url:c.toDataURL('image/png')};})()"""

DIMS_JS = """(function(){var c=window.WH_GAME.renderer.domElement;
  return {cw:c.width, ch:c.height, pr:window.WH_GAME.renderer.getPixelRatio(),
          dpr:window.devicePixelRatio};})()"""


def poll_dims(page, want, wall=20.0):
    """Wait (wall-generous) until the canvas buffer reaches want=(w,h)."""
    d = None
    deadline = time.time() + wall
    while time.time() < deadline:
        d = page.evaluate(DIMS_JS)
        if (d["cw"], d["ch"]) == want:
            return d
        page.wait_for_timeout(300)
    return d


def ac_p1(browser, page, errs, div):
    want = (round(VIEW_W / div), round(VIEW_H / div))
    # (a) buffer readback
    s = page.evaluate(SNAP_JS)
    img = decode_image(s["url"])
    if is_degenerate(img):
        raise InfraError("degenerate readback frame")
    a_ok = ((s["cw"], s["ch"]) == want and img.size == want
            and (s["dw"], s["dh"]) == (VIEW_W, VIEW_H)
            and s["ir"] in ("pixelated", "crisp-edges") and s["pr"] == 1)
    a_ev = ("buf=%dx%d dec=%dx%d disp=%dx%d ir=%s pr=%s"
            % (s["cw"], s["ch"], img.size[0], img.size[1], s["dw"], s["dh"],
               s["ir"], s["pr"]))
    # (b) A2 block metrics on the composited display
    wait_frames(page, 2)
    shot = decode_image(page.screenshot(type="png", full_page=False))
    if is_degenerate(shot):
        raise InfraError("blank screenshot")
    try:
        shot.save("/tmp/whr3_p1_shot.png")
    except Exception:
        pass
    m = block_metrics(shot)
    b_ok = block_bars(m)
    # (c) resize path
    page.set_viewport_size({"width": 1280, "height": 720})
    wait_frames(page, 2)
    dc = poll_dims(page, (round(1280 / div), round(720 / div)))
    page.set_viewport_size({"width": VIEW_W, "height": VIEW_H})
    wait_frames(page, 2)
    dr = poll_dims(page, want)
    c_ok = ((dc["cw"], dc["ch"]) == (round(1280 / div), round(720 / div))
            and (dr["cw"], dr["ch"]) == want)
    # (d) DPR law: dsf=2 context still renders the low-res buffer
    derr = {"console": [], "page": [], "resp": []}
    ctx2, p2 = new_page(browser, derr, dsf=2)
    try:
        if not load_index(p2):
            raise InfraError("dsf2 page never ready")
        dd = poll_dims(p2, want, wall=10.0)
    finally:
        ctx2.close()
    d_ok = (dd["cw"], dd["ch"]) == want and dd["pr"] == 1 and dd["dpr"] == 2
    ev = ("a=%s[%s] b=%s[%s] c=%s[720p=%dx%d back=%dx%d] "
          "d=%s[dsf2 buf=%dx%d pr=%s dpr=%s]"
          % (a_ok, a_ev, b_ok, json.dumps(m), c_ok, dc["cw"], dc["ch"],
             dr["cw"], dr["ch"], d_ok, dd["cw"], dd["ch"], dd["pr"],
             dd["dpr"]))
    if a_ok and b_ok and c_ok and d_ok:
        check("P1", "pixel-locked upscale", True, ev)
    elif a_ok and c_ok and d_ok:
        check("P1", "pixel-locked upscale", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("P1", "pixel-locked upscale", False, ev)


# ------------------------------------------------------------ AC-P2 --------
# Sanctioned measurement write (valspec): renderer.internalResDiv + resize.
# A3: every timed render is followed by a 1-px gl.readPixels sync.
SWEEP_JS = """function(a){var divs=a[0], n=a[1], warm=a[2];
  var G=window.WH_GAME, R=G.renderer, C=window.WH_CONFIG.renderer;
  var gl=R.getContext(), buf=new Uint8Array(4), rows=[], orig=C.internalResDiv;
  function one(){R.render(G.scene,G.camera);
    gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,buf);}
  for(var k=0;k<divs.length;k++){
    C.internalResDiv=divs[k]; window.dispatchEvent(new Event('resize'));
    for(var i=0;i<warm;i++) one();
    var t0=performance.now();
    for(var j=0;j<n;j++) one();
    var ms=(performance.now()-t0)/n;
    rows.push({div:divs[k], w:R.domElement.width, h:R.domElement.height,
      ms:ms, tris:R.info.render.triangles, calls:R.info.render.calls});
  }
  C.internalResDiv=orig; window.dispatchEvent(new Event('resize'));
  return rows;}"""

TRIS_JS = """(function(){var G=window.WH_GAME;
  G.renderer.render(G.scene,G.camera);
  return {tris:G.renderer.info.render.triangles,
          calls:G.renderer.info.render.calls};})()"""


def tmp_tree(src_prototype=None, archive_rev=None):
    """Temp repo-shaped root: prototype/ (copy of worktree or git archive
    of archive_rev) + tools/build_v7.py; every other top-level entry is
    symlinked (assets are served from the repo root)."""
    root = tempfile.mkdtemp(prefix="whr3_")
    if archive_rev:
        arc = subprocess.run(["git", "archive", archive_rev, "prototype"],
                             cwd=REPO_ROOT, capture_output=True, timeout=120)
        subprocess.run(["tar", "-x", "-C", root], input=arc.stdout,
                       capture_output=True, timeout=120)
    else:
        shutil.copytree(src_prototype, os.path.join(root, "prototype"),
                        ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(root, "tools"))
    shutil.copy(os.path.join(REPO_ROOT, "tools", "build_v7.py"),
                os.path.join(root, "tools", "build_v7.py"))
    for ent in os.listdir(REPO_ROOT):
        if ent in ("prototype", "tools", ".git"):
            continue
        os.symlink(os.path.join(REPO_ROOT, ent), os.path.join(root, ent))
    return root


def pre_triangles(browser):
    """Pre-implementation triangle count at the same pose (A spawn after
    settle) measured on a git-archive copy of the R2 base tree."""
    if PRE_TRIS_ENV:
        return int(PRE_TRIS_ENV), "env"
    root = tmp_tree(archive_rev=BASE_COMMIT)
    proc = None
    try:
        proc, base = spawn_server(root)
        if not base:
            return None, "pre-server-failed"
        errs = {"console": [], "page": [], "resp": []}
        ctx, pg = new_page(browser, errs)
        try:
            if not load_index(pg, base):
                return None, "pre-page-never-ready"
            return pg.evaluate(TRIS_JS)["tris"], "archive %s" % BASE_COMMIT
        finally:
            ctx.close()
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def ac_p2(browser, page, div):
    reps = 1 if SMOKE else 3
    pre, pre_src = pre_triangles(browser)
    allrows = []
    for rep in range(reps):
        rows = page.evaluate(SWEEP_JS, [DIVS, 20, 3])
        for r in rows:
            r["rep"] = rep
        allrows.extend(rows)
    back = poll_dims(page, (round(VIEW_W / div), round(VIEW_H / div)))
    restored = (back["cw"], back["ch"]) == (round(VIEW_W / div),
                                            round(VIEW_H / div))
    base1 = {r["rep"]: r for r in allrows if r["div"] == 1}
    a_ok = True
    pre_miss_reps = 0
    for rep in range(reps):
        tr = {r["tris"] for r in allrows if r["rep"] == rep}
        a_ok = a_ok and len(tr) == 1
        if pre is not None and tr != {pre}:
            pre_miss_reps += 1
    pre_fail = pre is not None and pre_miss_reps == reps
    b_ok = True
    table = []
    med1 = None
    for d in DIVS:
        rs = [r for r in allrows if r["div"] == d]
        ms = [round(r["ms"], 2) for r in rs]
        med = statistics.median(ms) if ms else None
        if d == 1:
            med1 = med
        r0, b1 = rs[0], base1.get(rs[0]["rep"])
        elim = (1 - (r0["w"] * r0["h"]) / float(b1["w"] * b1["h"])
                if b1 else None)
        exp = 1 - 1.0 / (d * d)
        if elim is None or abs(elim - exp) > 0.01:
            b_ok = False
        table.append({"div": d, "wxh": "%dx%d" % (r0["w"], r0["h"]),
                      "px": r0["w"] * r0["h"],
                      "eliminated": None if elim is None else round(elim, 4),
                      "expected": round(exp, 4), "ms": ms, "median": med,
                      "tris": [r["tris"] for r in rs],
                      "calls": [r["calls"] for r in rs]})
    for t in table:
        t["ratio_vs_div1"] = (round(t["median"] / med1, 3)
                              if med1 and t["median"] is not None else None)
    EXTRA["p2_table"] = table
    m2 = [t["median"] for t in table if t["div"] == 2]
    c_ok = bool(m2) and med1 is not None and m2[0] <= med1
    ev = ("a=%s(pre=%s src=%s preMissReps=%d/%d) b=%s c=%s restored=%s "
          "hwbar=ENV-LIMIT GPU (p99<=16.6ms GPU-only, M-08) table=%s"
          % (a_ok and not pre_fail, pre, pre_src, pre_miss_reps, reps,
             b_ok, c_ok, restored, json.dumps(table)))
    if a_ok and not pre_fail and b_ok and restored and c_ok:
        check("P2", "fragment cost drop", True, ev)
    elif a_ok and not pre_fail and b_ok and restored:
        check("P2", "fragment cost drop", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("P2", "fragment cost drop", False, ev)


# ------------------------------------------------------------ AC-P5 --------
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# real-assignment law (R2 part10): key-ish word '=' >=8 class chars.
ASSIGN_RE = re.compile(r"(api[_-]?key|apikey|secret|password|token)"
                       r"\s*=\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
MESHY_RE = re.compile(r"msy_[A-Za-z0-9]{8}")
GAME_WINDOWS = [(29, 41), (940, 947)]     # setupRenderer(+helper) / resize
CONFIG_WINDOW = (7, 14)
CONFIG_KEEP = ["outputColorSpaceSRGB: true,", "toneMappingName: 'Neutral',",
               "toneMappingExposure: 1.15,", "maxPixelRatio: 2,",
               "shadowMapEnabled: false"]
CSS_ADD = ["  image-rendering: pixelated;", "  image-rendering: crisp-edges;"]


def hunks(path):
    """[(old_start, old_len, added[], removed[])] vs BASE_COMMIT."""
    out = []
    for ln in git("diff", "-U0", BASE_COMMIT, "--", path).splitlines():
        m = HUNK_RE.match(ln)
        if m:
            ol = int(m.group(2)) if m.group(2) is not None else 1
            out.append([int(m.group(1)), ol, [], []])
        elif out and ln.startswith("+") and not ln.startswith("+++"):
            out[-1][2].append(ln[1:])
        elif out and ln.startswith("-") and not ln.startswith("---"):
            out[-1][3].append(ln[1:])
    return out


def _within(h, windows):
    lo = h[0]
    hi = h[0] + max(h[1], 1) - 1
    return any(a <= lo and hi <= b for a, b in windows)


def style_hunk_exact():
    hs = hunks("prototype/style.css")
    if len(hs) != 1 or hs[0][3] or hs[0][2] != CSS_ADD:
        return False, "hunks=%s" % hs
    src = open(os.path.join(REPO_ROOT, "prototype/style.css")).read()
    m = re.search(r"#wh-canvas\s*\{([^}]*)\}", src)
    body = m.group(1) if m else ""
    ok = (CSS_ADD[0] in body and CSS_ADD[1] in body
          and body.index(CSS_ADD[0]) < body.index(CSS_ADD[1]))
    return ok, "insert@old%d inRule=%s" % (hs[0][0], ok)


def changed_paths():
    dirty = []
    for line in git("status", "--porcelain", "--untracked-files=all"
                    ).splitlines():
        p = line[3:].strip().strip('"')     # R1 A8 leading-3-char strip
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        dirty.append(p)
    committed = [p for p in git("diff", "--name-only", BASE_COMMIT, "HEAD",
                                "--", "prototype", "tests").splitlines() if p]
    gate_docs = [p for p in git("diff", "--name-only", BASE_COMMIT, "HEAD"
                                ).splitlines() if p and p not in committed]
    return dirty, committed, gate_docs


def secrets_scan():
    """git diff vs base (tracked) + content of untracked new files."""
    txt = git("diff", BASE_COMMIT)
    for p in git("ls-files", "--others", "--exclude-standard").splitlines():
        try:
            with open(os.path.join(REPO_ROOT, p), errors="replace") as f:
                txt += f.read()
        except Exception:
            pass
    return (len(MESHY_RE.findall(txt)) + len(ASSIGN_RE.findall(txt)))


def v7_rebuild_clean(browser):
    """A8: rebuild on a temp copy; load result; 0 console/page errors."""
    root = tmp_tree(src_prototype=os.path.join(REPO_ROOT, "prototype"))
    proc = None
    try:
        b = subprocess.run([sys.executable, "tools/build_v7.py"], cwd=root,
                           capture_output=True, text=True, timeout=180)
        if b.returncode != 0:
            return False, "build rc=%d %s" % (b.returncode, b.stderr[-200:])
        proc, base = spawn_server(root)
        if not base:
            return False, "temp server failed"
        errs = {"console": [], "page": [], "resp": []}
        ctx, pg = new_page(browser, errs)
        try:
            ready = load_index(pg, base, "builds/v7-playable.html")
        finally:
            ctx.close()
        ok = ready and not errs["console"] and not errs["page"]
        return ok, "ready=%s consoleErr=%d pageErr=%d" % (
            ready, len(errs["console"]), len(errs["page"]))
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def ac_p5(browser):
    dirty, committed, gate_docs = changed_paths()
    resid = sorted({p for p in dirty + committed if not in_surface(p)})
    proto = sorted({p for p in dirty + committed
                    if p.startswith("prototype/")})
    fourth = [p for p in proto if p not in P5_SURFACE[:3]]
    gh = hunks("prototype/js/game.js")
    g_ok = bool(gh) and all(_within(h, GAME_WINDOWS) for h in gh)
    ch = hunks("prototype/js/CONFIG.js")
    cfg_src = open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")).read()
    removed = [r for h in ch for r in h[3]]
    c_ok = (bool(ch) and all(_within(h, [CONFIG_WINDOW]) for h in ch)
            and all(k in cfg_src for k in CONFIG_KEEP)
            and not any(k in r for r in removed for k in CONFIG_KEEP))
    s_ok, s_ev = style_hunk_exact()
    idx = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    i_ok = idx == INDEX_FREEZE_SHA256
    # RECORD: byte-identity vs the R3 code base (pin drift = combat/anim)
    i_base = not git("diff", "--name-only", BASE_COMMIT, "--",
                     "prototype/index.html").strip()
    v_ok, v_ev = v7_rebuild_clean(browser)
    builds_dirty = [p for p in dirty if p.startswith("prototype/builds/")]
    nsec = secrets_scan()
    added = [a for p in P5_SURFACE[:3] for h in hunks(p) for a in h[2]]
    free_hits = [a for a in added if re.search(r"\bfree\b", a, re.I)]
    untouched = [p for p in proto if re.search(
        r"region-manager\.js|player\.js|hud", p)]
    ok = (not resid and not fourth and g_ok and c_ok and s_ok and i_ok
          and v_ok and not builds_dirty and nsec == 0 and not free_hits
          and not untouched)
    ev = ("resid=%s fourthProto=%s gameHunks=%s(%s) configHunks=%s(%s) "
          "css=%s(%s) index=%s(identToBase=%s) v7=%s(%s) buildsDirty=%s "
          "secretsHits=%d "
          "freeHits=%d untouchedViol=%s gateDocsSinceBase=%d(RECORD: IO "
          "gate-doc commits, outside prototype/tests)"
          % (resid, fourth, g_ok, [(h[0], h[1]) for h in gh], c_ok,
             [(h[0], h[1]) for h in ch], s_ok, s_ev,
             "freeze-ok" if i_ok else "DRIFT:" + idx[:12], i_base, v_ok, v_ev,
             builds_dirty, nsec, len(free_hits), untouched, len(gate_docs)))
    blockish = fourth or not i_ok or nsec
    check("P5", "preservation surface", ok, ev,
          verdict=None if ok else ("BLOCK" if blockish else "FAIL"))


# ------------------------------------------------------------ AC-P6 --------
def ac_p6(page):
    r = page.evaluate("(function(){var r=window.WH_CONFIG.renderer;"
                      "return {div:r.internalResDiv, isInt:"
                      "Number.isInteger(r.internalResDiv), "
                      "mpr:('maxPixelRatio' in r)?r.maxPixelRatio:null};})()")
    lines = open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")
                 ).read().splitlines()
    quote = None
    for i, ln in enumerate(lines):
        if "maxPixelRatio" in ln:
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(lines) and re.search(r"supersed", lines[j],
                                                       re.I):
                    quote = lines[j].strip()
            break
    ok = r["isInt"] and r["div"] == DISPATCH_DIV and r["mpr"] is not None
    check("P6", "CONFIG record", ok,
          "internalResDiv=%s int=%s maxPixelRatio=%s comment(RECORD)=%r"
          % (r["div"], r["isInt"], r["mpr"], quote))
    return r["div"]


# ------------------------------------------------ floor subprocess runner --
def run_floor_harness(rel, extra_env, timeout):
    """Run an UNCHANGED prior-round harness on our shared server; parse
    the final JSON (balanced-join from the last '{'-leading line, works
    for R1's pretty-printed and R2's one-line verdicts)."""
    env = dict(os.environ)
    env.pop("WH_SMOKE", None)            # floors run their full protocol
    env["WH_BASE_ROOT"] = BASE_ROOT
    env.update(extra_env)
    proc = subprocess.run([sys.executable, rel], cwd=REPO_ROOT,
                          capture_output=True, text=True, timeout=timeout,
                          env=env)
    lines = (proc.stdout or "").splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("{"):
            try:
                j = json.loads("\n".join(lines[i:]))
                by = {a.get("id"): a for a in j.get("per_ac", [])}
                fails = sorted({a.get("id") for a in j.get("per_ac", [])
                                if a.get("verdict") in
                                ("FAIL", "FAIL-RETUNE-PENDING")})
                return j, by, fails
            except Exception:
                continue
    return None, {}, []


L10_SCALED_JS = """(function(){
  var rid=window.WH_CONFIG.regionA.id;
  var l=window.WH_DEBUG.getRegionManager().getEnemies(rid), g=null;
  for(var i=0;i<l.length;i++){ if(l[i].type==='ghoul'){g=l[i];break;} }
  if(!g || g.x!==g.x || g.z!==g.z) return null;      // law 4 NaN guard
  var v=new THREE.Vector3(g.x,(g.ty||0)+0.9*window.WH_CONFIG.world.characterHeight,g.z);
  var G=window.WH_GAME; v.project(G.camera);
  G.renderer.render(G.scene,G.camera);
  return {sx:(v.x*0.5+0.5)*window.innerWidth, sy:(-v.y*0.5+0.5)*window.innerHeight,
          vz:v.z, url:G.renderer.domElement.toDataURL('image/png')};})()"""


def _ring_mean(img, cx, cy, r0, r1, excl):
    px = img.load()
    w, h = img.size
    s = n = 0
    for y in range(max(0, cy - r1), min(h, cy + r1 + 1)):
        for x in range(max(0, cx - r1), min(w, cx + r1 + 1)):
            dx, dy = x - cx, y - cy
            if r0 is None:
                if abs(dx) > excl or abs(dy) > excl:
                    continue
            else:
                rr = dx * dx + dy * dy
                if rr < r0 * r0 or rr > r1 * r1 or (abs(dx) <= excl
                                                    and abs(dy) <= excl):
                    continue
            p = px[x, y]
            s += 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
            n += 1
    return s / max(1, n)


def l10_scaled(page, d=10):
    """RECORD-only judgment evidence (valspec AC-P4): R2 L10 geometry at
    d=10, box +-5 / annulus r60-90 in BUFFER px (= R2's footprint / 2)."""
    gp = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies("
                       "window.WH_CONFIG.regionA.id);for(var i=0;i<l.length;"
                       "i++){if(l[i].type==='ghoul'&&l[i].x===l[i].x)"
                       "return {x:l[i].x,z:l[i].z};}return null;})()")
    if not gp:
        return {"err": "no ghoul"}
    page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)"
                  % (gp["x"] - d * 0.3, gp["z"] + d * 0.95))
    page.wait_for_timeout(4000)
    s = None
    for _ in range(4):
        wait_frames(page, 3)
        s = page.evaluate(L10_SCALED_JS)
        if s and s["vz"] < 1:            # law 3: settle (vz>1 = behind)
            break
    if not s or s["vz"] >= 1:
        return {"err": "camera never settled", "vz": s and s["vz"]}
    img = decode_image(s["url"])
    w, h = img.size
    cx, cy = int(s["sx"] * w / VIEW_W), int(s["sy"] * h / VIEW_H)
    t = _ring_mean(img, cx, cy, None, 5, 5)
    b = _ring_mean(img, cx, cy, 60, 90, 7)
    return {"d": d, "t": round(t, 1), "b": round(b, 1),
            "c": round(abs(t - b) / max(b, 1.0), 3), "buf": "%dx%d" % (w, h)}


def ac_p4(page):
    """R2 floor (A5: WH_R2_FLOOR=0, WH_R2_PORT = our port for R2's
    identity probe). Waivers: L10-alone drift (pre-declared R3 artifact,
    scaled re-measure RECORD) + A6 SCOPE residual wholly in P5 surface."""
    j, by, fails = run_floor_harness(
        "tests/wh_world_r2_validation.py",
        {"WH_R2_FLOOR": "0", "WH_R2_PORT": str(PORT)}, 3600)
    rec = {"verdict": j and j.get("verdict"), "fails": fails, "waivers": [],
           "per_ac": ["%s:%s" % (k, v.get("verdict")) for k, v in by.items()]}
    EXTRA["floor"]["r2"] = rec
    if j is None:
        check("P4", "R2 floor", False, "no parseable R2 verdict")
        return rec
    if j.get("verdict") == "PASS":
        check("P4", "R2 floor", True, "r2=PASS %s" % rec["per_ac"])
        return rec
    ok_all = bool(fails)
    for f in fails:
        ev = by[f].get("evidence", "")
        if f == "L10":
            rec["l10_rows"] = ev
            rec["l10_scaled"] = l10_scaled(page)
            rec["waivers"].append("L10-R3-artifact (buffer-px annulus 2x "
                                  "on screen at div 2; pre-declared)")
        elif f == "SCOPE":
            viol = re.findall(r"'([^']+)'", ev.split("secrets=")[0])
            clean = ("secrets=[]" in ev and "pageErr=0" in ev
                     and "consoleErr=0" in ev)
            if clean and all(in_surface(p) for p in viol):
                rec["waivers"].append("A6-SCOPE residual in P5 surface %s"
                                      % viol)
            else:
                ok_all = False
        else:
            ok_all = False
    if ok_all:
        check("P4", "R2 floor", True,
              "FLOOR-WAIVER r2=%s fails=%s waivers=%s l10_scaled=%s "
              "(carrier-req: Testerbot revalidates harness on lane recovery)"
              % (j.get("verdict"), fails, rec["waivers"],
                 rec.get("l10_scaled")), verdict="WAIVED")
    else:
        check("P4", "R2 floor", False,
              "r2=%s fails=%s waived=%s (non-artifact -> STOP)"
              % (j.get("verdict"), fails, rec["waivers"]), verdict="BLOCK")
    return rec


# ------------------------------------------------------------ AC-P3 --------
def r2_a3_subprobe():
    """A3 settle subprobe source, read verbatim from the R2 harness at run
    time (READ-only; one source of truth for the inherited waiver class)."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"A3_SUBPROBE = r'''(.*?)'''", src, re.S)
    return m.group(1) if m else None


def ac_p3(r2rec):
    """R1 floor re-proof: tests/wh_world_r1_validation.py UNCHANGED as a
    subprocess on the shared server. Inherited waiver classes re-verified
    in-run as R2 part10 ac_floor; A4 amendment (style.css FREEZE waiver)."""
    j, by, fails = run_floor_harness("tests/wh_world_r1_validation.py",
                                     {"WH_R1_PORT": str(PORT)}, 1800)
    rec = {"verdict": j and j.get("verdict"), "fails": fails, "waivers": [],
           "per_ac": ["%s:%s" % (k, v.get("verdict")) for k, v in by.items()]}
    EXTRA["floor"]["r1"] = rec
    if j is None:
        check("P3", "R1 floor", False, "no parseable R1 verdict")
        return
    if j.get("verdict") == "PASS":
        check("P3", "R1 floor", True, "r1=PASS %s" % rec["per_ac"])
        return
    ev = {k: (v.get("evidence") or "") for k, v in by.items()}
    p5_ok = any(r["id"] == "P5" and r["verdict"] == "PASS" for r in RESULTS)
    idx_ok = (sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
              == INDEX_FREEZE_SHA256)
    w = rec["waivers"]

    def a2():
        e = ev.get("A2", "")
        if "idleBad" in e and "minY=-0" in e.replace(" ", ""):
            w.append("A2-dev-baseline")
            return True
        return False

    def a3():
        sub = r2_a3_subprobe()
        if not sub:
            return False
        sp = subprocess.run([sys.executable, "-c", sub, BASE_ROOT],
                            capture_output=True, text=True, timeout=240)
        for ln in reversed((sp.stdout or "").splitlines()):
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                row = json.loads(ln)
                if row.get("converged"):
                    w.append("A3-settle tail=%s" % row.get("tail"))
                    return True
                break
        return False

    def a4():
        # night-rig chain re-verified from THIS run's R2 floor: L4 PASS and
        # L10 PASS or L10 waived with scaled c10 >= 0.25 (R3 deviation:
        # L4/L10 are not in-suite in R3; they ride the P4 subprocess)
        pa = dict(x.split(":", 1) for x in r2rec.get("per_ac", []))
        sc = (r2rec.get("l10_scaled") or {}).get("c")
        l10 = pa.get("L10") == "PASS" or (isinstance(sc, float) and sc >= 0.25)
        if pa.get("L4") == "PASS" and l10:
            w.append("A4-nightrig (r2 L4 PASS, L10 %s)" % pa.get("L10"))
            return True
        return False

    def a6():
        if "DRIFT" in ev.get("A6", ""):
            w.append("A6-hash-drift")
            return True
        return False

    def a7():
        s_ok, _ = style_hunk_exact()
        if idx_ok and s_ok:
            w.append("A7-R3-style.css-freeze (A4 amendment: index freeze-ok, "
                     "exact P5 hunk)")
            return True
        return False

    def a8():
        paths = re.findall(r"'([^']+)'", ev.get("A8", ""))
        inherit = ("io/specs/", "io/reports/", "tests/wh_world_r2_validation",
                   "tests/r2parts")
        if p5_ok and paths and all(in_surface(p) or any(
                p.startswith(x) for x in inherit) for p in paths):
            w.append("A8-surface (residual in P5/R2 surfaces, secrets "
                     "re-verified by P5)")
            return True
        return False

    covered = {"A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "A8": a8}
    unexplained = [f for f in fails if f not in covered]
    if not unexplained and all(covered[f]() for f in fails):
        check("P3", "R1 floor", True,
              "FLOOR-WAIVER r1=%s fails=%s classes=%s (carrier-req: "
              "Testerbot revalidates harness on lane recovery)"
              % (j.get("verdict"), fails, " | ".join(w)), verdict="WAIVED")
    else:
        check("P3", "R1 floor", False,
              "r1=%s fails=%s unexplained=%s waived=%s (non-artifact -> STOP;"
              " manual adjudication per spec :77)"
              % (j.get("verdict"), fails, unexplained, " | ".join(w)),
              verdict="BLOCK")


# ---------------------------------------------------- flake rule + main ----
def run_ac(ac, fn, page, *args):
    """Flake rule: infra-shaped failures (exception / timeout / degenerate
    frame / page not ready) retry up to 2x after a fresh reload; number
    misses return normally and are NEVER retried. Last attempt wins."""
    for attempt in range(3):
        mark = len(RESULTS)
        try:
            return fn(*args)
        except Exception as e:
            del RESULTS[mark:]
            if attempt == 2:
                check(ac, "runner-exception", False, "%r (after %d retries)"
                      % (e, attempt))
                return None
            FLAKES.append("%s#%d %r" % (ac, attempt, e)[:200])
            print("[flake] %s attempt %d: %r" % (ac, attempt, e))
            try:
                page.reload(wait_until="load", timeout=60000)
                load_index(page)
            except Exception:
                pass


def final_verdict():
    by = {r["id"]: r["verdict"] for r in RESULTS}
    if len(FLAKES) >= 3 or "BLOCK" in by.values() or by.get("BOOT") != "PASS":
        return "BLOCK"
    floors_ok = all(by.get(k) in ("PASS", "WAIVED") for k in ("P3", "P4"))
    core = [by.get(k) for k in ("P1", "P2", "P5", "P6")]
    if all(v == "PASS" for v in core) and floors_ok:
        return "PASS"
    hard = [v for v in core if v not in ("PASS", "FAIL-RETUNE-PENDING")]
    if not hard and "FAIL-RETUNE-PENDING" in core:
        return "FAIL-RETUNE-PENDING"
    if all(v == "PASS" for v in core) and not FLOOR:
        return "PASS-FLOOR-SKIPPED"
    return "FAIL"


def main():
    errs = {"console": [], "page": [], "resp": []}
    server, how = None, ""
    div = DISPATCH_DIV
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            server, how = start_server()
            ctx, page = new_page(browser, errs)
            ok = bool(BASE_ROOT) and load_index(page)
            check("BOOT", "identity+ready", ok, "%s base=%s" % (how, BASE_ROOT))
            if ok:
                div = run_ac("P6", ac_p6, page, page) or DISPATCH_DIV
                run_ac("P1", ac_p1, page, browser, page, errs, div)
                run_ac("P2", ac_p2, page, browser, page, div)
                run_ac("P5", ac_p5, page, browser)
                if FLOOR:
                    r2rec = run_ac("P4", ac_p4, page, page) or {}
                    run_ac("P3", ac_p3, page, r2rec)
                else:
                    for k in ("P3", "P4"):
                        check(k, "floor subprocess", True,
                              "skipped by WH_W3_FLOOR=0", verdict="SKIP-NOTED")
            else:
                for k in ("P1", "P2", "P3", "P4", "P5", "P6"):
                    check(k, "page-never-ready", False, "page never ready")
            ctx.close()
            browser.close()
    except Exception as e:
        check("RUN", "harness-exception", False, repr(e)[:300])
    finally:
        stop_server(server)
    verdict = final_verdict()
    out = {"round": "world-r3", "verdict": verdict, "div": div,
           "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                       "evidence": r["detail"]} for r in RESULTS],
           "floor": EXTRA["floor"], "p2_table": EXTRA["p2_table"],
           "flakes": len(FLAKES),
           "notes": "smoke=%s floor=%s divs=%s server=%s flakeLog=%s "
                    "(carrier-req: Testerbot revalidates harness on lane "
                    "recovery)" % (SMOKE, FLOOR, DIVS, how, FLAKES)}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # law 6: exit 0 ALWAYS, last line = JSON
        print(json.dumps({"round": "world-r3", "verdict": "BLOCK",
                          "notes": "fatal %r" % e}))
    sys.exit(0)
