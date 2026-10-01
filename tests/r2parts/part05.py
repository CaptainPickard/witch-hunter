# --------------------------------------------------- AC L1 + L2 (R2 rig Id) --
# R1-validated prewarm entry (valspec L1): teleport to boundary z=-25 minus 22
# => z=-47 is 22 INSIDE region B, so teleport to z=-3 (22 short of boundary)
# then walk -z across. Correct valspec wording: "teleport to regionA boundary
# z (-25) + 22 inside CFG.preWarm distance" = z=-47? No: +22 from -25 toward A
# = -3. Use z=-3 (A side, within preWarm 30), hold W, cross at -25.
CROSS_JS = ("(function(){var r=window.WH_DEBUG.getRegionManager();"
            "return r.logic.activeId;})()")


def organic_cross(page, timeout=40.0, start_z=-3.0):
    """Transition crossing via sanctioned teleportPlayer STEPS across the
    boundary plane. The transition code path (tickTransition -> mapPosition-
    Across -> applyRegionLighting) runs 100% real; only the locomotion is
    stepped, because SwiftShader's ~1-3fps x maxDt(0.05) makes an organic
    22-unit walk a multi-minute gamble that also churns enemy aggro. IO-
    documented deviation (report section: crossing method)."""
    before = page.evaluate(CROSS_JS)
    crossed_to = None
    for z in (-5, -8, -12, -16, -21, -24, -27):
        page.evaluate("window.WH_DEBUG.teleportPlayer(-2,%d)" % z)
        page.wait_for_timeout(400)
        now = page.evaluate(CROSS_JS)
        if now != before:
            crossed_to = now
            break
    if crossed_to is None:
        return {"crossed": False, "method": "stepped-stuck",
                "activeId": before}
    return {"crossed": True, "method": "stepped-teleport",
            "activeId": crossed_to}


def ac_l1(page, scan_a, scan_b, cross):
    """L1 (valspec verbatim bars): AmbientLight count==0 in BOTH regions
    (scene + boot probe); exactly 1 HemisphereLight, colors match CONFIG
    (0x4a5a80 / 0x16181e); hemi.intensity == 1.35 (A) and == 0.7425 (B,
    tol ±0.03); CFG.lighting.ambientIntensity === 0; moon intensity identical
    across regions (region-independent 0.45)."""
    a, b = scan_a or {}, scan_b or {}
    boot = page.evaluate("window.__R2_BOOT_PROBE || {}") or {}
    ok_amb = (a.get("ambient") == 0 and b.get("ambient") == 0
              and boot.get("ambient") == 0)
    ok_hemi_n = (a.get("hemi") == 1 and b.get("hemi") == 1)
    hd = a.get("hemiDetail") or {}
    ok_hemi_c = (hd.get("c") == 0x4a5a80 and hd.get("gc") == 0x16181e)
    ok_a_i = abs((a.get("hemiDetail") or {}).get("i", -9) - 1.35) <= 0.03
    ok_b_i = abs((b.get("hemiDetail") or {}).get("i", -9) - 0.7425) <= 0.03
    amb_cfg = page.evaluate(
        "window.WH_CONFIG.lighting.ambientIntensity")
    ok_cfg0 = amb_cfg == 0
    moon_a = a.get("moonI")
    moon_b = b.get("moonI")
    ok_moon = (moon_a is not None and moon_b is not None
               and abs(moon_a - moon_b) < 1e-6)
    crossed_ok = bool(cross.get("crossed"))
    ok = (ok_amb and ok_hemi_n and ok_hemi_c and ok_a_i and ok_b_i
          and ok_cfg0 and ok_moon and crossed_ok)
    check("L1", "ambient0+hemiScale", ok,
          "ambA=%d ambB=%d boot=%s | hemiN=%d/%d c=%s gc=%s | "
          "IA=%.4f IB=%.4f want 1.35/0.7425 | cfgAmb=%s | "
          "moonI A=%s B=%s | cross=%s(%s)->%s"
          % (a.get("ambient"), b.get("ambient"), boot.get("ambient"),
             a.get("hemi"), b.get("hemi"), hex(hd.get("c") or 0),
             hex(hd.get("gc") or 0),
             (a.get("hemiDetail") or {}).get("i", -9),
             (b.get("hemiDetail") or {}).get("i", -9), amb_cfg,
             moon_a, moon_b, crossed_ok, cross.get("method"),
             cross.get("activeId")))
    return ok


def ac_l2(page, scan_a):
    """L2 position bars (valspec verbatim, PASS basis): exactly 1 dir light;
    color == CFG.moonColor; world z<0; elevation deg within 25-35; |x|/len
    <= 0.08; target scene-fixed at origin. Backlight probe is separate."""
    a = scan_a or {}
    moon = a.get("moonL") or {}
    ok_n = a.get("dir", 0) == 1
    ok_c = moon.get("c") == 0xa8bce6
    pos = moon.get("pos") or {}
    ln = math.sqrt(pos.get("x", 0) ** 2 + pos.get("y", 0) ** 2
                   + pos.get("z", 0) ** 2)
    ok_z = ln > 0 and pos.get("z", 0) < 0
    elev = math.degrees(math.asin(abs(pos.get("y", 0)) / ln)) if ln > 0 else 0
    azx = abs(pos.get("x", 0)) / ln if ln > 0 else 1
    ok_elev = 25.0 <= elev <= 35.0
    ok_az = azx <= 0.08
    tgt = moon.get("tgt") or {}
    ok_tgt = (tgt.get("x") == 0 and tgt.get("y") == 0 and tgt.get("z") == 0)
    ok = ok_n and ok_c and ok_z and ok_elev and ok_az and ok_tgt
    check("L2", "moon direction", ok,
          "dirCount=%d c=%s z=%.2f<0 elev=%.1f(25-35) |x|/len=%.3f "
          "tgt=(%s,%s,%s) [backlight probe: separate RECORD]"
          % (a.get("dir"), hex(moon.get("c") or 0), pos.get("z", 0),
             elev, azx, tgt.get("x"), tgt.get("y"), tgt.get("z")))
    return ok