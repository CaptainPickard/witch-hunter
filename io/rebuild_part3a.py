"""PART3: A1 ACs (orig lines 314..566) for the harness rebuild."""

A1_PART = r'''def ac_a1_1(page):
    """D2-C sampler: swing-1; sampler during recover; chain-press; displacement
    on swing-2's first windup frame; rate-capped chase assertion."""
    if not fresh(page):
        return check("A1-1", "windup yaw chase", False, "pre-run: page never ready")
    try:
        locked, tgt = (None, None)
        for _attempt in range(3):
            locked, tgt = lock_and_face_bandit(page)
            if locked and tgt:
                break
            page.wait_for_timeout(400)
        if not (locked and tgt):
            return check("A1-1", "windup yaw chase", False,
                         "pre-run: lock failed locked=%s tgt=%s" % (locked, tgt))
        lmb(page)
        wait_for_stage(page, "recover", 5.0)
        handle, cfg = run_sampler(page, 4500, True, 4.0, 0.0)
        lmb(page)   # chain-press during recover window
        trace = drain_sampler(page, lambda s: s.get("displaced"), 3.0)
        rows = trace["rows"]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        if not wu or not trace["displaced"]:
            return check("A1-1", "windup yaw chase", False,
                         "windup not sampled displaced=%s wu=%d rows=%d" %
                         (trace["displaced"], len(wu), len(rows)))
        max_dyaw = 0.0
        displaced_seen = False
        for i in range(1, len(wu)):
            dt_r = (wu[i]["t"] - wu[i - 1]["t"]) / 1000.0
            dy = abs(wrap_pi(wu[i]["yaw"] - wu[i - 1]["yaw"]))
            max_dyaw = max(max_dyaw, dy)
            if wu[i]["x"] != wu[i - 1]["x"]:
                displaced_seen = True
        def err(r):
            return (r["x"], r["z"], r["yaw"])
        jump = displaced_seen and max_dyaw > 0.5
        ok = (not displaced_seen) and max_dyaw <= 240 * math.pi / 180.0
        check("A1-1", "windup yaw chase", ok,
              "dispInWindup=%s wuFrames=%d maxDyaw=%.4f jump=%s e %.3f->%.3f" %
              (displaced_seen, len(wu), max_dyaw, jump,
               wu[0]["yaw"] if wu else 0.0, wu[-1]["yaw"] if wu else 0.0))
    except Exception as e:
        check("A1-1", "windup yaw chase", False, "exception %r" % e)
'''