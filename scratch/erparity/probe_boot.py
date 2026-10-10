#!/usr/bin/env python3
"""Boot probe for EPR1 harness authoring: verify game boots at origin/dev worktree,
WH_DEBUG hooks live, rAF cadence, and Space keydown behavior (pre-build)."""
from playwright.sync_api import sync_playwright
import time, json, sys

BASE = 'http://127.0.0.1:8793/'

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"], headless=True)
        page = browser.new_page(viewport={"width": 640, "height": 400})
        errors = []
        cons = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: cons.append(m.text) if m.type == "error" else None)
        page.goto(BASE, wait_until="load", timeout=30000)
        t0 = time.time()
        ok = False
        while time.time() - t0 < 30:
            try:
                ok = page.evaluate(
                    "(function(){try{return typeof window.WH_DEBUG==='object' && "
                    "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
                    "!!window.WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()")
            except Exception:
                ok = False
            if ok:
                break
            page.wait_for_timeout(300)
        page.wait_for_timeout(1500)
        print('ready:', ok, 'elapsed', round(time.time() - t0, 1), 's')
        print('pageerrors:', errors)
        print('console errors:', cons[:5])
        if not ok:
            browser.close()
            return 1

        info = page.evaluate(
            "(function(){var d=window.WH_DEBUG;var p=d.getPlayer();return {"
            "pos:d.getPlayerPosition(),"
            "stage:d.getAttackStage(),"
            "rolling:(d.isRolling?d.isRolling():null),"
            "stamina:d.getStamina(),"
            "yaw:p.yaw, camYaw:p.camYaw,"
            "rollIW:d.getConfig().player.rollIFrameWindow,"
            "rollDur:d.getConfig().player.rollDuration,"
            "maxDt:d.getConfig().loop.maxDt,"
            "inputBufferSec:(window.WH_CONFIG.moveset?window.WH_CONFIG.moveset.inputBufferSec:null),"
            "attackTimer:p.attackTimer, attacking:!!p.attacking,"
            "hp:p.hp, offhand:p.offhand, toggling:!!p.toggling"
            "};})()")
        print('state:', json.dumps(info, indent=2))

        # cadence probe
        page.evaluate(
            "(function(){window.__IO_F={n:0,t0:performance.now(),last:0};"
            "var f=function(t){window.__IO_F.n++;window.__IO_F.last=t;requestAnimationFrame(f);};"
            "requestAnimationFrame(f);})()")
        page.wait_for_timeout(2000)
        m = page.evaluate("(function(){var s=window.__IO_F;return {n:s.n, wall:(s.last-s.t0)/1000};})()")
        print('rAF cadence: %d frames over %.2f s wall (%.1f fps)' % (m['n'], m['wall'], m['n'] / max(m['wall'], 0.01)))

        # organic Space press -> expected: roll fires on keyDOWN (pre-build)
        page.evaluate("window.__IO_F.n=0;")  # reset frame counter
        pre = page.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();return {rolling:p.rolling,iframes:p.iframes};})()")
        page.keyboard.down('Space')
        page.wait_for_timeout(400)  # a few frames
        mid = page.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();var f=window.__IO_F.n;return {rolling:p.rolling, rollTimer:p.rollTimer, iframes:p.iframes, frames:f};})()")
        page.keyboard.up('Space')
        page.wait_for_timeout(1500)
        post = page.evaluate("(function(){var p=window.WH_DEBUG.getPlayer();var f=window.__IO_F.n;return {rolling:p.rolling, iframes:p.iframes, frames:f};})()")
        print('pre-Space :', pre)
        print('during    :', mid)
        print('post      :', post)

        # organic LMB -> swing
        page.evaluate("window.__IO_F.n=0;")
        page.mouse.click(320, 200)
        page.wait_for_timeout(300)
        atk = page.evaluate("(function(){var d=window.WH_DEBUG;var p=d.getPlayer();return {attacking:p.attacking, stage:d.getAttackStage(), comboIdx:d.getComboIndex(), frames:window.__IO_F.n};})()")
        print('post-LMB  :', atk)
        browser.close()
        return 0

if __name__ == '__main__':
    sys.exit(main())
