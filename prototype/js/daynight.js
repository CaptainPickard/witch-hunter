// Witch Hunter prototype - day/night cycle (C2, io/missions/2026-10-05-cc-c2-daynight.md).
// One clock over CONFIG.dayNight.dayLengthSec: dawn > day > dusk > night
// (phase starts = CONFIG bounds fractions). The first blendFrac of each
// phase smoothsteps from the previous phase row into this one; the rest
// HOLDS the row exactly (hold = straight copy, never a lerp at t=1, so the
// night hold is bit-identical to the approved CONFIG look).
// TUTORIAL LAW: boots DORMANT on startPhase (clock frozen, nothing moves);
// beginCycle() starts dawn and the free-running cycle (C3: first sleep).
// Pure state - game.js applyDayNight() pushes .state into the scene.
// Exposes window.WH_DAYNIGHT:
//   DayNight   constructor (game.js owns the one instance)
//     .tick(dt)       advance (frozen while dormant)
//     .beginCycle()   dormant -> dawn, new day
//     .dormant .day .timeOfDay (0..1) .phase .dayDelta (days this tick)
//     .state          blended look { hemiSky, hemiGround (THREE.Color), ... }
//     .nightMatches   boot check: night row == today's CONFIG values
//     .attachSky(sky, areaId)  C2b WH_SKYPOOL: painted pano layers on the dome
//   SkyPool    the pano layers (ticked from DayNight.tick)

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var D = CFG.dayNight;

  var COLOR_KEYS = ['hemiSkyColor', 'hemiGroundColor', 'lightColor', 'zenithColor',
    'horizonBand', 'horizonGlow', 'discColor', 'discGlowColor'];
  var NUM_KEYS = ['hemiFillMult', 'lightIntensity', 'elevationDeg', 'exposureMult',
    'stars', 'discOpacity'];

  function smooth(t) {
    t = Math.min(1, Math.max(0, t));
    return t * t * (3 - 2 * t);
  }

  // shortest-arc angle lerp in degrees (dusk 250 -> night 0 goes +110)
  function lerpDeg(a, b, t) {
    var d = ((b - a) % 360 + 540) % 360 - 180;
    return a + d * t;
  }

  function makeState() {
    var s = { fog: {} };
    COLOR_KEYS.forEach(function (k) { s[k] = new THREE.Color(); });
    return s;
  }

  // state = row exactly (no arithmetic on the values)
  function copyRow(s, row) {
    var i, k;
    for (i = 0; i < COLOR_KEYS.length; i++) s[COLOR_KEYS[i]].setHex(row[COLOR_KEYS[i]]);
    for (i = 0; i < NUM_KEYS.length; i++) s[NUM_KEYS[i]] = row[NUM_KEYS[i]];
    s.azimuthDeg = row.azimuthDeg;
    for (k in row.fog) {
      var f = row.fog[k], o = s.fog[k] || (s.fog[k] = { color: new THREE.Color(), cemColor: new THREE.Color() });
      o.color.setHex(f.color);
      o.density = f.density;
      o.hasCem = f.cemColor !== undefined;
      if (o.hasCem) { o.cemColor.setHex(f.cemColor); o.cemDensity = f.cemDensity; }
    }
  }

  var tmpA = new THREE.Color(), tmpB = new THREE.Color();
  function lerpRow(s, a, b, t) {
    var i, k;
    for (i = 0; i < COLOR_KEYS.length; i++) {
      k = COLOR_KEYS[i];
      s[k].lerpColors(tmpA.setHex(a[k]), tmpB.setHex(b[k]), t);
    }
    for (i = 0; i < NUM_KEYS.length; i++) {
      k = NUM_KEYS[i];
      s[k] = a[k] + (b[k] - a[k]) * t;
    }
    s.azimuthDeg = lerpDeg(a.azimuthDeg, b.azimuthDeg, t);
    for (k in b.fog) {
      var fa = a.fog[k] || b.fog[k], fb = b.fog[k];
      var o = s.fog[k] || (s.fog[k] = { color: new THREE.Color(), cemColor: new THREE.Color() });
      o.color.lerpColors(tmpA.setHex(fa.color), tmpB.setHex(fb.color), t);
      o.density = fa.density + (fb.density - fa.density) * t;
      o.hasCem = fb.cemColor !== undefined && fa.cemColor !== undefined;
      if (o.hasCem) {
        o.cemColor.lerpColors(tmpA.setHex(fa.cemColor), tmpB.setHex(fb.cemColor), t);
        o.cemDensity = fa.cemDensity + (fb.cemDensity - fa.cemDensity) * t;
      }
    }
  }

  // Boot check: the night row must equal today's approved CONFIG values.
  function verifyNight() {
    var n = D.phases.night, L = CFG.lighting, S = CFG.sky, A = CFG.regionA, B = CFG.regionB;
    var checks = [
      ['hemiSkyColor', n.hemiSkyColor, L.hemiSkyColor],
      ['hemiGroundColor', n.hemiGroundColor, L.hemiGroundColor],
      ['hemiFillMult', n.hemiFillMult, 1],
      ['lightColor', n.lightColor, L.moonColor],
      ['lightIntensity', n.lightIntensity, L.moonIntensity],
      ['azimuthDeg', n.azimuthDeg, L.moonAzimuthDeg],
      ['elevationDeg', n.elevationDeg, L.moonElevationDeg],
      ['exposureMult', n.exposureMult, 1],
      ['fogA.color', n.fog[A.id].color, A.fogColor],
      ['fogA.density', n.fog[A.id].density, A.fogDensity],
      ['fogA.cemColor', n.fog[A.id].cemColor, A.cemeteryFog.color],
      ['fogA.cemDensity', n.fog[A.id].cemDensity, A.cemeteryFog.density],
      ['fogB.color', n.fog[B.id].color, B.fogColor],
      ['fogB.density', n.fog[B.id].density, B.fogDensity],
      ['zenithColor', n.zenithColor, S.zenithColor],
      ['horizonBand', n.horizonBand, S.horizonBand],
      ['horizonGlow', n.horizonGlow, S.horizonGlow],
      ['stars', n.stars, 1],
      ['discColor', n.discColor, S.moonColor],
      ['discGlowColor', n.discGlowColor, S.moonGlowColor],
      ['discOpacity', n.discOpacity, 1]
    ];
    var bad = checks.filter(function (c) { return c[1] !== c[2]; });
    if (bad.length) {
      console.warn('[WH_DAYNIGHT] night row drifts from the approved look:',
        bad.map(function (c) { return c[0] + ' ' + c[1] + ' != ' + c[2]; }).join(', '));
    }
    return bad.length === 0;
  }

  function DayNight() {
    this.dormant = true;
    this.day = 0;                     // 0 = the tutorial's first night; +1 per new day
    this.clock = 0;                   // seconds into the current cycle
    this.bootT = 0;                   // PLAYTEST hatch timer (autoBeginSec)
    this.dayDelta = 0;
    this.phase = D.startPhase;
    this.timeOfDay = D.bounds[D.startPhase];
    this.state = makeState();
    this.nightMatches = verifyNight();
    copyRow(this.state, D.phases[D.startPhase]);
  }

  // dormant -> dawn. A new day (C3: rest/sleep = morning).
  DayNight.prototype.beginCycle = function () {
    if (!this.dormant) return;
    this.dormant = false;
    this.clock = 0;
    this.day++;
  };

  DayNight.prototype.phaseAt = function (f) {
    var cur = D.order[0];
    for (var i = 0; i < D.order.length; i++) {
      if (f >= D.bounds[D.order[i]]) cur = D.order[i];
    }
    return cur;
  };

  DayNight.prototype.tick = function (dt) {
    this.dayDelta = 0;
    if (this.dormant) {
      // !!! PLAYTEST-ONLY HATCH (C3 deletes): auto-begin after autoBeginSec
      if (D.autoBeginSec > 0) {
        this.bootT += dt;
        if (this.bootT >= D.autoBeginSec) this.beginCycle();
      }
      if (this.dormant) return;       // frozen: state stays the startPhase row
      dt = 0;                         // the cycle starts at exactly dawn this frame
    }
    var len = D.dayLengthSec;
    this.clock += dt;
    this.dayDelta = dt / len;
    while (this.clock >= len) { this.clock -= len; this.day++; }
    var f = this.clock / len;
    this.timeOfDay = f;
    var ph = this.phaseAt(f);
    this.phase = ph;
    var idx = D.order.indexOf(ph);
    var prev = D.order[(idx + D.order.length - 1) % D.order.length];
    var start = D.bounds[ph];
    var end = idx + 1 < D.order.length ? D.bounds[D.order[idx + 1]] : 1;
    var u = (f - start) / (end - start);
    var w = smooth(u / D.blendFrac);
    if (w >= 1) copyRow(this.state, D.phases[ph]);
    else lerpRow(this.state, D.phases[prev], D.phases[ph], w);
  };

  // ---- C2b WH_SKYPOOL: painted dome pano layers ------------------------------
  // (io/missions/2026-10-06-cc-c2b-skydome-pools.md) Two inside-out spheres
  // just under the gradient dome paint the phase panos (CONFIG.dayNight.pools).
  // Layer A holds the current pano at opacity 1; on phase enter layer B takes
  // the new phase's pano and fades in over that phase's blendFrac window (the
  // lighting's own smoothstep), then A := B and B idles. The gradient dome
  // stays the UNDERLAY until a pano is live (never a black sky) and returns if
  // none is; the moon/sun disc sprites retire while panos show. The live star
  // Points keep compositing over the paint (applyDayNight drives them).
  // Lighting is untouched: this only paints the dome.
  var P = D.skyPool;

  function panoGeometry(radius) {
    var g = new THREE.SphereGeometry(radius, 64, 32);
    var uv = g.attributes.uv;
    for (var i = 0; i < uv.count; i++) {
      // u flipped: seen from inside, the pano reads left-to-right unmirrored.
      // v: zenith = top edge, horizon = bottom edge; below the horizon
      // repeats the horizon row (ClampToEdge) under the ground and fog.
      uv.setXY(i, 1 - uv.getX(i), Math.max(0, (uv.getY(i) - 0.5) * 2));
    }
    return g;
  }

  function panoLayer(geo, order) {
    var m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
      side: THREE.BackSide, depthWrite: false, fog: false, transparent: true,
      toneMapped: false, opacity: 0
    }));
    m.renderOrder = order;            // under the stars (-9), over the gradient dome
    m.rotation.y = P.yawDeg * Math.PI / 180;
    m.visible = false;
    return m;
  }

  function setupPanoTex(tex) {
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 1;
    tex.wrapS = THREE.RepeatWrapping;    // seam-fixed: wraps clean at u 0/1
    tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.minFilter = THREE.LinearMipmapLinearFilter;   // pixelation is baked in
    tex.generateMipmaps = true;
    tex.needsUpdate = true;
  }

  function resolvePano(rel) {
    return window.WH_ASSETS ? window.WH_ASSETS.resolveUrl(rel) : rel;
  }

  // blend weight of the current phase (same math as DayNight.tick)
  function phaseBlend(dn) {
    var idx = D.order.indexOf(dn.phase);
    var start = D.bounds[dn.phase];
    var end = idx + 1 < D.order.length ? D.bounds[D.order[idx + 1]] : 1;
    return smooth((dn.timeOfDay - start) / (end - start) / D.blendFrac);
  }

  function SkyPool(sky, dn, areaId) {
    var geo = panoGeometry(CFG.sky.domeRadius * 0.99);
    this.sky = sky;
    this.dn = dn;
    this.area = areaId;
    this.dome = null;                 // the gradient dome mesh (underlay, never disposed)
    var self = this;
    sky.group.children.forEach(function (o) { if (o.material === sky.domeMat) self.dome = o; });
    this.a = panoLayer(geo, -9.8);
    this.b = panoLayer(geo, -9.7);
    sky.group.add(this.a);
    sky.group.add(this.b);
    this.aUrl = null;
    this.cache = {};                  // url -> { tex, ready, failed }
    this.fade = null;                 // B fade-in { url, mode: 'phase' | 'time', t }
    this.phase = dn.phase;
    this.retarget('time');            // dormant night pano loads at boot
  }

  SkyPool.prototype.variantUrl = function (phase) {
    return D.pools[phase][0];
  };

  SkyPool.prototype.request = function (url) {
    var e = this.cache[url];
    if (e) return e;
    e = this.cache[url] = { tex: null, ready: false, failed: false };
    new THREE.TextureLoader().load(resolvePano(url), function (tex) {
      setupPanoTex(tex);
      e.tex = tex;
      e.ready = true;
    }, undefined, function (err) {
      e.failed = true;
      console.warn('[WH_SKYPOOL] ' + url + ' failed (' + err + '): keeping the previous sky');
    });
    return e;
  };

  // point B at the current phase's pano. mode 'phase' fades over the
  // blendFrac window; 'time' over areaFadeSec.
  SkyPool.prototype.retarget = function (mode) {
    var url = this.variantUrl(this.phase);
    if (this.fade) {
      if (this.fade.url === url) return;
      // a fade still running: keep it if mostly in, else drop it
      if (this.b.material.opacity >= 0.5) this.commit();
      else this.dropFade();
    }
    if (url === this.aUrl) return;
    this.fade = { url: url, mode: mode, t: 0 };
    this.request(url);
  };

  SkyPool.prototype.commit = function () {
    var a = this.a.material, b = this.b.material;
    if (a.map !== b.map) { a.map = b.map; a.needsUpdate = true; }
    a.opacity = 1;
    this.a.visible = true;
    this.aUrl = this.fade.url;
    this.dropFade();
  };

  SkyPool.prototype.dropFade = function () {
    this.b.material.opacity = 0;
    this.b.visible = false;
    this.fade = null;
  };

  SkyPool.prototype.tick = function (dt) {
    var dn = this.dn;
    if (dn.phase !== this.phase) {
      this.phase = dn.phase;
      this.retarget('phase');
    }
    var f = this.fade;
    if (f) {
      var e = this.cache[f.url];
      if (e.failed) this.dropFade();          // previous pano (or gradient) stays
      else if (e.ready) {
        var b = this.b.material;
        if (b.map !== e.tex) { b.map = e.tex; b.needsUpdate = true; }
        f.t += dt;
        var w = Math.min(1, f.t / P.areaFadeSec);
        if (f.mode === 'phase' && this.aUrl && !dn.dormant) w = Math.min(w, phaseBlend(dn));
        if (w >= 1) this.commit();
        else { b.opacity = w; this.b.visible = true; }
      }
    }
    // underlay law: gradient dome only while no pano covers the sky; disc
    // sprites retire whenever a pano shows (no double moon)
    var live = this.a.visible && !!this.a.material.map;
    var any = live || this.b.visible;
    if (this.dome) this.dome.visible = !live;
    this.sky.core.visible = !any;
    this.sky.glow.visible = !any;
  };

  // game.js boot hook: build the pano layers on the sky rig
  DayNight.prototype.attachSky = function (sky, areaId) {
    this.sky = new SkyPool(sky, this, areaId);
  };

  var coreTick = DayNight.prototype.tick;
  DayNight.prototype.tick = function (dt) {
    coreTick.call(this, dt);
    if (this.sky) this.sky.tick(dt);
  };

  window.WH_DAYNIGHT = {
    DayNight: DayNight,
    SkyPool: SkyPool                  // WH_SKYPOOL
  };
})();
