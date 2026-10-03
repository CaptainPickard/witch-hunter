

# ---------------------------------------------------- verdict + main -------
GATING = ["R4-1", "R4-2", "R4-3", "R4-4", "R4-5", "PNG", "PRES"]


def guard(ac, fn, *args):
    """Per-AC try/except (law 6): exceptions become recorded FAIL data.
    Infra retries live in collect_retry (flake rule); number misses are
    never retried."""
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
    ok_states = ("PASS", "WAIVED")
    if all(by.get(k) == "PASS" or (k == "R4-5" and by.get(k) == "WAIVED")
           for k in GATING):
        return "PASS", skipped, by
    rest = [k for k in GATING if k != "R4-3"]
    if (by.get("R4-3") == "FAIL-RETUNE-PENDING" and by.get("R4-1") == "PASS"
            and all(by.get(k) in ok_states + ("SKIP-NOTED",) for k in rest)):
        return "FAIL-RETUNE-PENDING", skipped, by
    return "FAIL", skipped, by


def main():
    server, how, ident = None, "", False
    on = off = pre = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            server, how, ident = start_server()
            if BASE_ROOT:
                on = collect_retry(browser, False)
                off = collect_retry(browser, True)
            ok = bool(BASE_ROOT) and on is not None and "error" not in on
            check("BOOT", "server+ready", ok,
                  "%s base=%s identity(R4 signature)=%s on_err=%s off_err=%s"
                  % (how, BASE_ROOT, ident, (on or {}).get("error"),
                     (off or {}).get("error")))
            if ok and "error" not in off:
                pre = baseline(browser, on)
                guard("R4-1", ac_r4_1, on, off, pre)
                guard("R4-2", ac_r4_2, on, off)
                guard("R4-3", ac_r4_3, on, off)
            else:
                for k in ("R4-1", "R4-2", "R4-3"):
                    check(k, "context-never-ready", False, "collect failed")
            guard("PNG", ac_png)
            guard("PRES", ac_pres, browser)
            if ok and "error" not in off:
                guard("R4-4", ac_r4_4, on, off)
                guard("R4-5", ac_r4_5, pre, on)
            else:
                for k in ("R4-4", "R4-5"):
                    check(k, "context-never-ready", False, "collect failed")
            browser.close()
    except Exception as e:
        check("RUN", "harness-exception", False, repr(e)[:300])
    finally:
        stop_server(server)
    check("NET", "no :%d request" % FORBIDDEN_PORT, not REQ8791,
          "hits=%s" % REQ8791[:5], verdict=None if not REQ8791 else "BLOCK")
    verdict, skipped, by = final_verdict()
    out = {"round": "world-r4", "verdict": verdict, "atlas": ATLAS,
           "kill_switch": {"on": EXTRA["kill_switch"].get("on", []),
                           "off": EXTRA["kill_switch"].get("off", []),
                           "rewrite_count":
                               EXTRA["kill_switch"].get("rewrite_count")},
           "per_ac": [{"id": r["id"], "verdict": r["verdict"],
                       "evidence": r["detail"]} for r in RESULTS],
           "mem_table": EXTRA["mem_table"],
           "floor": EXTRA["floor"], "skip_noted": skipped,
           "flakes": len(FLAKES),
           "notes": "smoke=%s floor=%s server=%s pre=%s flakeLog=%s "
                    "(carrier-req: Testerbot revalidates harness on lane "
                    "recovery)" % (SMOKE, FLOOR, how,
                                   (pre or {}).get("src"), FLAKES)}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # law 6: exit 0 ALWAYS, last line = JSON
        print(json.dumps({"round": "world-r4", "verdict": "BLOCK",
                          "notes": "fatal %r" % e}))
    sys.exit(0)
