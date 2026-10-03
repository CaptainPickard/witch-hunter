// whanim2: presentation-only animation; the combat FSM owns every timing edge.
(function () {
  'use strict';

  var CFG = window.WH_CONFIG.animRt;
  var NAMES = {
    idle: 'WH_Idle', walk: 'WH_Walk', run: 'WH_Run',
    attack: 'WH_Attack1', hit: 'WH_Hit', death: 'WH_Death'
  };

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

  // 10-04: the player clip is phase-mapped like the enemy one - windup /
  // strike / recover each own a clip segment and play over the CONFIG move's
  // durations, so per-move timings (thrust vs slash) drive the clip.
  CharacterAnim.prototype.playerAttack = function (phase, phaseTime, durations) {
    if (this.dead || !this.actions.attack) return;
    // Chained swings stay in 'attack' and re-seek; no self-crossfade.
    if (this.clip !== 'attack') this.transition('attack', CFG.oneShotFadeSeconds, true);
    this.attackPhase = phase;
    // Seeking to the FSM clock also handles chained/restarted attacks without
    // allowing mixer drift or a render hitch to move the damage window.
    this.seekAttack(phase === 'windup' ? 0 : phase === 'strike' ? 1 : 2,
      phaseTime, [durations.windup, durations.strike, durations.recover]);
  };

  // Shared attack-clip seek: segment 0 windup [0, s), 1 strike/active
  // [s, 2s), 2 recover [2s, end) with s = attackClipStrikeFraction * length.
  CharacterAnim.prototype.seekAttack = function (seg, phaseTime, durations) {
    var clip = this.actions.attack.getClip();
    var strike = clip.duration * CFG.attackClipStrikeFraction;
    var part = seg === 0 ? { start: 0, span: strike } :
      seg === 1 ? { start: strike, span: strike } :
      { start: strike * 2, span: clip.duration - strike * 2 };
    this.actions.attack.timeScale = part.span / Math.max(1e-4, durations[seg]);
    this.actions.attack.time = Math.min(clip.duration, part.start +
      Math.max(0, phaseTime) * this.actions.attack.timeScale);
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
      this.playerAttack(ph.stage, ph.t, ph.durations);
    } else {
      this.attackPhase = null;
      this.setLocomotion(player.animMoveSpeed || 0, !!player.sprinting || player.rolling);
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
    return { clip: NAMES[this.clip] || null, time: time,
      phase: duration ? time / duration : 0, weights: weights,
      timeScale: action ? action.timeScale : 0,
      locomotion: NAMES[this.locomotion], attackSerial: this.attackSerial };
  };

  window.WH_CharacterAnim = CharacterAnim;
})();
