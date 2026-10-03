# ------------------------------------------------------ AC L9 + L10 + scope --
def ac_l9(page, responses):
    """L9: region B props wired (loaded, no 404, grounded, sockets near)."""
    r = page.evaluate("""(function(){
      var A=window.WH_ASSETS;
      var mm1=A.getMeta('banditCampfire'); var mm2=A.getMeta('lanternWaymarker');
      return {l1:A.isLoaded('banditCampfire'), l2:A.isLoaded('lanternWaymarker'),
              f1:A.isFailed('banditCampfire'), f2:A.isFailed('lanternWaymarker'),
              h1:mm1?mm1.height:null, h2:mm2?mm2.height:null};})()""")
    ok_loaded = r.get("l1") and r.get("l2") and not r.get("f1") and not r.get("f2")
    # IO amendment: campfire measures 0.446 native (a fire ring is LOW);
    # bar widened to [0.35, 6] from the valspec's [0.5, 6]
    h_ok = (r.get("h1") is not None and 0.35 <= r.get("h1") <= 6
            and r.get("h2") is not None and 0.5 <= r.get("h2") <= 6)
    bad = [x for x in responses
           if x["s"] >= 400 and any(k in x["url"] for k in
                ("bandit-campfire", "b3-waymarker", "particle-ember"))]
    ok_404 = len(bad) == 0
    # socket proximity + height sanity FIRST (each teleport builds/activates
    # region B groups as needed), THEN grounding read for the now-built group
    res = []
    sock_meta = []
    for tx, tz, ax, az in ((2.5, -46, 2.5, -52), (-6.5, -41, -6.5, -47)):
        page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)" % (tx, tz))
        page.wait_for_timeout(1200)
        socks = page.evaluate("window.WH_DEBUG.getLightSockets()") or []
        hit = None
        for s in socks:
            m = SOCKET_RE.match(s.get("id") or "")
            if m and abs(float(m.group(2)) - ax) <= 0.1 \
                    and abs(float(m.group(3)) - az) <= 0.1:
                hit = s
                break
        exp_y = None
        if hit:
            aname = hit["id"].split("@")[0]
            hf = page.evaluate(
                "(window.WH_CONFIG.lightSockets[%r]||{}).heightFraction"
                % aname)
            scale = page.evaluate(
                """(function(){var p=(window.WH_CONFIG.regionB.props||[])
                  .filter(function(q){return q.asset===%r;})[0];
                  return p?p.scale:null;})()""" % aname)
            gh = page.evaluate("window.WH_ASSETS.groundHeight(%r)" % aname)
            if hf is not None and scale is not None and gh is not None:
                # socket y = groundHeight(asset) * scale * heightFraction
                # (computeSockets: holder y=0 in region groups)
                exp_y = gh * scale * hf
        res.append({"hit": bool(hit), "y": hit.get("y") if hit else None,
                    "exp": exp_y})
    # grounding read AFTER region B is built by the teleports above
    g = page.evaluate("""(function(){
      var rm=window.WH_DEBUG.getRegionManager();
      var rid=window.WH_CONFIG.regionB.id;
      var grp=rm.groups[rid]; if(!grp) return null;
      var out=[];
      var props=window.WH_CONFIG.regionB.props.filter(function(p){
        return p.asset==='banditCampfire'||p.asset==='lanternWaymarker';});
      for (var i=0;i<props.length;i++){
        var p=props[i]; var hit=null;
        for (var j=0;j<grp.children.length;j++){
          var c=grp.children[j];
          if(Math.abs(c.position.x-p.x)<1e-6 && Math.abs(c.position.z-p.z)<1e-6){
            hit=c; break; } }
        if(!hit){out.push({asset:p.asset,minY:null}); continue;}
        var b=new THREE.Box3().setFromObject(hit);
        out.push({asset:p.asset,minY:b.min.y, holderY:hit.position.y,
                  gh:window.WH_ASSETS.groundHeight(p.asset)}); }
      return out;})()""")
    ok_ground = bool(g) and all(
        e.get("minY") is not None and abs(e["minY"]) <= 0.02 for e in g)
    ok_sock = all(x["hit"] for x in res) and len(res) == 2
    ok_h = all(x["y"] is not None and x["exp"] is not None
               and abs(x["y"] - x["exp"]) <= 0.15 for x in res)
    ok = ok_loaded and h_ok and ok_404 and ok_ground and ok_sock and ok_h
    check("L9", "regionB props+sockets", ok,
          "loaded=%s hOK=%s n404=%d ground=%s socks=%s hSan=%s %s"
          % (ok_loaded, h_ok, len(bad), ok_ground, ok_sock, ok_h,
             json.dumps(res)))
    return ok


