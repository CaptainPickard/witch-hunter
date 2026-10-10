import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8791/scratch/pl_probe.html"

with sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    page = b.new_context(viewport={"width": 800, "height": 600}).new_page()
    page.goto(URL, wait_until="load")
    page.wait_for_timeout(300)

    # M: clean measurement - lock, THEN clear moves, THEN synthetic moves
    page.evaluate("window.__doLock()")
    page.wait_for_timeout(400)
    page.evaluate("window.__EV.moves=[]; window.__EV.cap=200;")
    # move in a pattern
    page.mouse.move(300, 200)
    page.mouse.move(340, 200)
    page.mouse.move(340, 240)
    page.mouse.move(300, 240)
    page.wait_for_timeout(400)
    print("M locked=%s moves=%s" % (page.evaluate("!!document.pointerLockElement"),
                                    page.evaluate("window.__EV.moves")))

    # N: unlock, then synthetic moves (drag-style, no lock) - clientX should change
    page.evaluate("window.__unlock()")
    page.wait_for_timeout(400)
    page.evaluate("window.__EV.moves=[];")
    page.mouse.move(300, 200)
    page.mouse.move(340, 200)
    page.mouse.move(340, 240)
    page.wait_for_timeout(300)
    print("N unlocked moves=%s" % page.evaluate("window.__EV.moves"))

    # O: two fresh boots relock-retry need? lock/unlock x3 rapid
    for i in range(3):
        page.evaluate("window.__doLock()")
        page.wait_for_timeout(300)
        ok1 = page.evaluate("!!document.pointerLockElement")
        page.evaluate("window.__unlock()")
        page.wait_for_timeout(150)
        print("O cycle%d locked=%s" % (i, ok1))
    b.close()
print("probe3 done")