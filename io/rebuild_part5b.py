"""PART5b: ac_a3_3 (orig lines 805..845) for the harness rebuild."""

A3B_PART = r'''def ac_a3_3(page):
    """D2 page-clock: 2 full bandit cycles vs stationary player => exactly
    2 hp drops (page-side watcher, 8 page-s window)."""
    if not fresh(page):
        return check("A3-3", "two clean hits", False, "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-3", "two clean hits", False, "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-3", "two clean hits", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        watcher = page.evaluate_handle("""(function(e){return new Promise(function(resolve){
          var hp0 = window.WH_DEBUG.getPlayer().hp;
          var drops = [];
          var frames = 0;
          var lastHp = hp0;
          function tick(){
            frames++;
            var p = window.WH_DEBUG.getPlayer();
            if (p && p.hp < lastHp) { drops.push({f: frames, hp: p.hp});
              lastHp = p.hp;
              if (drops.length >= 2) { resolve({drops: drops}); return; } }
            if (frames > 200) { resolve({drops: drops}); return; }  // 200 frames = 10 sim-s
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          setTimeout(function(){ resolve({drops: drops}); }, 40000);
        })})""", handle)
        res = (watcher.json_value() if hasattr(watcher, "json_value")
               else watcher)
        drops = list(res.get("drops"))
        gap = (drops[1]["f"] - drops[0]["f"]) if len(drops) == 2 else None
        ok = (len(drops) == 2 and gap is not None and 30 <= gap <= 45)
        check("A3-3", "two clean hits", ok,
              "hpDrops=%d want=2 frameGap=%s (want ~33)" %
              (len(drops), gap))
    except Exception as e:
        check("A3-3", "two clean hits", False, "exception %r" % e)
'''