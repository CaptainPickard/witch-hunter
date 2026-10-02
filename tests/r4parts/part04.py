

# ------------------------------------------- pre-Devbot baseline capture ----
def tmp_tree(src_prototype=None, archive_rev=None):
    """Temp repo-shaped root: prototype/ (copy of worktree or git archive
    of archive_rev) + tools/build_v7.py; every other top-level entry is
    symlinked (assets are served from the repo root)."""
    root = tempfile.mkdtemp(prefix="whr4_")
    if archive_rev:
        arc = subprocess.run(["git", "archive", archive_rev, "prototype"],
                             cwd=REPO_ROOT, capture_output=True, timeout=120)
        subprocess.run(["tar", "-x", "-C", root], input=arc.stdout,
                       capture_output=True, timeout=120)
    else:
        shutil.copytree(src_prototype, os.path.join(root, "prototype"),
                        ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(root, "tools"))
    shutil.copy(os.path.join(REPO_ROOT, "tools", "build_v7.py"),
                os.path.join(root, "tools", "build_v7.py"))
    for ent in os.listdir(REPO_ROOT):
        if ent in ("prototype", "tools", ".git"):
            continue
        os.symlink(os.path.join(REPO_ROOT, ent), os.path.join(root, ent))
    return root


OFF_KEYS = ["w", "h", "ctor", "mag", "min", "flipY", "colorSpace", "wrapS",
            "wrapT"]


def off_rows(tex):
    return {r["name"]: {k: r.get(k) for k in OFF_KEYS} for r in tex["rows"]}


def archive_baseline(browser):
    """Fallback pre-capture: the pre-Devbot tree (PNG_COMMIT) served from a
    git-archive copy; same TEX_JS + A2 probe at the same pose."""
    root = tmp_tree(archive_rev=PNG_COMMIT)
    proc = None
    try:
        proc, base = spawn_server(root)
        if not base:
            return None
        errs = new_errs()
        ctx, pg = new_page(browser, errs)
        try:
            if not load_index(pg, base):
                return None
            wait_loaded(pg)
            return {"off": off_rows(pg.evaluate(TEX_JS)), "a2": a2_probe(pg),
                    "src": "archive %s" % PNG_COMMIT}
        finally:
            ctx.close()
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def baseline(browser, on):
    """Pre-Devbot capture. On the pre-Devbot tree (key absent) THIS run's
    ON context IS the baseline -> written to tests/artifacts/r4-pre-*.json.
    Else: WH_W4_PRE_A2 / artifact files, else the archive fallback."""
    if on.get("tex", {}).get("key") == "__absent__":
        pre = {"off": off_rows(on["tex"]), "a2": on["a2"],
               "src": "this-run (pre-Devbot tree)"}
        save_json(PRE_OFF_FILE, pre["off"])
        save_json(PRE_A2_FILE, pre["a2"])
        return pre
    off = load_json(PRE_OFF_FILE)
    a2 = json.loads(PRE_A2_ENV) if PRE_A2_ENV else load_json(PRE_A2_FILE)
    if off and a2:
        return {"off": off, "a2": a2,
                "src": "env" if PRE_A2_ENV else "artifact files"}
    arc = archive_baseline(browser)
    if arc:
        return {"off": off or arc["off"], "a2": a2 or arc["a2"],
                "src": arc["src"]}
    return {"off": off, "a2": a2, "src": "MISSING"}


# ------------------------------------------------------------ AC-R4-1 ------
def _row(c, name):
    for r in (c.get("tex") or {}).get("rows", []):
        if r["name"] == name:
            return r
    return {}


def _live_shared(c, name):
    r = _row(c, name)
    live = (c.get("tex") or {}).get("live", {}).get(name, [])
    return bool(live) and all(u == r.get("uuid") for u in live), len(live)


