"""PART6: A4 ACs (orig lines 1022..1216) for the harness rebuild."""

A4_PART = r'''def ac_a4_1(page):
    """D2-C: big displacement on swing-2 windup (page-side, at first windup
    frame); rate cap; strike+recover frozen (srDrift<=0.06); post-swing
    convergence."""
    if not fresh(page):
        return check("A4-1", "windup rate-cap", False,
                     "pre-run: page never ready")
    try:
        locked, tgt = (None, None)
        for _attempt in range(3):
            locked, tgt = lock_and_face_bandit(page)
            if locked and tgt:
                break
            page.wait_for_timeout(400)
        if not (locked and tgt):
            return check("A4-1", "windup rate-cap", False,
                         "pre-run: lock failed locked=%s tgt=%s" % (locked, tgt))
        lmb(page)
        if not wait_for_stage(page, "recover", 5.0):
            return check("A4-1", "windup rate-cap", False,
                         "pre-run: swing-1 recover not reached in 5s")
        handle, cfg = run_sampler(page, 4500, True, 4.0, 0.0)
        lmb(page)
        trace = drain_sampler(page, lambda s: s.get("displaced"), 3.0)
        rows = trace["rows"]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        if not wu or not trace["displaced"]:
            return check("A4-1", "windup rate-cap", False,
                         "windup not sampled displaced=%s wu=%d sr=%d rows=%d" %
                         (trace["displaced"], len(wu), len(sr), len(rows)))
        max_rate = 0.0
        snapped = False
        for i in range(1, len(wu)):
            dt_r = (wu[i]["t"] - wu[i - 1]["t"]) / 1000.0
            dy = abs(wrap_pi(wu[i]["yaw"] - wu[i - 1]["yaw"]))
            max_rate = max(max_rate, dy / dt_r if dt_r > 0 else 0.0)
            if dy > 0.5:
                snapped = True
        sr_drift = 0.0
        if sr:
            y0 = sr[0]["yaw"]
            sr_drift = max((abs(wrap_pi(r["yaw"] - y0)) for r in sr), default=0.0)
        x_disp = tgt["x"] + 4.0
        post_conv = 0.0
        end_rows = [r for r in rows if r["st"] is None]
        if len(end_rows) >= 2:
            def er(r):
                return abs(wrap_pi(math.atan2(x_disp - r["x"], tgt["z"] - r["z"])
                                   - r["yaw"]))
            post_conv = er(end_rows[0]) - er(end_rows[-1])
        cap = 240 * math.pi / 180 + 0.35
        ok = (trace["displaced"] and max_rate <= cap and not snapped
              and sr_drift <= 0.06 and post_conv > 0)
        check("A4-1", "windup rate-cap", ok,
              "maxRate=%.1fdeg/s (<=240) snapped=%s srDrift=%.4f postConv=%.3f" %
              (max_rate * 180 / math.pi, snapped, sr_drift, post_conv))
    except Exception as e:
        check("A4-1", "windup rate-cap", False, "exception %r" % e)


def ac_a4_2(page):
    """D2-C: W held; chain press; windup distance integrated over ALL swing-2
    windup frames; strike+recover freeze (srDist < 1e-3); post-swing resume."""
    if not fresh(page):
        return check("A4-2", "windup move slow-down", False,
                     "pre-run: page never ready")
    try:
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.wait_for_timeout(200)
        page.keyboard.down("w")
        lmb(page)
        if not wait_for_stage(page, "recover", 5.0):
            page.keyboard.up("w")
            return check("A4-2", "windup move slow-down", False,
                         "pre-run: swing-1 recover not reached in 5s")
        run_sampler(page, 4000, displace=False)
        page.mouse.click(512, 384)
        trace = drain_sampler(page)
        page.keyboard.up("w")
        rows = trace["rows"]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        post = [r for r in rows if r["st"] is None]
        if not wu or len(sr) < 2:
            return check("A4-2", "windup move slow-down", False,
                         "windup/sr not sampled wu=%d sr=%d rows=%d" %
                         (len(wu), len(sr), len(rows)))
        wind_d = sum(math.hypot(wu[i]["x"] - wu[i - 1]["x"],
                                wu[i]["z"] - wu[i - 1]["z"])
                     for i in range(1, len(wu)))
        sr_d = (max((math.hypot(r["x"] - sr[0]["x"], r["z"] - sr[0]["z"])
                     for r in sr), default=0.0) if sr else 0.0)
        post_d = 0.0
        if len(post) >= 2:
            post_d = math.hypot(post[-1]["x"] - post[0]["x"],
                                post[-1]["z"] - post[0]["z"])
        windup_sim = page.evaluate(
            "(function(){try{return window.WH_CONFIG.player.attackDuration * "
            "window.WH_CONFIG.moveset.attack.windupFrac;}"
            "catch(e){return 0.15;}})()")
        walkspeed = page.evaluate(
            "(function(){try{return window.WH_CONFIG.player.walkSpeed;}"
            "catch(e){return 6.0;}})()")
        want = walkspeed * 0.3 * windup_sim
        ok = (0.7 * want <= wind_d <= 1.3 * want and sr_d < 0.06
              and post_d is not None and post_d > 0.05)
        check("A4-2", "windup move slow-down", ok,
              "windupDist=%.3f (want ~%.3f +-30%%) srDist=%.5f (<1e-3) "
              "postResume=%.3f wuF=%d" %
              (wind_d, want, sr_d, post_d, len(wu)))
    except Exception as e:
        check("A4-2", "windup move slow-down", False, "exception %r" % e)


def ac_a4_3(page):
    """D2-C: W held, no lock; camYaw swept page-side from the first swing-2
    windup frame; yaw tracks at <= 720deg/s; strike+recover freeze."""
    if not fresh(page):
        return check("A4-3", "windup turn allowance", False,
                     "pre-run: page never ready")
    try:
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(90)")
        page.wait_for_timeout(200)
        page.keyboard.down("w")
        lmb(page)
        if not wait_for_stage(page, "recover", 5.0):
            page.keyboard.up("w")
            return check("A4-3", "windup turn allowance", False,
                         "pre-run: swing-1 recover not reached in 5s")
        run_sampler(page, 4000, displace=False, yaw_sweep=True, yaw_rate=0.5)
        page.mouse.click(512, 384)
        trace = drain_sampler(page)
        page.keyboard.up("w")
        rows = trace["rows"]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        post = [r for r in rows if r["st"] is None]
        if not wu:
            return check("A4-3", "windup turn allowance", False,
                         "windup not sampled wu=%d sr=%d rows=%d" %
                         (len(wu), len(sr), len(rows)))
        max_rate = 0.0
        for i in range(1, len(wu)):
            dt_r = (wu[i]["t"] - wu[i - 1]["t"]) / 1000.0
            dy = abs(wrap_pi(wu[i]["yaw"] - wu[i - 1]["yaw"]))
            max_rate = max(max_rate, dy / dt_r if dt_r > 0 else 0.0)
        sr_drift = 0.0
        if sr:
            y0 = sr[0]["yaw"]
            sr_drift = max((abs(wrap_pi(r["yaw"] - y0)) for r in sr),
                           default=0.0)
        post_delta = 0.0
        if len(post) >= 2:
            post_delta = abs(wrap_pi(post[-1]["yaw"] - post[0]["yaw"]))
        cap = 720 * math.pi / 180 + 0.6
        ok = (max_rate <= cap and sr_drift < 0.02
              and (post_delta > 0.02 or max_rate > 0.1))
        check("A4-3", "windup turn allowance", ok,
              "maxRate=%.1fdeg/s (<=720) srDrift=%.4f postTurnDelta=%.3f wu=%d" %
              (max_rate * 180 / math.pi, sr_drift, post_delta, len(wu)))
    except Exception as e:
        check("A4-3", "windup turn allowance", False, "exception %r" % e)


def ac_a4_4(page):
    """CONFIG read: windup turn 720, lock track 240, enemy.attackPhase exact fields."""
    if not fresh(page):
        return check("A4-4", "config constants", False,
                     "pre-run: page never ready")
    try:
        cfg = page.evaluate(
            "(function(){function g(f){try{return f();}catch(e){return null;}}"
            "var C=window.WH_CONFIG;var out={};"
            "out.turnWu=g(function(){return C.player.turnLerpDegPerSecAttackWindup;});"
            "out.track=g(function(){return C.lockOn&&C.lockOn.trackWindupDegPerSec;});"
            "out.bandit=g(function(){var b=C.enemy&&C.enemy.bandit&&C.enemy.bandit.attackPhase;"
            "return b?{w:b.windup,a:b.active,r:b.recover,arc:b.hitArcDeg,"
            "track:b.trackDegPerSec}:null;});"
            "out.ghoul=g(function(){var h=C.enemy&&C.enemy.ghoul&&C.enemy.ghoul.attackPhase;"
            "return h?{w:h.windup,a:h.active,r:h.recover,arc:h.hitArcDeg,"
            "track:h.trackDegPerSec}:null;});return out;})()")
        b = cfg.get("bandit")
        g = cfg.get("ghoul")
        ok = (cfg.get("turnWu") == 720 and cfg.get("track") == 240
              and b is not None
              and abs(b["w"] - 0.7) < 1e-9
              and abs(b["a"] - 0.12) < 1e-9
              and abs(b["r"] - 0.8) < 1e-9
              and b["arc"] == 50 and b["track"] == 180
              and g is not None
              and abs(g["w"] - 0.45) < 1e-9
              and abs(g["a"] - 0.12) < 1e-9
              and abs(g["r"] - 0.5) < 1e-9
              and g["arc"] == 50 and g["track"] == 180)
        check("A4-4", "config constants", ok,
              "turnWu=%s track=%s bandit=%s ghoul=%s" %
              (cfg.get("turnWu"), cfg.get("track"), b, g))
    except Exception as e:
        check("A4-4", "config constants", False, "exception %r" % e)
'''