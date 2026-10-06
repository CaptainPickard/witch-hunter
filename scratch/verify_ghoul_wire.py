#!/usr/bin/env python3
"""Round A ghoul Mixamo wiring validation (io/astrabot-brief-ghoul-wire.md).

    python3 scratch/verify_ghoul_wire.py

Starts prototype/server.py on a scratch port, loads prototype/index.html in
headless chromium (playwright, --no-sandbox, headless=new) and checks:
  0. syntax: every edited JS file compiles (new Function) in chromium
  1. ghoul: 13 clips; rest WH_Idle_Zombie; walk-home WH_Walk_Zombie; chase
     WH_Run_Zombie; attack WH_Attack_Zombie; damage WH_Hit_Zombie; death
     WH_Death (never WH_Death_Zombie)
  2. fallback: zombie variant on a clip list missing WH_Walk_Zombie falls back
     to WH_Walk
  3. bandit: default map only (WH_Idle ..., no *_Zombie)
  4. player: chain clips resolve, attack plays a chain clip
  5. no console errors / pageerrors
Evidence -> scratch/ghoul-wire-evidence/. Exit 0 only if all pass.
"""
import json
import os
import socket
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "scratch", "ghoul-wire-evidence")
CHROME = os.path.expanduser(
    "~/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome")
JS_FILES = ["prototype/js/anim.js", "prototype/js/enemy.js", "prototype/js/assets.js"]
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"check": name, "pass": bool(ok), "detail": detail})
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


# Page-side helpers: spawn an enemy exactly like RegionManager.buildRegion
# does, then sample its anim state every rAF into a window buffer.
SETUP = r"""
(function(){
  var rm = window.WH_DEBUG.getRegionManager();
  var CFG = window.WH_CONFIG;
  window.__GW = {rows: {}, enemies: {}};
  window.__GW.spawn = function(tag, type, x, z){
    var rid = rm.logic.activeId;
    var enemy = new window.WH_Enemy(type, rm.scene, rid, x, z);
    var bodyName = type === 'bandit' ? 'banditBody' : 'ghoulBody';
    var eBody = window.WH_ASSETS.instance(bodyName);
    var eScale = CFG.world.characterHeight /
      (window.WH_ASSETS.groundHeight(bodyName) || CFG.world.characterHeight);
    eBody.scale.setScalar(eScale);
    eBody.position.y = -(window.WH_ASSETS.groundMinY(bodyName) * eScale);
    eBody.children[0].position.y += window.WH_ASSETS.groundMinY(bodyName);
    enemy.setBody(eBody);
    rm.enemies[rid].push(enemy);
    rm.groups[rid].add(enemy.root);
    window.__GW.enemies[tag] = enemy;
    window.__GW.rows[tag] = [];
    return {clips: window.WH_ASSETS.getClips(bodyName).map(function(c){return c.name;}),
            hasAnim: !!enemy.anim,
            names: enemy.anim ? enemy.anim.names : null,
            moveNames: enemy.anim ? enemy.anim.moveNames : null,
            actions: enemy.anim ? Object.keys(enemy.anim.actions) : null};
  };
  function tick(){
    Object.keys(window.__GW.enemies).forEach(function(tag){
      var e = window.__GW.enemies[tag];
      if (!e.anim) return;
      var s = e.anim.getState();
      var active = Object.keys(s.weights).filter(function(k){return s.weights[k] > 0;});
      window.__GW.rows[tag].push({t: +(performance.now()/1000).toFixed(3), fsm: e.fsm,
        clip: s.clip, active: active, speed: +(e.animMoveSpeed||0).toFixed(2)});
    });
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  return true;
})()
"""


def rows_since(page, tag, t0):
    return page.evaluate(
        "(function(t,t0){return window.__GW.rows[t].filter(function(r){return r.t>=t0;});})"
        "('%s', %f)" % (tag, t0))


def poll(page, tag, t0, pred, timeout_s):
    """Headless swiftshader runs ~1-2 fps (baseline too), so phases wait on
    the sampled condition rather than a fixed wall-clock budget."""
    deadline = time.time() + timeout_s
    while True:
        r = rows_since(page, tag, t0)
        if any(pred(x) for x in r) or time.time() > deadline:
            return r
        page.wait_for_timeout(500)


def now(page):
    return page.evaluate("performance.now()/1000")


