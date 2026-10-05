#!/usr/bin/env python3
"""IO probe 8: N2b pitch raw deltas + N5 chip-click stage trace."""
import sys, importlib.util, time
sys.argv = ["probe8", "/workspace/witch-hunter/prototype/builds/v8-playable.html"]
spec = importlib.util.spec_from_file_location("mv", "/workspace/witch-hunter/tests/wh_mousebind_validation.py")
mv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mv)
server = mv.start_server()
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        pg = b.new_context(viewport={"width": 1280, "height": 800}).new_page()
        pg.add_init_script(mv.INIT_SCRIPT)
        pg.goto(mv.page_url(), wait_until="load", timeout=30000)
        mv.wait_boot(pg)
        st = mv.page_state(pg)
        rad = 3.141592653589793 / 180.0
        sens = 0.25 * 0.85
        # --- N2b section ---
        mv.press_bq(pg); mv.poll_until(pg, lambda: mv.page_state(pg)["locked"], 4.0)
        y0 = mv.page_state(pg)["yaw"]; pp0 = mv.page_state(pg)["pitch"]
        pg.evaluate("document.dispatchEvent(new MouseEvent('mousemove',{movementX:40,movementY:0,bubbles:true}))")
        pg.wait_for_timeout(80)
        s1 = mv.page_state(pg)
        print("E1 yaw: d=%r exp=%r" % (s1["yaw"] - y0, -40*sens*rad))
        print("E1 pitch: d=%r exp=0" % (s1["pitch"] - pp0))
        pg.evaluate("document.dispatchEvent(new MouseEvent('mousemove',{movementX:-40,movementY:40,bubbles:true}))")
        pg.wait_for_timeout(80)
        s2 = mv.page_state(pg)
        print("E2 yaw: d=%r exp=%r ok=%s" % (s2["yaw"]-y0, 0.0, abs(s2["yaw"]-y0) < 1e-6))
        print("E2 pitch: d=%r exp=%r" % (s2["pitch"]-pp0, 40*sens*rad))
        # raw event fields sanity
        print("cfg in page: sensMult=%r" % pg.evaluate("window.WH_CONFIG.mouse && WH_CONFIG.mouse.pointerLockSensMult"))
        # --- N5 (b) section ---
        mv.press_bq(pg); mv.poll_until(pg, lambda: not mv.page_state(pg)["locked"], 4.0)
        mv.poll_until(pg, lambda: mv.page_state(pg)["stage"] is None, 8.0)
        pg.wait_for_timeout(300)
        pre = mv.page_state(pg)["stage"]
        box = mv.chip_box(pg)
        print("N5 stage pre-click:", pre, "chip box:", bool(box))
        if box:
            pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]/2)
            pg.wait_for_timeout(200)
            print("N5 +200ms: stage=%r bound=%r" % (mv.page_state(pg)["stage"], mv.page_state(pg)["bound"]))
            pg.wait_for_timeout(150)
            print("N5 +350ms: stage=%r bound=%r" % (mv.page_state(pg)["stage"], mv.page_state(pg)["bound"]))
            # who fires? watch tryAttack calls directly
            pg.evaluate("window.__whMBTest.attackCalls = 0; const P=window.WH_DEBUG.getPlayer(); if (P) { const o=P.tryAttack.bind(P); P.tryAttack=function(){window.__whMBTest.attackCalls++; return o();}; }")
            pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]/2)
            pg.wait_for_timeout(250)
            print("N5 click2: attackCalls=%r stage=%r bound=%r" % (
                pg.evaluate("window.__whMBTest.attackCalls"), mv.page_state(pg)["stage"], mv.page_state(pg)["bound"]))
        b.close()
finally:
    mv.stop_server(server)
print("PROBE8 DONE")