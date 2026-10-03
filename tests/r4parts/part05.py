

# ---------------------------------------------------- PNG byte proof -------
def ac_png():
    """3 PNGs: HTTP 200 from our root, image/png, decode 512x512, served
    sha256 == worktree file == PNG_COMMIT blob (re-bake = FAIL, B8)."""
    rows, bad = [], []
    for b in BODIES:
        rel = PNG_PATHS[b]
        row = {"body": b}
        try:
            st, ct, data = _served(BASE_ROOT, rel)
            img = decode_image(data)
            blob = git_blob(PNG_COMMIT, rel)
            row.update({"status": st, "ct": ct, "dims": "%dx%d" % img.size,
                        "served": sha256_bytes(data)[:16],
                        "worktree": sha256_file(os.path.join(REPO_ROOT,
                                                             rel))[:16],
                        "blob": sha256_bytes(blob)[:16] if blob else None,
                        "bytes": len(data)})
            if not (st == 200 and ct.startswith("image/png")
                    and img.size == (ATLAS, ATLAS)
                    and row["served"] == row["worktree"] == row["blob"]):
                bad.append(b)
        except Exception as e:
            row["err"] = repr(e)[:120]
            bad.append(b)
        rows.append(row)
    check("PNG", "pixelated PNG byte proof", not bad,
          "bad=%s rows=%s" % (bad, json.dumps(rows)))


# --------------------------------------------- AC-R4-4 anim regressions -----
def _scan8791(text):
    hits = re.findall(r"[a-z]+://[^\s'\"]*:%d[^\s'\"]*" % FORBIDDEN_PORT,
                      text or "")
    REQ8791.extend(hits)
    return hits


V3_RUNNER = r'''
import re, sys
root = sys.argv[1]
src = open("tests/wh_v3_anim_probes.py").read()
pat = re.compile(r"^ORIGINS = \[.*\]$", re.M)
n = len(pat.findall(src))
print("ORIGINS_REWRITE_COUNT=%d" % n)
sys.stdout.flush()
if n != 1:
    sys.exit(97)
src = pat.sub(lambda m: "ORIGINS = [%r]" % root, src)
sys.argv = ["tests/wh_v3_anim_probes.py"]
exec(compile(src, "tests/wh_v3_anim_probes.py", "exec"),
     {"__name__": "__main__", "__file__": "tests/wh_v3_anim_probes.py"})
'''


def _sub(cmd, extra_env, timeout=3600):
    env = dict(os.environ)
    env.pop("WH_SMOKE", None)            # regressions run their full protocol
    env["WH_BASE_ROOT"] = BASE_ROOT
    env.update(extra_env)
    try:
        p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        return "timeout", str(e.stdout or ""), "timeout"


def _last_json(out):
    lines = out.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("{"):
            try:
                return json.loads("\n".join(lines[i:]))
            except Exception:
                continue
    return None


def anim_v3():
    rc, out, err = _sub([sys.executable, "-c", V3_RUNNER, BASE_ROOT], {})
    m = re.search(r"ORIGINS_REWRITE_COUNT=(\d+)", out)
    cnt = int(m.group(1)) if m else None
    passed = "V3 ANIM PROBES: PASS" in out
    keys = None
    i = out.find("V3 ANIM PROBES:")
    if i >= 0:
        try:
            keys = sorted(json.loads(out[out.index("\n", i) + 1:]).keys())
        except Exception:
            keys = None
    hits = _scan8791(out + err)
    ok = (rc == 0 and cnt == 1 and passed and keys == [BASE_ROOT]
          and not hits)
    return ok, {"rc": rc, "rewrite_count": cnt, "line_pass": passed,
                "keys": keys, "8791": hits[:3], "tail": err[-160:] if rc else ""}


def anim_ds1():
    rc, out, err = _sub([sys.executable, "tests/wh_combat_ds1_validation.py"],
                        {})
    j = _last_json(out) or {}
    m = re.search(r"COMBAT-DS1-A SMOKE SUMMARY\s+total=(\d+) pass=(\d+) "
                  r"fail=(\d+) crashes=(\d+)", out)
    budget = "runtime budget exceeded" in out
    hits = _scan8791(out + err)
    verdict = ("PASS" if j and j.get("fail") == 0 and j.get("crashes") == 0
               else "FAIL")
    ok = verdict == "PASS" and not hits
    return ok, {"rc": rc, "verdict": verdict, "total": j.get("total"),
                "failed": j.get("fail"), "crashes": j.get("crashes"),
                "summary": m.group(0) if m else None, "budget_cut": budget,
                "fails": [a.get("id") for a in j.get("per_ac", [])
                          if a.get("verdict") != "PASS"], "8791": hits[:3]}


def anim_v2():
    rc, out, err = _sub([sys.executable, "tests/wh_v2_verify.py"],
                        {"WH_BASE_PROXY": "http://127.0.0.1:9/"})
    m = re.search(r"ASSET AUDIT \[root\]: (\d+) glb fetches, non-200: "
                  r"(\[.*?\]) =>", out)
    total = int(m.group(1)) if m else None
    non200 = m.group(2) if m else None
    hits = _scan8791(out + err)
    ok = (rc == 0 and m is not None and non200 == "[]"
          and "V2 VERIFY: PASS" in out and not hits)
    return ok, {"rc": rc, "glb_total": total, "non200": non200,
                "proxy_ran": "ASSET AUDIT [proxy]" in out, "8791": hits[:3]}


def ac_r4_4(on, off):
    """B3: whanim2's committed A12 regression set as subprocesses + in-harness
    clips/bones (both contexts) + frozen-GLB sha law."""
    inh = []
    for b in BODIES:
        r, o = _row(on, b), _row(off, b)
        if r.get("clips") != 6 or o.get("clips") != 6:
            inh.append("%s clips %s/%s" % (b, r.get("clips"), o.get("clips")))
        if r.get("bones") is None or r.get("bones") != o.get("bones"):
            inh.append("%s bones %s/%s" % (b, r.get("bones"), o.get("bones")))
        blob = git_blob(BASE_COMMIT, GLB_PATHS[b])
        if not blob or sha256_bytes(blob) != sha256_file(
                os.path.join(REPO_ROOT, GLB_PATHS[b])):
            inh.append("%s GLB sha drift" % b)
    bones = {b: [_row(on, b).get("bones"), _row(off, b).get("bones")]
             for b in BODIES}
    if not FLOOR:
        check("R4-4", "anim regressions", False,
              "subprocesses skipped by WH_W4_FLOOR=0 (wh_v7_weave SKIP-NOTED: "
              "writes builds/) inHarness=%s bones=%s"
              % (inh or "ok", bones), verdict="SKIP-NOTED")
        return
    res = {}
    for k, fn in (("v3", anim_v3), ("ds1", anim_ds1), ("v2", anim_v2)):
        try:
            res[k] = fn()
        except Exception as e:
            res[k] = (False, {"err": repr(e)[:200]})
    EXTRA["floor"]["anim"] = {k: v[1] for k, v in res.items()}
    ok = all(v[0] for v in res.values()) and not inh
    ev = ("v3=%s ds1=%s v2=%s inHarness=%s bones=%s v7weave=SKIP-NOTED "
          "(writes builds/; v7 load covered by PRES)" % (
              json.dumps(res["v3"][1]), json.dumps(res["ds1"][1]),
              json.dumps(res["v2"][1]), inh or "ok", bones))
    check("R4-4", "anim regressions", ok, ev,
          verdict=None if ok else "BLOCK")
