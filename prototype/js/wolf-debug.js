// Witch Hunter - CC-C12 wolf-anim debug chip (URL ?whdbg=1).
// DIAGNOSTIC ONLY - reads live state from window.WH_GAME; touches nothing.
// Nicko: load the playtest URL with ?whdbg=1, walk to any wolf pack, and
// read the chip (top-right, under FPS). Tell IO the lines it shows.
(function () {
  'use strict';
  var qp = new URLSearchParams(window.location.search);
  if (qp.get('whdbg') !== '1') return;
  var el = document.createElement('div');
  el.id = 'wh-wolfdbg';
  el.style.cssText = 'position:fixed;top:8px;right:8px;z-index:9999;' +
    'background:rgba(0,0,0,0.75);color:#9fe89f;font:11px/1.5 monospace;' +
    'padding:6px 9px;border:1px solid #3a5a3a;white-space:pre;pointer-events:none;';
  document.getElementById('wh-hud').appendChild(el);
  // CC-C13b: every helper below is read-only and guarded (the chip never throws)
  function actW(act) {
    try { return act && act.isRunning && act.isRunning() ? act.getEffectiveWeight() : 0; } catch (err) { return 0; }
  }
  function wOf(a, key) {
    var act = a && a.mixer && a.actions ? a.actions[key] : null;
    return act ? actW(act).toFixed(2) : '?';
  }
  function top2(a) {
    var acts = a && a.actions ? a.actions : {}, rows = [];
    Object.keys(acts).forEach(function (k) {
      var w = actW(acts[k]);
      if (w >= 0.01) rows.push({ k: k.replace(/^WH_Wolf_/, ''), w: w });
    });
    rows.sort(function (p, q) { return q.w - p.w; });
    return rows.length ? rows.slice(0, 2).map(function (r) { return r.k + ':' + r.w.toFixed(2); }).join('/') : 'none';
  }
  function standIn(e) {
    var hit = null;
    try {
      if (e.body && e.body.traverse) {
        e.body.traverse(function (o) { if (!hit && o && /standin/i.test(o.name || '')) hit = o.name; });
      }
    } catch (err) { hit = null; }
    return hit;
  }
  function clipCount() {
    try {
      var A = window.WH_ASSETS, cfg = window.WH_CONFIG;
      var name = (cfg && cfg.assets && cfg.assets.bodyByType && cfg.assets.bodyByType.wolf) || 'wolfBody';
      var c = A && A.getClips ? A.getClips(name) : [];
      return c && c.length != null ? c.length : 0;
    } catch (err) { return 0; }
  }
  function tailLines(e, n) {
    var si = standIn(e);
    var out = ['  CLIPS=' + n + (n === 0 ? ' (0 CLIPS = LATE-SWAP/STAND-IN BUG)' : '') +
      ' rigid=' + (e.rigidAnim ? 'yes' : 'no') + ' standin=' + (si ? 'y' : 'n')];
    if (si) out.push('  STAND-IN IN PLAY: ' + si);
    return out;
  }
  function snap() {
    var g = window.WH_GAME;
    if (!g || !g.regionManager) { el.textContent = 'whdbg: waiting for game...'; return; }
    var rm = g.regionManager;
    var lines = ['WH WOLF DBG'];
    var regions = Object.keys(rm.enemies || {});
    var found = 0, nClips = clipCount();
    for (var r = 0; r < regions.length && found < 2; r++) {
      var list = rm.enemies[regions[r]] || [];
      for (var i = 0; i < list.length && found < 2; i++) {
        var e = list[i];
        if (!e || e.type !== 'wolf' || e.fsm === 'dead') continue;
        found++;
        var a = e.anim;
        if (!a) {
          lines.push('wolf#' + i + ' NO ANIM OBJ (stand-in or late-swap bug - capture this!)');
          lines.push.apply(lines, tailLines(e, nClips));
          continue;
        }
        var st = {};
        try { st = (a.getState ? a.getState() : {}) || {}; } catch (err) { st = {}; }
        var wlk = st.weights && st.weights.WH_Wolf_Walk != null ? st.weights.WH_Wolf_Walk.toFixed(2) : '?';
        var idl = st.weights && st.weights.WH_Wolf_Idle != null ? st.weights.WH_Wolf_Idle.toFixed(2) : '?';
        var mts = a.mixer && typeof a.mixer.timeScale === 'number' ? a.mixer.timeScale.toFixed(2) : '?';
        lines.push('wolf#' + i + ' fsm=' + e.fsm + ' spd=' + (e.animMoveSpeed || 0).toFixed(1) +
          ' clip=' + (st.clip || '?') + ' ts=' + (st.timeScale || 0).toFixed(2) + ' mts=' + mts +
          ' W(walk)=' + wlk + ' W(idle)=' + idl);
        lines.push('  W(Hit)=' + wOf(a, 'WH_Wolf_Hit') + ' W(Death)=' + wOf(a, 'WH_Wolf_Death') +
          ' loco=' + (st.locomotion || '?') + ' t=' + (st.time || 0).toFixed(2) + '/' + '?' +
          ' top=' + top2(a));
        lines.push.apply(lines, tailLines(e, nClips));
      }
    }
    if (!found) lines.push('no live wolves in loaded regions (walk to a pack)');
    el.textContent = lines.join('\n');
  }
  setInterval(snap, 500);
  snap();
})();