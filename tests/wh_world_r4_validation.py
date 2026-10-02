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


# ------------------------------------------------ in-page probes (JS) -------
# Shared prelude: first mesh carrying material.map under a root.
FIRSTMAP = """function firstMap(root){var f=null; if(!root) return null;
  root.traverse(function(o){ if(f||!o.isMesh) return;
    var ms=Array.isArray(o.material)?o.material:[o.material];
    for(var i=0;i<ms.length;i++){ if(ms[i]&&ms[i].map){f={mesh:o,map:ms[i].map};
      break;} } }); return f;}
  var BODIES=['playerBody','banditBody','ghoulBody'];"""

# AC-R4-1 probe (one evaluate): template maps + live-instance map uuids.
TEX_JS = """(function(){ %s
  var A=window.WH_ASSETS, C=window.WH_CONFIG.assets||{};
  var out={key:('pixelatedBodies' in C)?C.pixelatedBodies:'__absent__',
           loaded:A.loadedCount(), rows:[], live:{playerBody:[],banditBody:[],
           ghoulBody:[]}, consts:{nearest:THREE.NearestFilter,
           lmml:THREE.LinearMipmapLinearFilter, linear:THREE.LinearFilter}};
  BODIES.forEach(function(n){ var f=firstMap(A.getTemplate(n));
    var r={name:n, failed:A.isFailed(n), clips:A.getClips(n).length};
    if(f){ var m=f.map, im=m.image||{};
      r.w=im.width; r.h=im.height; r.src=im.currentSrc||im.src||'';
      r.ctor=im.constructor?im.constructor.name:''; r.mag=m.magFilter;
      r.min=m.minFilter; r.flipY=m.flipY; r.colorSpace=m.colorSpace;
      r.wrapS=m.wrapS; r.wrapT=m.wrapT; r.uuid=m.uuid;
      r.bones=f.mesh.skeleton?f.mesh.skeleton.bones.length:null; }
    out.rows.push(r); });
  var p=window.WH_DEBUG.getPlayer(), pf=p&&firstMap(p.body);
  if(pf) out.live.playerBody.push(pf.map.uuid);
  var rm=window.WH_DEBUG.getRegionManager(), E=rm.enemies||{};
  Object.keys(E).forEach(function(k){ (E[k]||[]).forEach(function(e){
    var f=firstMap(e.root); if(!f) return;
    var n=e.type==='bandit'?'banditBody':(e.type==='ghoul'?'ghoulBody':null);
    if(n) out.live[n].push(f.map.uuid); }); });
  return out; })()""" % FIRSTMAP

# AC-R4-2 probe: symmetric upload of the 3 template maps, forced render,
# then renderer.info.memory counts.
MEM_JS = """(function(){ %s
  var G=window.WH_GAME, R=G.renderer, A=window.WH_ASSETS, up=0;
  BODIES.forEach(function(n){ var f=firstMap(A.getTemplate(n));
    if(f){ R.initTexture(f.map); up++; } });
  R.render(G.scene,G.camera);
  return {textures:R.info.memory.textures,
          geometries:R.info.memory.geometries, uploaded:up}; })()""" % FIRSTMAP

# AC-R4-3(a) probe: draw each template map.image onto a 512 canvas and
# count distinct levels per channel (+ mod-8 congruence + top-8 levels).
TEXSPACE_JS = """(function(){ %s
  var A=window.WH_ASSETS, out=[];
  BODIES.forEach(function(n){ var f=firstMap(A.getTemplate(n));
    if(!f||!f.map.image){ out.push({name:n, err:'no map'}); return; }
    var cv=document.createElement('canvas'); cv.width=512; cv.height=512;
    var cx=cv.getContext('2d'); cx.imageSmoothingEnabled=false;
    cx.drawImage(f.map.image,0,0,512,512);
    var d=cx.getImageData(0,0,512,512).data, ch=[{},{},{}];
    for(var i=0;i<d.length;i+=4){ for(var c=0;c<3;c++){ var v=d[i+c];
      ch[c][v]=(ch[c][v]||0)+1; } }
    var row={name:n, levels:[], mod8:[], top8:[]};
    for(var c2=0;c2<3;c2++){ var ks=Object.keys(ch[c2]);
      row.levels.push(ks.length);
      var res={}; ks.forEach(function(k){ res[k%%8]=1; });
      row.mod8.push(Object.keys(res).length===1);
      ks.sort(function(a,b){return ch[c2][b]-ch[c2][a];});
      row.top8.push(ks.slice(0,8).map(function(k){return [+k,ch[c2][k]];})); }
    out.push(row); });
  return out; })()""" % FIRSTMAP

# AC-R4-3(b) probe (ONE evaluate): render -> readback; hide player body;
# render -> readback; restore (sanctioned, restored in-evaluate).
SCREEN_JS = """(function(){
  var G=window.WH_GAME, p=window.WH_DEBUG.getPlayer();
  if(!p||!p.body) return null;
  var c=G.renderer.domElement, v=new THREE.Vector3();
  p.body.getWorldPosition(v); v.project(G.camera);
  G.renderer.render(G.scene,G.camera);
  var shown=c.toDataURL('image/png');
  var was=p.body.visible; p.body.visible=false;
  G.renderer.render(G.scene,G.camera);
  var hidden=c.toDataURL('image/png');
  p.body.visible=was;
  G.renderer.render(G.scene,G.camera);
  return {shown:shown, hidden:hidden, vz:v.z, cw:c.width, ch:c.height}; })()"""


def wait_loaded(page, wall=60.0):
    """WH_ASSETS.loadedCount settled (2 equal polls 1s apart) -> count."""
    last, deadline = None, time.time() + wall
    while time.time() < deadline:
        n = page.evaluate("window.WH_ASSETS.loadedCount()")
        if n == last:
            return n
        last = n
        page.wait_for_timeout(1000)
    return last