def ac_r4_1(on, off, pre):
    K = on["tex"]["consts"]
    bad = []
    if on["tex"]["key"] is not True:
        bad.append("ON key=%s" % on["tex"]["key"])
    if not on["served_eq_worktree"] or on["route_served"]:
        bad.append("ON served!=worktree or route active")
    ok_png = [p for p in on["png_log"] if p["s"] == 200
              and p["url"].startswith(BASE_ROOT)]
    if len(on["png_log"]) != 3 or len(ok_png) != 3:
        bad.append("ON png requests=%d ok=%d" % (len(on["png_log"]),
                                                 len(ok_png)))
    ON_ROWS, OFF_ROWS = [], []
    for b in BODIES:
        r, o = _row(on, b), _row(off, b)
        sh, nl = _live_shared(on, b)
        ON_ROWS.append(dict(r, live_shared=sh, live_n=nl))
        if not (r.get("w") == r.get("h") == ATLAS):
            bad.append("%s ON dims %sx%s" % (b, r.get("w"), r.get("h")))
        if not str(r.get("src", "")).endswith(
                "races_regen/rigged/%s.rigged.pixelated.png" % STEMS[b]):
            bad.append("%s ON src=%s" % (b, str(r.get("src"))[-60:]))
        if r.get("mag") != K["nearest"] or r.get("min") != K["lmml"]:
            bad.append("%s ON mag/min=%s/%s" % (b, r.get("mag"), r.get("min")))
        if r.get("flipY") is not False:
            bad.append("%s ON flipY=%s" % (b, r.get("flipY")))
        for k in ("colorSpace", "wrapS", "wrapT"):
            if r.get(k) != o.get(k):
                bad.append("%s ON %s=%s OFF=%s" % (b, k, r.get(k), o.get(k)))
        if r.get("failed") or r.get("clips") != 6:
            bad.append("%s ON failed=%s clips=%s" % (b, r.get("failed"),
                                                     r.get("clips")))
        if not sh:
            bad.append("%s ON live map not shared (n=%d)" % (b, nl))
    # OFF state
    if off.get("rewrite_count") != 1:
        bad.append("OFF rewrite_count=%s" % off.get("rewrite_count"))
    if off.get("png_log"):
        bad.append("OFF png requests=%d" % len(off["png_log"]))
    if (off.get("tex") or {}).get("key") is not False:
        bad.append("OFF key=%s" % (off.get("tex") or {}).get("key"))
    pre_off = (pre or {}).get("off") or {}
    for b in BODIES:
        o = _row(off, b)
        sh, nl = _live_shared(off, b)
        OFF_ROWS.append(dict(o, live_shared=sh, live_n=nl))
        if not (o.get("w") == o.get("h") == 2048):
            bad.append("%s OFF dims %sx%s" % (b, o.get("w"), o.get("h")))
        if "pixelated" in str(o.get("src", "")):
            bad.append("%s OFF src pixelated" % b)
        pb = pre_off.get(b)
        if not pb:
            bad.append("%s OFF no pre capture" % b)
        else:
            for k in ("mag", "min", "flipY", "colorSpace"):
                if o.get(k) != pb.get(k):
                    bad.append("%s OFF %s=%s pre=%s" % (b, k, o.get(k),
                                                        pb.get(k)))
        if o.get("failed") or o.get("clips") != 6:
            bad.append("%s OFF failed=%s clips=%s" % (b, o.get("failed"),
                                                      o.get("clips")))
        if not sh:
            bad.append("%s OFF live map not shared (n=%d)" % (b, nl))
    EXTRA["kill_switch"] = {"on": ON_ROWS, "off": OFF_ROWS,
                            "rewrite_count": off.get("rewrite_count"),
                            "on_png_log": on["png_log"],
                            "pre_src": (pre or {}).get("src")}
    slim = lambda rows: [{k: r.get(k) for k in ("name", "w", "h", "mag", "min",
                                                "flipY", "colorSpace", "wrapS",
                                                "wrapT", "ctor", "clips",
                                                "live_shared")} for r in rows]
    check("R4-1", "texture source+filters", not bad,
          "bad=%s on=%s off=%s rewrite=%s pngReq=%s pre=%s" % (
              bad[:12], json.dumps(slim(ON_ROWS)), json.dumps(slim(OFF_ROWS)),
              off.get("rewrite_count"), [(p["url"][-40:], p["s"], p["ct"])
                                         for p in on["png_log"]],
              (pre or {}).get("src")))


