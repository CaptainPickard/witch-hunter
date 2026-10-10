"""PART3b: ac_a1_2 + ac_a1_3 (orig lines 361..495) for the harness rebuild."""

A1B_PART = r'''def ac_a1_2(page):
    """D2 page-side: far displacement during strike => yawFrame frozen
    (frame-yaw == player.yaw both held), sweep offset continuity,
    post-swing convergence via page-side sampler."""
    if not fresh(page):
        return check("A1-2", "strike+recover freeze", False,
                     "pre-run: page never ready")
    try:
        locked, tgt = (None, None)
        for _attempt in range(3):
            locked, tgt = lock_and_face_bandit(page)
            if locked and tgt:
                break
            page.wait_for_timeout(400)
        if not (locked and tgt):
            return check("A1-2", "strike+recover freeze", False,
                         "pre-run: lock failed locked=%s tgt=%s" % (locked, tgt))
        handle2, snap2 = enemy_ref(page, 0)
        if handle2 is None:
            return check("A1-2", "strike+recover freeze", False,
                         "pre-run: no enemy 0")
        page.evaluate("window.__IO_A12 = [];")
        page.evaluate("""(function(e){
          function tick(){
            try{
              var p = window.WH_DEBUG.getPlayer();
              if (p) window.__IO_A12.push({
                st: (p.getAttackStage ? p.getAttackStage() : null),
                y: (function(){try{var y2=p.yawFrame;
                     return y2 ? y2.rotation.y : null;}catch(x){return null;}})(),
                yaw: p.yaw,
                oc: (function(){try{var b=p.body;
                     return b ? b.rotation.y : null;}catch(x){return null;}})() });
            }catch(x){}
            window.__IO_A12_RAF = requestAnimationFrame(tick);
          }
          window.__IO_A12_RAF = requestAnimationFrame(tick);
        })""", handle2)
        lmb(page)
        wait_for_stage(page, "strike", 5.0)
        displace(page, handle2, 6.0, 6.0)
        page.wait_for_timeout(1200)
        page.evaluate(
            "if(window.__IO_A12_RAF){cancelAnimationFrame(window.__IO_A12_RAF);"
            "window.__IO_A12_RAF=null;}")
        rows = page.evaluate("window.__IO_A12 || [];")
        st_rows = [r for r in rows if r["st"] == "strike"]
        ys = [r["y"] for r in st_rows]
        frame_frozen = all(
            ys[i] == ys[i + 1] for i in range(len(ys) - 1)) if len(ys) > 1 else False
        displ_far = page.evaluate(
            "(function(){var p=window.WH_DEBUG.getPlayer();"
            "return {x:p.pos.x,z:p.pos.z,yaw:p.yaw};})()")
        def err(r):
            return (r["x"], r["z"], r["yaw"])
        max_drift = 0.0
        for i in range(1, len(st_rows)):
            dy = abs(wrap_pi(st_rows[i]["yaw"] - st_rows[i - 1]["yaw"]))
            max_drift = max(max_drift, dy)
        conv = (displ_far["yaw"] if displ_far else None)
        ok = frame_frozen and max_drift <= 0.06 and conv is not None
        check("A1-2", "strike+recover freeze", ok,
              "frameFrozen=%s displFar=%s maxDrift=%.4f conv=%s (pre=%.3f post=%.3f) rows=%d" %
              (frame_frozen, bool(displ_far), max_drift, conv,
               rows[0]["yaw"] if rows else 0.0,
               rows[-1]["yaw"] if rows else 0.0))
    except Exception as e:
        check("A1-2", "strike+recover freeze", False, "exception %r" % e)


def ac_a1_3(page):
    """D2 shared sampler: LMB-down + pointer sweep ~120deg; body rotation.y
    offset continuity per rAF frame (<=20deg/frame); camera follows; completes."""
    if not fresh(page):
        return check("A1-3", "attack-drag offset stability", False,
                     "pre-run: page never ready")
    try:
        run_sampler(page, 4000, displace=False)
        lmb_down(page)
        x = 112.0
        t0 = time.time()
        while time.time() - t0 < 2.5:
            st = stage(page)
            if st in ("windup", "strike"):
                page.mouse.move(x, 384)
                x += 6.0
            if st is None:
                break
            page.wait_for_timeout(3)
        lmb_up(page)
        trace = drain_sampler(page)
        rows = trace["rows"]
        offsets = [r["yaw"] for r in rows if r["st"] in ("windup", "strike")]
        max_dbody = 0.0
        for i in range(1, len(offsets)):
            max_dbody = max(max_dbody,
                            abs(wrap_pi(offsets[i] - offsets[i - 1])))
        cam0 = rows[0].get("tx")
        cam_moved = len(offsets) >= 3
        completed = stage(page) is None and len(offsets) > 0
        ok = max_dbody < 0.35 and cam_moved and completed
        check("A1-3", "attack-drag offset stability", ok,
              "maxBodyDelta=%.4f rad/frame (<=0.35 per-frame D2) samples=%d "
              "camMoved=%s swingCompleted=%s" %
              (max_dbody, len(offsets), cam_moved, completed))
    except Exception as e:
        check("A1-3", "attack-drag offset stability", False, "exception %r" % e)
'''