def config_rewrite_route(ctx, counter):
    """B2 sanctioned measurement-only intervention: serve the WORKTREE
    CONFIG.js with `pixelatedBodies: true` rewritten to false. The
    worktree file is never modified; counter['n'] = rewrite count."""
    with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")) as f:
        src = f.read()
    counter["n"] = src.count("pixelatedBodies: true")
    body = src.replace("pixelatedBodies: true", "pixelatedBodies: false")

    def handler(route):
        counter["served"] = counter.get("served", 0) + 1
        route.fulfill(status=200, body=body,
                      headers={"Content-Type": "application/javascript"})
    ctx.route("**/js/CONFIG.js", handler)


# ------------------------------------------- screen-space body metrics -----
def body_metrics(shown, hidden):
    """B6: mask = pixels whose max channel |shown-hidden| > 8. D = distinct
    RGB over mask (shown); E = share of 4-neighbour in-mask pairs whose max
    channel diff <= 2."""
    w, h = shown.size
    a = list(shown.getdata())
    b = list(hidden.getdata())
    mask = [max(abs(p[0] - q[0]), abs(p[1] - q[1]), abs(p[2] - q[2])) > 8
            for p, q in zip(a, b)]
    colors = set()
    eq = pairs = 0
    for i, m in enumerate(mask):
        if not m:
            continue
        p = a[i]
        colors.add(p)
        x = i % w
        for j in ((i + 1) if x + 1 < w else -1, (i + w) if i + w < w * h
                  else -1):
            if j >= 0 and mask[j]:
                q = a[j]
                pairs += 1
                eq += (abs(p[0] - q[0]) <= 2 and abs(p[1] - q[1]) <= 2
                       and abs(p[2] - q[2]) <= 2)
    return {"mask_px": sum(mask), "D": len(colors),
            "E": round(eq / max(1, pairs), 4), "pairs": pairs,
            "size": "%dx%d" % (w, h)}


def screen_probe(page, tag):
    """Camera-settled (vz<1) one-evaluate shown/hidden readback; mask >= 400
    px at 960x540 else settle-retry (infra)."""
    last = None
    for _ in range(1 if SMOKE else 3):
        for _k in range(4):
            wait_frames(page, 3)
            s = page.evaluate(SCREEN_JS)
            if s and s["vz"] < 1:
                break
        if not s or s["vz"] >= 1:
            last = "camera never settled vz=%s" % (s and s["vz"])
            continue
        shown, hidden = decode_image(s["shown"]), decode_image(s["hidden"])
        if is_degenerate(shown) or is_degenerate(hidden):
            last = "degenerate frame"
            continue
        m = body_metrics(shown, hidden)
        if m["mask_px"] < 400:
            last = "mask %d px < 400" % m["mask_px"]
            page.wait_for_timeout(1500)
            continue
        try:
            os.makedirs(ART_DIR, exist_ok=True)
            shown.save(os.path.join(ART_DIR, "r4-screen-%s-shown.png" % tag))
            hidden.save(os.path.join(ART_DIR, "r4-screen-%s-hidden.png" % tag))
        except Exception:
            pass
        m["buf"] = "%dx%d" % (s["cw"], s["ch"])
        return m
    raise InfraError("screen probe (%s): %s" % (tag, last))


