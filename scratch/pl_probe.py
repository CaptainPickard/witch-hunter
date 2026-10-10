import sys, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:8791/scratch/pl_probe.html"

def dump(tag, page):
    ev = page.evaluate("window.__EV")
    print(f"[{tag}] {ev}")

with sync_playwright() as p:
    print("playwright driver:", p.chromium.name)
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 800, "height": 600})
    page = ctx.new_page()
    page.on("pageerror", lambda e: print("PAGEERROR:", e))
    page.on("console", lambda m: print("CONSOLE:", m.type, m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="load", timeout=15000)
    page.wait_for_timeout(500)

    # A: JS-initiated lock
    r = page.evaluate("window.__doLock()")
    print("A doLock() ret:", r)
    page.wait_for_timeout(600)
    print("A pointerLockElement:", page.evaluate("!!document.pointerLockElement"))
    dump("A after JS lock", page)

    # B: synthetic mouse move WHILE locked
    page.mouse.move(300, 200)
    page.wait_for_timeout(100)
    page.mouse.move(360, 260)
    page.wait_for_timeout(300)
    dump("B after synthetic moves locked", page)

    # C: user-gesture click-then-move while locked (click then move)
    page.mouse.click(700, 550)  # outside canvas
    page.evaluate("window.__doLock()")
    page.wait_for_timeout(400)
    page.mouse.move(400, 300)
    page.wait_for_timeout(100)
    page.mouse.move(500, 300)
    page.wait_for_timeout(300)
    dump("C after click+doLock+move", page)

    # D: Esc unbind = keyboard.press Escape
    page.keyboard.press("Escape")
    page.wait_for_timeout(400)
    print("D pointerLockElement after Esc:", page.evaluate("!!document.pointerLockElement"))
    dump("D after Esc", page)

    # E: does user-gesture-bound JS call lock (click on canvas then __doLock)
    page.mouse.click(300, 200)
    page.evaluate("window.__doLock()")
    page.wait_for_timeout(400)
    print("E pointerLockElement:", page.evaluate("!!document.pointerLockElement"))
    dump("E after canvas click + doLock", page)

    # F: keyboard.press('`') while locked then move
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    ok = page.evaluate("!!document.pointerLockElement")
    print("F pre-state locked:", ok)
    b.close()
print("probe done")