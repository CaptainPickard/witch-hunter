#!/usr/bin/env python3
"""IO probe 6: bisect which pre-p5 harness step kills pad steering.
After EACH pre-p5 step: quick pad drag, record dyaw alive/dead."""
import sys, importlib.util
sys.argv = ["probe6", "/workspace/witch-hunter/prototype/builds/v7-playable.html"]
spec = importlib.util.spec_from_file_location(
    "mbh", "/workspace/witch-hunter/tests/wh_mousebind_validation.py")
mbh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mbh)

server = mbh.start_server()
url = mbh.page_url()
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        ctx.add_init_script(mbh.INIT_SCRIPT)
        page = ctx.new_page()
        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_function(
            "window.WH_DEBUG && window.WH_DEBUG.getPlayer && "
            "window.WH_DEBUG.getPlayer()", timeout=90000)

        def pad_alive(tag):
            page.evaluate("window.WH_TouchControls && window.WH_TouchControls.show()")
            page.wait_for_timeout(150)
            pad = page.query_selector(".wh-touch-ctl.cam")
            if not pad:
                print(tag, "pad MISSING"); return
            b0 = pad.bounding_box()
            cx, cy = b0["x"] + b0["width"] / 2, b0["y"] + b0["height"] / 2
            y0 = mbh.page_state(page)["yaw"]
            page.mouse.move(cx, cy); page.wait_for_timeout(100)
            page.mouse.down()
            page.mouse.move(cx - 50, cy, steps=1); page.wait_for_timeout(80)
            page.mouse.move(cx - 50, cy + 30, steps=1); page.wait_for_timeout(80)
            page.mouse.up(); page.wait_for_timeout(250)
            y1 = mbh.page_state(page)["yaw"]
            dy = (y1 - y0) if (y1 is not None and y0 is not None) else None
            print("%-14s pad dyaw=%r %s" % (tag, dy, "ALIVE" if (dy or 0) != 0 else "DEAD"))

        st0 = mbh.page_state(page)
        alive0 = pad_alive("pristine")
        mbh.n4_free_inert(page, st0)
        pad_alive("after-n4")
        mbh.p4_drag_math(page, mbh.page_state(page))
        pad_alive("after-p4")
        mbh.p2_wheel(page, mbh.page_state(page))
        pad_alive("after-wheel")
        mbh.p2_block_ctx(page)
        pad_alive("after-block")
        mbh.p2_strike(page)
        pad_alive("after-strike")
        bound, st_bind = mbh.n2_bind(page)
        pad_alive("after-n2")
        mbh.n8_stamps(page)
        pad_alive("after-n8")
        mbh.n3_unbind(page)
        pad_alive("after-n3")
        mbh.n5_autorebind(page)
        pad_alive("after-n5")
        mbh.n6_chip_toggle(page)
        pad_alive("after-n6")
        mbh.n7_fault(page)
        pad_alive("after-n7")
        browser.close()
finally:
    if server:
        try:
            server.terminate(); server.wait()
        except Exception:
            pass
print("PROBE6 DONE")