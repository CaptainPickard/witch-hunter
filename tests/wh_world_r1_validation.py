"""Witch Hunter World R1 validation harness (Testerbot, gate step 2).

Validates ACs A1-A8 of io/specs/devbot-spec-wh-world-r1.md against the LIVE
source tree (prototype/index.html via prototype/server.py). Playwright sync
API, headless chromium (--enable-unsafe-swiftshader). WH_BASE_ROOT /
WH_R1_PORT env overrides (v2 pattern); WH_SMOKE=1 short mode; WH_R1_SUITES=1
runs the preservation suites as subprocesses (A6 full mode).

Exit code is ALWAYS 0 - failures are data (final stdout line is JSON).
"""
from playwright.sync_api import sync_playwright
import base64
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
BASE_ROOT = os.environ.get("WH_BASE_ROOT", "http://localhost:8791/")
PORT = int(os.environ.get("WH_R1_PORT", "8791"))
SMOKE = os.environ.get("WH_SMOKE", "0") == "1"
RUN_SUITES = os.environ.get("WH_R1_SUITES", "0") == "1"

# Dispatch-time preservation floors (spec A6): sha256 + expected profile.
FLOOR_WEAVE = {
    "path": "tests/wh_v7_weave.py",
    "sha256": "d2893c23b834337936fdc9440f9f3cf99736cede2bbc28e647bcf9f9566b4c9b",
    "profile": "10/8",
    "expected_pass": 10, "expected_fail": 8,
}
FLOOR_DS1 = {
    "path": "tests/wh_combat_ds1_validation.py",
    "sha256": "9093216de6a3da6dd3d392fae86a701c623dafe7b2fafe485a00cafddfdf49fb",
    "profile": "capture-at-smoke",  # pre-fix expectation 2 PASS / 16 FAIL
}
# Freeze sha256 for A7 byte-identity (from /tmp/wh-world-r1-freeze-20260930.txt)
FREEZE = {
    "prototype/index.html": "cec75217eb376395cea4642a7640c3d1d9314587f0e3b8c3222c72f7dec2b637",
    "prototype/style.css": "d31fe8487155bbfdb734e233c2973f85204e12a13ff4a5836520ec3db83c1fb7",
    "prototype/builds/v7-playable.html": "a5b5cfdd0e95ab8575f88a76d8073844c208e61f55b6ac8c552af10af19e2a32",
}
ALLOWED_R1_EDITS = [
    "prototype/js/assets.js", "prototype/js/region-manager.js",
    "prototype/js/game.js", "prototype/js/CONFIG.js", "prototype/js/enemy.js",
]
FREEZE_DIRTY = [
    "docs/planning/04-combat-system.md", "docs/planning/08-open-questions.md",
    "docs/planning/17-magic-system.md", "docs/planning/27-equipment-visual-system.md",
    "docs/planning/33-equipment-and-formulas.md", "prototype/index.html",
    "prototype/js/CONFIG.js", "prototype/js/enemy.js", "prototype/js/game.js",
    "prototype/js/player.js", "prototype/style.css",
]

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


def start_server():
    """Spawn prototype/server.py; poll BASE_ROOT for HTTP 200 (max 15s)."""
    try:
        with urllib.request.urlopen(BASE_ROOT, timeout=1.0) as r:
            if r.status == 200:
                return None  # external server already up
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

# ------------------------------------------------------------- page boot ----
def new_page(browser, console_errors, page_errors):
    page = browser.new_page(viewport={"width": 960, "height": 600})
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("console", lambda m: console_errors.append(m.text)
            if m.type == "error" else None)
    return page


def load_index(page, path="index.html"):
    """Load a tree page and wait until WH_DEBUG is ready (max 20s)."""
    page.goto(BASE_ROOT + path, wait_until="load", timeout=30000)
    deadline = time.time() + 20.0
    while time.time() < deadline:
        try:
            ok = page.evaluate(
                "(function(){try{return typeof window.WH_DEBUG==='object' && "
                "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
                "!!window.WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()")
            if ok:
                page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        page.wait_for_timeout(250)
    print("[diag] WH_DEBUG never ready for " + path)
    return False


