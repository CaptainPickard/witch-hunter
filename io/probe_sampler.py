"""Empirical sampler test: install sampler THEN click; dump the trace."""
import time, math
from playwright.sync_api import sync_playwright

SAMPLER_JS = """(function(cfg){return new Promise(function(resolve){
  var out = {rows: [], displaced: false, t0: null};
  var deadline = performance.now() + cfg.ms;
  function tick(now){
    var p = window.WH_DEBUG.getPlayer();
    if (p) {
      var st = p.getAttackStage ? p.getAttackStage() : null;
      if (out.t0 === null) out.t0 = now;
      var row = {t: +(now - out.t0).toFixed(1), st: st, yaw: +p.yaw.toFixed(4),
                 locked: !!p.lockTarget,
                 tx: p.lockTarget ? +p.lockTarget.pos.x.toFixed(3) : null,
                 x: +p.pos.x.toFixed(3), z: +p.pos.z.toFixed(3)};
      if (st === 'windup' && cfg.displace && !out.displaced) {
        out.displaced = true;
        try { var e = cfg.eget(); if (e && e.pos) { e.pos.x += cfg.dx;
              e.pos.z += cfg.dz; if (e.root) { e.root.position.x = e.pos.x;
              e.root.position.z = e.pos.z; } } } catch (x) {}
      }
      out.rows.push(row);
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
    handle = page.evaluate_handle("(function(){var e=window.WH_DEBUG.getEnemy(0);return e?e.ref:null;})()")
    hold = page.evaluate_handle(SAMPLER_JS, {"ms": 3000, "displace": True, "dx": 0.8, "dz": 0.0, "eget": None})
    page.mouse.click(512, 384)
    trace = hold.json_value()
    print("rows:", len(trace["rows"]), "displaced:", trace["displaced"])
    for r in trace["rows"][:20]:
        print(r)
    b.close()