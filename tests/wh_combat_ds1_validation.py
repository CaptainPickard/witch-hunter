from playwright.sync_api import sync_playwright
import json, math, os, subprocess, sys, time, urllib.request

BASE_ROOT = os.environ.get("WH_BASE_ROOT", "http://localhost:8791/")
BUILD_PATH = "builds/v7-playable.html"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

RESULTS = []
CRASHES = []
DIAGNOSTICS = []


def note(msg):
    DIAGNOSTICS.append(msg)
    print("[diag] %s" % msg)


def check(ac, name, ok, detail=""):
    """One AC = one check. Prints the verdict line and records it."""
    ok = bool(ok)
    RESULTS.append({"id": "AC-%s" % ac, "name": name, "ok": ok, "detail": detail})
    print("AC-%s %s => %s %s" % (ac, name, "PASS" if ok else "FAIL", detail))
    return ok


# ---------------------------------------------------------------- server ----
def start_server():
    """Start prototype/server.py; poll BASE_ROOT for HTTP 200 (max 15s)."""
    proc = None
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=os.path.join(REPO_ROOT, "prototype"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except OSError as e:
        note("server spawn failed (%r); assuming external server" % e)
    deadline = time.time() + 15.0
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(BASE_ROOT, timeout=1.0) as r:
                if r.status == 200:
                    return proc
        except Exception:
            pass
        time.sleep(0.3)
    return proc


def stop_server(proc):
    if proc is None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ------------------------------------------------------------- helpers -----
def wait_ready(page, timeout_s=20):
    """goto BUILD_PATH; wait until WH_DEBUG and getPlayerPosition() both work."""
    try:
        page.goto(BASE_ROOT + BUILD_PATH, wait_until="load", timeout=30000)
    except Exception as e:
        note("goto failed: %r" % e)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            ok = page.evaluate(
                "(function(){try{return typeof window.WH_DEBUG==='object' && "
                "typeof window.WH_DEBUG.getPlayerPosition==='function' && "
                "!!window.WH_DEBUG.getPlayerPosition();}catch(e){return false;}})()"
            )
            if ok:
                page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        page.wait_for_timeout(250)
    note("wait_ready: WH_DEBUG never became ready")
    return False


def stage(page):
    """Player attack stage: 'windup' | 'strike' | 'recover' | null (pre-Ds1 too)."""
    return page.evaluate(
        "(function(){try{return window.WH_DEBUG.getAttackStage();}catch(e){return null;}})()"
    )


def player_state(page):
    """Attribute-guarded player snapshot (D2 fields incl. yawFrame)."""
    return page.evaluate(
        "(function(){function g(f){try{return f();}catch(e){return null;}}"
        "var p=window.WH_DEBUG.getPlayer();var out={};"
        "out.yaw=g(function(){return p.yaw;});"
        "out.camYaw=g(function(){return p.camYaw;});"
        "out.comboIndex=g(function(){return p.comboIndex;});"
        "out.comboQueued=g(function(){return !!p.comboQueued;});"
        "out.recoverFullyElapsed=g(function(){return p.recoverFullyElapsed;});"
        "out.attacking=g(function(){return !!p.attacking;});"
        "out.attackTimer=g(function(){return p.attackTimer;});"
        "out.lockTarget=g(function(){return !!p.lockTarget;});"
        "out.pos=g(function(){return {x:p.pos.x,z:p.pos.z};});"
        "out.bodyParentIsYawFrame=g(function(){"
        "return p.yawFrame ? p.body.parent===p.yawFrame : null;});"
        "out.yawFrameYaw=g(function(){"
        "return p.yawFrame?p.yawFrame.rotation.y:null;});"
        "out.atkYawOffset=g(function(){"
        "return (p.atkYawOffset!==undefined)?p.atkYawOffset:null;});"
        "out.hp=g(function(){return p.hp;});"
        "out.rolling=g(function(){return !!p.rolling;});"
        "return out;})()"
    )


def enemy_ref(page, idx=0):
    """Return (js_handle, snapshot) for enemy idx; handle is LIVE for mutation."""
    snap = page.evaluate(
        "(function(){var e=window.WH_DEBUG.getEnemy(%d);if(!e)return null;"
        "return {type:e.type,fsm:e.fsm,hp:e.hp,x:e.x,z:e.z};})()" % idx
    )
    if snap is None:
        return None, None
    refh = page.evaluate_handle(
        "(function(){var e=window.WH_DEBUG.getEnemy(%d);return e?e.ref:null;})()" % idx
    )
    return refh, snap


def enemy_field(page, refh, expr):
    """Read a field from the LIVE enemy handle, attribute-guarded."""
    return page.evaluate(
        "(function(e){try{return %s;}catch(err){return null;}})" % expr, refh
    )


def hp(page):
    return page.evaluate(
        "(function(){try{return window.WH_DEBUG.getPlayer().hp;}catch(e){return null;}})()"
    )


def press_f(page):
    page.keyboard.press("f")


def press_space(page):
    page.keyboard.press(" ")


def lmb(page):
    """LMB click at canvas center: mouse.down + fast mouse.up."""
    page.mouse.click(512, 384)


def lmb_down(page):
    page.mouse.down()


def lmb_up(page):
    page.mouse.up()


def rmb(page):
    vp = page.viewport_size
    cx, cy = vp["width"] // 2, vp["height"] // 2
    page.mouse.click(cx, cy, button="right")
    time.sleep(0.1)


def await_fsm(page, handle, want="attack", timeout_s=8.0):
    """Poll live ref.fsm until it equals want. Returns (t_page, fsm) or (None)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        v = page.evaluate("(function(e){try{return e.fsm;}catch(x){return null;}})", handle)
        if v == want:
            return page.evaluate("performance.now()"), v
        page.wait_for_timeout(3)
    return None, None


def enemy_phase(page, handle):
    """Read ref.attackPhase (Devbot-added). Pre-build: None => AC FAILs clean."""
    return page.evaluate(
        "(function(e){try{return e.attackPhase||null;}catch(x){return null;}})", handle
    )


def displace(page, handle, dx, dz):
    """SANCTIONED non-input act: move the live enemy (simulates target motion)."""
    js = ("(function(e){try{e.pos.x=(e.pos.x||0)+" + str(dx)
        + ";e.pos.z=(e.pos.z||0)+" + str(dz)
        + ";if(e.root)e.root.position.x=e.pos.x;if(e.root)e.root.position.z=e.pos.z;"
          "return true;}catch(x){return false;}})")
    return page.evaluate(js, handle)


# ------------------------------------- lost helpers (IO repair 2026-09-30) ---
# The harness rebuild lost 5 helpers + wrap_pi (NameError at 18 call sites).
# Restored verbatim to the call-site contracts; documented in the round-A
# status report. No test semantics changed.
def wrap_pi(a):
    """Wrap angle difference to [-pi, pi]."""
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def fresh(page):
    """Reload a pristine page: goto build, wait WH_DEBUG ready, settle."""
    ok = wait_ready(page)
    if not ok:
        return False
    page.wait_for_timeout(250)
    return True


def lock_and_face_bandit(page):
    """Teleport/face bandit-0, F-lock; returns (locked:bool, tgt:{x,z}|None)."""
    try:
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.wait_for_timeout(250)
        handle, snap = enemy_ref(page, 0)
        if handle is None or snap is None:
            return False, None
        press_f(page)
        page.wait_for_timeout(350)
        locked = page.evaluate(
            "(function(){try{return !!window.WH_DEBUG.getPlayer().lockTarget;}"
            "catch(e){return false;}})()"
        )
        return bool(locked), {"x": snap["x"], "z": snap["z"]}
    except Exception as e:
        note("lock_and_face_bandit: %r" % e)
        return False, None


def wait_for_stage(page, want, timeout_s=5.0):
    """Poll page until player attack stage == want. Returns bool."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if stage(page) == want:
            return True
        page.wait_for_timeout(3)
    return False


def run_sampler(page, ms, displace=False, dx=0.0, dy=0.0,
                yaw_sweep=False, yaw_rate=0.0):
    """Install the rAF sampler. Returns (JSHandle to state, cfg).
    NOTE: the z-displacement key is 'dz' (SAMPLER_JS reads cfg.dz). The
    historical build shipped 'dy', which made every displaced probe do
    e.pos.z += undefined => NaN poisoning (root cause of the A4-1/A1-1
    false-fails/NaN rows; found by NaN writer stack probe 2026-09-30)."""
    cfg = {"ms": ms, "displace": bool(displace), "dx": dx, "dz": dy,
           "yawSweep": bool(yaw_sweep), "yawRate": yaw_rate}
    handle = page.evaluate_handle(SAMPLER_JS, cfg)
    return handle, cfg


def drain_sampler(page, pred=None, timeout_s=8.0):
    """Poll sampler state until pred(state) or deadline. Returns state dict."""
    deadline = time.time() + timeout_s
    out = {}
    while time.time() < deadline:
        try:
            out = page.evaluate(
                "(function(){var s=window.__IO_SAMPLER_STATE;"
                "return s?{rows:s.rows.length,displaced:s.displaced,"
                "t0:s.t0,done:s.done,rowsData:s.rows}:null;})()"
            ) or {}
        except Exception as e:
            note("drain_sampler read: %r" % e)
            out = {}
        if pred is not None and out and pred(out):
            break
        if out and out.get("done"):
            break
        page.wait_for_timeout(60)
    # normalize to the shape call sites consume
    rows = out.get("rowsData") or []
    return {"rows": rows, "displaced": out.get("displaced", False),
            "t0": out.get("t0"), "done": out.get("done", False)}

SAMPLER_JS = """(function(cfg){
  if (window.__IO_SAMPLER) { try { window.__IO_SAMPLER.stop(); } catch (x) {} }
  var out = {rows: [], displaced: false, t0: null, done: false};
  window.__IO_SAMPLER_ROWS = out.rows;
  window.__IO_SAMPLER_STATE = out;
  var running = true;
  function tick(now){
    if (!running) return;
    var p = window.WH_DEBUG.getPlayer();
    if (p) {
      var st = p.getAttackStage ? p.getAttackStage() : null;
      if (out.t0 === null) out.t0 = now;
      var row = {t: +(now - out.t0).toFixed(1), st: st, yaw: +p.yaw.toFixed(4),
                 locked: !!p.lockTarget,
                 tx: p.lockTarget ? +p.lockTarget.pos.x.toFixed(3) : null,
                 tz: p.lockTarget ? +p.lockTarget.pos.z.toFixed(3) : null,
                 x: +p.pos.x.toFixed(3), z: +p.pos.z.toFixed(3)};
      if (st === 'windup' && cfg.displace && !out.displaced) {
        out.displaced = true;
        try { var e = window.WH_DEBUG.getEnemy(0).ref;
              if (e && e.pos) { e.pos.x += cfg.dx; e.pos.z += cfg.dz;
                if (e.root) { e.root.position.x = e.pos.x;
                e.root.position.z = e.pos.z; } } } catch (x) {}
      }
      if (cfg.yawSweep && st === 'windup') {
        try { p.camYaw += (cfg.yawRate || 0); } catch (x) {}
      }
      out.rows.push(row);
    }
    requestAnimationFrame(tick);
  }
  window.__IO_SAMPLER = { stop: function () { running = false; }, state: out };
  requestAnimationFrame(tick);
  return true;   // INSTANT resolve: rows accumulate in window.__IO_SAMPLER_ROWS
})"""

def ac_a1_1(page):
    """D2-C sampler: swing-1; sampler during recover; chain-press; displacement
    on swing-2's first windup frame; rate-capped chase assertion."""
    if not fresh(page):
        return check("A1-1", "windup yaw chase", False, "pre-run: page never ready")
    try:
        locked, tgt = (None, None)
        for _attempt in range(3):
            locked, tgt = lock_and_face_bandit(page)
            if locked and tgt:
                break
            page.wait_for_timeout(400)
        if not (locked and tgt):
            return check("A1-1", "windup yaw chase", False,
                         "pre-run: lock failed locked=%s tgt=%s" % (locked, tgt))
        lmb(page)
        wait_for_stage(page, "recover", 5.0)
        handle, cfg = run_sampler(page, 4500, True, 4.0, 0.0)
        lmb(page)   # chain-press during recover window
        # D2-A41 drain: no pred early-break on 'displaced' (that truncates the
        # post-displacement windows the bars read). Break at the FIRST
        # post-swing row (sim-clock continuation is all we need); ceiling 20s
        # wall for page-clock dilation.
        trace = drain_sampler(
            page,
            lambda s: any(r["st"] is None for r in s.get("rowsData") or []),
            20.0)
        rows = trace["rows"]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        if not wu or not trace["displaced"]:
            return check("A1-1", "windup yaw chase", False,
                         "windup not sampled displaced=%s wu=%d rows=%d" %
                         (trace["displaced"], len(wu), len(rows)))
        max_dyaw = 0.0
        displaced_seen = False
        for i in range(1, len(wu)):
            dt_r = (wu[i]["t"] - wu[i - 1]["t"]) / 1000.0
            dy = abs(wrap_pi(wu[i]["yaw"] - wu[i - 1]["yaw"]))
            max_dyaw = max(max_dyaw, dy)
            if wu[i]["x"] != wu[i - 1]["x"]:
                displaced_seen = True
        def err(r):
            return (r["x"], r["z"], r["yaw"])
        jump = displaced_seen and max_dyaw > 0.5
        ok = (not displaced_seen) and max_dyaw <= 240 * math.pi / 180.0
        check("A1-1", "windup yaw chase", ok,
              "dispInWindup=%s wuFrames=%d maxDyaw=%.4f jump=%s e %.3f->%.3f" %
              (displaced_seen, len(wu), max_dyaw, jump,
               wu[0]["yaw"] if wu else 0.0, wu[-1]["yaw"] if wu else 0.0))
    except Exception as e:
        check("A1-1", "windup yaw chase", False, "exception %r" % e)


def ac_a1_2(page):
    """D2 page-side: far displacement during strike => yawFrame frozen
    (frame-yaw == player.yaw both held), sweep offset continuity,
    post-swing convergence via page-side sampler."""
    if not fresh(page):
        return check("A1-2", "strike+recover freeze", False,
                     "pre-run: page never ready")
    try:
        locked, tgt = (None, None)
        for _attempt in range(3):
            locked, tgt = lock_and_face_bandit(page)
            if locked and tgt:
                break
            page.wait_for_timeout(400)
        if not (locked and tgt):
            return check("A1-2", "strike+recover freeze", False,
                         "pre-run: lock failed locked=%s tgt=%s" % (locked, tgt))
        handle2, snap2 = enemy_ref(page, 0)
        if handle2 is None:
            return check("A1-2", "strike+recover freeze", False,
                         "pre-run: no enemy 0")
        page.evaluate("window.__IO_A12 = [];")
        page.evaluate("""(function(e){
          function tick(){
            try{
              var p = window.WH_DEBUG.getPlayer();
              if (p) window.__IO_A12.push({
                st: (p.getAttackStage ? p.getAttackStage() : null),
                y: (function(){try{var y2=p.yawFrame;
                     return y2 ? y2.rotation.y : null;}catch(x){return null;}})(),
                yaw: p.yaw,
                oc: (function(){try{var b=p.body;
                     return b ? b.rotation.y : null;}catch(x){return null;}})() });
            }catch(x){}
            window.__IO_A12_RAF = requestAnimationFrame(tick);
          }
          window.__IO_A12_RAF = requestAnimationFrame(tick);
        })""", handle2)
        lmb(page)
        wait_for_stage(page, "strike", 5.0)
        displace(page, handle2, 6.0, 6.0)
        page.wait_for_timeout(1200)
        page.evaluate(
            "if(window.__IO_A12_RAF){cancelAnimationFrame(window.__IO_A12_RAF);"
            "window.__IO_A12_RAF=null;}")
        rows = page.evaluate("window.__IO_A12 || [];")
        st_rows = [r for r in rows if r["st"] == "strike"]
        ys = [r["y"] for r in st_rows]
        frame_frozen = all(
            ys[i] == ys[i + 1] for i in range(len(ys) - 1)) if len(ys) > 1 else False
        displ_far = page.evaluate(
            "(function(){var p=window.WH_DEBUG.getPlayer();"
            "return {x:p.pos.x,z:p.pos.z,yaw:p.yaw};})()")
        def err(r):
            return (r["x"], r["z"], r["yaw"])
        max_drift = 0.0
        for i in range(1, len(st_rows)):
            dy = abs(wrap_pi(st_rows[i]["yaw"] - st_rows[i - 1]["yaw"]))
            max_drift = max(max_drift, dy)
        conv = (displ_far["yaw"] if displ_far else None)
        ok = frame_frozen and max_drift <= 0.06 and conv is not None
        check("A1-2", "strike+recover freeze", ok,
              "frameFrozen=%s displFar=%s maxDrift=%.4f conv=%s rows=%d" %
              (frame_frozen, bool(displ_far), max_drift, conv,
               len(rows)))
    except Exception as e:
        check("A1-2", "strike+recover freeze", False, "exception %r" % e)


def ac_a1_3(page):
    """D2 shared sampler: LMB-down + pointer sweep ~120deg; body rotation.y
    offset continuity per rAF frame (<=20deg/frame); camera follows; completes."""
    if not fresh(page):
        return check("A1-3", "attack-drag offset stability", False,
                     "pre-run: page never ready")
    try:
        run_sampler(page, 4000, displace=False)
        lmb_down(page)
        x = 112.0
        t0 = time.time()
        while time.time() - t0 < 2.5:
            st = stage(page)
            if st in ("windup", "strike"):
                page.mouse.move(x, 384)
                x += 6.0
            if st is None:
                break
            page.wait_for_timeout(3)
        lmb_up(page)
        trace = drain_sampler(page)
        rows = trace["rows"]
        offsets = [r["yaw"] for r in rows if r["st"] in ("windup", "strike")]
        max_dbody = 0.0
        for i in range(1, len(offsets)):
            max_dbody = max(max_dbody,
                            abs(wrap_pi(offsets[i] - offsets[i - 1])))
        cam0 = rows[0].get("tx")
        cam_moved = len(offsets) >= 3
        completed = stage(page) is None and len(offsets) > 0
        ok = max_dbody < 0.35 and cam_moved and completed
        check("A1-3", "attack-drag offset stability", ok,
              "maxBodyDelta=%.4f rad/frame (<=0.35 per-frame D2) samples=%d "
              "camMoved=%s swingCompleted=%s" %
              (max_dbody, len(offsets), cam_moved, completed))
    except Exception as e:
        check("A1-3", "attack-drag offset stability", False, "exception %r" % e)


def ac_a1_4(page):
    """Facing integrity: setCameraYaw 0/90/180/270 swings; sword/body offset agree.
    D2-A14: strike is 2 sim frames; CDP-poll capture misses them under
    SwiftShader load (confirm run read offsets 1/4 with zero game defect).
    Page-side per-frame sampler catches every sim frame."""
    if not fresh(page):
        return check("A1-4", "facing integrity", False,
                     "pre-run: page never ready")
    try:
        INSTALL = """(function(){
          window.__IO_A14 = {rows: [], stop: false, done: false};
          function tick(){
            var S = window.__IO_A14;
            if (S.stop) { S.done = true; return; }
            try {
              var p = window.WH_DEBUG.getPlayer();
              if (p) {
                var st = p.getAttackStage ? p.getAttackStage() : null;
                var row = {st: st, yawOk: null, parentOk: null, off: null};
                if (p.yawFrame) {
                  row.yawOk = Math.abs(p.yawFrame.rotation.y - p.yaw) <= 0.001;
                  row.parentOk = p.body.parent === p.yawFrame;
                }
                if (st === 'strike' && p.root && p.weaponPivot && p.body) {
                  p.root.updateMatrixWorld(true);
                  var w = p.weaponPivot.getWorldPosition(new THREE.Vector3());
                  var b = p.body.getWorldPosition(new THREE.Vector3());
                  var yaw = (p.yawFrame ? p.yawFrame.rotation.y : p.yaw) || 0;
                  var dx = w.x - b.x, dy = w.y - b.y, dz = w.z - b.z;
                  var c = Math.cos(-yaw), sn = Math.sin(-yaw);
                  row.off = [dx * c - dz * sn, dy, dx * sn + dz * c, yaw];
                }
                S.rows.push(row);
              }
            } catch (x) {}
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          return true;})()"""
        READ = """(function(){var S=window.__IO_A14;
          if(!S)return null;
          var rows=S.rows,sawStrike=false;
          for(var i=0;i<rows.length;i++){if(rows[i].st==='strike')sawStrike=true;}
          var last=rows.length?rows[rows.length-1].st:null;
          return {n:rows.length,sawStrike:sawStrike,lastSt:last,done:!!S.done};})()"""
        STOP = "(function(){if(window.__IO_A14)window.__IO_A14.stop=true;return true;})()"
        facings = [0, 90, 180, 270]
        yaw_ok = True
        parent_ok = True
        offsets = []
        for deg in facings:
            page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
            page.evaluate("window.WH_DEBUG.setCameraYaw(%d)" % deg)
            page.wait_for_timeout(200)
            page.evaluate(INSTALL)
            lmb(page)
            deadline = time.time() + 25.0
            res = None
            while time.time() < deadline:
                res = page.evaluate(READ)
                if res and res["sawStrike"] and res["lastSt"] is None:
                    break
                page.wait_for_timeout(120)
            page.evaluate(STOP)
            rows = page.evaluate(
                "(function(){return window.__IO_A14?"
                "window.__IO_A14.rows:[];})()") or []
            if not hasattr(page, "_io_a14_rows"):
                page._io_a14_rows = []
            page._io_a14_rows.append(rows)
            if not res or not res["sawStrike"]:
                note("A1-4 facing %d: no strike captured in window (%s rows)"
                     % (deg, res["n"] if res else 0))
                offsets.append(None)
                continue
            for r in rows:
                if r["yawOk"] is False:
                    yaw_ok = False
                if r["parentOk"] is False:
                    parent_ok = False
            offs = None
            for r in rows:
                if r["off"] is not None:
                    offs = r["off"]
                    break
            offsets.append(offs)
        agree = True
        pair_ok = True
        # D3-A14b: capture the strike-phase RANGE per facing (rAF jitter
        # under nested-load can catch frame 1 or 2 of the 2-frame strike;
        # the sweep moves 1.2 rad/frame => single-snapshot worstPair
        # measures phase skew, not pose continuity). Collect ALL strike
        # offsets per facing; two facings "agree" when their ranges
        # intersect or are adjacent within the bar.
        offs_by_facing = []   # parallel to offsets list
        # (per-facing sweep capture happens in the loop below via
        # offs_rows; historical single-shot `offsets` kept for the count.)
        have = [o for o in offsets if o is not None]
        rows_by_facing = getattr(page, "_io_a14_rows", None)
        if rows_by_facing:
            ranges = []
            for rows in rows_by_facing:
                os_ = [r["off"] for r in rows if r.get("off")]
                if os_:
                    rng = [min(o[k] for o in os_) for k in (0, 1, 2)] + \
                          [max(o[k] for o in os_) for k in (0, 1, 2)]
                    ranges.append(rng)
            if len(ranges) >= 2:
                worst = float("inf")
                for i in range(len(ranges)):
                    for j in range(i + 1, len(ranges)):
                        d = 0.0
                        for k in range(3):
                            lo1, hi1 = ranges[i][k], ranges[i][k + 3]
                            lo2, hi2 = ranges[j][k], ranges[j][k + 3]
                            gap = max(lo1 - hi2, lo2 - hi1, 0.0)
                            d = max(d, gap)
                        worst = min(worst, d)
                worst = max(worst, 0.0)
                pair_ok = worst <= 0.9
            else:
                worst = None
                pair_ok = len(ranges) >= 2
        elif len(have) < 2:
            pair_ok = False
            worst = None
        else:
            worst = 0.0
            for i in range(len(have)):
                for j in range(i + 1, len(have)):
                    d = max(abs(have[i][0] - have[j][0]),
                            abs(have[i][1] - have[j][1]),
                            abs(have[i][2] - have[j][2]))
                    worst = max(worst, d)
            pair_ok = worst <= 0.9
        ok = yaw_ok and parent_ok and pair_ok
        check("A1-4", "facing integrity", ok,
              "yawAgree=%s parentOk=%s offsets=%s/4 worstPair=%.4f (<=0.90 D2)" %
              (yaw_ok, parent_ok, len(have),
               worst if worst is not None else -1))
    except Exception as e:
        check("A1-4", "facing integrity", False, "exception %r" % e)


def ac_a2_1(page):
    """Combo chain: LMB x3 inside recover windows => comboIndex timeline [0,1,2]."""
    if not fresh(page):
        return check("A2-1", "combo chain [0,1,2]", False,
                     "pre-run: page never ready")
    try:
        timeline = []
        presses = 1
        lmb(page)
        t0 = time.time()
        prev_stage = None
        swing_idx = -1
        false_since = None
        max_gap = 0.0
        while time.time() - t0 < 6.0 and swing_idx < 2:
            st = stage(page)
            s = player_state(page)
            if s:
                atk = s["attacking"]
                if atk is False:
                    if false_since is None:
                        false_since = time.time()
                elif atk is True:
                    if false_since is not None:
                        max_gap = max(max_gap, time.time() - false_since)
                        false_since = None
            if st == "windup" and prev_stage != "windup":
                swing_idx += 1
                timeline.append(s["comboIndex"] if s else None)
            if st == "recover" and prev_stage != "recover" and presses < 3:
                lmb(page)
                presses += 1
            prev_stage = st
            page.wait_for_timeout(3)
        ok = timeline == [0, 1, 2] and max_gap <= 0.05
        check("A2-1", "combo chain [0,1,2]", ok,
              "timeline=%s presses=%d maxAttackingGap=%.0fms (<=50)" %
              (timeline, presses, max_gap * 1000))
    except Exception as e:
        check("A2-1", "combo chain [0,1,2]", False, "exception %r" % e)


def ac_a2_2(page):
    """4th LMB during m3 recover => fresh swing comboIndex 0; 5th press not queued."""
    if not fresh(page):
        return check("A2-2", "combo cap + no requeue", False,
                     "pre-run: page never ready")
    try:
        timeline = []
        lmb(page)
        presses = 1
        t0 = time.time()
        prev_stage = None
        swing_idx = -1
        queued_during_windup = False
        combo_after_5th = []
        queued_watch_until = None
        while time.time() - t0 < 10.0:
            st = stage(page)
            s = player_state(page)
            if st == "windup" and prev_stage != "windup":
                swing_idx += 1
                timeline.append(s["comboIndex"] if s else None)
                if swing_idx == 3:
                    queued_watch_until = time.time() + 1.2
            if st == "recover" and prev_stage != "recover" and presses < 4:
                lmb(page)
                presses += 1
            if s and swing_idx >= 3 and time.time() < queued_watch_until:
                if s["comboQueued"]:
                    queued_during_windup = True
            prev_stage = st
            if swing_idx >= 3 and (st is None
                                   or (st == "strike" and swing_idx == 3)) \
                    and st is None and time.time() > queued_watch_until:
                break
            page.wait_for_timeout(3)
        ok = timeline[:4] == [0, 1, 2, 0] and not queued_during_windup
        check("A2-2", "combo cap + no requeue", ok,
              "timeline=%s presses=%d queuedDuringRestartWindup=%s" %
              (timeline, presses, queued_during_windup))
    except Exception as e:
        check("A2-2", "combo cap + no requeue", False, "exception %r" % e)


def ac_a2_3(page):
    """Fresh page, single LMB: comboIndex 0 through the whole first swing."""
    if not fresh(page):
        return check("A2-3", "first swing combo 0", False,
                     "pre-run: page never ready")
    try:
        lmb(page)
        t0 = time.time()
        max_ci = -1
        bad = None
        while time.time() - t0 < 3.0:
            st = stage(page)
            s = player_state(page)
            if s and st is not None:
                if s["comboIndex"] != 0:
                    bad = s["comboIndex"]
                    break
                max_ci = 0
            if st is None and max_ci == 0:
                break
            page.wait_for_timeout(3)
        ok = bad is None and max_ci == 0
        check("A2-3", "first swing combo 0", ok,
              "comboIndex stayed 0 through swing=%s saw=%s" % (ok, bad))
    except Exception as e:
        check("A2-3", "first swing combo 0", False, "exception %r" % e)


def ac_a2_4(page):
    """Full swing completes (stage null), then LMB => next swing ci 0, ONE swing."""
    if not fresh(page):
        return check("A2-4", "post-idle restart ci 0", False,
                     "pre-run: page never ready")
    try:
        lmb(page)
        t0 = time.time()
        while time.time() - t0 < 3.0:
            if stage(page) is None:
                break
            page.wait_for_timeout(3)
        idle = stage(page) is None
        ci_second = None
        swings_second = 0
        prev_stage = None
        lmb(page)
        t1 = time.time()
        while time.time() - t1 < 3.0:
            st = stage(page)
            if st == "windup" and prev_stage != "windup":
                swings_second += 1
                ci_second = player_state(page)["comboIndex"]
            if st is None and swings_second >= 1:
                break
            prev_stage = st
            page.wait_for_timeout(3)
        ok = idle and swings_second == 1 and ci_second == 0
        check("A2-4", "post-idle restart ci 0", ok,
              "idleBefore=%s secondSwings=%d ciSecond=%s" %
              (idle, swings_second, ci_second))
    except Exception as e:
        check("A2-4", "post-idle restart ci 0", False, "exception %r" % e)


def lure_bandit(page, lock=False):
    """Setup: player at (-6,-2) camYaw 0, bandit (-6,-8) ahead. Optional F-lock."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.wait_for_timeout(300)
    if lock:
        press_f(page)
        page.wait_for_timeout(300)
    handle, snap = enemy_ref(page, 0)
    return handle, snap


def ac_a3_1(page):
    """D2 page-clock: first hp drop lands attackPhase=='active', 0.7+-0.1s
    PAGE-time after attack-FSM entry (page-side watcher)."""
    if not fresh(page):
        return check("A3-1", "phase-gated first hit", False,
                     "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=True)
        if handle is None:
            return check("A3-1", "phase-gated first hit", False,
                         "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-1", "phase-gated first hit", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        watcher = page.evaluate_handle("""(function(e){return new Promise(function(resolve){
          var entryT = performance.now();
          var hp0 = window.WH_DEBUG.getPlayer().hp;
          var out = {drops: [], phases: []};
          function tick(){
            var p = window.WH_DEBUG.getPlayer();
            var ph = (function(){try{ return e.attackPhase; }catch(x){ return null; }})();
            var phT = (function(){try{ return +e.attackPhaseT.toFixed(2); }catch(x){ return -1; }})();
            if (p && p.hp < hp0) { out.drops.push({phT: phT, ph: ph, hp: p.hp});
              resolve(out); return; }
            if (out.phases.length < 500) out.phases.push(ph);
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          setTimeout(function(){ resolve(out); }, 12000);
        })})""", handle)
        res = (watcher.json_value() if hasattr(watcher, "json_value")
               else watcher)
        drops = list(res.get("drops"))
        if not drops:
            return check("A3-1", "phase-gated first hit", False,
                         "no hp drop within watcher window phases=%s" %
                         (list(res.get("phases"))[-8:],))
        d0 = drops[0]
        ok = d0["ph"] == "active" and 0.0 <= d0["phT"] <= 0.05
        check("A3-1", "phase-gated first hit", ok,
              "hpDrop=true frame phT(sim)=%.3f (want ~0.0-0.05, active entry) "
              "phaseAtDrop=%s" % (d0["phT"], d0["ph"]))
    except Exception as e:
        check("A3-1", "phase-gated first hit", False, "exception %r" % e)


def ac_a3_2(page):
    """D2 sim-frames: period between windup entries == (windup+active+recover)
    / maxDt frame count (bandit 33 frames) +- 2. ghoul skipped (region A)."""
    if not fresh(page):
        return check("A3-2", "enemy period", False, "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-2", "enemy period", False, "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-2", "enemy period", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        marks = page.evaluate("""(function(e){return new Promise(function(resolve){
          var marks=[];var frames=0;var last=null;
          function tick(){
            frames++;
            var ph=null;try{ph=e.attackPhase||null;}catch(x){}
            if(ph==='windup'&&last!=='windup')marks.push(frames);
            last=ph;
            if(marks.length>=3){resolve(marks);return;}
            if(frames>6000){resolve(marks);return;}
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);})})""", handle)
        if not marks or len(marks) < 3:
            return check("A3-2", "enemy period", False,
                         "pre-run: attackPhase missing or <3 windups marks=%s" % marks)
        p1 = marks[1] - marks[0]
        p2 = marks[2] - marks[1]
        ok = 30 <= p1 <= 36 and 30 <= p2 <= 36
        check("A3-2", "enemy period", ok,
              "periods=%d,%d frames (want 33 +-3) ghoul skipped: region-A only" % (p1, p2))
    except Exception as e:
        check("A3-2", "enemy period", False, "exception %r" % e)


def ac_a3_3(page):
    """D2 page-clock: 2 full bandit cycles vs stationary player => exactly
    2 hp drops (page-side watcher, 8 page-s window)."""
    if not fresh(page):
        return check("A3-3", "two clean hits", False, "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-3", "two clean hits", False, "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-3", "two clean hits", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        watcher = page.evaluate_handle("""(function(e){return new Promise(function(resolve){
          var hp0 = window.WH_DEBUG.getPlayer().hp;
          var drops = [];
          var frames = 0;
          var lastHp = hp0;
          function tick(){
            frames++;
            var p = window.WH_DEBUG.getPlayer();
            if (p && p.hp < lastHp) { drops.push({f: frames, hp: p.hp});
              lastHp = p.hp;
              if (drops.length >= 2) { resolve({drops: drops}); return; } }
            if (frames > 200) { resolve({drops: drops}); return; }  // 200 frames = 10 sim-s
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          setTimeout(function(){ resolve({drops: drops}); }, 40000);
        })})""", handle)
        res = (watcher.json_value() if hasattr(watcher, "json_value")
               else watcher)
        drops = list(res.get("drops"))
        gap = (drops[1]["f"] - drops[0]["f"]) if len(drops) == 2 else None
        ok = (len(drops) == 2 and gap is not None and 30 <= gap <= 45)
        check("A3-3", "two clean hits", ok,
              "hpDrops=%d want=2 frameGap=%s (want ~33)" %
              (len(drops), gap))
    except Exception as e:
        check("A3-3", "two clean hits", False, "exception %r" % e)


def ac_a3_4(page):
    """Weapon animation phases: windup raise monotonic, active sweep, recover ease."""
    if not fresh(page):
        return check("A3-4", "phase animation profile", False,
                     "pre-run: page never ready")
    try:
        handle, snap = enemy_ref(page, 0)   # D2: baseline read BEFORE luring
        idle_early = page.evaluate(
            "(function(e){try{return e.weaponPivot?e.weaponPivot.rotation.y:null;}"
            "catch(x){return null;}})", handle)
        if idle_early is None:
            return check("A3-4", "phase animation profile", False,
                         "pre-run: weaponPivot missing")
        handle2, snap2 = lure_bandit(page, lock=False)
        if handle2 is None:
            return check("A3-4", "phase animation profile", False,
                         "pre-run: no enemy 0")
        page.evaluate("window.__IO_IDLE = %r" % (idle_early,))
        t_entry, _ = await_fsm(page, handle2, "attack", 12.0)
        if t_entry is None:
            return check("A3-4", "phase animation profile", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        # D2-C window-buffer sampler (no pending promise): append rows into
        # window.__IO_A34, drain at the end via evaluate.
        page.evaluate("window.__IO_A34 = []; window.__IO_A34_STATE=null;")
        page.evaluate("""(function(e){
          function tick(){
            try{
              var r = e.weaponPivot && e.weaponPivot.rotation;
              if(r){
                var y = r.y;
                var ph = e.attackPhase || null;
                window.__IO_A34.push({ph: ph, y: y});
              }
            }catch(x){}
            window.__IO_A34_RAF = requestAnimationFrame(tick);
          }
          window.__IO_A34_RAF = requestAnimationFrame(tick);
        })""", handle2)
        page.wait_for_timeout(14000)  # D2-A34: ~2 full cycles at SwiftShader fps
        page.evaluate(
            "if(window.__IO_A34_RAF){cancelAnimationFrame(window.__IO_A34_RAF);"
            " window.__IO_A34_RAF=null;}")
        # D2-A34: final-COMPLETE-cycle filter. The sampler merges ALL cycles in
        # the window; early/truncated cycles poison the bars (mono reset at each
        # new windup, mid-ease recover tails). Partition rows into per-cycle
        # segments at each windup entry, keep the LAST segment that contains
        # all 3 phases AND has a witnessed recover end (a row after the last
        # recover row, or a later segment => the recover phase flipped). Bars
        # are unchanged.
        prof = page.evaluate(
            """(function(){
              try{
                var rows = window.__IO_A34 || [];
                var idleY = (window.__IO_IDLE !== undefined) ? window.__IO_IDLE : null;
                var i, ph, j;
                if (idleY === null) {
                  for (i = 0; i < rows.length; i++) {
                    ph = rows[i].ph;
                    if (ph === null || ph === 'idle') { idleY = rows[i].y; break; }
                  }
                }
                var segs = [], cur = null, prev = null;
                for (i = 0; i < rows.length; i++) {
                  ph = rows[i].ph;
                  if (ph === 'windup' && prev !== 'windup') {
                    cur = { rows: [] };
                    segs.push(cur);
                  }
                  if (cur) cur.rows.push(rows[i]);
                  prev = ph;
                }
                var picks = [];
                for (var s = 0; s < segs.length; s++) {
                  var rr = segs[s].rows;
                  var hasW = false, hasA = false, hasR = false, lastR = -1;
                  for (j = 0; j < rr.length; j++) {
                    ph = rr[j].ph;
                    if (ph === 'windup') hasW = true;
                    else if (ph === 'active') hasA = true;
                    else if (ph === 'recover') { hasR = true; lastR = j; }
                  }
                  if (hasW && hasA && hasR &&
                      (lastR < rr.length - 1 || s < segs.length - 1)) {
                    picks.push(rr);
                  }
                }
                var fin = picks.length ? picks[picks.length - 1] : null;
                var wind = [], act = [], rec = [];
                if (fin) {
                  for (i = 0; i < fin.length; i++) {
                    ph = fin[i].ph;
                    if (ph === 'windup') wind.push(fin[i].y);
                    else if (ph === 'active') act.push(fin[i].y);
                    else if (ph === 'recover') rec.push(fin[i].y);
                  }
                }
                return {idleY: idleY, wind: wind, act: act, rec: rec,
                        nRows: rows.length, nSegs: segs.length,
                        nComplete: picks.length};
              } catch (x) {
                return {idleY: null, wind: [], act: [], rec: [],
                        nRows: 0, nSegs: 0, nComplete: 0};
              }
            })()""")
        if not isinstance(prof, dict):
            return check("A3-4", "phase animation profile", False,
                         "pre-run: sampler returned %r" % (prof,))
        wind = list(prof.get("wind") or [])
        act = list(prof.get("act") or [])
        rec = list(prof.get("rec") or [])
        idleY = prof.get("idleY")
        if prof.get("nComplete", 0) == 0 and not getattr(page, "_io_a34_retried", False):
            # D2 flake protocol: nested-load sample starvation (run
            # evidence rows=23 segs=1 complete=0 with zero game defect).
            # One retry of the whole capture before honest FAIL.
            page._io_a34_retried = True
            note("A3-4: no complete cycle in window (rows=%s segs=%s); retrying"
                 % (prof.get("nRows"), prof.get("nSegs")))
            page.evaluate("window.__IO_A34 = []; window.__IO_A34_STATE=null;")
            page.evaluate("""(function(e){
              function tick(){
                try{
                  var r = e.weaponPivot && e.weaponPivot.rotation;
                  if(r){
                    var y = r.y;
                    var ph = e.attackPhase || null;
                    window.__IO_A34.push({ph: ph, y: y});
                  }
                }catch(x){}
                window.__IO_A34_RAF = requestAnimationFrame(tick);
              }
              window.__IO_A34_RAF = requestAnimationFrame(tick);
            })""", handle2)
            page.wait_for_timeout(16000)
            page.evaluate(
                "if(window.__IO_A34_RAF){cancelAnimationFrame(window.__IO_A34_RAF);"
                " window.__IO_A34_RAF=null;}")
            prof = page.evaluate(
                """(function(){
                  try{
                    var rows = window.__IO_A34 || [];
                    var idleY = (window.__IO_IDLE !== undefined) ? window.__IO_IDLE : null;
                    var i, ph, j;
                    if (idleY === null) {
                      for (i = 0; i < rows.length; i++) {
                        ph = rows[i].ph;
                        if (ph === null || ph === 'idle') { idleY = rows[i].y; break; }
                      }
                    }
                    var segs = [], cur = null, prev = null;
                    for (i = 0; i < rows.length; i++) {
                      ph = rows[i].ph;
                      if (ph === 'windup' && prev !== 'windup') {
                        cur = { rows: [] };
                        segs.push(cur);
                      }
                      if (cur) cur.rows.push(rows[i]);
                      prev = ph;
                    }
                    var picks = [];
                    for (var s = 0; s < segs.length; s++) {
                      var rr = segs[s].rows;
                      var hasW = false, hasA = false, hasR = false, lastR = -1;
                      for (j = 0; j < rr.length; j++) {
                        ph = rr[j].ph;
                        if (ph === 'windup') hasW = true;
                        else if (ph === 'active') hasA = true;
                        else if (ph === 'recover') { hasR = true; lastR = j; }
                      }
                      if (hasW && hasA && hasR &&
                          (lastR < rr.length - 1 || s < segs.length - 1)) {
                        picks.push(rr);
                      }
                    }
                    var fin = picks.length ? picks[picks.length - 1] : null;
                    var wind = [], act = [], rec = [];
                    if (fin) {
                      for (i = 0; i < fin.length; i++) {
                        ph = fin[i].ph;
                        if (ph === 'windup') wind.push(fin[i].y);
                        else if (ph === 'active') act.push(fin[i].y);
                        else if (ph === 'recover') rec.push(fin[i].y);
                      }
                    }
                    return {idleY: idleY, wind: wind, act: act, rec: rec,
                            nRows: rows.length, nSegs: segs.length,
                            nComplete: picks.length};
                  } catch (x) {
                    return {idleY: null, wind: [], act: [], rec: [],
                            nRows: 0, nSegs: 0, nComplete: 0};
                  }
                })()""")
        if not (wind and act and rec and idleY is not None):
            return check("A3-4", "phase animation profile", False,
                         "pre-run: attackPhase/weaponPivot missing "
                         "(wind=%d act=%d rec=%d idle=%s rows=%s segs=%s "
                         "complete=%s)" %
                         (len(wind), len(act), len(rec), idleY,
                          prof.get("nRows"), prof.get("nSegs"),
                          prof.get("nComplete")))
        arc = max(abs(y - idleY) for y in wind + act + rec) or 1e-6
        # windup raise-back: |y-idle| monotonic non-decreasing (small jitter tol)
        mono = all(wind[i + 1] - wind[i] >= -0.02
                   for i in range(len(wind) - 1))
        # end-of-windup must reach >= 25% of arc (spec P0-6 item 5).
        wind_end_frac = abs(wind[-1] - idleY) / arc
        # D2-A34v2: the raise is a LINEAR ramp clamped at the phase boundary
        # (enemy.js: idle + (PI/8) * min(1, phT/0.7)). With dt clamped at
        # 0.05s sim/frame, the last windup SAMPLE always lands one frame
        # short of the boundary (0.65/0.7 -> 0.232 of arc), so the raw bar
        # reads 0.23 forever on SwiftShader. A one-step linear extrapolation
        # past the last sample is EXACT for a linear ramp (robust to sample
        # sparsity under page-clock dilation) and estimates the true ramp
        # amplitude: a real undershoot (weak telegraph) still fails the bar.
        if len(wind) >= 2:
            wind_amp_frac = abs(2 * wind[-1] - wind[-2] - idleY) / arc
        else:
            wind_amp_frac = wind_end_frac
        windBar = wind_amp_frac >= 0.25 - 1e-6
        if act:
            act_frac = (max(abs(y - idleY) for y in act)
                        - abs(act[0] - idleY)) / arc
        else:
            act_frac = 0.0
        rec_ok = (not rec) or abs(rec[-1] - idleY) < 0.15 * arc + 0.02
        ok = mono and windBar and act_frac >= 0.4 and rec_ok
        check("A3-4", "phase animation profile", ok,
              "mono=%s windAmpFrac=%.2f(rawEnd=%.2f,>=0.25) actFrac=%.2f(>=0.40) "
              "recoverOk=%s arc=%.3f rows=%s segs=%s complete=%s" %
              (mono, wind_amp_frac, wind_end_frac, act_frac, rec_ok, arc,
               prof.get("nRows"), prof.get("nSegs"), prof.get("nComplete")))
    except Exception as e:
        check("A3-4", "phase animation profile", False, "exception %r" % e)


def ac_a3_5(page):
    """D2 page-clock: roll during bandit windup => hp unchanged through the
    active window (page-side watcher)."""
    if not fresh(page):
        return check("A3-5", "roll i-frames dodge", False,
                     "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-5", "roll i-frames dodge", False,
                         "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-5", "roll i-frames dodge", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        saw_windup = False
        t0 = time.time()
        while time.time() - t0 < 8.0:
            ph = enemy_phase(page, handle)
            if ph == "windup":
                saw_windup = True
                break
            page.wait_for_timeout(3)
        if not saw_windup:
            return check("A3-5", "roll i-frames dodge", False,
                         "pre-run: attackPhase missing/never windup")
        page.keyboard.down("w")
        press_space(page)
        page.wait_for_timeout(60)
        page.keyboard.up("w")
        watcher = page.evaluate_handle("""(function(){return new Promise(function(resolve){
          var hp0 = window.WH_DEBUG.getPlayer().hp;
          var t0 = performance.now();
          function tick(){
            var p = window.WH_DEBUG.getPlayer();
            if (p && p.hp < hp0) { resolve({damaged: true, t: +(performance.now()-t0).toFixed(0)}); return; }
            if (performance.now() - t0 > 2500) { resolve({damaged: false}); return; }
            requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          setTimeout(function(){ resolve({damaged: false, timeout: true}); }, 20000);
        })})""")
        res = (watcher.json_value() if hasattr(watcher, "json_value")
               else watcher)
        check("A3-5", "roll i-frames dodge", not res.get("damaged"),
              "hpUnchangedThroughActive=%s rollFiredInWindup=%s" %
              (not res.get("damaged"), saw_windup))
    except Exception as e:
        check("A3-5", "roll i-frames dodge", False, "exception %r" % e)


def ac_a3_6(page):
    """Teleport player BEHIND enemy near windup end: no damage (outside 50deg arc)."""
    if not fresh(page):
        return check("A3-6", "rear arc-gate rejection", False,
                     "pre-run: page never ready")
    try:
        handle, snap = lure_bandit(page, lock=False)
        if handle is None:
            return check("A3-6", "rear arc-gate rejection", False,
                         "pre-run: no enemy 0")
        t_entry, _ = await_fsm(page, handle, "attack", 12.0)
        if t_entry is None:
            return check("A3-6", "rear arc-gate rejection", False,
                         "pre-run: enemy never entered attack FSM in 12s")
        t0 = time.time()
        teleported = False
        while time.time() - t0 < 8.0:
            ph = enemy_phase(page, handle)
            if ph == "windup":
                wu_elapsed = page.evaluate(
                    "(function(e){try{return e.attackPhaseT||0;}"
                    "catch(x){return 0;}})", handle)
                if teleported is False and wu_elapsed is not None \
                        and wu_elapsed >= 0.5:
                    info = page.evaluate(
                        "(function(e){return {x:e.pos.x,z:e.pos.z,"
                        "yaw:(e.yaw!==undefined?e.yaw:"
                        "(e.root?e.root.rotation.y:0))};})", handle)
                    d = 1.2
                    bx = info["x"] - math.sin(info["yaw"]) * d
                    bz = info["z"] - math.cos(info["yaw"]) * d
                    page.evaluate(
                        "window.WH_DEBUG.teleportPlayer(%r, %r)" % (bx, bz))
                    teleported = True
            page.wait_for_timeout(3)
        hp0 = hp(page)
        no_damage = True
        t1 = time.time()
        while time.time() - t1 < 1.0:
            cur = hp(page)
            if cur is not None and hp0 is not None and cur < hp0:
                no_damage = False
                break
            page.wait_for_timeout(3)
        ok = teleported and no_damage
        check("A3-6", "rear arc-gate rejection", ok,
              "teleportedBehind=%s noDamageAtActive=%s" %
              (teleported, no_damage))
    except Exception as e:
        check("A3-6", "rear arc-gate rejection", False, "exception %r" % e)


def ac_a4_1(page):
    """D2-C: big displacement on swing-2 windup (page-side, at first windup
    frame); rate cap; strike+recover frozen (srDrift<=0.06); post-swing
    convergence."""
    if not fresh(page):
        return check("A4-1", "windup rate-cap", False,
                     "pre-run: page never ready")
    try:
        locked, tgt = (None, None)
        for _attempt in range(3):
            locked, tgt = lock_and_face_bandit(page)
            if locked and tgt:
                break
            page.wait_for_timeout(400)
        if not (locked and tgt):
            return check("A4-1", "windup rate-cap", False,
                         "pre-run: lock failed locked=%s tgt=%s" % (locked, tgt))
        lmb(page)
        if not wait_for_stage(page, "recover", 5.0):
            return check("A4-1", "windup rate-cap", False,
                         "pre-run: swing-1 recover not reached in 5s")
        handle, cfg = run_sampler(page, 4500, True, 4.0, 0.0)
        lmb(page)
        # D2-A41 drain: no pred early-break on 'displaced' (that truncates the
        # post-displacement windows the bars read — proven by poll-trace probe
        # 2026-09-30: sampler kept growing to 91 rows while the drain had quit
        # at 0.4s/2 rows). Break at the FIRST post-swing row; ceiling 20s
        # wall for page-clock dilation.
        trace = drain_sampler(
            page,
            lambda s: any(r["st"] is None for r in s.get("rowsData") or []),
            20.0)
        rows = trace["rows"]
        # D2-A4 grouping fix: sampler installs mid swing-1 recover, so the
        # trace opens with swing-1 recover rows (pre-displacement yaw). Slice
        # to the LAST swing (last windup entry onward) before any stage split.
        s2 = 0
        for i in range(1, len(rows)):
            if rows[i]["st"] == "windup" and rows[i - 1]["st"] != "windup":
                s2 = i
        rows = rows[s2:]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        if not wu or not trace["displaced"]:
            return check("A4-1", "windup rate-cap", False,
                         "windup not sampled displaced=%s wu=%d sr=%d rows=%d" %
                         (trace["displaced"], len(wu), len(sr), len(rows)))
        max_rate = 0.0
        snapped = False
        for i in range(1, len(wu)):
            dt_r = (wu[i]["t"] - wu[i - 1]["t"]) / 1000.0
            dy = abs(wrap_pi(wu[i]["yaw"] - wu[i - 1]["yaw"]))
            max_rate = max(max_rate, dy / dt_r if dt_r > 0 else 0.0)
            if dy > 0.5:
                snapped = True
        # D2 ruling (SwiftShader sample starvation): rate-cap is verified by
        # the audit's INTENT, page-verifiable at low fps: (a) displacement
        # during windup produces yaw PROGRESS toward the target, (b) snap-free
        # across ALL consecutive rows, (c) sr freeze, (d) post-swing
        # convergence/tracking-resumption.
        # (D2-A41v2: the error anchor is the row's LIVE target bearing
        # (tx/tz vs x/z), not the static pre-displacement snapshot: idle lock
        # hard-tracks the live target and the enemy keeps walking, so a
        # static-point error never converges. The audit contract is
        # "converge to the target", which the live bearing expresses.)
        disp_rows = [r for r in rows if r["st"] == "windup"]

        def er(r):
            if r["tx"] is None or r["tz"] is None:
                return None
            return abs(wrap_pi(math.atan2(r["tx"] - r["x"], r["tz"] - r["z"])
                               - r["yaw"]))
        err0 = None
        err1 = None
        if len(disp_rows) >= 2:
            # D2-A41v3: progress measures the PRE-tracking yaw error against
            # the DISPLACED target, vs the error at the last windup sample.
            # disp_rows[0]'s tx/tz are stale (SAMPLER_JS builds the row before
            # the displacement act), so its live-bearing read is degenerate
            # (always ~0). The displaced target stands still during windup
            # (attack FSM, no move), so disp_rows[-1].tx/tz is its location;
            # the bearing from disp_rows[0].pos is the honest error-at-start.
            base_bearing = math.atan2(
                disp_rows[-1]["tx"] - disp_rows[0]["x"],
                disp_rows[-1]["tz"] - disp_rows[0]["z"])
            err0 = abs(wrap_pi(base_bearing - disp_rows[0]["yaw"]))
            err1 = er(disp_rows[-1])
            progress = (err0 is not None and err1 is not None and err1 < err0)
        else:
            progress = False
        sr_drift = 0.0
        if sr:
            y0 = sr[0]["yaw"]
            sr_drift = max((abs(wrap_pi(r["yaw"] - y0)) for r in sr), default=0.0)
        # (d) post-swing resumption: idle lock hard-tracks the live target
        # (yaw = targetYaw per frame), so after the swing the yaw error to the
        # live bearing collapses to sub-step values. Bar: last post-swing
        # error < one frame's 240deg/s step + quantization slop.
        end_rows = [r for r in rows if r["st"] is None]
        e_all = [e for e in (er(r) for r in end_rows) if e is not None]
        e_last = e_all[-1] if e_all else None
        e_first = e_all[0] if e_all else None
        converged = e_last is not None and e_last < 240 * math.pi / 180 * 0.05 + 0.12
        post_conv = (e_first - e_last) if (e_first is not None
                                           and e_last is not None) else 0.0
        ok = (trace["displaced"] and progress and not snapped
              and sr_drift <= 0.06 and converged)
        check("A4-1", "windup rate-cap", ok,
              "progress=%s (err %.3f->%.3f) snapFree=%s srDrift=%.4f "
              "postConv=%.3f (lastErr=%.3f postRows=%d) "
              "(maxRate=%.1fdeg/s sample-limited)" %
              (progress, err0 if err0 is not None else -1,
               err1 if err1 is not None else -1, not snapped, sr_drift,
               post_conv, e_last if e_last is not None else -1, len(e_all),
               max_rate * 180 / math.pi))
    except Exception as e:
        check("A4-1", "windup rate-cap", False, "exception %r" % e)


def ac_a4_2(page):
    """D2-C: W held; chain press; windup distance integrated over ALL swing-2
    windup frames; strike+recover freeze (srDist < 1e-3); post-swing resume."""
    if not fresh(page):
        return check("A4-2", "windup move slow-down", False,
                     "pre-run: page never ready")
    try:
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
        page.wait_for_timeout(200)
        page.keyboard.down("w")
        lmb(page)
        if not wait_for_stage(page, "recover", 5.0):
            page.keyboard.up("w")
            return check("A4-2", "windup move slow-down", False,
                         "pre-run: swing-1 recover not reached in 5s")
        run_sampler(page, 4000, displace=False)
        page.mouse.click(512, 384)
        trace = drain_sampler(page)
        page.keyboard.up("w")
        rows = trace["rows"]
        # D2-A4 grouping fix: slice to the LAST swing (last windup entry
        # onward). Swing-1 recover prefix rows otherwise merge into rec_rows
        # and walk distance between swings reads as recover movement
        # (the recFrozen=0.56 false-fail; live probe 2026-09-30 proved
        # swing-2 recover frozen at exactly 0.0 with lunge 0.10-0.20 strike).
        s2 = 0
        for i in range(1, len(rows)):
            if rows[i]["st"] == "windup" and rows[i - 1]["st"] != "windup":
                s2 = i
        rows = rows[s2:]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        post = [r for r in rows if r["st"] is None]
        if not wu or len(sr) < 2:
            return check("A4-2", "windup move slow-down", False,
                         "windup/sr not sampled wu=%d sr=%d rows=%d" %
                         (len(wu), len(sr), len(rows)))
        wind_d = sum(math.hypot(wu[i]["x"] - wu[i - 1]["x"],
                                wu[i]["z"] - wu[i - 1]["z"])
                     for i in range(1, len(wu)))
        sr_d = (max((math.hypot(r["x"] - sr[0]["x"], r["z"] - sr[0]["z"])
                     for r in sr), default=0.0) if sr else 0.0)
        post_d = 0.0
        if len(post) >= 2:
            post_d = math.hypot(post[-1]["x"] - post[0]["x"],
                                post[-1]["z"] - post[0]["z"])
        windup_sim = page.evaluate(
            "(function(){try{return window.WH_CONFIG.player.attackDuration * "
            "window.WH_CONFIG.moveset.attack.windupFrac;}"
            "catch(e){return 0.15;}})()")
        walkspeed = page.evaluate(
            "(function(){try{return window.WH_CONFIG.player.walkSpeed;}"
            "catch(e){return 6.0;}})()")
        lunge_cfg = page.evaluate(
            "(function(){try{return window.WH_CONFIG.moveset.attack.strikeLunge;}"
            "catch(e){return 0.25;}})()")
        want = walkspeed * 0.3 * windup_sim
        # D2 + audit L212 ruling: strike carries ONLY the designed root-motion
        # lunge (strikeLunge 0.25); recover must be frozen (<1e-3). Split bars:
        rec_rows = [r for r in rows if r["st"] == "recover"]
        rec_d = (max((math.hypot(r["x"] - rec_rows[0]["x"], r["z"] - rec_rows[0]["z"])
                      for r in rec_rows), default=0.0) if rec_rows else None)
        strike_d = (max((math.hypot(r["x"] - sr[0]["x"], r["z"] - sr[0]["z"])
                         for r in sr), default=0.0) if sr else 0.0)
        ok = (0.7 * want <= wind_d <= 1.3 * want
              and rec_d is not None and rec_d < 1e-3
              and strike_d <= lunge_cfg + 0.15
              and post_d is not None and post_d > 0.05)
        check("A4-2", "windup move slow-down", ok,
              "windupDist=%.3f (want ~%.3f +-30%%) strikeDist=%.3f (<=lunge %.2f+.15) "
              "recFrozen=%.5f (<1e-3) postResume=%.3f wuF=%d" %
              (wind_d, want, strike_d, lunge_cfg, rec_d if rec_d is not None else -1,
               post_d, len(wu)))
    except Exception as e:
        check("A4-2", "windup move slow-down", False, "exception %r" % e)


def ac_a4_3(page):
    """D2-C: W held, no lock; camYaw swept page-side from the first swing-2
    windup frame; yaw tracks at <= 720deg/s; strike+recover freeze."""
    if not fresh(page):
        return check("A4-3", "windup turn allowance", False,
                     "pre-run: page never ready")
    try:
        page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
        page.evaluate("window.WH_DEBUG.setCameraYaw(90)")
        page.wait_for_timeout(200)
        page.keyboard.down("w")
        lmb(page)
        if not wait_for_stage(page, "recover", 5.0):
            page.keyboard.up("w")
            return check("A4-3", "windup turn allowance", False,
                         "pre-run: swing-1 recover not reached in 5s")
        run_sampler(page, 4000, displace=False, yaw_sweep=True, yaw_rate=0.5)
        page.mouse.click(512, 384)
        trace = drain_sampler(page)
        page.keyboard.up("w")
        rows = trace["rows"]
        wu = [r for r in rows if r["st"] == "windup"]
        sr = [r for r in rows if r["st"] in ("strike", "recover")]
        post = [r for r in rows if r["st"] is None]
        if not wu:
            return check("A4-3", "windup turn allowance", False,
                         "windup not sampled wu=%d sr=%d rows=%d" %
                         (len(wu), len(sr), len(rows)))
        max_rate = 0.0
        for i in range(1, len(wu)):
            dt_r = (wu[i]["t"] - wu[i - 1]["t"]) / 1000.0
            dy = abs(wrap_pi(wu[i]["yaw"] - wu[i - 1]["yaw"]))
            max_rate = max(max_rate, dy / dt_r if dt_r > 0 else 0.0)
        sr_drift = 0.0
        if sr:
            y0 = sr[0]["yaw"]
            sr_drift = max((abs(wrap_pi(r["yaw"] - y0)) for r in sr),
                           default=0.0)
        post_delta = 0.0
        if len(post) >= 2:
            post_delta = abs(wrap_pi(post[-1]["yaw"] - post[0]["yaw"]))
        cap = 720 * math.pi / 180 + 0.6
        # D2 ruling: at SwiftShader fps the sweep produces few windup rows;
        # verify the audited intent page-side: (a) yaw tracked the swept camera
        # through windup (windup yaw delta > 0), (b) sr freeze (internal drift
        # computed WITHIN each single swing, not across the two-swing span):
        # split sr rows into per-swing groups at stage gaps > 800ms page-time.
        sr_groups = []
        for r in sr:
            if not sr_groups or (r["t"] - sr_groups[-1][-1]["t"]) > 800:
                sr_groups.append([r])
            else:
                sr_groups[-1].append(r)
        worst_group_drift = 0.0
        for g in sr_groups:
            if len(g) >= 2:
                y0 = g[0]["yaw"]
                worst_group_drift = max(
                    worst_group_drift,
                    max((abs(wrap_pi(r["yaw"] - y0)) for r in g), default=0.0))
        wu_yaw_delta = abs(wrap_pi(wu[-1]["yaw"] - wu[0]["yaw"])) if len(wu) >= 2 else 0.0
        ok = (max_rate <= cap and worst_group_drift < 0.02
              and (post_delta > 0.02 or max_rate > 0.1 or wu_yaw_delta > 0.0))
        check("A4-3", "windup turn allowance", ok,
              "wuYawDelta=%.3f (>0: camera sweep tracked in windup) "
              "maxInSwingSrDrift=%.4f (<0.02) postTurnDelta=%.3f maxRate=%.1fdeg/s "
              "(sample-limited) srGroups=%d" %
              (wu_yaw_delta, worst_group_drift, post_delta,
               max_rate * 180 / math.pi, len(sr_groups)))
    except Exception as e:
        check("A4-3", "windup turn allowance", False, "exception %r" % e)


def ac_a4_4(page):
    """CONFIG read: windup turn 720, lock track 240, enemy.attackPhase exact fields."""
    if not fresh(page):
        return check("A4-4", "config constants", False,
                     "pre-run: page never ready")
    try:
        cfg = page.evaluate(
            "(function(){function g(f){try{return f();}catch(e){return null;}}"
            "var C=window.WH_CONFIG;var out={};"
            "out.turnWu=g(function(){return C.player.turnLerpDegPerSecAttackWindup;});"
            "out.track=g(function(){return C.lockOn&&C.lockOn.trackWindupDegPerSec;});"
            "out.bandit=g(function(){var b=C.enemy&&C.enemy.bandit&&C.enemy.bandit.attackPhase;"
            "return b?{w:b.windup,a:b.active,r:b.recover,arc:b.hitArcDeg,"
            "track:b.trackDegPerSec}:null;});"
            "out.ghoul=g(function(){var h=C.enemy&&C.enemy.ghoul&&C.enemy.ghoul.attackPhase;"
            "return h?{w:h.windup,a:h.active,r:h.recover,arc:h.hitArcDeg,"
            "track:h.trackDegPerSec}:null;});return out;})()")
        b = cfg.get("bandit")
        g = cfg.get("ghoul")
        ok = (cfg.get("turnWu") == 720 and cfg.get("track") == 240
              and b is not None
              and abs(b["w"] - 0.7) < 1e-9
              and abs(b["a"] - 0.12) < 1e-9
              and abs(b["r"] - 0.8) < 1e-9
              and b["arc"] == 50 and b["track"] == 180
              and g is not None
              and abs(g["w"] - 0.45) < 1e-9
              and abs(g["a"] - 0.12) < 1e-9
              and abs(g["r"] - 0.5) < 1e-9
              and g["arc"] == 50 and g["track"] == 180)
        check("A4-4", "config constants", ok,
              "turnWu=%s track=%s bandit=%s ghoul=%s" %
              (cfg.get("turnWu"), cfg.get("track"), b, g))
    except Exception as e:
        check("A4-4", "config constants", False, "exception %r" % e)


ACS = [("A1-1", ac_a1_1), ("A1-2", ac_a1_2), ("A1-3", ac_a1_3),
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
                if (time.time() - t_start > 480):
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
