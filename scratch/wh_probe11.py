#!/usr/bin/env python3
"""IO probe 11: P5-pad in-run fail - bisect with PRECISE stage instrumentation.
Replay: (boot) -> wheel -> block/cast -> strike -> N2 bind -> N8 -> unbind ->
then pad drag, dumping TC internals (pointers map state) at each stage."""
import sys, importlib.util
sys.argv = ["probe11", "/workspace/witch-hunter/prototype/builds/v8-playable.html"]
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
        # deep TC instrumentation: spy on camMove calls
        pg.evaluate("""(() => {
          window.__padLog = [];
        })()""")
        def pad_drag(tag):
            mvs = pg.evaluate("(() => { /* purge */ return 0; })()")
            mv.p5_touch_pad(pg)  # the REAL harness fn - shows layer itself
            st = mv.page_state(pg)
            print(tag, "dyaw-check: use p5 result row above")

        # Stage 1: pristine (fresh boot, nothing done) - run p5 FIRST
        r1 = mv.p5_touch_pad(pg)
        print("S1 pristine p5:", r1)

        # Stage 2: now do the harness pre-legs (wheel, block, strike, N2, unbind)
        mv.p2_wheel(pg, mv.page_state(pg))
        mv.p2_block_ctx(pg)
        mv.p2_strike(pg)
        bound, st_bind = mv.n2_bind(pg)
        print("S2 n2 bound:", bound)
        if bound:
            mv.n2a_locked_motion(pg, st_bind)
            mv.n2b_dispatch(pg, st_bind)
        mv.n8_stamps(pg)
        mv.n3_unbind(pg)
        # Stage 3: pad drag after ALL that
        r3 = mv.p5_touch_pad(pg)
        print("S3 post-legs p5:", r3)
        b.close()
finally:
    mv.stop_server(server)
print("PROBE11 DONE")