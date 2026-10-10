"""probe_matrix: three sampler designs vs the same click; which samples truth?

A: promise-only sampler (pending until deadline) - KNOWN BAD baseline.
B: promise with a HANDLE arg (mimics A3-1's signature).
C: window-buffer sampler: installs rAF that appends to window.__IO_BUF and
   returns INSTANTLY; python drives; buffer read at the end.
"""
import time
from playwright.sync_api import sync_playwright

SAMPLER_A = """(function(cfg){return new Promise(function(resolve){
  var out = {rows: []};
  var deadline = performance.now() + cfg.ms;
  function tick(now){
    var p = window.WH_DEBUG.getPlayer();
    if (p) {
      var st = p.getAttackStage ? p.getAttackStage() : null;
      out.rows.push({t: +(now).toFixed(0), st: st, att: !!p.attacking});
    }
    if (now > deadline) { resolve(out); return; }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})})"""

SAMPLER_B = """(function(e, cfg){return new Promise(function(resolve){
  var out = {rows: []};
  var deadline = performance.now() + cfg.ms;
  function tick(now){
    var p = window.WH_DEBUG.getPlayer();
    if (p) {
      var st = p.getAttackStage ? p.getAttackStage() : null;
      out.rows.push({t: +(now).toFixed(0), st: st, att: !!p.attacking,
                     efsm: (function(){try{return e.fsm;}catch(x){return null;}})()});
    }
    if (now > deadline) { resolve(out); return; }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})})"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])

    def run_case(tag, sampler, arg_fn):
        page = b.new_page()
        page.goto("http://localhost:8791/builds/v7-playable.html")
        page.wait_for_timeout(3500)
        arg = arg_fn(page)          # install sampler FIRST
        page.mouse.click(512, 384)
        time.sleep(0.9)
        # direct read WHILE pending (for A/B):
        direct = page.evaluate(
            "(function(){var p=window.WH_DEBUG.getPlayer();"
            "return {st:(p.getAttackStage?p.getAttackStage():null),"
            "att:!!p.attacking};})()")
        if isinstance(arg, tuple):
            handle, cfg = handle_cfg(arg)
            trace = arg[0].json_value()
        else:
            trace = arg.json_value()
        hist = {}
        for r in trace["rows"]:
            hist[(r["st"], r["att"])] = hist.get((r["st"], r["att"]), 0) + 1
        print("%s direct@0.9s=%s history=%s" % (tag, direct, hist))
        page.close()

    def handle_cfg(t):
        return t

    run_case("A promise-only", SAMPLER_A,
             lambda p: p.evaluate_handle(SAMPLER_A, {"ms": 3500}))
    handle_setup = lambda p: p.evaluate_handle(
        "(function(){var e=window.WH_DEBUG.getEnemy(0);return e?e.ref:null;})()")
    en = None
    def arg_b(page):
        global en
        en = handle_setup(page)
        return page.evaluate_handle(SAMPLER_B, en, {"ms": 3500})
    # NOTE: evaluate_handle(expr, arg1, arg2) is valid: two args.
    run_case("B handle+promise", SAMPLER_B, arg_b)
    b.close()