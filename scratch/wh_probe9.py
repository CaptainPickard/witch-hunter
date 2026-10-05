#!/usr/bin/env python3
"""IO probe 9: who is on top at chip center when TC layer is shown?"""
import sys, importlib.util
sys.argv = ["probe9", "/workspace/witch-hunter/prototype/builds/v8-playable.html"]
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

        def geo(tag):
            print(tag, pg.evaluate("""(() => {
              const c = document.getElementById('wh-mouse-chip');
              const cb = c.getBoundingClientRect();
              const cx = cb.x + cb.width/2, cy = cb.y + cb.height/2;
              const top = document.elementFromPoint(cx, cy);
              const ctrls = [...document.querySelectorAll('.wh-touch-ctl')].map(e => {
                const r = e.getBoundingClientRect();
                return {cls: e.className, x: Math.round(r.x), y: Math.round(r.y),
                        w: Math.round(r.width), h: Math.round(r.height)};
              });
              return {chip: {x: Math.round(cb.x), y: Math.round(cb.y),
                             w: Math.round(cb.width), h: Math.round(cb.height)},
                      topEl: top ? (top.id + '|' + top.className) : 'null',
                      same: top === c, tcVisible: !!(window.WH_TouchControls &&
                             window.WH_TouchControls.isVisible()), ctrls: ctrls};
            })()"""))

        geo("BEFORE show:")
        pg.evaluate("window.WH_TouchControls && window.WH_TouchControls.show()")
        pg.wait_for_timeout(200)
        geo("AFTER show: ")
        b.close()
finally:
    mv.stop_server(server)
print("PROBE9 DONE")