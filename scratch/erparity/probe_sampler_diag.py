#!/usr/bin/env python3
"""Diag 2: why does the attack end after 1 frame in the diag probe?
Install a sampler (like the harness), do one LMB, and print all rows."""
from playwright.sync_api import sync_playwright
import json
BASE = "http://127.0.0.1:8793/"
SAMPLER_JS = """
(function(){
  if (window.__D) window.__D.stop();
  var S = {rows: [], frame: 0, stopped: false, stop: function(){this.stopped=true; if(this.raf)cancelAnimationFrame(this.raf);}};
  window.__D = S;
  function snap(){
    var d = window.WH_DEBUG; var p = d.getPlayer(); var md = null;
    try { md = d.getMoveDef(); } catch(e) {}
    return {f: S.frame, attacking: !!p.attacking, rolling: !!p.rolling,
            moveId: md ? md.moveId : null,
            stage: md && md.phase ? md.phase.stage : null,
            t: md && md.phase ? md.phase.t : null,
            elapsed: p.attacking ? (p.attackTotal - p.attackTimer) : null,
            timer: p.attackTimer, total: p.attackTotal,
            pos: {x: p.pos.x, z: p.pos.z}};
  }
  function tick(){ if (S.stopped) return; S.rows.push(snap()); S.frame++; S.raf = requestAnimationFrame(tick); }
  S.raf = requestAnimationFrame(tick);
  return true;
})()
"""
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"], headless=True)
    pg = b.new_page(viewport={"width": 640, "height": 400})
    pg.on("pageerror", lambda e: print("PAGEERROR:", e))
    pg.on("console", lambda m: print("console.%s: %s" % (m.type, m.text[:200])) if m.type in ("error","warning") else None)
    pg.goto(BASE, wait_until="load", timeout=30000)
    for _ in range(60):
        if pg.evaluate("(function(){try{return typeof WH_DEBUG==='object' && !!WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()"): break
        pg.wait_for_timeout(400)
    pg.wait_for_timeout(1500)
    pg.evaluate("(function(){WH_DEBUG.teleportPlayer(2.5,74);WH_DEBUG.setCameraYaw(180);WH_DEBUG.setStamina(100);})()")
    print("install:", pg.evaluate(SAMPLER_JS))
    pg.mouse.click(320, 200)
    import time
    t0 = time.time()
    pg.wait_for_timeout(9000)
    pg.evaluate("window.__D.stop()")
    rows = pg.evaluate("window.__D.rows")
    print("elapsed wall=%.1f rows=%d" % (time.time()-t0, len(rows)))
    for r in rows[:40]:
        print(r)
    b.close()
