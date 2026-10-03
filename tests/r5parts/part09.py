

# ------------------------------------------------ AC-PRES R1 floor ---------
def r1_js(name):
    """R1 actor-minY JS read verbatim from the UNCHANGED R1 harness."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r1_validation.py")
               ).read()
    m = re.search(r'%s = """(.*?)"""' % name, src, re.S)
    return m.group(1) if m else None


def a2_probe(page):
    """R1 A2 protocol in-harness (R4 part03 verbatim): idle |minY| per actor
    + sprint-walk max |minY| (13 x 160ms, ShiftLeft+w)."""
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


def a2_live(browser, base=None):
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page, base):
            return None
        return a2_probe(page)
    finally:
        ctx.close()


def a2_pre(browser):
    """pre = tests/artifacts/r5-pre-a2.json (smoke capture); absent ->
    measured live on a git-archive copy of the R5 base (818d8bc) and
    written to the artifact (same probe, same pose)."""
    pre = load_json(PRE_A2_FILE)
    if pre:
        return pre, "artifact r5-pre-a2.json"
    root = tmp_tree(archive_rev=BASE_COMMIT)
    proc = None
    try:
        proc, base = spawn_server(root)
        if not base:
            return None, "archive server failed"
        pre = a2_live(browser, base)
        if pre:
            save_json(PRE_A2_FILE, pre)
        return pre, "archive %s (written to artifact)" % BASE_COMMIT
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def r2_a3_subprobe():
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"A3_SUBPROBE = r'''(.*?)'''", src, re.S)
    return m.group(1) if m else None


A2_NOISE = 0.0145   # R4 B11 measured same-build spread; bar = 3x (0.05)
LANDED = ["prototype/js/game.js", "prototype/style.css",
          "prototype/js/assets.js", "tests/wh_world_r3_validation.py",
          "tests/wh_world_r4_validation.py"]
INHERIT_PREFIX = ("io/specs/", "io/reports/", "tests/wh_world_r2_validation",
                  "tests/r2parts", "tests/wh_world_r3_validation",
                  "tests/r3parts", "tests/wh_world_r4_validation",
                  "tests/r4parts", RIGGED_DIR)


def a2_compare(pre, post):
    bad = []
    for k in ("player", "bandit", "ghoul", "walk"):
        a, b = (pre or {}).get(k), (post or {}).get(k)
        if a is None or b is None:
            bad.append("%s pre=%s post=%s (missing)" % (k, a, b))
        elif b > a + A2_NOISE * 3:
            bad.append("%s %.4f > pre %.4f + %.3f (3x noise)"
                       % (k, b, a, A2_NOISE * 3))
    return bad


def ac_pres_r1(browser):
    pre, pre_src = a2_pre(browser)
    post = a2_live(browser)
    a2_bad = a2_compare(pre, post)
    rec = {"verdict": None, "fails": [], "waivers": [], "a2_pre": pre,
           "a2_post": post, "a2_bad": a2_bad, "a2_pre_src": pre_src}
    EXTRA["floor"]["r1"] = rec
    if not FLOOR:
        check("PRES-R1", "R1 floor", False,
              "R1 subprocess skipped by WH_W5_FLOOR=0; in-harness A2 pre=%s "
              "post=%s bad=%s" % (pre, post, a2_bad), verdict="SKIP-NOTED")
        return
    j, by, fails = run_floor_harness(
        "tests/wh_world_r1_validation.py",
        {"WH_R1_PORT": str(PORT), "WH_R2_FLOOR": "0"}, 3600)
    rec.update({"verdict": j and j.get("verdict"), "fails": fails,
                "per_ac": ["%s:%s" % (k, v.get("verdict"))
                           for k, v in by.items()]})
    if j is None:
        check("PRES-R1", "R1 floor", False, "no parseable R1 verdict",
              verdict="BLOCK")
        return
    ev = {k: (v.get("evidence") or "") for k, v in by.items()}
    pres_ok = any(r["id"] == "PRES" and r["verdict"] == "PASS"
                  for r in RESULTS)
    idx_ok = (sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
              == INDEX_FREEZE_SHA256)
    r2rec = EXTRA["floor"].get("r2") or {}
    w = rec["waivers"]

    def a2():
        e = ev.get("A2", "")
        if "idleBad" in e and "minY=-0" in e.replace(" ", "") and not a2_bad:
            w.append("A2-dev-baseline (B11: post <= pre + 0.05)")
            return True
        return False

    def a3():
        sub = r2_a3_subprobe()
        if not sub:
            return False
        sp = subprocess.run([sys.executable, "-c", sub, BASE_ROOT],
                            capture_output=True, text=True, timeout=240)
        _scan8791(sp.stdout + sp.stderr)
        for ln in reversed((sp.stdout or "").splitlines()):
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                row = json.loads(ln)
                if row.get("converged"):
                    w.append("A3-settle tail=%s" % row.get("tail"))
                    return True
                break
        return False

    def a4():
        # C3: R5 edits region-manager/game/player -> night-rig chain
        # re-verified from THIS run's R2 floor: L4 PASS + (L10 PASS or
        # scaled c10 >= 0.25)
        pa = dict(x.split(":", 1) for x in r2rec.get("per_ac", []))
        sc = (r2rec.get("l10_scaled") or {}).get("c")
        l10 = pa.get("L10") == "PASS" or (isinstance(sc, float) and sc >= 0.25)
        if pa.get("L4") == "PASS" and l10:
            w.append("A4-nightrig (C3: r2 L4 PASS, L10 %s c10=%s)"
                     % (pa.get("L10"), sc))
            return True
        return False

    def a6():
        if "DRIFT" in ev.get("A6", ""):
            w.append("A6-hash-drift")
            return True
        return False

    def a7():
        if idx_ok and unchanged_since_base("prototype/style.css"):
            w.append("A7-style.css-freeze (index freeze-ok, style.css == %s)"
                     % BASE_COMMIT)
            return True
        return False

    def a8():
        paths = re.findall(r"'([^']+)'", ev.get("A8", ""))
        okp = lambda p: (in_surface(p) or p.startswith(INHERIT_PREFIX)
                         or (p in LANDED and (unchanged_since_base(p)
                                              or in_surface(p))))
        if pres_ok and paths and all(okp(p) for p in paths):
            w.append("A8-surface (residual in PRES/inherited surfaces, "
                     "secrets re-verified by PRES)")
            return True
        return False

    covered = {"A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "A8": a8}
    unexplained = [f for f in fails if f not in covered]
    a1_ok = (by.get("A1") or {}).get("verdict") == "PASS"
    if j.get("verdict") == "PASS" and a1_ok and not a2_bad:
        check("PRES-R1", "R1 floor", True, "r1=PASS %s a2_pre=%s a2_post=%s"
              % (rec["per_ac"], pre, post))
    elif (a1_ok and not a2_bad and not unexplained
          and all(covered[f]() for f in fails)):
        check("PRES-R1", "R1 floor", True,
              "FLOOR-WAIVER r1=%s fails=%s classes=%s a2_pre=%s(%s) "
              "a2_post=%s (carrier-req: Testerbot revalidates harness on "
              "lane recovery)" % (j.get("verdict"), fails, " | ".join(w),
                                  pre, pre_src, post), verdict="WAIVED")
    else:
        check("PRES-R1", "R1 floor", False,
              "r1=%s A1=%s fails=%s unexplained=%s waived=%s a2_bad=%s "
              "(non-artifact -> STOP)" % (j.get("verdict"), a1_ok, fails,
                                          unexplained, " | ".join(w), a2_bad),
              verdict="BLOCK")
