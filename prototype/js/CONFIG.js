// Witch Hunter prototype v1 - global tunables.
// All tuned values live here; logic files must reference CONFIG, not literals.
// Sources: docs/planning/33-equipment-and-formulas.md where straightforward,
// otherwise POC-scaled values marked (POC).
window.WH_CONFIG = {

  renderer: {
    // r185 colorspace + dark-albedo exposure (per validated Witch Hunter 3D settings)
    outputColorSpaceSRGB: true,       // renderer.outputColorSpace = SRGBColorSpace
    toneMappingExposure: 1.6,         // lifted for dark Meshy albedo (POC)
    maxPixelRatio: 2,
    shadowMapEnabled: false           // v1: swiftshader software render, shadows off (POC)
  },

  lighting: {
    // R4: ambient fill high, keys moderate (dark albedo needs big fill)
    ambientColor: 0x8a8fa8,
    ambientIntensity: 4.0,            // bright ambient fill (POC, validated setting)
    keyColor: 0xfff2dd,
    keyIntensity: 1.2,                // moderate key
    hemiSkyColor: 0x6b7fa8,
    hemiGroundColor: 0x3a3a44,
    hemiIntensity: 1.5
  },

  world: {
    groundRadius: 90,                 // playable disc radius per region
    groundColorA: 0x3d3a2c,           // dark mud/olive (darkwood canon palette)
    groundColorB: 0x232620,           // near-charcoal mud (darkwood canon palette)
    groundTexture: {                  // procedural pixel-art ground canvas (region-manager.js)
      size: 256,                      // canvas px per side (one per region, boot-time)
      repeat: 12,                     // texture repeats across the ground disc
      blotchCount: 140,               // noise blotch clusters per canvas
      mossDensity: 0.06,              // pale sickly moss accent, pixel fraction
      puddleDensity: 0.03             // near-black wet puddle specks, pixel fraction
    },
    fogNearFactor: 0.25,              // fog near = radius * factor
    fogFarFactor: 1.5,                // fog far = radius * factor
    characterHeight: 1.8              // normalized character height (POC)
  },

  regionA: {
    id: 'hold_outskirts',
    name: 'Hold Outskirts',
    spawn: { x: 0, z: 45 },           // south of center, boundary is north (z = -25)
    gravityY: -22,
    fogColor: 0x9aa0a3,               // pale ash grey, whiter (darkwood canon)
    fogDensity: 0.012,                // heavier, lower fog (darkwood canon)
    ambientLightLevel: 1.0,           // multiplier on base lighting
    enemies: [
      { type: 'bandit', x: -6, z: -8 },
      { type: 'bandit', x: 10, z: -14 },
      { type: 'ghoul', x: 2, z: -30 }
    ],
    props: [
      { asset: 'gravestoneObelisk', x: -10, z: 20, rotY: 0.3, scale: 1.6 },
      { asset: 'gravestoneObelisk', x: -13, z: 17, rotY: -0.2, scale: 1.4 },
      { asset: 'gravestoneObelisk', x: 12, z: 22, rotY: 1.1, scale: 1.5 },
      { asset: 'stoneCrossTilted', x: -5, z: 15, rotY: 0.7, scale: 1.6 },
      { asset: 'stoneCrossTilted', x: 8, z: 12, rotY: -1.2, scale: 1.3 },
      { asset: 'graveMound', x: 3, z: 24, rotY: 0.0, scale: 2.2 },
      { asset: 'graveMound', x: 15, z: 6, rotY: 0.4, scale: 1.8 },
      { asset: 'buriedCoffin', x: -18, z: 5, rotY: 0.9, scale: 1.7 },
      { asset: 'lanternPost', x: -2, z: 30, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: 4, z: -2, rotY: 0.0, scale: 2.4 },
      { asset: 'deadTree', x: -22, z: -2, rotY: 0.5, scale: 6.5 },
      { asset: 'deadTree', x: 20, z: 18, rotY: -0.8, scale: 6.5 },
      { asset: 'deadTree', x: -16, z: -18, rotY: 2.1, scale: 6.5 },
      { asset: 'picketFence', x: 15.4, z: 13.2, rotY: 0.0, scale: 1.63 },
      { asset: 'picketFence', x: 12.2, z: 12.2, rotY: 0.0, scale: 1.55 },
      { asset: 'picketFence', x: -19.1, z: 10.8, rotY: 1.57, scale: 1.59 },
      { asset: 'picketFence', x: -19.8, z: 7.6, rotY: 1.57, scale: 1.67 },
      { asset: 'picketFence', x: -20.8, z: 13.3, rotY: 1.57, scale: 1.57 },
      { asset: 'ironFenceSection', x: -5.6, z: 28.9, rotY: 1.65, scale: 1.33 },
      { asset: 'ironFenceSection', x: -7.6, z: 31.1, rotY: 3.54, scale: 1.36 },
      { asset: 'deadTree', x: 26.0, z: 9.0, rotY: 4.24, scale: 6.5 },
      { asset: 'livingOak', x: -27.8, z: -19.9, rotY: 1.8, scale: 6.5 },
      { asset: 'yewTree', x: 29.4, z: 1.3, rotY: 3.03, scale: 6.5 },
      { asset: 'mossBoulder', x: 17.2, z: -9.0, rotY: 5.46, scale: 1.37 },
      { asset: 'mossBoulder', x: -24.4, z: 23.0, rotY: 0.73, scale: 1.34 },
      { asset: 'treeStump', x: 7.2, z: 18.4, rotY: 6.18, scale: 1.14 },
      { asset: 'treeStump', x: -8.4, z: 8.3, rotY: 5.43, scale: 1.21 },
      { asset: 'fallenLog', x: -13.0, z: -7.1, rotY: 0.8, scale: 1.52 },
      { asset: 'mourningStatue', x: -11.4, z: 12.7, rotY: 2.43, scale: 1.72 },
      { asset: 'mossBoulder', x: 5.5, z: 8.5, rotY: 1.1, scale: 1.1 },
      { asset: 'mossBoulder', x: -2.5, z: -6.5, rotY: 3.9, scale: 1.05 },
      { asset: 'mossBoulder', x: 10.5, z: -14.5, rotY: 5.2, scale: 1.2 },
      { asset: 'treeStump', x: -15.5, z: 3.5, rotY: 2.2, scale: 1.15 },
      { asset: 'treeStump', x: 15.5, z: -2.5, rotY: 0.9, scale: 1.18 },
      { asset: 'graveMound', x: -4.5, z: -12.5, rotY: 0.6, scale: 1.6 },
      { asset: 'fallenLog', x: 12.5, z: 2.5, rotY: 2.4, scale: 1.45 },
      { asset: 'gravestoneObelisk', x: 16.5, z: 10.5, rotY: 0.8, scale: 1.3 },
      { asset: 'stoneCrossTilted', x: 18.5, z: 14.5, rotY: 2.1, scale: 1.25 },
      { asset: 'graveMound', x: 20.5, z: 11.5, rotY: 1.3, scale: 1.7 },
      { asset: 'gravestoneObelisk', x: -14.5, z: 20.5, rotY: 1.9, scale: 1.35 },
      { asset: 'graveMound', x: -17.5, z: 24.5, rotY: 2.4, scale: 1.55 },
      { asset: 'buriedCoffin', x: 6.5, z: 12.5, rotY: 0.4, scale: 1.5 },
      { asset: 'mossBoulder', x: -20.5, z: -12.5, rotY: 4.4, scale: 1.15 },
      { asset: 'treeStump', x: 20.5, z: 2.5, rotY: 3.1, scale: 1.1 }
    ]
  },

  regionB: {
    id: 'darkwood_edge',
    name: 'Darkwood Edge',
    spawn: { x: 0, z: -45 },          // north of center, boundary is south (z = +25)
    gravityY: -22,
    fogColor: 0x6f7477,               // pale grey sea of mist (darkwood canon)
    fogDensity: 0.024,                // denser midground mist (darkwood canon)
    ambientLightLevel: 0.55,          // darker ambient
    enemies: [
      { type: 'ghoul', x: -8, z: -38 },
      { type: 'ghoul', x: 9, z: -50 },
      { type: 'bandit', x: 0, z: -60 }
    ],
    props: [
      { asset: 'livingOak', x: 6.2, z: -46.4, rotY: 0.44, scale: 7.25 },
      { asset: 'witchwoodTree', x: -31.2, z: -50.3, rotY: 3.15, scale: 8.6 },
      { asset: 'livingOak', x: 25.2, z: -73.8, rotY: 2.69, scale: 7.45 },
      { asset: 'livingOak', x: -31.1, z: -68.7, rotY: 5.13, scale: 8.43 },
      { asset: 'witchwoodTree', x: 19.0, z: -54.7, rotY: 4.18, scale: 8.28 },
      { asset: 'witchwoodTree', x: -10.9, z: -55.8, rotY: 4.43, scale: 10.43 },
      { asset: 'livingOak', x: -22.3, z: -59.2, rotY: 1.82, scale: 9.0 },
      { asset: 'deadTree', x: 35.5, z: -52.1, rotY: 2.09, scale: 9.85 },
      { asset: 'witchwoodTree', x: -18.1, z: -35.6, rotY: 0.99, scale: 7.38 },
      { asset: 'deadTree', x: -9.1, z: -35.8, rotY: 2.13, scale: 8.0 },
      { asset: 'yewTree', x: 21.9, z: -55.6, rotY: 5.57, scale: 8.38 },
      { asset: 'deadTree', x: 28.8, z: -55.3, rotY: 0.33, scale: 7.62 },
      { asset: 'yewTree', x: -31.3, z: -43.3, rotY: 3.91, scale: 10.4 },
      { asset: 'deadTree', x: 31.4, z: -48.7, rotY: 0.61, scale: 7.33 },
      { asset: 'yewTree', x: 19.4, z: -66.5, rotY: 1.34, scale: 9.18 },
      { asset: 'deadTree', x: -23.0, z: -47.8, rotY: 0.13, scale: 8.45 },
      { asset: 'witchwoodTree', x: -29.1, z: -72.5, rotY: 4.72, scale: 6.78 },
      { asset: 'yewTree', x: 13.4, z: -70.9, rotY: 4.67, scale: 9.43 },
      { asset: 'deadTree', x: -20.5, z: -42.5, rotY: 4.19, scale: 8.05 },
      { asset: 'livingOak', x: -23.0, z: -39.2, rotY: 5.43, scale: 6.92 },
      { asset: 'yewTree', x: -37.4, z: -47.4, rotY: 3.99, scale: 8.12 },
      { asset: 'livingOak', x: 23.5, z: -37.4, rotY: 4.81, scale: 7.55 },
      { asset: 'deadTree', x: 36.4, z: -37.1, rotY: 3.3, scale: 7.05 },
      { asset: 'witchwoodTree', x: -7.4, z: -41.5, rotY: 5.92, scale: 10.02 },
      { asset: 'yewTree', x: 27.7, z: -49.3, rotY: 2.97, scale: 9.75 },
      { asset: 'yewTree', x: 24.0, z: -61.4, rotY: 3.8, scale: 9.7 },
      { asset: 'witchwoodTree', x: 7.8, z: -38.4, rotY: 2.24, scale: 8.0 },
      { asset: 'yewTree', x: 15.1, z: -49.5, rotY: 4.85, scale: 7.45 },
      { asset: 'deadTree', x: -31.1, z: -74.8, rotY: 0.61, scale: 8.68 },
      { asset: 'livingOak', x: -22.9, z: -71.1, rotY: 0.72, scale: 7.82 },
      { asset: 'witchwoodTree', x: 29.8, z: -76.9, rotY: 0.5, scale: 9.68 },
      { asset: 'witchwoodTree', x: -28.4, z: -79.9, rotY: 4.96, scale: 9.8 },
      { asset: 'deadTree', x: -16.0, z: -76.7, rotY: 3.09, scale: 9.45 },
      { asset: 'churchArchway', x: 8, z: -58, rotY: 0.9, scale: 2.2 },
      { asset: 'churchCornerButtress', x: -14, z: -62, rotY: 0.3, scale: 2.0 },
      { asset: 'churchPewBroken', x: 16, z: -52, rotY: -0.7, scale: 1.8 },
      { asset: 'rubblePile', x: -6, z: -48, rotY: 0.0, scale: 1.9 },
      { asset: 'mossBoulder', x: 32.3, z: -55.2, rotY: 1.89, scale: 1.33 },
      { asset: 'mossBoulder', x: 17.1, z: -52.8, rotY: 4.82, scale: 0.9 },
      { asset: 'mossBoulder', x: -27.1, z: -69.5, rotY: 2.43, scale: 0.95 },
      { asset: 'mossBoulder', x: 32.2, z: -52.2, rotY: 6.24, scale: 1.01 },
      { asset: 'mossBoulder', x: 11.0, z: -50.6, rotY: 3.81, scale: 1.57 },
      { asset: 'mossBoulder', x: 25.0, z: -64.4, rotY: 2.36, scale: 1.46 },
      { asset: 'mossBoulder', x: -23.0, z: -51.6, rotY: 2.49, scale: 0.91 },
      { asset: 'fallenLog', x: 28.2, z: -59.0, rotY: 0.0, scale: 1.34 },
      { asset: 'fallenLog', x: -28.6, z: -63.7, rotY: 1.57, scale: 1.61 },
      { asset: 'fallenLog', x: -29.1, z: -45.6, rotY: 1.57, scale: 1.58 },
      { asset: 'fallenLog', x: -10.1, z: -62.1, rotY: 3.14, scale: 1.59 },
      { asset: 'treeStump', x: 13.4, z: -58.7, rotY: 0.72, scale: 1.43 },
      { asset: 'treeStump', x: -11.1, z: -44.1, rotY: 3.43, scale: 1.04 },
      { asset: 'treeStump', x: 13.0, z: -55.5, rotY: 5.02, scale: 1.23 },
      { asset: 'treeStump', x: -25.4, z: -46.9, rotY: 1.05, scale: 1.24 },
      { asset: 'cemeteryGate', x: 25.8, z: -42.0, rotY: 0.3, scale: 1.53 },
      { asset: 'cemeteryGate', x: 20.1, z: -50.4, rotY: 1.2, scale: 1.71 },
      { asset: 'picketFence', x: 22.1, z: -53.0, rotY: 1.57, scale: 1.46 },
      { asset: 'picketFence', x: -27.4, z: -51.6, rotY: 2.2, scale: 1.29 },
      { asset: 'gravestoneObelisk', x: 13.1, z: -41.5, rotY: 3.73, scale: 1.38 },
      { asset: 'gravestoneObelisk', x: 20.1, z: -40.0, rotY: 0.14, scale: 1.38 },
      { asset: 'stoneCrossTilted', x: -13.5, z: -36.6, rotY: 5.5, scale: 1.22 },
      { asset: 'stoneCrossTilted', x: 18.0, z: -43.1, rotY: 6.16, scale: 1.6 }
    ]
  },

  // Boundary between A and B: the plane z = CONFIG.boundary.z.
  // Region A occupies z > boundaryZ, region B occupies z < boundaryZ.
  boundary: {
    z: -25,                           // shared boundary plane (A is +z side, B is -z side)
    xMin: -80,                        // lateral extent of the world edge
    xMax: 80,
    wallHeight: 8                     // invisible wall visual scale reference
  },

  chokepoint: {
    centerX: 0,                       // gate sits at x = 0 on the boundary
    width: 8,                         // passable corridor width along the boundary
    markerScale: 2.0
  },

  preWarm: {
    distance: 30,                     // build neighbor when player is this close to boundary
    hysteresis: 20                    // dispose pre-warm when player is this much farther away
  },

  // Darkwood dressing pass: cheap ground mist layer, built by region-manager
  // buildRegion for region B only (y ~ 1.5, double-sided, no collider).
  mistPlane: {
    enabled: true,
    regionId: 'darkwood_edge',        // build only for this region id
    colorHex: 0xc5c9cc,               // pale ash highlight fog (canon)
    y: 1.5,                           // plane height above ground
    opacityX100: 14                   // opacity 0.14 (within 0.12-0.18 band)
  },

  player: {
    // (POC) scale: character model is ~2 units tall
    walkSpeed: 6.0,
    sprintSpeed: 10.0,
    sprintStaminaPerSec: 18.0,
    rollSpeed: 14.0,
    rollDuration: 0.45,               // seconds
    rollIFrameWindow: 0.35,           // seconds of i-frames within a roll
    rollStaminaCost: 25.0,
    attackDuration: 0.5,
    attackStaminaCost: 15.0,
    attackRange: 3.2,
    attackArcHalfAngleDeg: 70,        // swing arc half-angle
    attackDamage: 34,                 // (POC) from doc 33 one-hand band
    attackDamageGhoulBonus: 1.15,
    staminaMax: 100.0,                // (doc 33 band)
    staminaRegenPerSec: 28.0,
    staminaRegenDelay: 0.6,           // seconds after spend before regen resumes
    hpMax: 100.0,
    hpRegenPerSec: 0.0,               // no passive regen in v1
    turnLerpDegPerSec: 720.0,         // body yaw turn rate toward move dir
    radius: 0.7,                      // collision circle
    camDistance: 7.0,
    camMinDistance: 3.0,
    camMaxDistance: 14.0,
    camPitchMinDeg: -15,
    camPitchMaxDeg: 65,
    camHeight: 2.6,
    camFollowLerp: 12.0,              // per-second lerp factor
    camAutoFollowDelay: 1.2,          // seconds after manual drag before auto-follow resumes
    camAutoFollowRate: 2.5,           // per-second exp lerp for auto yaw follow
    mouseSensDegPerPx: 0.25,
    respawnDelay: 2.2                 // seconds on death screen before respawn
  },

  // v6: block and parry (defense layer v1, HUD/DOM cues only)
  block: {
    parryWindow: 0.25,            // s, RMB-down parry window
    parryStaminaCost: 5,          // stamina spent on a successful parry
    absorb: 0.8,                  // fraction of damage negated on block (chip = 20%)
    staminaCostMult: 0.9,         // blocked hit drains damage * this
    blockArcHalfAngleDeg: 90,     // half-angle of the block/parry arc
    moveMult: 0.5,                // movement speed multiplier while blocking
    blockingRegenMult: 0.5,       // stamina regen rate multiplier while blocking
    guardBreakStun: 0.8,          // s, stun after guard break
    guardBreakMinStamina: 30,     // cannot block again until stamina >= this
    riposteMult: 1.75,            // next hit on a staggered enemy
    riposteStaggerDur: 1.25,      // s, enemy stagger after a parry
    parryFlashSeconds: 0.15,      // HUD white flash duration
    blockFlashSeconds: 0.12,      // HUD gray flash duration
    guardBreakFlashSeconds: 0.5,  // HUD red flash duration
    guardBreakTextSeconds: 1.4    // GUARD BROKEN text pulse duration
  },

  enemy: {
    // All senses/combat numbers are POC-scaled; doc 33 has no sight values (D4b-1).
    bandit: {
      hpMax: 70.0,
      moveSpeed: 3.6,
      chaseSpeed: 5.0,
      attackDamage: 12.0,
      attackRange: 2.4,
      attackCooldown: 1.4,
      sightRadius: 16.0,
      leashRadius: 34.0,              // beyond this from spawn, disengage
      staggerTime: 0.4,
      radius: 0.7,
      aggroPingInterval: 0.2          // seconds between sense checks
    },
    ghoul: {
      hpMax: 45.0,
      moveSpeed: 4.4,
      chaseSpeed: 7.0,                // faster than bandit per D4
      attackDamage: 8.0,
      attackRange: 2.0,
      attackCooldown: 1.0,
      sightRadius: 18.0,
      leashRadius: 36.0,
      staggerTime: 0.35,
      radius: 0.6,
      aggroPingInterval: 0.2
    },
    separationPush: 6.0,              // circle push-out strength
    holdAtBoundaryMargin: 1.5         // enemies stop this far before the boundary
  },

  hud: {
    regionNameFadeSeconds: 2.6,
    deathFadeSeconds: 0.8,
    fpsUpdateInterval: 0.5
  },

  lockOn: {
    maxDistance: 18.0,              // engage range (world units)
    hysteresis: 1.25,               // break at maxDistance * hysteresis
    facingConeDeg: 140,             // total cone around CAMERA forward
    camLerp: 6.0,                   // per-second lerp for lock camera follow
    camExtraDistance: 3.5,           // camera pulls back this much past target dist
    reticleOffsetY: 0.9             // reticle aim height above enemy feet
  },

  // v3: procedural animation feel (transform-only; assets are unrigged).
  // Stage fractions are of CONFIG.player.attackDuration and sum to 1.
  anim: {
    attack: {
      windupFrac: 0.30,             // of attackDuration
      strikeFrac: 0.25,             // of attackDuration (recover = remainder)
      windupLean: -0.25,            // rad, body rotation.x lean back
      windupCrouch: 0.06,           // root dip (units) during windup
      windupSwordRaise: 0.9,        // rad, sword rotation.z lift in windup
      strikeYawSweepDeg: 140,       // total body yaw sweep through strike
      strikeLunge: 0.25,            // forward units along facing during strike
      strikeSwordSweepDeg: 160,     // sword arc through strike
      recoverLean: 0.10             // rad, forward-lean settle in recover
    },
    walk: {
      bobAmp: 0.09,                 // primary vertical bob
      bobFreqWalk: 9,               // rad/s phase rate
      bobFreqSprint: 14,
      leanWalk: 0.08,               // rad forward lean at walk speed
      leanSprint: 0.16,             // rad forward lean at sprint speed
      swayAmp: 0.05,                // lateral sway (position.x in body space)
      swayFreqMult: 0.5,            // half the bob frequency
      counterRollAmp: 0.05,         // rad rotation.z counter-roll
      yawOscAmp: 0.06,              // rad yaw oscillation at bob frequency
      footDipAmp: 0.04,             // secondary vertical sine
      footDipFreqMult: 2,           // 2x bob frequency (two dips per cycle)
      sprintAmpMult: 1.5,           // multiplies all layer amplitudes
      idleDelay: 0.5,               // seconds of no movement before idle anim
      idleBobAmp: 0.02,             // breathing bob amplitude
      idlePeriod: 1.2,              // seconds per breath
      idleYawAmp: 0.02              // rad tiny yaw drift
    },
    // Per-type enemy walk amplitude multipliers (layered cycle parity).
    enemyWalk: {
      bandit: { bob: 1.0, sway: 1.0, lean: 1.0, yawOsc: 1.0 },
      ghoul:  { bob: 1.1, sway: 1.6, lean: 1.2, yawOsc: 1.3 }
    },
    ghoulHop: {
      height: 0.25,                 // root y arc height (units)
      duration: 0.25                // seconds, fired at chase -> attack
    },
    stagger: {
      visualDuration: 0.15,         // seconds of lean-back/knockback visual
      leanBack: 0.25,               // rad body rotation.x lean back
      knockback: 1.2                // units/s push away from attacker
    },
    death: {
      settleOvershoot: 0.05,        // bounce above final sink at end of fall
      settleDuration: 0.45          // seconds for the settle bounce
    },
    shake: {
      amplitude: 0.05,              // camera shake pulse (units)
      duration: 0.15                // seconds decay
    }
  },

  loop: {
    maxDt: 1 / 20,                    // clamp dt (tab-blur / hitch protection)
    fixedTickHz: 60                   // nominal update rate reference
  },

  assets: {
    timeoutMs: 20000,                 // per-asset load timeout before stand-in substitution
    standInColor: 0x777777
  }
};
window.WH_CONFIG.moveset = {
  idlePose: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
  comboChainCap: 3,
  banditStageMult: 1.6,
  enemyWeapon: { bandit: 'handAxe' }
};
