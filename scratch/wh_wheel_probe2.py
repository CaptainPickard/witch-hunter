#!/usr/bin/env python3
"""IO probe 2: replicate harness flow (boot via harness server, n4, p4) then
watch wheel delivery with an in-page event counter before/after p2_wheel."""
import sys, importlib.util, time
sys.argv = ["probe2", "/workspace/witch-hunter/prototype/builds/v7-playable.html"]
spec = importlib.util.spec_from_file_location(
    "mbh", "/workspace/witch-hunter/tests/wh_mousebind_validation.py")
mbh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mbh)

server = mbh.start_server()
url = mbh.page_url()
print("URL:", url)
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        ctx.add_init_script(mbh.INIT_SCRIPT)
        page = ctx.new_page()
        page.on("pageerror", lambda e: print("PAGEERR", str(e)[:120]))
        page.goto(url, wait_until="load", timeout=30000)
        booted = mbh.wait_boot(page)
        print("booted:", booted)
        page.evaluate("""
          window.__whWheelCount = 0;
          window.addEventListener('wheel', function () {
            window.__whWheelCount++; }, { passive: true, capture: true });
        """)
        st0 = mbh.page_state(page)
        print("st0 dist=%s yaw=%s" % (st0["dist"], st0["yaw"]))
        mbh.n4_free_inert(page, st0)
        st1 = mbh.page_state(page)
        print("after n4: dist=%s" % st1["dist"])
        mbh.p4_drag_math(page, st1)
        st2 = mbh.page_state(page)
        print("after p4: dist=%s yaw=%s" % (st2["dist"], st2["yaw"]))
        print("wheelCount BEFORE p2_wheel:", page.evaluate("window.__whWheelCount"))
        # instrument p2_wheel manually, step by step:
        page.mouse.move(640, 400)
        page.wait_for_timeout(80)
        page.mouse.wheel(0, 120)
        page.wait_for_timeout(200)
        print("after +120: wheelCount=%s dist=%s" % (
            page.evaluate("window.__whWheelCount"),
            mbh.page_state(page)["dist"]))
        page.mouse.wheel(0, -120)
        page.wait_for_timeout(300)
        print("after -120: wheelCount=%s dist=%s" % (
            page.evaluate("window.__whWheelCount"),
            mbh.page_state(page)["dist"]))
        # and a FRESH page does it work?
        page2 = ctx.new_page()
        page2.goto(url, wait_until="load", timeout=30000)
        page2.wait_for_function(
            "window.WH_DEBUG && window.WH_DEBUG.getPlayer && "
            "window.WH_DEBUG.getPlayer()", timeout=90000)
        page2.mouse.move(640, 400)
        page2.wait_for_timeout(80)
        page2.mouse.wheel(0, 120)
        page2.wait_for_timeout(200)
        print("FRESH page after +120: dist=%s" % mbh.page_state(page2)["dist"])
        browser.close()
finally:
    if server:
        try:
            server.terminate()
            server.wait()
        except Exception:
            pass
print("PROBE2 DONE")