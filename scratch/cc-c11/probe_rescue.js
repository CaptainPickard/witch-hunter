// CC-C11 offline state-machine probe: static, no browser or harness.
const fs=require('fs'), vm=require('vm'), assert=require('assert');
const src=fs.readFileSync('prototype/js/npc.js','utf8');
const window={}; vm.runInNewContext(fs.readFileSync('prototype/js/CONFIG.js','utf8'),{window,Math});
const q=window.WH_CONFIG.regionC.quest, d=window.WH_CONFIG.regionC.npc.dialog;
for(const key of ['hudText','hudRescued','hudComplete','rescuedToast','rescuePrompt']) assert(q[key],key);
for(const key of ['lineRescue','lineRescued','lineComplete']) assert(d[key],key);
for(const mark of ["quest === 'active' && !rescued", 'rescued && rid === CFG.regionC.id', "rid === CFG.regionD.id", "daughterRoot.visible = false", "rescued = true", "quest = 'complete'", "game.inventoryUI.toast(Q.rescuedToast)", 'return { state: quest, rescued: rescued }']) assert(src.includes(mark),mark);
assert.strictEqual((src.match(/quest = 'active';/g)||[]).length,1);
assert.strictEqual((src.match(/quest = 'complete';/g)||[]).length,1);
console.log('STATIC PASS available -> active -> rescued:true -> complete; daughter chamber(active&&!rescued) -> homestead(rescued), hidden otherwise; toast CONFIG');
