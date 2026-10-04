// Witch Hunter prototype v1 - global tunables.
// All tuned values live here; logic files must reference CONFIG, not literals.
// Sources: docs/planning/33-equipment-and-formulas.md where straightforward,
// otherwise POC-scaled values marked (POC).
window.WH_CONFIG = {

  renderer: {
    // r185 colorspace + dark-albedo exposure (per validated Witch Hunter 3D settings)
    outputColorSpaceSRGB: true,       // renderer.outputColorSpace = SRGBColorSpace
    toneMappingName: 'Neutral',       // R2 P0-3: Neutral tonemap (ACES fallback in game.js)
    toneMappingExposure: 1.15,        // R2 P0-3: re-set so fog stays the brightest large area (audit)
    // R3 P0-4: maxPixelRatio superseded by internalResDiv (setPixelRatio(1)); legacy key kept
    maxPixelRatio: 2,
    internalResDiv: 2,                // R3 P0-4: buffer = window px / div (960x540 at 1080p), CSS upscales; 10-03 F1/F2 debug keys tune it live (1..4)
    shadowMapEnabled: false           // v1: swiftshader software render, shadows off (POC)
  },

  lighting: {
    // R2 P0-3 moon night rig: AmbientLight removed entirely - the
    // hemisphere is the only fill, and region.ambientLightLevel scales it
    // (region fill = hemiBaseIntensity * ambientLightLevel). Moon = cool
    // directional on the -z side backlighting the A->B main path. The R2
    // player lantern is DELETED (10-05 light radius order): player light is
    // earned - see CONFIG.playerLight.
    ambientIntensity: 0,              // P0-3: AmbientLight removed (kept for backward-compat readers; must stay 0)
    hemiSkyColor: 0x4a5a80,           // indigo-slate sky (audit 5.3)
    hemiGroundColor: 0x16181e,        // near-black ground (audit 5.3)
    // 10-03 order 4 (starry night, moon-dominant): hemi fill cut so the moon
    // directional is the main sky light; sky luminance comes from the dome.
    hemiBaseIntensity: 0.55,          // fill at ambientLightLevel 1.0; region fill = base * level
    moonColor: 0xa8bce6,              // cool moon (audit 5.3)
    // 10-03 order 4: moon is now the main sky light (fill cut 1.35 -> 0.55).
    // Directional intensity raised so moon:fill vertical ratio actually lands.
    moonIntensity: 0.9,              // moon:fill (vertical faces) 3-5:1
    moonAzimuthDeg: 0,                // -z side, backlights A->B main path
    moonElevationDeg: 30,             // audit: 25-35 deg
    // 10-03 order 4: 1.15x base fill for B (darker Darkwood); region A uses 1.0
    regionBFillMult: 1.15
  },

  // 10-05 light radius order (js/light.js WH_PlayerLight): the player has NO
  // intrinsic light. Per hand (max 2 follow lights, on the hand bone at the
  // casterGlow anchor): an equipped item's items[id].light, else a caster
  // hand's bound spell's spell[id].light. Light blocks are
  // { color, intensity, distance, decay, flickerPct }. All lights exist from
  // boot at intensity 0 (fixed scene light count, no shader recompiles).
  playerLight: {
    flickerPhaseStep: 2.3,            // rad between lights' flicker phases (no lockstep pulse)
    projectilePoolSize: 2             // in-flight bolt lights (spell[id].projectileLight); extra bolts go unlit
  },

  // 10-03 order 4: starry night sky (game.js setupSky). Dome ignores fog;
  // scene.background goes near-black so fog color no longer lights the world.
  sky: {
    domeRadius: 400,                  // beyond ground disc, inside camera far 500
    zenithColor: 0x070a18,            // deep night indigo
    horizonBand: 0x2b3350,            // faint band where fog meets sky
    horizonGlow: 0x8f98ad,            // pale ash highlight (fog-color kin, low band)
    horizonGlowStop: 0.16,            // glow fade fraction from horizon upward
    starCount: 600,
    starSizeMin: 1.2,                 // px at internal res
    starSizeMax: 2.6,
    starColors: [0xcfd8e8, 0xaebad0, 0xe8ecf4, 0x9fb2d8],
    twinklePct: 12,                   // fraction of stars that twinkle slowly
    moonAzimuthDeg: 0,                // matches lighting.moon (directional -z)
    moonElevationDeg: 30,
    moonDistance: 330,                // on the dome, inside camera far
    moonSizePx: 64,                   // angular size at dome distance
    moonColor: 0xdfe7f2,
    moonGlowColor: 0xa8bce6
  },

  // R2: fixed pool of PointLights (P1-8) - nearest-socket handoff, no per-frame allocation.
  lightPool: {
    size: 4,
    color: 0xffc27a,
    distance: 11,
    decay: 2,
    handoffFadeSec: 0.35,   // intensity fade time constant on handoff
    minIntensityFloor: 0.0  // unused slot = 0 intensity, never removed
  },
  // P1-8: CONFIG assets whose props host a light socket (fixed pool hooks
  // these, nearest to the player wins). heightFraction is up the prop's
  // native height; intensity is the pool target when hosting the socket.
  lightSockets: {
    lanternPost: { heightFraction: 0.85, intensity: 1.6 },
    banditCampfire: { heightFraction: 0.55, intensity: 2.4 },
    lanternWaymarker: { heightFraction: 0.80, intensity: 1.8 }
  },

  world: {
    groundRadius: 90,                 // playable disc radius per region
    // R5 P0-5: player + enemies are held inside groundRadius - playerMargin;
    // the visual ground extends visualGroundFogMult * d95 past that rim, where
    // d95 = sqrt(-ln(1 - fogOpaqueFrac)) / region fogDensity (FogExp2).
    playerMargin: 1.5,
    visualGroundFogMult: 1.1,
    fogOpaqueFrac: 0.95,
    colliderCorridorHalfDepth: 6,     // gate corridor = chokepoint x-span, boundary.z +- this
    groundColorA: 0x3d3a2c,           // dark mud/olive (darkwood canon palette)
    groundColorB: 0x232620,           // near-charcoal mud (darkwood canon palette)
    groundTexture: {                  // procedural pixel-art ground canvas (region-manager.js)
      size: 256,                      // canvas px per side (one per region, boot-time)
      repeat: 12,                     // texture repeats across the ground disc
      blotchCount: 140,               // noise blotch clusters per canvas
      mossDensity: 0.06,              // pale sickly moss accent, pixel fraction
      puddleDensity: 0.03             // near-black wet puddle specks, pixel fraction
    },
    // 10-03 change order 2: dirt path ribbon (region-manager buildDirtPath).
    // Swaying centerline through the south clearing into the cemetery; visual
    // only (no collider), pixel-art dirt canvas, repeat-wrapped along length.
    dirtPath: {
      regionId: 'hold_outskirts',     // build for region A only (like mistPlane)
      zFrom: 86.0,                    // south rim start (inside playable 88.5); order 3: span ends at yard fence
      zTo: 32.0,                      // order 3: ends AT the graveyard fence mouth
      halfWidth: 2.7,                 // 5.4m wide
      swayAmp: 1.6,                   // centerline x = amp*sin(2pi(z-zFrom)/period)
      swayPeriod: 34.0,
      y: 0.02,                        // above ground disc
      tileLengthMeters: 3.0,          // one texture tile per 3m along the path
      repeatAcrossWidth: 1            // one tile across (u-edge fade lands only at strip borders)
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
      { type: 'ghoul', x: 2, z: -23.5 },
      { type: 'bandit', x: -54.3, z: 64.8 },
      { type: 'ghoul', x: -23.1, z: 71.2 },
      { type: 'bandit', x: -63.2, z: -18.0 },
      { type: 'ghoul', x: -64.7, z: 20.5 },
      { type: 'bandit', x: -42.6, z: 70.7 },
      { type: 'ghoul', x: -64.9, z: 35.8 },
      { type: 'bandit', x: -48.5, z: 39.6 },
      { type: 'ghoul', x: 54.2, z: 74.5 },
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
      { asset: 'yewTree', x: 29.4, z: 1.3, rotY: 3.03, scale: 6.5 },
      { asset: 'lanternPost', x: -2, z: 30, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: 4, z: -2, rotY: 0.0, scale: 2.4 },
      { asset: 'picketFence', x: 15.4, z: 13.2, rotY: 0.0, scale: 1.63 },
      { asset: 'picketFence', x: 12.2, z: 12.2, rotY: 0.0, scale: 1.55 },
      { asset: 'picketFence', x: -19.1, z: 10.8, rotY: 1.57, scale: 1.59 },
      { asset: 'picketFence', x: -19.8, z: 7.6, rotY: 1.57, scale: 1.67 },
      { asset: 'picketFence', x: -20.8, z: 13.3, rotY: 1.57, scale: 1.57 },
      { asset: 'ironFenceSection', x: -5.6, z: 28.9, rotY: 1.65, scale: 1.33 },
      { asset: 'ironFenceSection', x: -7.6, z: 31.1, rotY: 3.54, scale: 1.36 },
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
 ,

      // 10-03 change order 2: dirt-path lantern chain (every ~12m along the
      // path; joins existing posts at z 30 and z -2; fixed light pool auto-hooks)
      { asset: 'lanternPost', x: 5.04, z: 62.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: -3.36, z: 51.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: 2.6, z: 39.5, rotY: 0.0, scale: 2.4 },
      // order 3 forest (10-03): ring around graveyard (outside),
      // path alley, rim fill, dead accents - mixed healthy species
      { asset: 'yewTree', x: 10.09, y: 0.00, z: 39.59, rotY: 0.90, scale: 9.17 },
      { asset: 'yewTree', x: 13.43, y: 0.00, z: 36.39, rotY: 3.25, scale: 9.46 },
      { asset: 'witchwoodTree', x: 19.45, y: 0.00, z: 32.88, rotY: 1.91, scale: 10.41 },
      { asset: 'yewTree', x: 22.95, y: 0.00, z: 26.82, rotY: 4.36, scale: 9.16 },
      { asset: 'yewTree', x: 27.04, y: 0.00, z: 25.77, rotY: 4.36, scale: 9.65 },
      { asset: 'yewTree', x: 25.71, y: 0.00, z: 21.17, rotY: 5.30, scale: 8.52 },
      { asset: 'yewTree', x: 29.51, y: 0.00, z: 18.91, rotY: 4.30, scale: 9.70 },
      { asset: 'yewTree', x: 28.16, y: 0.00, z: 14.60, rotY: 0.28, scale: 9.64 },
      { asset: 'livingOak', x: 30.87, y: -1.57, z: 7.31, rotY: 4.33, scale: 9.82 },
      { asset: 'yewTree', x: 26.52, y: 0.00, z: -3.92, rotY: 3.01, scale: 9.90 },
      { asset: 'witchwoodTree', x: 21.93, y: 0.00, z: -10.21, rotY: 5.88, scale: 9.87 },
      { asset: 'yewTree', x: 17.79, y: 0.00, z: -11.16, rotY: 2.92, scale: 9.73 },
      { asset: 'yewTree', x: -6.20, y: 0.00, z: -17.34, rotY: 1.52, scale: 10.05 },
      { asset: 'yewTree', x: -12.93, y: 0.00, z: -17.42, rotY: 5.83, scale: 10.75 },
      { asset: 'witchwoodTree', x: -14.29, y: 0.00, z: -12.52, rotY: 1.90, scale: 8.82 },
      { asset: 'yewTree', x: -24.43, y: 0.00, z: -8.01, rotY: 2.41, scale: 8.73 },
      { asset: 'witchwoodTree', x: -24.57, y: 0.00, z: -3.33, rotY: 4.43, scale: 10.10 },
      { asset: 'yewTree', x: -26.77, y: 0.00, z: 2.16, rotY: 0.50, scale: 8.78 },
      { asset: 'yewTree', x: -27.54, y: 0.00, z: 6.47, rotY: 0.41, scale: 10.35 },
      { asset: 'livingOak', x: -29.75, y: -1.63, z: 10.41, rotY: 5.62, scale: 10.19 },
      { asset: 'livingOak', x: -28.27, y: -1.71, z: 16.41, rotY: 5.56, scale: 10.66 },
      { asset: 'livingOak', x: -29.82, y: -1.60, z: 20.75, rotY: 6.07, scale: 9.99 },
      { asset: 'livingOak', x: -26.92, y: -1.51, z: 24.25, rotY: 6.16, scale: 9.42 },
      { asset: 'livingOak', x: -26.15, y: -1.51, z: 28.48, rotY: 1.12, scale: 9.42 },
      { asset: 'yewTree', x: -21.42, y: 0.00, z: 29.64, rotY: 2.49, scale: 9.68 },
      { asset: 'witchwoodTree', x: -20.77, y: 0.00, z: 34.44, rotY: 1.53, scale: 9.91 },
      { asset: 'yewTree', x: -16.38, y: 0.00, z: 33.81, rotY: 5.21, scale: 8.51 },
      { asset: 'yewTree', x: -14.60, y: 0.00, z: 38.65, rotY: 4.31, scale: 9.54 },
      { asset: 'yewTree', x: -9.91, y: 0.00, z: 36.97, rotY: 1.14, scale: 9.72 },
      { asset: 'yewTree', x: 23.78, y: 0.00, z: 31.00, rotY: 4.33, scale: 8.81 },
      { asset: 'livingOak', x: 17.93, y: -1.69, z: 36.83, rotY: 0.95, scale: 10.54 },
      { asset: 'yewTree', x: -9.10, y: 0.00, z: 41.16, rotY: 2.50, scale: 8.98 },
      { asset: 'witchwoodTree', x: 22.57, y: 0.00, z: -5.39, rotY: 4.20, scale: 10.43 },
      { asset: 'yewTree', x: -31.91, y: 0.00, z: 28.49, rotY: 6.17, scale: 10.74 },
      { asset: 'livingOak', x: 24.50, y: -1.41, z: 39.30, rotY: 3.87, scale: 8.80 },
      { asset: 'witchwoodTree', x: -28.80, y: 0.00, z: -6.55, rotY: 0.83, scale: 8.67 },
      { asset: 'livingOak', x: -33.27, y: -1.53, z: 14.18, rotY: 2.82, scale: 9.58 },
      { asset: 'livingOak', x: -17.59, y: -1.56, z: -20.61, rotY: 6.06, scale: 9.72 },
      { asset: 'livingOak', x: -33.41, y: -1.43, z: 6.92, rotY: 6.09, scale: 8.92 },
      { asset: 'yewTree', x: 18.49, y: 0.00, z: -20.26, rotY: 0.73, scale: 9.43 },
      { asset: 'yewTree', x: -15.56, y: 0.00, z: 44.39, rotY: 4.45, scale: 9.08 },
      { asset: 'witchwoodTree', x: -21.84, y: 0.00, z: 41.43, rotY: 3.70, scale: 8.53 },
      { asset: 'yewTree', x: 12.06, y: 0.00, z: 44.64, rotY: 1.05, scale: 10.24 },
      { asset: 'witchwoodTree', x: 27.83, y: 0.00, z: -10.74, rotY: 5.68, scale: 8.65 },
      { asset: 'yewTree', x: 27.72, y: 0.00, z: 33.52, rotY: 5.85, scale: 9.50 },
      { asset: 'yewTree', x: -28.62, y: 0.00, z: -13.03, rotY: 4.86, scale: 8.55 },
      { asset: 'yewTree', x: 6.93, y: 0.00, z: 82.72, rotY: 1.45, scale: 10.21 },
      { asset: 'yewTree', x: -10.12, y: 0.00, z: 77.36, rotY: 3.54, scale: 10.09 },
      { asset: 'yewTree', x: -8.48, y: 0.00, z: 70.95, rotY: 3.89, scale: 10.29 },
      { asset: 'yewTree', x: 8.55, y: 0.00, z: 73.01, rotY: 0.60, scale: 9.88 },
      { asset: 'youngAsh', x: 8.91, y: -0.95, z: 64.05, rotY: 1.62, scale: 9.51 },
      { asset: 'youngAsh', x: -7.85, y: -0.90, z: 59.98, rotY: 4.10, scale: 8.95 },
      { asset: 'yewTree', x: 10.33, y: 0.00, z: 54.25, rotY: 1.08, scale: 9.79 },
      { asset: 'yewTree', x: -9.62, y: 0.00, z: 47.00, rotY: 2.10, scale: 9.98 },
      { asset: 'yewTree', x: 8.60, y: 0.00, z: 33.51, rotY: 4.98, scale: 10.12 },
      { asset: 'yewTree', x: 57.04, y: 0.00, z: -15.79, rotY: 2.90, scale: 9.27 },
      { asset: 'yewTree', x: -59.24, y: 0.00, z: -0.74, rotY: 2.93, scale: 9.73 },
      { asset: 'yewTree', x: 60.96, y: 0.00, z: 56.50, rotY: 6.11, scale: 9.80 },
      { asset: 'yewTree', x: -57.78, y: 0.00, z: 59.64, rotY: 2.87, scale: 9.29 },
      { asset: 'yewTree', x: -41.08, y: 0.00, z: 21.82, rotY: 4.32, scale: 9.33 },
      { asset: 'yewTree', x: 60.10, y: 0.00, z: 31.08, rotY: 1.40, scale: 9.58 },
      { asset: 'yewTree', x: 16.57, y: 0.00, z: 73.83, rotY: 1.37, scale: 9.70 },
      { asset: 'yewTree', x: -52.83, y: 0.00, z: 10.61, rotY: 5.48, scale: 9.20 },
      { asset: 'yewTree', x: 32.79, y: 0.00, z: 43.69, rotY: 1.16, scale: 9.12 },
      { asset: 'yewTree', x: 70.05, y: 0.00, z: 25.87, rotY: 3.84, scale: 10.48 },
      { asset: 'yewTree', x: 81.14, y: 0.00, z: -1.12, rotY: 0.50, scale: 9.25 },
      { asset: 'yewTree', x: 65.62, y: 0.00, z: -18.16, rotY: 2.96, scale: 8.96 },
      { asset: 'yewTree', x: -52.77, y: 0.00, z: 24.81, rotY: 3.24, scale: 10.59 },
      { asset: 'yewTree', x: -67.03, y: 0.00, z: -13.59, rotY: 5.40, scale: 10.35 },
      { asset: 'yewTree', x: 45.49, y: 0.00, z: 69.52, rotY: 5.29, scale: 9.06 },
      { asset: 'yewTree', x: 63.12, y: 0.00, z: -7.81, rotY: 4.66, scale: 10.46 },
      { asset: 'yewTree', x: 59.89, y: 0.00, z: 40.01, rotY: 1.88, scale: 9.53 },
      { asset: 'yewTree', x: -67.76, y: 0.00, z: 40.30, rotY: 0.76, scale: 10.22 },
      { asset: 'yewTree', x: -70.13, y: 0.00, z: 1.49, rotY: 0.38, scale: 9.85 },
      { asset: 'yewTree', x: -36.08, y: 0.00, z: 64.13, rotY: 0.08, scale: 8.52 },
      { asset: 'yewTree', x: 69.01, y: 0.00, z: 9.89, rotY: 5.47, scale: 10.26 },
      { asset: 'yewTree', x: -78.76, y: 0.00, z: 2.67, rotY: 3.41, scale: 10.39 },
      { asset: 'yewTree', x: -39.99, y: 0.00, z: 41.03, rotY: 1.04, scale: 9.43 },
      { asset: 'yewTree', x: -17.37, y: 0.00, z: 54.75, rotY: 2.74, scale: 8.35 },
      { asset: 'yewTree', x: -32.98, y: 0.00, z: 74.52, rotY: 3.10, scale: 9.64 },
      { asset: 'yewTree', x: 67.57, y: 0.00, z: 1.41, rotY: 3.78, scale: 8.71 },
      { asset: 'deadTree', x: 50.59, y: 0.00, z: 51.57, rotY: 6.05, scale: 8.18 },
      { asset: 'deadTree', x: 50.76, y: 0.00, z: 5.13, rotY: 5.28, scale: 8.50 },
      { asset: 'deadTree', x: 47.13, y: 0.00, z: -7.95, rotY: 3.05, scale: 8.41 },
      { asset: 'deadTree', x: -42.33, y: 0.00, z: -9.63, rotY: 5.02, scale: 8.95 },
      // 10-03 change order 2: darkwood forest ring - yew alley flanking the
      // dirt path, arc around the cemetery, rim scatter (trunk colliders are
      // automatic since R5; placement enforces spawn/enemy/corridor/path/prop
      // clearances; deterministic seed 20261003)
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
      { asset: 'livingOak', y: -1.28, x: 6.2, z: -46.4, rotY: 0.44, scale: 8.0 },
      { asset: 'witchwoodTree', x: -31.2, z: -50.3, rotY: 3.15, scale: 8.6 },
      { asset: 'livingOak', y: -1.28, x: 25.2, z: -73.8, rotY: 2.69, scale: 8.0 },
      { asset: 'livingOak', y: -1.35, x: -31.1, z: -68.7, rotY: 5.13, scale: 8.43 },
      { asset: 'witchwoodTree', x: 19.0, z: -54.7, rotY: 4.18, scale: 8.28 },
      { asset: 'witchwoodTree', x: -10.9, z: -55.8, rotY: 4.43, scale: 10.43 },
      { asset: 'livingOak', y: -1.44, x: -22.3, z: -59.2, rotY: 1.82, scale: 9.0 },
      { asset: 'deadTree', x: 35.5, z: -52.1, rotY: 2.09, scale: 9.85 },
      { asset: 'witchwoodTree', x: -18.1, z: -35.6, rotY: 0.99, scale: 8.0 },
      { asset: 'deadTree', x: -9.1, z: -35.8, rotY: 2.13, scale: 8.0 },
      { asset: 'yewTree', x: 21.9, z: -55.6, rotY: 5.57, scale: 8.38 },
      { asset: 'deadTree', x: 28.8, z: -55.3, rotY: 0.33, scale: 8.0 },
      { asset: 'yewTree', x: -31.3, z: -43.3, rotY: 3.91, scale: 10.4 },
      { asset: 'deadTree', x: 31.4, z: -48.7, rotY: 0.61, scale: 8.0 },
      { asset: 'yewTree', x: 19.4, z: -66.5, rotY: 1.34, scale: 9.18 },
      { asset: 'yewTree', x: -23.0, z: -47.8, rotY: 0.13, scale: 8.45 },
      { asset: 'witchwoodTree', x: -29.1, z: -72.5, rotY: 4.72, scale: 8.0 },
      { asset: 'yewTree', x: 13.4, z: -70.9, rotY: 4.67, scale: 9.43 },
      { asset: 'deadTree', x: -20.5, z: -42.5, rotY: 4.19, scale: 8.05 },
      { asset: 'livingOak', y: -1.28, x: -23.0, z: -39.2, rotY: 5.43, scale: 8.0 },
      { asset: 'yewTree', x: -37.4, z: -47.4, rotY: 3.99, scale: 8.12 },
      { asset: 'livingOak', y: -1.28, x: 23.5, z: -37.4, rotY: 4.81, scale: 8.0 },
      { asset: 'deadTree', x: 36.4, z: -37.1, rotY: 3.3, scale: 8.0 },
      { asset: 'witchwoodTree', x: -7.4, z: -41.5, rotY: 5.92, scale: 10.02 },
      { asset: 'yewTree', x: 27.7, z: -49.3, rotY: 2.97, scale: 9.75 },
      { asset: 'yewTree', x: 24.0, z: -61.4, rotY: 3.8, scale: 9.7 },
      { asset: 'yewTree', x: 7.8, z: -38.4, rotY: 2.24, scale: 8.0 },
      { asset: 'yewTree', x: 15.1, z: -49.5, rotY: 4.85, scale: 7.45 },
      { asset: 'deadTree', x: -31.1, z: -74.8, rotY: 0.61, scale: 8.68 },
      { asset: 'livingOak', y: -1.28, x: -22.9, z: -71.1, rotY: 0.72, scale: 8.0 },
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
      { asset: 'stoneCrossTilted', x: 18.0, z: -43.1, rotY: 6.16, scale: 1.6 },
      // R2: darkwood light-socket props (doc 61 batches B2/B3)
      { asset: 'banditCampfire', x: 2.5, z: -52, rotY: 0.0, scale: 1.8 },
      { asset: 'lanternWaymarker', x: -6.5, z: -47, rotY: 1.1, scale: 1.9 }
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

  // v7 "Weave Slice": focus pool, spells, belt, loadouts, armed finishers.
  player: {
    // (POC) scale: character model is ~2 units tall
    walkSpeed: 6.0,
    sprintSpeed: 10.0,
    sprintStaminaPerSec: 18.0,
    rollSpeed: 14.0,
    rollDuration: 0.45,               // seconds
    rollIFrameWindow: 0.35,           // seconds of i-frames within a roll
    rollStaminaCost: 25.0,
    // 10-04: player attack timing/damage/sweep/stamina moved to
    // CONFIG.moveset.weapons[*].moves (per-weapon moveset framework).
    staminaMax: 100.0,                // (doc 33 band)
    staminaRegenPerSec: 28.0,
    staminaRegenDelay: 0.6,           // seconds after spend before regen resumes
    hpMax: 100.0,
    hpRegenPerSec: 0.0,               // no passive regen in v1
    turnLerpDegPerSec: 720.0,         // body yaw turn rate toward move dir
    turnLerpDegPerSecAttackWindup: 720, // combat-ds1 P0-4: free turn during windup only
    radius: 0.7,                      // collision circle
    camDistance: 7.0,
    camMinDistance: 3.0,
    camMaxDistance: 14.0,
    camPitchMinDeg: -15,
    camPitchMaxDeg: 65,
    camHeight: 2.6,
    camGroundClearance: 0.4,          // R5 P0-5: camera y floor over the ground (y = 0)
    camPitchDistShrink: 0.35,         // R5: cap = camMaxDistance * (1 - k * max(0, sin pitch))
    camFollowLerp: 12.0,              // per-second lerp factor
    // 10-04 (Nicko): movement auto-follow keys removed - camera yaw is
    // manual-only (mouse drag / camera joystick); lock-on has its own framing.
    mouseSensDegPerPx: 0.25,
    respawnDelay: 2.2,                 // seconds on death screen before respawn
    // v7: focus pool (spells spend Focus, weapons spend Stamina)
    focusMax: 100,                    // max focus
    focusRegenPerSec: 8,              // focus regen per second after delay
    focusRegenDelay: 0.5,             // seconds after spend before regen resumes
    castFocusTaxMult: 1.25            // spell focus tax while weapon in main hand
  },

  // v7: bound spells (spell-in-hand battle-mage weave). kind picks the
  // WH_SPELLS.spawn class: 'projectile' = Firebolt, 'followLight' = Radiance.
  spell: {
    firebolt: {
      kind: 'projectile',
      focusCost: 8,                   // base focus cost (tax applied by player)
      damage: 12,                     // hp removed on enemy hit
      speed: 40,                      // projectile speed (units/s)
      hitRadius: 0.5,                 // collision circle radius vs enemy
      maxRange: 30,                   // lifetime = maxRange / speed
      castWindup: 0.25,               // seconds before the bolt spawns
      castCooldown: 0.3,              // seconds after cast before next cast
      schoolColor: 0xff7722,          // fire school color (offhand glow, HUD tint)
      name: 'Firebolt', glyph: 'FB',  // CHARACTER tab spell columns
      // 10-05 light radius order: per-hand light while a caster hand's
      // binding is firebolt (WH_PlayerLight, hand-bone anchor). Brightness
      // matched to the deleted R2 lantern (0xffb060 @6.5, d12): 0xff7722 has
      // ~0.65x the linear luminance of 0xffb060, so 10.0 here ~= 6.5 there
      light: { color: 0xff7722, intensity: 10.0, distance: 12, decay: 2, flickerPct: 5 },
      // in-flight glow, one pooled light per live bolt (CONFIG.playerLight.projectilePoolSize)
      projectileLight: { color: 0xff7722, intensity: 2.5, distance: 6, decay: 2, flickerPct: 8 }
    },
    // 10-04 (Nicko): key 2 light that follows the player for 60s. Once cast
    // it ignores the left hand entirely (stow / swap / Q / roll / death);
    // only expiry ends it. Recast = same light, timer back to full.
    radiance: {
      kind: 'followLight',
      focusCost: 10,                  // base focus cost (tax applied by player)
      castWindup: 0.3,                // seconds before the light appears
      castCooldown: 0.3,              // seconds after cast before next cast
      durationSeconds: 60,            // light lifetime from the last cast
      lightColor: 0xffb36b,           // warm white-amber
      // 2.2 read dim beside the (now deleted) 6.5 decay-2 lantern from 1.9m
      // up; 8.0 lights a ~6m ground pool
      lightIntensity: 8.0,
      lightDistance: 14,              // PointLight range cutoff
      lightDecay: 2,                  // physical falloff
      glowColor: 0xffd9a0,            // orb color
      schoolColor: 0xffd9a0,          // offhand glow + HUD tint while held
      name: 'Radiance', glyph: 'RD',  // CHARACTER tab spell columns
      light: null,                    // 10-05: no per-hand binding light (its cast follow-light is lightColor..)
      orbRadius: 0.14,
      orbSegments: [12, 8],           // sphere width / height segments
      // yawFrame-local (+X = body left, measured: L_Hand sits at +X and the
      // soles point +Z): above and left of the head
      anchorOffset: [0.45, 1.9, 0.1],
      bobAmp: 0.06,                   // vertical bob amplitude (m)
      bobHz: 0.5,                     // bob cycles per second
      fadeInSeconds: 0.4,             // fade up on cast / recast from parked
      fadeOutSeconds: 1.0             // fade down over the last N seconds
    }
  },

  // v7: the magic belt (5 abilities + 2 consumables, doc 04 ruling part C)
  belt: {
    slots: 5,                         // spell ability slots (keys 1-5)
    // boot belt = learned-spell quick slots; null = empty slot. Order C:
    // two bindings point into it - Digit1-5 = MAIN (right) hand, Shift+
    // Digit1-5 = OFF (left) hand; both start on slot 1
    defaultSpells: ['firebolt', 'radiance', null, null, null],
    regripSeconds: 0.3,               // re-grip busy window after selection
    consumableSlots: 2                // consumable slots (keys R / T)
  },

  // v7: loadout toggle (commit window, doc 04 ruling part C)
  loadout: {
    toggleSeconds: 0.8                // cannot attack/cast/block/roll during toggle
  },

  // v7: armed finishers (doc 04 ruling part A, slice simplification)
  armed: {
    windowSeconds: 3.5,               // armed state persistence window
    damageMult: 1.5,                  // armed finisher damage multiplier
    crossDamageMult: 2.0              // cross-finisher damage multiplier
  },

  // v7: belt consumables (active combat potions only, doc 04 ruling part C)
  consumable: {
    healthPotion: {
      heal: 40,                       // hp restored (never above hpMax)
      charges: 3                      // uses per refill
    }
  },

  // v6: block and parry (defense layer v1, HUD/DOM cues only)
  block: {
    parryWindow: 0.25,            // s, RMB-down parry window
    parryStaminaCost: 5,          // stamina spent on a successful parry
    absorb: 0.8,                  // fraction of damage negated on block (chip = 20%)
    staminaCostMult: 0.9,         // blocked hit drains damage * this
    blockArcHalfAngleDeg: 90,     // half-angle of the block/parry arc
    moveMult: 0.5,                // movement speed multiplier while blocking (fallback;
                                  // D-amend: the left-hand shield's items[id].block.moveMult wins)
    blockingRegenMult: 0.5,       // stamina regen rate multiplier while blocking
    guardBreakStun: 0.8,          // s, stun after guard break
    guardBreakMinStamina: 30,     // cannot block again until stamina >= this
    riposteMult: 1.75,            // next hit on a staggered enemy
    riposteStaggerDur: 1.25,      // s, enemy stagger after a parry
    parryFlashSeconds: 0.15,      // HUD white flash duration
    blockFlashSeconds: 0.12,      // HUD gray flash duration
    guardBreakFlashSeconds: 0.5,  // HUD red flash duration
    guardBreakTextSeconds: 1.4,   // GUARD BROKEN text pulse duration
    // Order D presentation only (Blender clips in combat-chain.glb, driven by
    // anim.js syncBlock). Hold = the clamped last frame of raise / impact /
    // swipe (all end on the same guard pose). Release / roll / shield loss
    // exit through the normal locomotion crossfade (animRt.crossfadeSeconds).
    blockAnim: {
      raiseCrossfadeSec: 0.06,      // locomotion -> WH_ShieldRaise (clip itself is 0.25s)
      impactCrossfadeSec: 0.03,     // hold -> WH_ShieldImpact on each blocked hit
      parryCrossfadeSec: 0.03,      // hold -> WH_ParrySwipe on a landed parry
      guardBreakCrossfadeSec: 0.06  // -> WH_GuardBreakStagger (0.79s vs guardBreakStun 0.8)
    },
    // Order D enemy feedback (presentation; attack FSM timing untouched).
    // Blocked or parried swing: the attacker recoils for this long.
    deflectEnemyRecoilSec: 0.15,
    deflect: {
      yawDeg: 18,                   // body twist toward its weapon side (snap, ease out)
      leanBackDeg: 10,              // body tips back
      weaponKnockDeg: 40,           // hand-held axe knocked about hand-local X (negate to flip)
      pushback: 0.25                // world units slid away from the player over the recoil
    },
    parryEnemyHitReact: true,       // parried enemy plays its WH_Hit once (stagger read on rigged bodies)
    // Riposte window marker under a parry-staggered enemy: shown while
    // isStaggered() && riposteArmed (riposteStaggerDur, gone once the riposte
    // lands). Amber = canon human-opportunity accent (equip consumable amber).
    riposteMarker: {
      color: 0xd8b24a,
      radius: 0.85,                 // outer radius (world units)
      width: 0.14,                  // ring thickness
      segments: 12,                 // low-poly = chunky/pixel read
      opacity: 0.9,                 // pulse peak
      pulseMin: 0.45,               // pulse trough (fraction of opacity)
      pulseHz: 3,
      endScale: 0.6,                // ring shrinks to this as the window closes
      yOffset: 0.04                 // above ground (avoid z-fight)
    }
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
      aggroPingInterval: 0.2,          // seconds between sense checks
      attackPhase: {                   // combat-ds1 P0-6: bandit telegraph and strike
        windup: 0.7,                   // combat-ds1 P0-6
        active: 0.12,                  // combat-ds1 P0-6
        recover: 0.8,                  // combat-ds1 P0-6
        hitArcDeg: 50,                 // combat-ds1 P0-6
        trackDegPerSec: 180            // combat-ds1 P0-6
      }
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
      aggroPingInterval: 0.2,
      attackPhase: {                   // combat-ds1 P0-6: ghoul telegraph and strike
        windup: 0.45,                  // combat-ds1 P0-6
        active: 0.12,                  // combat-ds1 P0-6
        recover: 0.5,                  // combat-ds1 P0-6
        hitArcDeg: 50,                 // combat-ds1 P0-6
        trackDegPerSec: 180            // combat-ds1 P0-6
      }
    },
    separationPush: 6.0,              // circle push-out strength
    holdAtBoundaryMargin: 1.5         // enemies stop this far before the boundary
  },

  hud: {
    regionNameFadeSeconds: 2.6,
    deathFadeSeconds: 0.8,
    fpsUpdateInterval: 0.5,
    // 2026-10-03 boot loading screen: overlay fade-out duration in ms.
    bootOverlayFadeMs: 900
  },

  lockOn: {
    maxDistance: 18.0,              // engage range (world units)
    hysteresis: 1.25,               // break at maxDistance * hysteresis
    facingConeDeg: 140,             // total cone around CAMERA forward
    camLerp: 6.0,                   // per-second lerp for the lock camera YAW aim
    trackWindupDegPerSec: 240,      // combat-ds1 P0-4: lock-on turn rate during attack windup
    // Order E1 (Nicko 10-05): RETIRED. The lock camera no longer re-anchors
    // at the player/enemy midpoint or zooms; it only aims yaw and keeps the
    // unlocked orbit distance/pitch. Legacy key kept at 0; nothing reads it.
    camExtraDistance: 0,
    // frameCheckNote (E2 AC): default orbit (camDistance 7, pitch 22deg,
    // camHeight 2.6, fov 60 -> 30deg half-vertical). Enemy feet at 18m ahead
    // sit ~10deg above screen center = in frame. Steep pitch pushes it up:
    // ~pitch > 50deg puts an 18m enemy past the top edge (player's own
    // pitch choice; reticle hides off-frame). Playtest is the real gate.
    reticleOffsetY: 0.9,            // reticle aim height above enemy feet
    // Order E2 (Nicko 10-05): lock-on only on enemies inside REAL light
    // (hand light / Radiance / world fire sockets; moonlight never counts).
    // Lock radius = light range * this: firebolt 12 -> 9.6m, Radiance
    // 14 -> 11.2m, world fire (lightPool.distance 11) -> 8.8m.
    lightRadiusFactor: 0.8,
    lightCheckIntervalSec: 0,       // light registry rebuild interval; 0 = every frame
    tooDarkText: 'Too dark to target',
    tooDarkToastSeconds: 1.2        // refusal toast lifetime (an enemy was in range but unlit)
  },

  animRt: {
    crossfadeSeconds: 0.18,
    oneShotFadeSeconds: 0.08,
    walkMetersPerCycle: 6,
    runMetersPerCycle: 6,
    attackClipStrikeFraction: 0.25
  },
  // v3: procedural animation feel (transform-only; assets are unrigged).
  // 10-04: stage durations + lunge are per move in CONFIG.moveset.weapons;
  // windup crouch / recover lean are per pose (WH_MOVESET crouch/bodyLean).
  anim: {
    attack: {
      windupLean: -0.25,            // rad, body rotation.x lean back
      windupSwordRaise: 0.9,        // rad, sword rotation.z lift in windup
      strikeYawSweepDeg: 140,       // total body yaw sweep through strike
      strikeSwordSweepDeg: 160      // sword arc through strike
    },
    walk: {
      bobAmp: 0.02,                 // primary vertical bob (R1 feet contact)
      bobFreqWalk: 9,               // rad/s phase rate
      bobFreqSprint: 14,
      leanWalk: 0.08,               // rad forward lean at walk speed
      leanSprint: 0.16,             // rad forward lean at sprint speed
      swayAmp: 0.05,                // lateral sway (position.x in body space)
      swayFreqMult: 0.5,            // half the bob frequency
      counterRollAmp: 0.05,         // rad rotation.z counter-roll
      yawOscAmp: 0.06,              // rad yaw oscillation at bob frequency
      footDipAmp: 0.005,            // secondary vertical sine (R1 contact)
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
    // Grey-stand-in resilience: rigged body loads retry on fetch/parse errors
    // with linear backoff before the stand-in swap; 0 disables retry. Failure
    // banner names asset + cause in console and HUD (see js/assets.js).
    bodyRetryCount: 2,                // extra attempts per rigged body (default on)
    bodyRetryDelayMs: 750,            // backoff base; delay = base * attempt#
    // R4 kill switch: true swaps the 3 rigged body atlases for the committed
    // 512px pixelated PNGs at postload; false = original 2048 atlas path.
    pixelatedBodies: true,
    standInColor: 0x777777,
    // Measured weapon sizing (2026-10-03, Nicko: weapons "comically large").
    // Targets are hand-held lengths in metres: longsword ~1.05m vs the 1.8m
    // player, handAxe ~0.6m. scaleFor(name) divides the target by the
    // MEASURED GROUND_META height of the loaded GLB - derived from bounds,
    // not magic constants. weaponScaleEnabled is the default-on kill switch.
    weaponScaleEnabled: true,
    // roundShield (10-04): 1.0m target / 2.0017 measured disc height
    // (raw ext 1.995 x 2.002 x 0.393) = scale 0.4996; inside the 0.9-scaled
    // player body that is a ~0.9m world diameter.
    // torch (10-05 asset mission): 0.62m target / 1.8988 measured height
    // (raw ext 0.334 x 1.899 x 0.334, scratch/torch_glb_check.py) = scale
    // 0.3265 - a one-hand torch about a third of the 1.8m player. Read only
    // once the code order gives items.torch a mesh + hand mount.
    weaponTargetHeight: { longsword: 1.05, handAxe: 0.6, roundShield: 1.0, torch: 0.62 },
    // Grip-mount tuning (2026-10-03): rollDeg rolls a hand-held weapon about
    // the hand's local +Z (grip forward; positive = CCW, right-hand rule)
    // with no code change. enabled:false reverts to the raw GLB axes for
    // asset debugging. One knob drives both the player sword and bandit axe.
    // gripHolderY (Nicko 10-03 "hilt at the opposite end" fix): post-
    // groundAlign holder-local Y of the weapon's GRIP point, measured from
    // the GLB. The longsword spans raw y -0.987..+1.001 (tip at -0.987,
    // crossguard +0.53, grip ~+0.65) and groundAlign shifts it +0.987, so
    // grip sits at holder y=1.637 while the mount had the TIP at the fist -
    // hand gripped mid-blade, hilt floating behind. The code subtracts this
    // value so the fist lands ON the grip. handAxe grip is its butt at
    // holder 0, already correct.
    weaponMount: { rollDeg: 0, enabled: true,
                   gripHolderY: { longsword: 1.637, handAxe: 0 } },
    // 10-04 left-hand shield mount (scratch/measure_shield.py, L_Hand at
    // WH_Idle frame 0). Vectors are L_Hand-local. faceAxis: where the boss
    // side (raw +Z) points = body-left turned 20 deg toward forward, level.
    // upAxis: where the disc's raw +Y points = world up. rollDeg: extra turn
    // about hand-local +Z (weaponMount convention). offset: hand-local spot
    // the shield's back-most point sits on = fist centroid [0.018, 0.078,
    // 0.021] pushed 0.042 (fist depth) + 0.01 along faceAxis; the L_Thigh
    // clears that plane by 0.027 at idle.
    shieldMount: { faceAxis: [-0.876, 0.4, 0.271], upAxis: [-0.327, -0.903, 0.277],
                   rollDeg: 0, offset: [-0.028, 0.099, 0.035] }
  }
};
// 10-04 change order (Nicko: combo spam -> real chains, souls-style).
// Per-weapon moveset framework: EVERY player combat number lives here. Pose
// SHAPES stay in js/moveset.js (window.WH_MOVESET keyframes) and are
// referenced by name via move.pose. Player swing rules (js/player.js):
//  - each swing runs its own windup -> strike -> recover (seconds below);
//  - LMB in windup is IGNORED; LMB in strike/recover is BUFFERED for
//    inputBufferSec and fires the next chain move once the swing is
//    chainOpenSec into its recover (never earlier - no skipped stages);
//  - the LAST chain move has no early window: a buffered press waits for
//    its full recover, then starts a fresh chain at chain[0];
//  - roll may cancel RECOVER only (never windup/strike) and resets the chain.
// chainCap = moves per chain AND landed hits that arm the v7 finisher.
window.WH_CONFIG.moveset = {
  idlePose: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
  banditStageMult: 1.6,
  enemyWeapon: { bandit: 'handAxe' },
  playerWeapon: 'longsword',        // which weapons[] entry the player wields
  inputBufferSec: 0.35,             // buffered LMB lifetime (strike/recover presses)
  weapons: {
    longsword: {
      chainCap: 3,
      // Nicko's order: swipe right->left, swipe left->right, THRUST, reset.
      chain: ['slashR2L', 'slashL2R', 'thrust'],
      // movement speed multiplier per swing stage (windup keeps 0.3 creep)
      moveMultWhileAttacking: { windup: 0.3, strike: 0, recover: 0 },
      bladeAxisY: -1,               // mesh-local blade axis (-Y tip, see setWeapon)
      moves: {
        slashR2L: { pose: 'm2', windup: 0.14, strike: 0.20, recover: 0.30,
                    chainOpenSec: 0.12,
                    damage: 34, range: 3.2, halfAngleDeg: 70, lunge: 0.8,
                    staminaCost: 15, damageGhoulMult: 1.15 },
        slashL2R: { pose: 'm1', windup: 0.14, strike: 0.20, recover: 0.30,
                    chainOpenSec: 0.12,
                    damage: 34, range: 3.2, halfAngleDeg: 70, lunge: 0.8,
                    staminaCost: 15, damageGhoulMult: 1.15 },
        // thrust = narrow, longer reach, more damage, heavier recover
        thrust:   { pose: 'm4', windup: 0.16, strike: 0.14, recover: 0.40,
                    chainOpenSec: 0.40,   // last move: full recover anyway
                    damage: 40, range: 3.8, halfAngleDeg: 22, lunge: 1.4,
                    staminaCost: 20, damageGhoulMult: 1.15 }
      }
    },
    // Quick 2-hit hatchet chain: faster, shorter, lower damage per hit.
    handAxe: {
      chainCap: 2,
      chain: ['hack', 'chop'],
      moveMultWhileAttacking: { windup: 0.4, strike: 0, recover: 0 },
      bladeAxisY: 1,                // axe bit along mesh-local +Y (as enemy.js)
      moves: {
        hack: { pose: 'claw', windup: 0.10, strike: 0.14, recover: 0.22,
                chainOpenSec: 0.08,
                damage: 22, range: 2.6, halfAngleDeg: 60, lunge: 0.5,
                staminaCost: 10, damageGhoulMult: 1.15 },
        chop: { pose: 'm3', windup: 0.12, strike: 0.14, recover: 0.30,
                chainOpenSec: 0.30,
                damage: 27, range: 2.7, halfAngleDeg: 35, lunge: 0.7,
                staminaCost: 12, damageGhoulMult: 1.15 }
      }
    }
  }
};

// 2026-10-03 touch controls layer (parallel input; see js/touch-controls.js).
// enabled:false keeps the layer hidden until the edge toggle is used - the
// mouse/keyboard path stays the primary control surface, untouched.
window.WH_CONFIG.touch = {
  enabled: false,                 // layer hidden until toggle button used
  opacity: 0.35,                  // faint outlines
  deadzone: 0.15,                 // stick deadzone (fraction of radius)
  scaleDefault: 1.0,              // global control scale
  scaleMin: 0.6,
  scaleMax: 1.6,
  buttonSize: 64,                 // px diameter of action buttons at scale 1
  joystickRadius: 70,             // px radius of stick/camera circles at scale 1
  sensDegPerPx: 0.25,             // camera pad sens (matches mouseSensDegPerPx)
  // Default layout: fractions of viewport (0-1), resize-safe. Movement stick
  // bottom-left, camera pad bottom-right, action cluster right side.
  layout: {
    stick:    { x: 0.18, y: 0.72 },
    cam:      { x: 0.82, y: 0.72 },
    sprint:   { x: 0.68, y: 0.62 },
    attack:   { x: 0.90, y: 0.45 },
    lockon:   { x: 0.72, y: 0.82 },
    dodge:    { x: 0.55, y: 0.88 },
    block:    { x: 0.90, y: 0.65 }
  }
};

// 2026-10-05 inventory Order A (Nicko 10-04): possession system, separate
// from the belt (belt = casting, inventory = possession; keys 1-5 / Q are
// untouched). Fixed N-slot grid, per-item stack caps, stacks join on pickup.
window.WH_CONFIG.inventory = {
  slots: 24,                        // fixed grid size, growable later
  defaultStackCap: 60,              // consumables/ingredients without their own stackCap
  // fresh-spawn kit (boot only; death keeps the inventory, no persistence yet).
  // Order B (magic canon 10-05): no spell charges - spells are knowledge.
  // CONFIG.equip.defaultHands pulls its items OUT of this kit into the hands
  // at boot, so the grid starts with the shield + bandage only.
  startingItems: [
    { id: 'magicGlove', count: 1 },
    { id: 'magicGlove', count: 1 },   // Order C: glove #2 (stays in the grid; dual-cast kit)
    { id: 'longsword', count: 1 },
    { id: 'roundShield', count: 1 },
    { id: 'bandage', count: 1 }
  ],
  drop: {
    mode: 'physical',               // 'physical' (item entity at feet) | 'void' (delete + toast)
    scatterRadius: 1.75,            // m, dropped items land up to this far from the player
    pickupRadius: 1.6               // m, E collects the nearest item entity within this
  },
  // placeholder world item visual (box, unlit so it reads at night; art pass later)
  entity: {
    size: 0.28,                     // m, box edge
    spinDegPerSec: 70,              // slow yaw spin so drops catch the eye
    colors: {                       // one accent per category
      consumable: 0xd8b24a,         // amber (canon fire/human accent)
      gear: 0x4ac8d8,               // cyan
      valuable: 0x9ff0f0,           // stage 2: pale cyan (Stolen Coin; vendor/currency not built)
      ingredient: 0x7cb860          // stage 2: moss green (gathered cooking ingredients)
    }
  }
};

// Stage 2 (Nicko 10-05): enemy drops. ONE shared pool for both enemy types
// (bandit + ghoul drop exactly the same things). Every kill: the guaranteed
// stack, plus a bonusChance roll into the weighted bonusPool (weight / sum).
// Cooking ingredients NEVER drop from enemies (gather nodes + wild animals
// only). Drops spawn as ordinary WorldItems boxes (same E pickup / region
// gating) at the corpse x/z, spawnDelaySec after the kill. No despawn yet.
window.WH_CONFIG.drops = {
  bonusChance: 0.20,                // per kill
  bonusPool: [                      // weighted pick (torch most common, glove rare)
    { id: 'torch', weight: 50 },
    { id: 'bandage', weight: 30 },
    { id: 'magicGlove', weight: 8 }
  ],
  guaranteed: { id: 'stolenCoin', count: 1 },
  spawnDelaySec: 0.6,               // drop pops shortly after the corpse settles
  bonusOffset: 0.45                 // m, bonus box sits this far from the coin (no overlap)
};

// Item registry. ids are canonical (stage 2 enemy drops + gatherables reuse
// it). Consumables omit stackCap -> CONFIG.inventory.defaultStackCap; gear = 1.
// Order B gear data (read by inventory.js + player.js):
//   kind        'caster' | 'melee' | 'shield' | 'torch' - the ONLY thing
//               combat code keys off (player.handAction per hand, Order C);
//               'torch' has no hand action (its button is inert - NOT a
//               caster) and exists for its light stat
//   hands       which hands it may enter ('right' / 'left'; one item per hand)
//   equipHint   default hand for a plain click on the CHARACTER tab
//   cast        casting implement data; powerTier glove 1 < wand 2 < staff 3
//               (wands/staffs come later - nothing scales off it yet)
//   moveset     melee: key into CONFIG.moveset.weapons (right-hand chain)
//   mesh        WH_ASSETS name of the hand-held model (none = no mesh yet)
//   light       10-05: { color, intensity, distance, decay, flickerPct } -
//               while held, that hand's follow light (WH_PlayerLight) uses
//               these values, winning over the hand's spell-binding light
//   block       shield: { moveMult } - walk-speed multiplier while blocking
//               with it in the left hand (D-amend weight class: buckler 0.75
//               / medium 0.5 / tower 0.25); absent = CONFIG.block.moveMult
//   kind melee/shield without a mesh refuses to equip ('No visual - asset
//   pending') except via WH_DEBUG.equipItem(id, hand, fromInv, true)
// Spells are KNOWLEDGE (magic canon 10-05), never items or charges; books /
// scrolls (learn-on-read) are a later category.
window.WH_CONFIG.items = {
  bandage:        { id: 'bandage', name: 'Bandage', glyph: 'BD',
                    category: 'consumable', useHint: { kind: 'heal', amount: 25 } },
  magicGlove:     { id: 'magicGlove', name: 'Magic Glove', glyph: 'MG',
                    category: 'gear', stackCap: 1, kind: 'caster',
                    hands: ['left', 'right'], equipHint: 'leftHand',
                    cast: { powerTier: 1 } },
  longsword:      { id: 'longsword', name: 'Longsword', glyph: 'LS',
                    category: 'gear', stackCap: 1, kind: 'melee', moveset: 'longsword', mesh: 'longsword',
                    hands: ['right', 'left'], equipHint: 'rightHand' },
  roundShield:    { id: 'roundShield', name: 'Round Shield', glyph: 'SH',
                    category: 'gear', stackCap: 1, kind: 'shield', mesh: 'roundShield',
                    hands: ['right', 'left'], equipHint: 'leftHand',
                    block: { moveMult: 0.5 } },                 // medium
  // DORMANT shield classes (D-amend 10-05): no mesh / mount yet, no drop
  // source - stage 2 drops. Data only.
  buckler:        { id: 'buckler', name: 'Buckler', glyph: 'BK',
                    category: 'gear', stackCap: 1, kind: 'shield',
                    hands: ['right', 'left'], equipHint: 'leftHand',
                    block: { moveMult: 0.75 } },                // light
  towerShield:    { id: 'towerShield', name: 'Tower Shield', glyph: 'TS',
                    category: 'gear', stackCap: 1, kind: 'shield',
                    hands: ['right', 'left'], equipHint: 'leftHand',
                    block: { moveMult: 0.25 } },                // heavy
  // Torch (10-05 asset mission): either hand, no block. Its light stat wins
  // over that hand's spell light (torch + glove = both lights live). Light
  // ~1.3x firebolt's feel (firebolt 10.0 / 12m) - playtest tunes these.
  // No mesh key yet: the gather/drop code order adds mesh: 'torch'
  // (MANIFEST.torch) with its hand mount, and the drop source.
  torch:          { id: 'torch', name: 'Torch', glyph: 'TR',
                    category: 'gear', stackCap: 1, kind: 'torch',
                    hands: ['left', 'right'], equipHint: 'leftHand',
                    light: { color: 0xffa040, intensity: 10.5, distance: 15,
                             decay: 2, flickerPct: 7 } },
  // Stage 2 enemy drop (CONFIG.drops.guaranteed). 'valuable' = new category;
  // vendor / currency systems are NOT built - it only stacks for now.
  stolenCoin:     { id: 'stolenCoin', name: 'Stolen Coin', glyph: 'SC',
                    category: 'valuable', stackCap: 999 }
};

// Order B (2026-10-05) free per-hand equip. Hands are equip-screen driven;
// belt keys 1-5 only pick the active learned spell.
window.WH_CONFIG.equip = {
  // boot: these leave the starting kit and go straight into the hands
  defaultHands: { right: 'longsword', left: 'magicGlove' },
  // Order C two-button combat (supersedes Order B's rmbOrder): each mouse
  // button acts with ONE hand. 'mainHand' = right hand: longsword -> attack
  // chain, caster -> cast the main binding, else inert. 'offHand' = left
  // hand: caster -> cast the off binding, roundShield -> hold-to-block,
  // else inert. A shield blocks only from the left hand; a melee weapon
  // swings only from the right. Touch attack button = lmb, block = rmb.
  twoHand: { lmb: 'mainHand', rmb: 'offHand' },
  // Q = left-hand swap between these two items (0.8s CONFIG.loadout window)
  qSwap: ['magicGlove', 'roundShield'],
  // Each item's mount (weaponMount / shieldMount) is measured for its NATIVE
  // hand. The other hand gets the mount mirrored by this hand-local factor:
  // L_Hand <-> R_Hand local frames map by diag(-1, 1, 1) within 0.01
  // (scratch/measure_hand_mirror.py, bind pose). Roll angles flip sign.
  nativeHand: { longsword: 'right', roundShield: 'left', magicGlove: 'left' },
  mirrorScale: [-1, 1, 1],
  // Magic glove placeholder (no glove mesh this order): the spell glow orb
  // on the caster hand. anchor 'hand' = child of the hand bone at
  // handOffset (fist centroid in the nativeHand.magicGlove bone's frame,
  // scratch/measure_shield.py; mirrored for the other hand); 'idlePose' = the old yawFrame anchor (weapon idle
  // pose, mirrored per hand). Order C: perHand = one orb on EACH hand
  // holding a caster, colored by that hand's binding (false = one orb, left
  // first); casts spawn from the casting hand's orb. windupScale = orb size
  // at the end of a windup (grows from 1, per-hand cast cue).
  casterGlow: { anchor: 'hand', handOffset: [0.018, 0.078, 0.021],
                perHand: true, windupScale: 1.8 }
};

// Inventory screen (DOM modal). While open, player movement/combat input is
// suspended (the world keeps running).
window.WH_CONFIG.inventoryUI = {
  openKey: 'KeyI',
  closeKeys: ['KeyI', 'Escape'],
  dropKey: 'KeyG',                  // drop 1 of the selected stack; Shift+G = whole stack
  pickupKey: 'KeyE',                // world: collect the nearest item entity in pickupRadius
  gridCols: 6,                      // 24 slots -> 6 x 4
  toastSeconds: 1.8,                // "Dropped X x1" / "Inventory full" toast lifetime
  // Order B: clickable HUD button, same toggle as the I key. left / bottom
  // are px from the viewport's bottom-left corner.
  openButton: { enabled: true, label: 'INV', left: 16, bottom: 20 }
};
