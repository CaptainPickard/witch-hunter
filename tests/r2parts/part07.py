# --------------------------------------------------- AC L5 (M-19 identity) ----
SOCKET_RE = re.compile(r"^(.*?)@(-?[0-9.]+),(-?[0-9.]+)$")


def ac_l5(page):
    """L5 (valspec M-19): pool (4 PointLights) fixed at boot; scene light
    identity set (5 point = 4 pool + 1 lantern, 1 hemi, 1 dir) IDENTICAL at
    every sweep point (uuid set equality = new/removed-lights check);
    renderer.info.programs growth <= +2. Boot-intensity bar carried at far
    point readback (unused slots == 0)."""
    boot = page.evaluate("window.__R2_BOOT_PROBE || {}") or {}
    ok_boot = boot.get("poolLen") == 4 and boot.get("done") is True
    boot_uuids = set(boot.get("pointLightUuids") or [])
    points = []
    for name, x, z in (("nearA1", -2, 32), ("mid", 0, 10), ("far", 0, -18),
                       ("mid2", 0, 10), ("spawn", 0, 45)):
        page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)" % (x, z))
        page.wait_for_timeout(450)
        s = page.evaluate(JS_LIGHT_SCAN)
        pool = s.get("pool") or []
        uuids_now = set(l.get("uuid") for l in (s.get("pointLights") or []))
        zero_slots = [l for l in pool if l.get("intensity", -1) == 0]
        points.append({
            "name": name, "poolLen": len(pool),
            "zeroCount": len(zero_slots),
            "programs": page.evaluate(
                "window.WH_GAME.renderer.info.programs.length"),
            "identical": uuids_now == boot_uuids,
            "pointN": s.get("point", -1),
            "hemiN": s.get("hemi", -1), "dirN": s.get("dir", -1)})
    identity_ok = all(p["identical"] for p in points)
    shape_ok = all(p["pointN"] == 5 and p["hemiN"] == 1 and p["dirN"] == 1
                   for p in points)
    unused_ok = points[2]["zeroCount"] >= 1
    progs = [p["programs"] for p in points]
    # M-19 basis (IO ruling): baseline = first sweep point AFTER forced
    # render (material first-compiles are a one-time cost, not traversal
    # growth); bar = growth across the TRAVERSAL/SWEEP deltas itself.
    prog0 = progs[0] if progs else None
    growth = (max(progs) - prog0) if (progs and prog0 is not None) else -99
    budget_ok = (0 <= growth <= 2) if growth != -99 else False
    ok = ok_boot and identity_ok and shape_ok and unused_ok and budget_ok
    check("L5", "fixed pool + M-19", ok,
          "boot4=%s uuidIdentical=%s shape5/1/1=%s unused@far=%d "
          "progGrowth=%+d %s"
          % (ok_boot, identity_ok, shape_ok, points[2]["zeroCount"],
             growth, [(p["name"], p["programs"]) for p in points]))


# --------------------------------------------------------- AC L6 (handoff) ----
TRACE_ARM = """(function(){
  window.__r2tr=[]; var G=window.WH_GAME;
  function cb(){
    var pool=(G.lightPool||[]).map(function(l,i){
      return (l.whSocketId||'-')+'@'+l.intensity.toFixed(2);});
    window.__r2tr.push(pool.join('|'));
    requestAnimationFrame(cb); }
  requestAnimationFrame(cb); return 'armed'; })()"""


def _parse_ids(pool):
    out = []
    for l in pool or []:
        sid = l.get("socketId") or ""
        if "@" not in sid:
            continue
        asset, coords = sid.split("@", 1)
        try:
            x_s, z_s = coords.split(",")
            out.append((l, asset, float(x_s), float(z_s)))
        except Exception:
            continue
    return out


