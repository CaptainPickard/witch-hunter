"""PART2: SAMPLER_JS + D2 helpers (orig lines 212..313) for the harness rebuild."""

SAMPLER_JS_PART = r'''SAMPLER_JS = """(function(cfg){
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
})"""'''


def drain_sampler(page, until_state=None, max_wall_s=None):
    """Wait until the sampler state flags done/condition, then return rows."""
    deadline = (page.__io_sampler_deadline
                if hasattr(page, "__io_sampler_deadline")
                else time.time() + 3.0)
    if max_wall_s:
        deadline = min(deadline, time.time() + max_wall_s)
    while time.time() < deadline:
        st = page.evaluate(
            "(function(){try{var s=window.__IO_SAMPLER_STATE;"
            "return s ? JSON.stringify({d:s.displaced, n:s.rows.length}) : null;}"
            "catch(x){return null;}})()"
        )
        page.wait_for_timeout(30)
        if until_state and st:
            try:
                if json.loads(st).get("d"):
                    break
            except Exception:
                pass
    rows = page.evaluate(
        "(function(){try{return window.__IO_SAMPLER_ROWS;}catch(x){return [];}})()"
    )
    state = page.evaluate(
        "(function(){try{var s=window.__IO_SAMPLER_STATE;"
        "return {displaced:s.displaced, n:s.rows.length};}"
        "catch(x){return {displaced: False, n: 0};}})()"
    )
    page.evaluate("if(window.__IO_SAMPLER)window.__IO_SAMPLER.stop();")
    return {"rows": rows, "displaced": state.get("displaced", False)}


def run_sampler(page, ms=0.0, displace=False, dx=0.0, dz=0.0,
                yaw_sweep=False, yaw_rate=0.0):
    """Install a rAF sampler on the page for ms milliseconds. Returns rows."""
    handle = page.evaluate_handle(
        "(function(){var e=window.WH_DEBUG.getEnemy(0);return e?e.ref:null;})()"
    )
    cfg = {"ms": ms, "displace": displace, "dx": dx, "dz": dz,
           "eget": None, "yawSweep": yaw_sweep, "yawRate": yaw_rate}
    return handle, page.evaluate_handle(SAMPLER_JS, cfg)


def wait_for_stage(page, want, timeout_s=5.0):
    """Poll from python until stage == want (stage is set for >=1 sim frame)."""
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if stage(page) == want:
            return True
        page.wait_for_timeout(3)
    return False


def fresh(page):
    """Fresh load + ready wait. Every AC starts here unless it explicitly reuses."""
    return wait_ready(page)


def wrap_pi(x):
    """Wrap an angle to (-pi, pi]."""
    return (x + math.pi) % (2.0 * math.pi) - math.pi


def lock_and_face_bandit(page):
    """Shared setup: stand at (-6,-2), camYaw 0, F-lock the bandit at (-6,-8)."""
    page.evaluate("window.WH_DEBUG.teleportPlayer(-6, -2)")
    page.evaluate("window.WH_DEBUG.setCameraYaw(0)")
    page.wait_for_timeout(500)
    press_f(page)
    page.wait_for_timeout(500)
    locked = page.evaluate(
        "(function(){try{return !!window.WH_DEBUG.isLocked();}"
        "catch(e){return false;}})()"
    )
    tgt = page.evaluate(
        "(function(){try{return window.WH_DEBUG.getLockTarget();}"
        "catch(e){return null;}})()"
    )
    return locked, tgt