#!/usr/bin/env python3
"""IO probe 4: touch pad steering gate. Log pointerIds; try manual same-id
PointerEvent pair on the pad; compare against playwright mouse drag."""
import sys, importlib.util
sys.argv = ["probe4", "/workspace/witch-hunter/prototype/builds/v7-playable.html"]
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
        page.evaluate("window.WH_TouchControls && window.WH_TouchControls.show()")
        page.wait_for_timeout(300)
        page.evaluate("""(() => {
          window.__whPID = { down: [], move: [], up: [] };
          ['pointerdown','pointermove','pointerup'].forEach(function (t) {
            var k = t === 'pointerdown' ? 'down' : (t === 'pointermove' ? 'move' : 'up');
            document.addEventListener(t, function (e) {
              window.__whPID[k].push(e.pointerId);
            }, true);
          });
        })()""")
        pad = page.query_selector(".wh-touch-ctl.cam")
        b0 = pad.bounding_box()
        cx, cy = b0["x"] + b0["width"] / 2, b0["y"] + b0["height"] / 2
        y0 = mbh.page_state(page)["yaw"]
        # playwright drag
        page.mouse.move(cx, cy)
        page.mouse.down()
        page.mouse.move(cx - 60, cy, steps=1)
        page.mouse.move(cx - 60, cy + 40, steps=1)
        page.mouse.up()
        page.wait_for_timeout(250)
        ids = page.evaluate("window.__whPID")
        y1 = mbh.page_state(page)["yaw"]
        print("PLAYWRIGHT drag: ids=%s dyaw=%r" % (
            {k: list(set(v)) for k, v in ids.items()}, y1 - y0 if y1 is not None else None))
        # manual same-id pair
        y1b = mbh.page_state(page)["yaw"]
        js = """(() => {
          var pad = document.querySelector('.wh-touch-ctl.cam');
          var cx = %f, cy = %f;
          var pd = new PointerEvent('pointerdown', { pointerId: 777,
            clientX: cx, clientY: cy, bubbles: true, cancelable: true,
            pointerType: 'mouse', isPrimary: true });
          pad.dispatchEvent(pd);
          var pm1 = new PointerEvent('pointermove', { pointerId: 777,
            clientX: cx - 60, clientY: cy + 40, bubbles: true,
            cancelable: true, pointerType: 'mouse', isPrimary: true });
          pad.dispatchEvent(pm1);
          var pu = new PointerEvent('pointerup', { pointerId: 777,
            clientX: cx - 60, clientY: cy + 40, bubbles: true,
            cancelable: true, pointerType: 'mouse', isPrimary: true });
          pad.dispatchEvent(pu);
        })()""" % (cx, cy)
        page.evaluate(js)
        page.wait_for_timeout(250)
        y2 = mbh.page_state(page)["yaw"]
        print("MANUAL 777 pair: dyaw=%r" % (y2 - y1b if y2 is not None and y1b is not None else None))
        # visible/editMode introspection
        diag = page.evaluate("""(() => {
          var tc = window.WH_TouchControls;
          return { keys: Object.keys(tc), vis: tc.isVisible ? tc.isVisible() : null,
                   cfgTouch: !!(window.WH_CONFIG && window.WH_CONFIG.touch) };
        })()""")
        print("TC DIAG:", diag)
        browser.close()
finally:
    if server:
        try:
            server.terminate(); server.wait()
        except Exception:
            pass
print("PROBE4 DONE")