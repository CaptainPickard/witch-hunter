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
    // R2 P0-3 moon-and-lantern night rig: AmbientLight removed entirely - the
    // hemisphere is the only fill, and region.ambientLightLevel scales it
    // (region fill = hemiBaseIntensity * ambientLightLevel). Moon = cool
    // directional on the -z side backlighting the A->B main path. Lantern =
    // warm PointLight parented into the player's yawFrame (left-hip anchor).
    ambientIntensity: 0,              // P0-3: AmbientLight removed (kept for backward-compat readers; must stay 0)
    hemiSkyColor: 0x4a5a80,           // indigo-slate sky (audit 5.3)
    hemiGroundColor: 0x16181e,        // near-black ground (audit 5.3)
    hemiBaseIntensity: 1.35,          // fill at ambientLightLevel 1.0; region fill = base * level
    moonColor: 0xa8bce6,              // cool moon (audit 5.3)
    moonIntensity: 0.45,              // moon:fill (vertical faces) 3-5:1
    moonAzimuthDeg: 0,                // -z side, backlights A->B main path
    moonElevationDeg: 30,             // audit: 25-35 deg
    lanternColor: 0xffb060,           // warm amber (audit 5.3; canon accent)
    lanternIntensity: 6.5,            // audit 5.3: 6-8 cd class
    lanternDistance: 12,              // audit: distance ~12
    lanternDecay: 2,                  // physical falloff
    lanternFlickerPct: 5,             // +-5% flicker band
    lanternAnchor: 'left-hip',        // yawFrame-space anchor
    lanternAnchorOffset: [-0.32, 0.95, 0.08] // tuned starting anchor
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
      zFrom: 86.0,                    // south rim start (inside playable 88.5)
      zTo: -23.5,                     // just past the gate mouth, before plane
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
      { type: 'ghoul', x: 2, z: -23.5 }
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
      { asset: 'picketFence', x: 15.4, z: 13.2, rotY: 0.0, scale: 1.63 },
      { asset: 'picketFence', x: 12.2, z: 12.2, rotY: 0.0, scale: 1.55 },
      { asset: 'picketFence', x: -19.1, z: 10.8, rotY: 1.57, scale: 1.59 },
      { asset: 'picketFence', x: -19.8, z: 7.6, rotY: 1.57, scale: 1.67 },
      { asset: 'picketFence', x: -20.8, z: 13.3, rotY: 1.57, scale: 1.57 },
      { asset: 'ironFenceSection', x: -5.6, z: 28.9, rotY: 1.65, scale: 1.33 },
      { asset: 'ironFenceSection', x: -7.6, z: 31.1, rotY: 3.54, scale: 1.36 },
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
 ,

      // 10-03 change order 2: dirt-path lantern chain (every ~12m along the
      // path; joins existing posts at z 30 and z -2; fixed light pool auto-hooks)
      { asset: 'lanternPost', x: 5.04, z: 62.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: -3.36, z: 51.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: 2.6, z: 39.5, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: -2.77, z: 20.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: 2.77, z: 8.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: -3.62, z: -5.0, rotY: 0.0, scale: 2.4 },
      { asset: 'lanternPost', x: 5.16, z: -16.5, rotY: 0.0, scale: 2.4 },
      // 10-03 change order 2: darkwood forest ring - yew alley flanking the
      // dirt path, arc around the cemetery, rim scatter (trunk colliders are
      // automatic since R5; placement enforces spawn/enemy/corridor/path/prop
      // clearances; deterministic seed 20261003)
      { asset: 'yewTree', x: 8.28, z: 82.89, rotY: 3.76, scale: 10.37 },
      { asset: 'yewTree', x: -9.66, z: 82.84, rotY: 1.88, scale: 10.57 },
      { asset: 'yewTree', x: -11.24, z: 78.37, rotY: 6.18, scale: 10.81 },
      { asset: 'yewTree', x: 7.46, z: 77.48, rotY: 6.27, scale: 10.15 },
      { asset: 'yewTree', x: -10.73, z: 72.26, rotY: 0.03, scale: 10.45 },
      { asset: 'yewTree', x: 6.75, z: 69.97, rotY: 1.5, scale: 9.86 },
      { asset: 'yewTree', x: -7.94, z: 65.29, rotY: 4.95, scale: 10.54 },
      { asset: 'yewTree', x: 11.87, z: 58.48, rotY: 2.39, scale: 10.84 },
      { asset: 'yewTree', x: -8.15, z: 58.37, rotY: 0.25, scale: 10.98 },
      { asset: 'yewTree', x: 54.94, z: 58.16, rotY: 1.74, scale: 8.88 },
      { asset: 'yewTree', x: -52.64, z: 57.44, rotY: 2.87, scale: 8.49 },
      { asset: 'yewTree', x: -40.75, z: 52.9, rotY: 3.2, scale: 10.03 },
      { asset: 'yewTree', x: 8.37, z: 52.65, rotY: 2.43, scale: 10.78 },
      { asset: 'yewTree', x: 48.08, z: 51.74, rotY: 0.66, scale: 8.17 },
      { asset: 'yewTree', x: -44.69, z: 47.44, rotY: 5.35, scale: 8.56 },
      { asset: 'yewTree', x: 36.91, z: 45.69, rotY: 1.14, scale: 9.99 },
      { asset: 'yewTree', x: 47.09, z: 45.09, rotY: 4.79, scale: 9.24 },
      { asset: 'yewTree', x: -11.15, z: 44.52, rotY: 1.95, scale: 10.62 },
      { asset: 'yewTree', x: 57.4, z: 41.78, rotY: 1.62, scale: 8.3 },
      { asset: 'yewTree', x: -48.37, z: 41.42, rotY: 1.65, scale: 8.45 },
      { asset: 'yewTree', x: 68.78, z: 38.69, rotY: 5.5, scale: 8.07 },
      { asset: 'yewTree', x: -10.91, z: 38.5, rotY: 6.12, scale: 10.2 },
      { asset: 'yewTree', x: 37.35, z: 36.45, rotY: 1.78, scale: 10.02 },
      { asset: 'yewTree', x: 60.52, z: 36.24, rotY: 5.66, scale: 8.55 },
      { asset: 'yewTree', x: 30.53, z: 35.85, rotY: 2.41, scale: 8.25 },
      { asset: 'yewTree', x: 48.44, z: 34.8, rotY: 4.18, scale: 8.08 },
      { asset: 'yewTree', x: -57.86, z: 34.51, rotY: 3.1, scale: 8.17 },
      { asset: 'yewTree', x: -28.1, z: 32.04, rotY: 1.53, scale: 8.48 },
      { asset: 'yewTree', x: 34.77, z: 31.8, rotY: 0.02, scale: 8.71 },
      { asset: 'yewTree', x: 7.78, z: 31.7, rotY: 0.11, scale: 10.82 },
      { asset: 'yewTree', x: -39.02, z: 29.84, rotY: 3.47, scale: 9.9 },
      { asset: 'yewTree', x: 50.98, z: 29.81, rotY: 1.7, scale: 8.1 },
      { asset: 'yewTree', x: 76.11, z: 29.32, rotY: 1.77, scale: 8.42 },
      { asset: 'yewTree', x: 22.23, z: 29.09, rotY: 2.41, scale: 8.52 },
      { asset: 'yewTree', x: 9.62, z: 26.67, rotY: 3.91, scale: 9.85 },
      { asset: 'yewTree', x: -66.88, z: 26.1, rotY: 1.41, scale: 8.91 },
      { asset: 'yewTree', x: -55.31, z: 25.79, rotY: 1.61, scale: 8.95 },
      { asset: 'yewTree', x: 63.43, z: 25.64, rotY: 5.0, scale: 9.18 },
      { asset: 'yewTree', x: -33.79, z: 25.33, rotY: 0.97, scale: 9.59 },
      { asset: 'yewTree', x: 33.24, z: 25.21, rotY: 3.61, scale: 10.25 },
      { asset: 'yewTree', x: -9.37, z: 24.89, rotY: 5.03, scale: 10.24 },
      { asset: 'yewTree', x: 56.92, z: 23.78, rotY: 3.17, scale: 10.44 },
      { asset: 'yewTree', x: -40.2, z: 23.54, rotY: 5.76, scale: 10.07 },
      { asset: 'yewTree', x: 70.96, z: 23.47, rotY: 2.16, scale: 9.35 },
      { asset: 'yewTree', x: 26.01, z: 23.25, rotY: 3.81, scale: 8.72 },
      { asset: 'yewTree', x: 48.98, z: 22.33, rotY: 4.56, scale: 10.2 },
      { asset: 'yewTree', x: 42.33, z: 22.26, rotY: 4.55, scale: 9.46 },
      { asset: 'yewTree', x: -74.39, z: 21.0, rotY: 1.99, scale: 9.76 },
      { asset: 'yewTree', x: 17.1, z: 20.4, rotY: 3.88, scale: 8.98 },
      { asset: 'yewTree', x: -37.26, z: 19.14, rotY: 0.69, scale: 8.92 },
      { asset: 'yewTree', x: 37.65, z: 18.11, rotY: 3.64, scale: 8.75 },
      { asset: 'yewTree', x: 76.06, z: 16.57, rotY: 5.13, scale: 10.23 },
      { asset: 'yewTree', x: 62.22, z: 16.06, rotY: 0.23, scale: 9.82 },
      { asset: 'yewTree', x: -25.09, z: 15.84, rotY: 3.88, scale: 9.86 },
      { asset: 'yewTree', x: 26.48, z: 15.06, rotY: 4.79, scale: 9.23 },
      { asset: 'yewTree', x: -45.1, z: 14.9, rotY: 5.04, scale: 8.88 },
      { asset: 'yewTree', x: -30.3, z: 14.39, rotY: 3.91, scale: 8.95 },
      { asset: 'yewTree', x: -51.29, z: 13.61, rotY: 6.09, scale: 10.11 },
      { asset: 'yewTree', x: -60.14, z: 12.23, rotY: 3.5, scale: 8.21 },
      { asset: 'yewTree', x: 31.15, z: 12.05, rotY: 4.48, scale: 9.32 },
      { asset: 'yewTree', x: 68.83, z: 11.69, rotY: 4.4, scale: 9.53 },
      { asset: 'yewTree', x: 75.02, z: 9.87, rotY: 5.88, scale: 8.73 },
      { asset: 'yewTree', x: -29.18, z: 8.27, rotY: 0.62, scale: 9.44 },
      { asset: 'yewTree', x: 62.61, z: 6.97, rotY: 2.16, scale: 9.91 },
      { asset: 'yewTree', x: -72.74, z: 6.81, rotY: 4.24, scale: 10.4 },
      { asset: 'yewTree', x: 28.27, z: 6.47, rotY: 6.09, scale: 9.75 },
      { asset: 'yewTree', x: 44.1, z: 6.4, rotY: 2.13, scale: 9.54 },
      { asset: 'yewTree', x: -58.23, z: 5.13, rotY: 2.25, scale: 10.19 },
      { asset: 'yewTree', x: 49.45, z: 4.63, rotY: 0.54, scale: 10.02 },
      { asset: 'yewTree', x: 77.0, z: 4.25, rotY: 5.07, scale: 8.31 },
      { asset: 'yewTree', x: 54.08, z: 1.63, rotY: 1.86, scale: 9.49 },
      { asset: 'yewTree', x: 66.8, z: 1.56, rotY: 0.01, scale: 8.17 },
      { asset: 'yewTree', x: 82.25, z: 0.43, rotY: 0.88, scale: 8.74 },
      { asset: 'yewTree', x: -19.94, z: -0.55, rotY: 0.89, scale: 8.85 },
      { asset: 'yewTree', x: -10.53, z: -0.91, rotY: 2.42, scale: 10.67 },
      { asset: 'yewTree', x: -51.96, z: -0.98, rotY: 3.83, scale: 9.18 },
      { asset: 'yewTree', x: 24.07, z: -1.14, rotY: 2.57, scale: 9.56 },
      { asset: 'yewTree', x: -25.86, z: -1.21, rotY: 3.81, scale: 9.74 },
      { asset: 'yewTree', x: 39.41, z: -2.83, rotY: 1.03, scale: 8.71 },
      { asset: 'yewTree', x: -79.46, z: -3.25, rotY: 3.09, scale: 8.82 },
      { asset: 'yewTree', x: -59.88, z: -4.85, rotY: 0.26, scale: 9.7 },
      { asset: 'yewTree', x: 33.4, z: -5.26, rotY: 4.86, scale: 8.93 },
      { asset: 'yewTree', x: -20.61, z: -5.92, rotY: 4.04, scale: 9.82 },
      { asset: 'yewTree', x: 61.57, z: -6.77, rotY: 5.11, scale: 8.41 },
      { asset: 'yewTree', x: 80.94, z: -7.2, rotY: 6.25, scale: 8.47 },
      { asset: 'yewTree', x: -51.29, z: -7.39, rotY: 1.87, scale: 8.49 },
      { asset: 'yewTree', x: -30.81, z: -7.39, rotY: 3.83, scale: 9.01 },
      { asset: 'yewTree', x: -75.06, z: -8.58, rotY: 0.23, scale: 9.96 },
      { asset: 'yewTree', x: -68.08, z: -10.21, rotY: 1.9, scale: 8.41 },
      { asset: 'yewTree', x: 45.3, z: -10.35, rotY: 4.63, scale: 10.42 },
      { asset: 'yewTree', x: -26.99, z: -11.51, rotY: 3.44, scale: 9.25 },
      { asset: 'yewTree', x: -39.06, z: -12.51, rotY: 4.06, scale: 8.6 },
      { asset: 'yewTree', x: 34.28, z: -12.69, rotY: 0.63, scale: 9.69 },
      { asset: 'yewTree', x: 40.47, z: -13.48, rotY: 0.66, scale: 10.34 },
      { asset: 'yewTree', x: 77.54, z: -13.74, rotY: 5.68, scale: 9.8 },
      { asset: 'yewTree', x: -10.36, z: -14.15, rotY: 5.2, scale: 9.99 },
      { asset: 'yewTree', x: 27.88, z: -14.51, rotY: 1.31, scale: 8.57 },
      { asset: 'yewTree', x: -49.27, z: -16.17, rotY: 5.11, scale: 9.54 },
      { asset: 'yewTree', x: 22.7, z: -16.44, rotY: 1.74, scale: 9.01 },
      { asset: 'yewTree', x: -11.23, z: -19.5, rotY: 2.22, scale: 10.07 },
      { asset: 'yewTree', x: -39.94, z: -19.71, rotY: 3.26, scale: 9.23 },
      { asset: 'yewTree', x: 72.75, z: -19.83, rotY: 2.65, scale: 9.21 },
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
      { asset: 'yewTree', x: 6.2, z: -46.4, rotY: 0.44, scale: 8.0 },
      { asset: 'yewTree', x: -31.2, z: -50.3, rotY: 3.15, scale: 8.6 },
      { asset: 'yewTree', x: 25.2, z: -73.8, rotY: 2.69, scale: 8.0 },
      { asset: 'yewTree', x: -31.1, z: -68.7, rotY: 5.13, scale: 8.43 },
      { asset: 'yewTree', x: 19.0, z: -54.7, rotY: 4.18, scale: 8.28 },
      { asset: 'yewTree', x: -10.9, z: -55.8, rotY: 4.43, scale: 10.43 },
      { asset: 'yewTree', x: -22.3, z: -59.2, rotY: 1.82, scale: 9.0 },
      { asset: 'yewTree', x: 35.5, z: -52.1, rotY: 2.09, scale: 9.85 },
      { asset: 'yewTree', x: -18.1, z: -35.6, rotY: 0.99, scale: 8.0 },
      { asset: 'yewTree', x: -9.1, z: -35.8, rotY: 2.13, scale: 8.0 },
      { asset: 'yewTree', x: 21.9, z: -55.6, rotY: 5.57, scale: 8.38 },
      { asset: 'yewTree', x: 28.8, z: -55.3, rotY: 0.33, scale: 8.0 },
      { asset: 'yewTree', x: -31.3, z: -43.3, rotY: 3.91, scale: 10.4 },
      { asset: 'yewTree', x: 31.4, z: -48.7, rotY: 0.61, scale: 8.0 },
      { asset: 'yewTree', x: 19.4, z: -66.5, rotY: 1.34, scale: 9.18 },
      { asset: 'yewTree', x: -23.0, z: -47.8, rotY: 0.13, scale: 8.45 },
      { asset: 'yewTree', x: -29.1, z: -72.5, rotY: 4.72, scale: 8.0 },
      { asset: 'yewTree', x: 13.4, z: -70.9, rotY: 4.67, scale: 9.43 },
      { asset: 'yewTree', x: -20.5, z: -42.5, rotY: 4.19, scale: 8.05 },
      { asset: 'yewTree', x: -23.0, z: -39.2, rotY: 5.43, scale: 8.0 },
      { asset: 'yewTree', x: -37.4, z: -47.4, rotY: 3.99, scale: 8.12 },
      { asset: 'yewTree', x: 23.5, z: -37.4, rotY: 4.81, scale: 8.0 },
      { asset: 'yewTree', x: 36.4, z: -37.1, rotY: 3.3, scale: 8.0 },
      { asset: 'yewTree', x: -7.4, z: -41.5, rotY: 5.92, scale: 10.02 },
      { asset: 'yewTree', x: 27.7, z: -49.3, rotY: 2.97, scale: 9.75 },
      { asset: 'yewTree', x: 24.0, z: -61.4, rotY: 3.8, scale: 9.7 },
      { asset: 'yewTree', x: 7.8, z: -38.4, rotY: 2.24, scale: 8.0 },
      { asset: 'yewTree', x: 15.1, z: -49.5, rotY: 4.85, scale: 7.45 },
      { asset: 'yewTree', x: -31.1, z: -74.8, rotY: 0.61, scale: 8.68 },
      { asset: 'yewTree', x: -22.9, z: -71.1, rotY: 0.72, scale: 8.0 },
      { asset: 'yewTree', x: 29.8, z: -76.9, rotY: 0.5, scale: 9.68 },
      { asset: 'yewTree', x: -28.4, z: -79.9, rotY: 4.96, scale: 9.8 },
      { asset: 'yewTree', x: -16.0, z: -76.7, rotY: 3.09, scale: 9.45 },
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
    camAutoFollowDelay: 1.2,          // seconds after manual drag before auto-follow resumes
    camAutoFollowRate: 2.5,           // per-second exp lerp for auto yaw follow
    mouseSensDegPerPx: 0.25,
    respawnDelay: 2.2,                 // seconds on death screen before respawn
    // v7: focus pool (spells spend Focus, weapons spend Stamina)
    focusMax: 100,                    // max focus
    focusRegenPerSec: 8,              // focus regen per second after delay
    focusRegenDelay: 0.5,             // seconds after spend before regen resumes
    castFocusTaxMult: 1.25            // spell focus tax while weapon in main hand
  },

  // v7: bound spells (spell-in-hand battle-mage weave, ONE spell in slice)
  spell: {
    firebolt: {
      focusCost: 8,                   // base focus cost (tax applied by player)
      damage: 12,                     // hp removed on enemy hit
      speed: 40,                      // projectile speed (units/s)
      hitRadius: 0.5,                 // collision circle radius vs enemy
      maxRange: 30,                   // lifetime = maxRange / speed
      castWindup: 0.25,               // seconds before the bolt spawns
      castCooldown: 0.3,              // seconds after cast before next cast
      schoolColor: 0xff7722           // fire school color (offhand glow, HUD tint)
    }
  },

  // v7: the magic belt (5 abilities + 2 consumables, doc 04 ruling part C)
  belt: {
    slots: 5,                         // spell ability slots (keys 1-5)
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
    camLerp: 6.0,                   // per-second lerp for lock camera follow
    trackWindupDegPerSec: 240,      // combat-ds1 P0-4: lock-on turn rate during attack windup
    camExtraDistance: 3.5,           // camera pulls back this much past target dist
    reticleOffsetY: 0.9             // reticle aim height above enemy feet
  },

  animRt: {
    crossfadeSeconds: 0.18,
    oneShotFadeSeconds: 0.08,
    walkMetersPerCycle: 6,
    runMetersPerCycle: 6,
    attackClipStrikeFraction: 0.25
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
    weaponTargetHeight: { longsword: 1.05, handAxe: 0.6 },
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
                   gripHolderY: { longsword: 1.637, handAxe: 0 } }
  }
};
window.WH_CONFIG.moveset = {
  idlePose: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
  comboChainCap: 3,
  banditStageMult: 1.6,
  enemyWeapon: { bandit: 'handAxe' }
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