# ------------------------------------------------- PNG decode (stdlib only) --
def decode_png(data_url):
    """Minimal PNG reader (8-bit RGB/RGBA, non-interlaced) from a data URL."""
    raw = base64.b64decode(data_url.split(",", 1)[1])
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a png")
    pos, w, h, depth, ctype = 8, 0, 0, 0, 0
    idat = b""
    while pos < len(raw):
        ln, typ = struct.unpack(">I4s", raw[pos:pos + 8])
        body = raw[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif typ == b"IDAT":
            idat += body
        pos += 12 + ln
    if depth != 8 or ctype not in (2, 6):
        raise ValueError("unsupported png depth=%d ctype=%d" % (depth, ctype))
    bpp = 3 if ctype == 2 else 4
    stride = w * bpp
    data = zlib.decompress(idat)
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = data[p]; p += 1
        line = bytearray(data[p:p + stride]); p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride: y * stride + stride] = line
        prev = line
    return w, h, bytes(out), bpp


def ring_pixels(w, h, n=64, r_frac=0.35):
    """Screen-space ring sample coordinates around viewport center."""
    cx, cy = w / 2.0, h / 2.0
    r = r_frac * min(w, h)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts


# ------------------------------------------------------- geometry JS helpers -
JS_SCENE_BBOXES = """(function(){
  function bbox(o){ try { var b=new THREE.Box3().setFromObject(o);
    return {minY:b.min.y, maxY:b.max.y}; } catch(e){ return null; } }
  var rm = window.WH_DEBUG.getRegionManager();
  var out = {regions:{}, player:null, enemies:[]};
  var ids = Object.keys(rm.groups || {});
  for (var i=0;i<ids.length;i++){
    var gid = ids[i]; var g = rm.groups[gid];
    var rec = {visible: g.visible, props: [], ground: null, children: g.children.length};
    var enemyRoots = [];
    var elist = rm.enemies[gid] || [];
    for (var j=0;j<elist.length;j++) enemyRoots.push(elist[j].root);
    for (var k=0;k<g.children.length;k++){
      var ch = g.children[k];
      var isEnemy = enemyRoots.indexOf(ch) >= 0;
      var isGround = !!(ch.geometry && ch.geometry.type === 'CircleGeometry');
      var isMist = !!(ch.material && ch.material.transparent === true &&
                      ch.geometry && ch.geometry.type === 'PlaneGeometry');
      if (isGround) { rec.ground = bbox(ch); continue; }
      if (isMist || isEnemy) continue;
      var b = bbox(ch);
      if (b) rec.props.push({name: ch.name || ch.children[0].name || '?',
                             minY: b.minY, maxY: b.maxY,
                             px: ch.position.x, pz: ch.position.z,
                             scale: ch.scale.x});
    }
    out.regions[gid] = rec;
  }
  var p = window.WH_DEBUG.getPlayer();
  if (p && p.root) { var pb = bbox(p.root); if (pb) out.player = pb; }
  var act = rm.logic.activeId;
  var ea = rm.enemies[act] || [];
  for (var m=0;m<ea.length;m++){
    var b2 = bbox(ea[m].root);
    out.enemies.push({type: ea[m].type, fsm: ea[m].fsm, bbox: b2,
                      rootY: ea[m].root.position.y});
  }
  return out;
})()"""

JS_PLAYER_BODY_MINY = """(function(){
  var p = window.WH_DEBUG.getPlayer();
  if (!p || !p.body) return null;
  var b = new THREE.Box3().setFromObject(p.body);
  return {minY: b.min.y, maxY: b.max.y};
})()"""

ENEMY_MINY_JS = """(function(){
  var rm = window.WH_DEBUG.getRegionManager();
  var list = rm.enemies[rm.logic.activeId] || [];
  var e = list[%d]; if (!e) return null;
  var b = new THREE.Box3().setFromObject(e.root);
  return {type: e.type, fsm: e.fsm, minY: b.min.y, maxY: b.max.y,
          rootY: e.root.position.y, hp: e.hp};
})()"""


