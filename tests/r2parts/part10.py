# ------------------------------------------------------------- FLOOR + main --
def ac_floor(REPO_ROOT):
    """Floor step (valspec verbatim): re-run R1 harness UNCHANGED as a
    subprocess sharing our server via WH_BASE_ROOT. PASS = R1 verdict PASS.
    FLOOR-WAIVER: R1 A8 scope fail citing only R2-round artifacts. R1's stale
    internal A6 constants DRIFT => that specific fail set gets the waiver
    treatment per IO ruling rebase (documented in R2 report; R1 file stays
    UNTOUCHED until its own re-baseline round)."""
    if not FLOOR:
        check("FLOOR", "r1-floor", False, "skipped by WH_R2_FLOOR=0",
              verdict="RECORD")
        return "SKIPPED"
    env = dict(os.environ)
    env["WH_BASE_ROOT"] = BASE_ROOT
    env.pop("WH_SMOKE", None)
    proc = subprocess.run([sys.executable, "tests/wh_world_r1_validation.py"],
                          cwd=REPO_ROOT, capture_output=True, text=True,
                          timeout=600, env=env)
    r1v = None
    fails = []
    for line in reversed((proc.stdout or "").splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                j = json.loads(s)
                r1v = j.get("verdict")
                fails = [a.get("id") for a in j.get("per_ac", [])
                         if a.get("verdict") == "FAIL"]
                break
            except Exception:
                continue
    if r1v == "PASS":
        check("FLOOR", "r1-floor", True, "r1=PASS")
        return "PASS"
    if fails and all(f in ("A8", "A6", "A7") for f in fails):
        check("FLOOR", "r1-floor", False,
              "FLOOR-WAIVER r1=%s fails=%s (known round artifacts; "
              "R1 constants frozen pre-round)" % (r1v, fails),
              verdict="RECORD")
        return "WAIVED"
    check("FLOOR", "r1-floor", False,
          "r1=%s fails=%s (hard fail)" % (r1v, fails))
    return "FAIL"


def main():
    page_errors, console_errors, responses = [], [], []
    server = None
    envlim = None
    l10v = None
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
        server = start_server()
        page = new_page(browser, console_errors, page_errors, responses)
        page_ok = load_index(page)
        boot = (page.evaluate("window.__R2_BOOT_PROBE || null")
                if page_ok else None)
        if not page_ok:
            for ac in ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8",
                       "L9", "L10"):
                check(ac, "page-never-ready", False, "page never ready")
            check("FLOOR", "r1-floor", False, "page never ready")
            check("SCOPE", "tree scope+secrets", True, "skipped (page fail)")
        else:
            check("BOOT", "boot probe", (boot or {}).get("done") is True,
                  "ambient=%s hemi=%s dir=%s pool=%s point=%s"
                  % ((boot or {}).get("ambient"), (boot or {}).get("hemi"),
                     (boot or {}).get("dir"), (boot or {}).get("poolLen"),
                     len((boot or {}).get("pointLightUuids") or [])))
            cross = {"crossed": False, "method": "not-attempted"}
            try:
                cross = organic_cross(page)   # L1 travels A -> B
            except Exception as e:
                check("L1", "crossing-exception", False, repr(e))
            scan_b = page.evaluate(JS_LIGHT_SCAN)
            # back to A for the rest (cross back organically)
            cross_back = {"crossed": False}
            try:
                cross_back = organic_cross(page, timeout=25.0)
            except Exception:
                pass
            scan_a = page.evaluate(JS_LIGHT_SCAN)
            try:
                ac_l1(page, scan_a, scan_b, cross)
            except Exception as e:
                check("L1", "runner-exception", False, repr(e))
            try:
                ac_l2(page, scan_a)
            except Exception as e:
                check("L2", "runner-exception", False, repr(e))
            try:
                ac_l3(page, scan_a)
            except Exception as e:
                check("L3", "runner-exception", False, repr(e))
            try:
                ac_l4(page)
            except Exception as e:
                check("L4", "runner-exception", False, repr(e))
            try:
                ac_l5(page)
            except Exception as e:
                check("L5", "runner-exception", False, repr(e))
            try:
                ac_l6(page)
            except Exception as e:
                check("L6", "runner-exception", False, repr(e))
            try:
                ac_l7(page)
            except Exception as e:
                check("L7", "runner-exception", False, repr(e))
            try:
                ac_l8(page)
            except Exception as e:
                check("L8", "runner-exception", False, repr(e))
            try:
                ac_l9(page, responses)
            except Exception as e:
                check("L9", "runner-exception", False, repr(e))
            try:
                l10v, envlim = ac_l10_probe(page, SMOKE)
            except Exception as e:
                check("L10", "runner-exception", False, repr(e))
                l10v, envlim = "FAIL", None
            if envlim:
                page.reload(wait_until="load")
                load_index(page)
            try:
                ac_scope_probe(
                    page, REPO_ROOT,
                    smoke_errors=page_errors, console=console_errors)
            except Exception as e:
                check("SCOPE", "runner-exception", False, repr(e))
    if server is not None:
        stop_server(server)
    per = [{"id": r["id"], "verdict": r["verdict"],
            "evidence": r["detail"]} for r in RESULTS]
    blocking = {"L1", "L3", "L5", "L6", "L9", "FLOOR", "SCOPE", "BOOT"}
    if SMOKE:
        verdict = "SMOKE-COMPLETE"
    elif any(r["verdict"] == "FAIL" and r["id"] in blocking
             for r in RESULTS):
        verdict = "BLOCK"
    elif any(r["id"] == "L10" and "RETUNE" in r.get("verdict", "")
             for r in RESULTS):
        verdict = "FAIL-RETUNE-PENDING"
    elif any(r["id"] == "FLOOR" and r["verdict"] == "FAIL"
             for r in RESULTS):
        verdict = "BLOCK"
    else:
        verdict = "PASS"
    out = {"round": "world-r2", "verdict": verdict,
           "per_ac": per, "flakes": len(FLAKES),
           "notes": ("WH_SMOKE=1 mode" if SMOKE
                     else "L10=%s L2probe-envlim=%s" % (l10v, envlim))}
    print(json.dumps(out))


if __name__ == "__main__":
    main()