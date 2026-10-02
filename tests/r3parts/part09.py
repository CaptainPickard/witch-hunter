

# ------------------------------------------------------------ AC-P3 --------
def r2_a3_subprobe():
    """A3 settle subprobe source, read verbatim from the R2 harness at run
    time (READ-only; one source of truth for the inherited waiver class)."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"A3_SUBPROBE = r'''(.*?)'''", src, re.S)
    return m.group(1) if m else None


def ac_p3(r2rec):
    """R1 floor re-proof: tests/wh_world_r1_validation.py UNCHANGED as a
    subprocess on the shared server. Inherited waiver classes re-verified
    in-run as R2 part10 ac_floor; A4 amendment (style.css FREEZE waiver)."""
    j, by, fails = run_floor_harness("tests/wh_world_r1_validation.py",
                                     {"WH_R1_PORT": str(PORT)}, 1800)
    rec = {"verdict": j and j.get("verdict"), "fails": fails, "waivers": [],
           "per_ac": ["%s:%s" % (k, v.get("verdict")) for k, v in by.items()]}
    EXTRA["floor"]["r1"] = rec
    if j is None:
        check("P3", "R1 floor", False, "no parseable R1 verdict")
        return
    if j.get("verdict") == "PASS":
        check("P3", "R1 floor", True, "r1=PASS %s" % rec["per_ac"])
        return
    ev = {k: (v.get("evidence") or "") for k, v in by.items()}
    p5_ok = any(r["id"] == "P5" and r["verdict"] == "PASS" for r in RESULTS)
    idx_ok = (sha256_file(os.path.join(REPO_ROOT, "prototype/index.html"))
              == INDEX_FREEZE_SHA256)
    w = rec["waivers"]

    def a2():
        e = ev.get("A2", "")
        if "idleBad" in e and "minY=-0" in e.replace(" ", ""):
            w.append("A2-dev-baseline")
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
        # night-rig chain re-verified from THIS run's R2 floor: L4 PASS and
        # L10 PASS or L10 waived with scaled c10 >= 0.25 (R3 deviation:
        # L4/L10 are not in-suite in R3; they ride the P4 subprocess)
        pa = dict(x.split(":", 1) for x in r2rec.get("per_ac", []))
        sc = (r2rec.get("l10_scaled") or {}).get("c")
        l10 = pa.get("L10") == "PASS" or (isinstance(sc, float) and sc >= 0.25)
        if pa.get("L4") == "PASS" and l10:
            w.append("A4-nightrig (r2 L4 PASS, L10 %s)" % pa.get("L10"))
            return True
        return False

    def a6():
        if "DRIFT" in ev.get("A6", ""):
            w.append("A6-hash-drift")
            return True
        return False

    def a7():
        s_ok, _ = style_hunk_exact()
        if idx_ok and s_ok:
            w.append("A7-R3-style.css-freeze (A4 amendment: index freeze-ok, "
                     "exact P5 hunk)")
            return True
        return False

    def a8():
        paths = re.findall(r"'([^']+)'", ev.get("A8", ""))
        inherit = ("io/specs/", "io/reports/", "tests/wh_world_r2_validation",
                   "tests/r2parts")
        if p5_ok and paths and all(in_surface(p) or any(
                p.startswith(x) for x in inherit) for p in paths):
            w.append("A8-surface (residual in P5/R2 surfaces, secrets "
                     "re-verified by P5)")
            return True
        return False

    covered = {"A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "A8": a8}
    unexplained = [f for f in fails if f not in covered]
    if not unexplained and all(covered[f]() for f in fails):
        check("P3", "R1 floor", True,
              "FLOOR-WAIVER r1=%s fails=%s classes=%s (carrier-req: "
              "Testerbot revalidates harness on lane recovery)"
              % (j.get("verdict"), fails, " | ".join(w)), verdict="WAIVED")
    else:
        check("P3", "R1 floor", False,
              "r1=%s fails=%s unexplained=%s waived=%s (non-artifact -> STOP;"
              " manual adjudication per spec :77)"
              % (j.get("verdict"), fails, unexplained, " | ".join(w)),
              verdict="BLOCK")