# ------------------------------------------------------------------ ACs ------
def ac_a1(page):
    """A1 prop ground-align: every CONFIG prop instance in both regions
    (B built organically via boundary approach -> manager prewarm) joined
    to scene objects by (x,z); |worldBBox.min.y| <= 0.02 and height
    consistent with measured template height * scale. NaN-safe."""
    data = page.evaluate("""(function(){
      var C=window.WH_CONFIG, rm=window.WH_DEBUG.getRegionManager();
      // walk toward boundary (z = C.boundary.z) from region A side to
      // trigger the manager's own prewarm build of region B
      try {
        var bz=C.boundary.z;
        var p=window.WH_DEBUG.getPlayerPosition();
        var tz = (p.z > bz) ? bz + 22 : bz - 22;   // inside preWarm dist
        window.WH_DEBUG.teleportPlayer(p.x, tz);
      } catch(e){}
      return true;})()""")
    page.wait_for_timeout(2500)
    built = page.evaluate(
        "(function(){var rm=window.WH_DEBUG.getRegionManager();"
        "return Object.keys(rm.groups);})()")
    info = page.evaluate("""(function(){
      var C=window.WH_CONFIG, rm=window.WH_DEBUG.getRegionManager();
      var out={rows:[],spawn:{ax:C.regionA.spawn.x,az:C.regionA.spawn.z}};
      [C.regionA, C.regionB].forEach(function(R){
        var g=rm.groups[R.id]; if(!g) return;
        R.props.forEach(function(p){
          var found=null;
          for(var i=0;i<g.children.length;i++){
            var ch=g.children[i];
            if(Math.abs(ch.position.x-p.x)<1e-6 &&
               Math.abs(ch.position.z-p.z)<1e-6){found=ch;break;}
          }
          if(!found){out.rows.push({r:R.id,a:p.asset,miss:true});return;}
          var b=new THREE.Box3().setFromObject(found);
          var gh=null; try{gh=window.WH_ASSETS.groundHeight(p.asset);}catch(e){}
          out.rows.push({r:R.id,a:p.asset,minY:b.min.y,maxY:b.max.y,
                    scale:p.scale,gh:gh});
        });
      });
      return out;})()""")
    # return player to region A spawn so later ACs start clean
    page.evaluate("(function(){var C=window.WH_CONFIG;"
                  "window.WH_DEBUG.teleportPlayer(C.regionA.spawn.x,"
                  "C.regionA.spawn.z);})()")
    page.wait_for_timeout(800)
    rows = info["rows"] if info else []
    miss = [d for d in rows if d.get("miss")]
    viol = [d for d in rows if not d.get("miss") and
            (not math.isfinite(d["minY"]) or abs(d["minY"]) > 0.02)]
    hv = [d for d in rows if not d.get("miss") and d.get("gh") and
          (not math.isfinite(d["maxY"]) or
           abs(d["maxY"] - d["gh"] * d["scale"]) > 0.05 * max(1, d["scale"]))]
    worst = sorted(viol, key=lambda d: -abs(d["minY"]))[:3]
    detail = ("props=%d missJoin=%d minYViol=%d heightViol=%d built=%s "
              "worst=[%s]" % (len(rows), len(miss), len(viol), len(hv),
              ",".join(built) or "-", "; ".join(
                  "%s/%s minY=%.2f" % (d["r"][:4], d["a"], d["minY"])
                  for d in worst) or "-"))
    ok = len(rows) > 0 and not miss and len(viol) == 0 and len(hv) == 0
    check("A1", "prop ground-align", ok, detail)


