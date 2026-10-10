#!/usr/bin/env python3
"""Diag: what does getMoveDef() report pre-build after one LMB?"""
from playwright.sync_api import sync_playwright
import time
BASE = "http://127.0.0.1:8793/"
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"], headless=True)
    pg = b.new_page(viewport={"width": 640, "height": 400})
    pg.goto(BASE, wait_until="load", timeout=30000)
    for _ in range(60):
        ok = pg.evaluate("(function(){try{return typeof WH_DEBUG==='object' && !!WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()")
        if ok: break
        pg.wait_for_timeout(400)
    pg.wait_for_timeout(1500)
    pg.evaluate("(function(){WH_DEBUG.teleportPlayer(2.5,74);WH_DEBUG.setCameraYaw(180);WH_DEBUG.setStamina(100);})()")
    print("pre-LMB getMoveDef:", pg.evaluate("(function(){try{return WH_DEBUG.getMoveDef();}catch(e){return String(e);}})()"))
    pg.mouse.click(320, 200)
    for i in range(28):
        md = pg.evaluate("(function(){try{return WH_DEBUG.getMoveDef();}catch(e){return null;}})()")
        p  = pg.evaluate("(function(){var p=WH_DEBUG.getPlayer();return {a:p.attacking, at:p.attackTimer, att:p.attackTotal};})()")
        print(i, md and (md.get('moveId'), md.get('phase') and md['phase'].get('stage')), p)
        if p and not p['a']:
            break
        pg.wait_for_timeout(500)
    b.close()
