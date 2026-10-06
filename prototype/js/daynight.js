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

  window.WH_DAYNIGHT = {
    DayNight: DayNight
  };
})();
