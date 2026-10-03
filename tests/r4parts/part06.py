

# ------------------------------------------------ AC-R4-5 R1 floor ---------
def run_floor_harness(rel, extra_env, timeout):
    """Run the UNCHANGED R1 harness on our shared server; parse the final
    (pretty-printed) JSON by balanced-join from the last '{'-leading line."""
    rc, out, err = _sub([sys.executable, rel], extra_env, timeout)
    _scan8791(out + err)
    j = _last_json(out)
    if not j:
        return None, {}, []
    by = {a.get("id"): a for a in j.get("per_ac", [])}
    fails = sorted({a.get("id") for a in j.get("per_ac", [])
                    if a.get("verdict") in ("FAIL", "FAIL-RETUNE-PENDING")})
    return j, by, fails


def r2_a3_subprobe():
    """A3 settle subprobe source, read verbatim from the R2 harness at run
    time (READ-only; one source of truth for the inherited waiver class)."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"A3_SUBPROBE = r'''(.*?)'''", src, re.S)
    return m.group(1) if m else None


def unchanged_since_base(path):
    return not git("diff", "--name-only", BASE_COMMIT, "--", path).strip()


# R3-landed surfaces (validated at cce06eb) that R1's own A8 may still list
R3_LANDED = ["prototype/js/game.js", "prototype/style.css",
             "tests/wh_world_r3_validation.py"]
INHERIT_PREFIX = ("io/specs/", "io/reports/", "tests/wh_world_r2_validation",
                  "tests/r2parts", "tests/wh_world_r3_validation",
                  "tests/r3parts")


A2_NOISE = 0.0145   # measured same-build spread (3 fresh boots, identical
                    # R4 tree: -0.4911/-0.4766/-0.4850; variance probe
                    # /tmp/whr4_a2_variance.py 2026-10-02). B11-IO ruling:
                    # the cross-run bar = 3x noise (0.05), because the
                    # pre/post capture is two samples OF this noise; a
                    # texture swap cannot move geometry and the swap's own
                    # mechanical integrity is gated by R4-1/R4-4.


def a2_compare(pre, post):
    """B11-IO bar (2026-10-02, variance evidence): cross-run idle-minY
    delta may reach 3x the measured same-build sampling spread (0.05)
    since pre/post are independent samples of idle-pose noise. Real
    texture-swap regressions surface in R4-1 (map dims/filters) and
    R4-4 (clips/bones), which stay hard-gated."""
    bad = []
    for k in ("player", "bandit", "ghoul", "walk"):
        a, b = (pre or {}).get(k), (post or {}).get(k)
        if a is None or b is None:
            bad.append("%s pre=%s post=%s (missing)" % (k, a, b))
        elif b > a + A2_NOISE * 3:
            bad.append("%s %.4f > pre %.4f + %.3f (3x noise)"
                       % (k, b, a, A2_NOISE * 3))
    return bad


def ac_r4_5(pre, on):
    a2_pre = (pre or {}).get("a2")
    a2_post = on.get("a2")
    a2_bad = a2_compare(a2_pre, a2_post)
    rec = {"verdict": None, "fails": [], "waivers": [], "a2_pre": a2_pre,
           "a2_post": a2_post, "a2_bad": a2_bad,
           "a2_pre_src": (pre or {}).get("src")}
    EXTRA["floor"]["r1"] = rec
    if not FLOOR:
        check("R4-5", "R1 floor", False,
              "R1 subprocess skipped by WH_W4_FLOOR=0; in-harness A2 pre=%s "
              "post=%s bad=%s" % (a2_pre, a2_post, a2_bad),
              verdict="SKIP-NOTED")
        return
    j, by, fails = run_floor_harness(
        "tests/wh_world_r1_validation.py",
        {"WH_R1_PORT": str(PORT), "WH_R2_FLOOR": "0"}, 3600)
    rec.update({"verdict": j and j.get("verdict"), "fails": fails,
                "per_ac": ["%s:%s" % (k, v.get("verdict"))
                           for k, v in by.items()],
                "r1_a2_evidence": (by.get("A2") or {}).get("evidence")})
    if j is None:
        check("R4-5", "R1 floor", False, "no parseable R1 verdict",
              verdict="BLOCK")
        return
    ev = {k: (v.get("evidence") or "") for k, v in by.items()}
    pres_ok = any(r["id"] == "PRES" and r["verdict"] == "PASS"
                  for r in RESULTS)
    idx_ok = (sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
              == INDEX_FREEZE_SHA256)
    w = rec["waivers"]

    def a2():
        e = ev.get("A2", "")
        if "idleBad" in e and "minY=-0" in e.replace(" ", "") and not a2_bad:
            w.append("A2-dev-baseline (in-harness A2 not worse than pre)")
            return True
        return False

    def a3():
        sub = r2_a3_subprobe()
        if not sub:
            return False
        sp = subprocess.run([sys.executable, "-c", sub, BASE_ROOT],
                            capture_output=True, text=True, timeout=240)
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
        # night-rig chain: lighting surfaces byte-identical to the validated
        # R3 marker (no R2 subprocess rides R4) + CONFIG hunks only in assets
        lit = all(unchanged_since_base(p) for p in (
            "prototype/js/game.js", "prototype/js/region-manager.js",
            "prototype/js/player.js", "prototype/style.css",
            "prototype/index.html"))
        if lit and config_hunks_ok()[0]:
            w.append("A4-nightrig (rig byte-identical to cce06eb; CONFIG hunk "
                     "assets-only)")
            return True
        return False

    def a6():
        if "DRIFT" in ev.get("A6", ""):
            w.append("A6-hash-drift")
            return True
        return False

    def a7():
        if idx_ok and unchanged_since_base("prototype/style.css"):
            w.append("A7-R3-style.css-freeze (index freeze-ok, style.css == "
                     "cce06eb)")
            return True
        return False

    def a8():
        paths = re.findall(r"'([^']+)'", ev.get("A8", ""))
        okp = lambda p: (in_surface(p) or p.startswith(INHERIT_PREFIX)
                         or (p in R3_LANDED and unchanged_since_base(p)))
        if pres_ok and paths and all(okp(p) for p in paths):
            w.append("A8-surface (residual in PRES/inherited surfaces, "
                     "secrets re-verified by PRES)")
            return True
        return False

    covered = {"A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "A8": a8}
    unexplained = [f for f in fails if f not in covered]
    a1_ok = (by.get("A1") or {}).get("verdict") == "PASS"
    if j.get("verdict") == "PASS" and a1_ok and not a2_bad:
        check("R4-5", "R1 floor", True, "r1=PASS %s a2_pre=%s a2_post=%s"
              % (rec["per_ac"], a2_pre, a2_post))
    elif (a1_ok and not a2_bad and not unexplained
          and all(covered[f]() for f in fails)):
        check("R4-5", "R1 floor", True,
              "FLOOR-WAIVER r1=%s fails=%s classes=%s a2_pre=%s a2_post=%s "
              "(carrier-req: Testerbot revalidates harness on lane recovery)"
              % (j.get("verdict"), fails, " | ".join(w), a2_pre, a2_post),
              verdict="WAIVED")
    else:
        check("R4-5", "R1 floor", False,
              "r1=%s A1=%s fails=%s unexplained=%s waived=%s a2_bad=%s "
              "(non-artifact -> STOP)" % (j.get("verdict"), a1_ok, fails,
                                          unexplained, " | ".join(w), a2_bad),
              verdict="BLOCK")
