"""Witch Hunter World R5 validation harness - collision + world bounds (P0-5
+ P1-4 camera half): radial rim clamp, visual ground extent, prop
colliders, boot spawn validator, camera ground clamp + distance-by-pitch.

Devbot-authored (gate step 3) from the valspec of record
io/specs/testerbot-spec-wh-world-r5.md (Testerbot authored the valspec of
record and REVALIDATES this harness on lane recovery - no silent fallback).
Implements AC-R5-1..R5-5 + PRES with amendments C1-C13 against the LIVE
tree (prototype/index.html via prototype/server.py). Playwright sync API,
headless chromium --enable-unsafe-swiftshader, page-clock timing only.

Env: WH_BASE_ROOT (reuse candidate, identity-checked incl. CONFIG byte
equality + playerMargin), WH_W5_PORT (0 = ephemeral self-spawn),
WH_SMOKE=1 (headings 0/90/180/270, 10 props/region; subprocesses still
run), WH_W5_FLOOR=0 (skip R2 + R1 subprocesses -> SKIP-NOTED, never PASS),
WH_W5_HEADINGS (default 0,45,...,315).

Assembled build artifact: cat tests/r5parts/part01..NN.py (see
tests/r5parts/build.py). Exit code is ALWAYS 0 - failures are data; the
final stdout line is one JSON verdict object.
"""
from playwright.sync_api import sync_playwright
import fnmatch
import hashlib
import io
import json
import math
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
PORT = int(os.environ.get("WH_W5_PORT", "0"))
SMOKE = os.environ.get("WH_SMOKE", "0") == "1"
FLOOR = os.environ.get("WH_W5_FLOOR", "1") != "0"
_HEAD_ENV = os.environ.get("WH_W5_HEADINGS", "")
if SMOKE and not _HEAD_ENV:
    HEADINGS = [0, 90, 180, 270]
else:
    HEADINGS = [int(h) for h in (_HEAD_ENV or "0,45,90,135,180,225,270,315"
                                 ).split(",") if h.strip()]
FORBIDDEN_PORT = 8791           # landed-work server: never touched
BASE_COMMIT = "818d8bc"         # R4 marker = R5 CODE base (valspec header)
ASSETS_BLOB_PREFIX = "4d27e6f9"  # assets.js blob @818d8bc (R4-frozen)
VIEW_W, VIEW_H = 1920, 1080
PLAYER_R = 0.7
ART_DIR = os.path.join(REPO_ROOT, "tests", "artifacts")
PRE_A2_FILE = os.path.join(ART_DIR, "r5-pre-a2.json")
# prototype/index.html pin (valspec 9ad39b809bc4...dc32)
INDEX_FREEZE_SHA256 = ("9ad39b809bc413c723f3cefd5728dfc1d5179f083c01f2846ed"
                       "f36806055dc32")
RIGGED_DIR = "art-direction/3d/assets/races_regen/rigged/"
# AC-PRES allowed set (valspec, exactly; player.js per C13)
PROTO_ALLOWED = ["prototype/js/region-manager.js", "prototype/js/CONFIG.js",
                 "prototype/js/game.js", "prototype/js/player.js"]
PRES_SURFACE = PROTO_ALLOWED + [
    "io/specs/*-r5*", "io/reports/*r5*", "tests/wh_world_r5_validation.py",
    "tests/r5parts", "tests/r5parts/*", "tests/artifacts/r5-*",
    "tests/artifacts/r4-*"]

RESULTS = []
FLAKES = []
REQ8791 = []                    # any ':8791' URL seen in any request/output
EXTRA = {"sweep": [], "validator": {}, "camera": [], "colliders": {},
         "crossing": {}, "floor": {"r1": {}, "r2": {}}, "r_play": None,
         "margin": None, "ground": {}, "notes": []}


class InfraError(Exception):
    """Infra-shaped failure (flake rule: retried up to 2x with reload)."""


def check(ac, name, ok, detail="", verdict=None):
    """One AC = one recorded line. verdict overrides PASS/FAIL (RECORD,
    WAIVED, SKIP-NOTED, BLOCK, FAIL-RETUNE-PENDING)."""
    ok = bool(ok)
    v = verdict or ("PASS" if ok else "FAIL")
    RESULTS.append({"id": ac, "name": name, "ok": ok, "verdict": v,
                    "detail": str(detail)})
    print("AC-%s %-30s => %s  %s" % (ac, name, v, str(detail)[:2000]))
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


def _worktree_config():
    with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js"), "rb") as f:
        return f.read()


def _identity_ok(base):
    """Law 5 + R3/R4 signatures + R5 playerMargin + byte equality."""
    if (":%d" % FORBIDDEN_PORT) in base:
        return False            # never touch the landed-work server
    try:
        _s, _ct, src = _served(base, "js/CONFIG.js")
        return (b"lightPool" in src and b"ambientIntensity: 0" in src
                and b"internalResDiv" in src and b"pixelatedBodies" in src
                and b"playerMargin" in src and src == _worktree_config())
    except Exception:
        return False


