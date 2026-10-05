#!/usr/bin/env python3
"""IO probe 5: bisect why harness p5_touch_pad reads 0 in-run but works fresh.
Run A: p5 as FIRST interaction. Run B: p5 after n4+p4+p2_wheel sequence.
Run C: inline drag right after a failed p5 (sticky-state check)."""
import sys, importlib.util
sys.argv = ["probe5", "/workspace/witch-hunter/prototype/builds/v7-playable.html"]
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

        # ---- Run A: p5 first interaction on a fresh page
        pa = ctx.new_page()
        pa.goto(url, wait_until="load", timeout=30000)
        pa.wait_for_function(
            "window.WH_DEBUG && window.WH_DEBUG.getPlayer && "
            "window.WH_DEBUG.getPlayer()", timeout=90000)
        rA = mbh.p5_touch_pad(pa)
        print("RUN A (p5 first):", rA)
        pa.close()

        # ---- Run B: n4 -> p4 -> p2_wheel -> p5
        pb = ctx.new_page()
        pb.goto(url, wait_until="load", timeout=30000)
        pb.wait_for_function(
            "window.WH_DEBUG && window.WH_DEBUG.getPlayer && "
            "window.WH_DEBUG.getPlayer()", timeout=90000)
        st0 = mbh.page_state(pb)
        mbh.n4_free_inert(pb, st0)
        mbh.p4_drag_math(pb, mbh.page_state(pb))
        mbh.p2_wheel(pb, mbh.page_state(pb))
        rB = mbh.p5_touch_pad(pb)
        print("RUN B (after n4/p4/wheel):", rB)

        # ---- Run C: inline drag immediately after failed p5
        if not rB:
            pad = pb.query_selector(".wh-touch-ctl.cam")
            b0 = pad.bounding_box()
            cx, cy = b0["x"] + b0["width"] / 2, b0["y"] + b0["height"] / 2
            y0 = mbh.page_state(pb)["yaw"]
            pb.mouse.move(cx, cy)
            pb.wait_for_timeout(100)
            pb.mouse.down()
            pb.mouse.move(cx - 60, cy, steps=1)
            pb.wait_for_timeout(100)
            pb.mouse.move(cx - 60, cy + 40, steps=1)
            pb.wait_for_timeout(100)
            pb.mouse.up()
            pb.wait_for_timeout(300)
            y1 = mbh.page_state(pb)["yaw"]
            print("RUN C (inline after p5): dyaw=%r" % (
                y1 - y0 if y1 is not None and y0 is not None else None))
            print("RUN C TC-state:", pb.evaluate("""(() => {
              var tc = window.WH_TouchControls;
              return { vis: tc.isVisible(), edit: tc.isEditMode ? tc.isEditMode() : null };
            })()"""))
        browser.close()
finally:
    if server:
        try:
            server.terminate(); server.wait()
        except Exception:
            pass
print("PROBE5 DONE")