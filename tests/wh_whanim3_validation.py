#!/usr/bin/env python3
"""Witch Hunter whanim3 "swing sight" validation harness (Testerbot).

Round: whanim3 (B1 blade orientation + B2 CSP texture intake + B3 build
freshness). Spec pair: io/specs/devbot-spec-whanim3-swingsight.md (IO) +
io/specs/testerbot-spec-whanim3-swingsight.md (Testerbot valspec, THIS
harness's contract).

Laws (ds1/weave rounds, valspec section 1):
- Playwright sync API, headless chromium --enable-unsafe-swiftshader.
- Organic input: real page.mouse.click attacks only. WH_DEBUG reads fine;
  WH_DEBUG writes (teleport/setCameraYaw/setStamina/breakLockOn) are SETUP
  acts, never a PASS basis.
- Window-buffer samplers ONLY: page code writes rows to window.__IO_*_ROWS
  and the install evaluate returns INSTANTLY. No pending-promise samplers.
- Page-time semantics: stages/elapsed from the game FSM, never wall-clock.

Usage:
  python3 tests/wh_whanim3_validation.py              # full run (AC1-AC6)
  WH_AC_SKIP_REGRESS=1 python3 tests/wh_whanim3_validation.py   # skip AC4
Exit code 0 only if every AC passes. Artifacts to /tmp/whanim3-artifacts/.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGIN = os.environ.get("WH_BASE_ROOT", "http://127.0.0.1:8792/witchhunter/")
PT_ROUTE = os.environ.get("WH_PLAYTEST_ROUTE", "http://127.0.0.1:8787/playtest/")
ENV_FILE = os.environ.get("WH_WEBUI_ENV", "/workspace/hermes-webui/.env")
BUILD_PATH = "builds/v7-playable.html"
BUILD_FILE = os.path.join(REPO_ROOT, "prototype", "builds", "v7-playable.html")
ART_DIR = os.environ.get("WHANIM3_ARTIFACTS", "/tmp/whanim3-artifacts")
BASE_HEAD = "dc697ce"

RESULTS = []     # (ac, name, ok, detail)
CRASHES = []     # unexpected exceptions / pageerrors at runner level
DIAG = []


def note(msg):
    DIAG.append(msg)
    print("[diag] %s" % msg)


def check(ac, name, ok, detail=""):
    ok = bool(ok)
    RESULTS.append((ac, name, ok, detail))
    print("AC%s %s => %s %s" % (ac, name, "PASS" if ok else "FAIL", detail))
    return ok


def sub(ac, name, ok, detail=""):
    """Record a sub-check without it counting as a top-level AC row."""
    ok = bool(ok)
    RESULTS.append(("%s.%s" % (ac, name), name, ok, detail))
    print("  AC%s-%s => %s %s" % (ac, name, "PASS" if ok else "FAIL", detail))
    return ok


def wrap_pi(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


# ---------------------------------------------------------------- helpers ---

def wait_ready(page, timeout_s=40, settle_ms=2500):
    """Wait until WH_DEBUG is live; settle for asset preload."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            ok = page.evaluate(
                "(function(){try{return typeof window.WH_DEBUG==='object' && "
                "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
                "!!window.WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()")
            if ok:
                page.wait_for_timeout(settle_ms)
                return True
        except Exception:
            pass
        page.wait_for_timeout(400)
    return False