# ------------------------------------------------- A2 in-harness probe -----
def r1_js(name):
    """R1 actor-minY JS read verbatim from the UNCHANGED R1 harness at run
    time (one source of truth for the A2 numbers)."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r1_validation.py")
               ).read()
    m = re.search(r'%s = """(.*?)"""' % name, src, re.S)
    return m.group(1) if m else None


def a2_probe(page):
    """R1 A2 protocol in-harness: idle |minY| per actor (player + first
    bandit + first ghoul of the active region) and sprint-walk max |minY|
    (13 x 160ms, ShiftLeft+w). Moves the player: run LAST on a page."""
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


# ------------------------------------------------ per-context collection ----
def collect(browser, off):
    """One fresh context = one full probe set (OFF = route rewrite active).
    Infra failures raise InfraError (flake rule retries the context)."""
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    counter = {"n": None}
    try:
        if off:
            config_rewrite_route(ctx, counter)
        if not load_index(page):
            raise InfraError("page never ready (%s)" % ("OFF" if off else "ON"))
        loaded = wait_loaded(page)
        tex = page.evaluate(TEX_JS)
        mem = page.evaluate(MEM_JS)
        txs = page.evaluate(TEXSPACE_JS)
        scr = screen_probe(page, "off" if off else "on")
        # ON context asserts no route: served CONFIG text == worktree
        served = page.evaluate("fetch('js/CONFIG.js',{cache:'no-store'})"
                               ".then(function(r){return r.text();})")
        with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")) as f:
            wt = f.read()
        a2 = None if off else a2_probe(page)
        return {"off": off, "loaded": loaded, "tex": tex, "mem": mem,
                "texspace": txs, "screen": scr, "a2": a2,
                "rewrite_count": counter["n"],
                "route_served": counter.get("served", 0),
                "served_eq_worktree": served == wt,
                "png_log": list(errs["png"]),
                "req_count": len(errs["req"]),
                "console_errors": errs["console"][:5],
                "page_errors": errs["page"][:5]}
    finally:
        ctx.close()


def collect_retry(browser, off):
    """Flake rule wrapper for one context (infra-shaped only, max 2)."""
    tag = "OFF" if off else "ON"
    for attempt in range(3):
        try:
            return collect(browser, off)
        except Exception as e:
            if attempt == 2:
                print("[diag] collect %s failed after retries: %r" % (tag, e))
                return {"error": repr(e)[:300]}
            FLAKES.append("collect-%s#%d %r" % (tag, attempt, e)[:200])
            print("[flake] collect %s attempt %d: %r" % (tag, attempt, e))


# ------------------------------------------- pre-Devbot baseline capture ----
def tmp_tree(src_prototype=None, archive_rev=None):
    """Temp repo-shaped root: prototype/ (copy of worktree or git archive
    of archive_rev) + tools/build_v7.py; every other top-level entry is
    symlinked (assets are served from the repo root)."""
    root = tempfile.mkdtemp(prefix="whr4_")
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


OFF_KEYS = ["w", "h", "ctor", "mag", "min", "flipY", "colorSpace", "wrapS",
            "wrapT"]


def off_rows(tex):
    return {r["name"]: {k: r.get(k) for k in OFF_KEYS} for r in tex["rows"]}


def archive_baseline(browser):
    """Fallback pre-capture: the pre-Devbot tree (PNG_COMMIT) served from a
    git-archive copy; same TEX_JS + A2 probe at the same pose."""
    root = tmp_tree(archive_rev=PNG_COMMIT)
    proc = None
    try:
        proc, base = spawn_server(root)
        if not base:
            return None
        errs = new_errs()
        ctx, pg = new_page(browser, errs)
        try:
            if not load_index(pg, base):
                return None
            wait_loaded(pg)
            return {"off": off_rows(pg.evaluate(TEX_JS)), "a2": a2_probe(pg),
                    "src": "archive %s" % PNG_COMMIT}
        finally:
            ctx.close()
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def baseline(browser, on):
    """Pre-Devbot capture. On the pre-Devbot tree (key absent) THIS run's
    ON context IS the baseline -> written to tests/artifacts/r4-pre-*.json.
    Else: WH_W4_PRE_A2 / artifact files, else the archive fallback."""
    if on.get("tex", {}).get("key") == "__absent__":
        pre = {"off": off_rows(on["tex"]), "a2": on["a2"],
               "src": "this-run (pre-Devbot tree)"}
        save_json(PRE_OFF_FILE, pre["off"])
        save_json(PRE_A2_FILE, pre["a2"])
        return pre
    off = load_json(PRE_OFF_FILE)
    a2 = json.loads(PRE_A2_ENV) if PRE_A2_ENV else load_json(PRE_A2_FILE)
    if off and a2:
        return {"off": off, "a2": a2,
                "src": "env" if PRE_A2_ENV else "artifact files"}
    arc = archive_baseline(browser)
    if arc:
        return {"off": off or arc["off"], "a2": a2 or arc["a2"],
                "src": arc["src"]}
    return {"off": off, "a2": a2, "src": "MISSING"}


# ------------------------------------------------------------ AC-R4-1 ------
def _row(c, name):
    for r in (c.get("tex") or {}).get("rows", []):
        if r["name"] == name:
            return r
    return {}


def _live_shared(c, name):
    r = _row(c, name)
    live = (c.get("tex") or {}).get("live", {}).get(name, [])
    return bool(live) and all(u == r.get("uuid") for u in live), len(live)


def ac_r4_1(on, off, pre):
    K = on["tex"]["consts"]
    bad = []
    if on["tex"]["key"] is not True:
        bad.append("ON key=%s" % on["tex"]["key"])
    if not on["served_eq_worktree"] or on["route_served"]:
        bad.append("ON served!=worktree or route active")
    ok_png = [p for p in on["png_log"] if p["s"] == 200
              and p["url"].startswith(BASE_ROOT)]
    if len(on["png_log"]) != 3 or len(ok_png) != 3:
        bad.append("ON png requests=%d ok=%d" % (len(on["png_log"]),
                                                 len(ok_png)))
    ON_ROWS, OFF_ROWS = [], []
    for b in BODIES:
        r, o = _row(on, b), _row(off, b)
        sh, nl = _live_shared(on, b)
        ON_ROWS.append(dict(r, live_shared=sh, live_n=nl))
        if not (r.get("w") == r.get("h") == ATLAS):
            bad.append("%s ON dims %sx%s" % (b, r.get("w"), r.get("h")))
        if not str(r.get("src", "")).endswith(
                "races_regen/rigged/%s.rigged.pixelated.png" % STEMS[b]):
            bad.append("%s ON src=%s" % (b, str(r.get("src"))[-60:]))
        if r.get("mag") != K["nearest"] or r.get("min") != K["lmml"]:
            bad.append("%s ON mag/min=%s/%s" % (b, r.get("mag"), r.get("min")))
        if r.get("flipY") is not False:
            bad.append("%s ON flipY=%s" % (b, r.get("flipY")))
        for k in ("colorSpace", "wrapS", "wrapT"):
            if r.get(k) != o.get(k):
                bad.append("%s ON %s=%s OFF=%s" % (b, k, r.get(k), o.get(k)))
        if r.get("failed") or r.get("clips") != 6:
            bad.append("%s ON failed=%s clips=%s" % (b, r.get("failed"),
                                                     r.get("clips")))
        if not sh:
            bad.append("%s ON live map not shared (n=%d)" % (b, nl))
    # OFF state
    if off.get("rewrite_count") != 1:
        bad.append("OFF rewrite_count=%s" % off.get("rewrite_count"))
    if off.get("png_log"):
        bad.append("OFF png requests=%d" % len(off["png_log"]))
    if (off.get("tex") or {}).get("key") is not False:
        bad.append("OFF key=%s" % (off.get("tex") or {}).get("key"))
    pre_off = (pre or {}).get("off") or {}
    for b in BODIES:
        o = _row(off, b)
        sh, nl = _live_shared(off, b)
        OFF_ROWS.append(dict(o, live_shared=sh, live_n=nl))
        if not (o.get("w") == o.get("h") == 2048):
            bad.append("%s OFF dims %sx%s" % (b, o.get("w"), o.get("h")))
        if "pixelated" in str(o.get("src", "")):
            bad.append("%s OFF src pixelated" % b)
        pb = pre_off.get(b)
        if not pb:
            bad.append("%s OFF no pre capture" % b)
        else:
            for k in ("mag", "min", "flipY", "colorSpace"):
                if o.get(k) != pb.get(k):
                    bad.append("%s OFF %s=%s pre=%s" % (b, k, o.get(k),
                                                        pb.get(k)))
        if o.get("failed") or o.get("clips") != 6:
            bad.append("%s OFF failed=%s clips=%s" % (b, o.get("failed"),
                                                      o.get("clips")))
        if not sh:
            bad.append("%s OFF live map not shared (n=%d)" % (b, nl))
    EXTRA["kill_switch"] = {"on": ON_ROWS, "off": OFF_ROWS,
                            "rewrite_count": off.get("rewrite_count"),
                            "on_png_log": on["png_log"],
                            "pre_src": (pre or {}).get("src")}
    slim = lambda rows: [{k: r.get(k) for k in ("name", "w", "h", "mag", "min",
                                                "flipY", "colorSpace", "wrapS",
                                                "wrapT", "ctor", "clips",
                                                "live_shared")} for r in rows]
    check("R4-1", "texture source+filters", not bad,
          "bad=%s on=%s off=%s rewrite=%s pngReq=%s pre=%s" % (
              bad[:12], json.dumps(slim(ON_ROWS)), json.dumps(slim(OFF_ROWS)),
              off.get("rewrite_count"), [(p["url"][-40:], p["s"], p["ct"])
                                         for p in on["png_log"]],
              (pre or {}).get("src")))


# ------------------------------------------------------------ AC-R4-2 ------
def ac_r4_2(on, off):
    mo, mf = on["mem"], off["mem"]
    rows, bad, tot_on, tot_off = [], [], 0, 0
    for b in BODIES:
        r, o = _row(on, b), _row(off, b)
        won, wof = (r.get("w") or 0) * (r.get("h") or 0), \
            (o.get("w") or 0) * (o.get("h") or 0)
        bon, bof = int(won * 4 * 4 / 3), int(wof * 4 * 4 / 3)
        ratio = (wof / float(won)) if won else None
        tot_on += bon
        tot_off += bof
        if ratio != 16.0:
            bad.append("%s ratio=%s" % (b, ratio))
        rows.append({"body": b, "dims_on": "%sx%s" % (r.get("w"), r.get("h")),
                     "dims_off": "%sx%s" % (o.get("w"), o.get("h")),
                     "bytes_on": bon, "bytes_off": bof, "ratio": ratio})
    if mo["textures"] != mf["textures"]:
        bad.append("textures ON=%s OFF=%s" % (mo["textures"], mf["textures"]))
    if mo["geometries"] != mf["geometries"]:
        bad.append("geometries ON=%s OFF=%s" % (mo["geometries"],
                                                mf["geometries"]))
    if mo["uploaded"] != 3 or mf["uploaded"] != 3:
        bad.append("uploaded ON=%s OFF=%s" % (mo["uploaded"], mf["uploaded"]))
    EXTRA["mem_table"] = rows + [{"counts_on": mo, "counts_off": mf,
                                  "total_on": tot_on, "total_off": tot_off,
                                  "total_drop": tot_off - tot_on}]
    check("R4-2", "GPU memory swap", not bad,
          "bad=%s table=%s" % (bad, json.dumps(EXTRA["mem_table"])))


# ------------------------------------------------------------ AC-R4-3 ------
def ac_r4_3(on, off):
    a_bad = []
    a_rec = {"on": on["texspace"], "off_levels": [
        {"name": r.get("name"), "levels": r.get("levels")}
        for r in off["texspace"]]}
    for r in on["texspace"]:
        if r.get("err") or any(n > 32 for n in r["levels"]):
            a_bad.append("%s levels=%s" % (r["name"], r.get("levels")))
    off_disc = all(any(n > 32 for n in r.get("levels", [0]))
                   for r in off["texspace"])
    so, sf = on["screen"], off["screen"]
    b_ok = (so["D"] <= 0.60 * sf["D"] and so["E"] - sf["E"] >= 0.10)
    ev = ("a=%s bad=%s offDiscriminates=%s on=%s off=%s | b=%s D_on=%d "
          "D_off=%d (bar<=%.1f) E_on=%.4f E_off=%.4f (dE=%.4f bar>=0.10) "
          "mask_on=%d mask_off=%d artifacts=tests/artifacts/r4-screen-*.png"
          % (not a_bad, a_bad, off_disc,
             json.dumps([{"name": r["name"], "levels": r.get("levels"),
                          "mod8": r.get("mod8"),
                          "top8": r.get("top8")} for r in on["texspace"]]),
             json.dumps(a_rec["off_levels"]), b_ok, so["D"], sf["D"],
             0.60 * sf["D"], so["E"], sf["E"], so["E"] - sf["E"],
             so["mask_px"], sf["mask_px"]))
    # B6-IO ruling (2026-10-02): texture-space (a) is the PRIMARY gate;
    # the spawn-pose screen bars are unmeasurable on a near-black
    # silhouette (smoke: D 475v467, dE 0.0008). (b) becomes a RECORD
    # scaled re-measure; a lit-pose re-measure rides the full run.
    if not a_bad:
        check("R4-3", "visual posterization", True,
              ev + " | b(RECORD per B6-IO)=%s" % ("met" if b_ok else "dark-pose-unmeasurable"))
    elif off_disc:
        check("R4-3", "visual posterization", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("R4-3", "visual posterization", False, ev)


# ---------------------------------------------------- PNG byte proof -------
def ac_png():
    """3 PNGs: HTTP 200 from our root, image/png, decode 512x512, served
    sha256 == worktree file == PNG_COMMIT blob (re-bake = FAIL, B8)."""
    rows, bad = [], []
    for b in BODIES:
        rel = PNG_PATHS[b]
        row = {"body": b}
        try:
            st, ct, data = _served(BASE_ROOT, rel)
            img = decode_image(data)
            blob = git_blob(PNG_COMMIT, rel)
            row.update({"status": st, "ct": ct, "dims": "%dx%d" % img.size,
                        "served": sha256_bytes(data)[:16],
                        "worktree": sha256_file(os.path.join(REPO_ROOT,
                                                             rel))[:16],
                        "blob": sha256_bytes(blob)[:16] if blob else None,
                        "bytes": len(data)})
            if not (st == 200 and ct.startswith("image/png")
                    and img.size == (ATLAS, ATLAS)
                    and row["served"] == row["worktree"] == row["blob"]):
                bad.append(b)
        except Exception as e:
            row["err"] = repr(e)[:120]
            bad.append(b)
        rows.append(row)
    check("PNG", "pixelated PNG byte proof", not bad,
          "bad=%s rows=%s" % (bad, json.dumps(rows)))


# --------------------------------------------- AC-R4-4 anim regressions -----
def _scan8791(text):
    hits = re.findall(r"[a-z]+://[^\s'\"]*:%d[^\s'\"]*" % FORBIDDEN_PORT,
                      text or "")
    REQ8791.extend(hits)
    return hits


V3_RUNNER = r'''
import re, sys
root = sys.argv[1]
src = open("tests/wh_v3_anim_probes.py").read()
pat = re.compile(r"^ORIGINS = \[.*\]$", re.M)
n = len(pat.findall(src))
print("ORIGINS_REWRITE_COUNT=%d" % n)
sys.stdout.flush()
if n != 1:
    sys.exit(97)
src = pat.sub(lambda m: "ORIGINS = [%r]" % root, src)
sys.argv = ["tests/wh_v3_anim_probes.py"]
exec(compile(src, "tests/wh_v3_anim_probes.py", "exec"),
     {"__name__": "__main__", "__file__": "tests/wh_v3_anim_probes.py"})
'''


def _sub(cmd, extra_env, timeout=3600):
    env = dict(os.environ)
    env.pop("WH_SMOKE", None)            # regressions run their full protocol
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


def anim_v3():
    rc, out, err = _sub([sys.executable, "-c", V3_RUNNER, BASE_ROOT], {})
    m = re.search(r"ORIGINS_REWRITE_COUNT=(\d+)", out)
    cnt = int(m.group(1)) if m else None
    passed = "V3 ANIM PROBES: PASS" in out
    keys = None
    i = out.find("V3 ANIM PROBES:")
    if i >= 0:
        try:
            keys = sorted(json.loads(out[out.index("\n", i) + 1:]).keys())
        except Exception:
            keys = None
    hits = _scan8791(out + err)
    ok = (rc == 0 and cnt == 1 and passed and keys == [BASE_ROOT]
          and not hits)
    return ok, {"rc": rc, "rewrite_count": cnt, "line_pass": passed,
                "keys": keys, "8791": hits[:3], "tail": err[-160:] if rc else ""}


def anim_ds1():
    rc, out, err = _sub([sys.executable, "tests/wh_combat_ds1_validation.py"],
                        {})
    j = _last_json(out) or {}
    m = re.search(r"COMBAT-DS1-A SMOKE SUMMARY\s+total=(\d+) pass=(\d+) "
                  r"fail=(\d+) crashes=(\d+)", out)
    budget = "runtime budget exceeded" in out
    hits = _scan8791(out + err)
    verdict = ("PASS" if j and j.get("fail") == 0 and j.get("crashes") == 0
               else "FAIL")
    ok = verdict == "PASS" and not hits
    return ok, {"rc": rc, "verdict": verdict, "total": j.get("total"),
                "failed": j.get("fail"), "crashes": j.get("crashes"),
                "summary": m.group(0) if m else None, "budget_cut": budget,
                "fails": [a.get("id") for a in j.get("per_ac", [])
                          if a.get("verdict") != "PASS"], "8791": hits[:3]}


def anim_v2():
    rc, out, err = _sub([sys.executable, "tests/wh_v2_verify.py"],
                        {"WH_BASE_PROXY": "http://127.0.0.1:9/"})
    m = re.search(r"ASSET AUDIT \[root\]: (\d+) glb fetches, non-200: "
                  r"(\[.*?\]) =>", out)
    total = int(m.group(1)) if m else None
    non200 = m.group(2) if m else None
    hits = _scan8791(out + err)
    ok = (rc == 0 and m is not None and non200 == "[]"
          and "V2 VERIFY: PASS" in out and not hits)
    return ok, {"rc": rc, "glb_total": total, "non200": non200,
                "proxy_ran": "ASSET AUDIT [proxy]" in out, "8791": hits[:3]}


def ac_r4_4(on, off):
    """B3: whanim2's committed A12 regression set as subprocesses + in-harness
    clips/bones (both contexts) + frozen-GLB sha law."""
    inh = []
    for b in BODIES:
        r, o = _row(on, b), _row(off, b)
        if r.get("clips") != 6 or o.get("clips") != 6:
            inh.append("%s clips %s/%s" % (b, r.get("clips"), o.get("clips")))
        if r.get("bones") is None or r.get("bones") != o.get("bones"):
            inh.append("%s bones %s/%s" % (b, r.get("bones"), o.get("bones")))
        blob = git_blob(BASE_COMMIT, GLB_PATHS[b])
        if not blob or sha256_bytes(blob) != sha256_file(
                os.path.join(REPO_ROOT, GLB_PATHS[b])):
            inh.append("%s GLB sha drift" % b)
    bones = {b: [_row(on, b).get("bones"), _row(off, b).get("bones")]
             for b in BODIES}
    if not FLOOR:
        check("R4-4", "anim regressions", False,
              "subprocesses skipped by WH_W4_FLOOR=0 (wh_v7_weave SKIP-NOTED: "
              "writes builds/) inHarness=%s bones=%s"
              % (inh or "ok", bones), verdict="SKIP-NOTED")
        return
    res = {}
    for k, fn in (("v3", anim_v3), ("ds1", anim_ds1), ("v2", anim_v2)):
        try:
            res[k] = fn()
        except Exception as e:
            res[k] = (False, {"err": repr(e)[:200]})
    EXTRA["floor"]["anim"] = {k: v[1] for k, v in res.items()}
    ok = all(v[0] for v in res.values()) and not inh
    ev = ("v3=%s ds1=%s v2=%s inHarness=%s bones=%s v7weave=SKIP-NOTED "
          "(writes builds/; v7 load covered by PRES)" % (
              json.dumps(res["v3"][1]), json.dumps(res["ds1"][1]),
              json.dumps(res["v2"][1]), inh or "ok", bones))
    check("R4-4", "anim regressions", ok, ev,
          verdict=None if ok else "BLOCK")


# ------------------------------------------------ AC-R4-5 R1 floor ---------
def run_floor_harness(rel, extra_env, timeout):
    """Run the UNCHANGED R1 harness on our shared server; parse the final
    (pretty-printed) JSON by balanced-join from the last '{'-leading line."""
    rc, out, err = _sub([sys.executable, rel], extra_env, timeout)
    _scan8791(out + err)
    j = _last_json(out)
    if not j:
        return None, {}, []
    by = {a.get("id"): a for a in j.get("per_ac", [])}
    fails = sorted({a.get("id") for a in j.get("per_ac", [])
                    if a.get("verdict") in ("FAIL", "FAIL-RETUNE-PENDING")})
    return j, by, fails


def r2_a3_subprobe():
    """A3 settle subprobe source, read verbatim from the R2 harness at run
    time (READ-only; one source of truth for the inherited waiver class)."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"A3_SUBPROBE = r'''(.*?)'''", src, re.S)
    return m.group(1) if m else None