# ------------------------------------------------------------ AC-R4-2 ------
def ac_r4_2(on, off):
    mo, mf = on["mem"], off["mem"]
    rows, bad, tot_on, tot_off = [], [], 0, 0
    for b in BODIES:
        r, o = _row(on, b), _row(off, b)
        won, wof = (r.get("w") or 0) * (r.get("h") or 0), \
            (o.get("w") or 0) * (o.get("h") or 0)
        bon, bof = int(won * 4 * 4 / 3), int(wof * 4 * 4 / 3)
        ratio = (wof / float(won)) if won else None
        tot_on += bon
        tot_off += bof
        if ratio != 16.0:
            bad.append("%s ratio=%s" % (b, ratio))
        rows.append({"body": b, "dims_on": "%sx%s" % (r.get("w"), r.get("h")),
                     "dims_off": "%sx%s" % (o.get("w"), o.get("h")),
                     "bytes_on": bon, "bytes_off": bof, "ratio": ratio})
    if mo["textures"] != mf["textures"]:
        bad.append("textures ON=%s OFF=%s" % (mo["textures"], mf["textures"]))
    if mo["geometries"] != mf["geometries"]:
        bad.append("geometries ON=%s OFF=%s" % (mo["geometries"],
                                                mf["geometries"]))
    if mo["uploaded"] != 3 or mf["uploaded"] != 3:
        bad.append("uploaded ON=%s OFF=%s" % (mo["uploaded"], mf["uploaded"]))
    EXTRA["mem_table"] = rows + [{"counts_on": mo, "counts_off": mf,
                                  "total_on": tot_on, "total_off": tot_off,
                                  "total_drop": tot_off - tot_on}]
    check("R4-2", "GPU memory swap", not bad,
          "bad=%s table=%s" % (bad, json.dumps(EXTRA["mem_table"])))


# ------------------------------------------------------------ AC-R4-3 ------
def ac_r4_3(on, off):
    a_bad = []
    a_rec = {"on": on["texspace"], "off_levels": [
        {"name": r.get("name"), "levels": r.get("levels")}
        for r in off["texspace"]]}
    for r in on["texspace"]:
        if r.get("err") or any(n > 32 for n in r["levels"]):
            a_bad.append("%s levels=%s" % (r["name"], r.get("levels")))
    off_disc = all(any(n > 32 for n in r.get("levels", [0]))
                   for r in off["texspace"])
    so, sf = on["screen"], off["screen"]
    b_ok = (so["D"] <= 0.60 * sf["D"] and so["E"] - sf["E"] >= 0.10)
    ev = ("a=%s bad=%s offDiscriminates=%s on=%s off=%s | b=%s D_on=%d "
          "D_off=%d (bar<=%.1f) E_on=%.4f E_off=%.4f (dE=%.4f bar>=0.10) "
          "mask_on=%d mask_off=%d artifacts=tests/artifacts/r4-screen-*.png"
          % (not a_bad, a_bad, off_disc,
             json.dumps([{"name": r["name"], "levels": r.get("levels"),
                          "mod8": r.get("mod8"),
                          "top8": r.get("top8")} for r in on["texspace"]]),
             json.dumps(a_rec["off_levels"]), b_ok, so["D"], sf["D"],
             0.60 * sf["D"], so["E"], sf["E"], so["E"] - sf["E"],
             so["mask_px"], sf["mask_px"]))
    # B6-IO ruling (2026-10-02): texture-space (a) is the PRIMARY gate;
    # the spawn-pose screen bars are unmeasurable on a near-black
    # silhouette (smoke: D 475v467, dE 0.0008). (b) becomes a RECORD
    # scaled re-measure; a lit-pose re-measure rides the full run.
    if not a_bad:
        check("R4-3", "visual posterization", True,
              ev + " | b(RECORD per B6-IO)=%s" % ("met" if b_ok else "dark-pose-unmeasurable"))
    elif off_disc:
        check("R4-3", "visual posterization", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("R4-3", "visual posterization", False, ev)
