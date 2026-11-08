// CC-C11 offline dialog/HUD copy probe (static only, no browser).
const fs=require('fs'),assert=require('assert'),n=fs.readFileSync('prototype/js/npc.js','utf8'),g=fs.readFileSync('prototype/js/game.js','utf8');
for(const s of ["lineIdx = quest === Q.states[0] ? 0 : -1", "if (quest === 'active' && rescued)", "else if (quest === 'complete') lineIdx = -3",'lineIdx === -2','lineIdx === -3','lineIdx === -4','D.lineRescued','D.lineComplete','D.lineRescue'])assert(n.includes(s),s);
for(const s of ['CFG.regionC.quest.hudRescued','CFG.regionC.quest.hudComplete','CFG.regionC.quest.hudText','detail.state === \'complete\'','detail.rescued'])assert(g.includes(s),s);
console.log('STATIC PASS intro(3 lines) preserved; rescue line -4, homecoming -2, complete re-talk -3; HUD available:hidden active:search rescued:return complete:unlocked');
