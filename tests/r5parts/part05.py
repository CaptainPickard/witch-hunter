

# ------------------------------------------------------------ AC-R5-3 ------
PITCHES = [-15, 0, 22, 45, 65]
CX, CY = VIEW_W // 2, VIEW_H // 2


def wheel_to(page, target, maxn=24):
    """Organic wheel: each notch = +-0.8 camDist (player.js:233-236)."""
    page.mouse.move(CX, CY)
    for _ in range(maxn):
        cur = st(page)["camDist"]
        if abs(cur - target) < 0.01:
            break
        page.mouse.wheel(0, 100 if target > cur else -100)
        wait_frames(page, 1)
    return st(page)["camDist"]


def drag_to(page, target, sens, pmin, pmax):
    """Organic LMB drag (mousedown also fires tryAttack :196, recorded).
    Clamp ends overshoot by 20 deg so the clamp itself lands the pitch."""
    cur = st(page)["pitch"]
    goal = target
    if target <= pmin:
        goal = pmin - 20
    elif target >= pmax:
        goal = pmax + 20
    dy = int(round((goal - cur) / sens))
    page.mouse.move(CX, CY)
    page.mouse.down()
    page.mouse.move(CX, CY + dy, steps=max(2, abs(dy) // 20))
    page.mouse.up()
    return st(page)["pitch"]


def cam_formula(P, dist, pitch):
    """Devbot-pinned law (report): cap = Max * (1 - k * max(0, sin p));
    eff = clamp(camDist, Min, max(Min, cap)); y floor = clearance."""
    mn, mx = P["camMinDistance"], P["camMaxDistance"]
    k = P.get("camPitchDistShrink")
    clr = P.get("camGroundClearance")
    if k is None or clr is None:
        return None
    sp = math.sin(math.radians(pitch))
    cap = max(mn, mx * (1 - k * max(0.0, sp)))
    eff = max(mn, min(cap, dist))
    vy = max(P["camHeight"] + eff * sp, clr) - P["camHeight"]
    return round(math.hypot(eff * math.cos(math.radians(pitch)), vy), 4)


def cam_cell(page, P, dist_req, pitch_req):
    pitch = drag_to(page, pitch_req, P["mouseSensDegPerPx"],
                    P["camPitchMinDeg"], P["camPitchMaxDeg"])
    s, settled, miny = settle_cam(page)
    s = st(page)
    d = math.sqrt((s["cx"] - s["x"]) ** 2 + (s["cy"] - (s["y"] + P["camHeight"]))
                  ** 2 + (s["cz"] - s["z"]) ** 2)
    return {"dist": dist_req, "pitch_req": pitch_req,
            "pitch": round(pitch, 3), "camDist": round(s["camDist"], 4),
            "y_min": round(min(miny, s["cy"]), 4), "y": round(s["cy"], 4),
            "d": round(d, 4), "d_formula": cam_formula(P, s["camDist"], pitch),
            "settled": settled}


def lock_probe(page, P):
    """C8: lock-on branch builds its own want; clamp must cover it."""
    e = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies(window."
                      "WH_CONFIG.regionA.id);for(var i=0;i<l.length;i++){if("
                      "l[i].type==='bandit'&&l[i].x===l[i].x)return {x:l[i].x,"
                      "z:l[i].z};}return null;})()")
    if not e:
        raise InfraError("no live A bandit for lock probe")
    teleport(page, e["x"], e["z"] + 6)
    poll(page)
    set_yaw(page, 0)
    drag_to(page, -15, P["mouseSensDegPerPx"], P["camPitchMinDeg"],
            P["camPitchMaxDeg"])
    wheel_to(page, 14)
    set_yaw(page, 0)
    page.evaluate("window.WH_DEBUG.engageLockOn()")
    locked = page.evaluate("window.WH_DEBUG.isLocked()")
    miny, ys = 1e9, []
    deadline = time.time() + 10.0
    while time.time() < deadline:
        s = poll(page)
        miny = min(miny, s["cy"])
        ys.append(round(s["cy"], 3))
    s2, settled, m2 = settle_cam(page, wall=20.0)
    still = page.evaluate("window.WH_DEBUG.isLocked()")
    page.evaluate("window.WH_DEBUG.breakLockOn()")
    return {"locked": locked, "still_locked": still, "y_min":
            round(min(miny, m2), 4), "y_settled": round(s2["cy"], 4),
            "settled": settled, "n": len(ys)}


def camera_run(browser, cfg):
    P = cfg["player"]
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-3)")
        cells = []
        for dist in (7, 14, 3):
            got = wheel_to(page, dist)
            for p in PITCHES:
                c = cam_cell(page, P, dist, p)
                c["wheel_readback"] = round(got, 4)
                cells.append(c)
        # by-pitch law re-read at camDist 14 in ascending order 0,22,45,65
        wheel_to(page, 14)
        law = [cam_cell(page, P, 14, p) for p in (0, 22, 45, 65)]
        cam_dist_after = st(page)["camDist"]
        lock = lock_probe(page, P)
        return {"cells": cells, "law": law, "camDist_after": cam_dist_after,
                "lock": lock, "page_errors": errs["page"][:3]}
    finally:
        ctx.close()


def ac_r5_3(browser, cfg):
    P = cfg["player"]
    res = None
    for attempt in range(3):
        try:
            res = camera_run(browser, cfg)
            break
        except InfraError as e:
            if attempt == 2:
                check("R5-3", "camera clamp + by-pitch", False, repr(e))
                return
            FLAKES.append("R5-3#%d %r" % (attempt, e))
    cells, law, lock = res["cells"], res["law"], res["lock"]
    EXTRA["camera"] = cells
    bad = []
    for c in cells + law:
        if c["y_min"] < 0.3:
            bad.append("(a) dist%s p%s y_min %.4f" % (c["dist"], c["pitch_req"],
                                                      c["y_min"]))
        if c["y"] < 0.395:
            bad.append("(b) dist%s p%s y %.4f" % (c["dist"], c["pitch_req"],
                                                  c["y"]))
    if not lock["locked"]:
        bad.append("(c) lock never engaged %s" % lock)
    elif lock["y_min"] < 0.3 or lock["y_settled"] < 0.395:
        bad.append("(c) lock y %s" % lock)
    ds = [c["d"] for c in law]
    for i in range(len(ds) - 1):
        if ds[i + 1] > ds[i] + 0.05:
            bad.append("law non-monotone %s" % ds)
            break
    if not (ds and ds[-1] <= 0.85 * ds[0]):
        bad.append("law d65 %s > 0.85 * d0 %s" % (ds[-1:], ds[:1]))
    if any(d < P["camMinDistance"] - 0.05 for d in ds):
        bad.append("law d < camMin %s" % ds)
    if abs(res["camDist_after"] - 14) > 1e-6:
        bad.append("camDist mutated %s" % res["camDist_after"])
    dflt = [c for c in cells if c["dist"] == 7 and c["pitch_req"] == 22]
    want_y = P["camHeight"] + 7 * math.sin(math.radians(22))
    if not dflt or abs(dflt[0]["d"] - 7) > 0.10 or abs(dflt[0]["y"] -
                                                        want_y) > 0.10:
        bad.append("default framing %s (want d 7 y %.3f)" % (dflt, want_y))
    check("R5-3", "camera clamp + by-pitch", not bad,
          "bad=%s law=%s lock=%s camDistAfter=%s cells=%s" % (
              bad, json.dumps(law), json.dumps(lock), res["camDist_after"],
              json.dumps(cells)))
