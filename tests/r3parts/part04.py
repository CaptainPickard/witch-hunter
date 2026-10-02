

# ------------------------------------------------------------ AC-P1 --------
SNAP_JS = """(function(){var G=window.WH_GAME, c=G.renderer.domElement;
  G.renderer.render(G.scene,G.camera);     // law 2: render+readback 1 eval
  return {cw:c.width, ch:c.height, dw:c.clientWidth, dh:c.clientHeight,
          ir:getComputedStyle(c).imageRendering,
          pr:G.renderer.getPixelRatio(), dpr:window.devicePixelRatio,
          url:c.toDataURL('image/png')};})()"""

DIMS_JS = """(function(){var c=window.WH_GAME.renderer.domElement;
  return {cw:c.width, ch:c.height, pr:window.WH_GAME.renderer.getPixelRatio(),
          dpr:window.devicePixelRatio};})()"""


def poll_dims(page, want, wall=20.0):
    """Wait (wall-generous) until the canvas buffer reaches want=(w,h)."""
    d = None
    deadline = time.time() + wall
    while time.time() < deadline:
        d = page.evaluate(DIMS_JS)
        if (d["cw"], d["ch"]) == want:
            return d
        page.wait_for_timeout(300)
    return d


def ac_p1(browser, page, errs, div):
    want = (round(VIEW_W / div), round(VIEW_H / div))
    # (a) buffer readback
    s = page.evaluate(SNAP_JS)
    img = decode_image(s["url"])
    if is_degenerate(img):
        raise InfraError("degenerate readback frame")
    a_ok = ((s["cw"], s["ch"]) == want and img.size == want
            and (s["dw"], s["dh"]) == (VIEW_W, VIEW_H)
            and s["ir"] in ("pixelated", "crisp-edges") and s["pr"] == 1)
    a_ev = ("buf=%dx%d dec=%dx%d disp=%dx%d ir=%s pr=%s"
            % (s["cw"], s["ch"], img.size[0], img.size[1], s["dw"], s["dh"],
               s["ir"], s["pr"]))
    # (b) A2 block metrics on the composited display
    wait_frames(page, 2)
    shot = decode_image(page.screenshot(type="png", full_page=False))
    if is_degenerate(shot):
        raise InfraError("blank screenshot")
    try:
        shot.save("/tmp/whr3_p1_shot.png")
    except Exception:
        pass
    m = block_metrics(shot)
    b_ok = block_bars(m)
    # (c) resize path
    page.set_viewport_size({"width": 1280, "height": 720})
    wait_frames(page, 2)
    dc = poll_dims(page, (round(1280 / div), round(720 / div)))
    page.set_viewport_size({"width": VIEW_W, "height": VIEW_H})
    wait_frames(page, 2)
    dr = poll_dims(page, want)
    c_ok = ((dc["cw"], dc["ch"]) == (round(1280 / div), round(720 / div))
            and (dr["cw"], dr["ch"]) == want)
    # (d) DPR law: dsf=2 context still renders the low-res buffer
    derr = {"console": [], "page": [], "resp": []}
    ctx2, p2 = new_page(browser, derr, dsf=2)
    try:
        if not load_index(p2):
            raise InfraError("dsf2 page never ready")
        dd = poll_dims(p2, want, wall=10.0)
    finally:
        ctx2.close()
    d_ok = (dd["cw"], dd["ch"]) == want and dd["pr"] == 1 and dd["dpr"] == 2
    ev = ("a=%s[%s] b=%s[%s] c=%s[720p=%dx%d back=%dx%d] "
          "d=%s[dsf2 buf=%dx%d pr=%s dpr=%s]"
          % (a_ok, a_ev, b_ok, json.dumps(m), c_ok, dc["cw"], dc["ch"],
             dr["cw"], dr["ch"], d_ok, dd["cw"], dd["ch"], dd["pr"],
             dd["dpr"]))
    if a_ok and b_ok and c_ok and d_ok:
        check("P1", "pixel-locked upscale", True, ev)
    elif a_ok and c_ok and d_ok:
        check("P1", "pixel-locked upscale", False, ev,
              verdict="FAIL-RETUNE-PENDING")
    else:
        check("P1", "pixel-locked upscale", False, ev)
