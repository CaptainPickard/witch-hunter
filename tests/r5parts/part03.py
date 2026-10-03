

# ------------------------------------------------------------ AC-R5-1 ------
def region_of(h, r_play):
    tz = r_play * math.cos(math.radians(h))
    return "A" if tz > -23 else "B"


def sweep_heading(page, h, r_play, table_reg, key, ref):
    """(b) walk-to-rim + (f) rim seam + (c) snapback for one heading."""
    row = {"h": h, "region": key, "start_shift": 0}
    hs = h
    for _ in range(72):
        sx = (r_play - 6) * math.sin(math.radians(hs))
        sz = (r_play - 6) * math.cos(math.radians(hs))
        if not inside_any(table_reg, sx, sz):
            break
        hs += 5
    row["start_shift"] = hs - h
    teleport(page, sx, sz)
    poll(page)
    samples = hold_w(page, hs + 180, 180.0, stationary_r)
    rs = [rr(s) for s in samples if not nan(s["x"], s["z"])]
    fin = samples[-1] if samples else None
    row["r_max"] = round(max(rs), 4) if rs else None
    row["r_final"] = round(rr(fin), 4) if fin else None
    row["n"] = len(samples)
    row["nan"] = any(nan(s["x"], s["z"]) for s in samples)
    row["home"] = bool(fin) and ((fin["z"] >= -25) if key == "A"
                                 else (fin["z"] <= -25))
    row["walk_ok"] = bool(rs and not row["nan"] and row["home"]
                          and row["r_max"] <= r_play + 0.02
                          and row["r_final"] >= r_play - 0.30)
    # (f) rim seam at the clamped pose (auto-follow holds yaw = outward)
    seam = render_S(page, "%s-h%03d" % (key, h))
    row["S_rim"] = seam["S"]
    row["S_ref"] = ref
    row["seam_ok"] = ref is not None and seam["S"] <= ref + 10
    # (c) snapback from r_play + 5 on the original heading
    teleport(page, (r_play + 5) * math.sin(math.radians(h)),
             (r_play + 5) * math.cos(math.radians(h)))
    snap = [poll(page), poll(page)]
    row["snap"] = round(min(rr(s) for s in snap), 4)
    row["snap_ok"] = row["snap"] <= r_play + 0.02
    return row


def corner_and_enemy(page, key, r_play, cfg):
    """(d) C5 corner trap + (e) enemy[0] radial hold on its home side."""
    out = {}
    tx, tz = (95, -30) if key == "A" else (95, -20)
    teleport(page, tx, tz)
    s = [poll(page), poll(page)][-1]
    out["corner"] = {"x": round(s["x"], 3), "z": round(s["z"], 3),
                     "r": round(rr(s), 4)}
    side_ok = s["z"] >= -25 if key == "A" else s["z"] <= -25
    out["corner_ok"] = bool(side_ok and rr(s) <= r_play + 0.02)
    # (e) enemy: live enemy[0], NaN-guarded, written radially home-side
    e = page.evaluate("(function(){var e=window.WH_DEBUG.getEnemy(0);"
                      "return e?{x:e.x,z:e.z,fsm:e.fsm}:null;})()")
    hx, hz = ((r_play + 5), 0.0) if key == "A" else (0.0, -(r_play + 5))
    if e is None or nan(e["x"], e["z"]):
        page.reload(wait_until="load")
        load_index(page)
        if key == "B":
            enter_b(page)
        e = page.evaluate("(function(){var e=window.WH_DEBUG.getEnemy(0);"
                          "return e?{x:e.x,z:e.z,fsm:e.fsm}:null;})()")
    if e is None or nan(e["x"], e["z"]):
        raise InfraError("enemy[0] NaN/absent in %s" % key)
    page.evaluate("(function(){var e=window.WH_DEBUG.getEnemy(0).ref;"
                  "e.pos.x=%f; e.pos.z=%f;})()" % (hx, hz))
    reads = []
    for _ in range(2):
        wait_frames(page, 2)
        reads.append(page.evaluate("(function(){var e=window.WH_DEBUG."
                                   "getEnemy(0);return {x:e.x,z:e.z};})()"))
    last = reads[-1]
    er = math.hypot(last["x"], last["z"])
    hold = (last["z"] >= -23.5) if key == "A" else (last["z"] <= -26.5)
    margin_key = [k for k in (cfg["world"] or {}) if "enemy" in k.lower()
                  and "margin" in k.lower()]
    out["enemy"] = {"wrote": [hx, hz], "read": last, "r": round(er, 4),
                    "r_enemy": r_play, "enemy_margin_key": margin_key or None}
    out["enemy_ok"] = (not nan(last["x"], last["z"]) and er <= r_play + 0.02
                       and hold)
    return out


