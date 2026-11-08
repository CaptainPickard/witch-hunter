// CC-LS1 (doc 61 P1-1): blob contact shadows - one shared geometry+texture,
// pooled meshes riding actor ground (pos.y) un-bobbed; fade+shrinks on lift.
// IIFE, 'use strict', ES5. One global (window.WH_SHCONTACTS). No allocations
// per frame after init (P1-8 pool law): the pool is built ONCE inside init.
window.WH_SHCONTACTS = (function () {
  'use strict';

  var _geom = null;      // one shared CircleGeometry(1, 16)
  var _tex = null;       // one radial CanvasTexture (cfg.textureSize)
  var _mat = null;       // one shared MeshBasicMaterial (all pooled meshes)
  var _scene = null;
  var _cfg = null;
  var _pool = [];        // [{ mesh, busy, owner, radius }, ...] fixed order
  var _warned = false;   // at most ONE console.warn per pool lifetime

  // Black core -> transparent edge, ~0.55 alpha at half radius, linear
  // falloff. Two linear segments: 1 at center -> 0.55 at r=R/2 -> 0 at r=R.
  // (1 - r/R) shape; carries the 0.55 half-radius value (A-1 texture law).
  function makeRadialTexture(size) {
    var canvas = (typeof document !== 'undefined' && document.createElement)
      ? document.createElement('canvas') : null;
    var canvasRendered = false;
    if (canvas) {
      canvas.width = size;
      canvas.height = size;
      var ctx = canvas.getContext('2d');
      var img = ctx.createImageData(size, size);
      var data = img.data;
      var r = size / 2;
      for (var y = 0; y < size; y++) {
        for (var x = 0; x < size; x++) {
          var dx = (x + 0.5) - r;
          var dy = (y + 0.5) - r;
          var dist = Math.sqrt(dx * dx + dy * dy) / r;
          var a;
          if (dist >= 1) {
            a = 0;
          } else if (dist <= 0.5) {
            a = 1 - 0.9 * dist;          // 1 -> 0.55 over the inner half
          } else {
            a = 1.1 * (1 - dist);        // 0.55 -> 0 linear to the edge
          }
          var i = (y * size + x) * 4;
          data[i] = 0;                   // black core, zero color fill
          data[i + 1] = 0;
          data[i + 2] = 0;
          data[i + 3] = Math.max(0, Math.min(255, Math.round(a * 255)));
        }
      }
      ctx.putImageData(img, 0, 0);
      canvasRendered = true;
    }
    var canvasTex = null;   // one CanvasTexture singleton across the pool
    if (canvasRendered) canvasTex = new THREE.CanvasTexture(canvas);
    // Non-DOM context (stubbed validator env): no canvas is available and
    // the CanvasTexture stub takes the size read only.
    if (!canvasTex) canvasTex = new THREE.CanvasTexture(size);
    return canvasTex;
  }

  function init(scene, cfg) {
    if (_pool.length) return;          // idempotent: pool built ONCE
    _scene = scene;
    _cfg = cfg;
    _geom = new THREE.CircleGeometry(1, 16);
    _tex = makeRadialTexture(cfg.textureSize);
    _mat = new THREE.MeshBasicMaterial({
      color: 0x000000,
      map: _tex,
      transparent: true,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -2,
      polygonOffsetUnits: -2
    });
    for (var i = 0; i < cfg.poolSize; i++) {
      var mesh = new THREE.Mesh(_geom, _mat);
      mesh.castShadow = false;
      mesh.receiveShadow = false;
      mesh.rotation.x = -Math.PI / 2;
      mesh.visible = false;
      _pool.push({ mesh: mesh, busy: false, owner: null, radius: 0 });
    }
    _warned = false;
  }

  // Radius resolution order (A-1 attach): explicit radius ->
  // (WH_ASSETS.getMeta(bodyName)||{}).width * 0.5 * (scale||1) -> radiusBase.
  // No meta loaded yet (stand-in) -> radiusBase fallback.
  function resolveRadius(cfg, opts) {
    if (opts && typeof opts.radius === 'number' && opts.radius > 0) {
      return opts.radius;
    }
    if (opts && opts.bodyName && window.WH_ASSETS &&
        typeof window.WH_ASSETS.getMeta === 'function') {
      var meta = window.WH_ASSETS.getMeta(opts.bodyName);
      if (meta && typeof meta.width === 'number' && meta.width > 0) {
        return meta.width * 0.5 * (opts.scale || 1);
      }
    }
    return cfg.radiusBase;
  }

  function attach(owner, opts) {
    if (!owner || !owner.root || !_pool.length) return null;
    // Idempotent: re-attach of the same owner = no-op, second opts ignored.
    for (var i = 0; i < _pool.length; i++) {
      if (_pool[i].busy && _pool[i].owner === owner) return _pool[i];
    }
    var slot = null;
    for (var j = 0; j < _pool.length; j++) {
      if (!_pool[j].busy) { slot = _pool[j]; break; }
    }
    if (!slot) {
      // Exhaustion = silent skip + at most ONE console.warn ever (P1-8).
      if (!_warned) {
        console.warn('CC-LS1: contact-shadow pool exhausted');
        _warned = true;
      }
      return null;
    }
    slot.busy = true;
    slot.owner = owner;
    slot.radius = resolveRadius(_cfg, opts);
    slot.mesh.visible = true;
    _scene.add(slot.mesh);
    return slot;
  }

  function releaseSlot(slot) {
    slot.busy = false;
    slot.owner = null;
    slot.radius = 0;
    slot.mesh.visible = false;
    _scene.remove(slot.mesh);   // freed blob leaves the scene (park detached)
  }

  function update() {
    if (!_pool.length) return;
    var maxLift = _cfg.maxLift;
    var minScale = _cfg.minScale;
    var maxOpacity = _cfg.maxOpacity;
    var groundOffset = _cfg.groundOffset;
    for (var i = 0; i < _pool.length; i++) {
      var slot = _pool[i];
      if (!slot.busy) continue;
      var owner = slot.owner;
      // Freed every tick: region swap / despawn -> parent gone (A-1 law).
      if (!owner || !owner.root || owner.root.parent === null) {
        releaseSlot(slot);
        continue;
      }
      var root = owner.root;
      var p = owner.pos;
      // Ground of the TICK: pos-anchored when owner.pos exists (CC-C5 law),
      // else the root's y. Never read from body bob (A-6).
      var groundY = (p && typeof p.y === 'number') ? p.y : root.position.y;
      var lift = Math.max(0, root.position.y - groundY);
      var t = 1 - lift / maxLift;
      var k = (t < 0) ? 0 : (t > 1) ? 1 : t;
      slot.mesh.material.opacity = maxOpacity * k;
      slot.mesh.position.x = root.position.x;   // x/z track the root,
      slot.mesh.position.z = root.position.z;   // never yawed
      slot.mesh.position.y = groundY + groundOffset;
      var s = slot.radius * (minScale + (1 - minScale) * k);
      slot.mesh.scale.set(s, s, 1);   // per-actor sizing via mesh.scale only
    }
  }

  // Explicit release, exported for tests only (no production caller).
  function detach(owner) {
    if (!owner) return;
    for (var i = 0; i < _pool.length; i++) {
      if (_pool[i].busy && _pool[i].owner === owner) {
        releaseSlot(_pool[i]);
        return;
      }
    }
  }

  return {
    init: init,
    attach: attach,
    update: update,
    detach: detach
  };
})();
