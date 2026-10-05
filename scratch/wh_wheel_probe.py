#!/usr/bin/env python3
"""IO probe: which wheel delivery route reaches the v7 wheel handler headlessly.
Route A: playwright page.mouse.move to canvas center + page.mouse.wheel
Route B: CDP Input.dispatchMouseEvent type=mouseWheel
Reads game.player.camDist before/after each."""
import subprocess, time, sys, os
from playwright.sync_api import sync_playwright

P = "/workspace/witch-hunter/prototype"
PORT = 8807
srv = subprocess.Popen([sys.executable, "server.py", str(PORT)],
                       cwd=P, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
url = "http://localhost:%d/builds/v7-playable.html" % PORT
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        pg = b.new_context(viewport={"width": 1280, "height": 800}).new_page()
        pg.goto(url, wait_until="load", timeout=30000)
        pg.wait_for_function(
            "window.WH_DEBUG && window.WH_DEBUG.getPlayer && "
            "window.WH_DEBUG.getPlayer()", timeout=90000)
        def dist():
            return pg.evaluate(
                "window.WH_DEBUG.getPlayer().camDist")
        print("d0", dist())
        # Route A: playwright mouse wheel after positioning over canvas
        pg.mouse.move(640, 400)
        pg.wait_for_timeout(80)
        pg.mouse.wheel(0, 120)
        pg.wait_for_timeout(150)
        print("afterA+120", dist())
        pg.mouse.wheel(0, -120)
        pg.wait_for_timeout(150)
        print("afterA-120", dist())
        # Route B: CDP mouseWheel
        cdp = pg.context.new_cdp_session(pg)
        def cdp_wheel(dy):
            cdp.send("Input.dispatchMouseEvent", {
                "type": "mouseWheel", "x": 640, "y": 400,
                "deltaX": 0, "deltaY": dy,
                "button": "none", "buttons": 0,
                "pointerType": "mouse"})
        d_prev = dist()
        cdp_wheel(120)
        pg.wait_for_timeout(150)
        print("afterB+120", dist(), "(prev %r)" % d_prev)
        cdp_wheel(-120)
        pg.wait_for_timeout(150)
        print("afterB-120", dist())
        # Route C: CDP with explicit modifiers/buttons=0 pointerType mouse (same as B basically)
        d_prev = dist()
        b.close()
finally:
    srv.terminate()
    srv.wait()
print("PROBE DONE")