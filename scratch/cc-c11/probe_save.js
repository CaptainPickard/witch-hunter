// CC-C11 offline save-wrap probe: static ownership and schema guards.
const fs=require('fs'),assert=require('assert'),g=fs.readFileSync('prototype/js/game.js','utf8'),n=fs.readFileSync('prototype/js/npc.js','utf8'),c=fs.readFileSync('prototype/js/chest.js','utf8'),s=fs.readFileSync('prototype/js/save.js','utf8');
const wrap=g.slice(g.indexOf('function setupSaveHooks()'),g.indexOf('// S5 quit persist'));
for(const needle of ['data.lairs = window.WH_Enemy.captureLairs()', 'data.questState.findDaughter = window.WH_NPC.questStateDetail()', 'data.chest = window.WH_Chest.capture()', 'stored.questState.findDaughter = window.WH_NPC.questStateDetail()', 'stored.chest = window.WH_Chest.capture()', 'window.WH_NPC.restoreQuest(data.questState)', 'if (data && window.WH_Chest) window.WH_Chest.restore(data.chest)', 'baseRestore(g, data)'])assert(wrap.includes(needle),needle);
assert(wrap.indexOf('restoreQuest(data.questState)')<wrap.indexOf('baseRestore(g, data)'));
assert(n.includes('if (s && typeof s === \'object\') s = s.state') && n.includes('Q.states.indexOf(s) >= 0 ? s : Q.states[0]'));
assert(c.includes('if (slots === undefined) return;') && c.includes('model.slots = Array.from(') && c.includes('model.slotAt(i)'));
assert(s.includes('version') || s.includes('v:'));
console.log('STATIC PASS schema-v1 additive quest detail + chest array capture/save/restore; legacy missing chest no-op, legacy quest string accepted');
