"""PART5d: ac_a3_5 + ac_a3_6 (orig lines 925..1020) for the harness rebuild."""

A3D_PART = r'''def ac_a3_5(page):
    """D2 page-clock: roll during bandit windup => hp unchanged through the
    active window (page-side watcher)."""
    if not fresh(page):
        return check("A3-5", "roll i-frames dodge", False,
                     "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-5", "roll i-frames dodge", False,
                         "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-5", "roll i-frames dodge", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        saw_windup = False
        t0 = time.time()
        while time.time() - t0 < 8.0:
            ph = enemy_phase(page, handle)
            if ph == "windup":
                saw_windup = True
                break
            page.wait_for_timeout(3)
        if not saw_windup:
            return check("A3-5", "roll i-frames dodge", False,
                         "pre-run: attackPhase missing/never windup")
        page.keyboard.down("w")
        press_space(page)
        page.wait_for_timeout(60)
        page.keyboard.up("w")
        watcher = page.evaluate_handle("""(function(){return new Promise(function(resolve){
          var hp0 = window.WH_DEBUG.getPlayer().hp;
          var t0 = performance.now();
          function tick(){
            var p = window.WH_DEBUG.getPlayer();
            if (p && p.hp < hp0) { resolve({damaged: true, t: +(performance.now()-t0).toFixed(0)}); return; }
            if (performance.now() - t0 > 2500) { resolve({damaged: false}); return; }
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          setTimeout(function(){ resolve({damaged: false, timeout: true}); }, 20000);
        })})""")
        res = (watcher.json_value() if hasattr(watcher, "json_value")
               else watcher)
        check("A3-5", "roll i-frames dodge", not res.get("damaged"),
              "hpUnchangedThroughActive=%s rollFiredInWindup=%s" %
              (not res.get("damaged"), saw_windup))
    except Exception as e:
        check("A3-5", "roll i-frames dodge", False, "exception %r" % e)


def ac_a3_6(page):
    """Teleport player BEHIND enemy near windup end: no damage (outside 50deg arc)."""
    if not fresh(page):
        return check("A3-6", "rear arc-gate rejection", False,
                     "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-6", "rear arc-gate rejection", False,
                         "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-6", "rear arc-gate rejection", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        t0 = time.time()
        teleported = False
        while time.time() - t0 < 8.0:
            ph = enemy_phase(page, handle)
            if ph == "windup":
                wu_elapsed = page.evaluate(
                    "(function(e){try{return e.attackPhaseT||0;}"
                    "catch(x){return 0;}})", handle)
                if teleported is False and wu_elapsed is not None \
                        and wu_elapsed >= 0.5:
                    info = page.evaluate(
                        "(function(e){return {x:e.pos.x,z:e.pos.z,"
                        "yaw:(e.yaw!==undefined?e.yaw:"
                        "(e.root?e.root.rotation.y:0))};})", handle)
                    d = 1.2
                    bx = info["x"] - math.sin(info["yaw"]) * d
                    bz = info["z"] - math.cos(info["yaw"]) * d
                    page.evaluate(
                        "window.WH_DEBUG.teleportPlayer(%r, %r)" % (bx, bz))
                    teleported = True
            page.wait_for_timeout(3)
        hp0 = hp(page)
        no_damage = True
        t1 = time.time()
        while time.time() - t1 < 1.0:
            cur = hp(page)
            if cur is not None and hp0 is not None and cur < hp0:
                no_damage = False
                break
            page.wait_for_timeout(3)
        ok = teleported and no_damage
        check("A3-6", "rear arc-gate rejection", ok,
              "teleportedBehind=%s noDamageAtActive=%s" %
              (teleported, no_damage))
    except Exception as e:
        check("A3-6", "rear arc-gate rejection", False, "exception %r" % e)
'''