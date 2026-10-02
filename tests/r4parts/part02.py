

# ------------------------------------------------ in-page probes (JS) -------
# Shared prelude: first mesh carrying material.map under a root.
FIRSTMAP = """function firstMap(root){var f=null; if(!root) return null;
  root.traverse(function(o){ if(f||!o.isMesh) return;
    var ms=Array.isArray(o.material)?o.material:[o.material];
    for(var i=0;i<ms.length;i++){ if(ms[i]&&ms[i].map){f={mesh:o,map:ms[i].map};
      break;} } }); return f;}
  var BODIES=['playerBody','banditBody','ghoulBody'];"""

# AC-R4-1 probe (one evaluate): template maps + live-instance map uuids.
TEX_JS = """(function(){ %s
  var A=window.WH_ASSETS, C=window.WH_CONFIG.assets||{};
  var out={key:('pixelatedBodies' in C)?C.pixelatedBodies:'__absent__',
           loaded:A.loadedCount(), rows:[], live:{playerBody:[],banditBody:[],
           ghoulBody:[]}, consts:{nearest:THREE.NearestFilter,
           lmml:THREE.LinearMipmapLinearFilter, linear:THREE.LinearFilter}};
  BODIES.forEach(function(n){ var f=firstMap(A.getTemplate(n));
    var r={name:n, failed:A.isFailed(n), clips:A.getClips(n).length};
    if(f){ var m=f.map, im=m.image||{};
      r.w=im.width; r.h=im.height; r.src=im.currentSrc||im.src||'';
      r.ctor=im.constructor?im.constructor.name:''; r.mag=m.magFilter;
      r.min=m.minFilter; r.flipY=m.flipY; r.colorSpace=m.colorSpace;
      r.wrapS=m.wrapS; r.wrapT=m.wrapT; r.uuid=m.uuid;
      r.bones=f.mesh.skeleton?f.mesh.skeleton.bones.length:null; }
    out.rows.push(r); });
  var p=window.WH_DEBUG.getPlayer(), pf=p&&firstMap(p.body);
  if(pf) out.live.playerBody.push(pf.map.uuid);
  var rm=window.WH_DEBUG.getRegionManager(), E=rm.enemies||{};
  Object.keys(E).forEach(function(k){ (E[k]||[]).forEach(function(e){
    var f=firstMap(e.root); if(!f) return;
    var n=e.type==='bandit'?'banditBody':(e.type==='ghoul'?'ghoulBody':null);
    if(n) out.live[n].push(f.map.uuid); }); });
  return out; })()""" % FIRSTMAP

# AC-R4-2 probe: symmetric upload of the 3 template maps, forced render,
# then renderer.info.memory counts.
MEM_JS = """(function(){ %s
  var G=window.WH_GAME, R=G.renderer, A=window.WH_ASSETS, up=0;
  BODIES.forEach(function(n){ var f=firstMap(A.getTemplate(n));
    if(f){ R.initTexture(f.map); up++; } });
  R.render(G.scene,G.camera);
  return {textures:R.info.memory.textures,
          geometries:R.info.memory.geometries, uploaded:up}; })()""" % FIRSTMAP

# AC-R4-3(a) probe: draw each template map.image onto a 512 canvas and
# count distinct levels per channel (+ mod-8 congruence + top-8 levels).
TEXSPACE_JS = """(function(){ %s
  var A=window.WH_ASSETS, out=[];
  BODIES.forEach(function(n){ var f=firstMap(A.getTemplate(n));
    if(!f||!f.map.image){ out.push({name:n, err:'no map'}); return; }
    var cv=document.createElement('canvas'); cv.width=512; cv.height=512;
    var cx=cv.getContext('2d'); cx.imageSmoothingEnabled=false;
    cx.drawImage(f.map.image,0,0,512,512);
    var d=cx.getImageData(0,0,512,512).data, ch=[{},{},{}];
    for(var i=0;i<d.length;i+=4){ for(var c=0;c<3;c++){ var v=d[i+c];
      ch[c][v]=(ch[c][v]||0)+1; } }
    var row={name:n, levels:[], mod8:[], top8:[]};
    for(var c2=0;c2<3;c2++){ var ks=Object.keys(ch[c2]);
      row.levels.push(ks.length);
      var res={}; ks.forEach(function(k){ res[k%%8]=1; });
      row.mod8.push(Object.keys(res).length===1);
      ks.sort(function(a,b){return ch[c2][b]-ch[c2][a];});
      row.top8.push(ks.slice(0,8).map(function(k){return [+k,ch[c2][k]];})); }
    out.push(row); });
  return out; })()""" % FIRSTMAP

# AC-R4-3(b) probe (ONE evaluate): render -> readback; hide player body;
# render -> readback; restore (sanctioned, restored in-evaluate).
SCREEN_JS = """(function(){
  var G=window.WH_GAME, p=window.WH_DEBUG.getPlayer();
  if(!p||!p.body) return null;
  var c=G.renderer.domElement, v=new THREE.Vector3();
  p.body.getWorldPosition(v); v.project(G.camera);
  G.renderer.render(G.scene,G.camera);
  var shown=c.toDataURL('image/png');
  var was=p.body.visible; p.body.visible=false;
  G.renderer.render(G.scene,G.camera);
  var hidden=c.toDataURL('image/png');
  p.body.visible=was;
  G.renderer.render(G.scene,G.camera);
  return {shown:shown, hidden:hidden, vz:v.z, cw:c.width, ch:c.height}; })()"""


def wait_loaded(page, wall=60.0):
    """WH_ASSETS.loadedCount settled (2 equal polls 1s apart) -> count."""
    last, deadline = None, time.time() + wall
    while time.time() < deadline:
        n = page.evaluate("window.WH_ASSETS.loadedCount()")
        if n == last:
            return n
        last = n
        page.wait_for_timeout(1000)
    return last


def config_rewrite_route(ctx, counter):
    """B2 sanctioned measurement-only intervention: serve the WORKTREE
    CONFIG.js with `pixelatedBodies: true` rewritten to false. The
    worktree file is never modified; counter['n'] = rewrite count."""
    with open(os.path.join(REPO_ROOT, "prototype/js/CONFIG.js")) as f:
        src = f.read()
    counter["n"] = src.count("pixelatedBodies: true")
    body = src.replace("pixelatedBodies: true", "pixelatedBodies: false")

    def handler(route):
        counter["served"] = counter.get("served", 0) + 1
        route.fulfill(status=200, body=body,
                      headers={"Content-Type": "application/javascript"})
    ctx.route("**/js/CONFIG.js", handler)
