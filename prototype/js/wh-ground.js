// wh-ground.js - CC-C4 heightfield ground (R-62.1, io/missions/2026-10-08-cc-c4-heightfield-landing.md).
// The CC-C1 spike CORE (scratch/region-c-spike/region-c-spike.js, playtest-approved)
// productionized: seeded value-noise fBm -> displaced PlaneGeometry mesh + the
// B-TRI sampler that reads the SAME Float32 grid the mesh renders (exact: it
// follows the mesh's per-cell triangle split). Classic script, no modules; load
// AFTER CONFIG.js (index.html). Node can require() it for the self-checks
// (module.exports = CORE) with THREE loaded first.
//
// window.WH_GROUND (gameplay API; only CONFIG regions with terrain.enabled):
//   .has(regionId)            true only for a heightfield region (regionC)
//   .build(regionId[, center]) grid + mesh once, synchronous (~27 ms), cached
//   .heightAt(regionId, x, z) B-TRI ground y at WORLD (x, z); 0 off the disc
//   .footY(regionId, x, z, r) min ground under a prop footprint (props / trees)
//   .mesh(regionId)           the terrain mesh (positioned at (center.x, 0, center.z))
//   .slopeTan(regionId, x, z) CC-C4b: ground steepness (tan) at WORLD (x, z)
//   .notchNear(regionId, x, z, r) / .holdAtNotch(regionId, pos)  CC-C4b rim notch blockers
//   .debugRaycast(regionId, x, z)  DEV ONLY (raycast, 1-3 ms/call, never per-frame)
// WORLD -> GRID mapping: the 560 x 560 plane is centered on the region's disc
// center, so local = (x - center.x, z - center.z) (C: (x, z + 366)); grid
// vertex (ix, iz) sits at local (ix * seg - HALF, iz * seg - HALF).
(function (root) {
  'use strict';
  var THREE = root.THREE;
  if (!THREE) throw new Error('wh-ground: THREE missing (load three.classic.js first)');

  // ===================================================================== CORE
  // Pure functions of a terrain row (deterministic: same row -> same Float32
  // grid). Spike numbers carried exactly: hash lattice, fBm offsets/salts,
  // remap clamp((n - nLo) / (nHi - nLo)) * hMax, smoothstep flats.

  // 32-bit integer hash of a lattice point -> [0, 1).
  function hash2(ix, iz, salt) {
    var h = Math.imul(ix | 0, 0x27d4eb2d) ^ Math.imul(iz | 0, 0x165667b1) ^ Math.imul(salt | 0, 0x9e3779b1);
    h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
    h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }

  // Value noise: hashed lattice values, smoothstep-interpolated.
  function valueNoise(x, z, salt) {
    var xi = Math.floor(x), zi = Math.floor(z);
    var fx = x - xi, fz = z - zi;
    var u = fx * fx * (3 - 2 * fx), v = fz * fz * (3 - 2 * fz);
    var a = hash2(xi, zi, salt), b = hash2(xi + 1, zi, salt);
    var c = hash2(xi, zi + 1, salt), d = hash2(xi + 1, zi + 1, salt);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }

  function smoothstep(e0, e1, x) {
    var t = (x - e0) / (e1 - e0);
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    return t * t * (3 - 2 * t);
  }

  // Height field over PLANE-local (x, z). T = terrain row; flats = LOCAL
  // [{ x, z, r, blend, h }] applied in order (h null = the raw fBm height at
  // the flat's center: a pad that keeps its hill's level); rim = { from, to }
  // fades the height to 0 radially (null = no fade, the spike's field).
  // CC-C4b RIM MOUNTAINS (rim.peakH set; absent = the fade alone, C4's
  // field): a ridge term ADDED on top of the faded fBm - rises over a
  // smoothstep band foot..foot + blend (foot = rim.from +- footJitterM of
  // lump noise), height peakH * (0.75 + 0.45 * lump), lump = 2-octave value
  // noise on the T.seed salt stream (seed + lumpSalt); faded to 0 over the
  // last edgeFadeM before the plane SQUARE's edge (mesh edge flush with the
  // skirt); multiplied by (1 - window) of every notch (LOCAL rows, see
  // notchRows). Zero ridge = exactly C4's height (+ 0 is bit-exact).
  function makeField(T, flats, rim, notches) {
    var SEED = T.seed, BW = T.baseWavelength, OCT = T.octaves, LAC = T.lacunarity, GAIN = T.gain;
    var H_MAX = T.hMax, N_LO = T.nLo, N_HI = T.nHi;
    var MTN = rim && rim.peakH ? rim : null, HALF = T.plane / 2;
    var NOT = notches || [];

    // fBm, normalised to [0, 1]. Per-octave salt + offset so lattices don't align at the origin.
    function fbm01(x, z) {
      var f = 1 / BW, amp = 1, sum = 0, norm = 0;
      for (var o = 0; o < OCT; o++) {
        sum += amp * valueNoise(x * f + o * 17.13, z * f - o * 9.71, SEED + o * 1013);
        norm += amp;
        f *= LAC;
        amp *= GAIN;
      }
      return sum / norm;
    }

    function raw(x, z) {
      var t = (fbm01(x, z) - N_LO) / (N_HI - N_LO);
      return H_MAX * (t < 0 ? 0 : t > 1 ? 1 : t);
    }

    var F = (flats || []).map(function (q) {
      return { x: q.x, z: q.z, r: q.r, rOut: q.r + q.blend,
               h: q.h === null || q.h === undefined ? raw(q.x, q.z) : q.h };
    });

    // CC-C4b notch window in [0, 1]: 1 on the notch axis within halfWidth,
    // smoothstep to 0 by halfWidth + shoulder (outward half-plane only).
    function notchOpen(x, z) {
      var open = 1;
      for (var i = 0; i < NOT.length; i++) {
        var q = NOT[i];
        if (x * q.ux + z * q.uz <= 0) continue;
        var lat = Math.abs(x * q.uz - z * q.ux);
        if (lat < q.hw + q.sh) open *= smoothstep(q.hw, q.hw + q.sh, lat);
      }
      return open;
    }

    // CC-C4b ridge height (0 inside the foot, exactly).
    function ridge(x, z) {
      var rr = Math.sqrt(x * x + z * z);
      if (rr <= MTN.from - MTN.footJitterM) return 0;
      var salt = SEED + MTN.lumpSalt, LW = MTN.lumpWavelength;
      var foot = MTN.from + MTN.footJitterM * (2 * valueNoise(x / LW + 3.7, z / LW - 1.3, salt + 2) - 1);
      if (rr <= foot) return 0;
      var lump = 0.65 * valueNoise(x / LW, z / LW, salt) +
        0.35 * valueNoise(x * 3 / LW + 5.1, z * 3 / LW + 8.3, salt + 1);
      var edge = HALF - Math.max(Math.abs(x), Math.abs(z));
      var r = MTN.peakH * (0.75 + 0.45 * lump) * smoothstep(foot, foot + MTN.blend, rr) *
        smoothstep(0, MTN.edgeFadeM, edge);
      return r === 0 ? 0 : r * notchOpen(x, z);
    }

    // Strategy A (ANALYTIC): the continuous height; also feeds the mesh vertices.
    // noRidge = C4's field (the vertex-color base under the mountains).
    function heightA(x, z, noRidge) {
      var h = raw(x, z);
      if (rim) {
        var rr = Math.sqrt(x * x + z * z);
        if (rr > rim.from) h = h * (1 - smoothstep(rim.from, rim.to, rr));
      }
      if (MTN && !noRidge) h += ridge(x, z);
      for (var i = 0; i < F.length; i++) {
        var q = F[i], dx = x - q.x, dz = z - q.z, r2 = dx * dx + dz * dz;
        // guard kept from the spike: outside rOut the height is untouched
        // (bit-exact - no FLAT_H + (h - FLAT_H) * 1 rounding)
        if (r2 < q.rOut * q.rOut) h = q.h + (h - q.h) * smoothstep(q.r, q.rOut, Math.sqrt(r2));
      }
      return h;
    }

    return { fbm01: fbm01, raw: raw, heightA: heightA, flats: F, T: T,
             ridge: MTN ? ridge : null, notchOpen: notchOpen, notches: NOT };
  }

  // CC-C4b: CONFIG rim.notches (WORLD mouths) -> LOCAL rows for makeField:
  // unit outward axis (ux, uz) from the disc center through the mouth, mouth
  // distance d, window halfWidth hw + shoulder sh (row or rim.notchShoulderM).
  function notchRows(rim, center) {
    if (!rim || !rim.notches) return [];
    return rim.notches.map(function (q) {
      var lx = q.x - center.x, lz = q.z - center.z, d = Math.sqrt(lx * lx + lz * lz);
      return { id: q.id, x: q.x, z: q.z, ux: lx / d, uz: lz / d, d: d, hw: q.halfWidth,
               sh: q.shoulder !== undefined ? q.shoulder : rim.notchShoulderM,
               blocker: !!q.blocker, bedM: q.bedM || 0 };
    });
  }

  // One PlaneGeometry(PLANE, PLANE, S, S), rotated flat, vertex y = heightA.
  // The grid holds exactly the Float32 heights the mesh renders (B-TRI reads
  // it). PlaneGeometry layout (r185): vertex (ix, iy) at local x = ix*seg -
  // HALF, z = iy*seg - HALF after rotateX(-PI/2); quad split along the
  // (ix, iy+1)-(ix+1, iy) diagonal.
  function buildTerrain(field, S, material, now) {
    var T = field.T, PLANE = T.plane, HALF = PLANE / 2, H_MAX = T.hMax;
    var t0 = now ? now() : 0;
    var colLow = new THREE.Color(T.meshColorMoss), colHigh = new THREE.Color(T.meshColorStone);
    var col = new THREE.Color();
    var geo = new THREE.PlaneGeometry(PLANE, PLANE, S, S);
    geo.rotateX(-Math.PI / 2);
    var pos = geo.attributes.position, n = pos.count, seg = PLANE / S, W = S + 1;
    var grid = new Float32Array(W * W);
    var colors = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      var x = pos.getX(i), z = pos.getZ(i);
      var h = field.heightA(x, z);
      pos.setY(i, h);
      var ix = Math.round((x + HALF) / seg), iz = Math.round((z + HALF) / seg);
      grid[iz * W + ix] = pos.getY(i); // read back -> identical Float32 to the mesh
      // CC-C4b stone band: a ridge vertex takes C4's moss->stone lerp of
      // the UNridged height (low faded rim ground = moss foothills), then
      // lerps to stone by smoothstep(stoneFromH, stoneToH, h) (upper slopes).
      // Ridge-free vertices: C4's colour exactly.
      var rg = field.ridge ? field.ridge(x, z) : 0;
      var t = smoothstep(0.3, H_MAX * 0.9, rg > 0 ? field.heightA(x, z, true) : h);
      col.copy(colLow).lerp(colHigh, t);
      if (rg > 0) col.lerp(colHigh, smoothstep(T.rim.stoneFromH, T.rim.stoneToH, h));
      colors[i * 3] = col.r; colors[i * 3 + 1] = col.g; colors[i * 3 + 2] = col.b;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    geo.computeBoundingBox();
    geo.computeBoundingSphere();
    var mesh = new THREE.Mesh(geo, material || new THREE.MeshBasicMaterial());
    return { S: S, seg: seg, half: HALF, geo: geo, mesh: mesh, grid: grid,
             verts: n, tris: geo.index.count / 3, buildMs: now ? now() - t0 : 0 };
  }

  // Strategy B-TRI (the shipped sampler): bilinear-free, interpolated over the
  // SAME two triangles the mesh draws (diagonal h01-h10) = the rendered
  // surface. Local (x, z); clamps to the plane.
  function gridTri(R, x, z) {
    var S = R.S, seg = R.seg, g = R.grid, W = S + 1, HALF = R.half;
    var gx = (x + HALF) / seg, gz = (z + HALF) / seg;
    gx = gx < 0 ? 0 : gx > S ? S : gx;
    gz = gz < 0 ? 0 : gz > S ? S : gz;
    var ix = Math.floor(gx), iz = Math.floor(gz);
    if (ix >= S) ix = S - 1;
    if (iz >= S) iz = S - 1;
    var fx = gx - ix, fz = gz - iz;
    var i = iz * W + ix;
    var h00 = g[i], h10 = g[i + 1], h01 = g[i + W], h11 = g[i + W + 1];
    if (fx + fz <= 1) return h00 + (h10 - h00) * fx + (h01 - h00) * fz;
    return h11 + (h01 - h11) * (1 - fx) + (h10 - h11) * (1 - fz);
  }

  // FNV-1a over the Float32 grid bits (the spike's determinism hash).
  function gridHash(grid) {
    var h = 2166136261, u = new Uint32Array(grid.buffer, grid.byteOffset, grid.length);
    for (var i = 0; i < u.length; i++) h = Math.imul(h ^ u[i], 16777619);
    return (h >>> 0).toString(16);
  }

  // A CONFIG terrain row + its region's disc -> the field the game walks on:
  // world-coord flats (pocket, stone pad) mapped to plane-local.
  function fieldFor(T, center) {
    var flats = [];
    [T.pocket, T.stonePad].forEach(function (q) {
      if (q) flats.push({ x: q.x - center.x, z: q.z - center.z, r: q.r, blend: q.blend, h: q.h });
    });
    return makeField(T, flats, T.rim || null, notchRows(T.rim, center));
  }

  var CORE = {
    hash2: hash2, valueNoise: valueNoise, smoothstep: smoothstep, makeField: makeField,
    fieldFor: fieldFor, buildTerrain: buildTerrain, gridTri: gridTri, gridHash: gridHash,
    notchRows: notchRows
  };

  // ================================================================= RUNTIME
  var cfgById = null;
  function regionCfg(regionId) {
    var CFG = root.WH_CONFIG;
    if (!CFG) return null;
    if (!cfgById) {
      cfgById = {};
      Object.keys(CFG).forEach(function (k) {
        var r = CFG[k];
        if (r && typeof r === 'object' && r.id && r.terrain && r.terrain.enabled) cfgById[r.id] = r;
      });
    }
    return cfgById[regionId] || null;
  }

  var cache = {};   // regionId -> { field, R (grid record), center, radius2, mesh }
  var _ray = null;

  function now() { return (typeof performance !== 'undefined' ? performance : Date).now(); }

  function has(regionId) { return !!regionCfg(regionId); }

  function build(regionId, center) {
    if (cache[regionId]) return cache[regionId];
    var rc = regionCfg(regionId);
    if (!rc) return null;
    var T = rc.terrain, c = center || rc.center || { x: 0, z: 0 };
    var field = fieldFor(T, c);
    var mat = new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true,
      roughness: 0.95, metalness: 0 });
    var R = buildTerrain(field, T.S, mat, now);
    R.mesh.name = 'ground-heightfield';
    R.mesh.position.set(c.x, 0, c.z);
    R.mesh.updateMatrixWorld(true);
    var rad = rc.groundRadius || T.plane / 2;
    var rec = cache[regionId] = { field: field, R: R, center: { x: c.x, z: c.z },
      radius2: rad * rad, mesh: R.mesh, hash: gridHash(R.grid) };
    // determinism assert (DEBUG): a second grid from the same row must hash
    // equal to the CONFIG row (and to this build). Logged once.
    if (T.debugAssert) {
      var R2 = buildTerrain(fieldFor(T, c), T.S, null, null);
      var h2 = gridHash(R2.grid);
      R2.geo.dispose();
      var ok = h2 === rec.hash && (!T.gridHash || T.gridHash === rec.hash);
      console[ok ? 'log' : 'warn']('[WH_GROUND] ' + regionId + ' S=' + T.S + ' grid ' + rec.hash +
        ' rebuild ' + h2 + (T.gridHash ? ' expect ' + T.gridHash : '') + (ok ? ' OK' : ' MISMATCH') +
        ' build ' + R.buildMs.toFixed(1) + 'ms tris ' + R.tris);
    }
    return rec;
  }

  // B-TRI ground y at WORLD (x, z); 0 off the region's disc (and for any
  // region without a heightfield). Builds lazily (save restore / spawn may
  // ask before the region group exists).
  function heightAt(regionId, x, z) {
    var rec = cache[regionId] || build(regionId);
    if (!rec) return 0;
    var lx = x - rec.center.x, lz = z - rec.center.z;
    if (lx * lx + lz * lz > rec.radius2) return 0;
    return gridTri(rec.R, lx, lz);
  }

  // Footprint seat: the lowest ground under a prop's base (center + 4
  // compass points at r), so a trunk on a slope never floats on its downhill
  // side (it sinks into the uphill side instead).
  function footY(regionId, x, z, r) {
    var h = heightAt(regionId, x, z);
    if (!r) return h;
    var a = heightAt(regionId, x + r, z), b = heightAt(regionId, x - r, z);
    var c = heightAt(regionId, x, z + r), d = heightAt(regionId, x, z - r);
    return Math.min(h, a, b, c, d);
  }

  function mesh(regionId) {
    var rec = cache[regionId] || build(regionId);
    return rec ? rec.mesh : null;
  }

  // CC-C4b: ground steepness (tan of the slope angle) at WORLD (x, z): central
  // differences over the B-TRI surface, +-0.5 m (game.js cliff guard).
  function slopeTan(regionId, x, z) {
    var gx = heightAt(regionId, x + 0.5, z) - heightAt(regionId, x - 0.5, z);
    var gz = heightAt(regionId, x, z + 0.5) - heightAt(regionId, x, z - 0.5);
    return Math.sqrt(gx * gx + gz * gz);
  }

  // CC-C4b soft blockers: the blocker notch whose mouth is within r of
  // WORLD (x, z), else null (game.js interact toast + prompt).
  function notchNear(regionId, x, z, r) {
    var rec = cache[regionId] || build(regionId);
    if (!rec) return null;
    var N = rec.field.notches;
    for (var i = 0; i < N.length; i++) {
      var dx = x - N[i].x, dz = z - N[i].z;
      if (N[i].blocker && dx * dx + dz * dz <= r * r) return N[i];
    }
    return null;
  }

  // CC-C4b: hold the player at a blocker notch's rim line (the mouth +
  // rim.notchHoldM along the notch axis) across the whole window + shoulder
  // band; beyond the band the cliff guard holds. Returns true if held.
  function holdAtNotch(regionId, pos) {
    var rec = cache[regionId] || build(regionId);
    if (!rec) return false;
    var N = rec.field.notches, held = false, hold = rec.field.T.rim.notchHoldM || 0;
    for (var i = 0; i < N.length; i++) {
      var q = N[i];
      if (!q.blocker) continue;
      var lx = pos.x - rec.center.x, lz = pos.z - rec.center.z;
      var along = lx * q.ux + lz * q.uz, lat = Math.abs(lx * q.uz - lz * q.ux);
      if (lat < q.hw + q.sh && along > q.d + hold) {
        pos.x -= q.ux * (along - q.d - hold);
        pos.z -= q.uz * (along - q.d - hold);
        held = true;
      }
    }
    return held;
  }

  // DEV ONLY: straight-down raycast on the mesh (the spike's strategy C).
  // Never called from a gameplay path.
  function debugRaycast(regionId, x, z) {
    var rec = cache[regionId] || build(regionId);
    if (!rec) return NaN;
    if (!_ray) { _ray = new THREE.Raycaster(); _ray.ray.direction.set(0, -1, 0); _ray.far = 80; }
    _ray.ray.origin.set(x, 50, z);
    rec.mesh.updateMatrixWorld(true);
    var hits = _ray.intersectObject(rec.mesh, false);
    return hits.length ? hits[0].point.y : NaN;
  }

  root.WH_GROUND = {
    has: has, build: build, heightAt: heightAt, footY: footY, mesh: mesh,
    slopeTan: slopeTan, notchNear: notchNear, holdAtNotch: holdAtNotch,
    debugRaycast: debugRaycast,
    gridHash: function (regionId) { var rec = cache[regionId]; return rec ? rec.hash : null; },
    CORE: CORE
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = CORE;
})(typeof window !== 'undefined' ? window : globalThis);
