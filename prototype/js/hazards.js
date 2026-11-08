// Witch Hunter prototype - CC-H5b Traps as Authored Hazards
// (io/specs/cc-h5b-hazards-spec.md, 2026-11-07; the Tithe Vaults flame vents).
// ONE authored hazard primitive: hand-placed flame vents in regionK that run
// an independent idle -> warn -> blast -> linger phase machine per vent (de-
// synced by construction: vent i starts idle offset i * 1.3 s, C3/C5). Zero
// new assets, zero new materials, zero new lights, zero new draw calls beyond
// the <= 4 pipe clones + <= 8 sprite cards this module owns (C1):
//   - pipe: a CLONE of the loaded okRuinColumn template (WH_ASSETS.instance,
//     the region-manager prop-row grammar), scale 0.55, y -0.1, tint
//     0x3a3a3e charcoal - reads as a floor stub.
//   - cards: TWO sprites per vent from the EXISTING ember texture
//     (particle-ember.png, the game.flameCards texture object - ONE texture
//     ref shared, per-vent material, AdditiveBlending, depthWrite false -
//     the pool-card grammar). Idle eye ALWAYS visible (authored-readable law).
// Light discipline (C4): NO new PointLight anywhere. The wick is a socket row
// handed to game.js computeSockets() via WH_HAZARDS.socketsFor(activeId) -
// rows appear ONLY for vents in warn/blast (noCard: true, color cueHex), so
// the 4-slot pool is never stolen at rest. poolTick is not edited.
// Damage law (C3): the hit uses Player.takeDamage DIRECTLY - a vent is not an
// attacker, so resolveIncomingHit's parry/block path is unreachable by
// construction (no attacker object exists to pass; doc 47: the vault is the
// hazard, not an opponent). i-frames still gate (takeDamage checks iframes +
// state - the spec's "i-frame wins" law). ONE damage event per vent-cycle
// (hitDone, re-armed at each non-blast phase entry) + CFG.hazards.
// hitCooldownSec global gate. Knockback pushes the player OUT to
// staggerMeters from the vent center; the standard rim/prop clamp follows
// next frame through the untouched player update.
// FX: the camera shake reuses the EXISTING triggerShake channel, wired by
// game.js init as game.hazardsFx.shake (disclosed). NO global hit-stop
// channel exists in game.js (grep: none) - the module runs its OWN scoped
// stop clock (S.stopT, CFG.hazards.hitStop seconds), consumed by nothing in
// game.js (disclosed deviation; a global clock-freeze would need a game.js
// loop edit this round does not buy).
// Save law (C5): NO persistence - every region build (re)sets vents to their
// phase-0 idle offsets; dispose drops the module rows only. save.js virgin.
// Journal: the existing WH_JOURNAL.append path is present, but the append
// seeds a toast and persists via capture(); the toast cue already covers the
// first-hit moment, so journal logging is SKIPPED this round (disclosed).
// Exposes window.WH_HAZARDS:
//   init(game)       store the game ref + the fx hooks game.js provides
//   tick(dt)         the per-vent phase machine (regionIds-gated)
//   state()          read-only snapshot { regionId, vents, cooldownT }
//   probeState()     PURE probe readout { regionId, vents: [{ phase, t,
//                    dist }] } - Math.random NEVER runs in this module
//   socketsFor(id)   light-pool socket rows for the ACTIVE region (C4)
//   onRegionBuilt(id, group) / onRegionDisposed(id) - region-manager hooks

