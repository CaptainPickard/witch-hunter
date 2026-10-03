

# ------------------------------------------------ in-page probes (JS) -------
STATE_JS = """(function(){var D=window.WH_DEBUG, p=D.getPlayer(), G=window.WH_GAME,
  c=G.camera.position; return {x:p.pos.x, y:p.pos.y, z:p.pos.z,
  active:D.activeRegionId, cx:c.x, cy:c.y, cz:c.z, camDist:p.camDist,
  pitch:p.camPitch*180/Math.PI, yaw:p.camYaw*180/Math.PI, state:p.state,
  locked:!!p.lockTarget};})()"""

CFG_JS = """(function(){var C=window.WH_CONFIG, D=window.WH_DEBUG, regs={};
  [C.regionA, C.regionB].forEach(function(r){ regs[r.id]=r.props.map(
    function(p,i){ var m=D.getAssetMeta(p.asset); return {i:i, name:p.asset,
      x:p.x, z:p.z, s:p.scale, w:m?m.width:null}; }); });
  return {props:regs, A:C.regionA.id, B:C.regionB.id,
    spawn:{A:C.regionA.spawn, B:C.regionB.spawn},
    enemies:{A:C.regionA.enemies, B:C.regionB.enemies},
    fog:{A:C.regionA.fogDensity, B:C.regionB.fogDensity},
    world:C.world, chokepoint:C.chokepoint, boundary:C.boundary,
    hold:C.enemy.holdAtBoundaryMargin, player:C.player};})()"""

RENDER_JS = """(function(){var G=window.WH_GAME;
  G.renderer.render(G.scene,G.camera);
  var c=G.renderer.domElement;
  return {url:c.toDataURL('image/png'), w:c.width, h:c.height};})()"""

GROUND_JS = """(function(){var rm=window.WH_DEBUG.getRegionManager(), out={};
  Object.keys(rm.groups||{}).forEach(function(id){ var g=rm.groups[id];
    g.children.forEach(function(ch){
      if(ch.name==='ground' && ch.geometry && ch.geometry.parameters){
        out[id]={R:ch.geometry.parameters.radius,
                 rep:ch.material.map?ch.material.map.repeat.x:null,
                 repY:ch.material.map?ch.material.map.repeat.y:null}; }
      if(ch.name==='mist-plane' && ch.geometry && ch.geometry.parameters){
        (out[id]=out[id]||{}).mist=ch.geometry.parameters.width; } }); });
  return out;})()"""


def st(page):
    return page.evaluate(STATE_JS)


def poll(page, frames=2):
    """One poll = 2 real rAF frames then a state read (law 1)."""
    wait_frames(page, frames)
    return st(page)


def teleport(page, x, z):
    page.evaluate("window.WH_DEBUG.teleportPlayer(%f,%f)" % (x, z))


def set_yaw(page, deg):
    page.evaluate("window.WH_DEBUG.setCameraYaw(%f)" % deg)


def nan(*vals):
    return any(v is None or v != v for v in vals)


def rr(s):
    return math.hypot(s["x"], s["z"])


def enter_b(page):
    """R2 L1 stepped teleport at x=-2 (R2 organic_cross verbatim steps);
    asserts activeId == regionB.id. Returns (ok, trace)."""
    cfg = page.evaluate("({A:window.WH_CONFIG.regionA.id,"
                        "B:window.WH_CONFIG.regionB.id})")
    trace = []
    for z in (-5, -8, -12, -16, -21, -24, -27):
        teleport(page, -2, z)
        page.wait_for_timeout(400)
        s = st(page)
        trace.append((z, s["active"]))
        if s["active"] == cfg["B"]:
            page.wait_for_timeout(1500)
            return True, trace
    return False, trace


def settle_cam(page, wall=40.0):
    """Law 3: |dcam| < 0.01 over 2 consecutive polls. Returns (state,
    settled, min camera y seen)."""
    last, calm, miny = None, 0, 1e9
    deadline = time.time() + wall
    s = None
    while time.time() < deadline:
        s = poll(page)
        miny = min(miny, s["cy"])
        if last is not None:
            d = math.sqrt((s["cx"] - last["cx"]) ** 2 + (s["cy"] - last["cy"])
                          ** 2 + (s["cz"] - last["cz"]) ** 2)
            calm = calm + 1 if d < 0.01 else 0
            if calm >= 2:
                return s, True, miny
        last = s
    return s, False, miny


def hold_w(page, yaw_deg, wall, stop, on_sample=None):
    """Real 'w' keydown with setCameraYaw(yaw) (W = (sin(yaw+PI),
    cos(yaw+PI)), player.js:753). Polls until stop(samples) or wall.
    Returns samples."""
    samples = []
    set_yaw(page, yaw_deg)
    page.keyboard.down("w")
    try:
        deadline = time.time() + wall
        while time.time() < deadline:
            s = poll(page)
            samples.append(s)
            if on_sample:
                on_sample(s)
            if stop(samples):
                break
            set_yaw(page, yaw_deg)
    finally:
        try:
            page.keyboard.up("w")
        except Exception:
            pass
    return samples


def stationary_r(samples, n=3, eps=0.01):
    """|dr| < eps over n consecutive polls."""
    if len(samples) < n + 1:
        return False
    rs = [rr(s) for s in samples[-(n + 1):]]
    return all(abs(rs[i + 1] - rs[i]) < eps for i in range(n))


