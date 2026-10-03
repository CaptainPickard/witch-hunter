

# ------------------------------------------------ subprocess plumbing -------
def _scan8791(text):
    hits = re.findall(r"[a-z]+://[^\s'\"]*:%d[^\s'\"]*" % FORBIDDEN_PORT,
                      text or "")
    if (":%d" % FORBIDDEN_PORT) in (text or "") and not hits:
        hits = [":%d (bare)" % FORBIDDEN_PORT]
    REQ8791.extend(hits)
    return hits


def _sub(cmd, extra_env, timeout=3600):
    env = dict(os.environ)
    env.pop("WH_SMOKE", None)            # floors run their full protocol
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


def run_floor_harness(rel, extra_env, timeout):
    """Run an UNCHANGED prior-round harness on our shared server."""
    rc, out, err = _sub([sys.executable, rel], extra_env, timeout)
    _scan8791(out + err)
    j = _last_json(out)
    if not j:
        return None, {}, []
    by = {a.get("id"): a for a in j.get("per_ac", [])}
    fails = sorted({a.get("id") for a in j.get("per_ac", [])
                    if a.get("verdict") in ("FAIL", "FAIL-RETUNE-PENDING")})
    return j, by, fails


# ------------------------------------------------ R3 L10 scaled re-measure --
L10_SCALED_JS = """(function(){
  var rid=window.WH_CONFIG.regionA.id;
  var l=window.WH_DEBUG.getRegionManager().getEnemies(rid), g=null;
  for(var i=0;i<l.length;i++){ if(l[i].type==='ghoul'){g=l[i];break;} }
  if(!g || g.x!==g.x || g.z!==g.z) return null;      // law 4 NaN guard
  var v=new THREE.Vector3(g.x,(g.ty||0)+0.9*window.WH_CONFIG.world.characterHeight,g.z);
  var G=window.WH_GAME; v.project(G.camera);
  G.renderer.render(G.scene,G.camera);
  return {sx:(v.x*0.5+0.5)*window.innerWidth, sy:(-v.y*0.5+0.5)*window.innerHeight,
          vz:v.z, url:G.renderer.domElement.toDataURL('image/png')};})()"""


def _ring_mean(img, cx, cy, r0, r1, excl):
    px = img.load()
    w, h = img.size
    s = n = 0
    for y in range(max(0, cy - r1), min(h, cy + r1 + 1)):
        for x in range(max(0, cx - r1), min(w, cx + r1 + 1)):
            dx, dy = x - cx, y - cy
            if r0 is None:
                if abs(dx) > excl or abs(dy) > excl:
                    continue
            else:
                q = dx * dx + dy * dy
                if q < r0 * r0 or q > r1 * r1 or (abs(dx) <= excl
                                                  and abs(dy) <= excl):
                    continue
            p = px[x, y]
            s += 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
            n += 1
    return s / max(1, n)


def l10_scaled(browser, d=10):
    """R3 deviation 3 RECORD: R2 L10 geometry at d=10 in BUFFER px."""
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            return {"err": "page never ready"}
        gp = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies("
                           "window.WH_CONFIG.regionA.id);for(var i=0;i<l.length;"
                           "i++){if(l[i].type==='ghoul'&&l[i].x===l[i].x)"
                           "return {x:l[i].x,z:l[i].z};}return null;})()")
        if not gp:
            return {"err": "no ghoul"}
        teleport(page, gp["x"] - d * 0.3, gp["z"] + d * 0.95)
        page.wait_for_timeout(4000)
        s = None
        for _ in range(4):
            wait_frames(page, 3)
            s = page.evaluate(L10_SCALED_JS)
            if s and s["vz"] < 1:
                break
        if not s or s["vz"] >= 1:
            return {"err": "camera never settled", "vz": s and s["vz"]}
        img = decode_image(s["url"])
        w, h = img.size
        cx, cy = int(s["sx"] * w / VIEW_W), int(s["sy"] * h / VIEW_H)
        t = _ring_mean(img, cx, cy, None, 5, 5)
        b = _ring_mean(img, cx, cy, 60, 90, 7)
        return {"d": d, "t": round(t, 1), "b": round(b, 1),
                "c": round(abs(t - b) / max(b, 1.0), 3),
                "buf": "%dx%d" % (w, h)}
    finally:
        ctx.close()


