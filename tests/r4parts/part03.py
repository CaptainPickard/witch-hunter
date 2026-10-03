

# ------------------------------------------- screen-space body metrics -----
def body_metrics(shown, hidden):
    """B6: mask = pixels whose max channel |shown-hidden| > 8. D = distinct
    RGB over mask (shown); E = share of 4-neighbour in-mask pairs whose max
    channel diff <= 2."""
    w, h = shown.size
    a = list(shown.getdata())
    b = list(hidden.getdata())
    mask = [max(abs(p[0] - q[0]), abs(p[1] - q[1]), abs(p[2] - q[2])) > 8
            for p, q in zip(a, b)]
    colors = set()
    eq = pairs = 0
    for i, m in enumerate(mask):
        if not m:
            continue
        p = a[i]
        colors.add(p)
        x = i % w
        for j in ((i + 1) if x + 1 < w else -1, (i + w) if i + w < w * h
                  else -1):
            if j >= 0 and mask[j]:
                q = a[j]
                pairs += 1
                eq += (abs(p[0] - q[0]) <= 2 and abs(p[1] - q[1]) <= 2
                       and abs(p[2] - q[2]) <= 2)
    return {"mask_px": sum(mask), "D": len(colors),
            "E": round(eq / max(1, pairs), 4), "pairs": pairs,
            "size": "%dx%d" % (w, h)}


def screen_probe(page, tag):
    """Camera-settled (vz<1) one-evaluate shown/hidden readback; mask >= 400
    px at 960x540 else settle-retry (infra)."""
    last = None
    for _ in range(1 if SMOKE else 3):
        for _k in range(4):
            wait_frames(page, 3)
            s = page.evaluate(SCREEN_JS)
            if s and s["vz"] < 1:
                break
        if not s or s["vz"] >= 1:
            last = "camera never settled vz=%s" % (s and s["vz"])
            continue
        shown, hidden = decode_image(s["shown"]), decode_image(s["hidden"])
        if is_degenerate(shown) or is_degenerate(hidden):
            last = "degenerate frame"
            continue
        m = body_metrics(shown, hidden)
        if m["mask_px"] < 400:
            last = "mask %d px < 400" % m["mask_px"]
            page.wait_for_timeout(1500)
            continue
        try:
            os.makedirs(ART_DIR, exist_ok=True)
            shown.save(os.path.join(ART_DIR, "r4-screen-%s-shown.png" % tag))
            hidden.save(os.path.join(ART_DIR, "r4-screen-%s-hidden.png" % tag))
        except Exception:
            pass
        m["buf"] = "%dx%d" % (s["cw"], s["ch"])
        return m
    raise InfraError("screen probe (%s): %s" % (tag, last))


# ------------------------------------------------- A2 in-harness probe -----
def r1_js(name):
    """R1 actor-minY JS read verbatim from the UNCHANGED R1 harness at run
    time (one source of truth for the A2 numbers)."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r1_validation.py")
               ).read()
    m = re.search(r'%s = """(.*?)"""' % name, src, re.S)
    return m.group(1) if m else None


def a2_probe(page):
    """R1 A2 protocol in-harness: idle |minY| per actor (player + first
    bandit + first ghoul of the active region) and sprint-walk max |minY|
    (13 x 160ms, ShiftLeft+w). Moves the player: run LAST on a page."""
    pj, ej = r1_js("JS_PLAYER_BODY_MINY"), r1_js("ENEMY_MINY_JS")
    page.wait_for_timeout(1000)
    out = {"player": None, "bandit": None, "ghoul": None, "walk": None}
    idle = page.evaluate(pj)
    if idle and idle["minY"] == idle["minY"]:
        out["player"] = round(abs(idle["minY"]), 4)
    for i in range(6):
        e = page.evaluate(ej % i)
        if (e and e["fsm"] != "dead" and e["type"] in out
                and out[e["type"]] is None and e["minY"] == e["minY"]):
            out[e["type"]] = round(abs(e["minY"]), 4)
    try:
        page.keyboard.down("ShiftLeft")
        page.keyboard.down("w")
        dev = 0.0
        for _ in range(13):
            page.wait_for_timeout(160)
            s = page.evaluate(pj)
            if s and s["minY"] == s["minY"]:
                dev = max(dev, abs(s["minY"]))
        out["walk"] = round(dev, 4)
    finally:
        try:
            page.keyboard.up("w")
            page.keyboard.up("ShiftLeft")
        except Exception:
            pass
    return out


# ------------------------------------------------ per-context collection ----
def collect(browser, off):
    """One fresh context = one full probe set (OFF = route rewrite active).
    Infra failures raise InfraError (flake rule retries the context)."""
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    counter = {"n": None}
    try:
        if off:
            config_rewrite_route(ctx, counter)
        if not load_index(page):
            raise InfraError("page never ready (%s)" % ("OFF" if off else "ON"))
        loaded = wait_loaded(page)
        tex = page.evaluate(TEX_JS)
        mem = page.evaluate(MEM_JS)
        txs = page.evaluate(TEXSPACE_JS)
        scr = screen_probe(page, "off" if off else "on")
        # ON context asserts no route: served CONFIG text == worktree
        served = page.evaluate("fetch('js/CONFIG.js',{cache:'no-store'})"
                               ".then(function(r){return r.text();})")
        with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")) as f:
            wt = f.read()
        a2 = None if off else a2_probe(page)
        return {"off": off, "loaded": loaded, "tex": tex, "mem": mem,
                "texspace": txs, "screen": scr, "a2": a2,
                "rewrite_count": counter["n"],
                "route_served": counter.get("served", 0),
                "served_eq_worktree": served == wt,
                "png_log": list(errs["png"]),
                "req_count": len(errs["req"]),
                "console_errors": errs["console"][:5],
                "page_errors": errs["page"][:5]}
    finally:
        ctx.close()


def collect_retry(browser, off):
    """Flake rule wrapper for one context (infra-shaped only, max 2)."""
    tag = "OFF" if off else "ON"
    for attempt in range(3):
        try:
            return collect(browser, off)
        except Exception as e:
            if attempt == 2:
                print("[diag] collect %s failed after retries: %r" % (tag, e))
                return {"error": repr(e)[:300]}
            FLAKES.append("collect-%s#%d %r" % (tag, attempt, e)[:200])
            print("[flake] collect %s attempt %d: %r" % (tag, attempt, e))
