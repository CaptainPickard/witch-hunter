// Witch Hunter prototype - NPCs (CC-C10, io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md).
// One villager for now: Farmer Aldric (CONFIG.regionC.npc) in the CC-C17
// homestead yard, the quest giver of findDaughter (CONFIG.regionC.quest).
// The farmer = a static placeholder body (the raw rigged dwarf smith GLB,
// bind pose, no mixer - IO ruling B3b) seated on the heightfield through
// WH_GROUND.footY, added straight to the scene (camp.js pattern: region
// dispose never eats it) and shown only while Region C is active and the
// player is inside npc.cullM. A small DOM name plate floats over his head.
// Talk = the game.js interact chain (tryTalkNpc, after tryNotch): E / touch
// USE within npc.interactM opens the DIALOG PANEL (tent-menu pattern: inv-
// panel + cook-btns, own el() copy, inline overlay style - no style.css).
// Lines 1 -> 2 -> 3 advance on Continue; reaching line 3 sets the quest
// 'active' (once); re-talk while active shows only the repeat line. Close /
// Esc close; death or a region change force-closes. The panel suspends
// input like the camp menu (player.setInputSuspended + inventoryUI.blocked),
// so the interact chain refuses E while it is open.
// QUEST HOLDER: this module owns the findDaughter state (one source of
// truth); game.js setupSaveHooks captures / restores it (questState block)
// and drives the HUD quest line from it. Completion = CC-C11.
// Every player-facing string comes from CONFIG.regionC.npc / .quest.
// Exposes window.WH_NPC = { init, update, talkPrompt, openDialog,
// closeDialog, questState, restoreQuest } (game.js owns the calls).

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var N = CFG.regionC.npc;
  var Q = CFG.regionC.quest;
  var D = N.dialog;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  var game = null;
  var root = null;            // scene group at the farmer's seat (built on first C visit)
  var body = null;            // the body holder inside root
  var real = false;           // body = the loaded GLB clone (not the stand-in box)
  var shown = false;
  var label = null;           // DOM name plate (#wh-hud)
  var dlg = null;             // dialog DOM refs
  var dialogOpen = false;
  var lineIdx = 0;            // 0..2 = line1..line3; -1 = the repeat line
  var quest = Q.states[0];    // findDaughter state ('available' on a NEW GAME)
  // CC-C11: rescued is a sub-field of findDaughter, not a fourth quest state.
  var rescued = false;
  var daughterRoot = null, daughterBody = null, daughterReal = false;
  var _v = null;

  // ---- farmer body ---------------------------------------------------------------
  // Loaded GLB -> a WHSkeletonUtils clone (bones rebound to the clone; the
  // manifest key has no CHARACTERS row, so WH_ASSETS.instance would share the
  // template skeleton). Still in flight / failed -> the WH_ASSETS stand-in box;
  // update() swaps the real clone in once the asset lands.
  function makeBody() {
    var A = window.WH_ASSETS;
    real = A.isLoaded(N.asset) && !A.isFailed(N.asset);
    var b = real ? window.WHSkeletonUtils.clone(A.getTemplate(N.asset)) : A.instance(N.asset);
    b.scale.setScalar(N.bodyHeight / (A.groundHeight(N.asset) || N.bodyHeight));
    return b;
  }

  function mountBody() {
    if (body) root.remove(body);
    body = makeBody();
    root.add(body);
  }

  function build() {
    var y = window.WH_GROUND ? window.WH_GROUND.footY(CFG.regionC.id, N.x, N.z, N.footR) : 0;
    root = new THREE.Group();
    root.name = 'npc-' + N.asset;
    root.position.set(N.x, y, N.z);
    root.rotation.y = N.rotY;
    root.visible = false;
    game.scene.add(root);
    mountBody();
  }

  // CC-C11: one daughter body moves from chamber to homestead when rescued.
  // The streamed GLB uses the same skeleton-safe clone path as the farmer.
  function mountDaughter() {
    var A = window.WH_ASSETS, name = 'dwarfFemaleBody';
    if (daughterBody) daughterRoot.remove(daughterBody);
    daughterReal = A.isLoaded(name) && !A.isFailed(name);
    daughterBody = daughterReal ? window.WHSkeletonUtils.clone(A.getTemplate(name)) : A.instance(name);
    daughterBody.scale.setScalar(N.bodyHeight / (A.groundHeight(name) || N.bodyHeight));
    daughterRoot.add(daughterBody);
  }
  function updateDaughter() {
    if (!game || !game.regionManager) return;
    var rid = game.regionManager.logic.activeId;
    var inDen = quest === 'active' && !rescued && rid === CFG.regionD.id;
    var atHome = rescued && rid === CFG.regionC.id;
    if (!inDen && !atHome) {
      if (daughterRoot) daughterRoot.visible = false; // chamber removal on rescue
      return;
    }
    if (!daughterRoot) {
      daughterRoot = new THREE.Group();
      daughterRoot.name = 'cc-c11-daughter';
      game.scene.add(daughterRoot);
      mountDaughter();
    }
    var A = window.WH_ASSETS;
    if (!daughterReal && A.isLoaded('dwarfFemaleBody') && !A.isFailed('dwarfFemaleBody')) mountDaughter();
    var x = inDen ? CFG.regionD.props.filter(function (p) { return p.asset === 'stoneSarcophagus'; })[0].x + 2 : N.x + 2;
    var z = inDen ? CFG.regionD.props.filter(function (p) { return p.asset === 'stoneSarcophagus'; })[0].z + 0.5 : N.z + 1;
    var y = window.WH_GROUND ? window.WH_GROUND.footY(rid, x, z, N.footR) : 0;
    daughterRoot.position.set(x, y, z);
    daughterRoot.rotation.y = inDen ? 0 : N.rotY;
    daughterRoot.visible = true;
  }

  // ---- DOM: name plate + dialog panel ----------------------------------------------
  function buildLabel() {
    label = el('div', null, N.name);
    label.id = 'wh-npc-label';
    label.style.cssText = 'position:absolute;display:none;transform:translate(-50%,-100%);' +
      'font-family:monospace;font-size:12px;letter-spacing:2px;color:#e3dcc4;white-space:nowrap;' +
      'text-shadow:1px 1px 0 #000,0 0 6px rgba(0,0,0,0.9);pointer-events:none;';
    document.getElementById('wh-hud').appendChild(label);
  }

  function buildDialog() {
    var r = el('div');
    r.id = 'wh-npc-dialog';
    // #wh-camp-menu's overlay rules, inline (style.css is ID-scoped there)
    r.style.cssText = 'position:absolute;inset:0;display:none;align-items:flex-end;' +
      'justify-content:center;padding-bottom:14%;box-sizing:border-box;' +
      'background:rgba(5,4,3,0.35);z-index:20;font-family:monospace;color:#d8d2c0;' +
      'image-rendering:pixelated;user-select:none;';
    var panel = el('div', 'inv-panel npc-dialog-panel');
    panel.style.cssText = 'max-width:520px;width:86%;';
    r.appendChild(panel);
    panel.appendChild(el('div', 'inv-title', N.name));
    var line = el('div', 'npc-dialog-line');
    line.style.cssText = 'margin:12px 4px 14px;font-size:14px;line-height:1.5;text-align:center;color:#d8d2c0;';
    panel.appendChild(line);
    var rows = el('div', 'cook-btns npc-dialog-btns');
    var cont = el('button', 'cook-btn npc-dialog-btn', D.cont);
    var close = el('button', 'cook-btn npc-dialog-btn', D.close);
    [cont, close].forEach(function (b) { b.type = 'button'; b.tabIndex = -1; rows.appendChild(b); });
    cont.addEventListener('click', advance);
    close.addEventListener('click', closeDialog);
    panel.appendChild(rows);
    panel.appendChild(el('div', 'inv-hint', D.hint));
    document.getElementById('wh-root').appendChild(r);
    dlg = { root: r, line: line, cont: cont };
  }

  function showLine() {
    var last = lineIdx < 0 || lineIdx >= 2;
    dlg.line.textContent = lineIdx < 0 ? D.repeat : D['line' + (lineIdx + 1)];
    // CC-C11: negative sentinel lines keep the three original intro lines intact.
    if (lineIdx === -2) dlg.line.textContent = D.lineRescued;
    if (lineIdx === -3) dlg.line.textContent = D.lineComplete;
    if (lineIdx === -4) dlg.line.textContent = D.lineRescue;
    dlg.cont.style.display = last ? 'none' : '';
    // line 3 = the quest seed: available -> active, the one assignment site
    if (lineIdx === 2 && quest === Q.states[0]) quest = 'active';
  }

  function advance() {
    if (!dialogOpen || lineIdx < 0 || lineIdx >= 2) return;
    lineIdx++;
    showLine();
  }

  function setOpen(open) {
    if (dialogOpen === open) return;
    dialogOpen = open;
    dlg.root.style.display = open ? 'flex' : 'none';
    game.inventoryUI.blocked = open;
    game.player.setInputSuspended(open);
  }

  // ---- talk range ------------------------------------------------------------------
  function inC() {
    var rm = game && game.regionManager;
    return !!rm && rm.logic.activeId === CFG.regionC.id;
  }

  function playerDist() {
    var p = game.player.pos;
    return Math.hypot(p.x - N.x, p.z - N.z);
  }

  // true while E / USE would open the dialog (the interact prompt mirrors it)
  function talkPrompt() {
    if (!game || dialogOpen || !shown || !inC()) return false;
    var p = game.player;
    if (p.state !== 'alive' || p.inputSuspended) return false;
    return playerDist() <= N.interactM;
  }

  // the farmer's dialog: lines 1-3 while the quest is available, else the
  // short state-aware line (CC-C11 owns the completion copy)
  function openDialog() {
    if (!game || dialogOpen) return false;
    lineIdx = quest === Q.states[0] ? 0 : -1;
    // CC-C11: rescued return talk completes the quest; later talks stay complete.
    if (quest === 'active' && rescued) { quest = 'complete'; lineIdx = -2; }
    else if (quest === 'complete') lineIdx = -3;
    showLine();
    setOpen(true);
    return true;
  }

  function closeDialog() {
    if (dlg) setOpen(false);
  }

  // CC-C11: rescue is a den-only E action; no quest, no sarcophagus action.
  function rescuePrompt() {
    if (!game || dialogOpen || quest !== 'active' || rescued || !game.regionManager ||
        game.regionManager.logic.activeId !== CFG.regionD.id) return false;
    var p = game.player;
    if (p.state !== 'alive' || p.inputSuspended) return false;
    var sarc = CFG.regionD.props.filter(function (row) { return row.asset === 'stoneSarcophagus'; })[0];
    if (!sarc) return false;
    return Math.hypot(p.pos.x - sarc.x, p.pos.z - sarc.z) <= Q.rescueInteractM;
  }
  function tryRescue() {
    if (!rescuePrompt()) return false;
    rescued = true;
    updateDaughter(); // hide chamber body on this press, before the next frame
    lineIdx = -4;
    showLine();
    setOpen(true);
    game.inventoryUI.toast(Q.rescuedToast);
    return true;
  }

  // ---- per frame -------------------------------------------------------------------
  function update(dt) {
    if (!game || !game.regionManager) return;
    var here = inC();
    if (here && !root) build();
    // CC-C11: daughter can exist in D before the C farmer has ever been built.
    updateDaughter();
    if (!root) return;
    var A = window.WH_ASSETS;
    if (!real && A.isLoaded(N.asset) && !A.isFailed(N.asset)) mountBody();   // stand-in -> GLB
    var dist = playerDist();
    shown = here && dist <= N.cullM;
    root.visible = shown;
    // death / region change: never leave the input suspended behind the panel
    if (dialogOpen && (!here || game.player.state !== 'alive')) closeDialog();
    updateLabel(dist);
  }

  function updateLabel(dist) {
    if (!shown || dialogOpen || dist > N.labelM) { label.style.display = 'none'; return; }
    if (!_v) _v = new THREE.Vector3();
    _v.set(N.x, root.position.y + N.bodyHeight + N.labelLiftM, N.z);
    _v.project(game.camera);
    if (_v.z > 1 || _v.z < -1) { label.style.display = 'none'; return; }
    label.style.display = 'block';
    label.style.left = Math.round((_v.x * 0.5 + 0.5) * window.innerWidth) + 'px';
    label.style.top = Math.round((-_v.y * 0.5 + 0.5) * window.innerHeight) + 'px';
  }

  // ---- quest state (save block questState, game.js setupSaveHooks) ------------------
  function questState() {
    return quest;
  }
  // CC-C11: persistent findDaughter object, retaining the C10 string getter.
  function questStateDetail() {
    return { state: quest, rescued: rescued };
  }

  // schema v1: missing / non-object / unknown state -> 'available'
  function restoreQuest(block) {
    var s = block && typeof block === 'object' ? block[Q.id] : null;
    var rescueBit = s && typeof s === 'object' && s.rescued === true;
    if (s && typeof s === 'object') s = s.state;
    quest = Q.states.indexOf(s) >= 0 ? s : Q.states[0];
    rescued = rescueBit && (quest === 'active' || quest === 'complete');
    updateDaughter();
    closeDialog();
  }

  function init(g) {
    game = g;
    buildLabel();
    buildDialog();
    document.addEventListener('keydown', function (e) {
      if (e.code !== 'Escape' || e.repeat || !dialogOpen) return;
      e.preventDefault();
      closeDialog();
    });
  }

  window.WH_NPC = {
    init: init,
    update: update,
    talkPrompt: talkPrompt,
    openDialog: openDialog,
    closeDialog: closeDialog,
    questState: questState,
    // CC-C11 rescue state + den interact seam.
    questStateDetail: questStateDetail,
    rescuePrompt: rescuePrompt,
    tryRescue: tryRescue,
    restoreQuest: restoreQuest
  };
})();
