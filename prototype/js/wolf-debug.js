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
  function snap() {
    var g = window.WH_GAME;
    if (!g || !g.regionManager) { el.textContent = 'whdbg: waiting for game...'; return; }
    var rm = g.regionManager;
    var lines = ['WH WOLF DBG'];
    var regions = Object.keys(rm.enemies || {});
    var found = 0;
    for (var r = 0; r < regions.length && found < 2; r++) {
      var list = rm.enemies[regions[r]];
      for (var i = 0; i < list.length && found < 2; i++) {
        var e = list[i];
        if (e.type !== 'wolf' || e.fsm === 'dead') continue;
        found++;
        var a = e.anim;
        if (!a) { lines.push('wolf#' + i + ' NO ANIM OBJ (stand-in or late-swap bug - capture this!)'); continue; }
        var st = a.getState ? a.getState() : {};
        var wlk = st.weights && st.weights.WH_Wolf_Walk != null ? st.weights.WH_Wolf_Walk.toFixed(2) : '?';
        var idl = st.weights && st.weights.WH_Wolf_Idle != null ? st.weights.WH_Wolf_Idle.toFixed(2) : '?';
        lines.push('wolf#' + i + ' fsm=' + e.fsm + ' spd=' + (e.animMoveSpeed || 0).toFixed(1) +
          ' clip=' + (st.clip || '?') + ' ts=' + (st.timeScale || 0).toFixed(2) +
          ' W(walk)=' + wlk + ' W(idle)=' + idl +
          ' loco=' + (st.locomotion || '?') + ' t=' + (st.time || 0).toFixed(2) + '/' + '?');
      }
    }
    if (!found) lines.push('no live wolves in loaded regions (walk to a pack)');
    el.textContent = lines.join('\n');
  }
  setInterval(snap, 500);
  snap();
})();