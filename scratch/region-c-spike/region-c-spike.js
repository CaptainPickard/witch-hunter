// region-c-spike.js — CC-C1 heightfield spike for Region C (Forest of the Old King).
// THROWAWAY scratch code: nothing in prototype/ imports this. Plain classic script.
// Requires window.THREE from ../../prototype/vendor/three.classic.js (r185).
//
// Layout: CORE (terrain + samplers + stats, DOM-free, also loadable by node via
// module.exports) and DEMO (scene, actor, camera, scripted bench, HUD; browser only).
(function (root) {
  'use strict';
  var THREE = root.THREE;
  if (!THREE) throw new Error('region-c-spike: THREE missing (load three.classic.js first)');

  // ===================================================================== CORE
  // Terrain constants (deterministic: same SEED -> same terrain, A4).
  var SEED = 1337;
  var PLANE = 560, HALF = PLANE / 2;
  var BASE_WAVELENGTH = 45, OCTAVES = 4, LACUNARITY = 2.0, GAIN = 0.45;
  var H_MAX = 5;
  // fBm01 output is remapped [N_LO, N_HI] -> [0, H_MAX] (clamped). Constants are
  // ~p1/p99 of fbm01 over the plane at SEED 1337 (measured once, see SPIKE-LOG.md).
  var N_LO = 0.22, N_HI = 0.79;
  // Spawn pocket: inside FLAT_R the ground is FLAT_H; smoothstep blend out to FLAT_R + FLAT_BLEND.
  var FLAT_R = 25, FLAT_BLEND = 20, FLAT_H = 0.4;
  var S_CANDIDATES = [100, 140, 180];
  var RAY_TOP = 50;

  function now() { return (typeof performance !== 'undefined' ? performance : Date).now(); }

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

  // fBm, normalised to [0, 1]. Per-octave salt + offset so lattices don't align at the origin.
  function fbm01(x, z) {
    var f = 1 / BASE_WAVELENGTH, amp = 1, sum = 0, norm = 0;
    for (var o = 0; o < OCTAVES; o++) {
      sum += amp * valueNoise(x * f + o * 17.13, z * f - o * 9.71, SEED + o * 1013);
      norm += amp;
      f *= LACUNARITY;
      amp *= GAIN;
    }
    return sum / norm;
  }

  function smoothstep(e0, e1, x) {
    var t = (x - e0) / (e1 - e0);
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    return t * t * (3 - 2 * t);
  }

  // Strategy A (ANALYTIC): the continuous height function. Also feeds the mesh vertices.
  function heightA(x, z) {
    var t = (fbm01(x, z) - N_LO) / (N_HI - N_LO);
    var h = H_MAX * (t < 0 ? 0 : t > 1 ? 1 : t);
    var r2 = x * x + z * z, rOut = FLAT_R + FLAT_BLEND;
    if (r2 < rOut * rOut) h = FLAT_H + (h - FLAT_H) * smoothstep(FLAT_R, rOut, Math.sqrt(r2));
    return h;
  }

  var COL_LOW = new THREE.Color(0x2c4424);   // dark moss green
  var COL_HIGH = new THREE.Color(0x8c7b5e);  // light stone brown
  var _col = new THREE.Color();

  // One PlaneGeometry(560, 560, S, S), rotated flat, vertex y = heightA. The cached grid
  // holds exactly the Float32 heights the mesh renders (B / B-TRI read this).
  // PlaneGeometry layout (r185): vertex (ix, iy) at world x = ix*seg - HALF, z = iy*seg - HALF
  // after rotateX(-PI/2); quad split along the (ix, iy+1)-(ix+1, iy) diagonal.
  function buildTerrain(S, material) {
    var t0 = now();
    var geo = new THREE.PlaneGeometry(PLANE, PLANE, S, S);
    geo.rotateX(-Math.PI / 2);
    var pos = geo.attributes.position, n = pos.count, seg = PLANE / S, W = S + 1;
    var grid = new Float32Array(W * W);
    var colors = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      var x = pos.getX(i), z = pos.getZ(i);
      var h = heightA(x, z);
      pos.setY(i, h);
      var ix = Math.round((x + HALF) / seg), iz = Math.round((z + HALF) / seg);
      grid[iz * W + ix] = pos.getY(i); // read back -> identical Float32 to the mesh
      var t = smoothstep(0.3, H_MAX * 0.9, h);
      _col.copy(COL_LOW).lerp(COL_HIGH, t);
      colors[i * 3] = _col.r; colors[i * 3 + 1] = _col.g; colors[i * 3 + 2] = _col.b;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    geo.computeBoundingBox();
    geo.computeBoundingSphere();
    var mesh = new THREE.Mesh(geo, material || new THREE.MeshBasicMaterial());
    mesh.updateMatrixWorld(true);
    return {
      S: S, seg: seg, geo: geo, mesh: mesh, grid: grid,
      verts: n, tris: geo.index.count / 3, buildMs: now() - t0
    };
  }

  // Samplers bound to one terrain record. All take world (x, z), return ground y.
  function makeSamplers(T) {
    var S = T.S, seg = T.seg, g = T.grid, W = S + 1;
    var raycaster = new THREE.Raycaster();
    raycaster.ray.direction.set(0, -1, 0);
    raycaster.far = RAY_TOP + 20;
    var hits = [];

    // Shared cell lookup -> writes into c = [ix, iz, fx, fz].
    var c = [0, 0, 0, 0];
    function cell(x, z) {
      var gx = (x + HALF) / seg, gz = (z + HALF) / seg;
      gx = gx < 0 ? 0 : gx > S ? S : gx;
      gz = gz < 0 ? 0 : gz > S ? S : gz;
      var ix = Math.floor(gx), iz = Math.floor(gz);
      if (ix >= S) ix = S - 1;
      if (iz >= S) iz = S - 1;
      c[0] = ix; c[1] = iz; c[2] = gx - ix; c[3] = gz - iz;
    }

    // Strategy B (GRID): bilinear over the cached vertex heights.
    function grid(x, z) {
      cell(x, z);
      var i = c[1] * W + c[0], fx = c[2], fz = c[3];
      var h00 = g[i], h10 = g[i + 1], h01 = g[i + W], h11 = g[i + W + 1];
      return (h00 + (h10 - h00) * fx) * (1 - fz) + (h01 + (h11 - h01) * fx) * fz;
    }

    // Strategy B-TRI (GRID, triangle-exact): same cached heights, but interpolated over
    // the SAME two triangles the mesh draws (diagonal h01-h10), so it is the rendered surface.
    function gridTri(x, z) {
      cell(x, z);
      var i = c[1] * W + c[0], fx = c[2], fz = c[3];
      var h00 = g[i], h10 = g[i + 1], h01 = g[i + W], h11 = g[i + W + 1];
      if (fx + fz <= 1) return h00 + (h10 - h00) * fx + (h01 - h00) * fz;
      return h11 + (h01 - h11) * (1 - fx) + (h10 - h11) * (1 - fz);
    }

    // Strategy C (RAYCAST): THREE.Raycaster straight down onto the mesh. NaN on miss.
    function raycast(x, z) {
      raycaster.ray.origin.set(x, RAY_TOP, z);
      hits.length = 0;
      raycaster.intersectObject(T.mesh, false, hits);
      return hits.length ? hits[0].point.y : NaN;
    }

    return { A: heightA, B: grid, T: gridTri, C: raycast };
  }

  // Deterministic PRNG for sample points.
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function samplePoints(n) {
    var rnd = mulberry32(SEED), xs = new Float64Array(n), zs = new Float64Array(n);
    var m = HALF - 0.5;
    for (var i = 0; i < n; i++) { xs[i] = (rnd() * 2 - 1) * m; zs[i] = (rnd() * 2 - 1) * m; }
    return { n: n, xs: xs, zs: zs };
  }

  // Sampler comparison as a resumable job (browser: per-frame budget; node: run to end).
  // Reference = raycast C. Errors and per-call cost for A, B, B-TRI; cost for C.
  var SAMPLER_KEYS = ['A', 'B', 'T', 'C'];
  var SAMPLER_NAMES = { A: 'A analytic fBm', B: 'B grid bilinear', T: 'B-TRI grid triangle', C: 'C raycast' };

  function compareJob(T, nPoints, reps) {
    var fns = makeSamplers(T), P = samplePoints(nPoints || 1000), R = reps || 50;
    var ref = new Float64Array(P.n), i = 0, cMs = 0, misses = 0, done = false, result = null;
    function finish() {
      var out = { S: T.S, n: P.n, misses: misses, rows: {} };
      ['A', 'B', 'T'].forEach(function (k) {
        var f = fns[k], maxE = 0, sumE = 0, cnt = 0;
        for (var j = 0; j < P.n; j++) {
          if (isNaN(ref[j])) continue;
          var e = Math.abs(f(P.xs[j], P.zs[j]) - ref[j]);
          if (e > maxE) maxE = e;
          sumE += e; cnt++;
        }
        var sink = 0, t0 = now();
        for (var r = 0; r < R; r++) for (var q = 0; q < P.n; q++) sink += f(P.xs[q], P.zs[q]);
        var us = (now() - t0) * 1000 / (R * P.n);
        out.rows[k] = { max: maxE, mean: sumE / Math.max(1, cnt), us: us, sink: sink };
      });
      out.rows.C = { max: 0, mean: 0, us: cMs * 1000 / P.n };
      out.verdict = verdict(out);
      return out;
    }
    return {
      step: function (budgetMs) {
        if (done) return true;
        var t0 = now();
        while (i < P.n) {
          var a = now();
          ref[i] = fns.C(P.xs[i], P.zs[i]);
          cMs += now() - a;
          if (isNaN(ref[i])) misses++;
          i++;
          if (budgetMs && now() - t0 > budgetMs) break;
        }
        if (i >= P.n) { result = finish(); done = true; }
        return done;
      },
      progress: function () { return i / P.n; },
      result: function () { return result; }
    };
  }

  // Verdict: cheapest strategy whose max |diff vs raycast| <= 0.05 units; fallback order follows.
  var ERR_OK = 0.05;
  function verdict(res) {
    var ok = ['A', 'B', 'T'].filter(function (k) { return res.rows[k].max <= ERR_OK; });
    ok.sort(function (a, b) { return res.rows[a].us - res.rows[b].us; });
    var pick = ok.length ? ok[0] : 'C';
    var order = [pick].concat(['T', 'B', 'A', 'C'].filter(function (k) { return k !== pick; }));
    return { pick: pick, order: order };
  }

  function pct(sorted, q) { return sorted[Math.min(sorted.length - 1, Math.floor(q * (sorted.length - 1)))]; }
  function summarise(arr) {
    var s = Float64Array.from(arr).sort();
    return { n: s.length, p50: pct(s, 0.5), p90: pct(s, 0.9), p99: pct(s, 0.99), max: s[s.length - 1] };
  }

  // Slope distribution (degrees) of the continuous height function, central differences
  // on a regular grid of points inside the plane.
  function slopeStatsAnalytic(step) {
    step = step || 2;
    var eps = 0.05, out = [], RAD = 180 / Math.PI;
    for (var z = -HALF + 1; z <= HALF - 1; z += step) {
      for (var x = -HALF + 1; x <= HALF - 1; x += step) {
        var gx = (heightA(x + eps, z) - heightA(x - eps, z)) / (2 * eps);
        var gz = (heightA(x, z + eps) - heightA(x, z - eps)) / (2 * eps);
        out.push(Math.atan(Math.sqrt(gx * gx + gz * gz)) * RAD);
      }
    }
    return summarise(out);
  }

  // Slope distribution (degrees) of the rendered facets at density S (what the actor walks on).
  function slopeStatsFacets(T) {
    var p = T.geo.attributes.position.array, idx = T.geo.index.array, out = [], RAD = 180 / Math.PI;
    for (var t = 0; t < idx.length; t += 3) {
      var a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
      var ux = p[b] - p[a], uy = p[b + 1] - p[a + 1], uz = p[b + 2] - p[a + 2];
      var vx = p[c] - p[a], vy = p[c + 1] - p[a + 1], vz = p[c + 2] - p[a + 2];
      var nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      var len = Math.sqrt(nx * nx + ny * ny + nz * nz);
      out.push(Math.acos(Math.min(1, Math.abs(ny) / len)) * RAD);
    }
    return summarise(out);
  }

  // Movement constants (stand-in actor).
  var WALK_SPEED = 6, RUN_SPEED = 9;
  // maxStepPerFrame = RUN_SPEED * dt * climbFactor. Per-frame horizontal step is speed*dt,
  // so the guard is a dt-independent slope cap: tan(maxSlope) = climbFactor * RUN_SPEED / speed.
  // Demo default 0.2 -> running caps at ~11.3 deg (blocks ~2.2% of S=140 facets), walking at
  // ~16.7 deg (~0.02%). This terrain tops out ~18 deg, so a production-sane value (0.6 = 31/42 deg)
  // would never fire here; 0.2 keeps the guard observable. Live-tunable with [ ]. See SPIKE-LOG.md.
  var CLIMB_FACTOR = 0.2;

  var CORE = {
    SEED: SEED, PLANE: PLANE, HALF: HALF, H_MAX: H_MAX, S_CANDIDATES: S_CANDIDATES,
    BASE_WAVELENGTH: BASE_WAVELENGTH, OCTAVES: OCTAVES, LACUNARITY: LACUNARITY, GAIN: GAIN,
    N_LO: N_LO, N_HI: N_HI, FLAT_R: FLAT_R, FLAT_BLEND: FLAT_BLEND, FLAT_H: FLAT_H,
    WALK_SPEED: WALK_SPEED, RUN_SPEED: RUN_SPEED, CLIMB_FACTOR: CLIMB_FACTOR, ERR_OK: ERR_OK,
    SAMPLER_KEYS: SAMPLER_KEYS, SAMPLER_NAMES: SAMPLER_NAMES,
    hash2: hash2, fbm01: fbm01, heightA: heightA, buildTerrain: buildTerrain,
    makeSamplers: makeSamplers, samplePoints: samplePoints, compareJob: compareJob,
    slopeStatsAnalytic: slopeStatsAnalytic, slopeStatsFacets: slopeStatsFacets, summarise: summarise,
    now: now
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = CORE;
  root.RCS = CORE;
  if (typeof document === 'undefined') return;

  // ===================================================================== DEMO
  var BENCH_WARMUP_S = 1.0, BENCH_MEASURE_S = 20.0; // 3 densities x ~21 s = ~63 s walk
  var BENCH_WAYPOINTS = [ // cross-hill loop; starts/ends in the spawn pocket
    [0, 0], [60, -40], [140, -120], [210, -30], [150, 90], [60, 170],
    [-60, 200], [-170, 120], [-220, -20], [-140, -150], [-30, -210], [40, -90], [0, 0]
  ];
  var CAM_MIN = 8, CAM_MAX = 24, CAM_CLEAR = 1.5, ACTOR_HALF_H = 0.9;
  var BG = 0xb9c6c4;

  var renderer, scene, camera, material, actor, actorMat, terrain = null, samplers = null;
  var hudEl, resultsEl;
  var sIndex = 1;                   // S = 140 default
  var samplerKey = 'T';             // live sampler (H cycles)
  var climbFactor = CLIMB_FACTOR;
  var keys = {};
  var act = { x: 0, z: 0, heading: 0, blocked: 0, flash: 0, lastDh: 0, lastMax: 0 };
  var cam = { yaw: 0.6, pitch: 0.45, dist: 14 };
  var buildMs = {}, verts = {}, terrTris = {};
  var frameStamps = [], lastT = 0, cpuMs = 0, infoTris = 0, infoCalls = 0;
  var bench = null, benchResults = {}, benchNote = '';
  var cmpQueue = [], cmpJob = null, cmpResults = {}, slopeA = null, slopeF = {};

  function setTerrain(S) {
    if (terrain) { scene.remove(terrain.mesh); terrain.geo.dispose(); }
    terrain = buildTerrain(S, material);
    scene.add(terrain.mesh);
    samplers = makeSamplers(terrain);
    buildMs[S] = terrain.buildMs; verts[S] = terrain.verts; terrTris[S] = terrain.tris;
  }

  // Ground height for the live sampler; raycast misses (off-plane) fall back to A.
  function ground(x, z) {
    var h = samplers[samplerKey](x, z);
    return isNaN(h) ? heightA(x, z) : h;
  }

  function init() {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(2, root.devicePixelRatio || 1));
    renderer.setSize(root.innerWidth, root.innerHeight);
    document.body.appendChild(renderer.domElement);

    scene = new THREE.Scene();
    scene.background = new THREE.Color(BG);
    scene.fog = new THREE.Fog(BG, 50, 190); // plane edge (>=280 from centre at spawn) fades out
    camera = new THREE.PerspectiveCamera(60, root.innerWidth / root.innerHeight, 0.1, 400);

    scene.add(new THREE.HemisphereLight(0xdfe8e4, 0x3a3524, 1.4));
    var sun = new THREE.DirectionalLight(0xfff2dc, 2.0);
    sun.position.set(80, 120, 40);
    scene.add(sun);

    material = new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: 0.95, metalness: 0 });

    actorMat = new THREE.MeshStandardMaterial({ color: 0xd9b45a, roughness: 0.6 });
    actor = new THREE.Group();
    var body = new THREE.Mesh(new THREE.CapsuleGeometry(0.4, 1.0, 4, 10), actorMat);
    var nose = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.18, 0.5), new THREE.MeshStandardMaterial({ color: 0x402818 }));
    nose.position.set(0, 0.3, 0.45);
    actor.add(body); actor.add(nose);
    scene.add(actor);

    hudEl = document.getElementById('hud');
    resultsEl = document.getElementById('results');

    setTerrain(S_CANDIDATES[sIndex]);
    bindInput();
    startBench();
    lastT = now();
    requestAnimationFrame(frame);
  }

  // ------------------------------------------------------------------ input
  function bindInput() {
    root.addEventListener('resize', function () {
      camera.aspect = root.innerWidth / root.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(root.innerWidth, root.innerHeight);
    });
    root.addEventListener('keydown', function (e) {
      if (e.target && e.target.tagName === 'TEXTAREA') return;
      var k = e.key.toLowerCase();
      keys[k] = true;
      if (e.key === 'Shift') keys.shift = true;
      if (k === '1' || k === '2' || k === '3') {
        if (bench) return;
        sIndex = +k - 1;
        setTerrain(S_CANDIDATES[sIndex]);
      } else if (k === 'h') {
        samplerKey = SAMPLER_KEYS[(SAMPLER_KEYS.indexOf(samplerKey) + 1) % SAMPLER_KEYS.length];
      } else if (k === '[') {
        climbFactor = Math.max(0.1, +(climbFactor - 0.05).toFixed(2));
      } else if (k === ']') {
        climbFactor = Math.min(3, +(climbFactor + 0.05).toFixed(2));
      } else if (k === 'b') {
        if (!bench) startBench();
      } else if (k === 'x') {
        if (bench) endBench('skipped by user (X)');
      } else if (k === 'r') {
        act.x = 0; act.z = 0;
      } else if (k === 'm') {
        resultsEl.style.display = resultsEl.style.display === 'block' ? 'none' : 'block';
        resultsEl.value = resultsMarkdown();
      }
    });
    root.addEventListener('keyup', function (e) {
      keys[e.key.toLowerCase()] = false;
      if (e.key === 'Shift') keys.shift = false;
    });
    root.addEventListener('blur', function () { keys = {}; });

    var drag = null, el = renderer.domElement;
    el.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, y: e.clientY }; el.setPointerCapture(e.pointerId); });
    el.addEventListener('pointerup', function () { drag = null; });
    el.addEventListener('pointermove', function (e) {
      if (!drag || bench) return;
      cam.yaw -= (e.clientX - drag.x) * 0.006;
      cam.pitch = Math.max(0.08, Math.min(1.35, cam.pitch + (e.clientY - drag.y) * 0.005));
      drag.x = e.clientX; drag.y = e.clientY;
    });
    el.addEventListener('wheel', function (e) {
      e.preventDefault();
      cam.dist = Math.max(CAM_MIN, Math.min(CAM_MAX, cam.dist + Math.sign(e.deltaY) * 1.0));
    }, { passive: false });

    document.addEventListener('visibilitychange', function () {
      if (document.hidden && bench) bench.invalid = true;
    });
  }

  // ------------------------------------------------------------- movement
  function moveActor(dt) {
    var mx = (keys.d ? 1 : 0) - (keys.a ? 1 : 0);
    var mz = (keys.w ? 1 : 0) - (keys.s ? 1 : 0);
    if (mx || mz) {
      var len = Math.sqrt(mx * mx + mz * mz);
      mx /= len; mz /= len;
      var sy = Math.sin(cam.yaw), cy = Math.cos(cam.yaw);
      // forward = (-sin yaw, -cos yaw), right = (cos yaw, -sin yaw)
      var dx = -sy * mz + cy * mx, dz = -cy * mz - sy * mx;
      var speed = keys.shift ? RUN_SPEED : WALK_SPEED;
      var nx = clampPlane(act.x + dx * speed * dt), nz = clampPlane(act.z + dz * speed * dt);
      var dh = ground(nx, nz) - ground(act.x, act.z);
      var maxStep = RUN_SPEED * dt * climbFactor; // maxStepPerFrame
      act.lastDh = dh; act.lastMax = maxStep;
      act.heading = Math.atan2(dx, dz);
      if (Math.abs(dh) > maxStep) { act.blocked++; act.flash = 0.25; } // move-reject
      else { act.x = nx; act.z = nz; }
    }
  }

  function clampPlane(v) { var m = HALF - 2; return v < -m ? -m : v > m ? m : v; }

  function benchWalk(dt) {
    var wp = BENCH_WAYPOINTS[bench.wp];
    var dx = wp[0] - act.x, dz = wp[1] - act.z, d = Math.sqrt(dx * dx + dz * dz);
    var step = RUN_SPEED * dt;
    if (d <= step) {
      act.x = wp[0]; act.z = wp[1];
      bench.wp = (bench.wp + 1) % BENCH_WAYPOINTS.length;
    } else {
      act.x += dx / d * step; act.z += dz / d * step;
      act.heading = Math.atan2(dx, dz);
    }
    // camera trails the heading: camera sits opposite the facing direction
    var want = act.heading + Math.PI, diff = Math.atan2(Math.sin(want - cam.yaw), Math.cos(want - cam.yaw));
    cam.yaw += diff * Math.min(1, dt * 2.5);
  }

  function updateCamera() {
    var tx = act.x, ty = actor.position.y + 0.6, tz = act.z;
    var cp = Math.cos(cam.pitch);
    var cx = tx + Math.sin(cam.yaw) * cp * cam.dist;
    var cz = tz + Math.cos(cam.yaw) * cp * cam.dist;
    var cyy = ty + Math.sin(cam.pitch) * cam.dist;
    var floor = ground(cx, cz) + CAM_CLEAR;   // never underground
    if (cyy < floor) cyy = floor;
    camera.position.set(cx, cyy, cz);
    camera.lookAt(tx, ty, tz);
  }

  // ---------------------------------------------------------------- bench
  function startBench() {
    bench = { i: 0, t: 0, wp: 0, frames: 0, measT: 0, dts: [], cpu: [], tris: 0, calls: 0, invalid: false };
    act.x = 0; act.z = 0;
    benchNote = '';
    benchResults = {};
    setTerrain(S_CANDIDATES[0]);
  }

  function benchFrame(dt, cpu) {
    bench.t += dt;
    if (bench.t > BENCH_WARMUP_S) {
      bench.frames++; bench.measT += dt; bench.dts.push(dt * 1000); bench.cpu.push(cpu);
      bench.tris = infoTris; bench.calls = infoCalls;
    }
    if (bench.t >= BENCH_WARMUP_S + BENCH_MEASURE_S) {
      var S = S_CANDIDATES[bench.i], ft = summarise(bench.dts), c = summarise(bench.cpu);
      benchResults[S] = {
        fps: bench.frames / bench.measT, low1: 1000 / ft.p99, ftMax: ft.max,
        cpuP50: c.p50, cpuP99: c.p99, tris: bench.tris, calls: bench.calls,
        build: buildMs[S], verts: verts[S], invalid: bench.invalid
      };
      bench.i++;
      if (bench.i >= S_CANDIDATES.length) { endBench('complete'); return; }
      bench.t = 0; bench.frames = 0; bench.measT = 0; bench.dts = []; bench.cpu = [];
      setTerrain(S_CANDIDATES[bench.i]);
    }
  }

  function endBench(note) {
    benchNote = note + (bench && bench.invalid ? ' — TAB WAS HIDDEN, numbers invalid; press B to rerun' : '');
    bench = null;
    sIndex = 1;
    setTerrain(S_CANDIDATES[sIndex]);
    act.x = 0; act.z = 0;
    if (!cmpJob && !Object.keys(cmpResults).length) queueComparisons();
  }

  // ---------------------------------------------------------- comparisons
  // Run after the bench so raycast stalls don't pollute fps. Off-scene meshes per S.
  function queueComparisons() {
    cmpQueue = S_CANDIDATES.slice();
    slopeA = slopeStatsAnalytic(2);
    nextComparison();
  }

  function nextComparison() {
    if (cmpJob && cmpJob.T) cmpJob.T.geo.dispose();
    cmpJob = null;
    if (!cmpQueue.length) return;
    var S = cmpQueue.shift(), T = buildTerrain(S, material);
    slopeF[S] = slopeStatsFacets(T);
    cmpJob = compareJob(T, 1000, 50);
    cmpJob.T = T;
  }

  function stepComparison() {
    if (!cmpJob) return;
    if (cmpJob.step(6)) {
      cmpResults[cmpJob.T.S] = cmpJob.result();
      nextComparison();
    }
  }

  // ------------------------------------------------------------------ HUD
  function f(v, d) { return v === undefined || v === null || isNaN(v) ? '—' : v.toFixed(d); }
  function pad(s, n) { s = String(s); while (s.length < n) s += ' '; return s; }

  function rollingFps(t) {
    frameStamps.push(t);
    while (frameStamps.length && frameStamps[0] < t - 1000) frameStamps.shift();
    return frameStamps.length;
  }

  var hudTimer = 0;
  function drawHud(fps) {
    var S = terrain.S, L = [];
    L.push('<b>CC-C1 HEIGHTFIELD SPIKE</b> · seed ' + SEED + ' · plane ' + PLANE + '²');
    if (bench) {
      L.push('<span class="warn">SCRIPTED WALK BENCH ' + (bench.i + 1) + '/3 · S=' + S + ' · ' +
        f(Math.max(0, BENCH_WARMUP_S + BENCH_MEASURE_S - bench.t), 0) + 's left · X skip</span>');
    } else if (benchNote) {
      L.push('bench: ' + benchNote);
    }
    L.push('');
    L.push('S density   ' + S + '  (keys 1/2/3 → 100/140/180) · seg ' + f(terrain.seg, 2) + 'u');
    L.push('verts       ' + terrain.verts + ' · terrain tris ' + terrain.tris + ' · build ' + f(terrain.buildMs, 1) + ' ms');
    L.push('renderer    tris ' + infoTris + ' · calls ' + infoCalls);
    L.push('fps         ' + fps + ' (rolling 1s) · cpu ' + f(cpuMs, 2) + ' ms/frame' +
      (cmpJob ? ' <span class="warn">(raycast comparison running: fps not representative)</span>' : ''));
    L.push('');
    L.push('actor       (' + f(act.x, 1) + ', ' + f(act.z, 1) + ') y ' + f(actor.position.y - ACTOR_HALF_H, 2) +
      ' · sampler <b>' + SAMPLER_NAMES[samplerKey] + '</b> (H)');
    L.push('step guard  climbFactor ' + f(climbFactor, 2) + ' ([ ]) · run cap ' + f(Math.atan(climbFactor) * 57.2958, 0) +
      '° walk cap ' + f(Math.atan(climbFactor * RUN_SPEED / WALK_SPEED) * 57.2958, 0) + '°');
    L.push('            |Δh| ' + f(Math.abs(act.lastDh), 3) + ' / max ' + f(act.lastMax, 3) + ' · blocked ' + act.blocked);
    L.push('');
    L.push('<b>bench (scripted walk, ' + BENCH_MEASURE_S + 's per S)</b>');
    L.push(pad('S', 5) + pad('fps', 7) + pad('1%low', 7) + pad('cpu50', 7) + pad('cpu99', 7) + pad('tris', 8) + pad('verts', 7) + 'build');
    S_CANDIDATES.forEach(function (s) {
      var r = benchResults[s];
      L.push(pad(s, 5) + (r ? pad(f(r.fps, 1), 7) + pad(f(r.low1, 1), 7) + pad(f(r.cpuP50, 2), 7) + pad(f(r.cpuP99, 2), 7) +
        pad(r.tris, 8) + pad(r.verts, 7) + f(r.build, 1) + 'ms' + (r.invalid ? ' !hidden' : '') : '…'));
    });
    L.push('');
    L.push('<b>samplers vs raycast (1000 pts)</b>' + (cmpJob ? ' · running S=' + cmpJob.T.S + ' ' + f(cmpJob.progress() * 100, 0) + '%' : ''));
    L.push(pad('S', 5) + pad('strategy', 22) + pad('max|d|', 9) + pad('mean|d|', 9) + 'µs/call');
    S_CANDIDATES.forEach(function (s) {
      var r = cmpResults[s];
      if (!r) { L.push(pad(s, 5) + '…'); return; }
      SAMPLER_KEYS.forEach(function (k) {
        var row = r.rows[k];
        L.push(pad(s, 5) + pad(SAMPLER_NAMES[k], 22) + pad(k === 'C' ? 'ref' : f(row.max, 4), 9) +
          pad(k === 'C' ? 'ref' : f(row.mean, 4), 9) + f(row.us, 3) + (r.verdict.pick === k ? '  ◀' : ''));
      });
    });
    var v = cmpResults[140];
    if (v) {
      L.push('<span class="ok">VERDICT (S=140): CC-C4 heightAt = ' + SAMPLER_NAMES[v.verdict.pick] +
        ' · fallback ' + v.verdict.order.slice(1).map(function (k) { return k === 'T' ? 'B-TRI' : k; }).join(' → ') + '</span>');
    }
    if (slopeA) {
      L.push('');
      L.push('slope°  analytic p50/p90/p99/max ' + [slopeA.p50, slopeA.p90, slopeA.p99, slopeA.max].map(function (x) { return f(x, 1); }).join(' / '));
      S_CANDIDATES.forEach(function (s) {
        var q = slopeF[s];
        if (q) L.push('        facets S=' + s + ' ' + [q.p50, q.p90, q.p99, q.max].map(function (x) { return f(x, 1); }).join(' / '));
      });
    }
    L.push('');
    L.push('WASD move · Shift run · drag orbit · wheel zoom · H sampler · [ ] climb · R respawn · B rerun bench · M results md');
    hudEl.innerHTML = L.join('\n');
  }

  function resultsMarkdown() {
    var L = ['### Bench (scripted walk, ' + BENCH_MEASURE_S + 's per S) — ' + (benchNote || 'not finished'),
      '| S | verts | terrain tris | renderer tris | calls | build ms | avg fps | 1% low fps | cpu ms p50 | cpu ms p99 |',
      '|---|---|---|---|---|---|---|---|---|---|'];
    S_CANDIDATES.forEach(function (s) {
      var r = benchResults[s];
      L.push('| ' + s + ' | ' + (verts[s] || '—') + ' | ' + (terrTris[s] || '—') + ' | ' + (r ? r.tris + ' | ' + r.calls + ' | ' + f(r.build, 1) +
        ' | ' + f(r.fps, 1) + ' | ' + f(r.low1, 1) + ' | ' + f(r.cpuP50, 2) + ' | ' + f(r.cpuP99, 2) : '— | — | — | — | — | — | —') + ' |');
    });
    L.push('', '### Samplers vs raycast (browser µs)', '| S | strategy | max diff | mean diff | µs/call |', '|---|---|---|---|---|');
    S_CANDIDATES.forEach(function (s) {
      var r = cmpResults[s];
      if (r) SAMPLER_KEYS.forEach(function (k) {
        L.push('| ' + s + ' | ' + SAMPLER_NAMES[k] + ' | ' + f(r.rows[k].max, 4) + ' | ' + f(r.rows[k].mean, 4) + ' | ' + f(r.rows[k].us, 3) + ' |');
      });
    });
    L.push('', 'UA: ' + navigator.userAgent, 'DPR: ' + renderer.getPixelRatio() + ' · canvas ' + renderer.domElement.width + 'x' + renderer.domElement.height);
    return L.join('\n');
  }

  // ---------------------------------------------------------------- frame
  function frame(t) {
    requestAnimationFrame(frame);
    var rawDt = Math.max(0, (t - lastT) / 1000);
    var dt = Math.min(0.05, rawDt); // sim dt clamped (tab-return spikes); bench uses rawDt
    lastT = t;
    var c0 = now();

    if (bench) benchWalk(dt); else moveActor(dt);
    actor.position.set(act.x, ground(act.x, act.z) + ACTOR_HALF_H, act.z);
    actor.rotation.y = act.heading;
    act.flash = Math.max(0, act.flash - dt);
    actorMat.color.setHex(act.flash > 0 ? 0xd94a3a : 0xd9b45a);
    updateCamera();

    renderer.render(scene, camera);
    infoTris = renderer.info.render.triangles;
    infoCalls = renderer.info.render.calls;
    cpuMs = now() - c0;
    var fps = rollingFps(t);

    if (bench) benchFrame(rawDt, cpuMs);
    else stepComparison();

    hudTimer += dt;
    if (hudTimer > 0.25) { hudTimer = 0; drawHud(fps); }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})(typeof window !== 'undefined' ? window : globalThis);
