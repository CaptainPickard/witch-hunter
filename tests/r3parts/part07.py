

def ac_p5(browser):
    dirty, committed, gate_docs = changed_paths()
    resid = sorted({p for p in dirty + committed if not in_surface(p)})
    proto = sorted({p for p in dirty + committed
                    if p.startswith("prototype/")})
    fourth = [p for p in proto if p not in P5_SURFACE[:3]]
    gh = hunks("prototype/js/game.js")
    g_ok = bool(gh) and all(_within(h, GAME_WINDOWS) for h in gh)
    ch = hunks("prototype/js/CONFIG.js")
    cfg_src = open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")).read()
    removed = [r for h in ch for r in h[3]]
    c_ok = (bool(ch) and all(_within(h, [CONFIG_WINDOW]) for h in ch)
            and all(k in cfg_src for k in CONFIG_KEEP)
            and not any(k in r for r in removed for k in CONFIG_KEEP))
    s_ok, s_ev = style_hunk_exact()
    idx = sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
    i_ok = idx == INDEX_FREEZE_SHA256
    # RECORD: byte-identity vs the R3 code base (pin drift = combat/anim)
    i_base = not git("diff", "--name-only", BASE_COMMIT, "--",
                     "prototype/index.html").strip()
    v_ok, v_ev = v7_rebuild_clean(browser)
    builds_dirty = [p for p in dirty if p.startswith("prototype/builds/")]
    nsec = secrets_scan()
    added = [a for p in P5_SURFACE[:3] for h in hunks(p) for a in h[2]]
    free_hits = [a for a in added if re.search(r"\bfree\b", a, re.I)]
    untouched = [p for p in proto if re.search(
        r"region-manager\.js|player\.js|hud", p)]
    ok = (not resid and not fourth and g_ok and c_ok and s_ok and i_ok
          and v_ok and not builds_dirty and nsec == 0 and not free_hits
          and not untouched)
    ev = ("resid=%s fourthProto=%s gameHunks=%s(%s) configHunks=%s(%s) "
          "css=%s(%s) index=%s(identToBase=%s) v7=%s(%s) buildsDirty=%s "
          "secretsHits=%d "
          "freeHits=%d untouchedViol=%s gateDocsSinceBase=%d(RECORD: IO "
          "gate-doc commits, outside prototype/tests)"
          % (resid, fourth, g_ok, [(h[0], h[1]) for h in gh], c_ok,
             [(h[0], h[1]) for h in ch], s_ok, s_ev,
             "freeze-ok" if i_ok else "DRIFT:" + idx[:12], i_base, v_ok, v_ev,
             builds_dirty, nsec, len(free_hits), untouched, len(gate_docs)))
    blockish = fourth or not i_ok or nsec
    check("P5", "preservation surface", ok, ev,
          verdict=None if ok else ("BLOCK" if blockish else "FAIL"))


# ------------------------------------------------------------ AC-P6 --------
def ac_p6(page):
    r = page.evaluate("(function(){var r=window.WH_CONFIG.renderer;"
                      "return {div:r.internalResDiv, isInt:"
                      "Number.isInteger(r.internalResDiv), "
                      "mpr:('maxPixelRatio' in r)?r.maxPixelRatio:null};})()")
    lines = open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")
                 ).read().splitlines()
    quote = None
    for i, ln in enumerate(lines):
        if "maxPixelRatio" in ln:
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(lines) and re.search(r"supersed", lines[j],
                                                       re.I):
                    quote = lines[j].strip()
            break
    ok = r["isInt"] and r["div"] == DISPATCH_DIV and r["mpr"] is not None
    check("P6", "CONFIG record", ok,
          "internalResDiv=%s int=%s maxPixelRatio=%s comment(RECORD)=%r"
          % (r["div"], r["isInt"], r["mpr"], quote))
    return r["div"]
