# ------------------------------------------------ light-scene scan (JS eval) --
# Traverses the live scene once; returns everything the L-ACs need. Mirrors
# the blueprint JS_LIGHT_SCAN contract (uuids, hemi detail, dir detail,
# pool lights, sockets, lantern hunt + parent-chain check, cfg refs).
JS_LIGHT_SCAN = """(function(){
  var out={ambient:0,hemi:0,dir:0,sprite:0,point:0,pointLights:[],sprites:[],
           hemiDetail:null,dirDetail:null,moonL:null};
  var G=window.WH_GAME;
  G.scene.traverse(function(o){
    if(o.isAmbientLight) out.ambient++;
    if(o.isHemisphereLight){out.hemi++;
      out.hemiDetail={c:o.color.getHex(),gc:o.groundColor.getHex(),i:o.intensity};}
    if(o.isDirectionalLight){out.dir++;
      out.dirDetail={c:o.color.getHex(),x:o.position.x,y:o.position.y,z:o.position.z,
        ty:o.target?o.target.position.y:null,tx:o.target?o.target.position.x:null,
        tz:o.target?o.target.position.z:null,i:o.intensity};
      out.moonL={c:o.color.getHex(),pos:{x:o.position.x,y:o.position.y,z:o.position.z},
        tgt:o.target?{x:o.target.position.x,y:o.target.position.y,z:o.target.position.z}:null,
        i:o.intensity};}
    if(o.isPointLight) out.pointLights.push({uuid:o.uuid,c:o.color.getHex(),
      x:o.position.x,y:o.position.y,z:o.position.z,d:o.distance,dec:o.decay,
      i:o.intensity,parentUuid:o.parent?o.parent.uuid:null});
    if(o.isSprite){var m=o.material||{};
      out.sprites.push({uuid:o.uuid,
        blending:(m.blending===THREE.AdditiveBlending)?1:0,
        mapSrc:(m.map&&m.map.image&&m.map.image.src)?m.map.image.src
              :((m.map&&m.map.image&&m.map.image.currentSrc)
                 ?m.map.image.currentSrc:"null"),
        depthWrite:!!m.depthWrite,transparent:!!m.transparent,
        x:o.position.x,y:o.position.y,z:o.position.z,
        scaleX:o.scale.x,scaleY:o.scale.y,visible:o.visible});}
  });
  out.point=out.pointLights.length;
  var poolUuids=(G.lightPool||[]).map(function(l){return l.uuid;});
  out.lantern=out.pointLights.filter(function(p){
    return poolUuids.indexOf(p.uuid)<0;})[0]||null;
  if(out.lantern){
    var root=G.player?G.player.root:null;
    var byUuid={}; G.scene.traverse(function(o){byUuid[o.uuid]=o;});
    var node=byUuid[out.lantern.parentUuid]; var found=false; var hops=0;
    while(node&&hops<20){ if(node===root){found=true;break;} node=node.parent; hops++; }
    out.lantern.chainToPlayerRoot=found;
    var v=new THREE.Vector3(); var l2=null;
    G.scene.traverse(function(o){ if(o.uuid===out.lantern.uuid) l2=o; });
    if(l2){ l2.getWorldPosition(v);
      out.lantern.wpv={x:v.x,y:v.y,z:v.z}; } }
  out.cfg=window.WH_CONFIG.lighting;
  out.cfgPool=window.WH_CONFIG.lightPool;
  out.ambCfg=window.WH_CONFIG.lighting.ambientIntensity;
  out.moonI=out.dirDetail?out.dirDetail.i:null;
  out.activeRegion=(window.WH_DEBUG.getRegionManager&&
     window.WH_DEBUG.getRegionManager().logic.activeId)||null;
  out.pool=(window.WH_DEBUG.getLightPool&&window.WH_DEBUG.getLightPool())||null;
  out.sockets=(window.WH_DEBUG.getLightSockets&&
               window.WH_DEBUG.getLightSockets())||null;
  return out;
})()"""