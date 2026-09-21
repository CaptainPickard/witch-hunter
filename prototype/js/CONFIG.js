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
    groundColorA: 0x4a5240,           // hold outskirts grass-dirt
    groundColorB: 0x2c3230,           // darkwood floor
    fogNearFactor: 0.25,              // fog near = radius * factor
    fogFarFactor: 1.5,                // fog far = radius * factor
    characterHeight: 1.8              // normalized character height (POC)
  },

  regionA: {
    id: 'hold_outskirts',
    name: 'Hold Outskirts',
    spawn: { x: 0, z: 45 },           // south of center, boundary is north (z = -25)
    gravityY: -22,
    fogColor: 0x7b8394,
    fogDensity: 0.006,
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
      { asset: 'deadTree', x: -22, z: -2, rotY: 0.5, scale: 3.0 },
      { asset: 'deadTree', x: 20, z: 18, rotY: -0.8, scale: 2.6 },
      { asset: 'deadTree', x: -16, z: -18, rotY: 2.1, scale: 2.8 }
    ]
  },

  regionB: {
    id: 'darkwood_edge',
    name: 'Darkwood Edge',
    spawn: { x: 0, z: -45 },          // north of center, boundary is south (z = +25)
    gravityY: -22,
    fogColor: 0x232830,
    fogDensity: 0.02,                 // R5: denser + darker fog than region A
    ambientLightLevel: 0.55,          // darker ambient
    enemies: [
      { type: 'ghoul', x: -8, z: -38 },
      { type: 'ghoul', x: 9, z: -50 },
      { type: 'bandit', x: 0, z: -60 }
    ],
    props: [
      { asset: 'deadTree', x: -12, z: -40, rotY: 0.2, scale: 3.4 },
      { asset: 'deadTree', x: 14, z: -44, rotY: -1.0, scale: 3.2 },
      { asset: 'deadTree', x: -20, z: -55, rotY: 1.7, scale: 3.6 },
      { asset: 'deadTree', x: 22, z: -58, rotY: 0.6, scale: 3.0 },
      { asset: 'deadTree', x: 2, z: -66, rotY: -0.4, scale: 3.5 },
      { asset: 'deadTree', x: -30, z: -48, rotY: 2.4, scale: 3.1 },
      { asset: 'churchArchway', x: 8, z: -58, rotY: 0.9, scale: 2.2 },
      { asset: 'churchCornerButtress', x: -14, z: -62, rotY: 0.3, scale: 2.0 },
      { asset: 'churchPewBroken', x: 16, z: -52, rotY: -0.7, scale: 1.8 },
      { asset: 'rubblePile', x: -6, z: -48, rotY: 0.0, scale: 1.9 }
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