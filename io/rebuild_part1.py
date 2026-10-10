"""Witch Hunter combat Round A validation harness (combat-ds1-A).

ORGANIC-PATH LAW: every ACT is a real input (page.mouse / page.keyboard) or the
sanctioned live-handle enemy displacement (simulates the target moving, per the
AC input paths in io/specs/testerbot-spec-combat-ds1.md section 6). Setup helpers
(teleport, setCameraYaw, page load) are clearly separated from ACTs. This harness
NEVER writes player combat state (no comboIndex/attacking/hp/yaw pokes). All
reads are attribute-guarded: a PRE-Devbot build yields clean FAILs, zero crashes.

Run: python3 tests/wh_combat_ds1_validation.py   (WH_BASE_ROOT overrides base)
"""
from playwright.sync_api import sync_playwright
import json, math, os, subprocess, sys, time, urllib.request

BASE_ROOT = os.environ.get("WH_BASE_ROOT", "http://localhost:8791/")
BUILD_PATH = "builds/v7-playable.html"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

RESULTS = []
CRASHES = []
DIAGNOSTICS = []


def note(msg):
    DIAGNOSTICS.append(msg)
    print("[diag] %s" % msg)


def check(ac, name, ok, detail=""):
    """One AC = one check. Prints the verdict line and records it."""
    ok = bool(ok)
    RESULTS.append({"id": "AC-%s" % ac, "name": name, "ok": ok, "detail": detail})
    print("AC-%s %s => %s %s" % (ac, name, "PASS" if ok else "FAIL", detail))
    return ok


# ---------------------------------------------------------------- server ----
def start_server():
    """Start prototype/server.py; poll BASE_ROOT for HTTP 200 (max 15s)."""
    proc = None
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=os.path.join(REPO_ROOT, "prototype"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except OSError as e:
        note("server spawn failed (%r); assuming external server" % e)
    deadline = time.time() + 15.0
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(BASE_ROOT, timeout=1.0) as r:
                if r.status == 200:
                    return proc
        except Exception:
            pass
        time.sleep(0.3)
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


# ------------------------------------------------------------- helpers -----
def wait_ready(page, timeout_s=20):
    """goto BUILD_PATH; wait until WH_DEBUG and getPlayerPosition() both work."""
    try:
        page.goto(BASE_ROOT + BUILD_PATH, wait_until="load", timeout=30000)
    except Exception as e:
        note("goto failed: %r" % e)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            ok = page.evaluate(
                "(function(){try{return typeof window.WH_DEBUG==='object' && "
                "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
                "!!window.WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()"
            )
            if ok:
                page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        page.wait_for_timeout(250)
    note("wait_ready: WH_DEBUG never became ready")
    return False


def stage(page):
    """Player attack stage: 'windup' | 'strike' | 'recover' | null (pre-Ds1 too)."""
    return page.evaluate(
        "(function(){try{return window.WH_DEBUG.getAttackStage();}catch(e){return null;}})()"
    )


def player_state(page):
    """Attribute-guarded player snapshot (D2 fields incl. yawFrame)."""
    return page.evaluate(
        "(function(){function g(f){try{return f();}catch(e){return null;}}"
        "var p=window.WH_DEBUG.getPlayer();var out={};"
        "out.yaw=g(function(){return p.yaw;});"
        "out.camYaw=g(function(){return p.camYaw;});"
        "out.comboIndex=g(function(){return p.comboIndex;});"
        "out.comboQueued=g(function(){return !!p.comboQueued;});"
        "out.recoverFullyElapsed=g(function(){return p.recoverFullyElapsed;});"
        "out.attacking=g(function(){return !!p.attacking;});"
        "out.attackTimer=g(function(){return p.attackTimer;});"
        "out.lockTarget=g(function(){return !!p.lockTarget;});"
        "out.pos=g(function(){return {x:p.pos.x,z:p.pos.z};});"
        "out.bodyParentIsYawFrame=g(function(){"
        "return p.yawFrame ? p.body.parent===p.yawFrame : null;});"
        "out.yawFrameYaw=g(function(){"
        "return p.yawFrame?p.yawFrame.rotation.y:null;});"
        "out.atkYawOffset=g(function(){"
        "return (p.atkYawOffset!==undefined)?p.atkYawOffset:null;});"
        "out.hp=g(function(){return p.hp;});"
        "out.rolling=g(function(){return !!p.rolling;});"
        "return out;})()"
    )


def enemy_ref(page, idx=0):
    """Return (js_handle, snapshot) for enemy idx; handle is LIVE for mutation."""
    snap = page.evaluate(
        "(function(){var e=window.WH_DEBUG.getEnemy(%d);if(!e)return null;"
        "return {type:e.type,fsm:e.fsm,hp:e.hp,x:e.x,z:e.z};})()" % idx
    )
    if snap is None:
        return None, None
    refh = page.evaluate_handle(
        "(function(){var e=window.WH_DEBUG.getEnemy(%d);return e?e.ref:null;})()" % idx
    )
    return refh, snap


def enemy_field(page, refh, expr):
    """Read a field from the LIVE enemy handle, attribute-guarded."""
    return page.evaluate(
        "(function(e){try{return %s;}catch(err){return null;}})" % expr, refh
    )


def hp(page):
    return page.evaluate(
        "(function(){try{return window.WH_DEBUG.getPlayer().hp;}catch(e){return null;}})()"
    )


def press_f(page):
    page.keyboard.press("f")


def press_space(page):
    page.keyboard.press(" ")


def lmb(page):
    """LMB click at canvas center: mouse.down + fast mouse.up."""
    page.mouse.click(512, 384)


def lmb_down(page):
    page.mouse.down()


def lmb_up(page):
    page.mouse.up()


def rmb(page):
    vp = page.viewport_size
    cx, cy = vp["width"] // 2, vp["height"] // 2
    page.mouse.click(cx, cy, button="right")
    time.sleep(0.1)


def await_fsm(page, handle, want="attack", timeout_s=8.0):
    """Poll live ref.fsm until it equals want. Returns (t_page, fsm) or (None)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        v = page.evaluate("(function(e){try{return e.fsm;}catch(x){return null;}})", handle)
        if v == want:
            return page.evaluate("performance.now()"), v
        page.wait_for_timeout(3)
    return None, None


def enemy_phase(page, handle):
    """Read ref.attackPhase (Devbot-added). Pre-build: None => AC FAILs clean."""
    return page.evaluate(
        "(function(e){try{return e.attackPhase||null;}catch(x){return null;}})", handle
    )


def displace(page, handle, dx, dz):
    """SANCTIONED non-input act: move the live enemy (simulates target motion)."""
    return page.evaluate(
        "(function(e){try{e.pos.x=(e.pos.x||0)+" % dx
        + ";e.pos.z=(e.pos.z||0)+" % dz
        + ";if(e.root)e.root.position.x=e.pos.x;if(e.root)e.root.position.z=e.pos.z;"
          "return true;}catch(x){return false;}})",
        handle,
    )