"""PART7: main + ACS + __main__ (orig lines 1218..~1300) for the harness rebuild."""

MAIN_PART = r'''ACS = [("A1-1", ac_a1_1), ("A1-2", ac_a1_2), ("A1-3", ac_a1_3),
       ("A1-4", ac_a1_4), ("A2-1", ac_a2_1), ("A2-2", ac_a2_2),
       ("A2-3", ac_a2_3), ("A2-4", ac_a2_4), ("A3-1", ac_a3_1),
       ("A3-2", ac_a3_2), ("A3-3", ac_a3_3), ("A3-4", ac_a3_4),
       ("A3-5", ac_a3_5), ("A3-6", ac_a3_6), ("A4-1", ac_a4_1),
       ("A4-2", ac_a4_2), ("A4-3", ac_a4_3), ("A4-4", ac_a4_4)]


def main():
    server = start_server()
    browser = None
    t_start = time.time()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
            page = browser.new_page()
            page.on("pageerror", lambda e: CRASHES.append("pageerror: %s" % e))
            page.on("console", lambda m: DIAGNOSTICS.append(
                "console.%s: %s" % (m.type, m.text)
            ) if m.type in ("error", "warning") else None)
            for ac_id, fn in ACS:
                try:
                    fn(page)
                except Exception as e:
                    CRASHES.append("AC-%s runner exception: %r" % (ac_id, e))
                    check(ac_id, "runner-guard", False, "runner exception %r" % e)
                if time.time() - t_start > 240:
                    note("runtime budget exceeded; remaining ACs not run")
                    break
            browser.close()
    except Exception as e:
        CRASHES.append("main runner exception: %r" % e)
    finally:
        stop_server(server)
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["ok"])
    failed = total - passed
    print()
    print("=" * 72)
    print("COMBAT-DS1-A SMOKE SUMMARY  total=%d pass=%d fail=%d crashes=%d" %
          (total, passed, failed, len(CRASHES)))
    for r in RESULTS:
        print("  AC-%s %-*s %s" % (r["id"][3:], 28, r["name"],
                                   "PASS" if r["ok"] else "FAIL"))
    print("ZERO CRASHES: %s" % ("YES" if not CRASHES
                                else "NO -> %s" % (CRASHES[:3],)))
    print("=" * 72)
    print(json.dumps({"round": "combat-ds1-A", "total": total,
                      "pass": passed, "fail": failed,
                      "crashes": len(CRASHES),
                      "per_ac": [dict(id=r["id"],
                                      verdict="PASS" if r["ok"] else "FAIL")
                                 for r in RESULTS]}, indent=1))
    sys.exit(1 if CRASHES else 0)


if __name__ == "__main__":
    main()
'''