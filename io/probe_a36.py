
import time, math
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
    page = b.new_page()
    page.goto("http://localhost:8791/builds/v7-playable.html")
    page.wait_for_timeout(3500)
    page.evaluate("window.WH_DEBUG.teleportPlayer(-6,-2)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.wait_for_timeout(200)
    h = page.evaluate_handle("(function(){var e=window.WH_DEBUG.getEnemy(0);return e?e.ref:null;})()")
    # wait for attack
    d0=time.time()
    while time.time()-d0<12:
        fsm = page.evaluate("(function(e){return e.fsm})", h)
        if fsm=="attack": break
        page.wait_for_timeout(5)
    print("fsm:", fsm, "after %.1fs" % (time.time()-d0))
    ph_reads=[]
    t0=time.time()
    teleported=False
    while time.time()-t0<8.0:
        ph = page.evaluate("(function(e){try{return e.attackPhase||null;}catch(x){return null;}})", h)
        if ph=="windup":
            wu = page.evaluate("(function(e){try{return e.attackPhaseT||0;}catch(x){return 0;}})", h)
            ph_reads.append(round(wu,2))
            if not teleported and wu>=0.5:
                info = page.evaluate("(function(e){return {x:e.pos.x,z:e.pos.z,yaw:e.yaw};})", h)
                d=1.2
                bx = info["x"] - math.sin(info["yaw"])*d
                bz = info["z"] - math.cos(info["yaw"])*d
                page.evaluate("window.WH_DEBUG.teleportPlayer(%r,%r)" % (bx,bz))
                teleported=True
                print("teleported to (%.2f,%.2f) enemy yaw=%.3f phT=%.2f" % (bx,bz,info["yaw"],wu))
        if teleported: break
        page.wait_for_timeout(3)
    print("teleported:", teleported, "| phT reads while windup:", ph_reads[:20], "..." if len(ph_reads)>20 else "")
    # watch for damage
    hp0 = page.evaluate("window.WH_DEBUG.getPlayer().hp")
    t1=time.time(); dmg=False
    while time.time()-t1<3.0:
        hp_ = page.evaluate("window.WH_DEBUG.getPlayer().hp")
        if hp_<hp0: dmg=True; break
        page.wait_for_timeout(5)
    print("damaged after rear teleport:", dmg)
    b.close()