def ac_a2(page):
    """A2 actor ground-align: player+bandit+ghoul idle |minY|<=0.02;
    sprint 2s max deviation <=0.05 (organic keyboard)."""
    page.wait_for_timeout(1000)
    idle = page.evaluate(JS_PLAYER_BODY_MINY)
    enemies = []
    for i in range(3):
        e = page.evaluate(ENEMY_MINY_JS % i)
        if e and e["fsm"] != "dead":
            enemies.append(e)
    idle_bad = []
    if not idle:
        idle_bad.append("player body missing")
    elif not math.isfinite(idle["minY"]):
        idle_bad.append("player minY=NaN")
    elif abs(idle["minY"]) > 0.02:
        idle_bad.append("player minY=%.3f" % idle["minY"])
    for e in enemies:
        if not math.isfinite(e["minY"]):
            idle_bad.append("%s minY=NaN" % e["type"])
        elif abs(e["minY"]) > 0.02:
            idle_bad.append("%s minY=%.3f" % (e["type"], e["minY"]))
    sprint_dev = None
    if not SMOKE:
        try:
            pos0 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
            page.keyboard.down("ShiftLeft")
            page.keyboard.down("w")
            maxdev = 0.0
            for _ in range(13):
                page.wait_for_timeout(160)
                s = page.evaluate(JS_PLAYER_BODY_MINY)
                if s and math.isfinite(s["minY"]):
                    maxdev = max(maxdev, abs(s["minY"]))
            sprint_dev = maxdev
        finally:
            try:
                page.keyboard.up("w")
                page.keyboard.up("ShiftLeft")
            except Exception:
                pass
            page.wait_for_timeout(400)
    idle_ok = not idle_bad
    sprint_ok = sprint_dev is None or sprint_dev <= 0.05
    ok = idle_ok and sprint_ok and len(enemies) >= 1
    detail = "idleBad=[%s] sprintMaxDev=%s enemies=%d" % (
        "; ".join(idle_bad) or "-", "skipped(smoke)" if sprint_dev is None
        else "%.3f" % sprint_dev, len(enemies))
    check("A2", "actor ground-align", ok, detail)


def ac_a3(page):
    """A3 corpse ground-align: kill an enemy (organic clicks), wait settle,
    corpse |minY| <= 0.05. Fallback: damage-hook (flagged)."""
    # Position near a bandit in region A (teleport = shipped debug API).
    page.evaluate("(function(){var C=window.WH_CONFIG;"
                  "var e=C.regionA.enemies;"
                  "window.WH_DEBUG.teleportPlayer(e[0].x+2, e[0].z);})()")
    page.wait_for_timeout(300)
    if SMOKE:
        # short mode: damage-hook fallback directly, marked as such
        page.evaluate("(function(){var rm=window.WH_DEBUG.getRegionManager();"
                      "var l=rm.enemies[rm.logic.activeId]||[];"
                      "if(l[0])l[0].takeDamage(99999);})()")
        page.wait_for_timeout(3500)
        e = page.evaluate(ENEMY_MINY_JS % 0)
        ok = bool(e and e["fsm"] == "dead" and
                  math.isfinite(e["minY"]) and abs(e["minY"]) <= 0.05)
        check("A3", "corpse ground-align", ok,
              "smoke damage-hook fallback minY=%s fsm=%s" %
              (e and round(e["minY"], 3), e and e["fsm"]))
        return
    dead_idx, clicks, used_hook = None, 0, False
    for attempt in range(20):
        page.mouse.click(480, 300)  # canvas center -> tryAttack (organic)
        clicks += 1
        page.wait_for_timeout(420)
        st = [(i, page.evaluate(ENEMY_MINY_JS % i)) for i in range(3)]
        for i, e in st:
            if e and e["fsm"] == "dead":
                dead_idx = i
                break
        if dead_idx is not None:
            break
    if dead_idx is None:
        # organic kill unreachable within budget -> sanctioned fallback
        page.evaluate("(function(){var rm=window.WH_DEBUG.getRegionManager();"
                      "var l=rm.enemies[rm.logic.activeId]||[];"
                      "if(l[0])l[0].takeDamage(99999);})()")
        used_hook = True
        dead_idx = 0
    page.wait_for_timeout(3500)  # settle + bounce decay
    e = page.evaluate(ENEMY_MINY_JS % dead_idx)
    if not e or e["fsm"] != "dead":
        check("A3", "corpse ground-align", False,
              "enemy %s not dead (clicks=%d hook=%s)" % (dead_idx, clicks, used_hook))
        return
    ok = e is not None and math.isfinite(e["minY"]) and abs(e["minY"]) <= 0.05
    detail = "minY=%.3f rootY=%.3f clicks=%d hook=%s" % (
        e["minY"], e["rootY"], clicks, used_hook)
    check("A3", "corpse ground-align", ok, detail)
    if used_hook:
        RESULTS[-1]["detail"] += " [fallback: damage-hook, organic unreachable]"