def click_center(page):
    vp = page.viewport_size or {"width": 640, "height": 400}
    page.mouse.click(vp["width"] // 2, vp["height"] // 2)


def drain_rows(page, var):
    try:
        return page.evaluate("(window.%s || [])" % var) or []
    except Exception as e:
        note("drain %s: %r" % (var, e))
        return []


def stop_sampler(page, var):
    try:
        page.evaluate("(function(){var s=window.%s; if(s&&s.stop) s.stop(); return true;})()" % var)
    except Exception as e:
        note("stop %s: %r" % (var, e))


def webui_password():
    try:
        txt = open(ENV_FILE).read()
        m = re.search(r"^HERMES_WEBUI_PASSWORD=(.*)$", txt, re.M)
        return m.group(1).strip() if m else None
    except Exception:
        return None


# ------------------------------------------------------------ AC1 samplers --

# Structural blade-axis sampler: per rAF row for the PLAYER's sword.
# Blade identified structurally ONCE (narrow transverse half = blade),
# then per frame: axis = normalize(tipWorld - hiltCentroidWorld).
# Rows land in window.__IO_W3A_ROWS; install returns INSTANTLY.
SWORD_SAMPLER = r"""
(function(){
  if (window.__IO_W3A) { try { window.__IO_W3A.stop(); } catch(x){} }
  var out = {rows: [], prep: null};
  window.__IO_W3A_ROWS = out.rows;
  window.__IO_W3A = out;
  var running = true;
  function prepSword(sword){
    var pts = [];
    sword.traverse(function(o){
      if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return;
      var pos = o.geometry.attributes.position;
      var v = new THREE.Vector3();
      var toSword = new THREE.Matrix4().copy(sword.matrixWorld).invert().multiply(o.matrixWorld);
      for (var i=0;i<pos.count;i++){ v.fromBufferAttribute(pos,i).applyMatrix4(toSword); pts.push(v.clone()); }
    });
    if (pts.length < 10) return null;
    var ys = pts.map(function(p){return p.y;});
    var lo = Math.min.apply(null,ys), hi = Math.max.apply(null,ys), mid=(lo+hi)/2;
    function span(arr,k){var a=arr.map(function(p){return p.getComponent(k);});
      return Math.max.apply(null,a)-Math.min.apply(null,a);}
    var top = pts.filter(function(p){return p.y>=mid;});
    var bot = pts.filter(function(p){return p.y<mid;});
    var bladeAtPlusY = (span(top,0)+span(top,2)) < (span(bot,0)+span(bot,2));
    var blade = bladeAtPlusY ? top : bot;
    var hilt  = bladeAtPlusY ? bot : top;
    var tipPt = null, ext = -1;
    blade.forEach(function(p){
      var e = Math.abs(p.y - mid);
      if (e > ext) { ext = e; tipPt = p; }
    });
    var hiltC = new THREE.Vector3();
    hilt.forEach(function(p){hiltC.add(p);});
    hiltC.divideScalar(hilt.length);
    return {tipPt: tipPt, hiltC: hiltC, bladeAtPlusY: bladeAtPlusY, n: pts.length};
  }
  function tick(now){
    if (!running) return;
    try {
      var p = window.WH_DEBUG.getPlayer();
      if (p && p.body) {
        var hand = p.body.getObjectByName('R_Hand');
        if (hand) {
          var sword = null;
          hand.children.forEach(function(c){ if (!sword && !c.isBone) sword = c; });
          if (sword) {
            if (!out.prep) out.prep = prepSword(sword);
            if (out.prep) {
              sword.updateMatrixWorld(true); hand.updateMatrixWorld(true);
              var tipW = out.prep.tipPt.clone().applyMatrix4(sword.matrixWorld);
              var hiltW = out.prep.hiltC.clone().applyMatrix4(sword.matrixWorld);
              var hw = new THREE.Vector3(); hand.matrixWorld.decompose(hw, new THREE.Quaternion(), new THREE.Vector3());
              var axis = tipW.clone().sub(hiltW).normalize();
              var facing = new THREE.Vector3(Math.sin(p.yaw), 0, Math.cos(p.yaw));
              var elapsed = window.WH_CONFIG.player.attackDuration - p.attackTimer;
              out.rows.push({t:+(now/1000).toFixed(3), elapsed:+elapsed.toFixed(3),
                st: p.getAttackStage ? p.getAttackStage() : null,
                yaw:+p.yaw.toFixed(3),
                axisDot:+axis.dot(facing).toFixed(4),
                axisUp:+axis.y.toFixed(4),
                sdTip:+tipW.clone().sub(hw).dot(facing).toFixed(3),
                sdHilt:+hiltW.clone().sub(hw).dot(facing).toFixed(3),
                attacking: !!p.attacking});
            }
          } else if (!out.prep) {
            out.rows.push({t:+(now/1000).toFixed(3), st:null, err:'no sword on R_Hand'});
          }
        }
      }
    } catch (x) { out.rows.push({err: String(x)}); }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  out.stop = function(){ running = false; };
  return true;
})"""


def ac1_player_blade(page):
    """AC1: player sword blade leads the swing (8792 clean origin)."""
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    try:
        page.goto(ORIGIN, wait_until="load", timeout=30000)
        if not wait_ready(page):
            return check(1, "player-blade-orientation", False, "page never ready")
        # setup acts (never assertion basis)
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.evaluate("window.WH_DEBUG.breakLockOn && window.WH_DEBUG.breakLockOn()")
        page.evaluate("window.WH_DEBUG.setStamina && window.WH_DEBUG.setStamina(100)")
        page.wait_for_timeout(300)
        page.evaluate(SWORD_SAMPLER)          # INSTANT return
        page.wait_for_timeout(300)
        idle_rows = [r for r in drain_rows(page, "__IO_W3A_ROWS") if r.get("st") is None and "err" not in r]
        # organic attack chain: 4 real clicks
        for _ in range(4):
            page.evaluate("window.WH_DEBUG.setStamina && window.WH_DEBUG.setStamina(100)")
            click_center(page)
            page.wait_for_timeout(1000)
        page.wait_for_timeout(300)
        try:
            page.screenshot(path=os.path.join(ART_DIR, "whanim3-strike.png"))
        except Exception as e:
            note("screenshot: %r" % e)
        stop_sampler(page, "__IO_W3A")
        rows = [r for r in drain_rows(page, "__IO_W3A_ROWS") if "err" not in r]
        if not rows:
            return check(1, "player-blade-orientation", False, "sampler produced no rows")
        band = [r for r in rows if r.get("st") == "strike" or
                (r.get("st") == "recover" and r.get("elapsed", 1) <= 0.32)]
        n = len(band)
        if n < 4:
            check(1, "player-blade-orientation", False,
                  "strike-band rows=%d (<4): sampler under-sampled" % n)
            return
        dots = [r["axisDot"] for r in band]
        a_ok = (min(dots) >= 0.4) and (sum(dots) / len(dots) >= 0.5)
        sub(1, "a", a_ok,
            "strike-band axisDot n=%d min=%+.4f mean=%+.4f vals=%s (gate >= +0.4 all, mean >= +0.5)" %
            (n, min(dots), sum(dots) / len(dots),
             ",".join("%+.3f(el %.2f)" % (r["axisDot"], r["elapsed"]) for r in band)))
        tip_lead = all(r["sdTip"] > r["sdHilt"] for r in band)
        sub(1, "b", tip_lead,
            "sdTip=%s sdHilt=%s (tip must be forward-most end)" %
            ([r["sdTip"] for r in band], [r["sdHilt"] for r in band]))
        idle_ok = False
        idle_deg = None
        if idle_rows:
            axis_up = idle_rows[-1]["axisUp"]
            idle_deg = math.degrees(math.acos(max(-1, min(1, abs(axis_up)))))
            idle_ok = abs(idle_deg - 26.3) <= 30.0
        sub(1, "c", idle_ok,
            "idle blade off-vertical=%.1f deg (baseline 26.3, tolerance +-30)" % (idle_deg
              if idle_deg is not None else -1))
        crash_ok = len(errors) == 0
        sub(1, "d", crash_ok, "pageerrors=%s" % (errors[:2],))
        ok = a_ok and tip_lead and idle_ok and crash_ok
        check(1, "player-blade-orientation", ok,
              "strike axisDot min=%+.4f mean=%+.4f (n=%d) tipLeads=%s idleDeg=%s pageerrors=%d" %
              (min(dots), sum(dots) / len(dots), n, tip_lead,
               ("%.1f" % idle_deg) if idle_deg is not None else "?", len(errors)))
    except Exception as e:
        check(1, "player-blade-orientation", False, "exception %r" % e)


# ------------------------------------------------------------ AC2 samplers --

AXE_SAMPLER = r"""
(function(){
  if (window.__IO_W3B) { try { window.__IO_W3B.stop(); } catch(x){} }
  var out = {rows: []};
  window.__IO_W3B_ROWS = out.rows;
  window.__IO_W3B = out;
  var running = true;
  function prepAxe(axe){
    var pts = [];
    axe.traverse(function(o){
      if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return;
      var pos = o.geometry.attributes.position;
      var v = new THREE.Vector3();
      var toAxe = new THREE.Matrix4().copy(axe.matrixWorld).invert().multiply(o.matrixWorld);
      for (var i=0;i<pos.count;i++){ v.fromBufferAttribute(pos,i).applyMatrix4(toAxe); pts.push(v.clone()); }
    });
    if (pts.length < 10) return null;
    var ys = pts.map(function(p){return p.y;});
    var lo = Math.min.apply(null,ys), hi = Math.max.apply(null,ys), mid=(lo+hi)/2;
    function span(arr,k){var a=arr.map(function(p){return p.getComponent(k);});
      return Math.max.apply(null,a)-Math.min.apply(null,a);}
    var top = pts.filter(function(p){return p.y>=mid;});
    var bot = pts.filter(function(p){return p.y<mid;});
    // axe HEAD is the wide half (blade mass), haft/butt the narrow half
    var headAtPlusY = (span(top,0)+span(top,2)) > (span(bot,0)+span(bot,2));
    var head = headAtPlusY ? top : bot;
    var headC = new THREE.Vector3();
    head.forEach(function(p){headC.add(p);});
    headC.divideScalar(head.length);
    return {headC: headC, n: pts.length, headAtPlusY: headAtPlusY};
  }
  var prep = null;
  function tick(now){
    if (!running) return;
    try {
      var e0 = window.WH_DEBUG.getEnemy(0);
      if (e0 && e0.ref) {
        var e = e0.ref;
        var p = window.WH_DEBUG.getPlayer();
        if (e.fsm === 'attack' && e.body && p) {
          var hand = e.body.getObjectByName('R_Hand');
          if (hand) {
            var axe = null;
            hand.children.forEach(function(c){ if (!axe && !c.isBone) axe = c; });
            if (axe) {
              if (!prep) prep = prepAxe(axe);
              if (prep) {
                axe.updateMatrixWorld(true); hand.updateMatrixWorld(true);
                var headW = prep.headC.clone().applyMatrix4(axe.matrixWorld);
                var hw = new THREE.Vector3(); hand.matrixWorld.decompose(hw, new THREE.Quaternion(), new THREE.Vector3());
                var dx = p.pos.x - e.pos.x, dz = p.pos.z - e.pos.z;
                var len = Math.hypot(dx,dz) || 1;
                var facing = new THREE.Vector3(dx/len, 0, dz/len);
                var hd = headW.clone().sub(hw);
                var bone = e.body.getObjectByName('R_UpperArm');
                out.rows.push({t:+(now/1000).toFixed(3), ph:e.attackPhase,
                  phT:+(e.attackPhaseT||0).toFixed(3),
                  headDot:+hd.clone().normalize().dot(facing).toFixed(4),
                  headH:+(headW.y - hw.y).toFixed(4),
                  wLocal: bone ? +bone.quaternion.w.toFixed(4) : null});
              }
            }
          }
        }
      }
    } catch (x) { out.rows.push({err: String(x)}); }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  out.stop = function(){ running = false; };
  return true;
})"""


def ac2_bandit_axe(page):
    """AC2: bandit axe orientation during enemy fsm=='attack' (measured-correct
    => verify-only; the harness never decides the fix, it re-measures)."""
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    try:
        page.goto(ORIGIN, wait_until="load", timeout=30000)
        if not wait_ready(page):
            return check(2, "bandit-axe-orientation", False, "page never ready")
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.wait_for_timeout(300)
        page.evaluate(AXE_SAMPLER)
        # organic: the bandit aggros and attacks on its own; just survive.
        # keep hp topped so the run cannot die mid-census (setup act)
        for _ in range(26):
            page.evaluate("window.WH_DEBUG.useConsumable && window.WH_DEBUG.getPlayer().hp < 60 && window.WH_DEBUG.useConsumable(0)")
            page.wait_for_timeout(1000)
        stop_sampler(page, "__IO_W3B")
        rows = [r for r in drain_rows(page, "__IO_W3B_ROWS") if "err" not in r]
        if not rows:
            return check(2, "bandit-axe-orientation", False,
                         "no attack rows: bandit never entered fsm=='attack'")
        act = [r for r in rows if r["ph"] == "active"]
        # group active rows into cycles on >800ms page-time gaps
        cycles, cur = [], []
        last_t = None
        for r in act:
            if last_t is not None and r["t"] - last_t > 0.8 and cur:
                cycles.append(cur)
                cur = []
            cur.append(r)
            last_t = r["t"]
        if cur:
            cycles.append(cur)
        # windup groups for the telegraph check
        windups, cur, prev_ph = [], [], None
        for r in rows:
            if r["ph"] == "windup" and prev_ph != "windup" and cur:
                windups.append(cur)
                cur = []
            if r["ph"] == "windup":
                cur.append(r)
            prev_ph = r["ph"]
        if cur:
            windups.append(cur)
        if not cycles:
            return check(2, "bandit-axe-orientation", False,
                         "attack rows=%d but no active-phase rows captured" % len(rows))
        # AC2a: orientation at the chop's leading edge (phT <= 0.05) + down-chop
        entry = [c[0] for c in cycles if c[0]["phT"] <= 0.05]
        entry_ok = len(entry) >= 2 and all(r["headDot"] >= 0.3 for r in entry)
        drop_ok = all(
            (c[0]["headH"] - c[-1]["headH"]) >= 0.5 for c in cycles if len(c) >= 2)
        sub(2, "a", entry_ok and drop_ok,
            "cycles=%d entryHeadDot=%s headH %s->%s (gate: entry >= +0.3 all cycles, drop >= 0.5)" %
            (len(cycles), [r["headDot"] for r in entry],
             [round(c[0]["headH"], 2) for c in cycles],
             [round(c[-1]["headH"], 2) for c in cycles]))
        # AC2b: windup telegraph band (wLocal 0.87->0.68 style, monotonic)
        tel_ok = False
        tel_detail = "no windup groups"
        # full windups only (>=10 rows): partial groups at sampler edges are
        # incomplete telegraphs, not evidence (valspec AMENDMENT A3).
        stats = []
        for w in windups:
            ws = [r["wLocal"] for r in w if r.get("wLocal") is not None]
            if len(ws) >= 10:
                desc = sum(1 for a, b in zip(ws, ws[1:]) if b < a - 1e-4)
                stats.append((ws[0], ws[-1], desc, len(ws) - 1))
        if stats:
            first_ok = all(s[0] >= 0.80 for s in stats)
            last_ok = all(s[1] <= 0.70 for s in stats)
            # trend gate: >=80% of consecutive steps descend (12fps frame
            # jitter admits 1-2 up-wiggles; endpoints carry the telegraph)
            mono_ok = all(s[2] >= 0.8 * s[3] for s in stats)
            tel_ok = first_ok and last_ok and mono_ok
            tel_detail = "wLocal %s mono=%s (gate: >=0.80 -> <=0.70, >=80%% steps)" % (
                [(round(s[0], 3), round(s[1], 3)) for s in stats],
                [(s[2], s[3]) for s in stats])
        else:
            tel_detail = "no full windup groups (>=10 rows)"
        sub(2, "b", tel_ok, tel_detail)
        ok = entry_ok and drop_ok and tel_ok and not errors
        check(2, "bandit-axe-orientation", ok,
              "entryHeadDot=%s drop=%s telegraph=%s pageerrors=%d rows=%d" %
              ([r["headDot"] for r in entry], drop_ok, tel_ok, len(errors), len(rows)))
    except Exception as e:
        check(2, "bandit-axe-orientation", False, "exception %r" % e)


# ------------------------------------------------------------------- AC3 ----

BODY_MATS_JS = r"""
(function(){
  var p = window.WH_DEBUG.getPlayer();
  if (!p || !p.body) return {err:'no body'};
  var found = [];
  p.body.traverse(function(o){
    if (o.isSkinnedMesh && o.material) {
      var mats = Array.isArray(o.material)?o.material:[o.material];
      mats.forEach(function(m){
        if (!m) return;
        var w = 0;
        if (m.map && m.map.image) {
          w = m.map.image.width || m.map.image.videoWidth || m.map.image.naturalWidth || 0;
        }
        found.push({hasMap: !!m.map, w: w});
      });
    }
  });
  return {mats: found};
})"""


def ac3_csp_texture(pw_browser):
    """AC3: 8787 playtest route — CSP census zero + textures present."""
    password = webui_password()
    if not password:
        return check(3, "csp-texture-intake-8787", False,
                     "no HERMES_WEBUI_PASSWORD in %s" % ENV_FILE)
    errors = []
    page = pw_browser.new_page(viewport={"width": 640, "height": 400})
    try:
        page.on("pageerror", lambda e: errors.append("PAGEERR " + str(e)))

        def on_console(m):
            if m.type == "error":
                errors.append(m.text)
        page.on("console", on_console)
        page.goto(PT_ROUTE, wait_until="load", timeout=30000)
        if "/login" in page.url:
            res = page.evaluate(
                "(async function(pw){try{var r=await fetch('/api/auth/login',"
                "{method:'POST',headers:{'Content-Type':'application/json'},"
                "credentials:'include',body:JSON.stringify({password:pw})});"
                "return {status:r.status, body:await r.text()};}catch(e){return {err:String(e)};}})",
                password)
            if not res or res.get("status") != 200:
                return check(3, "csp-texture-intake-8787", False,
                             "8787 login failed: %s" % (res,))
            page.goto(PT_ROUTE, wait_until="load", timeout=30000)
        if not wait_ready(page, timeout_s=40, settle_ms=0):
            return check(3, "csp-texture-intake-8787", False,
                         "8787 page never ready (post-login)")
        # full asset load + 10s gameplay hold
        page.wait_for_timeout(10000)
        click_center(page)
        page.wait_for_timeout(1500)
        try:
            page.screenshot(path=os.path.join(ART_DIR, "whanim3-playtest-8787.png"))
        except Exception as e:
            note("screenshot: %r" % e)
        # AC3a: CSP-violation census
        csp = [t for t in errors if re.search(
            r"Content Security Policy|Refused to connect|CSP directive", t)]
        a_ok = len(csp) == 0
        sub(3, "a", a_ok,
            "CSP-violation console errors=%d (gate 0) sample=%s" %
            (len(csp), csp[:2]))
        # AC3b: material map readback
        mats = page.evaluate(BODY_MATS_JS) or {}
        mat_list = mats.get("mats", [])
        b_ok = bool(mat_list) and all(m["hasMap"] and m["w"] >= 512 for m in mat_list)
        sub(3, "b", b_ok,
            "body materials=%s (gate: every map present, width >= 512)" % (mat_list,))
        # AC3c: zero stand-ins + live clips
        stand = page.evaluate(
            "(function(){var out=[];Object.keys(window.WH_ASSETS.MANIFEST).forEach("
            "function(n){if(window.WH_ASSETS.isFailed(n)) out.push(n);});"
            "return {failed: out, clips: {playerBody: window.WH_ASSETS.getClips('playerBody').length,"
            "banditBody: window.WH_ASSETS.getClips('banditBody').length,"
            "ghoulBody: window.WH_ASSETS.getClips('ghoulBody').length}};})()")
        c_ok = (not stand.get("failed")) and all(
            v == 6 for v in (stand.get("clips") or {}).values())
        sub(3, "c", c_ok, "standins/failed=%s clips=%s" %
            (stand.get("failed"), stand.get("clips")))
        pageerrors = [t for t in errors if t.startswith("PAGEERR")]
        ok = a_ok and b_ok and c_ok and not pageerrors
        check(3, "csp-texture-intake-8787", ok,
              "cspErrors=%d mapsOk=%s zeroStandins=%s pageerrors=%d" %
              (len(csp), b_ok, c_ok, len(pageerrors)))
    except Exception as e:
        check(3, "csp-texture-intake-8787", False, "exception %r" % e)
    finally:
        try:
            page.close()
        except Exception:
            pass


# ------------------------------------------------------------------- AC4 ----

def ac4_regression():
    """AC4: regression floor — ds1 18/18, weave 18/18, v2 asset audit, v3.
    Suites run at their OWN default origins (the whanim2-verified floor
    configuration): ds1 self-manages 8791; v2/v3 sweep both origins
    internally. No WH_BASE_* overrides: the floor is the suites' own
    verdicts, apples-to-apples pre and post build."""
    env = dict(os.environ)
    env.pop("WH_BASE_ROOT", None)
    env.pop("WH_BASE_PROXY", None)
    suites = [
        ("ds1", ["python3", "tests/wh_combat_ds1_validation.py"],
         lambda out: ("total=18" in out and "pass=18" in out and "fail=0" in out)),
        ("weave", ["python3", "tests/wh_v7_weave.py"],
         lambda out: ("18/18" in out)),
        ("v2", ["python3", "tests/wh_v2_verify.py"],
         lambda out: ("V2 VERIFY: PASS" in out)),
        ("v3", ["python3", "tests/wh_v3_anim_probes.py"],
         lambda out: ("V3 ANIM PROBES: PASS" in out)),
    ]
    all_ok = True
    for tag, cmd, summary_ok in suites:
        try:
            r = subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True,
                               text=True, timeout=900)
            out = r.stdout + r.stderr
            with open(os.path.join(ART_DIR, "whanim3-regress-%s.log" % tag), "w") as f:
                f.write(out)
            s_line = ""
            for line in out.splitlines():
                if ("SMOKE SUMMARY" in line or "V7 WEAVE:" in line
                        or "V2 VERIFY:" in line or "V3 ANIM PROBES:" in line):
                    s_line = line.strip()
            ok = (r.returncode == 0) and summary_ok(out)
            sub(4, tag, ok, "exit=%d summary='%s'" % (r.returncode, s_line))
        except Exception as e:
            sub(4, tag, False, "runner exception %r" % e)
            ok = False
        all_ok = all_ok and ok
    check(4, "regression-floor", all_ok,
          "ds1+weave+v2+v3 must all be green (see sub-checks)")


