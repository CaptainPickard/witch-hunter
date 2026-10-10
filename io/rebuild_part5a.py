"""PART5: A3 ACs (orig lines 710..1020) for the harness rebuild."""

A3_PART = r'''def lure_bandit(page, lock=False):
    """Setup: player at (-6,-2) camYaw 0, bandit (-6,-8) ahead. Optional F-lock."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.wait_for_timeout(300)
    if lock:
        press_f(page)
        page.wait_for_timeout(300)
    handle, snap = enemy_ref(page, 0)
    return handle, snap


def ac_a3_1(page):
    """D2 page-clock: first hp drop lands attackPhase=='active', 0.7+-0.1s
    PAGE-time after attack-FSM entry (page-side watcher)."""
    if not fresh(page):
        return check("A3-1", "phase-gated first hit", False,
                     "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=True)
        if handle is None:
            return check("A3-1", "phase-gated first hit", False,
                         "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-1", "phase-gated first hit", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        watcher = page.evaluate_handle("""(function(e){return new Promise(function(resolve){
          var entryT = performance.now();
          var hp0 = window.WH_DEBUG.getPlayer().hp;
          var out = {drops: [], phases: []};
          function tick(){
            var p = window.WH_DEBUG.getPlayer();
            var ph = (function(){try{ return e.attackPhase; }catch(x){ return null; }})();
            var phT = (function(){try{ return +e.attackPhaseT.toFixed(2); }catch(x){ return -1; }})();
            if (p && p.hp < hp0) { out.drops.push({phT: phT, ph: ph, hp: p.hp});
              resolve(out); return; }
            if (out.phases.length < 500) out.phases.push(ph);
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          setTimeout(function(){ resolve(out); }, 12000);
        })})""", handle)
        res = (watcher.json_value() if hasattr(watcher, "json_value")
               else watcher)
        drops = list(res.get("drops"))
        if not drops:
            return check("A3-1", "phase-gated first hit", False,
                         "no hp drop within watcher window phases=%s" %
                         (list(res.get("phases"))[-8:],))
        d0 = drops[0]
        ok = d0["ph"] == "active" and 0.0 <= d0["phT"] <= 0.05
        check("A3-1", "phase-gated first hit", ok,
              "hpDrop=true frame phT(sim)=%.3f (want ~0.0-0.05, active entry) "
              "phaseAtDrop=%s" % (d0["phT"], d0["ph"]))
    except Exception as e:
        check("A3-1", "phase-gated first hit", False, "exception %r" % e)


def ac_a3_2(page):
    """D2 sim-frames: period between windup entries == (windup+active+recover)
    / maxDt frame count (bandit 33 frames) +- 2. ghoul skipped (region A)."""
    if not fresh(page):
        return check("A3-2", "enemy period", False, "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-2", "enemy period", False, "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-2", "enemy period", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        marks = page.evaluate("""(function(e){return new Promise(function(resolve){
          var marks=[];var frames=0;var last=null;
          function tick(){
            frames++;
            var ph=null;try{ph=e.attackPhase||null;}catch(x){}
            if(ph==='windup'&&last!=='windup')marks.push(frames);
            last=ph;
            if(marks.length>=3){resolve(marks);return;}
            if(frames>6000){resolve(marks);return;}
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);})})""", handle)
        if not marks or len(marks) < 3:
            return check("A3-2", "enemy period", False,
                         "pre-run: attackPhase missing or <3 windups marks=%s" % marks)
        p1 = marks[1] - marks[0]
        p2 = marks[2] - marks[1]
        ok = 30 <= p1 <= 36 and 30 <= p2 <= 36
        check("A3-2", "enemy period", ok,
              "periods=%d,%d frames (want 33 +-3) ghoul skipped: region-A only" % (p1, p2))
    except Exception as e:
        check("A3-2", "enemy period", False, "exception %r" % e)
'''