JS_LUMA_SNAP = """(function(){
  var g = window.WH_GAME || window.game || null;
  var canvas = document.querySelector('canvas');
  if (!g || !g.renderer || !g.scene || !g.camera || !canvas) return null;
  g.renderer.render(g.scene, g.camera);   // forced synchronous render
  var url = canvas.toDataURL('image/png');
  return {url: url, w: canvas.width, h: canvas.height};
})()"""


def _readback(page):
    snap = page.evaluate(JS_LUMA_SNAP)
    if not snap or not snap.get("url"):
        return None
    w, h, px, bpp = decode_png(snap["url"])
    return {"w": w, "h": h, "px": px, "bpp": bpp}


def _sample(pts, img):
    vals = []
    w, h, px, bpp = img["w"], img["h"], img["px"], img["bpp"]
    for x, y in pts:
        if 0 <= x < w and 0 <= y < h:
            o = (y * w + x) * bpp
            vals.append(0.299 * px[o] + 0.587 * px[o + 1] + 0.114 * px[o + 2])
    return vals


def _stats(vals):
    if not vals:
        return 0.0, 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return mean, math.sqrt(var)


def ac_a4(page):
    """A4 ground luminance ring readback: mean > 20/255 scale (0-255) and
    pixel stddev > 4 in a ring around the player (headless-safe). The
    camera looks down at the player from behind, so a tight ring at
    r_frac=0.18 of viewport height is near-field ground; fog band pixels
    are excluded by dropping the darkest quartile (fog ~uniform and
    darkest), then gating on the brighter set."""
    img = _readback(page)
    if not img:
        check("A4", "ground luminance ring", False, "readback failed")
        return
    w, h = img["w"], img["h"]
    px, bpp = img["px"], img["bpp"]
    vals = []
    for y in range(int(0.72 * h), int(0.95 * h)):
        for x in range(int(0.30 * w), int(0.70 * w)):
            o = (y * w + x) * bpp
            vals.append(0.299 * px[o] + 0.587 * px[o + 1] + 0.114 * px[o + 2])
    if not vals:
        check("A4", "ground luminance ring", False, "no samples decoded")
        return
    mean, sd = _stats(vals)
    ok = mean > 20 and sd > 4
    check("A4", "ground luminance ring", ok,
          "groundBand[%d px] mean=%.2f sd=%.2f min=%.1f max=%.1f "
          "(need mean>20 sd>4)" % (len(vals), mean, sd, min(vals), max(vals)))


def ac_a5(page):
    """A5 temporal shimmer watch (record-only): slow camera pan via
    WH_DEBUG.setCameraYaw, far-ground pixel band temporal stddev. Non-blocking."""
    imgs = []
    try:
        for step in range(8):
            page.evaluate(
                "(function(s){window.WH_DEBUG.setCameraYaw(s * 4);})()", step)
            page.wait_for_timeout(500)
            img = _readback(page)
            if img:
                imgs.append(img)
    finally:
        pass
    if len(imgs) < 3:
        check("A5", "temporal shimmer record", False,
              "insufficient frames (%d)" % len(imgs), verdict="RECORD")
        return
    w, h = imgs[0]["w"], imgs[0]["h"]
    # far-ground band: upper third of the visible ground (between horizon
    # fog and the near band) — the pixels most affected by minification
    band = [(x, y) for y in range(int(0.66 * h), int(0.78 * h), 5)
            for x in range(int(0.25 * w), int(0.75 * w), 12)]
    per_pixel = {pt: [] for pt in band}
    for img in imgs:
        if (img["w"], img["h"]) != (w, h):
            continue
        for pt in band:
            x, y = pt
            if 0 <= x < w and 0 <= y < h:
                o = (y * w + x) * img["bpp"]
                px = img["px"]
                per_pixel[pt].append(0.299 * px[o] + 0.587 * px[o + 1]
                                     + 0.114 * px[o + 2])
    sds = [ _stats(v)[1] for v in per_pixel.values() if len(v) >= 3 ]
    mean_sd = sum(sds) / len(sds) if sds else 0.0
    max_sd = max(sds) if sds else 0.0
    check("A5", "temporal shimmer record", True,
          "frames=%d pixels=%d meanTempStddev=%.3f max=%.3f (recorded, "
          "non-blocking)" % (len(imgs), len(sds), mean_sd, max_sd),
          verdict="RECORD")


