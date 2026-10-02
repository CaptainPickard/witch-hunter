

# ---------------------------------------------------- flake rule + main ----
def run_ac(ac, fn, page, *args):
    """Flake rule: infra-shaped failures (exception / timeout / degenerate
    frame / page not ready) retry up to 2x after a fresh reload; number
    misses return normally and are NEVER retried. Last attempt wins."""
    for attempt in range(3):
        mark = len(RESULTS)
        try:
            return fn(*args)
        except Exception as e:
            del RESULTS[mark:]
            if attempt == 2:
                check(ac, "runner-exception", False, "%r (after %d retries)"
                      % (e, attempt))
                return None
            FLAKES.append("%s#%d %r" % (ac, attempt, e)[:200])
            print("[flake] %s attempt %d: %r" % (ac, attempt, e))
            try:
                page.reload(wait_until="load", timeout=60000)
                load_index(page)
            except Exception:
                pass


def final_verdict():
    by = {r["id"]: r["verdict"] for r in RESULTS}
    if len(FLAKES) >= 3 or "BLOCK" in by.values() or by.get("BOOT") != "PASS":
        return "BLOCK"
    floors_ok = all(by.get(k) in ("PASS", "WAIVED") for k in ("P3", "P4"))
    core = [by.get(k) for k in ("P1", "P2", "P5", "P6")]
    if all(v == "PASS" for v in core) and floors_ok:
        return "PASS"
    hard = [v for v in core if v not in ("PASS", "FAIL-RETUNE-PENDING")]
    if not hard and "FAIL-RETUNE-PENDING" in core:
        return "FAIL-RETUNE-PENDING"
    if all(v == "PASS" for v in core) and not FLOOR:
        return "PASS-FLOOR-SKIPPED"
    return "FAIL"


def main():
    errs = {"console": [], "page": [], "resp": []}
    server, how = None, ""
    div = DISPATCH_DIV
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            server, how = start_server()
            ctx, page = new_page(browser, errs)
            ok = bool(BASE_ROOT) and load_index(page)
            check("BOOT", "identity+ready", ok, "%s base=%s" % (how, BASE_ROOT))
            if ok:
                div = run_ac("P6", ac_p6, page, page) or DISPATCH_DIV
                run_ac("P1", ac_p1, page, browser, page, errs, div)
                run_ac("P2", ac_p2, page, browser, page, div)
                run_ac("P5", ac_p5, page, browser)
                if FLOOR:
                    r2rec = run_ac("P4", ac_p4, page, page) or {}
                    run_ac("P3", ac_p3, page, r2rec)
                else:
                    for k in ("P3", "P4"):
                        check(k, "floor subprocess", True,
                              "skipped by WH_W3_FLOOR=0", verdict="SKIP-NOTED")
            else:
                for k in ("P1", "P2", "P3", "P4", "P5", "P6"):
                    check(k, "page-never-ready", False, "page never ready")
            ctx.close()
            browser.close()
    except Exception as e:
        check("RUN", "harness-exception", False, repr(e)[:300])
    finally:
        stop_server(server)
    verdict = final_verdict()
    out = {"round": "world-r3", "verdict": verdict, "div": div,
           "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                       "evidence": r["detail"]} for r in RESULTS],
           "floor": EXTRA["floor"], "p2_table": EXTRA["p2_table"],
           "flakes": len(FLAKES),
           "notes": "smoke=%s floor=%s divs=%s server=%s flakeLog=%s "
                    "(carrier-req: Testerbot revalidates harness on lane "
                    "recovery)" % (SMOKE, FLOOR, DIVS, how, FLAKES)}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # law 6: exit 0 ALWAYS, last line = JSON
        print(json.dumps({"round": "world-r3", "verdict": "BLOCK",
                          "notes": "fatal %r" % e}))
    sys.exit(0)
