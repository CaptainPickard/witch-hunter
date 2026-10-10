"""PART4: A2 ACs (orig lines 568..708) for the harness rebuild."""

A2_PART = r'''def ac_a2_1(page):
    """Combo chain: LMB x3 inside recover windows => comboIndex timeline [0,1,2]."""
    if not fresh(page):
        return check("A2-1", "combo chain [0,1,2]", False,
                     "pre-run: page never ready")
    try:
        timeline = []
        presses = 1
        lmb(page)
        t0 = time.time()
        prev_stage = None
        swing_idx = -1
        false_since = None
        max_gap = 0.0
        while time.time() - t0 < 6.0 and swing_idx < 2:
            st = stage(page)
            s = player_state(page)
            if s:
                atk = s["attacking"]
                if atk is False:
                    if false_since is None:
                        false_since = time.time()
                elif atk is True:
                    if false_since is not None:
                        max_gap = max(max_gap, time.time() - false_since)
                        false_since = None
            if st == "windup" and prev_stage != "windup":
                swing_idx += 1
                timeline.append(s["comboIndex"] if s else None)
            if st == "recover" and prev_stage != "recover" and presses < 3:
                lmb(page)
                presses += 1
            prev_stage = st
            page.wait_for_timeout(3)
        ok = timeline == [0, 1, 2] and max_gap <= 0.05
        check("A2-1", "combo chain [0,1,2]", ok,
              "timeline=%s presses=%d maxAttackingGap=%.0fms (<=50)" %
              (timeline, presses, max_gap * 1000))
    except Exception as e:
        check("A2-1", "combo chain [0,1,2]", False, "exception %r" % e)


def ac_a2_2(page):
    """4th LMB during m3 recover => fresh swing comboIndex 0; 5th press not queued."""
    if not fresh(page):
        return check("A2-2", "combo cap + no requeue", False,
                     "pre-run: page never ready")
    try:
        timeline = []
        lmb(page)
        presses = 1
        t0 = time.time()
        prev_stage = None
        swing_idx = -1
        queued_during_windup = False
        combo_after_5th = []
        queued_watch_until = None
        while time.time() - t0 < 10.0:
            st = stage(page)
            s = player_state(page)
            if st == "windup" and prev_stage != "windup":
                swing_idx += 1
                timeline.append(s["comboIndex"] if s else None)
                if swing_idx == 3:
                    queued_watch_until = time.time() + 1.2
            if st == "recover" and prev_stage != "recover" and presses < 4:
                lmb(page)
                presses += 1
            if s and swing_idx >= 3 and time.time() < queued_watch_until:
                if s["comboQueued"]:
                    queued_during_windup = True
            prev_stage = st
            if swing_idx >= 3 and (st is None
                                   or (st == "strike" and swing_idx == 3)) \
                    and st is None and time.time() > queued_watch_until:
                break
            page.wait_for_timeout(3)
        ok = timeline[:4] == [0, 1, 2, 0] and not queued_during_windup
        check("A2-2", "combo cap + no requeue", ok,
              "timeline=%s presses=%d queuedDuringRestartWindup=%s" %
              (timeline, presses, queued_during_windup))
    except Exception as e:
        check("A2-2", "combo cap + no requeue", False, "exception %r" % e)


def ac_a2_3(page):
    """Fresh page, single LMB: comboIndex 0 through the whole first swing."""
    if not fresh(page):
        return check("A2-3", "first swing combo 0", False,
                     "pre-run: page never ready")
    try:
        lmb(page)
        t0 = time.time()
        max_ci = -1
        bad = None
        while time.time() - t0 < 3.0:
            st = stage(page)
            s = player_state(page)
            if s and st is not None:
                if s["comboIndex"] != 0:
                    bad = s["comboIndex"]
                    break
                max_ci = 0
            if st is None and max_ci == 0:
                break
            page.wait_for_timeout(3)
        ok = bad is None and max_ci == 0
        check("A2-3", "first swing combo 0", ok,
              "comboIndex stayed 0 through swing=%s saw=%s" % (ok, bad))
    except Exception as e:
        check("A2-3", "first swing combo 0", False, "exception %r" % e)


def ac_a2_4(page):
    """Full swing completes (stage null), then LMB => next swing ci 0, ONE swing."""
    if not fresh(page):
        return check("A2-4", "post-idle restart ci 0", False,
                     "pre-run: page never ready")
    try:
        lmb(page)
        t0 = time.time()
        while time.time() - t0 < 3.0:
            if stage(page) is None:
                break
            page.wait_for_timeout(3)
        idle = stage(page) is None
        ci_second = None
        swings_second = 0
        prev_stage = None
        lmb(page)
        t1 = time.time()
        while time.time() - t1 < 3.0:
            st = stage(page)
            if st == "windup" and prev_stage != "windup":
                swings_second += 1
                ci_second = player_state(page)["comboIndex"]
            if st is None and swings_second >= 1:
                break
            prev_stage = st
            page.wait_for_timeout(3)
        ok = idle and swings_second == 1 and ci_second == 0
        check("A2-4", "post-idle restart ci 0", ok,
              "idleBefore=%s secondSwings=%d ciSecond=%s" %
              (idle, swings_second, ci_second))
    except Exception as e:
        check("A2-4", "post-idle restart ci 0", False, "exception %r" % e)
'''