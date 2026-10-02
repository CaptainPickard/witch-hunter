

# ------------------------------------------------ floor subprocess runner --
def run_floor_harness(rel, extra_env, timeout):
    """Run an UNCHANGED prior-round harness on our shared server; parse
    the final JSON (balanced-join from the last '{'-leading line, works
    for R1's pretty-printed and R2's one-line verdicts)."""
    env = dict(os.environ)
    env.pop("WH_SMOKE", None)            # floors run their full protocol
    env["WH_BASE_ROOT"] = BASE_ROOT
    env.update(extra_env)
    proc = subprocess.run([sys.executable, rel], cwd=REPO_ROOT,
                          capture_output=True, text=True, timeout=timeout,
                          env=env)
    lines = (proc.stdout or "").splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("{"):
            try:
                j = json.loads("\n".join(lines[i:]))
                by = {a.get("id"): a for a in j.get("per_ac", [])}
                fails = sorted({a.get("id") for a in j.get("per_ac", [])
                                if a.get("verdict") in
                                ("FAIL", "FAIL-RETUNE-PENDING")})
                return j, by, fails
            except Exception:
                continue
    return None, {}, []


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
                rr = dx * dx + dy * dy
                if rr < r0 * r0 or rr > r1 * r1 or (abs(dx) <= excl
                                                    and abs(dy) <= excl):
                    continue
            p = px[x, y]
            s += 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
            n += 1
    return s / max(1, n)


def l10_scaled(page, d=10):
    """RECORD-only judgment evidence (valspec AC-P4): R2 L10 geometry at
    d=10, box +-5 / annulus r60-90 in BUFFER px (= R2's footprint / 2)."""
    gp = page.evaluate("(function(){var l=window.WH_DEBUG.getEnemies("
                       "window.WH_CONFIG.regionA.id);for(var i=0;i<l.length;"
                       "i++){if(l[i].type==='ghoul'&&l[i].x===l[i].x)"
                       "return {x:l[i].x,z:l[i].z};}return null;})()")
    if not gp:
        return {"err": "no ghoul"}
    page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)"
                  % (gp["x"] - d * 0.3, gp["z"] + d * 0.95))
    page.wait_for_timeout(4000)
    s = None
    for _ in range(4):
        wait_frames(page, 3)
        s = page.evaluate(L10_SCALED_JS)
        if s and s["vz"] < 1:            # law 3: settle (vz>1 = behind)
            break
    if not s or s["vz"] >= 1:
        return {"err": "camera never settled", "vz": s and s["vz"]}
    img = decode_image(s["url"])
    w, h = img.size
    cx, cy = int(s["sx"] * w / VIEW_W), int(s["sy"] * h / VIEW_H)
    t = _ring_mean(img, cx, cy, None, 5, 5)
    b = _ring_mean(img, cx, cy, 60, 90, 7)
    return {"d": d, "t": round(t, 1), "b": round(b, 1),
            "c": round(abs(t - b) / max(b, 1.0), 3), "buf": "%dx%d" % (w, h)}


def ac_p4(page):
    """R2 floor (A5: WH_R2_FLOOR=0, WH_R2_PORT = our port for R2's
    identity probe). Waivers: L10-alone drift (pre-declared R3 artifact,
    scaled re-measure RECORD) + A6 SCOPE residual wholly in P5 surface."""
    j, by, fails = run_floor_harness(
        "tests/wh_world_r2_validation.py",
        {"WH_R2_FLOOR": "0", "WH_R2_PORT": str(PORT)}, 3600)
    rec = {"verdict": j and j.get("verdict"), "fails": fails, "waivers": [],
           "per_ac": ["%s:%s" % (k, v.get("verdict")) for k, v in by.items()]}
    EXTRA["floor"]["r2"] = rec
    if j is None:
        check("P4", "R2 floor", False, "no parseable R2 verdict")
        return rec
    if j.get("verdict") == "PASS":
        check("P4", "R2 floor", True, "r2=PASS %s" % rec["per_ac"])
        return rec
    ok_all = bool(fails)
    for f in fails:
        ev = by[f].get("evidence", "")
        if f == "L10":
            rec["l10_rows"] = ev
            rec["l10_scaled"] = l10_scaled(page)
            rec["waivers"].append("L10-R3-artifact (buffer-px annulus 2x "
                                  "on screen at div 2; pre-declared)")
        elif f == "SCOPE":
            viol = re.findall(r"'([^']+)'", ev.split("secrets=")[0])
            clean = ("secrets=[]" in ev and "pageErr=0" in ev
                     and "consoleErr=0" in ev)
            if clean and all(in_surface(p) for p in viol):
                rec["waivers"].append("A6-SCOPE residual in P5 surface %s"
                                      % viol)
            else:
                ok_all = False
        else:
            ok_all = False
    if ok_all:
        check("P4", "R2 floor", True,
              "FLOOR-WAIVER r2=%s fails=%s waivers=%s l10_scaled=%s "
              "(carrier-req: Testerbot revalidates harness on lane recovery)"
              % (j.get("verdict"), fails, rec["waivers"],
                 rec.get("l10_scaled")), verdict="WAIVED")
    else:
        check("P4", "R2 floor", False,
              "r2=%s fails=%s waived=%s (non-artifact -> STOP)"
              % (j.get("verdict"), fails, rec["waivers"]), verdict="BLOCK")
    return rec
