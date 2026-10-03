

# ---------------------------------------------------- verdict + main -------
GATING = ["R5-1", "R5-2", "R5-3", "R5-4", "R5-5", "PRES", "PRES-R1"]
WAIVABLE = ("R5-5", "PRES-R1")


def guard(ac, fn, *args):
    """Per-AC try/except (law 6): exceptions become recorded FAIL data."""
    try:
        return fn(*args)
    except Exception as e:
        check(ac, "runner-exception", False, repr(e)[:300])
        return None


def final_verdict():
    by = {}
    for r in RESULTS:
        by[r["id"]] = r["verdict"]          # last attempt wins
    skipped = [k for k in GATING if by.get(k) == "SKIP-NOTED"]
    if (len(FLAKES) >= 3 or "BLOCK" in by.values()
            or by.get("BOOT") != "PASS" or by.get("NET") != "PASS"):
        return "BLOCK", skipped, by
    if all(by.get(k) == "PASS" or (k in WAIVABLE and by.get(k) == "WAIVED")
           for k in GATING):
        return "PASS", skipped, by
    soft = ("PASS", "WAIVED", "SKIP-NOTED", "FAIL-RETUNE-PENDING")
    if (any(by.get(k) == "FAIL-RETUNE-PENDING" for k in GATING)
            and all(by.get(k) in soft for k in GATING)):
        return "FAIL-RETUNE-PENDING", skipped, by
    return "FAIL", skipped, by


def boot_cfg(browser):
    for attempt in range(3):
        errs = new_errs()
        ctx, page = new_page(browser, errs)
        try:
            if load_index(page):
                cfg = page.evaluate(CFG_JS)
                return cfg, errs
            raise InfraError("page never ready (BOOT)")
        except Exception as e:
            if attempt == 2:
                return None, {"error": repr(e)[:300]}
            FLAKES.append("BOOT#%d %r" % (attempt, e))
        finally:
            ctx.close()


def main():
    server, how, ident = None, "", False
    cfg = table = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            server, how, ident = start_server()
            if BASE_ROOT:
                cfg, berr = boot_cfg(browser)
            ok = bool(BASE_ROOT) and cfg is not None
            if ok:
                table = collider_table(cfg)
            check("BOOT", "server+ready", ok,
                  "%s base=%s identity(R5 signature)=%s metaMissing=%s" % (
                      how, BASE_ROOT, ident,
                      [c["name"] for k in ("A", "B") for c in
                       (table or {}).get(k, {}).get("circles", [])
                       if not c["meta"]] if table else None))
            if ok:
                guard("R5-1", ac_r5_1, browser, cfg, table)
                guard("R5-2", ac_r5_2, browser, cfg, table)
                guard("R5-3", ac_r5_3, browser, cfg)
                org = guard("R5-5", ac_r5_5, browser, cfg, table)
                guard("R5-4", ac_r5_4, browser, table, org)
            else:
                for k in ("R5-1", "R5-2", "R5-3", "R5-4", "R5-5"):
                    check(k, "context-never-ready", False, "boot failed")
            guard("PRES", ac_pres, browser)
            if ok:
                guard("PRES-R1", ac_pres_r1, browser)
            else:
                check("PRES-R1", "context-never-ready", False, "boot failed")
            browser.close()
    except Exception as e:
        check("RUN", "harness-exception", False, repr(e)[:300])
    finally:
        stop_server(server)
    check("NET", "no :%d request" % FORBIDDEN_PORT, not REQ8791,
          "hits=%s" % REQ8791[:5], verdict=None if not REQ8791 else "BLOCK")
    verdict, skipped, by = final_verdict()
    val = EXTRA["validator"]
    col = EXTRA["colliders"]
    r1 = EXTRA["floor"].get("r1") or {}
    out = {"round": "world-r5", "verdict": verdict,
           "r_play": EXTRA["r_play"], "margin": EXTRA["margin"],
           "sweep": EXTRA["sweep"],
           "validator": {"report": val.get("report"),
                         "recompute": val.get("recompute"),
                         "neg": val.get("neg")},
           "camera": EXTRA["camera"],
           "colliders": {"radii": col.get("radii", []),
                         "exempt": col.get("exempt", []),
                         "a1": col.get("a1", {})},
           "crossing": {"organic": {k: v for k, v in
                                    (EXTRA["crossing"].get("organic") or {}
                                     ).items() if k != "trace"},
                        "r2": EXTRA["crossing"].get("r2", {})},
           "ground": EXTRA["ground"],
           "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                       "evidence": r["detail"]} for r in RESULTS],
           "floor": {"r1": {"waivers": r1.get("waivers", []),
                            "a2_pre": r1.get("a2_pre"),
                            "a2_post": r1.get("a2_post"),
                            "a2_pre_src": r1.get("a2_pre_src")},
                     "r2": EXTRA["floor"].get("r2", {})},
           "skip_noted": skipped, "flakes": len(FLAKES),
           "notes": "smoke=%s floor=%s headings=%s server=%s flakeLog=%s "
                    "(carrier-req: Testerbot revalidates harness on lane "
                    "recovery)" % (SMOKE, FLOOR, HEADINGS, how, FLAKES)}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # law 6: exit 0 ALWAYS, last line = JSON
        print(json.dumps({"round": "world-r5", "verdict": "BLOCK",
                          "notes": "fatal %r" % e}))
    sys.exit(0)
