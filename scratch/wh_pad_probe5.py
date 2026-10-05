#!/usr/bin/env python3
"""IO probe 7: in the FULL harness run, dump player/TC state at p5 entry."""
import sys, importlib.util
sys.argv = ["probe7", "/workspace/witch-hunter/prototype/builds/v7-playable.html"]
spec = importlib.util.spec_from_file_location(
    "mbh", "/workspace/witch-hunter/tests/wh_mousebind_validation.py")
mbh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mbh)

_orig_p5 = mbh.p5_touch_pad

def p5_diag(page):
    d = page.evaluate("""(() => {
      var P = window.WH_DEBUG && window.WH_DEBUG.getPlayer &&
              window.WH_DEBUG.getPlayer();
      var tc = window.WH_TouchControls;
      return {
        hasP: !!P, state: P ? P.state : null,
        dead: P ? !!P.dead : null,
        running: window.game ? !!window.game.running : null,
        tcVis: tc && tc.isVisible ? tc.isVisible() : null,
        padInDom: !!document.querySelector('.wh-touch-ctl.cam'),
        locked: !!document.pointerLockElement
      };
    })()""")
    print("=== P5-ENTRY DIAG:", d, flush=True)
    return _orig_p5(page)

mbh.p5_touch_pad = p5_diag
mbh.main()