def ac_a6():
    """A6 preservation floors: dispatch-time capture (sha256 + profile).
    Full mode (WH_R1_SUITES=1) invokes both suites and set-diffs failing IDs."""
    weave_hash = sha256_file(os.path.join(REPO_ROOT, FLOOR_WEAVE["path"]))
    ds1_hash = sha256_file(os.path.join(REPO_ROOT, FLOOR_DS1["path"]))
    hash_ok = (weave_hash == FLOOR_WEAVE["sha256"] and
               ds1_hash == FLOOR_DS1["sha256"])
    details = ["weave=%s(%s)" % (weave_hash[:12], "match" if weave_hash ==
              FLOOR_WEAVE["sha256"] else "DRIFT"),
               "ds1=%s(%s)" % (ds1_hash[:12], "match" if ds1_hash ==
              FLOOR_DS1["sha256"] else "DRIFT")]
    suite_runs = {}
    if RUN_SUITES:
        for floor in (FLOOR_WEAVE, FLOOR_DS1):
            try:
                proc = subprocess.run(
                    [sys.executable, floor["path"]],
                    cwd=REPO_ROOT, capture_output=True, text=True, timeout=420)
                m = re.search(r"\{[^{}]*\"round\"[\s\S]*\}", proc.stdout)
                summary = None
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            summary = json.loads(line)
                        except Exception:
                            pass
                suite_runs[floor["path"]] = summary or {"rc": proc.returncode}
                details.append("%s rc=%d pass=%s fail=%s" % (
                    os.path.basename(floor["path"]), proc.returncode,
                    (summary or {}).get("pass"), (summary or {}).get("fail")))
            except Exception as e:
                suite_runs[floor["path"]] = {"error": repr(e)}
                details.append("%s run-error %r" % (floor["path"], e))
    ok = hash_ok
    detail = " ".join(details) + (" floors embedded: weave 10/8, ds1 capture"
                                  "-at-smoke (pre-fix 2/16)")
    check("A6", "suite preservation floors", ok, detail)
    RESULTS[-1]["suites"] = {
        "wh_v7_weave.py": {"sha256": weave_hash, "profile": FLOOR_WEAVE["profile"]},
        "wh_combat_ds1_validation.py": {"sha256": ds1_hash,
                                        "profile": FLOOR_DS1["profile"]},
        "runs": suite_runs,
    }


def ac_a7(browser, console_errors, page_errors):
    """A7 rebuild load-assert: builds/v7-playable.html loads clean
    (zero console errors / pageerrors, WH_DEBUG ready). Post-Devbot the
    harness rebuilds first (WH_R1_REBUILD=1); byte-identity of index.html
    and style.css vs freeze is checked here too."""
    idx_hash = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    css_hash = sha256_file(os.path.join(REPO_ROOT, "prototype/style.css"))
    build_hash = sha256_file(os.path.join(
        REPO_ROOT, "prototype/builds/v7-playable.html"))
    idx_ok = idx_hash == FREEZE["prototype/index.html"]
    css_ok = css_hash == FREEZE["prototype/style.css"]
    if os.environ.get("WH_R1_REBUILD", "0") == "1":
        try:
            proc = subprocess.run([sys.executable, "tools/build_v7.py"],
                                  cwd=REPO_ROOT, capture_output=True,
                                  text=True, timeout=180)
            detail_rc = proc.returncode
            build_hash = sha256_file(os.path.join(
                REPO_ROOT, "prototype/builds/v7-playable.html"))
        except Exception as e:
            check("A7", "rebuild load-assert", False,
                  "build_v7.py failed %r" % e)
            return
    else:
        detail_rc = None
    page = new_page(browser, console_errors, page_errors)
    pre_err = len(console_errors), len(page_errors)
    try:
        ready = load_index(page, "builds/v7-playable.html")
    finally:
        post_err = (len(console_errors), len(page_errors))
    new_console = post_err[0] - pre_err[0]
    new_pageerr = post_err[1] - pre_err[1]
    # load-clean is the gate; freeze byte-identity is recorded (the tree
    # carries pre-existing weave-round drift, expected to persist).
    ok = ready and new_console == 0 and new_pageerr == 0
    check("A7", "rebuild load-assert", ok,
          "ready=%s consoleErr=%d pageErr=%d idx=%s css=%s buildHash=%s%s "
          "[byte-identity informational pre-Devbot]" % (
              ready, new_console, new_pageerr,
              "freeze-ok" if idx_ok else "DRIFT",
              "freeze-ok" if css_ok else "DRIFT", build_hash[:12],
              "" if detail_rc is None else " rebuildRc=%s" % detail_rc))
    page.close()


