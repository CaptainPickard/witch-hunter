#!/usr/bin/env python3
"""Diag 3: compare organic LMB vs WH_DEBUG.triggerAttack() — does the swing run to completion?"""
from playwright.sync_api import sync_playwright
import time
BASE = "http://127.0.0.1:8793/"

SAMPLER = """
(function(){
  if (window.__D) window.__D.stop();
  var S = {rows: [], frame: 0, stopped: false,
           stop: function(){this.stopped=true; if(this.raf)cancelAnimationFrame(this.raf);}};
  window.__D = S;
  function snap(){
    var p = window.WH_DEBUG.getPlayer();
    return {f: S.frame, attacking: !!p.attacking, state: p.state,
            timer: p.attackTimer, total: p.attackTotal,
            ci: p.comboIndex, cq: !!p.comboQueued};
  }
  function tick(){ if (S.stopped) return; S.rows.push(snap()); S.frame++; S.raf = requestAnimationFrame(tick); }
  S.raf = requestAnimationFrame(tick);
  return true;
})()
"""

def run_once(pg, organic):
    pg.evaluate("window.__D ? (window.__D.rows = [], window.__D.frame = 0) : null")
    if pg.evaluate("(function(){return !window.__D;})()"):
        assert pg.evaluate(SAMPLER)
    if organic:
        pg.mouse.click(320, 200)
    else:
        pg.evaluate("(function(){window.WH_DEBUG.triggerAttack();})()")
    pg.wait_for_timeout(12000)
    rows = pg.evaluate("window.__D.rows")
    seq = [(r['f'], r['attacking'], r['state'], round(r['timer'],2), r['ci']) for r in rows]
    print(("organic" if organic else "trigger-hook"), "rows=%d" % len(rows), ":", seq[:25])

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"], headless=True)
    pg = b.new_page(viewport={"width": 640, "height": 400})
    pg.on("pageerror", lambda e: print("PAGEERROR:", e))
    pg.goto(BASE, wait_until="load", timeout=30000)
    for _ in range(60):
        if pg.evaluate("(function(){try{return typeof WH_DEBUG==='object' && !!WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()"): break
        pg.wait_for_timeout(400)
    pg.wait_for_timeout(1500)
    pg.evaluate("(function(){WH_DEBUG.teleportPlayer(2.5,74);WH_DEBUG.setCameraYaw(180);WH_DEBUG.setStamina(100);})()")
    pg.evaluate(SAMPLER)
    print("=== triggerAttack (hook) ===")
    run_once(pg, organic=False)
    time.sleep(1)
    print("=== organic click ===")
    run_once(pg, organic=True)
    b.close()
