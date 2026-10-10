"""probe_sampler2: isolate the sampler+click interaction.

Part 1: no sampler - click, sleep 1.2s, read stage directly (control).
Part 2: sampler installed, click, sleep via python, then read stage + sampler.
"""
import time
from playwright.sync_api import sync_playwright

SAMPLER_JS = """(function(cfg){return new Promise(function(resolve){
  var out = {rows: [], displaced: false, t0: null};
  var deadline = performance.now() + cfg.ms;
  function tick(now){
    var p = window.WH_DEBUG.getPlayer();
    if (p) {
      var st = p.getAttackStage ? p.getAttackStage() : null;
      if (out.t0 === null) out.t0 = now;
      out.rows.push({t: +(now - out.t0).toFixed(1), st: st,
                     yaw: +p.yaw.toFixed(4)});
    }
    if (now > deadline) { resolve(out); return; }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})})"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])

    # ---- Part 1: control ------------------------------------------------
    page = b.new_page()
    page.goto("http://localhost:8791/builds/v7-playable.html")
    page.wait_for_timeout(3500)
    page.mouse.click(512, 384)
    time.sleep(1.2)
    s = page.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();"
                      "return {st:(p.getAttackStage?p.getAttackStage():null),"
                      "att:!!p.attacking, yaw:p.yaw};})()")
    print("CONTROL (no sampler):", s)
    page.close()

    # ---- Part 2: sampler + click ----------------------------------------
    page2 = b.new_page()
    page2.goto("http://localhost:8791/builds/v7-playable.html")
    page2.wait_for_timeout(3500)
    hold = page2.evaluate_handle(SAMPLER_JS, {"ms": 3000})
    page2.mouse.click(512, 384)
    time.sleep(1.2)   # let the swing play out in real time
    s2 = page2.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();"
                        "return {st:(p.getAttackStage?p.getAttackStage():null),"
                        "att:!!p.attacking, yaw:p.yaw};})()")
    trace = hold.json_value()
    st_counts = {}
    for r in trace["rows"]:
        st_counts[r["st"]] = st_counts.get(r["st"], 0) + 1
    print("SAMPLER page-state after 1.2s:", s2)
    print("SAMPLER rows:", len(trace["rows"]), "st histogram:", st_counts)
    page2.close()
    b.close()