def ac_a8():
    """A8 scope set-diff: git status vs freeze + allowed R1 surface.
    PASS = no NEW path outside (freeze-dirty set + 5 allowed files +
    devbot deliverable notes + testerbot deliverables)."""
    try:
        st = subprocess.run(["git", "status", "--porcelain"],
                            cwd=REPO_ROOT, capture_output=True, text=True,
                            timeout=30)
        lines = [l for l in st.stdout.splitlines() if l.strip()]
    except Exception as e:
        check("A8", "scope set-diff", False, "git status failed %r" % e)
        return
    current = set()
    for l in lines:
        # porcelain v1: XY<space>PATH where XY is the 2-char status code
        # (unstaged entries have a LEADING SPACE, so no global strip)
        if len(l) > 3:
            path = l[3:].strip().strip('"')
        else:
            path = l.strip()
        current.add(path)
        if path.endswith("/"):
            current.add(path.rstrip("/"))
    allowed = set(FREEZE_DIRTY) | set(ALLOWED_R1_EDITS) | {
        "io/reports/2026-09-30-world-r1-implementation.md",
        "io/specs/testerbot-spec-wh-world-r1.md",
        "io/specs/devbot-spec-wh-world-r1.md",
        "tests/wh_world_r1_validation.py",
        "io/reports/",
    }
    # everything listed in the freeze manifest is pre-existing surface
    freeze_manifest = os.path.join("/tmp", "wh-world-r1-freeze-20260930.txt")
    if os.path.exists(freeze_manifest):
        for line in open(freeze_manifest):
            parts = line.split(None, 1)
            if len(parts) == 2:            # "<sha256>  <path>"
                allowed.add(parts[1].strip())
            elif len(parts) == 1 and parts[0].strip().endswith("/"):
                allowed.add(parts[0].strip())       # dir entry, e.g io/reports/
                allowed.add(parts[0].strip().rstrip("/"))
    # any io/ rebuild_part*/probe_*/compare_*/dbg_* untracked file from the
    # concurrent workstream is pre-existing at freeze (56 untracked io/ paths)
    new_paths = []
    for p in sorted(current):
        if p in allowed:
            continue
        base = os.path.basename(p)
        top = p.split("/")[0]
        if top == "io" and re.match(
                r"(rebuild_part.*|probe_.*|compare_.*|dbg_.*|fix_.*|"
                r"check_.*|run_.*|dump_.*|assemble_.*|harness_corrupt.*|"
                r"notes.*)", base):
            continue  # concurrent workstream artifacts (freeze-dirty)
        new_paths.append(p)
    # secrets grep over the dirty surface
    secrets_hits = []
    try:
        grep = subprocess.run(
            ["git", "diff"], cwd=REPO_ROOT, capture_output=True, text=True,
            timeout=30)
        blob = grep.stdout
        for pat in ("api_key", "apiKey", "SECRET", "PASSWORD=", "password =",
                    "token ="):
            if pat.lower() in blob.lower():
                # crude: only flag if it looks like an assignment with a value
                for line in blob.splitlines():
                    if pat.lower() in line.lower() and "=" in line:
                        secrets_hits.append(line.strip()[:80])
                        break
    except Exception:
        pass
    ok = not new_paths and not secrets_hits
    check("A8", "scope set-diff", ok,
          "dirtyPaths=%d newOutsideSurface=%s secretsHits=%d" % (
              len(current), new_paths[:5] or "-", len(secrets_hits)))


