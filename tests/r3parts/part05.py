

# ------------------------------------------------------------ AC-P2 --------
# Sanctioned measurement write (valspec): renderer.internalResDiv + resize.
# A3: every timed render is followed by a 1-px gl.readPixels sync.
SWEEP_JS = """function(a){var divs=a[0], n=a[1], warm=a[2];
  var G=window.WH_GAME, R=G.renderer, C=window.WH_CONFIG.renderer;
  var gl=R.getContext(), buf=new Uint8Array(4), rows=[], orig=C.internalResDiv;
  function one(){R.render(G.scene,G.camera);
    gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,buf);}
  for(var k=0;k<divs.length;k++){
    C.internalResDiv=divs[k]; window.dispatchEvent(new Event('resize'));
    for(var i=0;i<warm;i++) one();
    var t0=performance.now();
    for(var j=0;j<n;j++) one();
    var ms=(performance.now()-t0)/n;
    rows.push({div:divs[k], w:R.domElement.width, h:R.domElement.height,
      ms:ms, tris:R.info.render.triangles, calls:R.info.render.calls});
  }
  C.internalResDiv=orig; window.dispatchEvent(new Event('resize'));
  return rows;}"""

TRIS_JS = """(function(){var G=window.WH_GAME;
  G.renderer.render(G.scene,G.camera);
  return {tris:G.renderer.info.render.triangles,
          calls:G.renderer.info.render.calls};})()"""


def tmp_tree(src_prototype=None, archive_rev=None):
    """Temp repo-shaped root: prototype/ (copy of worktree or git archive
    of archive_rev) + tools/build_v7.py; every other top-level entry is
    symlinked (assets are served from the repo root)."""
    root = tempfile.mkdtemp(prefix="whr3_")
    if archive_rev:
        arc = subprocess.run(["git", "archive", archive_rev, "prototype"],
                             cwd=REPO_ROOT, capture_output=True, timeout=120)
        subprocess.run(["tar", "-x", "-C", root], input=arc.stdout,
                       capture_output=True, timeout=120)
    else:
        shutil.copytree(src_prototype, os.path.join(root, "prototype"),
                        ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(root, "tools"))
    shutil.copy(os.path.join(REPO_ROOT, "tools", "build_v7.py"),
                os.path.join(root, "tools", "build_v7.py"))
    for ent in os.listdir(REPO_ROOT):
        if ent in ("prototype", "tools", ".git"):
            continue
        os.symlink(os.path.join(REPO_ROOT, ent), os.path.join(root, ent))
    return root


def pre_triangles(browser):
    """Pre-implementation triangle count at the same pose (A spawn after
    settle) measured on a git-archive copy of the R2 base tree."""
    if PRE_TRIS_ENV:
        return int(PRE_TRIS_ENV), "env"
    root = tmp_tree(archive_rev=BASE_COMMIT)
    proc = None
    try:
        proc, base = spawn_server(root)
        if not base:
            return None, "pre-server-failed"
        errs = {"console": [], "page": [], "resp": []}
        ctx, pg = new_page(browser, errs)
        try:
            if not load_index(pg, base):
                return None, "pre-page-never-ready"
            return pg.evaluate(TRIS_JS)["tris"], "archive %s" % BASE_COMMIT
        finally:
            ctx.close()
    finally:
        stop_server(proc)
        shutil.rmtree(root, ignore_errors=True)


def ac_p2(browser, page, div):
    reps = 1 if SMOKE else 3
    pre, pre_src = pre_triangles(browser)
    allrows = []
    for rep in range(reps):
        rows = page.evaluate(SWEEP_JS, [DIVS, 20, 3])
        for r in rows:
            r["rep"] = rep
        allrows.extend(rows)
    back = poll_dims(page, (round(VIEW_W / div), round(VIEW_H / div)))
    restored = (back["cw"], back["ch"]) == (round(VIEW_W / div),
                                            round(VIEW_H / div))
    base1 = {r["rep"]: r for r in allrows if r["div"] == 1}
    a_ok = True
    pre_miss_reps = 0
    for rep in range(reps):
        tr = {r["tris"] for r in allrows if r["rep"] == rep}
        a_ok = a_ok and len(tr) == 1
        if pre is not None and tr != {pre}:
            pre_miss_reps += 1
    pre_fail = pre is not None and pre_miss_reps == reps
    b_ok = True
    table = []
    med1 = None
    for d in DIVS:
        rs = [r for r in allrows if r["div"] == d]
        ms = [round(r["ms"], 2) for r in rs]
        med = statistics.median(ms) if ms else None
        if d == 1:
            med1 = med
        r0, b1 = rs[0], base1.get(rs[0]["rep"])
        elim = (1 - (r0["w"] * r0["h"]) / float(b1["w"] * b1["h"])
                if b1 else None)
        exp = 1 - 1.0 / (d * d)
        if elim is None or abs(elim - exp) > 0.01:
            b_ok = False
        table.append({"div": d, "wxh": "%dx%d" % (r0["w"], r0["h"]),
                      "px": r0["w"] * r0["h"],
                      "eliminated": None if elim is None else round(elim, 4),
                      "expected": round(exp, 4), "ms": ms, "median": med,
                      "tris": [r["tris"] for r in rs],
                      "calls": [r["calls"] for r in rs]})
    for t in table:
        t["ratio_vs_div1"] = (round(t["median"] / med1, 3)
                              if med1 and t["median"] is not None else None)
    EXTRA["p2_table"] = table
    m2 = [t["median"] for t in table if t["div"] == 2]
    c_ok = bool(m2) and med1 is not None and m2[0] <= med1
    ev = ("a=%s(pre=%s src=%s preMissReps=%d/%d) b=%s c=%s restored=%s "
          "hwbar=ENV-LIMIT GPU (p99<=16.6ms GPU-only, M-08) table=%s"
          % (a_ok and not pre_fail, pre, pre_src, pre_miss_reps, reps,
             b_ok, c_ok, restored, json.dumps(table)))
    if a_ok and not pre_fail and b_ok and restored and c_ok:
        check("P2", "fragment cost drop", True, ev)
    elif a_ok and not pre_fail and b_ok and restored:
        check("P2", "fragment cost drop", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("P2", "fragment cost drop", False, ev)
