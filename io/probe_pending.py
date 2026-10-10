"""probe_pending: does a pending evaluate_handle promise starve page rAF?

1. install sampler (pending promise, resolves at 3.5s)
2. click, sleep 0.35s
3. while the promise is still pending: evaluate stage/attacking directly
   -> if page attacks fine here but the SAMPLED trace shows st=None rows
   throughout, the pending promise starves the sampler's rAF reads.
4. after resolution, compare trace vs the direct read.
"""
import time
from playwright.sync_api import sync_playwright

SAMPLER_JS = """(function(cfg){return new Promise(function(resolve){
  var out = {rows: [], t0: null, marker: null};
  var deadline = performance.now() + cfg.ms;
  function tick(now){
    var p = window.WH_DEBUG.getPlayer();
    if (p) {
      var st = p.getAttackStage ? p.getAttackStage() : null;
      if (out.t0 === null) out.t0 = now;
      // capture attacking too, so we can tell attack-never-ran vs read-starved
      out.rows.push({t: +(now - out.t0).toFixed(1), st: st,
                     att: !!p.attacking, yaw: +p.yaw.toFixed(4)});
    }
    if (now > deadline) { resolve(out); return; }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})})"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
    page = b.new_page()
    page.goto("http://localhost:8791/builds/v7-playable.html")
    page.wait_for_timeout(3500)
    hold = page.evaluate_handle(SAMPLER_JS, {"ms": 3500})
    page.mouse.click(512, 384)
    time.sleep(0.35)   # promise still pending
    s = page.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();"
                      "return {st:(p.getAttackStage?p.getAttackStage():null),"
                      "att:!!p.attacking, yaw:p.yaw};})()")
    print("DIRECT READ at 0.35s (promise pending):", s)
    trace = hold.json_value()
    hist = {}
    for r in trace["rows"]:
        hist[(r["st"], r["att"])] = hist.get((r["st"], r["att"]), 0) + 1
    print("TRACE histogram (st, att):", hist)
    b.close()