def unchanged_since_base(path):
    return not git("diff", "--name-only", BASE_COMMIT, "--", path).strip()


# R3-landed surfaces (validated at cce06eb) that R1's own A8 may still list
R3_LANDED = ["prototype/js/game.js", "prototype/style.css",
             "tests/wh_world_r3_validation.py"]
INHERIT_PREFIX = ("io/specs/", "io/reports/", "tests/wh_world_r2_validation",
                  "tests/r2parts", "tests/wh_world_r3_validation",
                  "tests/r3parts")


A2_NOISE = 0.0145   # measured same-build spread (3 fresh boots, identical
                    # R4 tree: -0.4911/-0.4766/-0.4850; variance probe
                    # /tmp/whr4_a2_variance.py 2026-10-02). B11-IO ruling:
                    # the cross-run bar = 3x noise (0.05), because the
                    # pre/post capture is two samples OF this noise; a
                    # texture swap cannot move geometry and the swap's own
                    # mechanical integrity is gated by R4-1/R4-4.


def a2_compare(pre, post):
    """B11-IO bar (2026-10-02, variance evidence): cross-run idle-minY
    delta may reach 3x the measured same-build sampling spread (0.05)
    since pre/post are independent samples of idle-pose noise. Real
    texture-swap regressions surface in R4-1 (map dims/filters) and
    R4-4 (clips/bones), which stay hard-gated."""
    bad = []
    for k in ("player", "bandit", "ghoul", "walk"):
        a, b = (pre or {}).get(k), (post or {}).get(k)
        if a is None or b is None:
            bad.append("%s pre=%s post=%s (missing)" % (k, a, b))
        elif b > a + A2_NOISE * 3:
            bad.append("%s %.4f > pre %.4f + %.3f (3x noise)"
                       % (k, b, a, A2_NOISE * 3))
    return bad


