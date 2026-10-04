// whanim2: presentation-only animation; the combat FSM owns every timing edge.
(function () {
  'use strict';

  var CFG = window.WH_CONFIG.animRt;
  function BLK_ANIM() { return window.WH_CONFIG.block.blockAnim; }
  var NAMES = {
    idle: 'WH_Idle', walk: 'WH_Walk', run: 'WH_Run',
    attack: 'WH_Attack1', hit: 'WH_Hit', death: 'WH_Death'
  };
  // 10-04 chain clips: CONFIG move id -> per-move player clip. Bodies without
  // the clip (enemies, handAxe moves, older GLBs) use the shared 'attack'.
  var MOVE_NAMES = {
    slashR2L: 'WH_SlashR2L', slashL2R: 'WH_SlashL2R', thrust: 'WH_Thrust'
  };
  // Order D shield/block clips (player body only; NOT sword moves). All are
  // LoopOnce + clamp: raise/impact/swipe all END on the same guard frame, so
  // whichever one ran last, clamped, IS the block hold pose. The stagger ends
  // in a crouch the guard-break stun sits in.
  var CLIP_NAMES = {
    shieldRaise: 'WH_ShieldRaise', shieldImpact: 'WH_ShieldImpact',
    parrySwipe: 'WH_ParrySwipe', guardBreak: 'WH_GuardBreakStagger'
  };
  var SHIELD_HOLD = { shieldRaise: true, shieldImpact: true, parrySwipe: true };

  function CharacterAnim(body, clips) {
    this.body = body;
    this.clips = clips;
    this.mixer = new THREE.AnimationMixer(body);
    this.actions = {};
    this.clip = null;
    this.locomotion = 'idle';
    this.hitActive = false;
    this.dead = false;
    this.attackPhase = null;
    this.attackSerial = 0;
    var self = this;
    Object.keys(NAMES).forEach(function (state) {
      var clip = THREE.AnimationClip.findByName(clips, NAMES[state]);
      if (!clip) {
        console.warn('[WH anim] missing ' + NAMES[state]);
        return;
      }
      var action = self.mixer.clipAction(clip);
      if (state === 'hit' || state === 'attack' || state === 'death') {
        action.setLoop(THREE.LoopOnce, 1);
        action.clampWhenFinished = true;
      }
      self.actions[state] = action;
    });
    Object.keys(MOVE_NAMES).forEach(function (move) {
      var clip = THREE.AnimationClip.findByName(clips, MOVE_NAMES[move]);
      if (!clip) return;
      var action = self.mixer.clipAction(clip);
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true;
      self.actions[move] = action;
    });
    Object.keys(CLIP_NAMES).forEach(function (key) {
      var clip = THREE.AnimationClip.findByName(clips, CLIP_NAMES[key]);
      if (!clip) return;
      var action = self.mixer.clipAction(clip);
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true;
      self.actions[key] = action;
    });
    this.mixer.addEventListener('finished', function (event) {
      if (event.action === self.actions.hit && !self.dead) {
        self.hitActive = false;
        self.transition(self.locomotion, CFG.oneShotFadeSeconds);
      }
    });
    this.transition('idle', 0);
  }

  CharacterAnim.prototype.transition = function (state, seconds, restart) {
    if (!this.actions[state] || this.dead && state !== 'death') return;
    if (this.clip === state && !restart) return;
    // Leaving 'hit' for any other clip ends the hit reaction. An interrupted
    // (faded / stopped) hit action never fires the mixer 'finished' event, so
    // hitActive would latch and setLocomotion would never transition again.
    if (state !== 'hit') this.hitActive = false;
    var prev = this.actions[this.clip];
    var next = this.actions[state];
    // Interrupting a fade must not leave an older third action contributing
    // pose/weight when the next transition begins.
    var actions = this.actions;
    Object.keys(actions).forEach(function (key) {
      if (actions[key] !== prev && actions[key] !== next) actions[key].stop();
    });
    if (prev && prev !== next) prev.fadeOut(seconds);
    next.stopFading();
    next.reset();
    next.enabled = true;
    next.setEffectiveWeight(1);
    if (seconds) next.fadeIn(seconds);
    next.play();
    this.clip = state;
  };

  CharacterAnim.prototype.setLocomotion = function (speed, running) {
    if (this.dead) return;
    var state = speed <= 0.01 ? 'idle' : (running ? 'run' : 'walk');
    this.locomotion = state;
    // syncPlayer/syncEnemy only call this after their FSM attack branch ends.
    // A finished attack action remains named 'attack'; transition out of it
    // rather than leaving all clip weights at zero during locomotion.
    if (!this.hitActive) this.transition(state, CFG.crossfadeSeconds);
    if (state === 'walk' || state === 'run') {
      var action = this.actions[state];
      if (action) {
        var cycleMeters = state === 'walk' ? CFG.walkMetersPerCycle : CFG.runMetersPerCycle;
        action.timeScale = speed * action.getClip().duration / cycleMeters;
      }
    }
  };

  CharacterAnim.prototype.hit = function () {
    if (this.dead || !this.actions.hit) return;
    this.hitActive = true;
    this.transition('hit', CFG.oneShotFadeSeconds, true);
  };

  CharacterAnim.prototype.death = function (alreadyDead) {
    if (this.dead || !this.actions.death) return;
    this.dead = true;
    this.hitActive = false;
    this.transition('death', CFG.oneShotFadeSeconds);
    if (alreadyDead) {
      this.actions.death.time = this.actions.death.getClip().duration;
      this.actions.death.paused = true;
    }
  };

  // Order D: blocked hit / landed parry one-shots. Each call is one NEW
  // resolved enemy hit, so it restarts the clip (from guard back to guard).
  CharacterAnim.prototype.shieldImpact = function () {
    if (this.dead || !this.actions.shieldImpact) return;
    this.transition('shieldImpact', BLK_ANIM().impactCrossfadeSec, true);
  };

  CharacterAnim.prototype.shieldParry = function () {
    if (this.dead || !this.actions.parrySwipe) return;
    this.transition('parrySwipe', BLK_ANIM().parryCrossfadeSec, true);
  };

  // Order D state-driven block presentation (called from syncPlayer only when
  // the player is alive and not attacking). Returns true when it owns the
  // pose this frame; false hands over to setLocomotion. No latched flags:
  // every decision reads player state + this.clip each frame, and leaving
  // goes through transition() like any other clip change.
  CharacterAnim.prototype.syncBlock = function (player) {
    var cfg = BLK_ANIM();
    if (player.guardBroken && this.actions.guardBreak) {
      // stagger plays once and clamps on its crouch for the rest of the stun
      this.transition('guardBreak', cfg.guardBreakCrossfadeSec);
      return true;
    }
    if (player.rolling) return false;          // roll wins (it also ends the block)
    if (player.blocking && this.actions.shieldRaise) {
      // a real (unblocked, e.g. from behind) hit reaction finishes first
      if (this.hitActive) return true;
      if (!SHIELD_HOLD[this.clip]) this.transition('shieldRaise', cfg.raiseCrossfadeSec);
      return true;
    }
    // the parry branch ends the block (mechanics); the swipe still finishes
    if (this.clip === 'parrySwipe' && this.actions.parrySwipe.isRunning()) return true;
    return false;
  };

  // 10-04: the player clip is phase-mapped like the enemy one - windup /
  // strike / recover each own a clip segment and play over the CONFIG move's
  // durations, so per-move timings (thrust vs slash) drive the clip.
  // moveId picks the per-move chain clip when the body has it.
  CharacterAnim.prototype.playerAttack = function (phase, phaseTime, durations, moveId) {
    var key = MOVE_NAMES[moveId] && this.actions[moveId] ? moveId : 'attack';
    if (this.dead || !this.actions[key]) return;
    // Chained swings sharing a clip stay in it and re-seek (no self-crossfade);
    // a chain step onto another per-move clip crossfades like any one-shot.
    if (this.clip !== key) this.transition(key, CFG.oneShotFadeSeconds, true);
    this.attackPhase = phase;
    // Seeking to the FSM clock also handles chained/restarted attacks without
    // allowing mixer drift or a render hitch to move the damage window.
    this.seekAttack(phase === 'windup' ? 0 : phase === 'strike' ? 1 : 2,
      phaseTime, [durations.windup, durations.strike, durations.recover], key);
  };

  // Shared attack-clip seek: segment 0 windup [0, s), 1 strike/active
  // [s, 2s), 2 recover [2s, end) with s = attackClipStrikeFraction * length.
  // Per-move clips are authored on their CONFIG stage proportions, so their
  // segment edges are the move's own windup / windup+strike fractions.
  CharacterAnim.prototype.seekAttack = function (seg, phaseTime, durations, key) {
    var action = this.actions[key || 'attack'];
    var clip = action.getClip();
    var a, b;
    if (key && key !== 'attack') {
      var total = Math.max(1e-4, durations[0] + durations[1] + durations[2]);
      a = clip.duration * durations[0] / total;
      b = clip.duration * (durations[0] + durations[1]) / total;
    } else {
      a = clip.duration * CFG.attackClipStrikeFraction;
      b = a * 2;
    }
    var part = seg === 0 ? { start: 0, span: a } :
      seg === 1 ? { start: a, span: b - a } :
      { start: b, span: clip.duration - b };
    action.timeScale = part.span / Math.max(1e-4, durations[seg]);
    action.time = Math.min(clip.duration, part.start +
      Math.max(0, phaseTime) * action.timeScale);
  };

  CharacterAnim.prototype.enemyAttack = function (phase, phaseTime, durations) {
    if (this.dead || !this.actions.attack) return;
    if (phase === 'windup' && this.attackPhase !== 'windup') {
      this.transition('attack', CFG.oneShotFadeSeconds, true);
      this.attackSerial++;
    }
    this.attackPhase = phase;
    this.seekAttack(phase === 'windup' ? 0 : phase === 'active' ? 1 : 2,
      phaseTime, [durations.windup, durations.active, durations.recover]);
  };

  CharacterAnim.prototype.syncPlayer = function (player, dt) {
    if (player.state !== 'alive') {
      this.death();
    } else if (player.attacking) {
      var ph = player.getAttackPhase();
      this.playerAttack(ph.stage, ph.t, ph.durations, player.attackMoveId);
    } else {
      this.attackPhase = null;
      if (this.syncBlock(player)) {
        // keep the locomotion state current so the exit crossfade targets it
        this.locomotion = (player.animMoveSpeed || 0) <= 0.01 ? 'idle' :
          (player.sprinting ? 'run' : 'walk');
      } else {
        this.setLocomotion(player.animMoveSpeed || 0, !!player.sprinting || player.rolling);
      }
    }
    this.update(dt);
  };

  CharacterAnim.prototype.syncEnemy = function (enemy, dt) {
    if (enemy.fsm === 'dead') {
      this.death();
    } else if (enemy.fsm === 'attack') {
      this.enemyAttack(enemy.attackPhase, enemy.attackPhaseT, enemy.cfg.attackPhase);
    } else {
      this.attackPhase = null;
      this.setLocomotion(enemy.animMoveSpeed || 0,
        (enemy.animMoveSpeed || 0) > enemy.cfg.moveSpeed);
    }
    this.update(dt);
  };

  CharacterAnim.prototype.revive = function () {
    this.mixer.stopAllAction();
    this.dead = false;
    this.hitActive = false;
    this.attackPhase = null;
    this.clip = null;
    this.transition('idle', 0);
    this.mixer.update(0);
  };

  CharacterAnim.prototype.update = function (dt) {
    this.mixer.update(dt);
    if (this.dead && this.actions.death && this.actions.death.paused) {
      this.actions.death.time = this.actions.death.getClip().duration;
    }
  };

  CharacterAnim.prototype.getState = function () {
    var action = this.actions[this.clip];
    var time = action ? action.time : 0;
    var duration = action ? action.getClip().duration : 1;
    var weights = {};
    var self = this;
    Object.keys(NAMES).forEach(function (state) {
      var act = self.actions[state];
      weights[NAMES[state]] = act && (act.isRunning() ||
        (self.dead && state === 'death' && self.clip === 'death')) ?
        act.getEffectiveWeight() : 0;
    });
    Object.keys(MOVE_NAMES).forEach(function (move) {
      var act = self.actions[move];
      if (act) weights[MOVE_NAMES[move]] = act.isRunning() ? act.getEffectiveWeight() : 0;
    });
    Object.keys(CLIP_NAMES).forEach(function (key) {
      var act = self.actions[key];
      // a clamped (finished) shield clip still holds the pose at full weight
      if (act) weights[CLIP_NAMES[key]] = act.enabled && self.clip === key ?
        act.getEffectiveWeight() : (act.isRunning() ? act.getEffectiveWeight() : 0);
    });
    return { clip: NAMES[this.clip] || MOVE_NAMES[this.clip] || CLIP_NAMES[this.clip] || null,
      time: time,
      phase: duration ? time / duration : 0, weights: weights,
      timeScale: action ? action.timeScale : 0,
      locomotion: NAMES[this.locomotion], attackSerial: this.attackSerial };
  };

  window.WH_CharacterAnim = CharacterAnim;
})();
