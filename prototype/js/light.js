// Witch Hunter prototype - earned player light (light radius order, 10-05).
// window.WH_PlayerLight: the player has NO intrinsic light. Light comes only
// from what a hand holds:
//   1. an equipped item with a CONFIG.items[id].light stat (torch, stage 2)
//   2. else a caster hand whose CURRENT binding is a spell with a
//      CONFIG.spell[id].light block (firebolt yes, radiance null)
// plus a small fixed pool of in-flight projectile lights
// (CONFIG.spell[id].projectileLight). Radiance's cast follow-light
// (game.radiances) is a separate system and never touched here.
// Every light is created ONCE at boot and only its intensity goes to 0 when
// off: a scene light-count change recompiles every lit material (M-19).
// IIFE + window globals, no ES modules (prototype convention).

(function () {
  'use strict';

  var HANDS = ['right', 'left'];

  function cfg() { return window.WH_CONFIG; }

  // Light block for a hand ('right' / 'left'), or null.
  function handLightDef(player, hand) {
    var C = cfg();
    var id = player.hands ? player.hands[hand] : null;
    var item = id ? C.items[id] : null;
    if (!item || item.kind !== 'caster') return null;
    var sid = player.getBoundSpellId(hand);
    var S = sid ? C.spell[sid] : null;
    return S && S.light ? S.light : null;
  }

  // The R2 lantern's deterministic two-sine wobble (no Math.random), +-pct
  // of intensity, game-time via performance.now. phase separates lights so
  // two hands do not pulse in lockstep.
  function flicker(base, pct, t, phase) {
    if (!pct) return base;
    var w = 0.6 * Math.sin(7.3 * t + phase) + 0.4 * Math.sin(3.1 * t + 1.7 + phase);
    return base * (1 + w * pct / 100);
  }

  // Hand-bone anchor shared with the caster glow orbs (CONFIG.equip.casterGlow:
  // anchor 'hand' = hand bone at handOffset, mirrored for the non-native
  // hand; else / no bones = the weapon idle pose on yawFrame). Re-parents
  // only when the anchor mode or body changes.
  function anchorToHand(player, obj, hand) {
    var C = cfg();
    var G = C.equip.casterGlow;
    if (obj.userData.whAnchorKey === G.anchor && obj.userData.whBody === player.body &&
        obj.parent) return;
    obj.userData.whAnchorKey = G.anchor;
    obj.userData.whBody = player.body;
    var bone = G.anchor === 'hand' && player.body
      ? player.body.getObjectByName(hand === 'left' ? 'L_Hand' : 'R_Hand') : null;
    if (bone) {
      bone.add(obj);
      var nat = C.equip.nativeHand.magicGlove || 'left';
      var o = G.handOffset, m = hand === nat ? [1, 1, 1] : C.equip.mirrorScale;
      obj.position.set(o[0] * m[0], o[1] * m[1], o[2] * m[2]);
    } else {
      player.yawFrame.add(obj);
      var ip = C.moveset.idlePose;
      obj.position.set((hand === 'left' ? -1 : 1) * ip.pos[0], ip.pos[1], ip.pos[2]);
    }
  }

  // scene: lights live here (intensity 0) until the player body exists.
  function PlayerLight(scene) {
    var P = cfg().playerLight;
    this.hands = {};
    for (var h = 0; h < HANDS.length; h++) {
      var l = new THREE.PointLight(0xffffff, 0, 1, 2);
      scene.add(l);
      this.hands[HANDS[h]] = l;
    }
    this.projectile = [];
    for (var i = 0; i < P.projectilePoolSize; i++) {
      var pl = new THREE.PointLight(0xffffff, 0, 1, 2);
      scene.add(pl);
      this.projectile.push(pl);
    }
  }

  // Per frame (before render): hand lights follow the hands + bindings live,
  // projectile lights follow the live bolts that carry a projectileLight.
  PlayerLight.prototype.update = function (player, bolts) {
    var P = cfg().playerLight;
    var t = performance.now() / 1000;
    for (var h = 0; h < HANDS.length; h++) {
      var hand = HANDS[h];
      var light = this.hands[hand];
      var def = player && player.yawFrame ? handLightDef(player, hand) : null;
      if (!def) { light.intensity = 0; continue; }
      anchorToHand(player, light, hand);
      applyDef(light, def, t, h * P.flickerPhaseStep);
    }
    var n = 0;
    var list = bolts || [];
    for (var b = 0; b < list.length && n < this.projectile.length; b++) {
      var bolt = list[b];
      var pdef = bolt && bolt.alive && bolt.config ? bolt.config.projectileLight : null;
      if (!pdef) continue;
      var pl = this.projectile[n];
      pl.position.copy(bolt.pos);
      applyDef(pl, pdef, t, (HANDS.length + n) * P.flickerPhaseStep);
      n++;
    }
    for (; n < this.projectile.length; n++) this.projectile[n].intensity = 0;
  };

  function applyDef(light, def, t, phase) {
    light.color.setHex(def.color);
    light.distance = def.distance;
    light.decay = def.decay;
    light.intensity = flicker(def.intensity, def.flickerPct || 0, t, phase);
  }

  window.WH_PlayerLight = {
    PlayerLight: PlayerLight,
    handLightDef: handLightDef,
    anchorToHand: anchorToHand
  };
})();
