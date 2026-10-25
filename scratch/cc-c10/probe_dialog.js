// CC-C10 dialog / quest-state probe (node only: a minimal DOM stub + stub
// game / WH_ASSETS / WH_GROUND; NO browser, NO harness). Drives js/npc.js
// through the A2/A3/A5 state paths and prints one PASS line per check.
// usage: node probe_dialog.js <repoRoot>
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const ROOT = path.resolve(process.argv[2]);
const byId = {}, keyListeners = [];
function mkEl(tag) {
  const e = { tag, children: [], style: {}, listeners: {}, className: '', textContent: '', id: '',
    classList: { toggle() {}, add() {}, remove() {} },
    appendChild(c) { this.children.push(c); if (c.id) byId[c.id] = c; return c; },
    addEventListener(t, f) { (this.listeners[t] = this.listeners[t] || []).push(f); },
    click() { (this.listeners.click || []).forEach(f => f()); } };
  Object.defineProperty(e.style, 'cssText', { set(v) { v.split(';').forEach(kv => { const i = kv.indexOf(':');
    if (i > 0) e.style[kv.slice(0, i)] = kv.slice(i + 1); }); }, get() { return ''; } });
  return e;
}
byId['wh-root'] = mkEl('div'); byId['wh-hud'] = mkEl('div');
globalThis.document = { createElement: mkEl, getElementById: id => byId[id] || null,
  addEventListener(t, f) { if (t === 'keydown') keyListeners.push(f); } };
globalThis.innerWidth = 800; globalThis.innerHeight = 600;
require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
const C = window.WH_CONFIG, N = C.regionC.npc, D = N.dialog;
let loaded = false;
window.WH_ASSETS = { isLoaded: () => loaded, isFailed: () => false, groundHeight: () => 1.8,
  instance: () => { const g = new THREE.Group(); g.add(new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.8, 0.6))); return g; },
  getTemplate: () => { const g = new THREE.Group(); g.add(new THREE.Object3D()); return g; } };
window.WHSkeletonUtils = { clone: t => { const c = t.clone(true); c.userData.real = true; return c; } };
require(path.join(ROOT, 'prototype/js/npc.js'));
const W = window.WH_NPC;
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(60, 4 / 3, 0.1, 500);
const game = { scene, camera, inventoryUI: { blocked: false },
  regionManager: { logic: { activeId: C.regionC.id } },
  player: { pos: new THREE.Vector3(N.x + 2, 0, N.z), state: 'alive', inputSuspended: false,
    setInputSuspended(v) { this.inputSuspended = v; } } };
camera.position.set(N.x + 4, 6, N.z + 4); camera.lookAt(N.x, 3, N.z); camera.updateMatrixWorld(true);
const res = []; const check = (name, ok, info) => res.push((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  ' + JSON.stringify(info) : ''));

check('surface', ['init', 'update', 'talkPrompt', 'openDialog', 'closeDialog'].every(k => typeof W[k] === 'function'));
check('new game state = available', W.questState() === 'available');
W.init(game);
const dlg = byId['wh-npc-dialog'], line = () => dlg.children[0].children[1].textContent;
const btns = dlg.children[0].children[2].children, cont = btns[0], close = btns[1];
W.update(0.016);
const root = scene.children.find(o => o.name === 'npc-' + N.asset);
check('built in C, seated on footY', !!root && Math.abs(root.position.y - window.WH_GROUND.footY(C.regionC.id, N.x, N.z, N.footR)) < 1e-9, root && +root.position.y.toFixed(2));
check('visible in range', root.visible === true);
check('talkPrompt in range', W.talkPrompt() === true);
game.player.pos.x = N.x + N.interactM + 0.5;
check('talkPrompt out of range = false', W.talkPrompt() === false);
game.player.pos.x = N.x + 2;
loaded = true; W.update(0.016);
check('stand-in -> GLB clone swap', root.children.length === 1 && root.children[0].userData.real === true);
check('open -> line1', W.openDialog() === true && line() === D.line1 && dlg.style.display === 'flex');
check('open suspends input + blocks inventory', game.player.inputSuspended === true && game.inventoryUI.blocked === true);
check('talkPrompt false while open (chain refuses)', W.talkPrompt() === false);
cont.click(); check('continue -> line2 (quest still available)', line() === D.line2 && W.questState() === 'available');
cont.click(); check('continue -> line3 activates', line() === D.line3 && W.questState() === 'active' && cont.style.display === 'none');
cont.click(); check('continue past line3 = no-op', line() === D.line3);
close.click(); check('close restores input', dlg.style.display === 'none' && game.player.inputSuspended === false && game.inventoryUI.blocked === false);
W.openDialog(); check('re-talk while active = repeat line only', line() === D.repeat && cont.style.display === 'none');
keyListeners.forEach(f => f({ code: 'Escape', repeat: false, preventDefault() {} }));
check('Esc closes', dlg.style.display === 'none' && game.player.inputSuspended === false);
W.openDialog(); game.player.state = 'dead'; W.update(0.016);
check('death force-closes', dlg.style.display === 'none' && game.player.inputSuspended === false);
game.player.state = 'alive'; check('death keeps quest', W.questState() === 'active');
W.openDialog(); game.regionManager.logic.activeId = C.regionB.id; W.update(0.016);
check('region change force-closes + hides', dlg.style.display === 'none' && root.visible === false && game.player.inputSuspended === false);
check('talkPrompt false outside C', W.talkPrompt() === false);
game.regionManager.logic.activeId = C.regionC.id;
W.restoreQuest(undefined); check('restore missing block -> available', W.questState() === 'available');
W.restoreQuest({ findDaughter: 'active' }); check('restore active', W.questState() === 'active');
W.restoreQuest('junk'); check('restore non-object -> available', W.questState() === 'available');
W.restoreQuest({ findDaughter: 'bogus' }); check('restore bad state -> available', W.questState() === 'available');
W.restoreQuest({ findDaughter: 'complete' }); check('restore complete kept (CC-C11 state)', W.questState() === 'complete');
W.openDialog(); check('complete -> repeat line, no re-activation', line() === D.repeat && W.questState() === 'complete'); W.closeDialog();
game.player.pos.x = N.x + N.cullM + 1; W.update(0.016);
check('culled past cullM', root.visible === false);
console.log(res.join('\n'));
console.log(res.every(r => r.startsWith('PASS')) ? 'DIALOG PROBE PASS' : 'DIALOG PROBE FAIL');
