"""Probe wheel + touch-pad mechanics against live v7 build."""
from playwright.sync_api import sync_playwright
import subprocess, sys, time, urllib.request

proc = subprocess.Popen([sys.executable, "server.py", "8794"],
                        cwd="/workspace/witch-hunter/prototype",
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(30):
    try:
        urllib.request.urlopen("http://localhost:8794/", timeout=1); break
    except Exception: time.sleep(0.3)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1280, "height": 800})
    pg.on("console", lambda m: print("console[%s]: %s" % (m.type, m.text[:100])) if m.type == "error" else None)
    pg.goto("http://localhost:8794/builds/v7-playable.html")
    pg.wait_for_timeout(4000)
    st = pg.evaluate("""(() => { const P = window.WH_DEBUG && window.WH_DEBUG.getPlayer();
        return { dist: P ? P.camDist : null, yaw: P ? P.camYaw : null,
                 touchVisible: window.WH_TouchControls ? window.WH_TouchControls.isVisible() : null,
                 touchExists: !!window.WH_TouchControls,
                 touchEnabled: window.WH_CONFIG && WH_CONFIG.touch ? WH_CONFIG.touch.enabled : null }; })()""")
    print("pre:", st)
    pg.mouse.move(640, 400)
    pg.mouse.wheel(0, 120); pg.wait_for_timeout(200)
    d1 = pg.evaluate("window.WH_DEBUG.getPlayer().camDist")
    print("after CDP wheel +120:", d1)
    pg.mouse.wheel(0, -240); pg.wait_for_timeout(200)
    d2 = pg.evaluate("window.WH_DEBUG.getPlayer().camDist")
    print("after CDP wheel -240:", d2)
    # wheel event sanity: does a WheelEvent reach document at all?
    pg.evaluate("window.__wcnt = 0; document.addEventListener('wheel', () => window.__wcnt++, {passive:true})")
    pg.mouse.wheel(0, 100); pg.wait_for_timeout(150)
    print("wheel event count after CDP wheel:", pg.evaluate("window.__wcnt"))
    # touch pad: force show via public API then locate cam pad and drag
    vis = pg.evaluate("window.WH_TouchControls.show(); window.WH_TouchControls.isVisible()")
    print("after show():", vis)
    pg.wait_for_timeout(300)
    info = pg.evaluate("""(() => {
      const lay = document.getElementById('wh-touch-layer');
      const r = lay ? lay.getBoundingClientRect() : null;
      const cands = lay ? lay.querySelectorAll('*') : [];
      const boxes = [];
      for (const c of cands) {
        const b = c.getBoundingClientRect();
        if (b.width > 40 && b.height > 40 && b.width < 300 && b.left < 200) boxes.push({cls: c.className && String(c.className).slice(0,30), id: c.id, x: Math.round(b.x+b.width/2), y: Math.round(b.y+b.height/2), w: Math.round(b.width)});
      }
      return { layer: !!lay, rect: r ? {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)} : null, boxes: boxes.slice(0,10) }; })()""")
    print("layer:", info)
    b.close()
proc.terminate()
print("done")