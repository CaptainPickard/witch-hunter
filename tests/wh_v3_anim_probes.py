"""Witch Hunter v3 animation probes (spec D5). Both origins.
Drives the game with real CDP keyboard/mouse input (page.keyboard / page.mouse);
synthetic JS KeyboardEvents do not reach the input layer.
Probes: attack stage sequence, strike lunge, cancel rules, layered walk,
ghoul hop arc, ground alignment. Zero page/console errors required.
"""
from playwright.sync_api import sync_playwright
import json, math, sys

ORIGINS = ["http://localhost:8791/", "http://localhost:8792/witchhunter/"]

JS_HELPERS = """
() => {
  const D = window.WH_DEBUG;
  if (!D) return null;
  return {
    hasStage: typeof D.getAttackStage === 'function',
    hasTrigger: typeof D.triggerAttack === 'function',
    hasRolling: typeof D.isRolling === 'function',
    hasEnemy: typeof D.getEnemy === 'function'
  };
}
"""

def probe_attack_stages(page):
    """Real mouse click starts the attack; sample stage over time."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.evaluate("window.WH_DEBUG.breakLockOn()")
    page.evaluate("window.WH_DEBUG.setStamina(100)")
    page.mouse.click(640, 360)          # left button = attack
    stages = []
    for _ in range(90):                 # ~900ms at 10ms poll
        s = page.evaluate("window.WH_DEBUG.getAttackStage()")
        if not stages or stages[-1] != s:
            stages.append(s)
        page.wait_for_timeout(10)
    # expect windup ... strike ... recover ... null
    ok = False
    if stages and stages[0] == 'windup':
        if 'strike' in stages and 'recover' in stages and stages[-1] is None:
            iw, is_, ir = stages.index('windup'), stages.index('strike'), stages.index('recover')
            ok = iw < is_ < ir
    print("  attack stage sequence: %s => %s" % (json.dumps(stages), "PASS" if ok else "FAIL"))
    return ok

def probe_strike_lunge(page):
    """During STRIKE, player root moves forward along facing by > 0.1."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.evaluate("window.WH_DEBUG.breakLockOn()")
    page.evaluate("window.WH_DEBUG.setStamina(100)")
    z0 = page.evaluate("window.WH_DEBUG.getPlayerPosition()['z']")
    page.mouse.click(640, 360)
    # poll z every 16ms for the strike window (0.15-0.275s) and just after
    min_z, max_z = z0, z0
    for _ in range(30):
        z = page.evaluate("window.WH_DEBUG.getPlayerPosition()['z']")
        min_z = min(min_z, z); max_z = max(max_z, z)
        page.wait_for_timeout(16)
    # camYaw=0 => facing -z => lunge decreases z
    lunge = z0 - min_z
    ok = lunge > 0.1
    print("  strike lunge: %.3f => %s" % (lunge, "PASS" if ok else "FAIL"))
    return ok

def probe_cancel_rules(page):
    # rule 1: roll during windup cancels the attack
    page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.evaluate("window.WH_DEBUG.breakLockOn()")
    page.evaluate("window.WH_DEBUG.setStamina(100)")
    page.mouse.click(640, 360)
    # windup = 0.15s of the 0.5s attack; click latency ~1 frame, wait ~60ms then roll
    page.wait_for_timeout(55)
    stage = page.evaluate("window.WH_DEBUG.getAttackStage()")
    page.keyboard.press("Space")
    page.wait_for_timeout(150)
    rolling = page.evaluate("window.WH_DEBUG.isRolling()")
    attacking = page.evaluate("window.WH_DEBUG.getPlayer()['attacking']")
    ok1 = stage == 'windup' and rolling and not attacking
    print("  cancel roll-in-windup: stage=%s rolling=%s attacking=%s => %s"
          % (stage, rolling, attacking, "PASS" if ok1 else "FAIL"))
    page.wait_for_timeout(600)   # let roll finish

    # rule 2: roll during strike does NOT cancel (deterministic: force the
    # attackTimer into the strike stage rather than racing click latency)
    det2 = page.evaluate("""(function(){
        var D = window.WH_DEBUG;
        var pl = D.getPlayer();
        D.setStamina(100);
        D.breakLockOn();
        pl.rolling = false; pl.rollTimer = 0;   // cancel any roll left from rule 1
        pl.tryAttack();
        pl.attackTimer = 0.5 - 0.2;
        var stage = pl.getAttackStage();
        var before = pl.attacking;
        pl.tryRoll();
        return { stage: stage, before: before, after: pl.attacking,
                 stageAfter: pl.getAttackStage() };
    })()""")
    stage = det2["stage"]; attacking = det2["after"]; stage_after = det2["stageAfter"]
    ok2 = (stage == "strike" and attacking and stage_after == "strike")
    print("  cancel roll-in-strike blocked: stage=%s attacking=%s after=%s => %s"
          % (stage, attacking, stage_after, "PASS" if ok2 else "FAIL"))
    page.wait_for_timeout(600)

    # rule 3: attack cannot start during roll (deterministic: no key race,
    # no reliance on a previous attack having fully elapsed under rAF throttle)
    det3 = page.evaluate("""(function(){
        var D = window.WH_DEBUG;
        var pl = D.getPlayer();
        // full deterministic reset before testing
        D.setStamina(100);
        D.breakLockOn();
        pl.rolling = false; pl.rollTimer = 0;
        pl.attacking = false; pl.attackTimer = 0; pl.comboIndex = 0;
        // part (a): attack must be REFUSED while rolling
        pl.rolling = true;
        pl.tryAttack();
        var tryAttackRefused = !pl.attacking && pl.getAttackStage() === null;
        // part (b): reset, then a fresh roll must start
        pl.rolling = false; pl.rollTimer = 0;
        pl.tryRoll();
        var freshRoll = pl.rolling === true && pl.attacking === false;
        return { tryAttackRefused: tryAttackRefused,
                 attackStageAfterRoll: pl.getAttackStage(),
                 freshRoll: freshRoll,
                 rollingAfterRoll: pl.rolling };
    })()""")
    ok3 = det3["tryAttackRefused"] and det3["freshRoll"]
    print("  attack during roll blocked: rolling=%s tryAttackRefused=%s freshRoll=%s => %s"
          % (det3["rollingAfterRoll"], det3["tryAttackRefused"],
             det3["freshRoll"], "PASS" if ok3 else "FAIL"))
    page.wait_for_timeout(500)
    return ok1 and ok2 and ok3

