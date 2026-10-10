import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8791/scratch/pl_probe.html"

with sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    page = b.new_context(viewport={"width": 800, "height": 600}).new_page()
    page.on("pageerror", lambda e: print("PAGEERROR:", e))
    page.goto(URL, wait_until="load")
    page.wait_for_timeout(300)

    # G: Esc keydown code mapping (does Playwright '`' map to Backquote?)
    page.evaluate("window.__KEYS=[]; document.addEventListener('keydown',e=>window.__KEYS.push({code:e.code,key:e.key}));")
    page.keyboard.press("`")
    page.keyboard.press("Escape")
    print("G key codes:", page.evaluate("window.__KEYS"))

    # H: lock -> exitPointerLock fires pointerlockchange?
    page.evaluate("window.__doLock()")
    page.wait_for_timeout(400)
    locked1 = page.evaluate("!!document.pointerLockElement")
    r = page.evaluate("window.__unlock()")
    page.wait_for_timeout(400)
    print("H locked=%s unlock=%s now=%s plChange=%s plError=%s" % (
        locked1, r, page.evaluate("!!document.pointerLockElement"),
        page.evaluate("window.__EV.plChange"), page.evaluate("window.__EV.plError")))

    # I: immediate relock after exit (throttle?)
    r2 = page.evaluate("window.__doLock()")
    page.wait_for_timeout(400)
    print("I immediate relock ret=%s locked=%s" % (r2, page.evaluate("!!document.pointerLockElement")))

    # J: after Esc-exit-equivalent (exitPointerLock), re-lock throttled?
    page.evaluate("window.__unlock()")
    page.wait_for_timeout(300)
    r3 = page.evaluate("window.__doLock()")
    page.wait_for_timeout(400)
    l3 = page.evaluate("!!document.pointerLockElement")
    print("J relock-after-exit ret=%s locked=%s" % (r3, l3))
    if not l3:
        page.wait_for_timeout(1500)
        r4 = page.evaluate("window.__doLock()")
        page.wait_for_timeout(400)
        print("J2 relock after 1.8s ret=%s locked=%s" % (r4, page.evaluate("!!document.pointerLockElement")))

    # K: Esc press while unlocked: pointerlockerror? nothing?
    page.evaluate("window.__unlock()")
    page.wait_for_timeout(200)
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    print("K after esc-while-free: locked=%s plError=%s" % (
        page.evaluate("!!document.pointerLockElement"), page.evaluate("window.__EV.plError")))

    # L: headless args variant? skip. Print final EV
    print("L final:", page.evaluate("window.__EV"))
    b.close()
print("probe2 done")