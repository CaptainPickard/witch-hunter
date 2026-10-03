# ----------------------------------------------------------------- AC L3 -----
FLICKER_ARM = """(function(){
  window.__r2fl=[]; window.__r2ft=[]; var G=window.WH_GAME; var lant=null;
  G.scene.traverse(function(o){
    if(o.isPointLight&&o.color.getHex()===0xffb060) lant=o; });
  if(!lant) return 'no-lantern';
  window.__r2lant=lant; window.__r2n=0;
  function cb(){
    if(window.__r2n>=60) return;
    // SwiftShader renders on demand: force a render each sample so the
    // flicker tick (poolTick/frame) has visibly advanced state. The
    // WALL timestamp of each sample rides along (performance.now) —
    // C15 normalization needs the real sample gap.
    try{G.renderer.render(G.scene,G.camera);}catch(e){}
    window.__r2fl.push(window.__r2lant.intensity);
    window.__r2ft.push(performance.now());
    window.__r2n++;
    requestAnimationFrame(cb); }
  requestAnimationFrame(cb); return 'armed'; })()"""


def ac_l3(page, scan):
    """L3: lantern exists/config/chain + flicker band + follow."""
    L = (scan.get("cfg") or {})
    lant = scan.get("lantern")
    base = L.get("lanternIntensity", 6.5)
    ok_e = lant is not None
    ok_c = ok_e and lant.get("c") == 0xffb060
    ok_chain = ok_e and lant.get("chainToPlayerRoot") is True
    ok_d = ok_e and abs(lant.get("d", -1) - L.get("lanternDistance", 12)) < 1e-9 \
        and lant.get("dec") == L.get("lanternDecay", 2)
    only1 = (scan.get("point", 0) - len(scan.get("pool") or [])) == 1
    # per-frame sampler: the valspec L3 bar (max |step| <= 0.5) presumes
    # 60 CONSECUTIVE rAF frames; the 900ms wall-poll straddles 1-3 rAF
    # ticks at SwiftShader speed (multi-tick flicker gap up to ~0.76,
    # aliasing FAILs like diffMax=0.508 in full6). FLICKER_ARM records at
    # rAF cadence (forced render per cb = the render is the rAF cost);
    # steps over consecutive FRAME samples are the valspec's measure.
    armed = page.evaluate(FLICKER_ARM)
    fl_deadline = time.time() + 150
    while time.time() < fl_deadline:
        samples = page.evaluate("(window.__r2fl||[])")
        if armed != 'no-lantern' and len(samples) >= 60:
            break
        page.wait_for_timeout(900)
    samples = page.evaluate("(window.__r2fl||[])")
    stamps = page.evaluate("(window.__r2ft||[])")
    ok_l = len(samples) >= 8
    ok_band = ok_l and all(base * 0.95 <= s <= base * 1.05 for s in samples)
    ok_distinct = ok_l and len(set(round(s, 3) for s in samples)) >= 2
    diffs = [abs(samples[i + 1] - samples[i])
             for i in range(len(samples) - 1)] if ok_l else [0]
    # C15 (IO ruling 2026-10-02, R5): the wobble is WALL-clock
    # (performance.now in lanternTick) but the 0.5 step bar assumed
    # 60fps rAF (1s window). At SwiftShader ~3fps a frame is ~330ms
    # wall and the max |dw/dt| = 1.83/s -> up to 0.60 PER FRAME.
    # Normalized bar: step <= 1.9 intensity/s * gap_s (the analytic
    # max rate + margin), per consecutive sample pair. The 0.5 absolute
    # bar would fail a correctly-functioning lantern at low fps.
    gaps_ok = True
    if ok_l and len(stamps) == len(samples):
        for i in range(len(diffs)):
            gap_s = max(0.001, (stamps[i + 1] - stamps[i]) / 1000.0)
            if diffs[i] > 1.9 * gap_s:
                gaps_ok = False
    ok_diff = ok_l and gaps_ok
    flat = ok_l and (max(samples) - min(samples) < 1e-9)  # (RECORD)
    # follow: teleport +15/+15, lantern world pos delta == player delta
    p1 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
    wp1 = (scan.get("lantern") or {}).get("wpv") or {}
    page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)"
                  % (p1["x"] + 15, p1["z"] + 15))
    page.evaluate("window.WH_GAME.renderer.render(window.WH_GAME.scene,"
                  "window.WH_GAME.camera)")
    page.wait_for_timeout(300)
    scan2 = page.evaluate(JS_LIGHT_SCAN)
    p2 = page.evaluate("window.WH_DEBUG.getPlayerPosition()")
    wp2 = (scan2.get("lantern") or {}).get("wpv") or {}
    ok_follow = (abs((wp2.get("x", 0) - wp1.get("x", 0))
                     - (p2["x"] - p1["x"])) <= 0.01
                 and abs((wp2.get("z", 0) - wp1.get("z", 0))
                         - (p2["z"] - p1["z"])) <= 0.01)
    ok = (ok_e and ok_c and ok_chain and ok_d and only1
          and ok_l and ok_band and ok_distinct and ok_diff and ok_follow)
    check("L3", "player lantern", ok,
          "e=%s c=%s chain=%s dOK=%s only1=%s n=%d band=%s "
          "stepNorm(C15)=%s diffMax=%.3f flat=%s follow=%s"
          % (ok_e, ok_c, ok_chain, ok_d, only1, len(samples), ok_band,
             gaps_ok, max(diffs) if diffs else 0, flat, ok_follow))


# ----------------------------------------------------------------- AC L4 -----
def ac_l4(page):
    """L4: Neutral tonemap + exposure plumbing + sky-vs-ground pixel bars
    (single forced render+snapshot in ONE evaluate)."""
    r = page.evaluate("""(function(){
      var G=window.WH_GAME;
      return {toneMapping:G.renderer.toneMapping,
              neutral:(typeof THREE.NeutralToneMapping==='number')?
                      THREE.NeutralToneMapping:null,
              name:window.WH_CONFIG.renderer.toneMappingName,
              expo:G.renderer.toneMappingExposure,
              cfgExpo:window.WH_CONFIG.renderer.toneMappingExposure};})()""")
    ok_tm = (r.get("neutral") is not None
             and r.get("toneMapping") == r.get("neutral"))
    ok_name = r.get("name") == "Neutral"
    ok_expo = (r.get("expo") is not None) and (
        abs(r.get("expo") - (r.get("cfgExpo") or 0)) < 1e-9)
    snap = page.evaluate(
        "(function(){var g=window.WH_GAME;"
        "g.renderer.render(g.scene,g.camera);"
        "return g.renderer.domElement.toDataURL('image/png');})()")
    w, h, px, bpp = decode_png(snap)
    sky = mean_luma(px, w, h, bpp, 0.40 * w, 0.02 * h, 0.60 * w, 0.18 * h)
    gnd = mean_luma(px, w, h, bpp, 0.30 * w, 0.72 * h, 0.70 * w, 0.95 * h)
    ok_pix = sky["mean"] >= gnd["mean"] and sky["mean"] > 0
    ok = ok_tm and ok_name and ok_expo and ok_pix
    check("L4", "tonemap+exposure+skyfloor", ok,
          "tm=%s name=%s expo=%s vs cfg=%s sky=%.2f gnd=%.2f"
          % (ok_tm, ok_name, r.get("expo"), r.get("cfgExpo"),
             sky["mean"], gnd["mean"]))
