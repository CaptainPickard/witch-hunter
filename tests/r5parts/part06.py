

# ------------------------------------------------------------ AC-R5-4 ------
def isolated(c, reg_table, r_play):
    for o in reg_table["circles"]:
        if o is c:
            continue
        if math.hypot(c["x"] - o["x"], c["z"] - o["z"]) < c["R"] + o["R"] + 1.4:
            return False
    if abs(c["z"] - (-25)) < c["R"] + PLAYER_R:
        return False
    if math.hypot(c["x"], c["z"]) + c["R"] + PLAYER_R > r_play:
        return False
    return True


def ensure_alive(page, key):
    """Enemy aggro can kill the player mid-sweep; a dead player is not
    clamped. Fresh reload (+ B re-entry) restores a live probe body."""
    if st(page)["state"] == "alive":
        return 0
    page.reload(wait_until="load")
    if not load_index(page):
        raise InfraError("reload never ready")
    if key == "B" and not enter_b(page)[0]:
        raise InfraError("B re-entry failed")
    return 1


def a1_walk(page, table):
    c = [x for x in table["A"]["circles"] if x["name"] == "lanternPost"
         and abs(x["x"] + 2) < 1e-6 and abs(x["z"] - 30) < 1e-6]
    if not c:
        return {"error": "lanternPost A1 (-2,30) not in collider set"}
    c = c[0]
    R = c["R"]
    teleport(page, -2 + R + PLAYER_R + 4, 30)
    poll(page)
    samples = hold_w(page, 90, 120.0, stationary_xy)
    ds = [math.hypot(s["x"] - c["x"], s["z"] - c["z"]) for s in samples]
    xs = [s["x"] for s in samples]
    fin = ds[-1] if ds else None
    return {"R": R, "min_d": round(min(ds), 4) if ds else None,
            "final_d": round(fin, 4) if fin is not None else None,
            "min_x": round(min(xs), 4) if xs else None, "n": len(samples),
            "ok": bool(ds) and min(ds) >= R + PLAYER_R - 0.02
            and min(xs) >= -2 and fin <= R + PLAYER_R + 0.30}


def inside_pushout(page, key, table, r_play, limit):
    rows, reloads = [], 0
    reg = table[key]
    allp = sorted(reg["circles"] + reg["exempt"], key=lambda c: c["i"])
    for c in allp[:limit]:
        reloads += ensure_alive(page, key)
        teleport(page, c["x"] + 0.1, c["z"])
        s = [poll(page), poll(page)][-1]
        d = math.hypot(s["x"] - c["x"], s["z"] - c["z"])
        ex = c in reg["exempt"]
        iso = (not ex) and isolated(c, reg, r_play)
        row = {"region": key, "i": c["i"], "name": c["name"], "R": c["R"],
               "d": round(d, 4), "nan": nan(s["x"], s["z"]),
               "class": "exempt" if ex else ("isolated" if iso else
                                             "clustered/edge(RECORD)")}
        row["ok"] = (not row["nan"]) and (not iso or d >= c["R"] + PLAYER_R
                                          - 0.02)
        rows.append(row)
    return rows, reloads


def collider_run(browser, table, r_play):
    limit = 10 if SMOKE else 10 ** 6
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-4)")
        a1 = a1_walk(page, table)
        rows_a, ra = inside_pushout(page, "A", table, r_play, limit)
        ok, tr = enter_b(page)
        if not ok:
            raise InfraError("B entry failed %s" % tr)
        rows_b, rb = inside_pushout(page, "B", table, r_play, limit)
        return {"a1": a1, "rows": rows_a + rows_b, "reloads": ra + rb}
    finally:
        ctx.close()


def ac_r5_4(browser, table, corridor):
    r_play = EXTRA.get("r_play")
    if r_play is None:
        check("R5-4", "prop colliders", False, "no r_play (R5-1 (a) failed)")
        return
    res = None
    for attempt in range(3):
        try:
            res = collider_run(browser, table, r_play)
            break
        except InfraError as e:
            if attempt == 2:
                check("R5-4", "prop colliders", False, repr(e))
                return
            FLAKES.append("R5-4#%d %r" % (attempt, e))
    radii = [{"region": c["region"], "i": c["i"], "name": c["name"],
              "x": c["x"], "z": c["z"], "R": c["R"]}
             for k in ("A", "B") for c in table[k]["circles"] + table[k]["exempt"]]
    exempt = [{"region": c["region"], "i": c["i"], "name": c["name"],
               "R": c["R"]} for k in ("A", "B") for c in table[k]["exempt"]]
    EXTRA["colliders"] = {"radii": sorted(radii, key=lambda r: (r["region"],
                                                                 r["i"])),
                          "exempt": exempt, "a1": res["a1"],
                          "pushout": res["rows"], "reloads": res["reloads"]}
    bad = []
    if not res["a1"].get("ok"):
        bad.append("(a) A1 %s" % res["a1"])
    bad += ["(b) %s#%d %s d=%s R=%s" % (r["region"], r["i"], r["name"], r["d"],
                                        r["R"]) for r in res["rows"]
            if not r["ok"]]
    cmax = (corridor or {}).get("x_abs_max")
    if cmax is None or cmax > 0.10:
        bad.append("(c) corridor |x| max %s" % cmax)
    check("R5-4", "prop colliders", not bad,
          "bad=%s a1=%s corridor=%s exempt(RECORD,C6)=%s isolated=%d "
          "clustered=%d reloads=%d radii=%s" % (
              bad[:20], json.dumps(res["a1"]), cmax, exempt,
              sum(1 for r in res["rows"] if r["class"] == "isolated"),
              sum(1 for r in res["rows"] if r["class"].startswith("clust")),
              res["reloads"], json.dumps(EXTRA["colliders"]["radii"])))