def _served_ok(base):
    """Self-spawn readiness: CONFIG served byte-equal to our worktree (the
    pre-Devbot tree lacks playerMargin, so identity cannot hold there; byte
    equality still proves the server is OUR tree)."""
    if (":%d" % FORBIDDEN_PORT) in base:
        return False
    try:
        _s, _ct, src = _served(base, "js/CONFIG.js")
        return src == _worktree_config()
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
    REPO_ROOT on WH_W5_PORT / ephemeral. Returns (proc, how, identity)."""
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
    return {"console": [], "log": [], "page": [], "resp": [], "req": []}


def new_page(browser, errs):
    """Context + page with full request log (8791 BLOCK) + console capture
    (the spawn-validator line is a console.log). Returns (ctx, page)."""
    ctx = browser.new_context(viewport={"width": VIEW_W, "height": VIEW_H},
                              device_scale_factor=1)
    page = ctx.new_page()

    def on_req(r):
        errs["req"].append(r.url)
        if (":%d" % FORBIDDEN_PORT) in r.url:
            REQ8791.append(r.url)

    def on_console(m):
        if m.type == "error":
            errs["console"].append(m.text)
        if "[WH spawn-validator]" in m.text:
            errs["log"].append(m.text)

    page.on("pageerror", lambda e: errs["page"].append(str(e)))
    page.on("console", on_console)
    page.on("request", on_req)
    page.on("response", lambda r: errs["resp"].append(
        {"url": r.url, "s": r.status}) if r.status >= 400 else None)
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


# ------------------------------------------------ in-page probes (JS) -------
STATE_JS = """(function(){var D=window.WH_DEBUG, p=D.getPlayer(), G=window.WH_GAME,
  c=G.camera.position; return {x:p.pos.x, y:p.pos.y, z:p.pos.z,
  active:D.activeRegionId, cx:c.x, cy:c.y, cz:c.z, camDist:p.camDist,
  pitch:p.camPitch*180/Math.PI, yaw:p.camYaw*180/Math.PI, state:p.state,
  locked:!!p.lockTarget};})()"""

CFG_JS = """(function(){var C=window.WH_CONFIG, D=window.WH_DEBUG, regs={};
  [C.regionA, C.regionB].forEach(function(r){ regs[r.id]=r.props.map(
    function(p,i){ var m=D.getAssetMeta(p.asset); return {i:i, name:p.asset,
      x:p.x, z:p.z, s:p.scale, w:m?m.width:null}; }); });
  return {props:regs, A:C.regionA.id, B:C.regionB.id,
    spawn:{A:C.regionA.spawn, B:C.regionB.spawn},
    enemies:{A:C.regionA.enemies, B:C.regionB.enemies},
    fog:{A:C.regionA.fogDensity, B:C.regionB.fogDensity},
    world:C.world, chokepoint:C.chokepoint, boundary:C.boundary,
    hold:C.enemy.holdAtBoundaryMargin, player:C.player};})()"""

RENDER_JS = """(function(){var G=window.WH_GAME;
  G.renderer.render(G.scene,G.camera);
  var c=G.renderer.domElement;
  return {url:c.toDataURL('image/png'), w:c.width, h:c.height};})()"""

GROUND_JS = """(function(){var rm=window.WH_DEBUG.getRegionManager(), out={};
  Object.keys(rm.groups||{}).forEach(function(id){ var g=rm.groups[id];
    g.children.forEach(function(ch){
      if(ch.name==='ground' && ch.geometry && ch.geometry.parameters){
        out[id]={R:ch.geometry.parameters.radius,
                 rep:ch.material.map?ch.material.map.repeat.x:null,
                 repY:ch.material.map?ch.material.map.repeat.y:null}; }
      if(ch.name==='mist-plane' && ch.geometry && ch.geometry.parameters){
        (out[id]=out[id]||{}).mist=ch.geometry.parameters.width; } }); });
  return out;})()"""


def st(page):
    return page.evaluate(STATE_JS)


def poll(page, frames=2):
    """One poll = 2 real rAF frames then a state read (law 1)."""
    wait_frames(page, frames)
    return st(page)


def teleport(page, x, z):
    page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)" % (x, z))


def set_yaw(page, deg):
    page.evaluate("window.WH_DEBUG.setCameraYaw(%f)" % deg)


def nan(*vals):
    return any(v is None or v != v for v in vals)


def rr(s):
    return math.hypot(s["x"], s["z"])


def enter_b(page):
    """R2 L1 stepped teleport at x=-2 (R2 organic_cross verbatim steps);
    asserts activeId == regionB.id. Returns (ok, trace)."""
    cfg = page.evaluate("({A:window.WH_CONFIG.regionA.id,"
                        "B:window.WH_CONFIG.regionB.id})")
    trace = []
    for z in (-5, -8, -12, -16, -21, -24, -27):
        teleport(page, -2, z)
        page.wait_for_timeout(400)
        s = st(page)
        trace.append((z, s["active"]))
        if s["active"] == cfg["B"]:
            page.wait_for_timeout(1500)
            return True, trace
    return False, trace


def settle_cam(page, wall=40.0):
    """Law 3: |dcam| < 0.01 over 2 consecutive polls. Returns (state,
    settled, min camera y seen)."""
    last, calm, miny = None, 0, 1e9
    deadline = time.time() + wall
    s = None
    while time.time() < deadline:
        s = poll(page)
        miny = min(miny, s["cy"])
        if last is not None:
            d = math.sqrt((s["cx"] - last["cx"]) ** 2 + (s["cy"] - last["cy"])
                          ** 2 + (s["cz"] - last["cz"]) ** 2)
            calm = calm + 1 if d < 0.01 else 0
            if calm >= 2:
                return s, True, miny
        last = s
    return s, False, miny


def hold_w(page, yaw_deg, wall, stop, on_sample=None):
    """Real 'w' keydown with setCameraYaw(yaw) (W = (sin(yaw+PI),
    cos(yaw+PI)), player.js:753). Polls until stop(samples) or wall.
    Returns samples."""
    samples = []
    set_yaw(page, yaw_deg)
    page.keyboard.down("w")
    try:
        deadline = time.time() + wall
        while time.time() < deadline:
            s = poll(page)
            samples.append(s)
            if on_sample:
                on_sample(s)
            if stop(samples):
                break
            set_yaw(page, yaw_deg)
    finally:
        try:
            page.keyboard.up("w")
        except Exception:
            pass
    return samples


def stationary_r(samples, n=3, eps=0.01):
    """|dr| < eps over n consecutive polls."""
    if len(samples) < n + 1:
        return False
    rs = [rr(s) for s in samples[-(n + 1):]]
    return all(abs(rs[i + 1] - rs[i]) < eps for i in range(n))


def stationary_xy(samples, n=3, eps=0.01):
    if len(samples) < n + 1:
        return False
    tail = samples[-(n + 1):]
    return all(math.hypot(tail[i + 1]["x"] - tail[i]["x"],
                          tail[i + 1]["z"] - tail[i]["z"]) < eps
               for i in range(n))


# ------------------------------------------- independent recompute (R5-2/4) --
CORRIDOR = (-4.0, 4.0, -31.0, -19.0)   # valspec E set: x in [-4,4], z in [-31,-19]


def meets_corridor(x, z, r):
    x0, x1, z0, z1 = CORRIDOR
    nx, nz = min(max(x, x0), x1), min(max(z, z0), z1)
    return math.hypot(x - nx, z - nz) <= r


# C14 (IO ruling): trunk-class vegetation uses radius * TRUNK_RATIO; the
# harness mirrors the game's exact classification so its independent
# recompute checks the SAME law (the spawn/edge checks stay independent).
TRUNK_RATIO = 0.25
_TRUNK_SET = {"livingOak", "witchwoodTree", "birchTree", "deadTree",
              "deadTree2", "ancientOak", "hangingTree", "twistedSapling",
              "thornbush", "bramble", "largeFern", "deadShrub",
              "mossyStump", "hollowStump"}


def _trunk_r(name, w, s):
    r = (w or 0) * s / 2.0
    if name in _TRUNK_SET or re.search(
            r"tree|oak|birch|sapling|bush|bramble|fern|shrub|stump", name, re.I):
        return r * TRUNK_RATIO
    return r


def collider_table(cfg):
    """C14 radii: (width*scale/2) * TRUNK_RATIO for trunk-class vegetation,
    full footprint otherwise (valspec R5-4 + C14 ruling) per region;
    E = circles meeting the corridor rectangle (exempt, RECORD)."""
    out = {}
    for key in ("A", "B"):
        rid = cfg[key]
        circ, ex = [], []
        for p in cfg["props"][rid]:
            R = _trunk_r(p["name"], p["w"], p["s"])
            row = {"region": key, "i": p["i"], "name": p["name"],
                   "x": p["x"], "z": p["z"], "R": round(R, 4),
                   "meta": p["w"] is not None}
            (ex if meets_corridor(p["x"], p["z"], R) else circ).append(row)
        out[key] = {"circles": circ, "exempt": ex}
    return out


def inside_any(table_region, x, z, pad=PLAYER_R):
    return [c for c in table_region["circles"]
            if math.hypot(x - c["x"], z - c["z"]) < c["R"] + pad]


def recompute_validator(cfg, table, r_play):
    """Harness-side (i)-(iii) from WH_CONFIG + getAssetMeta."""
    viol = []
    plane, hold = cfg["boundary"]["z"], cfg["hold"]
    for key, side in (("A", 1), ("B", -1)):
        for p in cfg["props"][cfg[key]]:
            if (side == 1 and not p["z"] > plane) or (side == -1 and
                                                      not p["z"] < plane):
                viol.append(("prop", key, p["i"], p["name"], "side"))
            if math.hypot(p["x"], p["z"]) > r_play:
                viol.append(("prop", key, p["i"], p["name"], "radius"))
        for i, e in enumerate(cfg["enemies"][key]):
            if (side == 1 and not e["z"] >= plane + hold) or (
                    side == -1 and not e["z"] <= plane - hold):
                viol.append(("enemy", key, i, e["type"], "side"))
            if math.hypot(e["x"], e["z"]) > r_play:
                viol.append(("enemy", key, i, e["type"], "radius"))
        sp = cfg["spawn"][key]
        for c in table[key]["circles"]:
            if math.hypot(sp["x"] - c["x"], sp["z"] - c["z"]) < c["R"] + PLAYER_R:
                viol.append(("spawn", key, c["i"], c["name"],
                             "R=%.3f d=%.3f" % (c["R"], math.hypot(
                                 sp["x"] - c["x"], sp["z"] - c["z"]))))
    return viol


# ------------------------------------------------------------ seam metric ---
def luma_rows(img, cols, rows):
    """Per-row mean luma over the column strips (Rec.709 weights)."""
    px = img.load()
    out = []
    for y in range(rows[0], rows[1]):
        s = n = 0
        for c0, c1 in cols:
            for x in range(c0, c1):
                p = px[x, y]
                s += 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
                n += 1
        out.append(s / max(1, n))
    return out


def seam_S(img):
    """S = max_y |L(y+2) - L(y)| over strips [0.10w,0.30w] U [0.70w,0.90w],
    rows [0.05h,0.70h] (player body excluded by the column choice)."""
    w, h = img.size
    cols = [(int(0.10 * w), int(0.30 * w)), (int(0.70 * w), int(0.90 * w))]
    L = luma_rows(img, cols, (int(0.05 * h), int(0.70 * h)))
    return round(max(abs(L[i + 2] - L[i]) for i in range(len(L) - 2)), 3)


def render_S(page, tag):
    """Settled (law 3) one-evaluate forced render + readback -> S."""
    s, settled, _ = settle_cam(page)
    for _ in range(3):
        r = page.evaluate(RENDER_JS)
        img = decode_image(r["url"])
        if not is_degenerate(img):
            try:
                os.makedirs(ART_DIR, exist_ok=True)
                img.save(os.path.join(ART_DIR, "r5-seam-%s.png" % tag))
            except Exception:
                pass
            return {"S": seam_S(img), "buf": "%dx%d" % img.size,
                    "settled": settled}
        wait_frames(page, 2)
    raise InfraError("degenerate frame (%s)" % tag)


# ------------------------------------------------------------ AC-R5-1 ------
def region_of(h, r_play):
    tz = r_play * math.cos(math.radians(h))
    return "A" if tz > -23 else "B"


def sweep_heading(page, h, r_play, table_reg, key, ref):
    """(b) walk-to-rim + (f) rim seam + (c) snapback for one heading."""
    row = {"h": h, "region": key, "start_shift": 0}
    hs = h
    for _ in range(72):
        sx = (r_play - 6) * math.sin(math.radians(hs))
        sz = (r_play - 6) * math.cos(math.radians(hs))
        if not inside_any(table_reg, sx, sz):
            break
        hs += 5
    row["start_shift"] = hs - h
    teleport(page, sx, sz)
    poll(page)
    samples = hold_w(page, hs + 180, 180.0, stationary_r)
    rs = [rr(s) for s in samples if not nan(s["x"], s["z"])]
    fin = samples[-1] if samples else None
    row["r_max"] = round(max(rs), 4) if rs else None
    row["r_final"] = round(rr(fin), 4) if fin else None
    row["n"] = len(samples)
    row["nan"] = any(nan(s["x"], s["z"]) for s in samples)
    row["home"] = bool(fin) and ((fin["z"] >= -25) if key == "A"
                                 else (fin["z"] <= -25))
    row["walk_ok"] = bool(rs and not row["nan"] and row["home"]
                          and row["r_max"] <= r_play + 0.02
                          and row["r_final"] >= r_play - 0.30)
    # (f) rim seam at the clamped pose (auto-follow holds yaw = outward)
    seam = render_S(page, "%s-h%03d" % (key, h))
    row["S_rim"] = seam["S"]
    row["S_ref"] = ref
    row["seam_ok"] = ref is not None and seam["S"] <= ref + 10
    # (c) snapback from r_play + 5 on the original heading
    teleport(page, (r_play + 5) * math.sin(math.radians(h)),
             (r_play + 5) * math.cos(math.radians(h)))
    snap = [poll(page), poll(page)]
    row["snap"] = round(min(rr(s) for s in snap), 4)
    row["snap_ok"] = row["snap"] <= r_play + 0.02
    return row


def corner_and_enemy(page, key, r_play, cfg):
    """(d) C5 corner trap + (e) enemy[0] radial hold on its home side."""
    out = {}
    tx, tz = (95, -30) if key == "A" else (95, -20)
    teleport(page, tx, tz)
    s = [poll(page), poll(page)][-1]
    out["corner"] = {"x": round(s["x"], 3), "z": round(s["z"], 3),
                     "r": round(rr(s), 4)}
    side_ok = s["z"] >= -25 if key == "A" else s["z"] <= -25
    out["corner_ok"] = bool(side_ok and rr(s) <= r_play + 0.02)
    # (e) enemy: live enemy[0], NaN-guarded, written radially home-side
    e = page.evaluate("(function(){var e=window.WH_DEBUG.getEnemy(0);"
                      "return e?{x:e.x,z:e.z,fsm:e.fsm}:null;})()")
    hx, hz = ((r_play + 5), 0.0) if key == "A" else (0.0, -(r_play + 5))
    if e is None or nan(e["x"], e["z"]):
        page.reload(wait_until="load")
        load_index(page)
        if key == "B":
            enter_b(page)
        e = page.evaluate("(function(){var e=window.WH_DEBUG.getEnemy(0);"
                          "return e?{x:e.x,z:e.z,fsm:e.fsm}:null;})()")
    if e is None or nan(e["x"], e["z"]):
        raise InfraError("enemy[0] NaN/absent in %s" % key)
    page.evaluate("(function(){var e=window.WH_DEBUG.getEnemy(0).ref;"
                  "e.pos.x=%f; e.pos.z=%f;})()" % (hx, hz))
    reads = []
    for _ in range(2):
        wait_frames(page, 2)
        reads.append(page.evaluate("(function(){var e=window.WH_DEBUG."
                                   "getEnemy(0);return {x:e.x,z:e.z};})()"))
    last = reads[-1]
    er = math.hypot(last["x"], last["z"])
    hold = (last["z"] >= -23.5) if key == "A" else (last["z"] <= -26.5)
    margin_key = [k for k in (cfg["world"] or {}) if "enemy" in k.lower()
                  and "margin" in k.lower()]
    out["enemy"] = {"wrote": [hx, hz], "read": last, "r": round(er, 4),
                    "r_enemy": r_play, "enemy_margin_key": margin_key or None}
    out["enemy_ok"] = (not nan(last["x"], last["z"]) and er <= r_play + 0.02
                       and hold)
    return out


def region_pass(browser, key, cfg, r_play, table):
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (%s)" % key)
        yaw0 = st(page)["yaw"]
        if key == "B":
            ok, tr = enter_b(page)
            if not ok:
                return {"error": "B entry failed %s" % tr}
            sp = cfg["spawn"]["B"]
            teleport(page, sp["x"], sp["z"])
            set_yaw(page, yaw0)
        ref = render_S(page, "%s-ref" % key)["S"]
        rows = [sweep_heading(page, h, r_play, table[key], key, ref)
                for h in HEADINGS if region_of(h, r_play) == key]
        ce = corner_and_enemy(page, key, r_play, cfg)
        ground = page.evaluate(GROUND_JS)
        return {"rows": rows, "ce": ce, "ref": ref, "ground": ground,
                "page_errors": errs["page"][:3]}
    finally:
        ctx.close()


def region_pass_retry(browser, key, cfg, r_play, table):
    for attempt in range(3):
        try:
            return region_pass(browser, key, cfg, r_play, table)
        except InfraError as e:
            if attempt == 2:
                return {"error": repr(e)[:300]}
            FLAKES.append("R5-1-%s#%d %r" % (key, attempt, e))
            print("[flake] R5-1 %s attempt %d: %r" % (key, attempt, e))


def ac_r5_1(browser, cfg, table):
    W = cfg["world"]
    m = W.get("playerMargin")
    a_ok = (isinstance(m, (int, float)) and PLAYER_R <= m <= 3.0
            and W.get("groundRadius") == 90)
    if not isinstance(m, (int, float)):
        check("R5-1", "radial clamp sweep", False,
              "(a) world.playerMargin=%r groundRadius=%r" % (
                  m, W.get("groundRadius")))
        return
    r_play = 90 - m
    EXTRA["r_play"], EXTRA["margin"] = r_play, m
    res = {k: region_pass_retry(browser, k, cfg, r_play, table)
           for k in ("A", "B")}
    bad, seam_bad = [], []
    if not a_ok:
        bad.append("(a) margin %r out of [0.7,3.0]" % m)
    for k in ("A", "B"):
        r = res[k]
        if "error" in r:
            bad.append("%s error %s" % (k, r["error"]))
            continue
        for row in r["rows"]:
            EXTRA["sweep"].append({kk: row.get(kk) for kk in (
                "h", "region", "r_max", "r_final", "snap", "S_rim", "S_ref",
                "start_shift", "n")})
            if not row["walk_ok"]:
                bad.append("h%d walk r_max=%s r_final=%s home=%s nan=%s" % (
                    row["h"], row["r_max"], row["r_final"], row["home"],
                    row["nan"]))
            if not row["snap_ok"]:
                bad.append("h%d snap %s" % (row["h"], row["snap"]))
            if not row["seam_ok"]:
                seam_bad.append("h%d S_rim %s > S_ref %s + 10" % (
                    row["h"], row["S_rim"], row["S_ref"]))
        if not r["ce"]["corner_ok"]:
            bad.append("%s corner %s" % (k, r["ce"]["corner"]))
        if not r["ce"]["enemy_ok"]:
            bad.append("%s enemy %s" % (k, r["ce"]["enemy"]))
    # (f) geometry: texel density GATE, d95 extent RECORD
    ground = {}
    for k in ("A", "B"):
        g = (res[k].get("ground") or {}).get(cfg[k]) if "error" not in res[k] \
            else None
        d95 = math.sqrt(math.log(20)) / cfg["fog"][k]
        want = r_play + 1.1 * d95
        if not g or not g.get("R") or g.get("rep") is None:
            seam_bad.append("%s ground mesh unread %s" % (k, g))
            ground[k] = {"read": g}
            continue
        dens = g["rep"] / g["R"]
        dens_ok = abs(dens / (12.0 / 90.0) - 1) <= 0.02
        ground[k] = {"R_vis": round(g["R"], 3), "repeat": round(g["rep"], 4),
                     "mist": g.get("mist"), "density": round(dens, 5),
                     "density_ok": dens_ok, "d95": round(d95, 2),
                     "want_R_vis": round(want, 2),
                     "extent_met(RECORD)": g["R"] >= want - 1e-6}
        if not dens_ok:
            seam_bad.append("%s texel density %.5f vs %.5f" % (
                k, dens, 12.0 / 90.0))
    EXTRA["ground"] = ground
    ev = ("margin=%s r_play=%s bad=%s seamBad=%s ground=%s sweep=%s ce=%s" % (
        m, r_play, bad, seam_bad, json.dumps(ground), json.dumps(
            EXTRA["sweep"]), json.dumps({k: res[k].get("ce") for k in res})))
    if not bad and not seam_bad:
        check("R5-1", "radial clamp sweep", True, ev)
    elif not bad:
        check("R5-1", "radial clamp sweep", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("R5-1", "radial clamp sweep", False, ev)


# ------------------------------------------------------------ AC-R5-2 ------
REPORT_JS = """(function(){var rm=window.WH_DEBUG.getRegionManager();
  return rm ? (rm.spawnReport || null) : null;})()"""

NEG_REWRITES = [
    ("{ asset: 'gravestoneObelisk', x: -10, z: 20,",
     "{ asset: 'gravestoneObelisk', x: -10, z: -40,"),
    ("{ type: 'bandit', x: 0, z: -60 }", "{ type: 'bandit', x: 0, z: -95 }"),
]


def props_block(src, region_key):
    """Text of CONFIG.<region_key>.props: [ ... ] (byte-identity law)."""
    i = src.find("%s: {" % region_key)
    if i < 0:
        return None
    j = src.find("props: [", i)
    k = src.find("\n    ]", j)
    return src[j:k] if j >= 0 and k >= 0 else None


def wait_report(page, wall=30.0):
    deadline = time.time() + wall
    while time.time() < deadline:
        r = page.evaluate(REPORT_JS)
        if r is not None:
            return r
        wait_frames(page, 2)
    return None


def neg_control(browser):
    """Separate context: served CONFIG.js rewritten (sanctioned route, each
    rewrite exactly once). Worktree file never modified."""
    src = _worktree_config().decode()
    counts = [src.count(a) for a, _b in NEG_REWRITES]
    body = src
    for a, b in NEG_REWRITES:
        body = body.replace(a, b)
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    served = {"n": 0}

    def handler(route):
        served["n"] += 1
        route.fulfill(status=200, body=body,
                      headers={"Content-Type": "application/javascript"})
    try:
        ctx.route("**/js/CONFIG.js", handler)
        ready = load_index(page)
        rep = wait_report(page) if ready else None
        return {"counts": counts, "ready": ready, "served": served["n"],
                "report": rep, "page_errors": errs["page"][:3],
                "log": errs["log"][:2]}
    finally:
        ctx.close()


def ac_r5_2(browser, cfg, table):
    r_play = EXTRA.get("r_play") or (90 - (cfg["world"].get("playerMargin")
                                           or 0))
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-2)")
        rep = wait_report(page)
        page.wait_for_timeout(5000)                 # A ghoul runtime z (5 s)
        ghoul = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies("
                              "window.WH_CONFIG.regionA.id);for(var i=0;i<"
                              "l.length;i++){if(l[i].type==='ghoul')return "
                              "{x:l[i].x,z:l[i].z};}return null;})()")
        logs = list(errs["log"])
    finally:
        ctx.close()
    recompute = recompute_validator(cfg, table, r_play)
    n_props = sum(len(cfg["props"][cfg[k]]) for k in ("A", "B"))
    n_en = len(cfg["enemies"]["A"]) + len(cfg["enemies"]["B"])
    bad, spawn_only = [], True
    if rep is None:
        bad.append("spawnReport absent")
        spawn_only = False
    else:
        if rep.get("props") != n_props or n_props != 106:
            bad.append("props %s (cfg %d, want 106)" % (rep.get("props"),
                                                         n_props))
            spawn_only = False
        if rep.get("enemies") != n_en or n_en != 6:
            bad.append("enemies %s (cfg %d, want 6)" % (rep.get("enemies"),
                                                         n_en))
            spawn_only = False
        if rep.get("violations"):
            bad.append("violations %d" % len(rep["violations"]))
            if any(v.get("kind") != "spawn" for v in rep["violations"]):
                spawn_only = False
        if rep.get("error"):
            bad.append("validator error %s" % rep["error"])
            spawn_only = False
    if not logs:
        bad.append("no [WH spawn-validator] console line")
        spawn_only = False
    if recompute:
        bad.append("recompute %s" % recompute)
        if any(v[0] != "spawn" for v in recompute):
            spawn_only = False
    # A ghoul: CONFIG z >= -23.5, or gate-guard flag listed in exempt[]
    g_cfg = [e for e in cfg["enemies"]["A"] if e["type"] == "ghoul"]
    g_flag = bool(g_cfg and g_cfg[0].get("gateGuard"))
    g_exempt = bool(rep and any(x.get("kind") == "enemy" and x.get("name")
                                == "ghoul" for x in rep.get("exempt", [])))
    g_ok = bool(g_cfg) and (g_cfg[0]["z"] >= -23.5 or (
        g_flag and g_exempt and ghoul and ghoul["z"] >= -23.5))
    if not g_ok:
        bad.append("A ghoul cfg=%s flag=%s exempt=%s runtime=%s" % (
            g_cfg, g_flag, g_exempt, ghoul))
        spawn_only = False
    base = (git_blob(BASE_COMMIT, "prototype/js/CONFIG.js") or b"").decode()
    cur = _worktree_config().decode()
    props_same = {k: (props_block(base, k) is not None
                      and props_block(base, k) == props_block(cur, k))
                  for k in ("regionA", "regionB")}
    if not all(props_same.values()):
        bad.append("props arrays moved %s" % props_same)
        spawn_only = False
    # negative control
    neg = neg_control(browser)
    nrep = neg.get("report") or {}
    base_keys = {(v.get("kind"), v.get("region"), v.get("index"))
                 for v in (rep or {}).get("violations", [])}
    new = [v for v in nrep.get("violations", [])
           if (v.get("kind"), v.get("region"), v.get("index")) not in base_keys]
    want = {("prop", cfg["A"], 0, "side"), ("enemy", cfg["B"], 2, "radius")}
    got = {(v.get("kind"), v.get("region"), v.get("index"), v.get("why"))
           for v in new}
    neg_ok = (neg["counts"] == [1, 1] and neg["ready"] and neg["served"] >= 1
              and not neg["page_errors"]
              and len(nrep.get("violations", [])) >= 2 and got == want)
    if not neg_ok:
        bad.append("neg counts=%s ready=%s pageErr=%s new=%s" % (
            neg["counts"], neg["ready"], neg["page_errors"], sorted(got)))
        spawn_only = False
    EXTRA["validator"] = {"report": rep, "recompute": recompute,
                          "neg": {"counts": neg["counts"], "ready":
                                  neg["ready"], "new": sorted(got),
                                  "total": len(nrep.get("violations", []))},
                          "log": logs[:1], "ghoul_runtime": ghoul}
    ev = "bad=%s report=%s recompute=%s neg=%s log=%s ghoul=%s" % (
        bad, json.dumps(rep), recompute, json.dumps(EXTRA["validator"]["neg"]),
        logs[:1], ghoul)
    if not bad:
        check("R5-2", "boot spawn validator", True, ev)
    elif spawn_only:
        # mechanics PASS; only spawn-in-collider misses = radii numeric miss
        # (C12 exactly-once retune spans collider radii)
        check("R5-2", "boot spawn validator", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("R5-2", "boot spawn validator", False, ev)


# ------------------------------------------------------------ AC-R5-3 ------
PITCHES = [-15, 0, 22, 45, 65]
CX, CY = VIEW_W // 2, VIEW_H // 2


def wheel_to(page, target, maxn=24):
    """Organic wheel: each notch = +-0.8 camDist (player.js:233-236)."""
    page.mouse.move(CX, CY)
    for _ in range(maxn):
        cur = st(page)["camDist"]
        if abs(cur - target) < 0.01:
            break
        page.mouse.wheel(0, 100 if target > cur else -100)
        wait_frames(page, 1)
    return st(page)["camDist"]


def drag_to(page, target, sens, pmin, pmax):
    """Organic LMB drag (mousedown also fires tryAttack :196, recorded).
    Clamp ends overshoot by 20 deg so the clamp itself lands the pitch."""
    cur = st(page)["pitch"]
    goal = target
    if target <= pmin:
        goal = pmin - 20
    elif target >= pmax:
        goal = pmax + 20
    dy = int(round((goal - cur) / sens))
    page.mouse.move(CX, CY)
    page.mouse.down()
    page.mouse.move(CX, CY + dy, steps=max(2, abs(dy) // 20))
    page.mouse.up()
    return st(page)["pitch"]


def cam_formula(P, dist, pitch):
    """Devbot-pinned law (report): cap = Max * (1 - k * max(0, sin p));
    eff = clamp(camDist, Min, max(Min, cap)); y floor = clearance."""
    mn, mx = P["camMinDistance"], P["camMaxDistance"]
    k = P.get("camPitchDistShrink")
    clr = P.get("camGroundClearance")
    if k is None or clr is None:
        return None
    sp = math.sin(math.radians(pitch))
    cap = max(mn, mx * (1 - k * max(0.0, sp)))
    eff = max(mn, min(cap, dist))
    vy = max(P["camHeight"] + eff * sp, clr) - P["camHeight"]
    return round(math.hypot(eff * math.cos(math.radians(pitch)), vy), 4)


def cam_cell(page, P, dist_req, pitch_req):
    pitch = drag_to(page, pitch_req, P["mouseSensDegPerPx"],
                    P["camPitchMinDeg"], P["camPitchMaxDeg"])
    s, settled, miny = settle_cam(page)
    s = st(page)
    d = math.sqrt((s["cx"] - s["x"]) ** 2 + (s["cy"] - (s["y"] + P["camHeight"]))
                  ** 2 + (s["cz"] - s["z"]) ** 2)
    return {"dist": dist_req, "pitch_req": pitch_req,
            "pitch": round(pitch, 3), "camDist": round(s["camDist"], 4),
            "y_min": round(min(miny, s["cy"]), 4), "y": round(s["cy"], 4),
            "d": round(d, 4), "d_formula": cam_formula(P, s["camDist"], pitch),
            "settled": settled}


def lock_probe(page, P):
    """C8: lock-on branch builds its own want; clamp must cover it."""
    e = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies(window."
                      "WH_CONFIG.regionA.id);for(var i=0;i<l.length;i++){if("
                      "l[i].type==='bandit'&&l[i].x===l[i].x)return {x:l[i].x,"
                      "z:l[i].z};}return null;})()")
    if not e:
        raise InfraError("no live A bandit for lock probe")
    teleport(page, e["x"], e["z"] + 6)
    poll(page)
    set_yaw(page, 0)
    drag_to(page, -15, P["mouseSensDegPerPx"], P["camPitchMinDeg"],
            P["camPitchMaxDeg"])
    wheel_to(page, 14)
    set_yaw(page, 0)
    page.evaluate("window.WH_DEBUG.engageLockOn()")
    locked = page.evaluate("window.WH_DEBUG.isLocked()")
    miny, ys = 1e9, []
    deadline = time.time() + 10.0
    while time.time() < deadline:
        s = poll(page)
        miny = min(miny, s["cy"])
        ys.append(round(s["cy"], 3))
    s2, settled, m2 = settle_cam(page, wall=20.0)
    still = page.evaluate("window.WH_DEBUG.isLocked()")
    page.evaluate("window.WH_DEBUG.breakLockOn()")
    return {"locked": locked, "still_locked": still, "y_min":
            round(min(miny, m2), 4), "y_settled": round(s2["cy"], 4),
            "settled": settled, "n": len(ys)}


def camera_run(browser, cfg):
    P = cfg["player"]
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-3)")
        cells = []
        for dist in (7, 14, 3):
            got = wheel_to(page, dist)
            for p in PITCHES:
                c = cam_cell(page, P, dist, p)
                c["wheel_readback"] = round(got, 4)
                cells.append(c)
        # by-pitch law re-read at camDist 14 in ascending order 0,22,45,65
        wheel_to(page, 14)
        law = [cam_cell(page, P, 14, p) for p in (0, 22, 45, 65)]
        cam_dist_after = st(page)["camDist"]
        lock = lock_probe(page, P)
        return {"cells": cells, "law": law, "camDist_after": cam_dist_after,
                "lock": lock, "page_errors": errs["page"][:3]}
    finally:
        ctx.close()


def ac_r5_3(browser, cfg):
    P = cfg["player"]
    res = None
    for attempt in range(3):
        try:
            res = camera_run(browser, cfg)
            break
        except InfraError as e:
            if attempt == 2:
                check("R5-3", "camera clamp + by-pitch", False, repr(e))
                return
            FLAKES.append("R5-3#%d %r" % (attempt, e))
    cells, law, lock = res["cells"], res["law"], res["lock"]
    EXTRA["camera"] = cells
    bad = []
    for c in cells + law:
        if c["y_min"] < 0.3:
            bad.append("(a) dist%s p%s y_min %.4f" % (c["dist"], c["pitch_req"],
                                                      c["y_min"]))
        if c["y"] < 0.395:
            bad.append("(b) dist%s p%s y %.4f" % (c["dist"], c["pitch_req"],
                                                  c["y"]))
    if not lock["locked"]:
        bad.append("(c) lock never engaged %s" % lock)
    elif lock["y_min"] < 0.3 or lock["y_settled"] < 0.395:
        bad.append("(c) lock y %s" % lock)
    ds = [c["d"] for c in law]
    for i in range(len(ds) - 1):
        if ds[i + 1] > ds[i] + 0.05:
            bad.append("law non-monotone %s" % ds)
            break
    if not (ds and ds[-1] <= 0.85 * ds[0]):
        bad.append("law d65 %s > 0.85 * d0 %s" % (ds[-1:], ds[:1]))
    if any(d < P["camMinDistance"] - 0.05 for d in ds):
        bad.append("law d < camMin %s" % ds)
    if abs(res["camDist_after"] - 14) > 1e-6:
        bad.append("camDist mutated %s" % res["camDist_after"])
    dflt = [c for c in cells if c["dist"] == 7 and c["pitch_req"] == 22]
    want_y = P["camHeight"] + 7 * math.sin(math.radians(22))
    if not dflt or abs(dflt[0]["d"] - 7) > 0.10 or abs(dflt[0]["y"] -
                                                        want_y) > 0.10:
        bad.append("default framing %s (want d 7 y %.3f)" % (dflt, want_y))
    check("R5-3", "camera clamp + by-pitch", not bad,
          "bad=%s law=%s lock=%s camDistAfter=%s cells=%s" % (
              bad, json.dumps(law), json.dumps(lock), res["camDist_after"],
              json.dumps(cells)))


# ------------------------------------------------------------ AC-R5-4 ------
def isolated(c, reg_table, r_play):
    for o in reg_table["circles"]:
        if o is c:
            continue
        if math.hypot(c["x"] - o["x"], c["z"] - o["z"]) < c["R"] + o["R"] + 1.4:
            return False
    if abs(c["z"] - (-25)) < c["R"] + PLAYER_R:
        return False
    if math.hypot(c["x"], c["z"]) + c["R"] + PLAYER_R > r_play:
        return False
    return True


def ensure_alive(page, key):
    """Enemy aggro can kill the player mid-sweep; a dead player is not
    clamped. Fresh reload (+ B re-entry) restores a live probe body."""
    if st(page)["state"] == "alive":
        return 0
    page.reload(wait_until="load")
    if not load_index(page):
        raise InfraError("reload never ready")
    if key == "B" and not enter_b(page)[0]:
        raise InfraError("B re-entry failed")
    return 1


def a1_walk(page, table):
    c = [x for x in table["A"]["circles"] if x["name"] == "lanternPost"
         and abs(x["x"] + 2) < 1e-6 and abs(x["z"] - 30) < 1e-6]
    if not c:
        return {"error": "lanternPost A1 (-2,30) not in collider set"}
    c = c[0]
    R = c["R"]
    teleport(page, -2 + R + PLAYER_R + 4, 30)
    poll(page)
    samples = hold_w(page, 90, 120.0, stationary_xy)
    ds = [math.hypot(s["x"] - c["x"], s["z"] - c["z"]) for s in samples]
    xs = [s["x"] for s in samples]
    fin = ds[-1] if ds else None
    return {"R": R, "min_d": round(min(ds), 4) if ds else None,
            "final_d": round(fin, 4) if fin is not None else None,
            "min_x": round(min(xs), 4) if xs else None, "n": len(samples),
            "ok": bool(ds) and min(ds) >= R + PLAYER_R - 0.02
            and min(xs) >= -2 and fin <= R + PLAYER_R + 0.30}


def inside_pushout(page, key, table, r_play, limit):
    rows, reloads = [], 0
    reg = table[key]
    allp = sorted(reg["circles"] + reg["exempt"], key=lambda c: c["i"])
    for c in allp[:limit]:
        reloads += ensure_alive(page, key)
        teleport(page, c["x"] + 0.1, c["z"])
        s = [poll(page), poll(page)][-1]
        d = math.hypot(s["x"] - c["x"], s["z"] - c["z"])
        ex = c in reg["exempt"]
        iso = (not ex) and isolated(c, reg, r_play)
        row = {"region": key, "i": c["i"], "name": c["name"], "R": c["R"],
               "d": round(d, 4), "nan": nan(s["x"], s["z"]),
               "class": "exempt" if ex else ("isolated" if iso else
                                             "clustered/edge(RECORD)")}
        row["ok"] = (not row["nan"]) and (not iso or d >= c["R"] + PLAYER_R
                                          - 0.02)
        rows.append(row)
    return rows, reloads


def collider_run(browser, table, r_play):
    limit = 10 if SMOKE else 10 ** 6
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-4)")
        a1 = a1_walk(page, table)
        rows_a, ra = inside_pushout(page, "A", table, r_play, limit)
        ok, tr = enter_b(page)
        if not ok:
            raise InfraError("B entry failed %s" % tr)
        rows_b, rb = inside_pushout(page, "B", table, r_play, limit)
        return {"a1": a1, "rows": rows_a + rows_b, "reloads": ra + rb}
    finally:
        ctx.close()


def ac_r5_4(browser, table, corridor):
    r_play = EXTRA.get("r_play")
    if r_play is None:
        check("R5-4", "prop colliders", False, "no r_play (R5-1 (a) failed)")
        return
    res = None
    for attempt in range(3):
        try:
            res = collider_run(browser, table, r_play)
            break
        except InfraError as e:
            if attempt == 2:
                check("R5-4", "prop colliders", False, repr(e))
                return
            FLAKES.append("R5-4#%d %r" % (attempt, e))
    radii = [{"region": c["region"], "i": c["i"], "name": c["name"],
              "x": c["x"], "z": c["z"], "R": c["R"]}
             for k in ("A", "B") for c in table[k]["circles"] + table[k]["exempt"]]
    exempt = [{"region": c["region"], "i": c["i"], "name": c["name"],
               "R": c["R"]} for k in ("A", "B") for c in table[k]["exempt"]]
    EXTRA["colliders"] = {"radii": sorted(radii, key=lambda r: (r["region"],
                                                                 r["i"])),
                          "exempt": exempt, "a1": res["a1"],
                          "pushout": res["rows"], "reloads": res["reloads"]}
    bad = []
    if not res["a1"].get("ok"):
        bad.append("(a) A1 %s" % res["a1"])
    bad += ["(b) %s#%d %s d=%s R=%s" % (r["region"], r["i"], r["name"], r["d"],
                                        r["R"]) for r in res["rows"]
            if not r["ok"]]
    cmax = (corridor or {}).get("x_abs_max")
    if cmax is None or cmax > 0.10:
        bad.append("(c) corridor |x| max %s" % cmax)
    check("R5-4", "prop colliders", not bad,
          "bad=%s a1=%s corridor=%s exempt(RECORD,C6)=%s isolated=%d "
          "clustered=%d reloads=%d radii=%s" % (
              bad[:20], json.dumps(res["a1"]), cmax, exempt,
              sum(1 for r in res["rows"] if r["class"] == "isolated"),
              sum(1 for r in res["rows"] if r["class"].startswith("clust")),
              res["reloads"], json.dumps(EXTRA["colliders"]["radii"])))


# ------------------------------------------------ subprocess plumbing -------
def _scan8791(text):
    hits = re.findall(r"[a-z]+://[^\s'\"]*:%d[^\s'\"]*" % FORBIDDEN_PORT,
                      text or "")
    if (":%d" % FORBIDDEN_PORT) in (text or "") and not hits:
        hits = [":%d (bare)" % FORBIDDEN_PORT]
    REQ8791.extend(hits)
    return hits


def _sub(cmd, extra_env, timeout=3600):
    env = dict(os.environ)
    env.pop("WH_SMOKE", None)            # floors run their full protocol
    env["WH_BASE_ROOT"] = BASE_ROOT
    env.update(extra_env)
    try:
        p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        return "timeout", str(e.stdout or ""), "timeout"


def _last_json(out):
    lines = out.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("{"):
            try:
                return json.loads("\n".join(lines[i:]))
            except Exception:
                continue
    return None


def run_floor_harness(rel, extra_env, timeout):
    """Run an UNCHANGED prior-round harness on our shared server."""
    rc, out, err = _sub([sys.executable, rel], extra_env, timeout)
    _scan8791(out + err)
    j = _last_json(out)
    if not j:
        return None, {}, []
    by = {a.get("id"): a for a in j.get("per_ac", [])}
    fails = sorted({a.get("id") for a in j.get("per_ac", [])
                    if a.get("verdict") in ("FAIL", "FAIL-RETUNE-PENDING")})
    return j, by, fails


# ------------------------------------------------ R3 L10 scaled re-measure --
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
                q = dx * dx + dy * dy
                if q < r0 * r0 or q > r1 * r1 or (abs(dx) <= excl
                                                  and abs(dy) <= excl):
                    continue
            p = px[x, y]
            s += 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
            n += 1
    return s / max(1, n)


def l10_scaled(browser, d=10):
    """R3 deviation 3 RECORD: R2 L10 geometry at d=10 in BUFFER px."""
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            return {"err": "page never ready"}
        gp = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies("
                           "window.WH_CONFIG.regionA.id);for(var i=0;i<l.length;"
                           "i++){if(l[i].type==='ghoul'&&l[i].x===l[i].x)"
                           "return {x:l[i].x,z:l[i].z};}return null;})()")
        if not gp:
            return {"err": "no ghoul"}
        teleport(page, gp["x"] - d * 0.3, gp["z"] + d * 0.95)
        page.wait_for_timeout(4000)
        s = None
        for _ in range(4):
            wait_frames(page, 3)
            s = page.evaluate(L10_SCALED_JS)
            if s and s["vz"] < 1:
                break
        if not s or s["vz"] >= 1:
            return {"err": "camera never settled", "vz": s and s["vz"]}
        img = decode_image(s["url"])
        w, h = img.size
        cx, cy = int(s["sx"] * w / VIEW_W), int(s["sy"] * h / VIEW_H)
        t = _ring_mean(img, cx, cy, None, 5, 5)
        b = _ring_mean(img, cx, cy, 60, 90, 7)
        return {"d": d, "t": round(t, 1), "b": round(b, 1),
                "c": round(abs(t - b) / max(b, 1.0), 3),
                "buf": "%dx%d" % (w, h)}
    finally:
        ctx.close()


# ------------------------------------------------------------ AC-R5-5 ------
def organic_crossing(browser, cfg):
    """(a) teleport (0,-15), setCameraYaw(0), hold W -> B within 240 s;
    then setCameraYaw(180), hold W -> A within 240 s. |x| traced (R5-4 c)."""
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-5)")
        teleport(page, 0, -15)
        poll(page)
        go = hold_w(page, 0, 240.0, lambda ss: ss[-1]["active"] == cfg["B"])
        flip = go[-1] if go else None
        back = []
        if flip and flip["active"] == cfg["B"]:
            back = hold_w(page, 180, 240.0,
                          lambda ss: ss[-1]["active"] == cfg["A"])
        trace = [(round(s["x"], 3), round(s["z"], 3),
                  "A" if s["active"] == cfg["A"] else "B") for s in go + back]
        xs = [abs(s["x"]) for s in go + back if not nan(s["x"])]
        return {"to_b": bool(flip and flip["active"] == cfg["B"]),
                "z_after_flip": round(flip["z"], 3) if flip else None,
                "to_a": bool(back and back[-1]["active"] == cfg["A"]),
                "x_abs_max": round(max(xs), 4) if xs else None,
                "n": len(trace), "trace": trace[::max(1, len(trace) // 40)],
                "page_errors": errs["page"][:3]}
    finally:
        ctx.close()


def r2_teleport_targets(lid):
    """Literal teleport targets inside the R2 harness function ac_<lid>."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"\ndef ac_%s\(.*?(?=\ndef |\Z)" % lid.lower(), src, re.S)
    if not m:
        return []
    return [(float(a), float(b)) for a, b in re.findall(
        r"teleportPlayer\((-?[\d.]+),\s*(-?[\d.]+)\)", m.group(0))]


def r2_floor(browser, table):
    rec = {"verdict": None, "fails": [], "waivers": []}
    EXTRA["floor"]["r2"] = rec
    if not FLOOR:
        return rec, "SKIP-NOTED"
    j, by, fails = run_floor_harness(
        "tests/wh_world_r2_validation.py",
        {"WH_R2_FLOOR": "0", "WH_R2_PORT": str(PORT)}, 3600)
    rec.update({"verdict": j and j.get("verdict"), "fails": fails,
                "per_ac": ["%s:%s" % (k, v.get("verdict"))
                           for k, v in by.items()]})
    if j is None:
        return rec, "BLOCK"
    if (by.get("L1") or {}).get("verdict") != "PASS":
        rec["l1"] = (by.get("L1") or {}).get("evidence", "")[:400]
        return rec, "BLOCK"
    if not fails:
        return rec, "PASS"
    ok_all = True
    for f in fails:
        ev = by[f].get("evidence", "")
        if f == "L10":
            rec["l10_rows"] = ev[:600]
            rec["l10_scaled"] = l10_scaled(browser)
            rec["waivers"].append("L10-R3-artifact (scaled re-measure RECORD)")
        elif f == "SCOPE":
            viol = re.findall(r"'([^']+)'", ev.split("secrets=")[0])
            clean = ("secrets=[]" in ev and "pageErr=0" in ev
                     and "consoleErr=0" in ev)
            if clean and all(in_surface(p) for p in viol):
                rec["waivers"].append("A6-SCOPE residual in R5 PRES surface %s"
                                      % viol)
            else:
                ok_all = False
        else:
            hits = []
            for (tx, tz) in r2_teleport_targets(f):
                for k in ("A", "B"):
                    for c in inside_any(table[k], tx, tz):
                        hits.append({"t": [tx, tz], "c": [c["x"], c["z"]],
                                     "R": c["R"], "name": c["name"],
                                     "disp": round(c["R"] + PLAYER_R - math.hypot(
                                         tx - c["x"], tz - c["z"]), 4)})
            if hits:
                rec["waivers"].append("R5-collider-teleport(C10) %s %s"
                                      % (f, json.dumps(hits)))
            else:
                ok_all = False
    return rec, ("WAIVED" if ok_all else "BLOCK")


def ac_r5_5(browser, cfg, table):
    org = None
    for attempt in range(3):
        try:
            org = organic_crossing(browser, cfg)
            break
        except InfraError as e:
            if attempt == 2:
                org = {"error": repr(e)}
            else:
                FLAKES.append("R5-5#%d %r" % (attempt, e))
    EXTRA["crossing"]["organic"] = org
    org_ok = bool(org and org.get("to_b") and org.get("to_a")
                  and org.get("z_after_flip") is not None
                  and org["z_after_flip"] < -25)
    rec, fv = r2_floor(browser, table)
    EXTRA["crossing"]["r2"] = {"verdict": rec.get("verdict"),
                               "fails": rec.get("fails"),
                               "waivers": rec.get("waivers")}
    ev = "organic=%s r2=%s floorVerdict=%s" % (
        json.dumps({k: v for k, v in (org or {}).items() if k != "trace"}),
        json.dumps(EXTRA["crossing"]["r2"]), fv)
    if not org_ok:
        check("R5-5", "crossings re-proof", False, ev,
              verdict="BLOCK" if fv == "BLOCK" else None)
    elif fv == "PASS":
        check("R5-5", "crossings re-proof", True, ev)
    elif fv == "WAIVED":
        check("R5-5", "crossings re-proof", True,
              "FLOOR-WAIVER " + ev + " (carrier-req: Testerbot revalidates "
              "harness on lane recovery)", verdict="WAIVED")
    elif fv == "SKIP-NOTED":
        check("R5-5", "crossings re-proof", False,
              ev + " (R2 subprocess skipped by WH_W5_FLOOR=0)",
              verdict="SKIP-NOTED")
    else:
        check("R5-5", "crossings re-proof", False, ev + " (non-artifact -> "
              "STOP)", verdict="BLOCK")
    return org


# ------------------------------------------------------------ AC-PRES ------
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# real-assignment law (R2 part10): key-ish word '=' >=8 class chars.
ASSIGN_RE = re.compile(r"(api[_-]?key|apikey|secret|password|token)"
                       r"\s*=\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
MESHY_RE = re.compile(r"msy_[A-Za-z0-9]{8}")
# Sanctioned windows in BASE_COMMIT line numbers (valspec AC-PRES hunk law;
# insert windows allow +-1 for git's blank/brace-line slide ambiguity).
WINDOWS = {
    "prototype/js/CONFIG.js": [(59, 73),        # world {} (playerMargin + visual keys)
                               (86, 86),        # regionA.enemies ghoul
                               (270, 279)],     # player camera keys (C1)
    "prototype/js/region-manager.js": [
        (99, 113),                              # clampPlayer
        (116, 135),                             # clampEnemyToHomeSide + adjacent helpers
        (251, 255),                             # ground repeat :253
        (272, 276),                             # live wrapper + adjacent helpers
        (296, 298),                             # ground disc :297
        (315, 317)],                            # mist size
    "prototype/js/game.js": [(467, 478)],       # clampPlayerToBounds
    "prototype/js/player.js": [(896, 947)],     # updateCamera (C13)
}


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


def _block(src, start, end):
    i = src.find(start)
    return src[i:src.index(end, i) + len(end)] if i >= 0 else None


def classify_hunks():
    """Every hunk of every allowed proto file classified in/out of window."""
    rows, foreign = [], []
    for path, wins in WINDOWS.items():
        for h in hunks(path):
            ok = _within(h, wins)
            rows.append({"file": path.split("/")[-1], "old": [h[0], h[1]],
                         "add": len(h[2]), "rem": len(h[3]), "in": ok})
            if not ok:
                foreign.append("%s@%d,%d" % (path.split("/")[-1], h[0], h[1]))
    return rows, foreign


def player_invariants():
    """C13: wheel/mousemove/lock-on-framing bytes unchanged."""
    base = (git_blob(BASE_COMMIT, "prototype/js/player.js") or b"").decode()
    cur = open(os.path.join(REPO_ROOT, "prototype/js/player.js")).read()
    bad = []
    for start, end in (("document.addEventListener('mousemove'", "});"),
                       ("document.addEventListener('wheel'",
                        "{ passive: true });")):
        b = _block(base, start, end)
        if b is None or b != _block(cur, start, end):
            bad.append(start.split("'")[1])
    bl = base.splitlines()
    framing = "\n".join(bl[906:929]) if len(bl) >= 929 else None   # :907-929
    if not framing or framing not in cur:
        bad.append("lock-on framing :907-929")
    return bad


def config_invariants():
    base = (git_blob(BASE_COMMIT, "prototype/js/CONFIG.js") or b"").decode()
    cur = _worktree_config().decode()
    bad = []
    for k in ("regionA", "regionB"):
        if props_block(base, k) is None or props_block(base, k) != \
                props_block(cur, k):
            bad.append("%s.props" % k)
    for start in ("  renderer: {", "  lighting: {", "  lightPool: {",
                  "  assets: {"):
        if _block(base, start, "\n  }") != _block(cur, start, "\n  }"):
            bad.append(start.strip())
    return bad


def changed_paths():
    dirty = []
    for line in git("status", "--porcelain", "--untracked-files=all"
                    ).splitlines():
        p = line[3:].strip().strip('"')     # R1 A8 leading-3-char strip
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        dirty.append(p)
    committed = [p for p in git("diff", "--name-only", BASE_COMMIT, "HEAD"
                                ).splitlines() if p]
    return dirty, committed


def secrets_scan():
    """git diff vs base (tracked) + content of untracked new files."""
    txt = git("diff", BASE_COMMIT)
    for p in git("ls-files", "--others", "--exclude-standard").splitlines():
        if p.endswith(".png"):
            continue
        try:
            with open(os.path.join(REPO_ROOT, p), errors="replace") as f:
                txt += f.read()
        except Exception:
            pass
    return (len(MESHY_RE.findall(txt)) + len(ASSIGN_RE.findall(txt)))


def tmp_tree(src_prototype=None, archive_rev=None):
    """Temp repo-shaped root: prototype/ (worktree copy or git archive of
    archive_rev) + tools/build_v7.py; other top-level entries symlinked."""
    root = tempfile.mkdtemp(prefix="whr5_")
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


def v7_rebuild_clean(browser):
    """R3 A8: rebuild on a temp copy; load result; 0 console/page errors."""
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
        errs = new_errs()
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


def unchanged_since_base(path):
    return not git("diff", "--name-only", BASE_COMMIT, "--", path).strip()


def assets_blob():
    cur = subprocess.run(["git", "hash-object", "prototype/js/assets.js"],
                         cwd=REPO_ROOT, capture_output=True, text=True,
                         timeout=30).stdout.strip()
    base = git("rev-parse", "%s:prototype/js/assets.js" % BASE_COMMIT).strip()
    return cur, base


def ac_pres(browser):
    dirty, committed = changed_paths()
    allp = sorted(set(dirty + committed))
    resid = [p for p in allp if not in_surface(p)]
    other_proto = [p for p in allp if p.startswith("prototype/")
                   and p not in PROTO_ALLOWED]
    rows, foreign = classify_hunks()
    p_bad = player_invariants()
    c_bad = config_invariants()
    a_cur, a_base = assets_blob()
    a_ok = a_cur == a_base and a_cur.startswith(ASSETS_BLOB_PREFIX)
    rig_dirty = [p for p in allp if p.startswith(RIGGED_DIR)]
    idx = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    i_ok = idx == INDEX_FREEZE_SHA256
    v_ok, v_ev = v7_rebuild_clean(browser)
    builds_dirty = [p for p in dirty if p.startswith("prototype/builds/")]
    nsec = secrets_scan()
    added = [a for p in PROTO_ALLOWED for h in hunks(p) for a in h[2]]
    free_hits = [a for a in added if re.search(r"\bfree\b", a, re.I)]
    ok = (not resid and not other_proto and not foreign and not p_bad
          and not c_bad and a_ok and not rig_dirty and i_ok and v_ok
          and not builds_dirty and nsec == 0 and not free_hits)
    ev = ("resid=%s otherProto=%s foreignHunks=%s playerInv=%s configInv=%s "
          "assetsBlob=%s(base %s) rigDirty=%s index=%s v7=%s(%s) "
          "buildsDirty=%s secretsHits=%d freeHits=%d changedSinceBase=%d "
          "hunks=%s" % (resid, other_proto, foreign, p_bad, c_bad, a_cur[:12],
                        a_base[:12], rig_dirty,
                        "freeze-ok" if i_ok else "DRIFT:" + idx[:12], v_ok,
                        v_ev, builds_dirty, nsec, len(free_hits), len(allp),
                        json.dumps(rows)))
    blockish = (resid or other_proto or foreign or rig_dirty or not a_ok
                or not i_ok or nsec)
    check("PRES", "preservation surface", ok, ev,
          verdict=None if ok else ("BLOCK" if blockish else "FAIL"))


# ------------------------------------------------ AC-PRES R1 floor ---------
def r1_js(name):
    """R1 actor-minY JS read verbatim from the UNCHANGED R1 harness."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r1_validation.py")
               ).read()
    m = re.search(r'%s = """(.*?)"""' % name, src, re.S)
    return m.group(1) if m else None


def a2_probe(page):
    """R1 A2 protocol in-harness (R4 part03 verbatim): idle |minY| per actor
    + sprint-walk max |minY| (13 x 160ms, ShiftLeft+w)."""
    pj, ej = r1_js("JS_PLAYER_BODY_MINY"), r1_js("ENEMY_MINY_JS")
    page.wait_for_timeout(1000)
    out = {"player": None, "bandit": None, "ghoul": None, "walk": None}
    idle = page.evaluate(pj)
    if idle and idle["minY"] == idle["minY"]:
        out["player"] = round(abs(idle["minY"]), 4)
    for i in range(6):
        e = page.evaluate(ej % i)
        if (e and e["fsm"] != "dead" and e["type"] in out
                and out[e["type"]] is None and e["minY"] == e["minY"]):
            out[e["type"]] = round(abs(e["minY"]), 4)
    try:
        page.keyboard.down("ShiftLeft")
        page.keyboard.down("w")
        dev = 0.0
        for _ in range(13):
            page.wait_for_timeout(160)
            s = page.evaluate(pj)
            if s and s["minY"] == s["minY"]:
                dev = max(dev, abs(s["minY"]))
        out["walk"] = round(dev, 4)
    finally:
        try:
            page.keyboard.up("w")
            page.keyboard.up("ShiftLeft")
        except Exception:
            pass
    return out


def a2_live(browser, base=None):
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page, base):
            return None
        return a2_probe(page)
    finally:
        ctx.close()


def a2_pre(browser):
    """pre = tests/artifacts/r5-pre-a2.json (smoke capture); absent ->
    measured live on a git-archive copy of the R5 base (818d8bc) and
    written to the artifact (same probe, same pose)."""
    pre = load_json(PRE_A2_FILE)
    if pre:
        return pre, "artifact r5-pre-a2.json"
    root = tmp_tree(archive_rev=BASE_COMMIT)
    proc = None
    try:
        proc, base = spawn_server(root)
        if not base:
            return None, "archive server failed"
        pre = a2_live(browser, base)
        if pre:
            save_json(PRE_A2_FILE, pre)
        return pre, "archive %s (written to artifact)" % BASE_COMMIT
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def r2_a3_subprobe():
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"A3_SUBPROBE = r'''(.*?)'''", src, re.S)
    return m.group(1) if m else None


A2_NOISE = 0.0145   # R4 B11 measured same-build spread; bar = 3x (0.05)
LANDED = ["prototype/js/game.js", "prototype/style.css",
          "prototype/js/assets.js", "tests/wh_world_r3_validation.py",
          "tests/wh_world_r4_validation.py"]
INHERIT_PREFIX = ("io/specs/", "io/reports/", "tests/wh_world_r2_validation",
                  "tests/r2parts", "tests/wh_world_r3_validation",
                  "tests/r3parts", "tests/wh_world_r4_validation",
                  "tests/r4parts", RIGGED_DIR)


def a2_compare(pre, post):
    bad = []
    for k in ("player", "bandit", "ghoul", "walk"):
        a, b = (pre or {}).get(k), (post or {}).get(k)
        if a is None or b is None:
            bad.append("%s pre=%s post=%s (missing)" % (k, a, b))
        elif b > a + A2_NOISE * 3:
            bad.append("%s %.4f > pre %.4f + %.3f (3x noise)"
                       % (k, b, a, A2_NOISE * 3))
    return bad


def ac_pres_r1(browser):
    pre, pre_src = a2_pre(browser)
    post = a2_live(browser)
    a2_bad = a2_compare(pre, post)
    rec = {"verdict": None, "fails": [], "waivers": [], "a2_pre": pre,
           "a2_post": post, "a2_bad": a2_bad, "a2_pre_src": pre_src}
    EXTRA["floor"]["r1"] = rec
    if not FLOOR:
        check("PRES-R1", "R1 floor", False,
              "R1 subprocess skipped by WH_W5_FLOOR=0; in-harness A2 pre=%s "
              "post=%s bad=%s" % (pre, post, a2_bad), verdict="SKIP-NOTED")
        return
    j, by, fails = run_floor_harness(
        "tests/wh_world_r1_validation.py",
        {"WH_R1_PORT": str(PORT), "WH_R2_FLOOR": "0"}, 3600)
    rec.update({"verdict": j and j.get("verdict"), "fails": fails,
                "per_ac": ["%s:%s" % (k, v.get("verdict"))
                           for k, v in by.items()]})
    if j is None:
        check("PRES-R1", "R1 floor", False, "no parseable R1 verdict",
              verdict="BLOCK")
        return
    ev = {k: (v.get("evidence") or "") for k, v in by.items()}
    pres_ok = any(r["id"] == "PRES" and r["verdict"] == "PASS"
                  for r in RESULTS)
    idx_ok = (sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
              == INDEX_FREEZE_SHA256)
    r2rec = EXTRA["floor"].get("r2") or {}
    w = rec["waivers"]

    def a2():
        e = ev.get("A2", "")
        if "idleBad" in e and "minY=-0" in e.replace(" ", "") and not a2_bad:
            w.append("A2-dev-baseline (B11: post <= pre + 0.05)")
            return True
        return False

    def a3():
        sub = r2_a3_subprobe()
        if not sub:
            return False
        sp = subprocess.run([sys.executable, "-c", sub, BASE_ROOT],
                            capture_output=True, text=True, timeout=240)
        _scan8791(sp.stdout + sp.stderr)
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
        # C3: R5 edits region-manager/game/player -> night-rig chain
        # re-verified from THIS run's R2 floor: L4 PASS + (L10 PASS or
        # scaled c10 >= 0.25)
        pa = dict(x.split(":", 1) for x in r2rec.get("per_ac", []))
        sc = (r2rec.get("l10_scaled") or {}).get("c")
        l10 = pa.get("L10") == "PASS" or (isinstance(sc, float) and sc >= 0.25)
        if pa.get("L4") == "PASS" and l10:
            w.append("A4-nightrig (C3: r2 L4 PASS, L10 %s c10=%s)"
                     % (pa.get("L10"), sc))
            return True
        return False

    def a6():
        if "DRIFT" in ev.get("A6", ""):
            w.append("A6-hash-drift")
            return True
        return False

    def a7():
        if idx_ok and unchanged_since_base("prototype/style.css"):
            w.append("A7-style.css-freeze (index freeze-ok, style.css == %s)"
                     % BASE_COMMIT)
            return True
        return False

    def a8():
        paths = re.findall(r"'([^']+)'", ev.get("A8", ""))
        okp = lambda p: (in_surface(p) or p.startswith(INHERIT_PREFIX)
                         or (p in LANDED and (unchanged_since_base(p)
                                              or in_surface(p))))
        if pres_ok and paths and all(okp(p) for p in paths):
            w.append("A8-surface (residual in PRES/inherited surfaces, "
                     "secrets re-verified by PRES)")
            return True
        return False

    covered = {"A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "A8": a8}
    unexplained = [f for f in fails if f not in covered]
    a1_ok = (by.get("A1") or {}).get("verdict") == "PASS"
    if j.get("verdict") == "PASS" and a1_ok and not a2_bad:
        check("PRES-R1", "R1 floor", True, "r1=PASS %s a2_pre=%s a2_post=%s"
              % (rec["per_ac"], pre, post))
    elif (a1_ok and not a2_bad and not unexplained
          and all(covered[f]() for f in fails)):
        check("PRES-R1", "R1 floor", True,
              "FLOOR-WAIVER r1=%s fails=%s classes=%s a2_pre=%s(%s) "
              "a2_post=%s (carrier-req: Testerbot revalidates harness on "
              "lane recovery)" % (j.get("verdict"), fails, " | ".join(w),
                                  pre, pre_src, post), verdict="WAIVED")
    else:
        check("PRES-R1", "R1 floor", False,
              "r1=%s A1=%s fails=%s unexplained=%s waived=%s a2_bad=%s "
              "(non-artifact -> STOP)" % (j.get("verdict"), a1_ok, fails,
                                          unexplained, " | ".join(w), a2_bad),
              verdict="BLOCK")


# ---------------------------------------------------- verdict + main -------
GATING = ["R5-1", "R5-2", "R5-3", "R5-4", "R5-5", "PRES", "PRES-R1"]
WAIVABLE = ("R5-5", "PRES-R1")


def guard(ac, fn, *args):
    """Per-AC try/except (law 6): exceptions become recorded FAIL data."""
    try:
        return fn(*args)
    except Exception as e:
        check(ac, "runner-exception", False, repr(e)[:300])
        return None


def final_verdict():
    by = {}
    for r in RESULTS:
        by[r["id"]] = r["verdict"]          # last attempt wins
    skipped = [k for k in GATING if by.get(k) == "SKIP-NOTED"]
    if (len(FLAKES) >= 3 or "BLOCK" in by.values()
            or by.get("BOOT") != "PASS" or by.get("NET") != "PASS"):
        return "BLOCK", skipped, by
    if all(by.get(k) == "PASS" or (k in WAIVABLE and by.get(k) == "WAIVED")
           for k in GATING):
        return "PASS", skipped, by
    soft = ("PASS", "WAIVED", "SKIP-NOTED", "FAIL-RETUNE-PENDING")
    if (any(by.get(k) == "FAIL-RETUNE-PENDING" for k in GATING)
            and all(by.get(k) in soft for k in GATING)):
        return "FAIL-RETUNE-PENDING", skipped, by
    return "FAIL", skipped, by


def boot_cfg(browser):
    for attempt in range(3):
        errs = new_errs()
        ctx, page = new_page(browser, errs)
        try:
            if load_index(page):
                cfg = page.evaluate(CFG_JS)
                return cfg, errs
            raise InfraError("page never ready (BOOT)")
        except Exception as e:
            if attempt == 2:
                return None, {"error": repr(e)[:300]}
            FLAKES.append("BOOT#%d %r" % (attempt, e))
        finally:
            ctx.close()


def main():
    server, how, ident = None, "", False
    cfg = table = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            server, how, ident = start_server()
            if BASE_ROOT:
                cfg, berr = boot_cfg(browser)
            ok = bool(BASE_ROOT) and cfg is not None
            if ok:
                table = collider_table(cfg)
            check("BOOT", "server+ready", ok,
                  "%s base=%s identity(R5 signature)=%s metaMissing=%s" % (
                      how, BASE_ROOT, ident,
                      [c["name"] for k in ("A", "B") for c in
                       (table or {}).get(k, {}).get("circles", [])
                       if not c["meta"]] if table else None))
            if ok:
                guard("R5-1", ac_r5_1, browser, cfg, table)
                guard("R5-2", ac_r5_2, browser, cfg, table)
                guard("R5-3", ac_r5_3, browser, cfg)
                org = guard("R5-5", ac_r5_5, browser, cfg, table)
                guard("R5-4", ac_r5_4, browser, table, org)
            else:
                for k in ("R5-1", "R5-2", "R5-3", "R5-4", "R5-5"):
                    check(k, "context-never-ready", False, "boot failed")
            guard("PRES", ac_pres, browser)
            if ok:
                guard("PRES-R1", ac_pres_r1, browser)
            else:
                check("PRES-R1", "context-never-ready", False, "boot failed")
            browser.close()
    except Exception as e:
        check("RUN", "harness-exception", False, repr(e)[:300])
    finally:
        stop_server(server)
    check("NET", "no :%d request" % FORBIDDEN_PORT, not REQ8791,
          "hits=%s" % REQ8791[:5], verdict=None if not REQ8791 else "BLOCK")
    verdict, skipped, by = final_verdict()
    val = EXTRA["validator"]
    col = EXTRA["colliders"]
    r1 = EXTRA["floor"].get("r1") or {}
    out = {"round": "world-r5", "verdict": verdict,
           "r_play": EXTRA["r_play"], "margin": EXTRA["margin"],
           "sweep": EXTRA["sweep"],
           "validator": {"report": val.get("report"),
                         "recompute": val.get("recompute"),
                         "neg": val.get("neg")},
           "camera": EXTRA["camera"],
           "colliders": {"radii": col.get("radii", []),
                         "exempt": col.get("exempt", []),
                         "a1": col.get("a1", {})},
           "crossing": {"organic": {k: v for k, v in
                                    (EXTRA["crossing"].get("organic") or {}
                                     ).items() if k != "trace"},
                        "r2": EXTRA["crossing"].get("r2", {})},
           "ground": EXTRA["ground"],
           "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                       "evidence": r["detail"]} for r in RESULTS],
           "floor": {"r1": {"waivers": r1.get("waivers", []),
                            "a2_pre": r1.get("a2_pre"),
                            "a2_post": r1.get("a2_post"),
                            "a2_pre_src": r1.get("a2_pre_src")},
                     "r2": EXTRA["floor"].get("r2", {})},
           "skip_noted": skipped, "flakes": len(FLAKES),
           "notes": "smoke=%s floor=%s headings=%s server=%s flakeLog=%s "
                    "(carrier-req: Testerbot revalidates harness on lane "
                    "recovery)" % (SMOKE, FLOOR, HEADINGS, how, FLAKES)}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # law 6: exit 0 ALWAYS, last line = JSON
        print(json.dumps({"round": "world-r5", "verdict": "BLOCK",
                          "notes": "fatal %r" % e}))
    sys.exit(0)