def stationary_xy(samples, n=3, eps=0.01):
    if len(samples) < n + 1:
        return False
    tail = samples[-(n + 1):]
    return all(math.hypot(tail[i + 1]["x"] - tail[i]["x"],
                          tail[i + 1]["z"] - tail[i]["z"]) < eps
               for i in range(n))


# ------------------------------------------- independent recompute (R5-2/4) --
CORRIDOR = (-4.0, 4.0, -31.0, -19.0)   # valspec E set: x in [-4,4], z in [-31,-19]


def meets_corridor(x, z, r):
    x0, x1, z0, z1 = CORRIDOR
    nx, nz = min(max(x, x0), x1), min(max(z, z0), z1)
    return math.hypot(x - nx, z - nz) <= r


# C14 (IO ruling): trunk-class vegetation uses radius * TRUNK_RATIO; the
# harness mirrors the game's exact classification so its independent
# recompute checks the SAME law (the spawn/edge checks stay independent).
TRUNK_RATIO = 0.25
_TRUNK_SET = {"livingOak", "witchwoodTree", "birchTree", "deadTree",
              "deadTree2", "ancientOak", "hangingTree", "twistedSapling",
              "thornbush", "bramble", "largeFern", "deadShrub",
              "mossyStump", "hollowStump"}


def _trunk_r(name, w, s):
    r = (w or 0) * s / 2.0
    if name in _TRUNK_SET or re.search(
            r"tree|oak|birch|sapling|bush|bramble|fern|shrub|stump", name, re.I):
        return r * TRUNK_RATIO
    return r


def collider_table(cfg):
    """C14 radii: (width*scale/2) * TRUNK_RATIO for trunk-class vegetation,
    full footprint otherwise (valspec R5-4 + C14 ruling) per region;
    E = circles meeting the corridor rectangle (exempt, RECORD)."""
    out = {}
    for key in ("A", "B"):
        rid = cfg[key]
        circ, ex = [], []
        for p in cfg["props"][rid]:
            R = _trunk_r(p["name"], p["w"], p["s"])
            row = {"region": key, "i": p["i"], "name": p["name"],
                   "x": p["x"], "z": p["z"], "R": round(R, 4),
                   "meta": p["w"] is not None}
            (ex if meets_corridor(p["x"], p["z"], R) else circ).append(row)
        out[key] = {"circles": circ, "exempt": ex}
    return out


def inside_any(table_region, x, z, pad=PLAYER_R):
    return [c for c in table_region["circles"]
            if math.hypot(x - c["x"], z - c["z"]) < c["R"] + pad]


def recompute_validator(cfg, table, r_play):
    """Harness-side (i)-(iii) from WH_CONFIG + getAssetMeta."""
    viol = []
    plane, hold = cfg["boundary"]["z"], cfg["hold"]
    for key, side in (("A", 1), ("B", -1)):
        for p in cfg["props"][cfg[key]]:
            if (side == 1 and not p["z"] > plane) or (side == -1 and
                                                      not p["z"] < plane):
                viol.append(("prop", key, p["i"], p["name"], "side"))
            if math.hypot(p["x"], p["z"]) > r_play:
                viol.append(("prop", key, p["i"], p["name"], "radius"))
        for i, e in enumerate(cfg["enemies"][key]):
            if (side == 1 and not e["z"] >= plane + hold) or (
                    side == -1 and not e["z"] <= plane - hold):
                viol.append(("enemy", key, i, e["type"], "side"))
            if math.hypot(e["x"], e["z"]) > r_play:
                viol.append(("enemy", key, i, e["type"], "radius"))
        sp = cfg["spawn"][key]
        for c in table[key]["circles"]:
            if math.hypot(sp["x"] - c["x"], sp["z"] - c["z"]) < c["R"] + PLAYER_R:
                viol.append(("spawn", key, c["i"], c["name"],
                             "R=%.3f d=%.3f" % (c["R"], math.hypot(
                                 sp["x"] - c["x"], sp["z"] - c["z"]))))
    return viol


# ------------------------------------------------------------ seam metric ---
def luma_rows(img, cols, rows):
    """Per-row mean luma over the column strips (Rec.709 weights)."""
    px = img.load()
    out = []
    for y in range(rows[0], rows[1]):
        s = n = 0
        for c0, c1 in cols:
            for x in range(c0, c1):
                p = px[x, y]
                s += 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
                n += 1
        out.append(s / max(1, n))
    return out


def seam_S(img):
    """S = max_y |L(y+2) - L(y)| over strips [0.10w,0.30w] U [0.70w,0.90w],
    rows [0.05h,0.70h] (player body excluded by the column choice)."""
    w, h = img.size
    cols = [(int(0.10 * w), int(0.30 * w)), (int(0.70 * w), int(0.90 * w))]
    L = luma_rows(img, cols, (int(0.05 * h), int(0.70 * h)))
    return round(max(abs(L[i + 2] - L[i]) for i in range(len(L) - 2)), 3)


def render_S(page, tag):
    """Settled (law 3) one-evaluate forced render + readback -> S."""
    s, settled, _ = settle_cam(page)
    for _ in range(3):
        r = page.evaluate(RENDER_JS)
        img = decode_image(r["url"])
        if not is_degenerate(img):
            try:
                os.makedirs(ART_DIR, exist_ok=True)
                img.save(os.path.join(ART_DIR, "r5-seam-%s.png" % tag))
            except Exception:
                pass
            return {"S": seam_S(img), "buf": "%dx%d" % img.size,
                    "settled": settled}
        wait_frames(page, 2)
    raise InfraError("degenerate frame (%s)" % tag)
