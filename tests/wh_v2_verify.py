"""Witch Hunter v2 verification: both origins, asset audit, camera-relative
movement, lock-on cycle, region round trip. Playwright headless chromium.
Base URLs are overridable via WH_BASE_ROOT / WH_BASE_PROXY env vars.
"""
from playwright.sync_api import sync_playwright
import json, os, sys

BASE_ROOT = os.environ.get("WH_BASE_ROOT", "http://localhost:8791/")
BASE_PROXY = os.environ.get("WH_BASE_PROXY", "http://localhost:8792/witchhunter/")

RESULTS = []
glb_log = []          # (origin, url, status)

def track(page, origin):
    def on_response(resp):
        u = resp.url
        if u.endswith(".glb"):
            glb_log.append((origin, u, resp.status))
    page.on("response", on_response)

def audit_assets(origin):
    glbs = [(u, s) for (o, u, s) in glb_log if o == origin]
    bad = [(u, s) for (u, s) in glbs if s != 200]
    ok = len(glbs) > 0 and not bad
    print("ASSET AUDIT [%s]: %d glb fetches, non-200: %s => %s"
          % (origin, len(glbs), bad, "PASS" if ok else "FAIL"))
    return ok

def run_suite(page, base_url, origin, do_movement=True, do_lock=True, do_region=True):
    errors, console_errors = [], []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.goto(base_url, wait_until="load", timeout=30000)
    page.wait_for_timeout(6000)   # preload all assets

    ok_dbg = page.evaluate("typeof window.WH_DEBUG === 'object' && typeof window.WH_DEBUG.getLockTarget === 'function' && typeof window.WH_DEBUG.setCameraYaw === 'function' && typeof window.WH_DEBUG.isLocked === 'function'")
    print("[%s] WH_DEBUG v2 hooks present => %s" % (origin, "PASS" if ok_dbg else "FAIL"))

    ok_move = True
    if do_movement:
        # D2: camera-relative movement after setCameraYaw(90deg)
        page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(90)")
        page.wait_for_timeout(300)
        p0 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
        page.keyboard.down("w")
        page.wait_for_timeout(1000)
        page.keyboard.up("w")
        p1 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
        dx, dz = p1["x"] - p0["x"], p1["z"] - p0["z"]
        # camYaw=90deg => camera forward = (sin(270), cos(270)) = (-1, 0): x decreases
        # Direction proves camera-relativity; magnitude is rAF-throttle dependent
        ok_move = dx < -0.5 and abs(dz) < 1.0
        print("[%s] W after setCameraYaw(90): dx=%.2f dz=%.2f => %s"
              % (origin, dx, dz, "PASS" if ok_move else "FAIL"))

        # A should strafe back (opposite): dot with forward < 0
        page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(90)")
        page.wait_for_timeout(300)
        q0 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
        page.keyboard.down("a")
        page.wait_for_timeout(600)
        page.keyboard.up("a")
        q1 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
        adx, adz = q1["x"] - q0["x"], q1["z"] - q0["z"]
        # camYaw=90 => forward=(-1,0); right=(-fz,fx)=(0,-1); A = -right = +z
        ok_a = adz > 1.0 and abs(adx) < 1.5
        print("[%s] A strafe: dx=%.2f dz=%.2f => %s"
              % (origin, adx, adz, "PASS" if ok_a else "FAIL"))

    ok_lock = True
    if do_lock:
        # D3: engage near the region-A bandit at (-6, -8). Stand SOUTH of it
        # and aim the camera north (-z): forward = camYaw + PI, so 0 => -z.
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.wait_for_timeout(400)
        page.keyboard.press("f")
        page.wait_for_timeout(500)
        locked = page.evaluate("window.WH_DEBUG.isLocked()")
        tgt = page.evaluate("window.WH_DEBUG.getLockTarget()")
        yaw = page.evaluate("window.WH_DEBUG.getPlayer().yaw")
        import math
        if tgt:
            to_e = math.atan2(tgt["x"] - page.evaluate("window.WH_DEBUG.getPlayerPosition()")["x"],
                              tgt["z"] - page.evaluate("window.WH_DEBUG.getPlayerPosition()")["z"])
            dyaw = (to_e - yaw + math.pi) % (2 * math.pi) - math.pi
            faces = abs(dyaw) < 0.15
        else:
            faces = False
        ok_lock = locked and tgt is not None and faces
        print("[%s] F lock-on: locked=%s target=%s yawErr=%.3f => %s"
              % (origin, locked, tgt and tgt["type"], dyaw if tgt else 9,
                 "PASS" if ok_lock else "FAIL"))

        # reticle visible while locked
        ret_visible = page.evaluate("document.getElementById('wh-lock-reticle').style.display")
        ok_ret = ret_visible == "block"
        print("[%s] reticle visible while locked => %s" % (origin, "PASS" if ok_ret else "FAIL"))

        # A/D strafe while locked: displacement roughly perpendicular to target dir
        page.evaluate("window.WH_DEBUG.breakLockOn()")
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.wait_for_timeout(400)
        page.keyboard.press("f")
        page.wait_for_timeout(400)
        l0 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
        tgt0 = page.evaluate("window.WH_DEBUG.getLockTarget()")
        page.keyboard.down("d")
        page.wait_for_timeout(600)
        page.keyboard.up("d")
        l1 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
        still_locked = page.evaluate("window.WH_DEBUG.isLocked()")
        tdx, tdz = tgt0["x"] - l0["x"], tgt0["z"] - l0["z"]
        mdx, mdz = l1["x"] - l0["x"], l1["z"] - l0["z"]
        cross = (tdx * mdz - tdz * mdx)   # perpendicular component dominates
        dotn = tdx * mdx + tdz * mdz
        ok_strafe = still_locked and abs(cross) > 1.0 and abs(dotn) < abs(cross) * 2.5
        print("[%s] strafe while locked: cross=%.2f dot=%.2f => %s"
              % (origin, cross, dotn, "PASS" if ok_strafe else "FAIL"))

        # kill target -> unlock
        page.evaluate("(function(){ var t = window.WH_DEBUG.getLockTarget(); window.WH_DEBUG.getPlayer().lockTarget.takeDamage(9999); })()")
        page.wait_for_timeout(400)
        unlocked = not page.evaluate("window.WH_DEBUG.isLocked()")
        print("[%s] kill target -> unlock => %s" % (origin, "PASS" if unlocked else "FAIL"))
        ok_lock = ok_lock and ok_ret and ok_strafe and unlocked

    ok_region = True
    if do_region:
        # round-trip region crossing still works (v2.5 method)
        page.evaluate("window.WH_DEBUG.teleportPlayer(0, -26)")
        page.wait_for_timeout(900)
        regB = page.evaluate("window.WH_DEBUG.activeRegionId")
        page.evaluate("window.WH_DEBUG.teleportPlayer(0, -23)")
        page.wait_for_timeout(900)
        regA = page.evaluate("window.WH_DEBUG.activeRegionId")
        ok_region = regB == "darkwood_edge" and regA == "hold_outskirts"
        print("[%s] region round trip: B=%s A=%s => %s"
              % (origin, regB, regA, "PASS" if ok_region else "FAIL"))

    ok_err = not errors and not console_errors
    print("[%s] pageerrors=%s consoleErrors=%s => %s"
          % (origin, errors[:3], console_errors[:3], "PASS" if ok_err else "FAIL"))
    return ok_dbg, ok_move, ok_lock, ok_region, ok_err

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    results = {}
    # origin 1: root
    page1 = browser.new_page(viewport={"width": 1280, "height": 800})
    track(page1, "root")
    results["root"] = run_suite(page1, BASE_ROOT, "root")
    page1.close()
    # origin 2: proxy prefix
    page2 = browser.new_page(viewport={"width": 1280, "height": 800})
    track(page2, "proxy")
    results["proxy"] = run_suite(page2, BASE_PROXY, "proxy")
    page2.close()
    browser.close()

a1 = audit_assets("root"); a2 = audit_assets("proxy")
print("GLB sample:", json.dumps([u.split('/')[-1] for (o, u, s) in glb_log if o == 'proxy'][:5]))
flat = [x for r in (results["root"], results["proxy"]) for x in r] + [a1, a2]
print("V2 VERIFY:", "PASS" if all(flat) else "FAIL")
sys.exit(0 if all(flat) else 1)