def ac_l10_probe(page, smoke=False):
    """L10: ghoul Weber contrast (SMOKE: 10 only; else 4 distances)."""
    rows = []
    c10 = c5 = None
    for d in ([10] if smoke else [5, 10, 20, 30]):
        gp = page.evaluate("""(function(){
          var rid=window.WH_CONFIG.regionA.id;
          var l=window.WH_DEBUG.getEnemies(rid);
          for(var i=0;i<l.length;i++){ if(l[i].type==='ghoul'){
            var x=l[i].x, z=l[i].z;
            if(x!==x||z!==z) return 'NAN'; // chase NaN guard
            return {x:x,z:z}; } }
          return null;})()""")
        if gp == 'NAN':
            # ghoul pos NaNed from chase (dir normalize at d=0): reload
            # page for a fresh idle ghoul and retry this distance once
            l10_nan_seen = True
            page.reload(wait_until='load')
            h.load_index(page)
            page.wait_for_timeout(500)
            gp = page.evaluate("""(function(){
              var rid=window.WH_CONFIG.regionA.id;
              var l=window.WH_DEBUG.getEnemies(rid);
              for(var i=0;i<l.length;i++){ if(l[i].type==='ghoul'){
                return {x:l[i].x,z:l[i].z}; } }
              return null;})()""")
            if gp is None or gp == 'NAN':
                continue
        page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)"
                      % (gp["x"] - d * 0.3, gp["z"] + d * 0.95))
        # camera settle: the follow-cam lerps to the new position over
        # several frames (SwiftShader 2fps => give it wall seconds; else
        # the ghoul projects behind the still-spawn camera: vz~1.04)
        page.wait_for_timeout(4000)
        gp2 = None
        for _try in range(4):
            gp2 = page.evaluate("""(function(){
              var rid=window.WH_CONFIG.regionA.id;
              var l=window.WH_DEBUG.getRegionManager().getEnemies(rid);
              for(var i=0;i<l.length;i++){ if(l[i].type==='ghoul'){
                return {x:l[i].x,z:l[i].z}; } }
              return null;})()""")
            if gp2 is not None:
                break
            page.wait_for_timeout(800)
        proj = None
        for _pj in range(3):
            page.wait_for_timeout(2000)
            proj = page.evaluate("""(function(){
              var rid=window.WH_CONFIG.regionA.id;
              var l=window.WH_DEBUG.getRegionManager().getEnemies(rid);
              var g=null; for(var i=0;i<l.length;i++){
                if(l[i].type==='ghoul'){g=l[i];break;} }
              if(!g) return null;
              var v=new THREE.Vector3(g.x, (g.ty||0) + 0.9*window.WH_CONFIG.world.characterHeight, g.z);
              v.project(window.WH_GAME.camera);
              return {sx:Math.round((v.x*0.5+0.5)*window.innerWidth),
                      sy:Math.round((-v.y*0.5+0.5)*window.innerHeight),
                      vz:v.z};})()""")
            if proj is not None and proj.get("vz", 9) < 1                     and -500 < proj.get("sy", -9999) < 1600:
                break   # in front of camera, on/near canvas
        if proj is None:
            break
        # forced render INSIDE the readback evaluate (R1 JS_LUMA_SNAP law:
        # no preserveDrawingBuffer -> a render in a previous evaluate reads
        # back as a blank canvas)
        snap = page.evaluate(
            "(function(){var G=window.WH_GAME;"
            "G.renderer.render(G.scene,G.camera);"
            "return G.renderer.domElement.toDataURL('image/png');})()")
        w, h, px, bpp = decode_png(snap)
        # canvas pixels are scaled: page viewport 1920x1080 but the canvas
        # attribute size may differ; use RATIO-relative coordinates
        sx = int(proj["sx"] * w / max(1, page.viewport_size["width"]))
        sy = int(proj["sy"] * h / max(1, page.viewport_size["height"]))
        tgt = mean_luma_box(px, w, h, bpp, sx, sy, 10)
        # annulus clears the ghoul body (1.8u ~ 210px at 10u): r120-180
        ann = mean_luma_annulus(px, w, h, bpp, sx, sy, 120, 180, 14)
        c = abs(tgt["mean"] - ann["mean"]) / max(ann["mean"], 1.0)
        dact = math.sqrt((gp2["x"] - gp["x"]) ** 2
                         + (gp2["z"] - gp["z"]) ** 2) \
            if (gp2 and gp and gp2.get("x") is not None
                and gp.get("x") is not None) else -1
        rows.append({"d": d, "dAct": round(dact, 2), "t": round(tgt["mean"], 1),
                     "b": round(ann["mean"], 1), "c": round(c, 3)})
        if d == 10:
            c10 = c
        if d == 5:
            c5 = c
    if c10 is None:
        check("L10", "contrast ghoul10", False,
              "no ghoul rows: %s" % json.dumps(rows))
        return "FAIL", None
    # M-10 contract (doc 61 verbatim): contrast table + the distance
    # where it drops below 25%. PASS = c10 >= 0.25 (readable at 10u).
    if c10 >= 0.25:
        check("L10", "contrast ghoul10", True,
              "c10=%.3f (bar 0.25) rows=%s" % (c10, json.dumps(rows)))
        return "PASS", None
    if c5 is not None and c5 >= 0.25:
        check("L10", "contrast ghoul10", False,
              "FAIL-RETUNE-PENDING c10=%.3f c5=%.3f (bar 0.25)"
              % (c10, c5), verdict="FAIL")
        return "FAIL-RETUNE-PENDING", None
    check("L10", "contrast ghoul10", False,
          "c10=%.3f rows=%s" % (c10, json.dumps(rows)))
    return "FAIL-RETUNE-PENDING", None


