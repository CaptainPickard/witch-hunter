// CC-C11 offline chest probe: source invariants and site-frame geometry.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync('prototype/js/chest.js','utf8'), window={}; vm.runInNewContext(fs.readFileSync('prototype/js/CONFIG.js','utf8'),{window,Math});
const C=window.WH_CONFIG.camp, pegs=C.modules.find(m=>m.id==='pegs');
assert(pegs && pegs.offset[0]===0 && pegs.offset[1]===3.6);
assert(C.chest.capacity===24 && C.chest.slotsX===6 && C.chest.slotsY===4);
for(const mark of ['game.camp.camps()', 'site.modules', "m.row.id === 'pegs'", 'C.offset[0]', 'C.offset[1]', 'K.interactRadius', 'C.interactM', 'model.addItem','model.removeFromSlot', 'game.inventory.addItem', 'game.inventory.removeFromSlot', 'new window.WH_INVENTORY.Inventory(C.capacity)', 'function capture()', 'function restore(slots)', 'inv-panel','inv-title','cook-btns','cook-btn','inv-hint']) assert(src.includes(mark),mark);
const site={x:12,z:21,f:{x:0,z:1}}, p={x:12,z:17.4};
const x=p.x+site.f.z*C.chest.offset[0]-site.f.x*C.chest.offset[1],z=p.z-site.f.x*C.chest.offset[0]-site.f.z*C.chest.offset[1];
console.log('STATIC PASS chest 24 slots (6x4), only deployed sites via camps(), per-frame position from pegs; example pegs (12,17.4) chest ('+x+','+z+'), offset '+JSON.stringify(C.chest.offset)+', interactM '+C.chest.interactM+', campRadius '+C.interactRadius);