def clips_seen(rows):
    seen = []
    for r in rows:
        if r["clip"] not in seen:
            seen.append(r["clip"])
    return seen


def main():
    os.makedirs(OUT, exist_ok=True)
    port = free_port()
    srv = subprocess.Popen([sys.executable, os.path.join(REPO, "prototype", "server.py"),
                            str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = "http://127.0.0.1:%d/" % port
    console_errors, page_errors, warns = [], [], []
    evidence = {"url": url, "head": subprocess.run(
        ["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True).stdout.strip()}
    try:
        time.sleep(0.8)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=CHROME if os.path.exists(CHROME) else None,
                headless=True,
                args=["--no-sandbox", "--headless=new", "--enable-unsafe-swiftshader",
                      "--use-gl=angle", "--use-angle=swiftshader"])
            page = browser.new_page(viewport={"width": 960, "height": 600})
            page.on("console", lambda m: console_errors.append(
                "%s @ %s" % (m.text, m.location.get("url"))) if m.type == "error" else
                (warns.append(m.text) if m.type == "warning" else None))
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            http_errors = []
            page.on("response", lambda r: r.status >= 400 and http_errors.append(
                "%d %s" % (r.status, r.url)))

            # 0. syntax
            page.goto(url + "js/anim.js")  # same origin for fetch
            syn = {}
            for f in JS_FILES:
                rel = f.replace("prototype/", "")
                syn[f] = page.evaluate(
                    "(async function(u){var s=await (await fetch(u)).text();"
                    "try{new Function(s);return 'ok';}catch(e){return String(e);}})('%s')"
                    % (url + rel))
                check("syntax:" + f, syn[f] == "ok", syn[f])
            evidence["syntax"] = syn

            page.goto(url, wait_until="load", timeout=60000)
            deadline = time.time() + 90
            ready = False
            while time.time() < deadline:
                ready = page.evaluate(
                    "(function(){try{return !!(window.WH_DEBUG && window.WH_DEBUG.getPlayer()"
                    " && window.WH_DEBUG.getPlayer().anim && window.WH_ASSETS.getClips('ghoulBody')"
                    ".length && window.WH_ASSETS.getClips('banditBody').length);}catch(e){return false;}})()")
                if ready:
                    break
                page.wait_for_timeout(500)
            check("boot", ready, "WH_DEBUG + player anim + ghoul/bandit clips loaded")
            page.wait_for_timeout(1500)
            page.evaluate(SETUP)
            # Park the player far away so spawned enemies stay out of sight.
            pp = page.evaluate("WH_DEBUG.getPlayerPosition()")
            sight = page.evaluate("WH_CONFIG.enemy.ghoul.sightRadius")
            evidence["ghoulSightRadius"] = sight
            gx, gz = pp["x"] + sight + 15, pp["z"]

            # 1. ghoul
            g = page.evaluate("__GW.spawn('ghoul','ghoul',%f,%f)" % (gx, gz))
            evidence["ghoulSpawn"] = g
            check("ghoul:clips==13", len(g["clips"]) == 13, "%d %s" % (len(g["clips"]), g["clips"]))
            check("ghoul:names", g["names"] == {
                "idle": "WH_Idle_Zombie", "walk": "WH_Walk_Zombie", "run": "WH_Run_Zombie",
                "attack": "WH_Attack_Zombie", "hit": "WH_Hit_Zombie", "death": "WH_Death"},
                json.dumps(g["names"]))
            check("ghoul:no-move-clips", g["moveNames"] == {}
                  and not any(a in g["actions"] for a in ("slashR2L", "slashL2R", "thrust")),
                  "actions=%s" % g["actions"])
            phases = {}

            t0 = now(page)
            r = poll(page, "ghoul", t0, lambda x: False, 6)
            phases["rest"] = r
            check("ghoul:rest->WH_Idle_Zombie",
                  r and all(x["clip"] == "WH_Idle_Zombie" for x in r[-20:])
                  and "WH_Idle_Zombie" in r[-1]["active"],
                  "seen=%s fsm=%s" % (clips_seen(r), r[-1]["fsm"] if r else None))
            page.screenshot(path=os.path.join(OUT, "ghoul-idle.png"))

            # walk home: displace the ghoul 8 m from its spawn while unseen
            t0 = now(page)
            page.evaluate("(function(){var e=__GW.enemies.ghoul; e.pos.x += 8;})()")
            r = poll(page, "ghoul", t0, lambda x: x["clip"] == "WH_Walk_Zombie", 60)
            phases["walk"] = r
            check("ghoul:walk->WH_Walk_Zombie",
                  any(x["clip"] == "WH_Walk_Zombie" and "WH_Walk_Zombie" in x["active"] for x in r),
                  "seen=%s fsms=%s" % (clips_seen(r), sorted(set(x["fsm"] for x in r))))

            # chase: bring the player into sight but outside attack range
            t0 = now(page)
            page.evaluate("(function(){var e=__GW.enemies.ghoul;"
                          "WH_DEBUG.teleportPlayer(e.pos.x - 9, e.pos.z);})()")
            r = poll(page, "ghoul", t0, lambda x: x["clip"] == "WH_Run_Zombie", 60)
            phases["run"] = r
            check("ghoul:chase->WH_Run_Zombie",
                  any(x["clip"] == "WH_Run_Zombie" and "WH_Run_Zombie" in x["active"] for x in r),
                  "seen=%s fsms=%s" % (clips_seen(r), sorted(set(x["fsm"] for x in r))))
            page.screenshot(path=os.path.join(OUT, "ghoul-run.png"))

            # attack: let it close the distance
            t0 = now(page)
            r = poll(page, "ghoul", t0,
                     lambda x: x["fsm"] == "attack" and x["clip"] == "WH_Attack_Zombie", 120)
            phases["attack"] = r
            check("ghoul:attack->WH_Attack_Zombie",
                  any(x["fsm"] == "attack" and x["clip"] == "WH_Attack_Zombie" for x in r),
                  "seen=%s fsms=%s" % (clips_seen(r), sorted(set(x["fsm"] for x in r))))
            page.screenshot(path=os.path.join(OUT, "ghoul-attack.png"))

            # hit: forced non-lethal damage
            t0 = now(page)
            page.evaluate("(function(){var e=__GW.enemies.ghoul; e.hp = e.hpMax;"
                          "e.takeDamage(1, {x:1, z:0});})()")
            r = poll(page, "ghoul", t0, lambda x: x["clip"] == "WH_Hit_Zombie", 30)
            phases["hit"] = r
            check("ghoul:damage->WH_Hit_Zombie",
                  any(x["clip"] == "WH_Hit_Zombie" and "WH_Hit_Zombie" in x["active"] for x in r),
                  "seen=%s" % clips_seen(r))
            page.screenshot(path=os.path.join(OUT, "ghoul-hit.png"))

            # death: lethal damage
            t0 = now(page)
            page.evaluate("(function(){var e=__GW.enemies.ghoul; e.takeDamage(99999, {x:1, z:0});})()")
            deadline = time.time() + 180
            while time.time() < deadline and page.evaluate(
                    "__GW.enemies.ghoul.corpseFinalY === null"):
                page.wait_for_timeout(1000)
            r = rows_since(page, "ghoul", t0)
            phases["death"] = r
            dz = any("WH_Death_Zombie" in (x["clip"] or "") or "WH_Death_Zombie" in x["active"]
                     for rows in phases.values() for x in rows)
            corpse = page.evaluate("(function(){var e=__GW.enemies.ghoul;"
                                   "return {fsm:e.fsm, deadFall:e.deadFall, corpseFinalY:e.corpseFinalY};})()")
            evidence["ghoulCorpse"] = corpse
            check("ghoul:death->WH_Death",
                  r and r[-1]["clip"] == "WH_Death" and r[-1]["fsm"] == "dead" and not dz,
                  "seen=%s deathZombieEver=%s corpse=%s" % (clips_seen(r), dz, corpse))
            check("ghoul:corpse-settles", corpse["deadFall"] == 1 and corpse["corpseFinalY"] is not None,
                  json.dumps(corpse))
            page.screenshot(path=os.path.join(OUT, "ghoul-death.png"))
            evidence["ghoulPhases"] = {k: {"clipsSeen": clips_seen(v), "frames": len(v),
                                           "fsms": sorted(set(x["fsm"] for x in v)),
                                           "sample": v[::max(1, len(v) // 12)]}
                                       for k, v in phases.items()}

            # 2. fallback safety
            fb = page.evaluate(r"""(function(){
              var clips = WH_ASSETS.getClips('ghoulBody').filter(function(c){
                return c.name !== 'WH_Walk_Zombie';});
              var body = WH_ASSETS.instance('ghoulBody');
              var a = new WH_CharacterAnim(body, clips, {variant: 'zombie'});
              return {names: a.names, actions: Object.keys(a.actions)};
            })()""")
            evidence["fallback"] = fb
            check("fallback:missing-WH_Walk_Zombie->WH_Walk",
                  fb["names"].get("walk") == "WH_Walk" and "walk" in fb["actions"]
                  and fb["names"].get("idle") == "WH_Idle_Zombie", json.dumps(fb["names"]))
            check("fallback:warned", any("falling back to WH_Walk" in w for w in warns),
                  [w for w in warns if "WH anim" in w][-3:])

            # 3. bandit legacy map
            pp = page.evaluate("WH_DEBUG.getPlayerPosition()")
            b = page.evaluate("__GW.spawn('bandit','bandit',%f,%f)" % (pp["x"] - 60, pp["z"] + 60))
            t0 = now(page)
            r = poll(page, "bandit", t0, lambda x: False, 6)
            evidence["bandit"] = dict(b, clipsSeen=clips_seen(r))
            legacy = {"idle": "WH_Idle", "walk": "WH_Walk", "run": "WH_Run",
                      "attack": "WH_Attack1", "hit": "WH_Hit", "death": "WH_Death"}
            check("bandit:legacy-map", b["names"] == legacy, json.dumps(b["names"]))
            check("bandit:plays-legacy-clips-only", r and r[0]["clip"] == "WH_Idle"
                  and all(x["clip"] in legacy.values() for x in r)
                  and not any("Zombie" in a for x in r for a in x["active"]),
                  "seen=%s" % clips_seen(r))

            # 4. player chain smoke
            pl = page.evaluate("""(function(){var a=WH_DEBUG.getPlayer().anim;
              return {names:a.names, moveNames:a.moveNames, actions:Object.keys(a.actions)};})()""")
            page.evaluate("WH_DEBUG.teleportPlayer(%f,%f)" % (pp["x"] - 60, pp["z"] - 60))
            page.wait_for_timeout(300)
            page.evaluate("WH_DEBUG.triggerAttack()")
            seen = []
            for _ in range(20):
                page.wait_for_timeout(500)
                c = page.evaluate("WH_DEBUG.getAnimState().clip")
                if c not in seen:
                    seen.append(c)
            pl["attackClipsSeen"] = seen
            evidence["player"] = pl
            check("player:chain-clips-resolve",
                  all(m in pl["actions"] for m in ("slashR2L", "slashL2R", "thrust"))
                  and pl["moveNames"] == {"slashR2L": "WH_SlashR2L", "slashL2R": "WH_SlashL2R",
                                          "thrust": "WH_Thrust"}
                  and pl["names"]["idle"] == "WH_Idle", json.dumps(pl["actions"]))
            check("player:attack-plays-chain-clip",
                  any(c in ("WH_SlashR2L", "WH_SlashL2R", "WH_Thrust") for c in seen), seen)
            page.screenshot(path=os.path.join(OUT, "player-bandit-smoke.png"))

            # 5. console
            evidence["consoleErrors"] = console_errors
            evidence["pageErrors"] = page_errors
            evidence["httpErrors"] = http_errors
            evidence["animWarnings"] = [w for w in warns if "WH anim" in w]
            # The browser's own /favicon.ico probe 404s (repo ships none); it is
            # recorded above but is not a game error.
            game_errors = [c for c in console_errors if "/favicon.ico" not in c]
            evidence["consoleErrorsExclFavicon"] = game_errors
            check("console:no-errors", not game_errors and not page_errors,
                  "console=%s page=%s http=%s" % (console_errors[:5], page_errors[:5], http_errors[:5]))
            browser.close()
    finally:
        srv.terminate()
    evidence["results"] = RESULTS
    evidence["allPass"] = all(r["pass"] for r in RESULTS)
    with open(os.path.join(OUT, "ghoul-wire-evidence.json"), "w") as f:
        json.dump(evidence, f, indent=1)
    print("evidence:", os.path.join(OUT, "ghoul-wire-evidence.json"),
          "allPass=%s (%d/%d)" % (evidence["allPass"],
                                   sum(r["pass"] for r in RESULTS), len(RESULTS)))
    return 0 if evidence["allPass"] else 1


if __name__ == "__main__":
    sys.exit(main())
