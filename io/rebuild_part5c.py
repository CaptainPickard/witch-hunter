"""PART5c: ac_a3_4 (orig lines 847..923, the D2 window-buffer sampler) rebuild."""

A3C_PART = r'''def ac_a3_4(page):
    """Weapon animation phases: windup raise monotonic, active sweep, recover ease."""
    if not fresh(page):
        return check("A3-4", "phase animation profile", False,
                     "pre-run: page never ready")
    try:
        handle, snap = enemy_ref(page, 0)   # D2: baseline read BEFORE luring
        idle_early = page.evaluate(
            "(function(e){try{return e.weaponPivot?e.weaponPivot.rotation.y:null;}"
            "catch(x){return null;}})", handle)
        if idle_early is None:
            return check("A3-4", "phase animation profile", False,
                         "pre-run: weaponPivot missing")
        handle2, snap2 = lure_bandit(page, lock=False)
        if handle2 is None:
            return check("A3-4", "phase animation profile", False,
                         "pre-run: no enemy 0")
        page.evaluate("window.__IO_IDLE = %r" % (idle_early,))
        t_entry, _ = await_fsm(page, handle2, "attack", 12.0)
        if t_entry is None:
            return check("A3-4", "phase animation profile", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        # D2-C window-buffer sampler (no pending promise): append rows into
        # window.__IO_A34, drain at the end via evaluate.
        page.evaluate("window.__IO_A34 = []; window.__IO_A34_STATE=null;")
        page.evaluate("""(function(e){
          function tick(){
            try{
              var r = e.weaponPivot && e.weaponPivot.rotation;
              if(r){
                var y = r.y;
                var ph = e.attackPhase || null;
                window.__IO_A34.push({ph: ph, y: y});
              }
            }catch(x){}
            window.__IO_A34_RAF = requestAnimationFrame(tick);
          }
          window.__IO_A34_RAF = requestAnimationFrame(tick);
        })""", handle2)
        page.wait_for_timeout(6000)   # wall window; sim advances 1-2 cycles
        page.evaluate(
            "if(window.__IO_A34_RAF){cancelAnimationFrame(window.__IO_A34_RAF);"
            " window.__IO_A34_RAF=null;}")
        prof = page.evaluate(
            """(function(){try{return (function(rows){var idleSeed=window.__IO_IDLE||null;"""
            """var idleY=idleSeed,wind=[],act=[],rec=[],last=null,done=false;"""
            """for(var i=0;i<rows.length;i++){var r=rows[i];var ph=r.ph,y=r.y;"""
            """if(idleY===null&&ph===null)idleY=y;"""
            """if(ph==='windup')wind.push(y);else if(ph==='active')act.push(y);"""
            """else if(ph==='recover')rec.push(y);}})(window.__IO_A34||[]);"""
            """return {idleY:idleY,wind:wind,act:act,rec:rec};}"""
            """catch(x){return {idleY:null,wind:[],act:[],rec:[]};}})()""")
        if not isinstance(prof, dict):
            return check("A3-4", "phase animation profile", False,
                         "pre-run: sampler returned %r" % (prof,))
        wind = list(prof.get("wind") or [])
        act = list(prof.get("act") or [])
        rec = list(prof.get("rec") or [])
        idleY = prof.get("idleY")
        if not (wind and act and rec and idleY is not None):
            return check("A3-4", "phase animation profile", False,
                         "pre-run: attackPhase/weaponPivot missing "
                         "(wind=%d act=%d rec=%d idle=%s)" %
                         (len(wind), len(act), len(rec), idleY))
        arc = max(abs(y - idleY) for y in wind + act + rec) or 1e-6
        # windup raise-back: |y-idle| monotonic non-decreasing (small jitter tol)
        mono = all(wind[i + 1] - wind[i] >= -0.02
                   for i in range(len(wind) - 1))
        # end-of-windup must reach >= 25% of arc
        wind_end_frac = abs(wind[-1] - idleY) / arc
        if act:
            act_frac = (max(abs(y - idleY) for y in act)
                        - abs(act[0] - idleY)) / arc
        else:
            act_frac = 0.0
        rec_ok = (not rec) or abs(rec[-1] - idleY) < 0.15 * arc + 0.02
        ok = mono and wind_end_frac >= 0.25 and act_frac >= 0.4 and rec_ok
        check("A3-4", "phase animation profile", ok,
              "mono=%s windEndFrac=%.2f(>=0.25) actFrac=%.2f(>=0.40) recoverOk=%s "
              "arc=%.3f" % (mono, wind_end_frac, act_frac, rec_ok, arc))
    except Exception as e:
        check("A3-4", "phase animation profile", False, "exception %r" % e)
'''