def region_pass(browser, key, cfg, r_play, table):
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (%s)" % key)
        yaw0 = st(page)["yaw"]
        if key == "B":
            ok, tr = enter_b(page)
            if not ok:
                return {"error": "B entry failed %s" % tr}
            sp = cfg["spawn"]["B"]
            teleport(page, sp["x"], sp["z"])
            set_yaw(page, yaw0)
        ref = render_S(page, "%s-ref" % key)["S"]
        rows = [sweep_heading(page, h, r_play, table[key], key, ref)
                for h in HEADINGS if region_of(h, r_play) == key]
        ce = corner_and_enemy(page, key, r_play, cfg)
        ground = page.evaluate(GROUND_JS)
        return {"rows": rows, "ce": ce, "ref": ref, "ground": ground,
                "page_errors": errs["page"][:3]}
    finally:
        ctx.close()


def region_pass_retry(browser, key, cfg, r_play, table):
    for attempt in range(3):
        try:
            return region_pass(browser, key, cfg, r_play, table)
        except InfraError as e:
            if attempt == 2:
                return {"error": repr(e)[:300]}
            FLAKES.append("R5-1-%s#%d %r" % (key, attempt, e))
            print("[flake] R5-1 %s attempt %d: %r" % (key, attempt, e))


def ac_r5_1(browser, cfg, table):
    W = cfg["world"]
    m = W.get("playerMargin")
    a_ok = (isinstance(m, (int, float)) and PLAYER_R <= m <= 3.0
            and W.get("groundRadius") == 90)
    if not isinstance(m, (int, float)):
        check("R5-1", "radial clamp sweep", False,
              "(a) world.playerMargin=%r groundRadius=%r" % (
                  m, W.get("groundRadius")))
        return
    r_play = 90 - m
    EXTRA["r_play"], EXTRA["margin"] = r_play, m
    res = {k: region_pass_retry(browser, k, cfg, r_play, table)
           for k in ("A", "B")}
    bad, seam_bad = [], []
    if not a_ok:
        bad.append("(a) margin %r out of [0.7,3.0]" % m)
    for k in ("A", "B"):
        r = res[k]
        if "error" in r:
            bad.append("%s error %s" % (k, r["error"]))
            continue
        for row in r["rows"]:
            EXTRA["sweep"].append({kk: row.get(kk) for kk in (
                "h", "region", "r_max", "r_final", "snap", "S_rim", "S_ref",
                "start_shift", "n")})
            if not row["walk_ok"]:
                bad.append("h%d walk r_max=%s r_final=%s home=%s nan=%s" % (
                    row["h"], row["r_max"], row["r_final"], row["home"],
                    row["nan"]))
            if not row["snap_ok"]:
                bad.append("h%d snap %s" % (row["h"], row["snap"]))
            if not row["seam_ok"]:
                seam_bad.append("h%d S_rim %s > S_ref %s + 10" % (
                    row["h"], row["S_rim"], row["S_ref"]))
        if not r["ce"]["corner_ok"]:
            bad.append("%s corner %s" % (k, r["ce"]["corner"]))
        if not r["ce"]["enemy_ok"]:
            bad.append("%s enemy %s" % (k, r["ce"]["enemy"]))
    # (f) geometry: texel density GATE, d95 extent RECORD
    ground = {}
    for k in ("A", "B"):
        g = (res[k].get("ground") or {}).get(cfg[k]) if "error" not in res[k] \
            else None
        d95 = math.sqrt(math.log(20)) / cfg["fog"][k]
        want = r_play + 1.1 * d95
        if not g or not g.get("R") or g.get("rep") is None:
            seam_bad.append("%s ground mesh unread %s" % (k, g))
            ground[k] = {"read": g}
            continue
        dens = g["rep"] / g["R"]
        dens_ok = abs(dens / (12.0 / 90.0) - 1) <= 0.02
        ground[k] = {"R_vis": round(g["R"], 3), "repeat": round(g["rep"], 4),
                     "mist": g.get("mist"), "density": round(dens, 5),
                     "density_ok": dens_ok, "d95": round(d95, 2),
                     "want_R_vis": round(want, 2),
                     "extent_met(RECORD)": g["R"] >= want - 1e-6}
        if not dens_ok:
            seam_bad.append("%s texel density %.5f vs %.5f" % (
                k, dens, 12.0 / 90.0))
    EXTRA["ground"] = ground
    ev = ("margin=%s r_play=%s bad=%s seamBad=%s ground=%s sweep=%s ce=%s" % (
        m, r_play, bad, seam_bad, json.dumps(ground), json.dumps(
            EXTRA["sweep"]), json.dumps({k: res[k].get("ce") for k in res})))
    if not bad and not seam_bad:
        check("R5-1", "radial clamp sweep", True, ev)
    elif not bad:
        check("R5-1", "radial clamp sweep", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("R5-1", "radial clamp sweep", False, ev)
