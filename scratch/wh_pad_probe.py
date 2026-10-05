#!/usr/bin/env python3
"""IO probe 3: why p5_touch_pad reads dyaw=0. Instrument pointer delivery."""
import sys, importlib.util
sys.argv = ["probe3", "/workspace/witch-hunter/prototype/builds/v7-playable.html"]
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
        # show touch layer explicitly, then inspect cam pad candidates
        page.evaluate("window.WH_TouchControls && window.WH_TouchControls.show()")
        page.wait_for_timeout(300)
        info = page.evaluate("""(() => {
          var cands = document.querySelectorAll('.wh-touch-ctl.cam, [id*=cam i]');
          var out = [];
          for (var i = 0; i < cands.length; i++) {
            var e = cands[i];
            var r = e.getBoundingClientRect();
            out.push({tag: e.tagName, id: e.id, cls: e.className,
                      x: r.x, y: r.y, w: r.width, h: r.height,
                      pe: getComputedStyle(e).pointerEvents});
          }
          var ctl = document.querySelectorAll('.wh-touch-ctl');
          return {count: cands.length, cands: out,
                  ctlCount: ctl.length,
                  ctlIds: Array.prototype.map.call(ctl, function (e) {
                    return e.tagName + '#' + e.id + '.' + e.className; })};
        })()""")
        print("PAD INFO:", info)
        # attach capture-level listeners for pointer events
        page.evaluate("""(() => {
          window.__whPE = { down: [], move: 0, up: 0 };
          ['pointerdown','pointermove','pointerup'].forEach(function (t) {
            document.addEventListener(t, function (e) {
              if (t === 'pointerdown')
                window.__whPE.down.push((e.target.id || '') + '.' +
                  (e.target.className || '').slice(0, 30));
              else if (t === 'pointermove') window.__whPE.move++;
              else window.__whPE.up++;
            }, true);
          });
        })()""")
        st0 = mbh.page_state(page)
        res = mbh.p5_touch_pad(page)
        st = mbh.page_state(page)
        pe = page.evaluate("window.__whPE")
        print("p5 result:", res, "dyaw=%r dpitch=%r" % (
            (st["yaw"] - st0["yaw"]) if st["yaw"] is not None else None,
            (st["pitch"] - st0["pitch"]) if st["pitch"] is not None else None))
        print("POINTER EVENTS:", pe)
        browser.close()
finally:
    if server:
        try:
            server.terminate(); server.wait()
        except Exception:
            pass
print("PROBE3 DONE")