def probe_walk_layers(page):
    """Hold W for 1s: body.position.y p2p > 0.1 and > 2 local maxima."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.evaluate("window.WH_DEBUG.breakLockOn()")
    page.evaluate("window.WH_DEBUG.setStamina(100)")
    page.keyboard.down("w")
    ys = []
    for _ in range(60):   # ~1s at 16ms
        ys.append(page.evaluate("window.WH_DEBUG.getPlayer()['body']['position']['y']"))
        page.wait_for_timeout(16)
    page.keyboard.up("w")
    p2p = max(ys) - min(ys) if len(ys) > 2 else 0
    maxima = sum(1 for i in range(1, len(ys) - 1)
                 if ys[i] > ys[i-1] and ys[i] >= ys[i+1])
    ok = p2p > 0.1 and maxima > 2
    print("  walk p2p=%.3f maxima=%d samples=%d => %s"
          % (p2p, maxima, len(ys), "PASS" if ok else "FAIL"))
    return ok

def probe_ghoul_hop(page):
    """Move the PLAYER to the ghoul's spawn area so a natural chase->attack
    transition happens inside the ghoul's leash (teleporting the ghoul out
    of its leash makes it oscillate idle<->chase and never attack)."""
    page.evaluate("""
() => {
  const D = window.WH_DEBUG;
  const rm = D.getRegionManager();
  const list = rm.getEnemies(rm.logic.activeId);
  for (let i = 0; i < list.length; i++) {
    if (list[i].type === 'ghoul' && list[i].fsm !== 'dead') {
      const g = list[i];
      window.__ghoulIdx = i;
      // place the player just outside attack range at the ghoul's spawn
      D.teleportPlayer(g.pos.x + 1.5, g.pos.z + 1.5);
      break;
    }
  }
}
""")
    idx = page.evaluate("window.__ghoulIdx")
    if idx is None:
        print("  ghoul hop: no live ghoul => FAIL")
        return False
    ys = []
    for _ in range(120):       # ~2s wall
        y = page.evaluate("window.WH_DEBUG.getEnemy(window.__ghoulIdx)['y']")
        ys.append(y)
        page.wait_for_timeout(16)
    peak = max(ys) if ys else 0
    ok = peak > 0.20   # bob baseline ~0.05; arc apex 0.25, 16ms sampling may shave the apex
    print("  ghoul hop peak y=%.3f (n=%d) => %s" % (peak, len(ys), "PASS" if ok else "FAIL"))
    return ok

def probe_ground_align(page):
    res = page.evaluate("""
() => {
  const p = window.WH_DEBUG.getPlayer();
  const box = new THREE.Box3().setFromObject(p.root);
  return { minY: box.min.y, height: box.max.y - box.min.y };
}
""")
    ok = res["minY"] >= -0.05 and 1.7 <= res["height"] <= 1.9
    print("  ground align minY=%.3f height=%.3f => %s"
          % (res["minY"], res["height"], "PASS" if ok else "FAIL"))
    return ok

def run(page, origin):
    print("=== %s ===" % origin)
    errors, console_errors = [], []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.goto(origin, wait_until="load", timeout=30000)
    page.wait_for_timeout(12000)   # proxy origin loads GLBs slower; give it room
    hooks = page.evaluate(JS_HELPERS)
    ok_hooks = bool(hooks and all(hooks.values()))
    print("  v3 hooks present: %s => %s" % (hooks, "PASS" if ok_hooks else "FAIL"))

    results = {
        "hooks": ok_hooks,
        "stages": probe_attack_stages(page),
        "lunge": probe_strike_lunge(page),
        "cancel": probe_cancel_rules(page),
        "walk": probe_walk_layers(page),
        "hop": probe_ghoul_hop(page),
        "ground": probe_ground_align(page),
    }
    page.wait_for_timeout(300)
    ok_err = not errors and not console_errors
    print("  errors: page=%d console=%d => %s"
          % (len(errors), len(console_errors), "PASS" if ok_err else "FAIL"))
    results["errors"] = ok_err
    all_ok = all(results.values())
    print("  [%s] ALL PROBES: %s" % (origin, "PASS" if all_ok else "FAIL"))
    return all_ok, results

def main():
    all_ok = True
    summary = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
        for origin in ORIGINS:
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            ok, results = run(page, origin)
            all_ok = all_ok and ok
            summary[origin] = results
            page.close()
        browser.close()
    print("V3 ANIM PROBES: %s" % ("PASS" if all_ok else "FAIL"))
    print(json.dumps(summary, indent=1))
    sys.exit(0 if all_ok else 1)

main()