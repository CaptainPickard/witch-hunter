// Witch Hunter prototype - gather nodes (stage 2, 2026-10-05).
// Static interactable nodes from CONFIG.regionA/regionB .nodes, typed by
// CONFIG.gather.nodeTypes. E (game.js) harvests the nearest READY node in
// the active region within interactRadius; the node goes dormant and
// respawns on its type's timer (CONFIG.gather.economy - playtest seconds
// now, real day / week later). Visibility follows the active region, like
// WH_INVENTORY.WorldItems.
// Visual: a placeholder clump on the ground (later bush/grass art) and, ONLY
// while CONFIG.gather.playtestGlow is true, an unlit bobbing marker above
// ready nodes. No PointLights here - the light budget is fixed.
// Exposes window.WH_GATHER = { NodeManager, defs (= CONFIG.gather.nodeTypes) }.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var G = CFG.gather;

  // Mesh sets shared per node type (geometry + materials never disposed).
  function buildTypeKit(def) {
    var base = new THREE.Color(def.glowColor).multiplyScalar(G.base.colorMult);
    return {
      baseGeo: new THREE.DodecahedronGeometry(1, 0),
      baseMat: new THREE.MeshLambertMaterial({ color: base, flatShading: true }),
      markerGeo: new THREE.OctahedronGeometry(1, 0),
      markerMat: new THREE.MeshBasicMaterial({ color: def.glowColor })   // unlit, fogged (faint at range)
    };
  }

  function NodeManager(scene, regions) {
    this.scene = scene;
    this.nodes = [];
    this.pools = {};                  // 'regionId:type' -> [{ x, z }] placement pool
    this.clock = 0;                   // playtest game clock (s)
    this.kits = {};
    var self = this;
    Object.keys(G.nodeTypes).forEach(function (t) {
      self.kits[t] = buildTypeKit(G.nodeTypes[t]);
    });
    Object.keys(regions).forEach(function (rid) {
      var list = regions[rid].cfg.nodes || [];
      for (var i = 0; i < list.length; i++) {
        var n = list[i];
        if (!G.nodeTypes[n.type]) {
          console.warn('[gather] unknown node type', n.type, 'in', rid);
          continue;
        }
        var key = rid + ':' + n.type;
        (self.pools[key] = self.pools[key] || []).push({ x: n.x, z: n.z });
        self.nodes.push(self.makeNode(rid, n.type, n.x, n.z));
      }
    });
  }

  NodeManager.prototype.makeNode = function (regionId, type, x, z) {
    var def = G.nodeTypes[type];
    var kit = this.kits[type];
    var s = def.scale || 1;
    var holder = new THREE.Group();
    holder.position.set(x, 0, z);
    holder.rotation.y = Math.random() * Math.PI * 2;
    var body = new THREE.Group();     // fades (scale + sink) on harvest / respawn
    holder.add(body);
    var clump = new THREE.Mesh(kit.baseGeo, kit.baseMat);
    clump.scale.set(G.base.radius * s, G.base.height * s, G.base.radius * s);
    clump.position.y = G.base.height * s * 0.5;
    body.add(clump);
    var marker = null;
    if (G.playtestGlow) {
      marker = new THREE.Mesh(kit.markerGeo, kit.markerMat);
      marker.scale.setScalar(G.marker.size * s);
      body.add(marker);
    }
    this.scene.add(holder);
    return {
      type: type, regionId: regionId, x: x, z: z,
      state: 'ready',                 // 'ready' | 'dormant'
      readyAt: 0,                     // economy clock time the node returns
      fade: 1,                        // 0 = gone, 1 = fully shown
      phase: Math.random() * Math.PI * 2,
      mesh: holder, body: body, marker: marker
    };
  };

  // Economy clock: playtest = accumulated game seconds; real = wall clock.
  NodeManager.prototype.now = function () {
    return G.economy.mode === 'real' ? Date.now() / 1000 : this.clock;
  };

  NodeManager.prototype.respawnDelay = function (def) {
    var base = G.economy.mode === 'real'
      ? G.economy.realSec[def.rarity || 'common'] : def.respawnSec;
    var j = (G.respawnJitterPct || 0) / 100;
    return base * (1 + (Math.random() * 2 - 1) * j);
  };

  // Nearest READY node of regionId within radius of (x, z).
  NodeManager.prototype.nearestReady = function (x, z, radius, regionId) {
    var best = null, bestD2 = radius * radius;
    for (var i = 0; i < this.nodes.length; i++) {
      var n = this.nodes[i];
      if (n.state !== 'ready' || n.regionId !== regionId) continue;
      var dx = n.x - x, dz = n.z - z;
      var d2 = dx * dx + dz * dz;
      if (d2 <= bestD2) { bestD2 = d2; best = n; }
    }
    return best;
  };

  // inventory.addItem the whole yield; a partial fit is taken back out and
  // refused (node stays ready). Returns { ok, itemId, count, bonus }.
  // L1 Luck: bonusChance (0..1, game.js passes WH_LEVEL Luck) rolls ONE
  // extra unit after the full yield landed - explicit Math.random, kept only
  // if it fits (never refuses the harvest).
  NodeManager.prototype.harvest = function (node, inventory, bonusChance) {
    var y = G.nodeTypes[node.type].yield;
    var added = inventory.addItem(y.id, y.count);
    if (added < y.count) {
      if (added > 0) inventory.removeItem(y.id, added);
      return { ok: false, itemId: y.id, count: 0, bonus: 0 };
    }
    var bonus = bonusChance > 0 && Math.random() < bonusChance ? inventory.addItem(y.id, 1) : 0;
    node.state = 'dormant';
    node.readyAt = this.now() + this.respawnDelay(G.nodeTypes[node.type]);
    return { ok: true, itemId: y.id, count: y.count + bonus, bonus: bonus };
  };

  // Real-game reshuffle: move to a random pool spot no other node of the
  // pool occupies (own spot included, so a full pool keeps it in place).
  NodeManager.prototype.reshuffle = function (node) {
    var pool = this.pools[node.regionId + ':' + node.type] || [];
    var free = [];
    for (var i = 0; i < pool.length; i++) {
      var p = pool[i], used = false;
      for (var k = 0; k < this.nodes.length && !used; k++) {
        var o = this.nodes[k];
        used = o !== node && o.regionId === node.regionId && o.type === node.type &&
               o.x === p.x && o.z === p.z;
      }
      if (!used) free.push(p);
    }
    if (!free.length) return;
    var pick = free[Math.floor(Math.random() * free.length)];
    node.x = pick.x;
    node.z = pick.z;
    node.mesh.position.set(pick.x, 0, pick.z);
  };

  NodeManager.prototype.update = function (dt, activeRegionId) {
    this.clock += dt;
    var now = this.now();
    var fadeStep = dt / Math.max(0.001, G.fadeSec);
    var M = G.marker;
    for (var i = 0; i < this.nodes.length; i++) {
      var n = this.nodes[i];
      if (n.state === 'dormant' && now >= n.readyAt) {
        if (G.economy.reshuffleOnRespawn) this.reshuffle(n);
        n.state = 'ready';
      }
      n.fade = Math.max(0, Math.min(1, n.fade + (n.state === 'ready' ? fadeStep : -fadeStep)));
      var shown = n.regionId === activeRegionId && n.fade > 0;
      n.mesh.visible = shown;
      if (!shown) continue;
      n.body.scale.setScalar(n.fade);
      n.body.position.y = -0.15 * (1 - n.fade);
      if (n.marker) {
        var s = G.nodeTypes[n.type].scale || 1;
        var t = this.clock;
        n.marker.position.y = M.height * s + M.bobAmp * Math.sin(2 * Math.PI * M.bobHz * t + n.phase);
        var pulse = M.pulseMin + (1 - M.pulseMin) * (0.5 + 0.5 * Math.sin(2 * Math.PI * M.pulseHz * t + n.phase));
        n.marker.scale.setScalar(M.size * s * pulse);
        n.marker.rotation.y = t * 0.8 + n.phase;
      }
    }
  };

  window.WH_GATHER = { NodeManager: NodeManager, defs: G.nodeTypes };
})();
