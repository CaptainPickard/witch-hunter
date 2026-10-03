# A3 in-combat kill matrix (IO 10-02): kill bandit0 while AGGRO (A3's exact
# flow: teleport adjacent, wait, takeDamage mid-chase, sample corpse over
# wall time). Runs against BOTH 8793 (R2 tree) and 8791 (dev tree).
from playwright.sync_api import sync_playwright
import json, time, sys

KILL_JS = """(function(){
  var rm=window.WH_DEBUG.getRegionManager();
  var list=rm.enemies[rm.logic.activeId]||[];
  var e=list[0]; if(!e) return null;
  var b=new THREE.Box3().setFromObject(e.root);
  return {fsm:e.fsm,minY:b.min.y,deadFall:e.deadFall,t:e.fsmTime};
})()"""

def run(base, label):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 960, "height": 600})
        page.goto(base + "index.html", wait_until="load", timeout=30000)
        for _ in range(80):
            try:
                if page.evaluate("!!window.WH_DEBUG && !!window.WH_DEBUG.getPlayerPosition()"):
                    break
            except Exception:
                pass
            page.wait_for_timeout(250)
        page.wait_for_timeout(1000)
        # A3 exact: teleport next to bandit0
        page.evaluate("(function(){var C=window.WH_CONFIG;"
                      "var e=C.regionA.enemies[0];"
                      "window.WH_DEBUG.teleportPlayer(e.x+2, e.z);})()")
        page.wait_for_timeout(3000)   # let it aggro + reach the player
        st0 = page.evaluate(KILL_JS)
        print(label, "PRE-KILL:", json.dumps(st0))
        # kill mid-combat (same hook A3 falls back to)
        page.evaluate("(function(){var rm=window.WH_DEBUG.getRegionManager();"
                      "var l=rm.enemies[rm.logic.activeId]||[];"
                      "if(l[0])l[0].takeDamage(99999);})()")
        # sample corpse over 25s wall (A3's budget is 3.5s)
        rows = []
        t_end = time.time() + 25
        while time.time() < t_end:
            r = page.evaluate(KILL_JS)
            if r and r.get("fsm") == "dead":
                rows.append({"tw": round(len(rows), 1),
                             "minY": round(r["minY"], 3),
                             "deadFall": r.get("deadFall")})
            page.wait_for_timeout(1000)
        print(label, "SETTLE:", json.dumps(rows))
        print(label, "FINAL:", json.dumps(rows[-1]))
        browser.close()

run("http://localhost:8793/", "R2TREE")
run("http://localhost:8791/", "DEVTREE")