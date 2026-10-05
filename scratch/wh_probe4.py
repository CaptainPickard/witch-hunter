import sys
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 800, "height": 600})
    pg.goto("http://localhost:8791/scratch/pl_probe.html")
    pg.evaluate("window.__EV.moves = []; window.__EV.lockedMoves = 0")
    pg.evaluate("(() => { var c=document.getElementById('c'); var r=c.requestPointerLock(); })()")
    pg.wait_for_timeout(400)

    # 1) can a dispatched MouseEvent carry movementX to a real listener?
    pg.evaluate("""(() => {
      window.__disp = 0; window.__dispMv = null;
      document.addEventListener('mousemove', function(e){
        window.__disp++; window.__dispMv = {mx: e.movementX, my: e.movementY, trusted: e.isTrusted};
      }, true);
      var ev = new MouseEvent('mousemove', {movementX: 137, movementY: -42, bubbles: true});
      document.dispatchEvent(ev);
    })()""")
    d = pg.evaluate("({c: window.__disp, mv: window.__dispMv})")
    print("dispatch-carries-movementX:", d)

    # 2) does a real page.mouse.click on the chip position hit the chip (hit-testing) while locked?
    pg.evaluate("""(() => {
      var chip = document.createElement('div');
      chip.id = 'wh-mouse-chip';
      chip.style.cssText = 'position:fixed;bottom:14px;right:16px;width:120px;height:26px;z-index:60;pointer-events:auto;background:#333;color=#fff;';
      document.body.appendChild(chip);
      window.__chipClicks = 0;
      chip.addEventListener('click', function(){ window.__chipClicks++; });
    })()""")
    chip = pg.query_selector("#wh-mouse-chip")
    box = chip.bounding_box()
    if box:
        pg.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    pg.wait_for_timeout(150)
    print("chip clicks while pointer-locked:", pg.evaluate("window.__chipClicks"))

    # 3) unbound LMB on the canvas region: does a real click on canvas fire on canvas (baseline)?
    pg.evaluate("window.__canvasClicks = 0")
    pg.evaluate("document.getElementById('c').addEventListener('click', function(){ window.__canvasClicks++; })")
    pg.mouse.click(300, 200)
    pg.wait_for_timeout(150)
    print("canvas clicks:", pg.evaluate("window.__canvasClicks"))
    b.close()
print("probe4 done")