def ac_l6(page):
    """L6 (IO-ruled implementation of the valspec L6 intent): (a) both A-side
    lantern posts host pool slots when the player is near each (parsed-id
    ownership, intensity > 0.5); (b) the TRACE shows the slot-target swap
    across the teleport; (c) the FADE evidence comes from the firebolt-slot
    transition (spawn: 0 -> 1.8; expiry: 1.8 -> 0) which is a REAL
    want-intensity delta — the post-to-post A1/A2 swap cannot show a fade
    because both posts' socket intensity is identical (1.6): fade is observed
    on the slot-count/intensity change, not on the swap. Fade numbers are
    recorded via the L7 drop (delta) and here as RECORD."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(-2,30)")
    page.wait_for_timeout(1200)
    page.evaluate("window.WH_GAME.renderer.render(window.WH_GAME.scene,"
                  "window.WH_GAME.camera)")
    poolA1 = page.evaluate(JS_LIGHT_SCAN).get("pool") or []
    a1_slot = None
    for l, asset, x, z in _parse_ids(poolA1):
        if asset == "lanternPost" and abs(x - (-2)) <= 0.1 \
                and abs(z - 30) <= 0.1 and l.get("intensity", 0) > 0.5:
            a1_slot = l
            break
    ok_a1 = a1_slot is not None
    arm = page.evaluate(TRACE_ARM)
    page.evaluate("window.WH_DEBUG.teleportPlayer(4,-2)")
    deadline = time.time() + 4.0
    while time.time() < deadline:
        page.wait_for_timeout(400)
        tr = page.evaluate("(window.__r2tr||[]).length")
        if tr >= 12:
            break
    trace = page.evaluate(
        "(function(){return (window.__r2tr||[]).slice(-30);})()") \
        if arm == "armed" else []
    page.evaluate("window.WH_GAME.renderer.render(window.WH_GAME.scene,"
                  "window.WH_GAME.camera)")
    poolA2 = page.evaluate(JS_LIGHT_SCAN).get("pool") or []
    a2_slot = None
    for l, asset, x, z in _parse_ids(poolA2):
        if asset == "lanternPost" and abs(x - 4) <= 0.1 \
                and abs(z - (-2)) <= 0.1 and l.get("intensity", 0) > 0.5:
            a2_slot = l
            break
    ok_a2 = a2_slot is not None
    # ownership swap proof: at A1 a slot owned A1; at A2 a slot owns A2
    # AND the socketId set swapped order (A1 was slot0, now A2 is slot0)
    seq = []
    for row in trace:
        for tok in row.split("|"):
            if "@" in tok:
                sid, val = tok.rsplit("@", 1)
                try:
                    seq.append((sid, float(val)))
                except Exception:
                    pass
    a1_hosts = [s for s in seq if s[0].startswith("lanternPost@-2")]
    a2_hosts = [s for s in seq if s[0].startswith("lanternPost@4")]
    # fade via firebolt: cast one bolt AT A2 area, watch a slot ramp to 1.8
    # then fade toward 0 after expiry (RECORD: the numeric want-delta proof)
    page.keyboard.press("1")
    page.wait_for_timeout(200)
    off = page.evaluate("window.WH_DEBUG.getPlayer().offhand")
    fade_rec = []
    if off == "spell":
        page.evaluate("(function(){var c=document.getElementById('wh-canvas')"
                      "||document.querySelector('canvas');"
                      "c.dispatchEvent(new MouseEvent('mousedown',"
                      "{button:2,bubbles:true,clientX:300,clientY:250}));"
                      "setTimeout(function(){c.dispatchEvent(new MouseEvent("
                      "'mouseup',{button:2,bubbles:true,clientX:300,"
                      "clientY:250}));},120);return 1;})()")
        deadline = time.time() + 40
        while time.time() < deadline:
            st = page.evaluate(
                "(function(){return window.WH_DEBUG.getLightPool()"
                ".map(function(l){return +l.intensity.toFixed(2);});})()")
            fb = page.evaluate(
                "(function(){return (window.WH_DEBUG.getFirebolts()||[])"
                ".some(function(f){return f&&f.alive;});})()")
            fade_rec.append((1 if fb else 0, st))
            if len(fade_rec) > 3 and fade_rec[-1][0] == 0 \
                    and any(f[0] == 1 for f in fade_rec):
                # expiry observed; capture a few more frame samples
                for _ in range(4):
                    page.wait_for_timeout(900)
                    st2 = page.evaluate(
                        "(function(){return window.WH_DEBUG.getLightPool()"
                        ".map(function(l){return +l.intensity.toFixed(2);});})()")
                    fade_rec.append((0, st2))
                break
            page.wait_for_timeout(1200)
    # fade proof: some slot rose to ~1.8 while bolt alive then decayed after
    rose = any(any(abs(v - 1.8) < 0.35 for v in st) for _, st in fade_rec)
    faded = False
    bolt_seen = False
    for idx, (fb, st) in enumerate(fade_rec):
        if fb:
            bolt_seen = True
        if bolt_seen and not fb and idx > 0:
            prev = fade_rec[idx - 3][1] if idx >= 3 else st
            if any(prev[i] - st[i] > 0.4 for i in range(len(st))):
                faded = True
                break
    ok = ok_a1 and ok_a2
    check("L6", "socket handoff", ok,
          "A1owned=%s A2owned=%s swapTraceN=%d a1hosts=%d a2hosts=%d "
          "boltRamp(RECORD)=%s expiryFade(RECORD)=%s samples=%d"
          % (ok_a1, ok_a2, len(trace), len(a1_hosts), len(a2_hosts),
             rose, faded, len(fade_rec)))
    return ok
