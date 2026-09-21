// Witch Hunter prototype v1 - asset manifest + GLB loading.
// Paths are absolute under the served repo root (server.py serves the repo
// root, so /art-direction/... URLs resolve). Prefer -pixelated variants for
// props; races_regen characters have no pixelated variants (D4b-3), raw mesh
// is accepted for characters.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;

  // ---- Manifest: logical name -> served path --------------------------------
  var MANIFEST = {
    // graveyard props (pixelated variants preferred)
    gravestoneObelisk: '/art-direction/3d/assets/graveyard/gravestone-obelisk-pixelated.glb',
    stoneCrossTilted: '/art-direction/3d/assets/graveyard/stone-cross-tilted-pixelated.glb',
    graveMound: '/art-direction/3d/assets/graveyard/grave-mound-pixelated.glb',
    buriedCoffin: '/art-direction/3d/assets/graveyard/buried-coffin-pixelated.glb',

    // church-kit props + trees
    lanternPost: '/art-direction/3d/assets/church-kit/lantern-post-pixelated.glb',
    deadTree: '/art-direction/3d/assets/church-kit/dead-tree-pixelated.glb',
    rubblePile: '/art-direction/3d/assets/church-kit/rubble-pile-pixelated.glb',
    churchArchway: '/art-direction/3d/assets/church-kit/church-archway-pixelated.glb',
    churchCornerButtress: '/art-direction/3d/assets/church-kit/church-corner-buttress-pixelated.glb',
    churchPewBroken: '/art-direction/3d/assets/church-kit/church-pew-broken-pixelated.glb',

    // characters (races_regen, raw meshes, no pixelated variants exist)
    playerBody: '/art-direction/3d/assets/races_regen/human-hunter-male.glb',
    banditBody: '/art-direction/3d/assets/races_regen/orc-male-warrior.glb',
    ghoulBody: '/art-direction/3d/assets/races_regen/undead-ghoul-male.glb',

    // weapons (pixelated)
    longsword: '/art-direction/3d/assets/weapons/longsword-pixelated.glb'
  };

  // ---- Loading ---------------------------------------------------------------

  var cache = {};      // logical name -> cloned THREE.Group template
  var failed = {};     // logical name -> true (stand-in substituted)
  var loadedCount = 0;

  function makeStandIn(name) {
    // Procedural box/cone stand-in per spec hard constraint 5. Logged.
    console.warn('[WH assets] substitution: procedural stand-in for ' + name);
    failed[name] = true;
    var group = new THREE.Group();
    var mat = new THREE.MeshStandardMaterial({
      color: CFG.assets.standInColor,
      roughness: 0.9,
      metalness: 0.0,
      side: THREE.DoubleSide
    });
    var mesh = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.8, 0.6), mat);
    mesh.name = 'standin-' + name;
    group.add(mesh);
    return group;
  }

  function prepTemplate(group, isPixelated) {
    // Render settings per validated Witch Hunter 3D setup:
    // DoubleSide for safety (R3), NearestFilter on pixelated textures (R2).
    group.traverse(function (obj) {
      if (!obj.isMesh) return;
      obj.castShadow = false;
      obj.receiveShadow = false;
      var mats = Array.isArray(obj.material) ? obj.material : [obj.material];
      mats.forEach(function (m) {
        if (!m) return;
        m.side = THREE.DoubleSide;
        if (m.map) {
          m.map.magFilter = isPixelated ? THREE.NearestFilter : m.map.magFilter;
          m.map.minFilter = isPixelated ? THREE.LinearMipmapLinearFilter : m.map.minFilter;
          m.map.generateMipmaps = true;
          m.map.needsUpdate = true;
        }
        if (m.isMeshStandardMaterial) {
          m.metalness = Math.min(m.metalness, 0.25);  // tame Meshy metalness (POC)
          m.roughness = Math.max(m.roughness, 0.6);
        }
      });
    });
    return group;
  }

  function loadOne(name, path, isPixelated) {
    return new Promise(function (resolve) {
      var loader = new window.WHGLTFLoader();
      var done = false;
      var timer = setTimeout(function () {
        if (!done) { done = true; resolve(makeStandIn(name)); }
      }, CFG.assets.timeoutMs);
      loader.load(path, function (gltf) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        var root = gltf.scene;
        prepTemplate(root, isPixelated);
        cache[name] = root;
        loadedCount++;
        resolve(root);
      }, undefined, function (err) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        console.warn('[WH assets] load failed for ' + name + ' at ' + path + ': ' + err);
        resolve(makeStandIn(name));
      });
    });
  }

  // Preload every manifest entry. Resolves when all settle (failures become
  // stand-ins, never block boot).
  function preloadAll() {
    var jobs = [];
    Object.keys(MANIFEST).forEach(function (name) {
      var path = MANIFEST[name];
      jobs.push(loadOne(name, path, path.indexOf('-pixelated') !== -1));
    });
    return Promise.all(jobs).then(function () {
      console.log('[WH assets] loaded ' + loadedCount + ' assets, ' +
        Object.keys(failed).length + ' stand-ins');
      return cache;
    });
  }

  // Instance a fresh copy from the cache (Scene.clone(true) clones meshes).
  function instance(name) {
    var tmpl = cache[name];
    if (!tmpl) return makeStandIn(name);
    return tmpl.clone(true);
  }

  window.WH_ASSETS = {
    MANIFEST: MANIFEST,
    preloadAll: preloadAll,
    instance: instance,
    isLoaded: function (name) { return !!cache[name]; },
    isFailed: function (name) { return !!failed[name]; },
    loadedCount: function () { return loadedCount; }
  };
})();