# ------------------------------------------------------------------- AC5 ----

def ac5_build_freshness(page):
    """AC5: v7-playable.html fresh (byte-identical rebuild + hook greps + smoke)."""
    try:
        # 1. byte-identity: scratch rebuild with OUT patched to /tmp; ROOT must
        # stay the REPO (script computes ROOT from its own path, so patch it).
        os.makedirs(ART_DIR, exist_ok=True)
        scratch_src = os.path.join(ART_DIR, "build_v7_scratch.py")
        with open(os.path.join(REPO_ROOT, "tools", "build_v7.py")) as f:
            src = f.read()
        scratch_out = os.path.join(ART_DIR, "whanim3-v7-rebuilt.html")
        src = src.replace(
            "OUT = P / 'builds' / 'v7-playable.html'",
            "OUT = __import__('pathlib').Path(%r)" % scratch_out)
        src = src.replace(
            "ROOT = pathlib.Path(__file__).resolve().parent.parent   # repo root",
            "ROOT = pathlib.Path(%r)  # repo root (pinned by harness)" % REPO_ROOT)
        with open(scratch_src, "w") as f:
            f.write(src)
        r = subprocess.run(["python3", scratch_src], cwd=REPO_ROOT,
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(scratch_out):
            return check(5, "build-freshness", False,
                         "scratch rebuild failed: %s" % (r.stdout + r.stderr)[:200])
        def sha(p):
            import hashlib
            h = hashlib.sha256()
            with open(p, "rb") as f:
                h.update(f.read())
            return h.hexdigest()
        sha_disk = sha(BUILD_FILE)
        sha_new = sha(scratch_out)
        ident = sha_disk == sha_new
        sub(5, "ident", ident,
            "on-disk sha=%s scratch-rebuild sha=%s (byte-identity gate)" %
            (sha_disk[:16], sha_new[:16]))
        # 2. grep evidence
        with open(BUILD_FILE, errors="replace") as f:
            build_txt = f.read()
        has_anim = "CharacterAnim.prototype" in build_txt
        hook_ok = False
        for m in re.finditer(r"setURLModifier", build_txt):
            ctx = build_txt[max(0, m.start() - 200):m.start()]
            if "WHGLTFLoader" in ctx or "WH_ASSETS" in ctx or "blob:" in ctx:
                hook_ok = True
                break
        sub(5, "grep", has_anim and hook_ok,
            "CharacterAnim.prototype=%s intake-hook-context=%s" % (has_anim, hook_ok))
        # 3. build smoke on the clean origin
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(ORIGIN + BUILD_PATH, wait_until="load", timeout=30000)
        smoke_ok = False
        if wait_ready(page, timeout_s=40, settle_ms=1500):
            page.evaluate("window.WH_DEBUG.setStamina && window.WH_DEBUG.setStamina(100)")
            click_center(page)
            saw = False
            for _ in range(40):
                st = page.evaluate(
                    "(function(){try{return window.WH_DEBUG.getAttackStage();}catch(e){return null;}})()")
                if st:
                    saw = True
                    break
                page.wait_for_timeout(50)
            smoke_ok = saw and not errors
        sub(5, "smoke", smoke_ok,
            "build page boots, WH_DEBUG live, attack fired, pageerrors=%d" % len(errors))
        ok = ident and has_anim and hook_ok and smoke_ok
        check(5, "build-freshness", ok,
              "ident=%s CharacterAnim=%s hook=%s smoke=%s" %
              (ident, has_anim, hook_ok, smoke_ok))
    except Exception as e:
        check(5, "build-freshness", False, "exception %r" % e)


# ------------------------------------------------------------------- AC6 ----

FROZEN_DEBRIS = [
    "io/assemble_harness.py", "io/check_a14_cells.py", "io/check_harness.py",
    "io/compare_cocode.py", "io/compare_dumps.py", "io/compare_trees.py",
    "io/compare_trees2.py", "io/compare_trees3.py", "io/dbg_hp.py",
    "io/dbg_pyc_variant.py", "io/diff_dumps.py", "io/dump_facts.sh",
    "io/dump_new.py", "io/fix_dup.py", "io/fix_dup2.py", "io/fix_dupes.py",
    "io/fix_samplers.py", "io/harness_corrupt_20260930.py.bak",
    "io/note_part1_rewrite.txt", "io/probe_a36.py", "io/probe_click.py",
    "io/probe_consts.py", "io/probe_dis.py", "io/probe_isop.py",
    "io/probe_lines.py", "io/probe_matrix.py", "io/probe_module.py",
    "io/probe_pending.py", "io/probe_pyc.py", "io/probe_sampler.py",
    "io/probe_sampler2.py", "io/probe_sampler_js.py", "io/probe_tail.py",
    "io/rebuild_part1.py", "io/rebuild_part2.py", "io/rebuild_part3a.py",
    "io/rebuild_part3b.py", "io/rebuild_part3c.py", "io/rebuild_part4.py",
    "io/rebuild_part5a.py", "io/rebuild_part5b.py", "io/rebuild_part5c.py",
    "io/rebuild_part5d.py", "io/rebuild_part6.py", "io/rebuild_part7.py",
    "io/run_check.py", "io/run_harness.py",
    "io/reports/2026-10-01-playtest-why-no-anim-assessment.md",
    "io/specs/devbot-spec-whanim3-swingsight.md",
]

ALLOWED_PREFIXES = [
    "prototype/js/player.js", "prototype/js/enemy.js", "prototype/js/assets.js",
    "prototype/builds/v7-playable.html", "tests/wh_whanim3_validation.py",
    "io/specs/testerbot-spec-whanim3-swingsight.md", "io/reports/",
    "README.md", "io/__pycache__",
    # A3IO (2026-10-02, IO adjudication of the AC6 verdict): D4+D5
    # amendment-owned files - the ds1 spec amendment text + the ds1
    # harness socket-first re-target ordered by that amendment.
    "io/specs/devbot-spec-combat-ds1.md", "tests/wh_combat_ds1_validation.py",
]


def ac6_scope():
    """AC6: git census — no drift outside the allowed set."""
    try:
        st = subprocess.run(["git", "status", "--porcelain"],
                            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)
        lines = [l for l in st.stdout.splitlines() if l.strip()]
        changed = []
        for l in lines:
            path = l[3:].strip().strip('"')
            # rename entries: take the target side
            if " -> " in path:
                path = path.split(" -> ")[-1]
            if path.endswith("/"):
                path = path[:-1] + "/**"
            changed.append(path)
        drift = []
        for p in changed:
            if p in FROZEN_DEBRIS:
                continue
            if any(p == a or p.startswith(a) for a in ALLOWED_PREFIXES):
                continue
            drift.append(p)
        hard = [p for p in changed if re.match(
            r"^(prototype/js/(CONFIG|game|moveset|anim)\.js|prototype/vendor/|.*\.glb$)", p)]
        ok = (not drift) and (not hard)
        check(6, "scope-drift", ok,
              "changed=%d drift=%s hardViolations=%s" %
              (len(changed), drift[:8], hard[:8]))
    except Exception as e:
        check(6, "scope-drift", False, "exception %r" % e)


# ------------------------------------------------------------------ main ----

def main():
    os.makedirs(ART_DIR, exist_ok=True)
    skip_regress = os.environ.get("WH_AC_SKIP_REGRESS") == "1"
    t0 = time.time()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
        # AC1/AC2 share the origin; fresh pages each
        for fn in (ac1_player_blade,):
            page = browser.new_page(viewport={"width": 640, "height": 400})
            fn(page)
            page.close()
        for fn in (ac2_bandit_axe,):
            page = browser.new_page(viewport={"width": 640, "height": 400})
            fn(page)
            page.close()
        ac3_csp_texture(browser)
        if not skip_regress:
            ac4_regression()
        # AC5 uses a fresh page
        page = browser.new_page(viewport={"width": 640, "height": 400})
        ac5_build_freshness(page)
        page.close()
        browser.close()
    if skip_regress:
        note("AC4 skipped (WH_AC_SKIP_REGRESS=1): recorded as not-run, not PASS")
    ac6_scope()

    total = len([r for r in RESULTS if not isinstance(r[0], str) or "." not in str(r[0])])
    passed = len([r for r in RESULTS if ("." not in str(r[0])) and r[2]])
    failed = total - passed
    print()
    print("=" * 72)
    print("WHANIM3 SMOKE SUMMARY  total=%d pass=%d fail=%d crashes=%d" %
          (total, passed, failed, len(CRASHES)))
    for ac, name, ok, det in RESULTS:
        if "." not in str(ac):
            print("  AC%-6s %-32s %s" % (ac, name, "PASS" if ok else "FAIL"))
    print("ZERO CRASHES: %s" % ("YES" if not CRASHES else "NO -> %s" % CRASHES[:3]))
    print("=" * 72)
    verdict = {
        "round": "whanim3",
        "total": total,
        "pass": passed,
        "fail": failed,
        "crashes": len(CRASHES),
        "per_ac": [
            {"id": "AC%s" % ac, "name": name,
             "verdict": "PASS" if ok else "FAIL",
             "evidence": (det or "")[:400]}
            for ac, name, ok, det in RESULTS if "." not in str(ac)
        ],
        "sub_checks": [
            {"id": "AC%s" % ac, "verdict": "PASS" if ok else "FAIL",
             "evidence": (det or "")[:300]}
            for ac, name, ok, det in RESULTS if "." in str(ac)
        ],
        "runtime_s": round(time.time() - t0, 1),
        "skip_regress": skip_regress,
    }
    print(json.dumps(verdict, indent=1))
    with open(os.path.join(ART_DIR, "whanim3-verdict.json"), "w") as f:
        json.dump(verdict, f, indent=1)
    sys.exit(0 if (passed == total and not CRASHES) else 1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        CRASHES.append("main exception %r" % e)
        print("FATAL: %r" % e)
        sys.exit(2)