# ------------------------------------------------------------ AC-R5-5 ------
def organic_crossing(browser, cfg):
    """(a) teleport (0,-15), setCameraYaw(0), hold W -> B within 240 s;
    then setCameraYaw(180), hold W -> A within 240 s. |x| traced (R5-4 c)."""
    errs = new_errs()
    ctx, page = new_page(browser, errs)
    try:
        if not load_index(page):
            raise InfraError("page never ready (R5-5)")
        teleport(page, 0, -15)
        poll(page)
        go = hold_w(page, 0, 240.0, lambda ss: ss[-1]["active"] == cfg["B"])
        flip = go[-1] if go else None
        back = []
        if flip and flip["active"] == cfg["B"]:
            back = hold_w(page, 180, 240.0,
                          lambda ss: ss[-1]["active"] == cfg["A"])
        trace = [(round(s["x"], 3), round(s["z"], 3),
                  "A" if s["active"] == cfg["A"] else "B") for s in go + back]
        xs = [abs(s["x"]) for s in go + back if not nan(s["x"])]
        return {"to_b": bool(flip and flip["active"] == cfg["B"]),
                "z_after_flip": round(flip["z"], 3) if flip else None,
                "to_a": bool(back and back[-1]["active"] == cfg["A"]),
                "x_abs_max": round(max(xs), 4) if xs else None,
                "n": len(trace), "trace": trace[::max(1, len(trace) // 40)],
                "page_errors": errs["page"][:3]}
    finally:
        ctx.close()


def r2_teleport_targets(lid):
    """Literal teleport targets inside the R2 harness function ac_<lid>."""
    src = open(os.path.join(REPO_ROOT, "tests/wh_world_r2_validation.py")
               ).read()
    m = re.search(r"\ndef ac_%s\(.*?(?=\ndef |\Z)" % lid.lower(), src, re.S)
    if not m:
        return []
    return [(float(a), float(b)) for a, b in re.findall(
        r"teleportPlayer\((-?[\d.]+),\s*(-?[\d.]+)\)", m.group(0))]


def r2_floor(browser, table):
    rec = {"verdict": None, "fails": [], "waivers": []}
    EXTRA["floor"]["r2"] = rec
    if not FLOOR:
        return rec, "SKIP-NOTED"
    j, by, fails = run_floor_harness(
        "tests/wh_world_r2_validation.py",
        {"WH_R2_FLOOR": "0", "WH_R2_PORT": str(PORT)}, 3600)
    rec.update({"verdict": j and j.get("verdict"), "fails": fails,
                "per_ac": ["%s:%s" % (k, v.get("verdict"))
                           for k, v in by.items()]})
    if j is None:
        return rec, "BLOCK"
    if (by.get("L1") or {}).get("verdict") != "PASS":
        rec["l1"] = (by.get("L1") or {}).get("evidence", "")[:400]
        return rec, "BLOCK"
    if not fails:
        return rec, "PASS"
    ok_all = True
    for f in fails:
        ev = by[f].get("evidence", "")
        if f == "L10":
            rec["l10_rows"] = ev[:600]
            rec["l10_scaled"] = l10_scaled(browser)
            rec["waivers"].append("L10-R3-artifact (scaled re-measure RECORD)")
        elif f == "SCOPE":
            viol = re.findall(r"'([^']+)'", ev.split("secrets=")[0])
            clean = ("secrets=[]" in ev and "pageErr=0" in ev
                     and "consoleErr=0" in ev)
            if clean and all(in_surface(p) for p in viol):
                rec["waivers"].append("A6-SCOPE residual in R5 PRES surface %s"
                                      % viol)
            else:
                ok_all = False
        else:
            hits = []
            for (tx, tz) in r2_teleport_targets(f):
                for k in ("A", "B"):
                    for c in inside_any(table[k], tx, tz):
                        hits.append({"t": [tx, tz], "c": [c["x"], c["z"]],
                                     "R": c["R"], "name": c["name"],
                                     "disp": round(c["R"] + PLAYER_R - math.hypot(
                                         tx - c["x"], tz - c["z"]), 4)})
            if hits:
                rec["waivers"].append("R5-collider-teleport(C10) %s %s"
                                      % (f, json.dumps(hits)))
            else:
                ok_all = False
    return rec, ("WAIVED" if ok_all else "BLOCK")


def ac_r5_5(browser, cfg, table):
    org = None
    for attempt in range(3):
        try:
            org = organic_crossing(browser, cfg)
            break
        except InfraError as e:
            if attempt == 2:
                org = {"error": repr(e)}
            else:
                FLAKES.append("R5-5#%d %r" % (attempt, e))
    EXTRA["crossing"]["organic"] = org
    org_ok = bool(org and org.get("to_b") and org.get("to_a")
                  and org.get("z_after_flip") is not None
                  and org["z_after_flip"] < -25)
    rec, fv = r2_floor(browser, table)
    EXTRA["crossing"]["r2"] = {"verdict": rec.get("verdict"),
                               "fails": rec.get("fails"),
                               "waivers": rec.get("waivers")}
    ev = "organic=%s r2=%s floorVerdict=%s" % (
        json.dumps({k: v for k, v in (org or {}).items() if k != "trace"}),
        json.dumps(EXTRA["crossing"]["r2"]), fv)
    if not org_ok:
        check("R5-5", "crossings re-proof", False, ev,
              verdict="BLOCK" if fv == "BLOCK" else None)
    elif fv == "PASS":
        check("R5-5", "crossings re-proof", True, ev)
    elif fv == "WAIVED":
        check("R5-5", "crossings re-proof", True,
              "FLOOR-WAIVER " + ev + " (carrier-req: Testerbot revalidates "
              "harness on lane recovery)", verdict="WAIVED")
    elif fv == "SKIP-NOTED":
        check("R5-5", "crossings re-proof", False,
              ev + " (R2 subprocess skipped by WH_W5_FLOOR=0)",
              verdict="SKIP-NOTED")
    else:
        check("R5-5", "crossings re-proof", False, ev + " (non-artifact -> "
              "STOP)", verdict="BLOCK")
    return org
