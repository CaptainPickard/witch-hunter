

# ------------------------------------------------------------ AC-R5-2 ------
REPORT_JS = """(function(){var rm=window.WH_DEBUG.getRegionManager();
  return rm ? (rm.spawnReport || null) : null;})()"""

NEG_REWRITES = [
    ("{ asset: 'gravestoneObelisk', x: -10, z: 20,",
     "{ asset: 'gravestoneObelisk', x: -10, z: -40,"),
    ("{ type: 'bandit', x: 0, z: -60 }", "{ type: 'bandit', x: 0, z: -95 }"),
]


def props_block(src, region_key):
    """Text of CONFIG.<region_key>.props: [ ... ] (byte-identity law)."""
    i = src.find("%s: {" % region_key)
    if i < 0:
        return None
    j = src.find("props: [", i)
    k = src.find("\n    ]", j)
    return src[j:k] if j >= 0 and k >= 0 else None


def wait_report(page, wall=30.0):
    deadline = time.time() + wall
    while time.time() < deadline:
        r = page.evaluate(REPORT_JS)
        if r is not None:
            return r
        wait_frames(page, 2)
    return None


def neg_control(browser):
    """Separate context: served CONFIG.js rewritten (sanctioned route, each
    rewrite exactly once). Worktree file never modified."""
    src = _worktree_config().decode()
    counts = [src.count(a) for a, _b in NEG_REWRITES]
    body = src
    for a, b in NEG_REWRITES:
        body = body.replace(a, b)
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    served = {"n": 0}

    def handler(route):
        served["n"] += 1
        route.fulfill(status=200, body=body,
                      headers={"Content-Type": "application/javascript"})
    try:
        ctx.route("**/js/CONFIG.js", handler)
        ready = load_index(page)
        rep = wait_report(page) if ready else None
        return {"counts": counts, "ready": ready, "served": served["n"],
                "report": rep, "page_errors": errs["page"][:3],
                "log": errs["log"][:2]}
    finally:
        ctx.close()


def ac_r5_2(browser, cfg, table):
    r_play = EXTRA.get("r_play") or (90 - (cfg["world"].get("playerMargin")
                                           or 0))
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-2)")
        rep = wait_report(page)
        page.wait_for_timeout(5000)                 # A ghoul runtime z (5 s)
        ghoul = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies("
                              "window.WH_CONFIG.regionA.id);for(var i=0;i<"
                              "l.length;i++){if(l[i].type==='ghoul')return "
                              "{x:l[i].x,z:l[i].z};}return null;})()")
        logs = list(errs["log"])
    finally:
        ctx.close()
    recompute = recompute_validator(cfg, table, r_play)
    n_props = sum(len(cfg["props"][cfg[k]]) for k in ("A", "B"))
    n_en = len(cfg["enemies"]["A"]) + len(cfg["enemies"]["B"])
    bad, spawn_only = [], True
    if rep is None:
        bad.append("spawnReport absent")
        spawn_only = False
    else:
        if rep.get("props") != n_props or n_props != 106:
            bad.append("props %s (cfg %d, want 106)" % (rep.get("props"),
                                                         n_props))
            spawn_only = False
        if rep.get("enemies") != n_en or n_en != 6:
            bad.append("enemies %s (cfg %d, want 6)" % (rep.get("enemies"),
                                                         n_en))
            spawn_only = False
        if rep.get("violations"):
            bad.append("violations %d" % len(rep["violations"]))
            if any(v.get("kind") != "spawn" for v in rep["violations"]):
                spawn_only = False
        if rep.get("error"):
            bad.append("validator error %s" % rep["error"])
            spawn_only = False
    if not logs:
        bad.append("no [WH spawn-validator] console line")
        spawn_only = False
    if recompute:
        bad.append("recompute %s" % recompute)
        if any(v[0] != "spawn" for v in recompute):
            spawn_only = False
    # A ghoul: CONFIG z >= -23.5, or gate-guard flag listed in exempt[]
    g_cfg = [e for e in cfg["enemies"]["A"] if e["type"] == "ghoul"]
    g_flag = bool(g_cfg and g_cfg[0].get("gateGuard"))
    g_exempt = bool(rep and any(x.get("kind") == "enemy" and x.get("name")
                                == "ghoul" for x in rep.get("exempt", [])))
    g_ok = bool(g_cfg) and (g_cfg[0]["z"] >= -23.5 or (
        g_flag and g_exempt and ghoul and ghoul["z"] >= -23.5))
    if not g_ok:
        bad.append("A ghoul cfg=%s flag=%s exempt=%s runtime=%s" % (
            g_cfg, g_flag, g_exempt, ghoul))
        spawn_only = False
    base = (git_blob(BASE_COMMIT, "prototype/js/CONFIG.js") or b"").decode()
    cur = _worktree_config().decode()
    props_same = {k: (props_block(base, k) is not None
                      and props_block(base, k) == props_block(cur, k))
                  for k in ("regionA", "regionB")}
    if not all(props_same.values()):
        bad.append("props arrays moved %s" % props_same)
        spawn_only = False
    # negative control
    neg = neg_control(browser)
    nrep = neg.get("report") or {}
    base_keys = {(v.get("kind"), v.get("region"), v.get("index"))
                 for v in (rep or {}).get("violations", [])}
    new = [v for v in nrep.get("violations", [])
           if (v.get("kind"), v.get("region"), v.get("index")) not in base_keys]
    want = {("prop", cfg["A"], 0, "side"), ("enemy", cfg["B"], 2, "radius")}
    got = {(v.get("kind"), v.get("region"), v.get("index"), v.get("why"))
           for v in new}
    neg_ok = (neg["counts"] == [1, 1] and neg["ready"] and neg["served"] >= 1
              and not neg["page_errors"]
              and len(nrep.get("violations", [])) >= 2 and got == want)
    if not neg_ok:
        bad.append("neg counts=%s ready=%s pageErr=%s new=%s" % (
            neg["counts"], neg["ready"], neg["page_errors"], sorted(got)))
        spawn_only = False
    EXTRA["validator"] = {"report": rep, "recompute": recompute,
                          "neg": {"counts": neg["counts"], "ready":
                                  neg["ready"], "new": sorted(got),
                                  "total": len(nrep.get("violations", []))},
                          "log": logs[:1], "ghoul_runtime": ghoul}
    ev = "bad=%s report=%s recompute=%s neg=%s log=%s ghoul=%s" % (
        bad, json.dumps(rep), recompute, json.dumps(EXTRA["validator"]["neg"]),
        logs[:1], ghoul)
    if not bad:
        check("R5-2", "boot spawn validator", True, ev)
    elif spawn_only:
        # mechanics PASS; only spawn-in-collider misses = radii numeric miss
        # (C12 exactly-once retune spans collider radii)
        check("R5-2", "boot spawn validator", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("R5-2", "boot spawn validator", False, ev)