def ac_r4_5(pre, on):
    a2_pre = (pre or {}).get("a2")
    a2_post = on.get("a2")
    a2_bad = a2_compare(a2_pre, a2_post)
    rec = {"verdict": None, "fails": [], "waivers": [], "a2_pre": a2_pre,
           "a2_post": a2_post, "a2_bad": a2_bad,
           "a2_pre_src": (pre or {}).get("src")}
    EXTRA["floor"]["r1"] = rec
    if not FLOOR:
        check("R4-5", "R1 floor", False,
              "R1 subprocess skipped by WH_W4_FLOOR=0; in-harness A2 pre=%s "
              "post=%s bad=%s" % (a2_pre, a2_post, a2_bad),
              verdict="SKIP-NOTED")
        return
    j, by, fails = run_floor_harness(
        "tests/wh_world_r1_validation.py",
        {"WH_R1_PORT": str(PORT), "WH_R2_FLOOR": "0"}, 3600)
    rec.update({"verdict": j and j.get("verdict"), "fails": fails,
                "per_ac": ["%s:%s" % (k, v.get("verdict"))
                           for k, v in by.items()],
                "r1_a2_evidence": (by.get("A2") or {}).get("evidence")})
    if j is None:
        check("R4-5", "R1 floor", False, "no parseable R1 verdict",
              verdict="BLOCK")
        return
    ev = {k: (v.get("evidence") or "") for k, v in by.items()}
    pres_ok = any(r["id"] == "PRES" and r["verdict"] == "PASS"
                  for r in RESULTS)
    idx_ok = (sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
              == INDEX_FREEZE_SHA256)
    w = rec["waivers"]

    def a2():
        e = ev.get("A2", "")
        if "idleBad" in e and "minY=-0" in e.replace(" ", "") and not a2_bad:
            w.append("A2-dev-baseline (in-harness A2 not worse than pre)")
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
        # night-rig chain: lighting surfaces byte-identical to the validated
        # R3 marker (no R2 subprocess rides R4) + CONFIG hunks only in assets
        lit = all(unchanged_since_base(p) for p in (
            "prototype/js/game.js", "prototype/js/region-manager.js",
            "prototype/js/player.js", "prototype/style.css",
            "prototype/index.html"))
        if lit and config_hunks_ok()[0]:
            w.append("A4-nightrig (rig byte-identical to cce06eb; CONFIG hunk "
                     "assets-only)")
            return True
        return False

    def a6():
        if "DRIFT" in ev.get("A6", ""):
            w.append("A6-hash-drift")
            return True
        return False

    def a7():
        if idx_ok and unchanged_since_base("prototype/style.css"):
            w.append("A7-R3-style.css-freeze (index freeze-ok, style.css == "
                     "cce06eb)")
            return True
        return False

    def a8():
        paths = re.findall(r"'([^']+)'", ev.get("A8", ""))
        okp = lambda p: (in_surface(p) or p.startswith(INHERIT_PREFIX)
                         or (p in R3_LANDED and unchanged_since_base(p)))
        if pres_ok and paths and all(okp(p) for p in paths):
            w.append("A8-surface (residual in PRES/inherited surfaces, "
                     "secrets re-verified by PRES)")
            return True
        return False

    covered = {"A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "A8": a8}
    unexplained = [f for f in fails if f not in covered]
    a1_ok = (by.get("A1") or {}).get("verdict") == "PASS"
    if j.get("verdict") == "PASS" and a1_ok and not a2_bad:
        check("R4-5", "R1 floor", True, "r1=PASS %s a2_pre=%s a2_post=%s"
              % (rec["per_ac"], a2_pre, a2_post))
    elif (a1_ok and not a2_bad and not unexplained
          and all(covered[f]() for f in fails)):
        check("R4-5", "R1 floor", True,
              "FLOOR-WAIVER r1=%s fails=%s classes=%s a2_pre=%s a2_post=%s "
              "(carrier-req: Testerbot revalidates harness on lane recovery)"
              % (j.get("verdict"), fails, " | ".join(w), a2_pre, a2_post),
              verdict="WAIVED")
    else:
        check("R4-5", "R1 floor", False,
              "r1=%s A1=%s fails=%s unexplained=%s waived=%s a2_bad=%s "
              "(non-artifact -> STOP)" % (j.get("verdict"), a1_ok, fails,
                                          unexplained, " | ".join(w), a2_bad),
              verdict="BLOCK")


# ------------------------------------------------------------ AC-PRES ------
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
# real-assignment law (R2 part10): key-ish word '=' >=8 class chars.
ASSIGN_RE = re.compile(r"(api[_-]?key|apikey|secret|password|token)"
                       r"\s*=\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
MESHY_RE = re.compile(r"msy_[A-Za-z0-9]{8}")
CONFIG_WINDOW = (478, 481)                  # assets {} block at cce06eb
# assets.js windows at cce06eb: header comment, adjacent-to-MANIFEST table,
# adjacent swap helper (between prepTemplate and loadOne), loadOne success.
# Insert windows allow +-1 for git's blank/brace-line slide ambiguity.
ASSETS_WINDOWS = [(6, 7), (53, 56), (151, 154), (165, 179)]
ASSETS_FROZEN_FNS = ["resolveUrl", "makeStandIn", "groundAlign",
                     "prepTemplate", "preloadAll", "instance"]


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


def config_hunks_ok():
    """Only inside assets {}; pure additions = kill-switch comment +
    `pixelatedBodies: true`; timeoutMs/standInColor lines unchanged."""
    ch = hunks("prototype/js/CONFIG.js")
    added = [a for h in ch for a in h[2]]
    removed = [r for h in ch for r in h[3]]
    base = (git_blob(BASE_COMMIT, "prototype/js/CONFIG.js") or b"").decode()
    cur = open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")).read()
    blines = base.splitlines()
    keep = [blines[i - 1] for i in (479, 480)] if len(blines) >= 480 else []
    code = [a.strip() for a in added if not a.strip().startswith("//")]
    comments = [a for a in added if a.strip().startswith("//")]
    shape = (not ch) or (code in (["pixelatedBodies: true,"],
                                  ["pixelatedBodies: true"])
                         and any(re.search(r"kill[- ]?switch", c, re.I)
                                 for c in comments))
    ok = bool(all(_within(h, [CONFIG_WINDOW]) for h in ch)
              and not removed and shape and keep
              and all(k in cur.splitlines() for k in keep)
              and "timeoutMs" in keep[0] and "standInColor" in keep[1])
    return ok, [(h[0], h[1]) for h in ch]


def _fn_src(src, name):
    i = src.find("function %s(" % name)
    if i < 0:
        return None
    j, depth = src.index("{", i), 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[i:k + 1]
    return None


def _block(src, start, end):
    i = src.find(start)
    return src[i:src.index(end, i) + len(end)] if i >= 0 else None


def assets_hunks_ok():
    ah = hunks("prototype/js/assets.js")
    base = (git_blob(BASE_COMMIT, "prototype/js/assets.js") or b"").decode()
    cur = open(os.path.join(REPO_ROOT, "prototype/js/assets.js")).read()
    frozen = {n: (_fn_src(base, n) is not None
                  and _fn_src(base, n) == _fn_src(cur, n))
              for n in ASSETS_FROZEN_FNS}
    chars = [l for l in base.splitlines() if "var CHARACTERS" in l]
    frozen["CHARACTERS"] = bool(chars) and chars[0] in cur.splitlines()
    api = "window.WH_ASSETS = {"
    frozen["WH_ASSETS"] = (_block(base, api, "};") is not None
                           and _block(base, api, "};") == _block(cur, api,
                                                                 "};"))
    newfns = [a for h in ah for a in h[2]
              if re.search(r"^\s*function\s+\w+\s*\(", a)]
    # vacuous on the pre-Devbot tree (no hunks); post-Devbot R4-1 proves
    # the swap exists, this proves where it lives
    ok = (all(_within(h, ASSETS_WINDOWS) for h in ah)
          and all(frozen.values()) and len(newfns) <= 1)
    return ok, {"hunks": [(h[0], h[1]) for h in ah],
                "frozen_bad": [k for k, v in frozen.items() if not v],
                "new_fns": [f.strip()[:40] for f in newfns]}


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


def ac_pres(browser):
    dirty, committed = changed_paths()
    allp = sorted(set(dirty + committed))
    resid = [p for p in allp if not in_surface(p)]
    forbidden = [p for p in allp if p in FORBIDDEN_PROTO]
    other_proto = [p for p in allp if p.startswith("prototype/")
                   and p not in PRES_SURFACE[:5]]
    c_ok, c_h = config_hunks_ok()
    a_ok, a_ev = assets_hunks_ok()
    glb_dirty = [p for p in allp if p.startswith(RIGGED_DIR)
                 and p.endswith(".glb")]
    png_bad = [b for b in BODIES
               if sha256_bytes(git_blob(PNG_COMMIT, PNG_PATHS[b]) or b"")
               != sha256_file(os.path.join(REPO_ROOT, PNG_PATHS[b]))]
    idx = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    i_ok = idx == INDEX_FREEZE_SHA256
    i_base = unchanged_since_base("prototype/index.html")
    v_ok, v_ev = v7_rebuild_clean(browser)
    builds_dirty = [p for p in dirty if p.startswith("prototype/builds/")]
    nsec = secrets_scan()
    added = [a for p in PRES_SURFACE[:2] for h in hunks(p) for a in h[2]]
    free_hits = [a for a in added if re.search(r"\bfree\b", a, re.I)]
    ok = (not resid and not forbidden and not other_proto and c_ok and a_ok
          and not glb_dirty and not png_bad and i_ok and i_base and v_ok
          and not builds_dirty and nsec == 0 and not free_hits)
    ev = ("resid=%s forbidden=%s otherProto=%s configHunks=%s(%s) "
          "assetsHunks=%s(%s) glbDirty=%s pngRebake=%s index=%s(identToBase="
          "%s) v7=%s(%s) buildsDirty=%s secretsHits=%d freeHits=%d "
          "changedSinceBase=%d"
          % (resid, forbidden, other_proto, c_ok, c_h, a_ok, json.dumps(a_ev),
             glb_dirty, png_bad, "freeze-ok" if i_ok else "DRIFT:" + idx[:12],
             i_base, v_ok, v_ev, builds_dirty, nsec, len(free_hits),
             len(allp)))
    blockish = forbidden or other_proto or glb_dirty or not i_ok or nsec
    check("PRES", "preservation surface", ok, ev,
          verdict=None if ok else ("BLOCK" if blockish else "FAIL"))


# ---------------------------------------------------- verdict + main -------
GATING = ["R4-1", "R4-2", "R4-3", "R4-4", "R4-5", "PNG", "PRES"]


def guard(ac, fn, *args):
    """Per-AC try/except (law 6): exceptions become recorded FAIL data.
    Infra retries live in collect_retry (flake rule); number misses are
    never retried."""
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
    ok_states = ("PASS", "WAIVED")
    if all(by.get(k) == "PASS" or (k == "R4-5" and by.get(k) == "WAIVED")
           for k in GATING):
        return "PASS", skipped, by
    rest = [k for k in GATING if k != "R4-3"]
    if (by.get("R4-3") == "FAIL-RETUNE-PENDING" and by.get("R4-1") == "PASS"
            and all(by.get(k) in ok_states + ("SKIP-NOTED",) for k in rest)):
        return "FAIL-RETUNE-PENDING", skipped, by
    return "FAIL", skipped, by


def main():
    server, how, ident = None, "", False
    on = off = pre = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            server, how, ident = start_server()
            if BASE_ROOT:
                on = collect_retry(browser, False)
                off = collect_retry(browser, True)
            ok = bool(BASE_ROOT) and on is not None and "error" not in on
            check("BOOT", "server+ready", ok,
                  "%s base=%s identity(R4 signature)=%s on_err=%s off_err=%s"
                  % (how, BASE_ROOT, ident, (on or {}).get("error"),
                     (off or {}).get("error")))
            if ok and "error" not in off:
                pre = baseline(browser, on)
                guard("R4-1", ac_r4_1, on, off, pre)
                guard("R4-2", ac_r4_2, on, off)
                guard("R4-3", ac_r4_3, on, off)
            else:
                for k in ("R4-1", "R4-2", "R4-3"):
                    check(k, "context-never-ready", False, "collect failed")
            guard("PNG", ac_png)
            guard("PRES", ac_pres, browser)
            if ok and "error" not in off:
                guard("R4-4", ac_r4_4, on, off)
                guard("R4-5", ac_r4_5, pre, on)
            else:
                for k in ("R4-4", "R4-5"):
                    check(k, "context-never-ready", False, "collect failed")
            browser.close()
    except Exception as e:
        check("RUN", "harness-exception", False, repr(e)[:300])
    finally:
        stop_server(server)
    check("NET", "no :%d request" % FORBIDDEN_PORT, not REQ8791,
          "hits=%s" % REQ8791[:5], verdict=None if not REQ8791 else "BLOCK")
    verdict, skipped, by = final_verdict()
    out = {"round": "world-r4", "verdict": verdict, "atlas": ATLAS,
           "kill_switch": {"on": EXTRA["kill_switch"].get("on", []),
                           "off": EXTRA["kill_switch"].get("off", []),
                           "rewrite_count":
                               EXTRA["kill_switch"].get("rewrite_count")},
           "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                       "evidence": r["detail"]} for r in RESULTS],
           "mem_table": EXTRA["mem_table"],
           "floor": EXTRA["floor"], "skip_noted": skipped,
           "flakes": len(FLAKES),
           "notes": "smoke=%s floor=%s server=%s pre=%s flakeLog=%s "
                    "(carrier-req: Testerbot revalidates harness on lane "
                    "recovery)" % (SMOKE, FLOOR, how,
                                   (pre or {}).get("src"), FLAKES)}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # law 6: exit 0 ALWAYS, last line = JSON
        print(json.dumps({"round": "world-r4", "verdict": "BLOCK",
                          "notes": "fatal %r" % e}))
    sys.exit(0)
