"""PART3c: ac_a1_4 (orig lines 496..566) for the harness rebuild."""

A1C_PART = r'''def ac_a1_4(page):
    """Facing integrity: setCameraYaw 0/90/180/270 swings; sword/body offset agree."""
    if not fresh(page):
        return check("A1-4", "facing integrity", False,
                     "pre-run: page never ready")
    try:
        facings = [0, 90, 180, 270]
        yaw_ok = True
        parent_ok = True
        offsets = []
        for deg in facings:
            page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
            page.evaluate("window.WH_DEBUG.setCameraYaw(%d)" % deg)
            page.wait_for_timeout(200)
            lmb(page)
            t0 = time.time()
            seen_windup = False
            offs = None
            while time.time() - t0 < 2.5:
                st = stage(page)
                s = player_state(page)
                if st == "windup":
                    seen_windup = True
                    if s["bodyParentIsYawFrame"] is False:
                        parent_ok = False
                    if s["yawFrameYaw"] is not None and s["yaw"] is not None:
                        if abs(wrap_pi(s["yawFrameYaw"] - s["yaw"])) > 0.001:
                            yaw_ok = False
                if st == "strike" and offs is None:
                    offs = page.evaluate(
                        "(function(){function g(f){try{return f();}"
                        "catch(e){return null;}}var p=window.WH_DEBUG.getPlayer();"
                        "if(!p.root||!p.weaponPivot||!p.body)return null;"
                        "p.root.updateMatrixWorld(true);"
                        "var w=p.weaponPivot.getWorldPosition(new THREE.Vector3());"
                        "var b=p.body.getWorldPosition(new THREE.Vector3());"
                        "var yaw=(p.yawFrame?p.yawFrame.rotation.y:p.yaw)||0;"
                        "var dx=w.x-b.x,dy=w.y-b.y,dz=w.z-b.z;"
                        "var c=Math.cos(-yaw),sn=Math.sin(-yaw);"
                        "var rx=dx*c-dz*sn,rz=dx*sn+dz*c;"
                        "return [rx,dy,rz,yaw];})()")
                    if offs is not None:
                        break
                page.wait_for_timeout(3)
            if offs is None:
                offsets.append(None)
            else:
                offsets.append(offs)
        agree = True
        pair_ok = True
        have = [o for o in offsets if o is not None]
        if len(have) < 2:
            pair_ok = False
            worst = None
        else:
            worst = 0.0
            for i in range(len(have)):
                for j in range(i + 1, len(have)):
                    d = max(abs(have[i][0] - have[j][0]),
                            abs(have[i][1] - have[j][1]),
                            abs(have[i][2] - have[j][2]))
                    worst = max(worst, d)
            pair_ok = worst <= 0.9
        ok = yaw_ok and parent_ok and pair_ok
        check("A1-4", "facing integrity", ok,
              "yawAgree=%s parentOk=%s offsets=%s/4 worstPair=%.4f (<=0.90 D2)" %
              (yaw_ok, parent_ok, len(have),
               worst if worst is not None else -1))
    except Exception as e:
        check("A1-4", "facing integrity", False, "exception %r" % e)
'''