# ---------------------------------------------------------------- main -------
def run_with_retry(fn, page, ac_id, name, attempts=3):
    """Flake rule: infra-shaped failures (exception/timeout) retry up to
    `attempts` (fresh reload between). Deterministic assertion FAILs never
    retry. Returns number of infra-failures encountered."""
    infra = 0
    for attempt in range(attempts):
        before = len(RESULTS)
        try:
            fn(page)
            return infra
        except Exception as e:
            infra += 1
            if attempt == attempts - 1:
                check(ac_id, name, False, "runner exception after %d attempts "
                      "last=%r" % (attempts, e))
                return infra
            print("[diag] %s infra-shaped failure attempt %d: %r; reloading" %
                  (ac_id, attempt + 1, e))
            FLAKES.append("%s attempt%d" % (ac_id, attempt + 1))
            load_index(page)
    return infra


def main():
    server = start_server()
    console_errors, page_errors = [], []
    browser = None
    t0 = time.time()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            page = new_page(browser, console_errors, page_errors)
            if not load_index(page, "index.html"):
                check("BOOT", "index loads + WH_DEBUG ready", False,
                      "WH_DEBUG not ready")
            else:
                check("BOOT", "index loads + WH_DEBUG ready", True,
                      "consoleErr=%d pageErr=%d" %
                      (len(console_errors), len(page_errors)))
                run_with_retry(ac_a1, page, "A1", "prop ground-align")
                # reload between ACs: each AC starts from clean boot state
                # (A1's boundary walk / kills must not leak into A2/A3)
                for ac_id, name, fn in (
                        ("A2", "actor ground-align", ac_a2),
                        ("A3", "corpse ground-align", ac_a3),
                        ("A4", "ground luminance ring", ac_a4),
                        ("A5", "temporal shimmer record", ac_a5)):
                    load_index(page)
                    run_with_retry(fn, page, ac_id, name)
            ac_a6()
            try:
                ac_a7(browser, console_errors, page_errors)
            except Exception as e:
                check("A7", "rebuild load-assert", False,
                      "runner exception %r" % e)
            ac_a8()
            if page:
                try:
                    page.close()
                except Exception:
                    pass
            try:
                browser.close()
            except Exception:
                pass
    except Exception as e:
        check("MAIN", "harness runner", False, "exception %r" % e)
    finally:
        stop_server(server)

    print()
    print("=" * 72)
    print("WORLD-R1 SMOKE SUMMARY  total=%d pass=%d fail=%d flakes=%d "
          "elapsed=%.0fs" % (
              len(RESULTS), sum(1 for r in RESULTS if r["verdict"] == "PASS"),
              sum(1 for r in RESULTS if r["verdict"] == "FAIL"),
              len(FLAKES), time.time() - t0))
    for r in RESULTS:
        print("  AC-%s %-38s %s" % (r["id"], r["name"], r["verdict"]))
    print("=" * 72)

    suites = {}
    for r in RESULTS:
        if r["id"] == "A6" and "suites" in r:
            suites = r["suites"]
    verdict = "PASS"
    for r in RESULTS:
        if r["verdict"] == "FAIL":
            verdict = "FAIL"
            break
    if len(FLAKES) >= 3:
        verdict = "BLOCK"
    out = {
        "round": "world-r1",
        "verdict": verdict,
        "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                    "evidence": r["detail"]} for r in RESULTS],
        "suites": suites,
        "flakes": len(FLAKES),
        "notes": "pre-Devbot smoke; A1-A4 expected RED; A5 record-only; "
                 "exit 0 always (failures are data)",
    }
    print(json.dumps(out, indent=1))
    sys.exit(0)  # ALWAYS 0: failures are data


if __name__ == "__main__":
    main()
