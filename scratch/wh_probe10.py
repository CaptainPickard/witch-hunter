#!/usr/bin/env python3
"""IO probe 10: replay the EXACT harness leg order and trace mousedown
targets + tryAttack calls + stage, to find N5(b)'s real failure mode."""
import sys, importlib.util
sys.argv = ["probe10", "/workspace/witch-hunter/prototype/builds/v8-playable.html"]
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
        # instrument ONCE: mousedown target log + attack-wrap (re-wrappable)
        pg.evaluate("""(() => {
          window.__whMBTest.mdLog = [];
          document.addEventListener('mousedown', function (e) {
            window.__whMBTest.mdLog.push([e.button, e.target && e.target.id,
              !!document.pointerLockElement]);
          }, true);
        })()""")
        def rewrap():
            pg.evaluate("""(() => {
              const P = window.WH_DEBUG.getPlayer();
              if (P.__wrapped) return;
              const o = P.tryAttack.bind(P);
              P.tryAttack = function () {
                window.__whMBTest.attackCalls =
                  (window.__whMBTest.attackCalls || 0) + 1;
                return o();
              };
              P.__wrapped = true;
            })()""")
        # autoBind OFF for HEAD-parity legs (as harness does)
        pg.evaluate("if (window.WH_CONFIG && WH_CONFIG.mouse) WH_CONFIG.mouse.autoBindOnCanvasClick = false")
        # leg A: P4-style canvas drag (mimic)
        pg.evaluate("window.WH_TouchControls && window.WH_TouchControls.show()")
        pg.wait_for_timeout(150)
        pad = pg.query_selector(".wh-touch-ctl.cam")
        bb = pad.bounding_box()
        cx, cy = bb["x"]+bb["width"]/2, bb["y"]+bb["height"]/2
        st0 = mv.page_state(pg)
        pg.mouse.move(cx, cy); pg.mouse.down()
        pg.mouse.move(cx-60, cy, steps=1); pg.wait_for_timeout(100)
        pg.mouse.move(cx-60, cy+40, steps=1); pg.wait_for_timeout(100)
        pg.mouse.up()
        pg.wait_for_timeout(200)
        print("after pad drag: stage=%r bound=%r" % (
            mv.page_state(pg)["stage"], mv.page_state(pg)["bound"]))
        # leg B: strike (canvas LMB)
        rewrap()
        canvas = pg.query_selector("#wh-canvas")
        cb = canvas.bounding_box()
        pg.mouse.click(cb["x"]+cb["width"]/2, cb["y"]+cb["height"]/2)
        pg.wait_for_timeout(300)
        print("after canvas strike: attackCalls=%r stage=%r mdLog=%s" % (
            pg.evaluate("window.__whMBTest.attackCalls"),
            mv.page_state(pg)["stage"],
            pg.evaluate("window.__whMBTest.mdLog.slice(-3)")))
        # leg C: N5(b) chip click, FREE first, flush stage
        pg.evaluate("if (window.WH_CONFIG && WH_CONFIG.mouse) WH_CONFIG.mouse.autoBindOnCanvasClick = true")
        pg.wait_for_timeout(400)
        mv.poll_until(pg, lambda: mv.page_state(pg)["stage"] is None, 8.0)
        pg.wait_for_timeout(300)
        chip = pg.query_selector("#wh-mouse-chip")
        cb2 = chip.bounding_box()
        pg.evaluate("window.__whMBTest.attackCalls = 0")
        pg.mouse.click(cb2["x"]+cb2["width"]/2, cb2["y"]+cb2["height"]/2)
        pg.wait_for_timeout(350)
        print("after chip click: attackCalls=%r stage=%r bound=%r locked=%r mdLog=%s" % (
            pg.evaluate("window.__whMBTest.attackCalls"),
            mv.page_state(pg)["stage"], mv.page_state(pg)["bound"],
            mv.page_state(pg)["locked"],
            pg.evaluate("window.__whMBTest.mdLog.slice(-4)")))
        b.close()
finally:
    mv.stop_server(server)
print("PROBE10 DONE")