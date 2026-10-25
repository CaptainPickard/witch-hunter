// CC-C11 pre-paste and post-paste deterministic sarcophagus clearance probe.
const fs = require('fs');
const vm = require('vm');
const root = process.cwd();
const window = {};
vm.runInNewContext(fs.readFileSync(root + '/prototype/js/CONFIG.js', 'utf8'), {window});
const D = window.WH_CONFIG.regionD;
const proposed = {x: -201, z: -185, rotY: 0.4, scale: 1.2}; // seed CC-C11-20261025-01; den-local (-15,-5)
const present = D.props.filter(p=>p.asset==='stoneSarcophagus');
const site = present[0] || proposed; // pre-paste proposed, post-paste real CONFIG row
const dist = (a,b) => Math.hypot(a.x-b.x, a.z-b.z);
const file=fs.readFileSync(root+'/art-direction/3d/assets/crypt/stone-sarcophagus-pixelated.glb');
const gltf=JSON.parse(file.subarray(20,20+file.readUInt32LE(12)).toString('utf8'));
const pos=gltf.accessors.find(a=>a.type==='VEC3'&&a.min&&a.max);
const footprintWidth=pos.max[0]-pos.min[0], sarcRadius=footprintWidth*site.scale/2;
const spawn = D.spawn, lair = {x: D.center.x, z: D.center.z + window.WH_CONFIG.enemy.rotmother.lair.y};
const dx=lair.x-spawn.x, dz=lair.z-spawn.z, t=Math.max(0,Math.min(1,((site.x-spawn.x)*dx+(site.z-spawn.z)*dz)/(dx*dx+dz*dz)));
const walkway = dist(site,{x:spawn.x+t*dx,z:spawn.z+t*dz});
const rows = D.props.filter(p=>p.asset!=='stoneSarcophagus').map(p=>({asset:p.asset,d:dist(site,p)})).sort((a,b)=>a.d-b.d);
console.log(JSON.stringify({seed:'CC-C11-20261025-01',site,denLocal:{x:site.x-D.center.x,z:site.z-D.center.z},footprintWidth,sarcRadius,dCenter:dist(site,D.center),dLair:dist(site,lair),dWalkway:walkway,nearest:rows.slice(0,5),present:present.length},null,2));
if (site.x!==proposed.x || site.z!==proposed.z || present.length>1 || dist(site,D.center)>32.5 || dist(site,lair)<Math.max(12.5,10+1.1+sarcRadius+1) || walkway<2 || rows.some(p=>p.d<(p.asset.startsWith('whWall')?1:1.5))) process.exitCode=1;