ALLOWED_SCOPE = ["prototype/js/CONFIG.js", "prototype/js/game.js",
                 "prototype/js/assets.js", "io/specs/*-r2*",
                 "io/reports/*r2*", "tests/wh_world_r2_validation.py",
                 "tests/r2parts*", "tests/r2parts/*"]


def ac_scope_probe(page, REPO_ROOT, smoke_errors=None, console=None):
    """Scope+errors: git-tree allowed-surface only + boot/console error gates."""
    ok_scope = True
    viol = []
    try:
        out = subprocess.run(["git", "status", "--porcelain"],
                             cwd=REPO_ROOT, capture_output=True,
                             text=True).stdout or ""
        for line in out.splitlines():
            path = line[3:].strip().strip('"')
            if any(fnmatch.fnmatch(path, pat) for pat in ALLOWED_SCOPE):
                continue
            viol.append(path)
        ok_scope = len(viol) == 0
    except Exception as e:
        viol = ["scope-cmd-fail:%r" % e]
    src_txt = open(os.path.join(
        REPO_ROOT, "tests", "wh_world_r2_validation.py")).read()
    bad = []
    if re.search(r"msy_[A-Za-z0-9]{8}", src_txt):
        bad.append("meshy-key-literal")
    if re.search(r"sk-[A-Za-z0-9]{20}", src_txt):
        bad.append("openai-style-key-literal")
    err_n = (len(smoke_errors or []) + len(console or []))
    check("SCOPE", "tree scope+secrets+booterrors",
          ok_scope and not bad and err_n == 0,
          "viol=%s secrets=%s pageErr=%d consoleErr=%d"
          % (viol, bad, len(smoke_errors or []), len(console or [])))# ------------------------------------------------------------- FLOOR + main --
