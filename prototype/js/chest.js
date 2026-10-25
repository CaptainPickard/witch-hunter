// CC-C11: quest-unlocked camp chest; only deployed campkit sites, not world camps.
(function () {
  'use strict';
  var CFG = window.WH_CONFIG, K = CFG.camp, C = K.chest;
  var game = null, model = null, body = null, panel = null, chestGrid = null, bagGrid = null;
  var open = false, anchor = null, signature = '';

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // CC-C11: pegs are a module of each deployed site. Translate the chest's
  // [right, back] offset from the pegs in the site's own placement frame.
  function positionOf(site) {
    var pegs = site.modules.filter(function (m) { return m.row.id === 'pegs'; })[0];
    if (!pegs || !site.f) return null;
    return { x: pegs.x + site.f.z * C.offset[0] - site.f.x * C.offset[1],
      z: pegs.z - site.f.x * C.offset[0] - site.f.z * C.offset[1] };
  }

  function nearest() {
    if (!game || !game.camp || !window.WH_NPC || window.WH_NPC.questState() !== 'complete') return null;
    var rid = game.regionManager && game.regionManager.logic.activeId, p = game.player.pos;
    var best = null, bestD2 = Infinity;
    // camps() includes world camps, which have no pegs or site orientation.
    game.camp.camps().forEach(function (site) {
      if (site.world || site.regionId !== rid) return;
      var pos = positionOf(site);
      if (!pos) return;
      var d2 = Math.pow(p.x - pos.x, 2) + Math.pow(p.z - pos.z, 2);
      if (d2 < bestD2) { best = { site: site, pos: pos, d2: d2 }; bestD2 = d2; }
    });
    return best;
  }

  function buildBody() {
    var root = new THREE.Group();
    root.name = 'cc-c11-camp-chest';
    var wood = new THREE.MeshStandardMaterial({ color: 0x493726, roughness: 1 });
    var iron = new THREE.MeshStandardMaterial({ color: 0x858070, roughness: 0.8 });
    var box = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.65, 0.6), wood);
    box.position.y = 0.39; root.add(box);
    var lid = new THREE.Mesh(new THREE.BoxGeometry(1.08, 0.15, 0.68), wood);
    lid.position.y = 0.79; root.add(lid);
    var latch = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.3, 0.05), iron);
    latch.position.set(0, 0.6, 0.33); root.add(latch);
    root.visible = false;
    game.scene.add(root);
    return root;
  }

  function close() {
    if (!open) return;
    open = false;
    panel.style.display = 'none';
    game.inventoryUI.blocked = false;
    game.player.setInputSuspended(false);
  }

  function moveDeposit(i) {
    var item = game.inventory.slotAt(i);
    if (!item) return;
    var added = model.addItem(item.id, item.count);
    if (added) game.inventory.removeFromSlot(i, added);
    render();
  }
  function moveWithdraw(i) {
    var item = model.slotAt(i);
    if (!item) return;
    var added = game.inventory.addItem(item.id, item.count);
    if (added) model.removeFromSlot(i, added);
    render();
  }

  function fillGrid(grid, inventory, label, action) {
    grid.textContent = '';
    inventory.forEachSlot(function (item, i) {
      var d = item && window.WH_INVENTORY.itemDef(item.id);
      var btn = el('button', 'cook-btn', item ? label + ': ' + (d ? d.name : item.id) + ' x' + item.count : C.empty);
      btn.type = 'button'; btn.tabIndex = -1; btn.disabled = !item;
      btn.style.cssText = 'min-height:45px;white-space:normal;font-size:10px;padding:3px;';
      btn.addEventListener('click', function () { action(i); });
      grid.appendChild(btn);
    });
  }
  function render() {
    if (!panel || !game || !model) return;
    signature = JSON.stringify([model.slots, game.inventory.slots]);
    fillGrid(chestGrid, model, C.withdraw, moveWithdraw);
    fillGrid(bagGrid, game.inventory, C.deposit, moveDeposit);
  }

  function buildPanel() {
    var root = el('div'); root.id = 'wh-chest-menu';
    root.style.cssText = 'position:absolute;inset:0;display:none;align-items:flex-end;justify-content:center;' +
      'padding-bottom:8%;box-sizing:border-box;background:rgba(5,4,3,.6);z-index:20;' +
      'font-family:monospace;color:#d8d2c0;image-rendering:pixelated;user-select:none;';
    var box = el('div', 'inv-panel'); box.style.cssText = 'max-width:780px;width:94%;max-height:82vh;overflow-y:auto;';
    root.appendChild(box);
    box.appendChild(el('div', 'inv-title', C.title));
    box.appendChild(el('div', 'inv-hint', C.withdraw));
    chestGrid = el('div', 'cook-btns');
    chestGrid.style.cssText = 'display:grid;grid-template-columns:repeat(' + C.slotsX + ',minmax(0,1fr));gap:3px;';
    box.appendChild(chestGrid);
    box.appendChild(el('div', 'inv-hint', C.deposit));
    bagGrid = el('div', 'cook-btns');
    bagGrid.style.cssText = 'display:grid;grid-template-columns:repeat(' + C.slotsX + ',minmax(0,1fr));gap:3px;';
    box.appendChild(bagGrid);
    var row = el('div', 'cook-btns');
    var done = el('button', 'cook-btn', C.close);
    done.type = 'button'; done.tabIndex = -1; done.addEventListener('click', close);
    row.appendChild(done); box.appendChild(row);
    box.appendChild(el('div', 'inv-hint', C.hint));
    document.getElementById('wh-root').appendChild(root);
    panel = root;
  }

  // Camp interactRadius is binding; chest.interactM may narrow, never widen it.
  function interactPrompt() {
    var hit = nearest();
    return !!hit && !!body && body.visible && !open && game.player.state === 'alive' &&
      !game.player.inputSuspended && hit.d2 <= Math.pow(Math.min(K.interactRadius, C.interactM), 2);
  }
  function tryOpen() {
    if (!interactPrompt()) return false;
    render();
    open = true;
    panel.style.display = 'flex';
    game.inventoryUI.blocked = true;
    game.player.setInputSuspended(true);
    return true;
  }
  function update(dt) {
    if (!game || !game.regionManager) return;
    // Re-read camps() every frame: a packed/re-placed site moves the chest.
    var hit = nearest();
    if (hit && !body) body = buildBody();
    if (body) {
      body.visible = !!hit;
      if (hit) {
        anchor = hit.site;
        var G = window.WH_GROUND;
        var y = G && G.has(hit.site.regionId) ? G.footY(hit.site.regionId, hit.pos.x, hit.pos.z, 0.4) : 0;
        body.position.set(hit.pos.x, y, hit.pos.z);
        body.rotation.y = Math.atan2(hit.site.f.x, hit.site.f.z);
      } else anchor = null;
    }
    if (open && (!hit || hit.site !== anchor || game.player.state !== 'alive' ||
        hit.d2 > Math.pow(Math.min(K.interactRadius, C.interactM), 2))) close();
    if (open && signature !== JSON.stringify([model.slots, game.inventory.slots])) render();
  }

  // CC-C11: save only slot contents; restore never transfers items to the bag.
  function capture() {
    return model.slots.map(function (s) { return s ? { id: s.id, count: s.count } : null; });
  }
  function restore(slots) {
    if (slots === undefined) return; // old v1 profile with no chest block
    if (!Array.isArray(slots)) return;
    model.slots = Array.from({ length: C.capacity }, function (_, i) {
      var s = slots[i];
      if (!s || typeof s.id !== 'string' || !Number.isInteger(s.count) || s.count < 1 ||
          !window.WH_INVENTORY.itemDef(s.id)) return null;
      return { id: s.id, count: Math.min(s.count, window.WH_INVENTORY.stackCapOf(s.id)) };
    });
    render();
  }
  function init(g) {
    game = g;
    model = new window.WH_INVENTORY.Inventory(C.capacity);
    buildPanel();
    document.addEventListener('keydown', function (e) {
      if (e.code !== 'Escape' || e.repeat || !open) return;
      e.preventDefault(); close();
    });
  }
  window.WH_Chest = { init: init, update: update, interactPrompt: interactPrompt,
    tryOpen: tryOpen, capture: capture, restore: restore };
})();
