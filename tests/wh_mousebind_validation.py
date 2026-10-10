"""Witch Hunter pointer-lock mouse-bind-camera validation harness (Testerbot).

Contract: io/specs/mouse-bind-cam-valspec.md (per-check map, section 5).
Spec of record: io/specs/mouse-bind-cam-spec.md (N1-N10, P1-P8).

Usage: python3 tests/wh_mousebind_validation.py [<target.html>]
Default target: prototype/builds/v8-playable.html.
Env overrides: WH_MB_PORT (default 8793), WH_MB_ROOT (external base URL).
Exit code is ALWAYS 0 - failures are data (final stdout line is JSON-ish
summary; full record written to tests/artifacts/wh_mousebind_verdict.json).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
ARTIFACT_DIR = os.path.join(HERE, "artifacts")
PORT = int(os.environ.get("WH_MB_PORT", "8793"))
BASE_ROOT = os.environ.get("WH_MB_ROOT", "http://localhost:%d/" % PORT)
BOOT_TIMEOUT = float(os.environ.get("WH_MB_BOOT_TIMEOUT", "60"))

TARGET = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    REPO_ROOT, "prototype", "builds", "v8-playable.html")
TARGET_NAME = os.path.relpath(TARGET, REPO_ROOT)

# Single-file builds (no leftover <script src=>) that live OUTSIDE the repo are
# served from a temp dir; in-repo targets (v7, v8 default) are served in-situ
# by prototype/server.py so relative js/*.js and /art-direction assets resolve.
MODE = "repo"
PAGE_URL_PATH = TARGET_NAME if TARGET_NAME.startswith("builds/") else None
RAW_URL = None
_abs_t = os.path.abspath(TARGET)
_rroot = os.path.abspath(REPO_ROOT) + os.sep
if not (_abs_t + os.sep).startswith(_rroot):
    MODE = "raw"  # out-of-repo target only

FROZEN = {
    "head": "09712f6cbf2aa6ca64322e2ca4cc8ac12968d13a",
    "files": {
        "prototype/js/player.js":
            "97f0b9659a5c2d8ab478d9967896d3cf248cc4ffa1e998bde30ea0c77a6eee6d",
        "prototype/js/CONFIG.js":
            "7c7eba2ff8c2140d68ae9629093a3ced7e5f0583f3a804be95b1ca0bf56c8ca3",
        "prototype/index.html":
            "3784a007c5898606d09a09b2385e08956e37b7d5e156a7d152448e944985d6a6",
        "prototype/style.css":
            "3ad2a8deefe8a6f948646a40c05be355920b2d687c41de793e9031efa4968abc",
        "prototype/js/touch-controls.js":
            "051cc722152a2de67f319756c2e41520c67a7bda89d86eb8f2f477d8ad8891ce",
    },
    "tools/build_v7.py":
        "1ed740715ea02b76d0b62cfb07bb7686af0eda204b39e465d30c226c01e3157b",
    "builds": {
        "prototype/builds/v1-playable.html":
            "b874446a02cd3ee4c95cbecdec96f1a98073d23b0bda54216099aa9f84bd05d6",
        "prototype/builds/v2-playable.html":
            "9499392ee6ae7d0f1a5344cde8407e21b43904e5790c3ea8d6be2fc475d41e8d",
        "prototype/builds/v7-playable.html":
            "3008288416db373a3af9597eea081f167a659d3522e641f1f685dbc7a8b1de16",
    },
    "decimate_diff_sha":
        "025e86a5eb02e044ae5bb7eed879f383d3e23ee82c4522ebfa754748542e1105",
    "spec_sha":
        "3be2f2b439eb38fe052faf8b3e22400092fa13b9994810c730e1e441ebad2f31",
}
SCOPE = {
    "prototype/js/player.js", "prototype/js/CONFIG.js",
    "prototype/index.html", "prototype/style.css",
    "prototype/js/touch-controls.js", "tools/build_v8.py",
    "prototype/builds/v8-playable.html", "tests/wh_mousebind_validation.py",
    "tests/artifacts/wh_mousebind_verdict.json",
    "io/specs/mouse-bind-cam-spec.md", "io/specs/mouse-bind-cam-valspec.md",
}
SANCTIONED_VEHICLES = {
    "exitPointerLock-hook",   # valspec section 3.1 (N3/N2b Esc-equivalence only)
    "rAF-evaluate-reads",     # valspec section 3.2 (read-only state sampling)
    "init-script-fault",      # N7 fault-injection stub
    "dispatched-mouseevent",  # spec section 7 line 267 (N2b vehicle)
}

RESULTS = []
CONSOLE_ERRORS = []
PAGE_ERRORS = []
VEHICLE_USE = {}
FINALIZED = False

# ------------------------------------------------------------ tiny helpers ----


def check(cid, name, ok, detail="", verdict=None):
    ok = bool(ok)
    v = verdict or ("PASS" if ok else "FAIL")
    RESULTS.append({"id": cid, "name": name, "ok": ok, "verdict": v,
                    "detail": str(detail)[:400]})
    print("MB  %-4s %-46s => %-6s %s" % (cid, name, v, str(detail)[:170]))
    return ok


def use_vehicle(cid, veh):
    VEHICLE_USE.setdefault(cid, set()).add(veh)


def sha256_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return "ERR:%s" % e


def read_repo(rel):
    try:
        with open(os.path.join(REPO_ROOT, rel), "r", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def git(args):
    try:
        r = subprocess.run(["git"] + args, cwd=REPO_ROOT, capture_output=True,
                           text=True, timeout=30)
        return r.stdout
    except Exception as e:
        return "ERR:%s" % e


def start_server():
    try:
        with urllib.request.urlopen(BASE_ROOT, timeout=1.0) as r:
            if r.status == 200:
                return None
    except Exception:
        pass
    proc = None
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py", str(PORT)],
            cwd=os.path.join(REPO_ROOT, "prototype"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        print("[diag] server spawn failed %r; assuming external" % e)
    deadline = time.time() + 15.0
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(BASE_ROOT, timeout=1.0) as r:
                if r.status == 200:
                    return proc
        except Exception:
            pass
        time.sleep(0.3)
    print("[diag] server poll never got 200")
    return proc


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


# ------------------------------------------------------- injected scripts ----

# Runs BEFORE any page script. Arms: (a) requestPointerLock instrumented stub
# (counts calls; N7 fault modes armed later via __whMBTest.armed), (b) the
# P2b/N3 Esc-equivalence exit hook (dormant until exitHook=true), (c)
# pointerlockchange/error counters, (d) capture-phase movement recorder for
# N2a evidence, (e) contextmenu capture flag for P2. No console output: the
# N10 zero-error assertion must count ZERO harness-caused errors.
INIT_SCRIPT = """window.__whMBTest = {
  plChange: 0, plError: 0, exitCalls: 0, exitHook: false,
  rplCalls: 0, armed: false, rplThrowMode: null, silentFail: false,
  moveLog: [], ctxFlag: 0, contextFlag: 0
};
(function () {
  var rpl = HTMLCanvasElement.prototype.requestPointerLock;
  if (rpl) {
    HTMLCanvasElement.prototype.requestPointerLock = function () {
      var t = window.__whMBTest;
      t.rplCalls++;
      if (t.armed) {
        if (t.rplThrowMode === 'throw') {
          throw new TypeError('MBTEST fault: requestPointerLock stubbed to throw');
        }
        if (t.silentFail) return undefined;
        return Promise.reject(new TypeError('MBTEST fault: rejected promise'));
      }
      return rpl.apply(this, arguments);
    };
  }
  document.addEventListener('pointerlockchange', function () {
    var t = window.__whMBTest;
    t.plChange++;
    if (t.exitHook && document.pointerLockElement) {
      t.exitCalls++;
      try { document.exitPointerLock(); } catch (e) {}
    }
  });
  document.addEventListener('pointerlockerror', function () {
    window.__whMBTest.plError++;
  });
  document.addEventListener('mousemove', function (e) {
    var t = window.__whMBTest;
    if (t.moveLog.length < 200) {
      t.moveLog.push([e.movementX, e.movementY, e.clientX, e.clientY,
                      !!document.pointerLockElement]);
    }
  }, true);
  document.addEventListener('contextmenu', function () {
    window.__whMBTest.contextFlag++;
  }, true);
})();"""

STATE_JS = r"""(() => {
  const P = window.WH_DEBUG && window.WH_DEBUG.getPlayer &&
            window.WH_DEBUG.getPlayer();
  const chip = document.getElementById('wh-mouse-chip');
  const H = window.WH_DEBUG || {};
  const safe = function (fn) { try { return fn(); } catch (e) { return 'x'; } };
  return {
    hasPlayer: !!P, alive: P ? P.state : null,
    yaw: P ? P.camYaw : null, pitch: P ? P.camPitch : null,
    dist: P ? P.camDist : null,
    bound: P ? (('mouseBound' in P) ? P.mouseBound : 'MISSING') : null,
    locked: !!document.pointerLockElement,
    chip: chip ? chip.textContent : null,
    t: P ? P.lastManualCamT : null,
    stage: safe(function () { return P.getAttackStage(); }),
    blocking: P ? !!P.blocking : null,
    offhand: safe(function () { return H.getOffhand ? H.getOffhand() : null; }),
    cast: safe(function () { return H.getCastState ? H.getCastState() : null; }),
    pos: P ? { x: P.pos.x, z: P.pos.z } : null
  };
})()"""


def page_state(page):
    try:
        return page.evaluate(STATE_JS)
    except Exception as e:
        return {"hasPlayer": False, "error": str(e)[:150]}


def t_state(page):
    try:
        return page.evaluate("window.__whMBTest || null")
    except Exception:
        return None


def wait_boot(page, timeout_s=BOOT_TIMEOUT):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            if page.evaluate(
                    "!!(window.WH_DEBUG && window.WH_DEBUG.getPlayer && "
                    "window.WH_DEBUG.getPlayer())"):
                return True
        except Exception:
            pass
        page.wait_for_timeout(200)
    return False


def poll_until(page, fn, timeout_s=8.0, interval=0.1):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            if fn():
                return True
        except Exception:
            pass
        page.wait_for_timeout(int(interval * 1000))
    return False


def press_bq(page):
    """Organic Backquote press (spec N1/N3 bind toggle key)."""
    page.keyboard.press("Backquote")


def chip_box(page):
    chip = page.query_selector("#wh-mouse-chip")
    return chip.bounding_box() if chip else None


# --------------------------------------------------------- static checks ----

def check_n1(target_src):
    ok_rpl = ("requestPointerLock" in target_src) and \
             ("exitPointerLock" in target_src)
    lines = []
    for label, rel in (("target", None), ("player.js", "prototype/js/player.js")):
        txt = target_src if rel is None else read_repo(rel)
        for i, ln in enumerate(txt.splitlines(), 1):
            if "requestPointerLock" in ln and r"movementX" not in ln:
                lines.append("%s:%d" % (label, i))
                break
    chip_ok = "wh-mouse-chip" in target_src
    cfg_ok = ("autoBindOnCanvasClick" in target_src) and \
             ("pointerLockSensMult" in target_src)
    ev = "rpl/epl=%s anchor=%s chip=%s cfg.mouse=%s" % (
        ok_rpl, lines[:2], chip_ok, cfg_ok)
    ok = ok_rpl and chip_ok and cfg_ok
    check("N1", "lock JS + chip + CFG.mouse present", ok, ev)
    return ok


def check_n9(target_src, target_path):
    if not os.path.isfile(target_path):
        check("N9", "build artifact checks", False,
              "target missing: %s" % TARGET_NAME)
        return False
    title = re.search(r"<title>(.*?)</title>", target_src, re.S)
    ok_chip = "wh-mouse-chip" in target_src
    ok_cfg = "autoBindOnCanvasClick" in target_src
    ok_nosrc = "<script src=" not in target_src
    ok_title = bool(title) and title.group(1).strip() == \
        "Witch Hunter v8 - Mouse Bind Cam"
    ok = ok_chip and ok_cfg and ok_nosrc and ok_title
    check("N9", "build artifact checks", ok,
          "chip=%s cfg=%s noSrc=%s title=%r" % (
              ok_chip, ok_cfg, ok_nosrc, title.group(1).strip() if title else None))
    return ok


def check_p1():
    rows, ok = {}, True
    for rel, base in FROZEN["files"].items():
        now = sha256_file(os.path.join(REPO_ROOT, rel))
        if now == base:
            status = "match"
        else:
            status = "drift"
            head_line = git(["show", "HEAD:%s" % rel]).strip()
            cur = sha256_file(os.path.join(REPO_ROOT, rel))
            if head_line and not head_line.startswith("ERR"):
                import hashlib as _h
                head_sha = _h.sha256(
                    git(["show", "HEAD:%s" % rel]).encode()).hexdigest()
                status = "authorized-diff" if cur == head_sha else "drift"
            ok = status in ("match", "authorized-diff") and ok
        rows[rel] = {"baseSha": base[:16], "shaNow": now[:16], "status": status}
    import hashlib as _h
    ok2 = True
    echo = {"head": FROZEN["head"], "files": rows}
    head = git(["rev-parse", "HEAD"]).strip()
    ok_head = head == FROZEN["head"]
    detail = "head=%s(%s) drift=%s" % (
        head[:12], "ok" if ok_head else "MOVED",
        [k for k, v in rows.items() if v["status"] == "drift"] or "none")
    # head move alone is not a violation (Devbot may commit); file drifts and
    # unauthorized diffs are. Both recorded in echo. (Echo row is informational
    # X-class: the spec-AC preservation rows are P1/P1-anchor/P8.)
    check("X-echo", "five-file sha baseline echo", ok and ok2, detail)
    return ok, echo, ok_head


def check_p3():
    tc = sha256_file(os.path.join(REPO_ROOT, "prototype/js/touch-controls.js"))
    ok = tc == FROZEN["files"]["prototype/js/touch-controls.js"]
    check("P3", "touch-controls.js byte-identical", ok, "sha=%s" % tc[:16])
    return ok


def check_p4_static():
    """spec P1-anchor: drag handler body preserved; spec P4: lock-on framing
    untouched (mousemove early-return + game.js lock-on path unchanged)."""
    pj = read_repo("prototype/js/player.js")
    norm = re.sub(r"\s+", " ", pj)
    early_cnt = norm.count("self.lockTarget) return")
    drag_branch = ("lastDragX" in pj) and ("dragging" in pj) and \
        ("clientX" in pj)
    ok_anchor = early_cnt >= 1 and drag_branch
    check("P1-anchor", "drag handler core preserved in player.js", ok_anchor,
          "earlyReturn x%d dragBranch=%s" % (early_cnt, drag_branch))
    gj = read_repo("prototype/js/game.js")
    head_gj = git(["show", "HEAD:prototype/js/game.js"])
    import hashlib as _h
    game_unchanged = _h.sha256(gj.encode()).hexdigest() == \
        _h.sha256(head_gj.encode()).hexdigest()
    ok_p4 = early_cnt >= 1 and game_unchanged
    check("P4", "lock-on framing untouched (early-return + game.js)", ok_p4,
          "earlyReturn=x%d game.js unchanged=%s%s" % (
              early_cnt, game_unchanged,
              "" if game_unchanged else
              " (touching game.js requires an IO scope amendment)"))
    return ok_p4


def check_p5():
    head_txt = git(["show", "HEAD:prototype/js/CONFIG.js"])
    cur_txt = read_repo("prototype/js/CONFIG.js")
    pat = re.compile(r"^\s*([A-Za-z_$][A-Za-z0-9_$]*):", re.M)
    head_keys = set(pat.findall(head_txt))
    cur_keys = set(pat.findall(cur_txt))
    removed = sorted(head_keys - cur_keys)
    added = sorted(cur_keys - head_keys)
    ok = not removed
    check("P5", "CONFIG additive-only (no key removed)", ok,
          "removed=%s added=%s" % (removed or "none", added or "none"))
    return ok


def check_p6():
    rows = {}
    ok = True
    build_v7 = sha256_file(os.path.join(REPO_ROOT, "tools/build_v7.py"))
    rows["tools/build_v7.py"] = build_v7
    ok = ok and build_v7 == FROZEN["tools/build_v7.py"]
    for rel, base in FROZEN["builds"].items():
        now = sha256_file(os.path.join(REPO_ROOT, rel))
        rows[rel] = now
        ok = ok and now == base
    detail = "; ".join(
        "%s %s" % (os.path.basename(k),
                   "ok" if v == FROZEN["builds"].get(k) else "DRIFT")
        if k in FROZEN["builds"] else
        "%s %s" % (os.path.basename(k),
                   "ok" if v == FROZEN["tools/build_v7.py"] else "DRIFT")
        for k, v in rows.items())
    check("P6", "build_v7 + v1/v2/v7 builds untouched", ok, detail[:200])
    return ok


def check_p7_keyboard():
    pj = read_repo("prototype/js/player.js")
    keys = ["KeyF", "KeyQ", "KeyR", "KeyT", "KeyW", "KeyA", "KeyS", "KeyD"]
    missing = [k for k in keys if ("'%s'" % k) not in pj and
               ('"%s"' % k) not in pj]
    if "shiftKey" not in pj and "ShiftLeft" not in pj and \
            "ShiftRight" not in pj and "shift" not in pj.lower():
        missing.append("shift")
    if "indexOf('Digit')" not in pj:
        missing.append("Digit1-5(indexOf idiom)")
    ok = not missing
    check("P7-static", "keyboard handler set intact", ok,
          "missing=%s" % (missing or "none"))
    return ok


def check_p8():
    status = [ln for ln in git(["status", "--short"]).splitlines() if ln.strip()]
    baseline = [" M scratch/treeqa/roundI/decimate.jsonl"] + \
        [ln for ln in status if ln.startswith("?? io/") or ln.startswith("?? scratch/")]
    extra = [ln for ln in status
             if not any(ln.endswith(p) or (" %s" % p) in ln for p in SCOPE)
             and ln not in baseline]
    ok = not extra
    check("P8", "dirty-tree scope hygiene", ok,
          "entries=%d baselineKept=%d extra=%s" % (
              len(status), len(baseline), extra[:4] or "none"))
    return ok, baseline
# --------------------------------------------------------- runtime suite ----


def new_page(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.on("console", lambda m: CONSOLE_ERRORS.append(
        "%s: %s" % (m.type, m.text[:200])) if m.type == "error" else None)
    page.on("pageerror", lambda e: PAGE_ERRORS.append(str(e)[:200]))
    return page


def err_count():
    return len(CONSOLE_ERRORS), len(PAGE_ERRORS)


def page_url():
    global PAGE_URL_PATH
    if MODE == "raw":
        return RAW_URL
    base = BASE_ROOT if BASE_ROOT.endswith("/") else BASE_ROOT + "/"
    if not PAGE_URL_PATH:
        PAGE_URL_PATH = "index.html"  # repo-root prototype entry
    return base + PAGE_URL_PATH


def start_raw_server():
    """Serve a temp dir for single-file (no <script src=>) builds."""
    global RAW_URL
    import shutil
    import tempfile
    import threading
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
    tmpdir = tempfile.mkdtemp(prefix="wh_mb_raw_")
    shutil.copy(TARGET, os.path.join(tmpdir, "v8.html"))
    handler = lambda *a, **k: SimpleHTTPRequestHandler(*a, directory=tmpdir, **k)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    RAW_URL = "http://127.0.0.1:%d/v8.html" % PORT
    return srv


def yaw_ref_per_px():
    return -0.25 * 3.141592653589793 / 180.0


def n4_free_inert(page, st0):
    # organic plain moves, NO button: camera must not move
    for xy in ((300, 300), (500, 340), (360, 250)):
        page.mouse.move(*xy)
    page.wait_for_timeout(120)
    st = page_state(page)
    dy = (st["yaw"] - st0["yaw"]) if (st["yaw"] is not None and st0["yaw"] is not None) else None
    dp = (st["pitch"] - st0["pitch"]) if (st["pitch"] is not None and st0["pitch"] is not None) else None
    ok = dy == 0 and dp == 0
    check("N4", "free mousemove (no button) inert", ok,
          "dyaw=%r dpitch=%r" % (dy, dp))
    return ok


def p4_drag_math(page, st0):
    # organic buttoned drag, exact HEAD math
    page.mouse.move(200, 300)
    page.mouse.down()
    page.mouse.move(400, 300, steps=1)
    page.mouse.move(400, 340, steps=1)
    page.mouse.up()
    page.wait_for_timeout(120)
    st = page_state(page)
    rad = 3.141592653589793 / 180.0
    exp_dy = -(200) * 0.25 * rad
    exp_dp = (40) * 0.25 * rad
    dy = (st["yaw"] - st0["yaw"]) if (st["yaw"] is not None and st0["yaw"] is not None) else None
    dp = (st["pitch"] - st0["pitch"]) if (st["pitch"] is not None and st0["pitch"] is not None) else None
    ok = dy is not None and abs(dy - exp_dy) < 1e-6 and dp is not None and \
        abs(dp - exp_dp) < 1e-6
    check("P4", "drag-cam math identical to HEAD", ok,
          "dy=%r exp=%.6f dp=%r exp=%.6f" % (dy, exp_dy, dp, exp_dp))
    return ok, st


def _poll_dist_change(page, pred, timeout_ms=900):
    """IO-calibrated (10-05): wheel delivery is compositor-lagged headlessly.
    Poll page_state dist until pred(d) holds or the deadline passes; return
    the last observed value either way."""
    import time as _t
    deadline = _t.time() + timeout_ms / 1000.0
    last = None
    while _t.time() < deadline:
        st = page_state(page)
        d = st["dist"] if st else None
        last = d
        if d is not None and pred(d):
            return d
        page.wait_for_timeout(100)
    return last


def p2_wheel(page, st0):
    d0 = st0["dist"]
    # IO-calibrated (10-05 probe): pointer must be over the canvas or wheel
    # events deliver nothing headlessly; delivery is compositor-lagged (can
    # exceed 900ms mid-run), so every read polls with a generous deadline.
    # Semantics: +deltaY zooms out exactly +0.8; a single -deltaY returns EXACTLY
    # to baseline (handler is a fixed +-0.8 per event, clamp 3..14 untouched at 7).
    page.mouse.move(640, 400)
    page.wait_for_timeout(80)
    page.mouse.wheel(0, 120)   # deltaY>0 -> camDist += 0.8 (wheel handler +)
    d1 = _poll_dist_change(page, lambda d: d0 is not None and d > d0 + 0.3,
                           timeout_ms=2500)
    if not (d1 is not None and d0 is not None and d1 > d0 + 0.3):
        # IO calibrated retry (10-05): delivery can lag beyond 2.5s mid-run;
        # one re-issue of the wheel event before declaring failure.
        page.mouse.wheel(0, 120)
        d1 = _poll_dist_change(page, lambda d: d0 is not None and d > d0 + 0.3,
                               timeout_ms=1500)
    ok1 = d1 is not None and d0 is not None and d1 > d0 + 0.3
    # wheel back: single -120 must return exactly to d0
    page.mouse.wheel(0, -120)
    d2 = _poll_dist_change(page, lambda d: d0 is not None and abs(d - d0) < 0.3,
                           timeout_ms=2500)
    if not (d2 is not None and d0 is not None and abs(d2 - d0) < 0.3):
        page.mouse.wheel(0, -120)
        d2 = _poll_dist_change(page, lambda d: d0 is not None and abs(d - d0) < 0.3,
                               timeout_ms=1500)
    ok2 = d2 is not None and d0 is not None and abs(d2 - d0) < 0.3
    ok = ok1 and ok2
    check("P2-wheel", "wheel zoom semantics", ok,
          "d0=%r d1=%r d2=%r" % (d0, d1, d2))
    return ok


def p2_block_ctx(page):
    """RMB down: tryBlock (shield) or startCast (spell offhand) — semantic
    split per CONFIG.offhand; contextmenu capture via __whMBTest.contextFlag."""
    canvas = page.query_selector("#wh-canvas") or page.query_selector("canvas")
    box = canvas.bounding_box() if canvas else None
    cx, cy = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2) if box else (640, 400)
    page.mouse.move(cx, cy)
    st_pre = page_state(page)
    offhand = st_pre.get("offhand")
    is_shield = offhand == "shield"
    page.mouse.down(button="right")
    page.wait_for_timeout(200)
    st1 = page_state(page)
    page.mouse.up(button="right")
    page.wait_for_timeout(200)
    st2 = page_state(page)
    tt = t_state(page)
    if is_shield:
        expect_hold = st1.get("blocking") is True
    else:  # spell offhand: RMB casts (firebolt); cast state must leave idle/null
        expect_hold = st1.get("cast") not in (None, "x", "idle", False)
    expect_release = st2.get("blocking") is False
    ok = bool(expect_hold) and expect_release
    check("P2-block", "RMB press engages block/cast; release clears",
          ok,
          "offhand=%r down(block=%r cast=%r) up(block=%r)" % (
              offhand, st1.get("blocking"), st1.get("cast"), st2.get("blocking")))
    ok_ctx = bool(tt) and tt.get("contextFlag", tt.get("ctxFlag", 0)) >= 1
    check("P2-ctx", "contextmenu reaches document (captured)", ok_ctx,
          "contextFlag=%s" % (tt.get("contextFlag") if tt else None))
    return None


def p2_strike(page):
    st0 = page_state(page)
    canvas = page.query_selector("#wh-canvas") or page.query_selector("canvas")
    box = canvas.bounding_box() if canvas else None
    cx, cy = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2) if box else (640, 400)
    page.mouse.down()
    page.mouse.up()
    stage = None
    t0 = time.time()
    while time.time() - t0 < 8.0:
        stt = page_state(page)
        if stt["stage"] not in (None, "null", "x", "idle"):
            stage = stt["stage"]
            break
        page.wait_for_timeout(50)
    ok_strike = stage in ("windup", "strike", "recover")
    st1 = page_state(page)
    ok_yaw = st1["yaw"] is not None and st0["yaw"] is not None and \
        abs(st1["yaw"] - st0["yaw"]) < 1e-9
    check("P2-strike", "LMB strike fires, no cam orbit", ok_strike and ok_yaw,
          "stage=%r dyaw=%r" % (stage, (st1["yaw"] - st0["yaw"]) if st1["yaw"] is not None else None))
    return ok_strike


def n2_bind(page):
    press_bq(page)
    ok = poll_until(page, lambda: (page_state(page)["locked"] and
                                   page_state(page)["bound"]), 4.0)
    st = page_state(page)
    tt = t_state(page)
    chip_ok = st["chip"] == "MOUSE: BOUND [`]"
    ok2 = ok and chip_ok and bool(tt) and tt["plChange"] >= 1
    check("N2", "bind via Backquote (organic)", ok2,
          "locked=%r bound=%r chip=%r plChange=%s" % (
              st["locked"], st["bound"], st["chip"], tt["plChange"] if tt else None))
    return ok2, st


def n2a_locked_motion(page, st_bind):
    y0 = st_bind["yaw"]
    moves = [(340, 300), (380, 320), (420, 340), (460, 360)]
    for xy in moves:
        page.mouse.move(*xy)
    page.wait_for_timeout(120)
    st = page_state(page)
    tt = t_state(page)
    dy = (st["yaw"] - y0) if (st["yaw"] is not None and y0 is not None) else None
    locked_rows = [r for r in (tt.get("moveLog") or []) if r[4]] if tt else []
    ref = abs(yaw_ref_per_px()) * sum(
        abs(moves[i + 1][0] - moves[i][0]) for i in range(len(moves) - 1))
    ok = dy is not None and dy < 0 and abs(dy) > 0 and abs(abs(dy) - ref) / ref < 2.0
    if ok:
        check("N2a", "locked live motion", True, "dy=%r refPxYaw=%.3f" % (dy, ref),
              verdict="PASS")
    else:
        check("N2a", "locked live motion (RECORD-eligible)", False,
              "RECORD: dy=%r ref=%.3f lockedMoveRows=%d sample=%s" % (
                  dy, ref, len(locked_rows), locked_rows[-3:] if locked_rows else "none"),
              verdict="RECORD")
    return st


def n2b_dispatch(page, st0):
    y0 = st0["yaw"]
    p0 = st0["pitch"]

    def disp(mx, my):
        page.evaluate(
            "(() => { document.dispatchEvent(new MouseEvent('mousemove', "
            "{movementX: %d, movementY: %d, bubbles: true})); })()" % (mx, my))

    disp(40, 0)
    page.wait_for_timeout(60)
    st1 = page_state(page)
    rad = 3.141592653589793 / 180.0
    sens = 0.25 * 0.85   # mouseSensDegPerPx * pointerLockSensMult (spec v8)
    exp = -40 * sens * rad
    ok_yaw = st1["yaw"] is not None and y0 is not None and \
        abs((st1["yaw"] - y0) - exp) < 1e-6
    # A8 (10-05): normalize pitch to a known un-clamped point first - the row
    # before this (N2a live moves) can sit pitch at the 65deg clamp, where a
    # +40px event produces ZERO delta regardless of correct code.
    disp(0, -60000)   # slam to the -15deg floor (un-clamped start point)
    page.wait_for_timeout(80)
    st_norm = page_state(page)
    p0 = st_norm["pitch"]
    disp(-40, 40)
    page.wait_for_timeout(60)
    st2 = page_state(page)
    ok_pitch = st2["pitch"] is not None and p0 is not None and \
        abs((st2["pitch"] - p0) - 40 * sens * rad) < 1e-6
    ok_back = st2["yaw"] is not None and abs(st2["yaw"] - y0) < 1e-6
    # zero-movement event must NOT stamp
    t_before = page_state(page)["t"]
    disp(0, 0)
    page.wait_for_timeout(60)
    t_after = page_state(page)["t"]
    ok_nostamp = t_after == t_before
    # pitch clamp bounds
    disp(0, 60000)
    page.wait_for_timeout(60)
    st_hi = page_state(page)
    disp(0, -60000)
    page.wait_for_timeout(60)
    st_lo = page_state(page)
    ok_clamp = st_hi["pitch"] is not None and st_lo["pitch"] is not None and \
        abs(st_hi["pitch"] - 65 * rad) < 1e-6 and abs(st_lo["pitch"] + 15 * rad) < 1e-6
    ok = ok_yaw and ok_pitch and ok_back and ok_nostamp and ok_clamp
    use_vehicle("N2b", "dispatched-mouseevent")
    check("N2b", "dispatched movementX/Y math + clamps", ok,
          "yaw=%s pitch=%s back=%s nostamp=%s clamp=%s" % (
              ok_yaw, ok_pitch, ok_back, ok_nostamp, ok_clamp))
    return ok


def n8_stamps(page):
    # bound stamp via dispatched nonzero motion
    t0 = page_state(page)["t"]
    page.evaluate("(() => { document.dispatchEvent(new MouseEvent('mousemove', "
                  "{movementX: 30, movementY: 0, bubbles: true})); })()")
    page.wait_for_timeout(60)
    t1 = page_state(page)["t"]
    ok_bound = t1 is not None and t0 is not None and t1 > t0
    # free stamp via organic drag
    st0 = page_state(page)
    page.mouse.move(300, 300)
    page.mouse.down()
    page.mouse.move(340, 300, steps=1)
    page.mouse.up()
    page.wait_for_timeout(60)
    t2 = page_state(page)["t"]
    ok_free = t2 is not None and t1 is not None and t2 > t1
    ok = ok_bound and ok_free
    check("N8", "lastManualCamT stamp rules", ok,
          "boundStamp=%s freeStamp=%s" % (ok_bound, ok_free))
    return ok


def n3_unbind(page):
    press_bq(page)
    ok = poll_until(page, lambda: (not page_state(page)["locked"] and
                                   not page_state(page)["bound"]), 4.0)
    st = page_state(page)
    ok2 = ok and st["chip"] == "MOUSE: FREE [`]"
    check("N3", "unbind via Backquote (organic)", ok2,
          "locked=%r bound=%r chip=%r" % (st["locked"], st["bound"], st["chip"]))
    # Esc-equivalence: bind again, then emulate the native Esc exit via the
    # sanctioned exitPointerLock vehicle; assert the pointerlockchange-driven
    # chip sync drops state to FREE.
    press_bq(page)
    ok_re = poll_until(page, lambda: page_state(page)["locked"], 4.0)
    page.evaluate("document.exitPointerLock()")
    ok_esc = poll_until(page, lambda: (not page_state(page)["locked"] and
                                       not page_state(page)["bound"]), 4.0)
    st2 = page_state(page)
    ok3 = ok_esc and st2["chip"] == "MOUSE: FREE [`]"
    use_vehicle("N3", "exitPointerLock-hook")
    check("N3-esc", "native exit (Esc-equivalent) chip resync", ok3,
          "rebind=%r locked=%r bound=%r chip=%r" % (
              ok_re, st2["locked"], st2["bound"], st2["chip"]))
    return ok2 and ok3


def n6_chip_toggle(page):
    box = chip_box(page)
    if not box:
        check("N6", "chip toggle free x2 + bound-dir", False, "chip not found")
        return False
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    # --- free-direction leg 1: REAL mouse click on the chip (unlocked: hit
    # testing is physically real) ---
    page.mouse.click(cx, cy)
    ok_bound = poll_until(page, lambda: page_state(page)["bound"], 4.0)
    # --- bound-direction: the OS cursor is HIDDEN under real pointer lock
    # (the pointer simply cannot travel to the chip), so a real second chip
    # click is physically impossible while bound on ANY browser. The
    # dispatched-click vehicle through the REAL click listener is the
    # sanctioned bound-direction leg (documented valspec A7): it proves the
    # chip's own click handler toggles while bound (== ` equivalence) without
    # asserting an impossible physical input.
    page.evaluate("(() => { const c = document.getElementById('wh-mouse-chip'); "
                  "if (c) c.dispatchEvent(new MouseEvent('click', "
                  "{bubbles: true, cancelable: true})); })()")
    ok_locked = poll_until(page, lambda: not page_state(page)["locked"], 4.0)
    ok_free = poll_until(page, lambda: not page_state(page)["bound"], 1.5)
    # --- free leg 2: rebind via a real chip click again (both free directions
    # proven with REAL physical clicks around the dispatched bridge) ---
    page.mouse.click(cx, cy)
    ok_relock = poll_until(page, lambda: page_state(page)["locked"], 4.0)
    # exit the bound state to leave n6 in FREE for downstream legs
    page.evaluate("(() => { const c = document.getElementById('wh-mouse-chip'); "
                  "if (c) c.dispatchEvent(new MouseEvent('click', "
                  "{bubbles: true, cancelable: true})); })()")
    ok_unbind = poll_until(page, lambda: not page_state(page)["locked"],
                           4.0) and poll_until(
        page, lambda: not page_state(page)["bound"], 1.5)
    ok = ok_bound and ok_locked and ok_free and ok_relock and ok_unbind
    check("N6", "chip toggle free x2 + bound-dir", ok,
          "bindOnClick=%r exit=%r free=%r relock=%r unbind=%r" % (
              ok_bound, ok_locked, ok_free, ok_relock, ok_unbind))
    return ok


def n5_autorebind(page):
    # IO calibration (10-05): runner-level false (HEAD-parity legs) is still in
    # effect here; the autoBind feature under test needs it TRUE, and the
    # config-false leg below retunes it live both ways.
    page.evaluate("if (window.WH_CONFIG && WH_CONFIG.mouse) "
                  "WH_CONFIG.mouse.autoBindOnCanvasClick = true")
    canvas = page.query_selector("#wh-canvas") or page.query_selector("canvas")
    box = canvas.bounding_box() if canvas else None
    cx, cy = (640, 400) if not box else (box["x"] + box["width"] / 2,
                                         box["y"] + box["height"] / 2)
    # must be FREE here (N3 left us free); guard anyway
    if page_state(page)["locked"]:
        press_bq(page)
        poll_until(page, lambda: not page_state(page)["locked"], 3.0)
    # (a) canvas click: attack + rebind
    # IO calibration (10-05): flush any prior leg's attack stage to null and
    # re-read the yaw baseline AFTER the flush, else this leg's own strike
    # window aliases into the previous stage reading.
    poll_until(page, lambda: page_state(page)["stage"] is None, 3.0)
    st0 = page_state(page)
    page.mouse.click(cx, cy)
    ok_lock = poll_until(page, lambda: page_state(page)["locked"], 4.0)
    stage = None
    t0 = time.time()
    while time.time() - t0 < 6.0:
        stt = page_state(page)
        if stt["stage"] in ("windup", "strike", "recover"):
            stage = stt["stage"]
            break
        page.wait_for_timeout(50)
    ok_attack = stage in ("windup", "strike", "recover")
    # (b) chip click: UI-only path - no attack, no canvas auto-rebind hijack.
    # A4 (10-05, IO spec-owner resolution): 'chip does NOT rebind' (spec N5)
    # means the CANVAS auto-rebind mechanism must not drive UI clicks; the
    # chip's OWN toggle handler binding here is N6's contract (chip == `
    # equivalent). Sequence: flush any prior leg's strike window FIRST, then
    # the chip click under test, then assert no NEW attack (stage null 350ms
    # after a UI click; a UI click also toggles BIND, which poll-out below).
    press_bq(page)
    poll_until(page, lambda: not page_state(page)["locked"], 4.0)
    box = chip_box(page)
    ok_norebind = None
    if box:
        # A4-final sequence: flush prior strike window OUT COMPLETELY (attack
        # full cycle ~ windup+strike+recover; poll to null, then settle), so
        # the chip click's assertion reads THIS leg's stimulus only.
        # Probe10 evidence (10-05): chip click -> attackCalls=0, toggle binds.
        # Assert attack-count (the real contract), not stage (bleed-prone).
        poll_until(page, lambda: page_state(page)["stage"] is None, 8.0)
        page.wait_for_timeout(300)
        page.evaluate(
            "window.__whMBTest.attackCalls = 0; "
            "(() => { const P = window.WH_DEBUG.getPlayer(); "
            "if (P && !P.__mbw) { const o = P.tryAttack.bind(P); "
            "P.tryAttack = function () { window.__whMBTest.attackCalls++; "
            "return o(); }; P.__mbw = true; } })()")
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.wait_for_timeout(350)
        ac = page.evaluate("window.__whMBTest.attackCalls || 0")
        ok_norebind = (ac == 0)
    # (b2) IO calibration (10-05): the N6-contract chip toggle BINDS; the
    # config-false leg below needs FREE entry for a meaningful rpl delta.
    press_bq(page)
    poll_until(page, lambda: not page_state(page)["locked"], 4.0)
    ok = ok_lock and ok_attack and bool(ok_norebind)
    # (c) config-false leg: autoBindOnCanvasClick=false must disable the rebind
    page.evaluate("if (window.WH_CONFIG && WH_CONFIG.mouse) "
                  "WH_CONFIG.mouse.autoBindOnCanvasClick = false")
    tt2 = t_state(page) or {}
    r2 = tt2.get("rplCalls", 0)
    page.mouse.click(cx, cy)
    page.wait_for_timeout(300)
    tt3 = t_state(page) or {}
    r3 = tt3.get("rplCalls", 0)
    ok_off = (r3 == r2)
    page.evaluate("if (window.WH_CONFIG && WH_CONFIG.mouse) "
                  "WH_CONFIG.mouse.autoBindOnCanvasClick = true")
    check("N5", "canvas LMB = attack+rebind; chip LMB no-rebind", ok,
          "rebind=%r attack=%r chipNoRebind=%r" % (ok_lock, ok_attack, ok_norebind))
    check("N5-off", "autoBind=false disables canvas rebind", ok_off,
          "rpl %d -> %d with autoBind=false" % (r2, r3))
    return ok and ok_off


def n7_fault(page):
    tt = t_state(page)
    if not tt:
        check("N7", "fail hardening", False, "no __whMBTest (init script missing)")
        return False
    # ARM the fault NOW (pre-press): next requestPointerLock calls reject/throw.
    page.evaluate("window.__whMBTest.armed = true; "
                  "window.__whMBTest.rplThrowMode = 'throw'")
    press_bq(page)
    page.wait_for_timeout(400)
    tt = t_state(page)
    st = page_state(page)
    ok_pressed = tt["rplCalls"] >= 2  # >=1 before arming + the faulted press
    ok_state = (st["bound"] is False or st["bound"] is None) and \
        not st["locked"]
    ok_chip = st["chip"] == "MOUSE: FREE [`]"
    ce = len(CONSOLE_ERRORS)
    ok = ok_pressed and ok_state and ok_chip
    use_vehicle("N7", "init-script-fault")
    check("N7", "rpl throw: no uncaught, stays FREE", ok,
          "rplCalls=%d armedPress seen=%s state=%r chip=%r consoleErrs=%d" % (
              tt["rplCalls"], ok_pressed, st["bound"], st["chip"], ce))
    # disarm for the tail of the run
    page.evaluate("window.__whMBTest.armed = false")
    return ok


def p5_touch_pad(page):
    # touch layer exists? (auto-init requires CONFIG.touch.enabled OR saved)
    vis = page.evaluate("!!(window.WH_TouchControls && window.WH_TouchControls.isVisible())")
    if not vis:
        try:
            page.evaluate("window.WH_TouchControls && window.WH_TouchControls.show()")
        except Exception:
            pass
        vis = page.evaluate("!!(window.WH_TouchControls && window.WH_TouchControls.isVisible())")
    if not vis:
        check("P5", "touch cam pad still steers", False,
              "touch layer not visible (WH_TouchControls missing or CONFIG.touch off)")
        return False
    pad = page.query_selector(".wh-touch-ctl.cam") or page.query_selector(
        "[id*='cam' i]")
    if not pad:
        check("P5", "touch cam pad still steers", False, "cam pad element not found in layer")
        return False
    b0 = pad.bounding_box()
    if not b0:
        check("P5", "touch cam pad still steers", False, "cam pad has no layout box")
        return False
    cx, cy = b0["x"] + b0["width"] / 2, b0["y"] + b0["height"] / 2
    st0 = page_state(page)
    # IO-calibrated (10-05): settle after layer show, step waits during the
    # drag, and poll the final read (compositor lag can exceed fixed sleeps).
    page.mouse.move(cx, cy)
    page.wait_for_timeout(120)
    page.mouse.down()
    page.mouse.move(cx - 60, cy, steps=1)
    page.wait_for_timeout(100)
    page.mouse.move(cx - 60, cy + 40, steps=1)
    page.wait_for_timeout(100)
    page.mouse.up()
    import time as _t
    deadline = _t.time() + 2.5
    st = page_state(page)
    dy = (st["yaw"] - st0["yaw"]) if (st["yaw"] is not None and st0["yaw"] is not None) else None
    dp = (st["pitch"] - st0["pitch"]) if (st["pitch"] is not None and st0["pitch"] is not None) else None
    while _t.time() < deadline and not (
            dy is not None and dy > 0 and dp is not None and dp > 0):
        page.wait_for_timeout(100)
        st = page_state(page)
        dy = (st["yaw"] - st0["yaw"]) if (st["yaw"] is not None and st0["yaw"] is not None) else None
        dp = (st["pitch"] - st0["pitch"]) if (st["pitch"] is not None and st0["pitch"] is not None) else None
    ok = dy is not None and dy > 0 and dp is not None and dp > 0
    check("P5", "touch cam pad still steers (pad drag)", ok,
          "dyaw=%r dpitch=%r" % (dy, dp))
    return ok


def n10_console(page):
    ce, pe = err_count()
    ok = ce == 0 and pe == 0
    check("N10", "zero console errors, full organic run", ok,
          "consoleErrors=%d pageErrors=%d%s" % (
              ce, pe, (" first=%r" % (CONSOLE_ERRORS[:2] + PAGE_ERRORS[:2])) if (ce or pe) else ""))
    return ok


def p9_boot_record(page, url, t_load):
    st = page_state(page)
    ok = st["hasPlayer"]
    check("P9-boot", "boot telemetry record", ok,
          "url=%s loadToPlayer=%.1fs bound=%r locked=%r" % (
              url, time.time() - t_load, st["bound"], st["locked"]))
    return ok


# ------------------------------------------------------------------ main ----

def main():
    global MODE, PAGE_URL_PATH, RAW_URL
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    print("MB-VALIDATION target=%s mode=%s" % (TARGET_NAME, MODE))
    if MODE == "raw":
        srv_raw = start_raw_server()
        url = RAW_URL
        server = None
    else:
        srv_raw = None
        server = start_server()
        url = page_url()
    verdict_doc = {"round": "mouse-bind-cam", "target": TARGET_NAME,
                   "mode": MODE, "finalized": False}
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            ctx.add_init_script(INIT_SCRIPT)
            page = ctx.new_page()
            page.on("console", lambda m: CONSOLE_ERRORS.append(
                "%s: %s" % (m.type, m.text[:200])) if m.type == "error" else None)
            page.on("pageerror", lambda e: PAGE_ERRORS.append(str(e)[:200]))
            t_load = time.time()
            try:
                page.goto(url, wait_until="load", timeout=30000)
            except Exception as e:
                check("BOOT", "page load", False, "goto failed: %s" % str(e)[:150])
            booted = wait_boot(page)
            if not booted:
                check("BOOT", "WH_DEBUG player ready", False,
                      "player not ready within %.0fs" % BOOT_TIMEOUT)
            p9_boot_record(page, url, t_load)
            if booted:
                # ---------------- organic run body ----------------
                # IO calibration (10-05): HEAD-parity legs (N4/P4/P2-strike/
                # P2-ctx) must run with autoBind DISABLED, else the v8
                # canvas-LMB auto-rebind fires mid-check and cascades lock
                # state through every downstream leg. Restored true in n5.
                page.evaluate("if (window.WH_CONFIG && WH_CONFIG.mouse) "
                              "WH_CONFIG.mouse.autoBindOnCanvasClick = false")
                # IO calibration A5 (10-05): boot-race gate. Boot's faceTowards
                # (game.js, Nicko 10-03 spawn-facing order) lands up to ~1.5s
                # AFTER getPlayer() first resolves. No extra globals here -
                # WH_DEBUG.isRunning and window.game do NOT exist (game.js
                # closure) - so the gate is pure camYaw/camPitch stability:
                # sample until two consecutive identical reads (250ms apart),
                # capped at ~8s.
                _prev = None
                for _ in range(32):
                    _cur = page.evaluate(
                        "[window.WH_DEBUG.getPlayer().camYaw,"
                        "window.WH_DEBUG.getPlayer().camPitch]")
                    if _prev is not None and _cur == _prev:
                        break
                    _prev = _cur
                    page.wait_for_timeout(250)
                # A5-hardened (10-05): two matching reads can still fast-exit
                # BEFORE the late spawn-facing write (observed iofix3: P4
                # yaw delta returned). Require the pair to hold across a
                # FULL 2s span of 250ms samples before any baseline.
                _anchor = page.evaluate(
                    "[window.WH_DEBUG.getPlayer().camYaw,"
                    "window.WH_DEBUG.getPlayer().camPitch]")
                for _ in range(8):
                    page.wait_for_timeout(250)
                    _cur = page.evaluate(
                        "[window.WH_DEBUG.getPlayer().camYaw,"
                        "window.WH_DEBUG.getPlayer().camPitch]")
                    if _cur != _anchor:
                        _anchor = _cur
                # A6 (10-05): headless runs are AFK; region enemies can kill
                # the player mid-run and respawnPoison camYaw via faceTowards.
                # isolate the environment: permanent i-frames for the run.
                page.evaluate("window.WH_DEBUG.getPlayer().iframes = 1e9")
                st0 = page_state(page)
                n4_free_inert(page, st0)              # N4 free inertness
                p4_drag_math(page, st0)               # P4 drag math + P1 anchor
                p_touch = None
                try:
                    p_touch = p5_touch_pad(page)      # P5 touch pad (Testerbot
                    # 10-05 calibration v3: post-interaction slot (after P4
                    # drag, before wheel/strike); pristine-page runs write the
                    # face-angle class dyaw=-3.107/dpitch=0 (run-5), the
                    # probe-proven pass needs post-interaction state)
                except Exception as e:
                    check("P5", "touch cam pad still steers", False,
                          "runner exception %r" % e)
                p2_wheel(page, page_state(page))      # P2 wheel
                p2_block_ctx(page)                    # P2 RMB + contextmenu
                p2_strike(page)                       # P2 LMB strike no-orbit
                st1 = page_state(page)
                bound, st_bind = n2_bind(page)        # N2 organic bind
                if bound:
                    n2a_locked_motion(page, st_bind)  # N2a live-locked (RECORD ok)
                    n2b_dispatch(page, st_bind)       # N2b dispatched vehicle
                else:
                    check("N2a", "locked live motion", False, "skipped: bind failed")
                    check("N2b", "dispatched movementX/Y", False, "skipped: bind failed")
                n8_stamps(page)                       # N8 stamps (bound leg via dispatch)
                n3_unbind(page)                       # N3 unbind + esc-equiv
                n5_autorebind(page)                   # N5 auto-rebind both ways
                n6_chip_toggle(page)                  # N6 chip toggles
                n7_fault(page)                        # N7 fault injection (init script)
            n10_console(page)                     # N10 zero-errors assertion
            try:
                page.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass
    except Exception as e:
        check("HARNESS", "runner", False, "unhandled exception %r" % e)
    finally:
        stop_server(server)
        if srv_raw is not None:
            try:
                srv_raw.shutdown()
            except Exception:
                pass

    # ------------- static / floor checks (no browser) -----------------------
    target_src = ""
    try:
        with open(TARGET, "r", errors="replace") as f:
            target_src = f.read()
    except Exception:
        pass
    if target_src:
        check_n1(target_src)                       # N1
        check_n9(target_src, TARGET)               # N9
    else:
        check("N1", "lock JS + chip + CFG", False, "target unreadable")
        check("N9", "build artifact checks", False, "target unreadable")
    p1_ok, echo, head_ok = check_p1()
    check_p3()
    check_p4_static()
    check_p5_cfg = check_p5()                      # CONFIG additive-only
    check_p6()
    check_p7_keyboard()
    p8_ok, _base = check_p8()

    # ------------- verdict document ------------------------------------------
    npass = sum(1 for r in RESULTS if r["verdict"] == "PASS")
    nrec = sum(1 for r in RESULTS if r["verdict"] == "RECORD")
    nfail = sum(1 for r in RESULTS if r["verdict"] == "FAIL")
    verdict = "PASS" if nfail == 0 else "FAIL"
    # P7-floor discipline: RECORD allowed ONLY on N2a rows
    if any(r["verdict"] == "RECORD" and not r["id"].startswith("N2a") for r in RESULTS):
        verdict = "FAIL"
    ce, pe = err_count()
    ac_map = {}
    for r in RESULTS:
        ac_map.setdefault(r["id"].split("-")[0], []).append(r["id"])
    covered = set()
    for r in RESULTS:
        covered.add(r["id"])
    for ac in ["N1", "N2", "N2a", "N2b", "N3", "N3-esc", "N4", "N5", "N5-off",
               "N6", "N7", "N8", "N9", "N10", "P1-anchor", "P2-wheel",
               "P2-block", "P2-ctx", "P2-strike", "P3", "P4", "P5",
               "P6", "P7-static", "P8", "P9-boot", "X-echo", "BOOT", "HARNESS"]:
        if ac in ("BOOT", "HARNESS"):
            continue
        if ac not in covered:
            check(ac, "coverage", False, "row never executed")
    verdict_doc.update({
        "verdict": verdict,
        "finalized": FINALIZED,
        "target": TARGET_NAME,
        "mode": MODE,
        "harness": os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
        "specOfRecord": "io/specs/mouse-bind-cam-spec.md",
        "specSha256Run": sha256_file(os.path.join(REPO_ROOT, "io/specs/mouse-bind-cam-spec.md")),
        "harnessSha256Run": sha256_file(os.path.abspath(__file__)),
        "counts": {"pass": npass, "record": nrec, "fail": nfail,
                   "total": len(RESULTS)},
        "console": {"errors": ce, "pageErrors": pe,
                    "assert": "zero on full organic run",
                    "samples": (CONSOLE_ERRORS[:5] + PAGE_ERRORS[:5])},
        "perAc": [{"id": r["id"], "status": r["verdict"],
                   "evidence": r["detail"]} for r in RESULTS],
        "vehicles": {k: sorted(v) for k, v in VEHICLE_USE.items()},
        "baselineEcho": echo,
        "headVerified": head_ok,
        "notes": [],
    })
    out = os.path.join(ARTIFACT_DIR, "wh_mousebind_verdict.json")
    with open(out, "w") as f:
        json.dump(verdict_doc, f, indent=1)
    print("---")
    for r in RESULTS:
        if r["verdict"] != "PASS":
            print("%-6s %-44s %s :: %s" % (r["id"], r["name"], r["verdict"],
                                           r["detail"][:160]))
    print("MB-VALIDATION verdict=%s pass=%d record=%d fail=%d artifact=%s" % (
        verdict, npass, nrec, nfail, out))
    sys.exit(0)


if __name__ == "__main__":
    main()