(function () {
  'use strict';

  var HG = window.WH_CONFIG.hazards || null;
  var HK = window.WH_CONFIG.regionK && window.WH_CONFIG.regionK.hazards;

  // ---- module state (session-scoped; NOTHING saves) ------------------------
  var S = {
    game: null,
    fx: null,                  // { shake } wired by game.js init
    firstHitDone: false,       // CFG.hazards.firstHitOnly toast gate
    cooldownT: 0,              // global per-player re-hit gate countdown
    stopT: 0,                  // module-scoped hit-stop clock remaining
    regionId: null,            // the active region id last seen on tick
    vents: [],                 // per-vent runtime rows (per region build)
    group: null                // the 'wh-hazards' region-group child
  };

  function dist2(ax, az, bx, bz) {
    var dx = ax - bx, dz = az - bz;
    return Math.sqrt(dx * dx + dz * dz);
  }

  // ease-out cubic (C3 card laws); u clamped 0..1
  function easeOut(u) {
    u = Math.max(0, Math.min(1, u));
    var inv = 1 - u;
    return 1 - inv * inv * inv;
  }

  // ---- build (drains, no new materials) ------------------------------------

  // ONE ember texture for every sprite this module will ever own: the exact
  // game.flameCards texture object (loaded once at boot in game.js). No
  // second texture load ever happens (valspec F3 traverse law).
  function emberTexture() {
    var g = S.game;
    if (g && g.flameCards && g.flameCards.length && g.flameCards[0].material &&
        g.flameCards[0].material.map) return g.flameCards[0].material.map;
    return null;
  }

  function makeCard(tex, hex) {
    var sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: tex, color: hex, blending: THREE.AdditiveBlending,
      transparent: true, depthWrite: false
    }));
    sprite.visible = false;
    return sprite;
  }

  // Build the vent visuals for a regionIds-gated region: the 'wh-hazards'
  // group (a region-group child, so disposeRegion's traverse already frees
  // every clone mesh and sprite material with the region it hangs under).
  // Phase-0 de-sync (C3): vent i starts in idle with offset i * 1.3 s.
  function buildVents(regionId, parentGroup) {
    ventsReset();
    var tex = emberTexture();
    var vents = HK.vents;
    var group = new THREE.Group();
    group.name = 'wh-hazards';
    for (var i = 0; i < vents.length; i++) {
      var v = vents[i];
      // pipe: the approved okRuinColumn stand-in, scale 0.55, y -0.1, tint
      // 0x3a3a3e charcoal (per-row material copies; the template stays clean).
      // instance() yields a stand-in holder while the GLB streams - the same
      // grammar as every region-manager prop row. Ground Y: the flat K disc
      // (groundY 0; no heightfield region is in regionIds).
      var pipe = window.WH_ASSETS ? window.WH_ASSETS.instance('okRuinColumn') : null;
      if (pipe) {
        pipe.scale.setScalar(0.55);
        pipe.position.set(v.x, -0.1, v.z);
        pipe.updateMatrix && pipe.updateMatrix();
        var tint = new THREE.Color(0x3a3a3e);
        pipe.traverse(function (o) {
          if (!o.isMesh || !o.material) return;
          var list = Array.isArray(o.material) ? o.material : [o.material];
          o.material = list.map(function (m) {
            var c = m.clone();
            if (c.color) c.color.multiply(tint);
            return c;
          });
        });
        group.add(pipe);
      }
      var row = {
        cfg: v,
        idle: tex ? makeCard(tex, HK.cardIdleHex) : null,
        warn: tex ? makeCard(tex, HK.cueHex) : null,
        blast: tex ? makeCard(tex, HK.cardBlastHex) : null,
        phase: 'idle',
        t: 0, offset: i * 1.3,            // the de-sync: i * 1.3 s, first build
        hitDone: false, hitT: 0
      };
      if (row.idle) {                     // C1: the always-visible vent eye
        row.idle.material.opacity = 0.35;
        row.idle.scale.set(0.28, 0.28, 1);
        row.idle.position.set(v.x, HK.heightM, v.z);
        row.idle.visible = true;
        group.add(row.idle);
      }
      if (row.warn) {
        row.warn.scale.set(0.28, 0.28, 1);
        row.warn.position.set(v.x, HK.heightM, v.z);
        group.add(row.warn);
      }
      if (row.blast) {
        row.blast.scale.set(HK.blastRadiusM, HK.blastRadiusM, 1);
        row.blast.position.set(v.x, HK.heightM, v.z);
        group.add(row.blast);
      }
      S.vents.push(row);
    }
    S.group = group;
    parentGroup.add(group);
  }

  function ventsReset() {
    S.vents = [];
    S.group = null;
  }

  // ---- region-manager hooks (guarded, +6 lines there; wires game.js too) ----

  // True when regionId runs vents (the build hook's gate; hazards.js loads
  // after CONFIG, so the CFG rows exist - and the group must exist before the
  // first visible frame, hence the direct build here rather than a poll).
  function wantsRegion(regionId) {
    return !!(HG && HK && HG.enabled && HG.regionIds.indexOf(regionId) >= 0);
  }

  function onRegionBuilt(regionId, parentGroup) {
    if (!wantsRegion(regionId) || !parentGroup) return;
    buildVents(regionId, parentGroup);
  }

  function onRegionDisposed(regionId) {
    if (!wantsRegion(regionId)) return;
    // disposeRegion already freed the group's meshes/materials via its
    // traverse (the group was a region-group child) - only module refs die.
    ventsReset();
  }

  // ---- phase machine (C3) ---------------------------------------------------

  var PHASE_NEXT = { idle: 'warn', warn: 'blast', blast: 'linger', linger: 'idle' };
  var PHASE_LEN = { idle: 6.0, warn: 1.5, blast: 0.9, linger: 0.6 };   // re-bound in init

  function setPhase(row, phase) {
    row.phase = phase;
    row.t = 0;
    row.hitDone = false;             // ONE event per cycle: re-arm here
    row.hitT = 0;
  }

  function tickVents(dt) {
    for (var i = 0; i < S.vents.length; i++) {
      var row = S.vents[i];
      if (row.offset > 0) {          // first-build de-sync budget (spent once)
        var use = Math.min(row.offset, dt);
        row.offset -= use;
        dt -= use;
        if (dt <= 0) { applyVisuals(row); continue; }
      }
      row.t += dt;
      while (row.t >= PHASE_LEN[row.phase]) {
        row.t -= PHASE_LEN[row.phase];
        setPhase(row, PHASE_NEXT[row.phase]);
      }
      applyVisuals(row);
      if (row.phase === 'blast') damageCheck(row);
    }
  }

  function applyVisuals(row) {
    var v = row.cfg;
    var p = row.phase, t = row.t;
    // idle: eyes wick (opacity sine, period 2.2 s over 0.30..0.42; C3);
    // the phase clock is the wick's clock (no extra state).
    if (row.idle) {
      var wamp = p === 'idle' ? 0.06 : 0;
      var base = p === 'idle' ? 0.36 : 0.35;
      var wick = base + wamp *
        Math.sin((p === 'idle' ? t : 0) * (Math.PI * 2 / 2.2));
      row.idle.material.opacity = wick;
      row.idle.material.color.setHex(HK.cardIdleHex);
      row.idle.visible = true;
      row.idle.position.set(v.x, HK.heightM, v.z);
    }
    if (row.warn) {
      if (p === 'warn') {
        var k = easeOut(t / PHASE_LEN.warn);
        var s = 0.28 + (HK.warnRadiusM - 0.28) * k;
        row.warn.scale.set(s, s, 1);
        row.warn.material.opacity = 0.35 + (0.85 - 0.35) * k;
        row.warn.material.color.setHex(HK.cueHex);
        row.warn.visible = true;
        row.warn.position.set(v.x, HK.heightM, v.z);
      } else row.warn.visible = false;
    }
    if (row.blast) {
      if (p === 'blast') {
        // blast start: scale = blastRadiusM at once; opacity 0.95 -> 0.55
        var decay = Math.max(0, 1 - t / PHASE_LEN.blast);
        row.blast.scale.set(HK.blastRadiusM, HK.blastRadiusM, 1);
        row.blast.material.opacity = 0.55 + (0.95 - 0.55) * decay;
        row.blast.material.color.setHex(HK.cardBlastHex);
        row.blast.visible = true;
        row.blast.position.set(v.x, HK.heightM, v.z);
      } else row.blast.visible = false;
    }
  }

  // ---- damage law (C3): ONE event per vent-cycle + the global gate ---------

  function damageCheck(row) {
    var g = S.game;
    if (!g || !g.player || g.player.state !== 'alive') return;
    if (row.hitDone || S.cooldownT > 0) return;
    var v = row.cfg;
    var d = dist2(g.player.pos.x, g.player.pos.z, v.x, v.z);
    if (d > HK.radiusM) return;
    row.hitDone = true;              // the cycle's ONE damage event
    S.cooldownT = HG.hitCooldownSec; // global re-hit gate (all vents)
    // DIRECT takeDamage (no attacker object: no parry/block path possible;
    // i-frames + the dead-skip live inside takeDamage - the i-frame law).
    g.player.takeDamage(HK.damage);
    // knockback: OUT along vent->player to staggerMeters from the vent
    // center (the standard clamp follows next frame, untouched path).
    var dx = g.player.pos.x - v.x, dz = g.player.pos.z - v.z;
    var dd = Math.sqrt(dx * dx + dz * dz) || 1;
    g.player.pos.x = v.x + (dx / dd) * HK.staggerMeters;
    g.player.pos.z = v.z + (dz / dd) * HK.staggerMeters;
    // fx: shake = the existing camera-shake channel (wired via game.hazardsFx
    // at init; amplitude stays CONFIG.anim.shake, channel disclosed);
    // hit-stop = the module-scoped clock (S.stopT; no global channel exists).
    S.stopT = HK.hitStop;
    if (S.fx && S.fx.shake) S.fx.shake();
    if (g.inventoryUI && typeof g.inventoryUI.toast === 'function' &&
        !S.firstHitDone && HG.firstHitOnly) {
      S.firstHitDone = true;         // one cue, session-scoped (B2)
      g.inventoryUI.toast(HG.toastText, HK.blastSec);
    }
  }

  // ---- light discipline (C4): socket rows, warn/blast only ------------------

  function socketsFor(regionId) {
    var out = [];
    if (!wantsRegion(regionId) || S.regionId !== regionId) return out;
    for (var i = 0; i < S.vents.length; i++) {
      var row = S.vents[i];
      if (row.phase !== 'warn' && row.phase !== 'blast') continue;
      var inten;
      if (row.phase === 'warn') {
        inten = 2.2 * easeOut(row.t / PHASE_LEN.warn);          // wick 0 -> 2.2
      } else {                                                   // blast peak -> decay
        inten = row.t < PHASE_LEN.blast * 0.5
          ? 2.2 + (3.2 - 2.2) * (row.t / (PHASE_LEN.blast * 0.5))
          : 3.2 - (3.2 - 2.5) * ((row.t - PHASE_LEN.blast * 0.5) /
                                 (PHASE_LEN.blast * 0.5));
      }
      out.push({ id: 'hazardVent#' + i,
        x: row.cfg.x, y: HK.heightM * 0.5, z: row.cfg.z,
        intensity: inten, weight: 1.0, color: HK.cueHex, noCard: true });
    }
    return out;
  }

  // ---- module tick ----------------------------------------------------------

  function tick(dt) {
    if (!S.game || !HG || !HG.enabled) return;
    if (S.cooldownT > 0) S.cooldownT = Math.max(0, S.cooldownT - dt);
    if (S.stopT > 0) S.stopT = Math.max(0, S.stopT - dt);
    var id = S.game.regionManager ? S.game.regionManager.logic.activeId : null;
    S.regionId = id;
    if (!wantsRegion(id)) { if (S.vents.length) ventsReset(); return; }
    if (!S.vents.length) return;   // the build hook owns population
    tickVents(dt);
  }

  // ---- init / readouts ------------------------------------------------------

  function init(game) {
    S.game = game;
    PHASE_LEN = { idle: HK.idleSec, warn: HK.warnSec,
      blast: HK.blastSec, linger: HK.lingerSec };
    if (game.hazardsFx) S.fx = game.hazardsFx;
  }

  function state() {
    return {
      regionId: S.regionId,
      vents: S.vents.map(function (r) {
        return { phase: r.phase, t: r.t, hitDone: r.hitDone, offset: r.offset };
      }),
      cooldownT: S.cooldownT, stopT: S.stopT, firstHitDone: S.firstHitDone
    };
  }

  // PURE readout for probes (C6): per-vent phase + time-in-phase + distance
  // to the player; no Math.random use anywhere in this module.
  function probeState() {
    var g = S.game;
    var px = g && g.player ? g.player.pos.x : null;
    var pz = g && g.player ? g.player.pos.z : null;
    return {
      regionId: S.regionId,
      vents: S.vents.map(function (r) {
        return { phase: r.phase, t: r.t,
          dist: (px === null) ? null : dist2(px, pz, r.cfg.x, r.cfg.z) };
      })
    };
  }

  window.WH_HAZARDS = {
    init: init,
    tick: tick,
    state: state,
    probeState: probeState,
    socketsFor: socketsFor,
    onRegionBuilt: onRegionBuilt,
    onRegionDisposed: onRegionDisposed
  };
})();
