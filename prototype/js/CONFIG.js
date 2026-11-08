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

  // WH_POSTPASS_V1: ship the post pipeline with creative channels at identity/off.
  post: {
    enabled: true,
    regions: {
      hold_outskirts: { lift: [0.0, 0.0, 0.0], gamma: 1.0, gain: [1.0, 1.0, 1.0] },
      darkwood_edge: { lift: [0.0, 0.0, 0.0], gamma: 1.0, gain: [1.0, 1.0, 1.0] },
      forest_of_the_old_king: { lift: [0.0, 0.0, 0.0], gamma: 1.0, gain: [1.0, 1.0, 1.0] }
    },
    dither: { enabled: false, strength: 0.5 },
    grain: { enabled: false, strength: 0.5, speedSeconds: 0.25, sizePx: 1 },
    vignette: { enabled: false, radius: 0.72, softness: 0.35, strength: 0.35 }
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
  // Round D2: offset = [x, z] glTF-local (pre-rotY, pre-scale), measured from
  // GLB vertex bands (scratch/lantern_head_probe.py) so the light sits in the
  // hanging head: waymarker glass z +0.23..+0.47 @ 55-79% H. Intensities
  // matched to the player torch (10.5) for ground-pool parity under physical
  // decay 2. Round K: lantern-post-v2 tops the pillar (no side arm): glass
  // x -0.123..+0.127, z -0.116..+0.112 @ 75.5-87.5% H, centre within 2 mm
  // of the pillar axis (scratch/lantern_head_probe_roundK.py). Old post was
  // { heightFraction: 0.72, offset: [-0.18, 0.0] }. Round L: lantern-post-v3
  // hangs its cage from the arm's hook, OFF the pillar axis (pillar on the
  // glTF origin): cage floor 70% H, glass to 82.5% (cap brim 82.5-85%),
  // centre x -0.299, z 0.000 on every cage band
  // (scratch/lantern_head_probe_roundL.py). v2 was
  // { heightFraction: 0.81, offset: [0.0, 0.0] }.
  lightSockets: {
    lanternPost:      { heightFraction: 0.76, intensity: 9.0,
                        offset: [-0.30, 0.0] },
    banditCampfire:   { heightFraction: 0.55, intensity: 3.2,
                        offset: [0.0, 0.0] },
    // CK1: deployed-kit firepit (CONFIG.camp.assets.fire glb). groundHeight
    // is the WHOLE kit (~1.56 m, the tent) -> 0.25 = ~0.39 m above the pit;
    // offset [0, 0] = the firepit sits on the module origin (makePiece
    // counter-offset).
    whCampkit:        { heightFraction: 0.25, intensity: 3.2,   // PROPOSED
                        offset: [0.0, 0.0] },
    lanternWaymarker: { heightFraction: 0.67, intensity: 9.5,
                        offset: [0.0, 0.35] },
    // CC-B1 (2026-11-07): ruined-chapel altar candelabra (doc 61 P1-2). Joins
    // region B's warm family — banditCampfire + lanternWaymarker + this — per
    // the single-accent law (art-order 2026-11-06): one amber accent family
    // per region; all three ruin-cluster seats ≤ 25 m apart. heightFraction
    // 0.85 up the 1.98 m (× 0.45 scale) candelabrum = flame ≈ 1.9–2.0 m,
    // riding the altar-top y. WAKE-34 IO AMENDMENT: computeFireSockets
    // (game.js ~2904) computes h = groundHeight * scale * hf from GROUND
    // level — row y is NOT read — so the altar-top STACK needs
    // hf = (3.415 row y + 0.76 flame) / (1.98*0.45) = 4.175 / 0.891 ≈ 4.69
    // to put the flame at its intended ≈ 4.18 m seat (3.415 stack base + 0.76
    // flame).
    candelabra:       { heightFraction: 4.69, intensity: 5.5,   // PROPOSED
                        offset: [0.0, 0.0] },
    // Round F: gate-arch lantern (WORLD socket, both regions; not a region
    // prop). heightFraction is up the HUNG lantern's height from its base;
    // offset [x, z] is arch-local in meters (rotated with arch.rotY).
    // region-manager wallPlan().sockets -> game.js computeSockets.
    b3Gate:           { heightFraction: 0.45, intensity: 5.0,
                        offset: [0.0, 0.0] }
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
    spawn: { x: 2.5, z: 74.0 },       // Round H: south wall x path, halfway to first lantern
    gravityY: -22,
    fogColor: 0x9aa0a3,               // pale ash grey, whiter (darkwood canon)
    fogDensity: 0.012,                // heavier, lower fog (darkwood canon)
    // Round H: cemetery fog ramp (game.js cemeteryFogTick, region A only).
    // zone = the scatter keepOut ellipse with this regionId (the graveyard).
    // d = normalized ellipse distance (1 = rim); weight w = smoothstep from 0
    // at d = rampStart to 1 at d = rampEnd; fog density/color lerp from the
    // region base (fogDensity/fogColor above) toward these by w.
    cemeteryFog: {
      zoneKeepOutRegionId: 'hold_outskirts',
      density: 0.030,
      color: 0x7f8ea6,                // pale cool blue-grey
      rampStart: 1.35,
      rampEnd: 0.55
    },
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
      { asset: 'lanternPost', x: -2, z: 30, rotY: 0.0, scale: 2.535 },
      { asset: 'lanternPost', x: 4, z: -2, rotY: 0.0, scale: 2.535 },
      // CC-C13b fence normalization: one scale per asset (picket 1.40, iron 1.35), rotY re-seated per run; x/z unchanged
      { asset: 'picketFence', x: 15.4, z: 13.2, rotY: 0.0, scale: 1.40 },
      { asset: 'picketFence', x: 12.2, z: 12.2, rotY: 0.0, scale: 1.40 },
      { asset: 'picketFence', x: -19.1, z: 10.8, rotY: 1.57, scale: 1.40 },
      { asset: 'picketFence', x: -19.8, z: 7.6, rotY: 1.57, scale: 1.40 },
      { asset: 'picketFence', x: -20.8, z: 13.3, rotY: 1.57, scale: 1.40 },
      { asset: 'ironFenceSection', x: -5.6, z: 28.9, rotY: 3.97, scale: 1.35 },
      { asset: 'ironFenceSection', x: -7.6, z: 31.1, rotY: 3.97, scale: 1.35 },
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
      { asset: 'lanternPost', x: 5.04, z: 62.0, rotY: 0.0, scale: 2.535 },
      { asset: 'lanternPost', x: -3.36, z: 51.0, rotY: 0.0, scale: 2.535 },
      { asset: 'lanternPost', x: 2.6, z: 39.5, rotY: 0.0, scale: 2.535 },
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
      { asset: 'reachTreeA', x: 21.93, y: 0.00, z: -10.21, rotY: 5.88, scale: 9.87 },
      { asset: 'yewTree', x: 17.79, y: 0.00, z: -11.16, rotY: 2.92, scale: 9.73 },
      { asset: 'yewTree', x: -6.20, y: 0.00, z: -17.34, rotY: 1.52, scale: 10.05 },
      { asset: 'yewTree', x: -12.93, y: 0.00, z: -17.42, rotY: 5.83, scale: 10.75 },
      { asset: 'witchwoodTree', x: -14.29, y: 0.00, z: -12.52, rotY: 1.90, scale: 8.82 },
      { asset: 'yewTree', x: -24.43, y: 0.00, z: -8.01, rotY: 2.41, scale: 8.73 },
      { asset: 'reachTreeB', x: -24.57, y: 0.00, z: -3.33, rotY: 4.43, scale: 10.10 },
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
      { asset: 'reachTreeC', x: 22.57, y: 0.00, z: -5.39, rotY: 4.20, scale: 10.43 },
      { asset: 'yewTree', x: -31.91, y: 0.00, z: 28.49, rotY: 6.17, scale: 10.74 },
      { asset: 'livingOak', x: 24.50, y: -1.41, z: 39.30, rotY: 3.87, scale: 8.80 },
      { asset: 'witchwoodTree', x: -28.80, y: 0.00, z: -6.55, rotY: 0.83, scale: 8.67 },
      { asset: 'livingOak', x: -33.27, y: -1.53, z: 14.18, rotY: 2.82, scale: 9.58 },
      { asset: 'livingOak', x: -17.59, y: -1.56, z: -20.61, rotY: 6.06, scale: 9.72 },
      { asset: 'livingOak', x: -33.41, y: -1.43, z: 6.92, rotY: 6.09, scale: 8.92 },
      { asset: 'yewTree', x: 18.49, y: 0.00, z: -20.26, rotY: 0.73, scale: 9.43 },
      { asset: 'yewTree', x: -15.56, y: 0.00, z: 44.39, rotY: 4.45, scale: 9.08 },
      { asset: 'reachTreeA', x: -21.84, y: 0.00, z: 41.43, rotY: 3.70, scale: 8.53 },
      // Round I6: 6 reach-trees deliberately placed along the path corridor
      // (Nicko: 'still no different trees' - none stood near the walked
      // path). Deterministic spots: even z-steps, alternating sides, 8-11m
      // off the centerline, clash-checked vs every prop collider.
      { asset: 'reachTreeA', x: 7.16,  y: 0.00, z: 38.00, rotY: 0.60, scale: 8.90 },
      { asset: 'reachTreeB', x: -12.57, y: 0.00, z: 42.50, rotY: 1.07, scale: 9.40 },
      { asset: 'reachTreeC', x: 7.29,  y: 0.00, z: 49.50, rotY: 1.54, scale: 9.10 },
      { asset: 'reachTreeA', x: -6.82, y: 0.00, z: 56.50, rotY: 2.01, scale: 8.90 },
      { asset: 'reachTreeB', x: 8.44,  y: 0.00, z: 67.50, rotY: 2.48, scale: 9.40 },
      { asset: 'reachTreeC', x: -7.29, y: 0.00, z: 66.50, rotY: 2.95, scale: 9.10 },
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
    ],
    // Stage 2 gather nodes (CONFIG.gather.nodeTypes; js/gather.js). Open
    // forest floor only: clear of the dirt path (+2.5m), the cemetery +
    // its tree ring, props (trees 4m / others 3m), enemy spawns (5m), the
    // player spawn (6m), the gate corridor (z > -17); 9m apart.
    // scratch/gen_gather_nodes.py, seed 20261005. In the real game each
    // type's list is its PLACEMENT POOL (see CONFIG.gather.economy).
    nodes: [
      { type: 'herbBundle', x: 59.8, z: 23.1 },
      { type: 'herbBundle', x: 13.5, z: 58.4 },
      { type: 'herbBundle', x: -54.7, z: -15.4 },
      { type: 'herbBundle', x: -54.5, z: 44.3 },
      { type: 'herbBundle', x: 21.3, z: 71.0 },
      { type: 'herbBundle', x: 39.8, z: 43.1 },
      { type: 'deadwoodPile', x: 69.4, z: 16.4 },
      { type: 'deadwoodPile', x: 70.8, z: -3.8 },
      { type: 'deadwoodPile', x: -34.3, z: 42.0 },
      { type: 'deadwoodPile', x: -40.0, z: 4.6 },
      // C1 CEMETERY ECOLOGY (Nicko 10-05): mushrooms grow ONLY around burial
      // grounds - woodland just past the cemetery tree ring (in_graveyard
      // ellipse d 1.06..1.13), never the open yard; W / E / SW / S of the
      // yard. Same clearances (props >= 4.1m, enemies >= 20m, nodes >= 11m,
      // spawn >= 36m, path + 2.5m). Was x 38 / 59 / 68.5 east field + x -60.
      { type: 'mushroomCluster', x: -37.1, z: 19.9 },
      { type: 'mushroomCluster', x: 37.3, z: -4.0 },
      { type: 'mushroomCluster', x: -29.7, z: 32.0 },
      { type: 'mushroomCluster', x: 20.1, z: 42.6 }
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
      { asset: 'reachTreeB', x: -31.2, z: -50.3, rotY: 3.15, scale: 8.6 },
      { asset: 'livingOak', y: -1.28, x: 25.2, z: -73.8, rotY: 2.69, scale: 8.0 },
      { asset: 'livingOak', y: -1.35, x: -31.1, z: -68.7, rotY: 5.13, scale: 8.43 },
      { asset: 'witchwoodTree', x: 19.0, z: -54.7, rotY: 4.18, scale: 8.28 },
      { asset: 'reachTreeC', x: -10.9, z: -55.8, rotY: 4.43, scale: 10.43 },
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
      { asset: 'reachTreeA', x: -29.1, z: -72.5, rotY: 4.72, scale: 8.0 },
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
      { asset: 'reachTreeB', x: 29.8, z: -76.9, rotY: 0.5, scale: 9.68 },
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
      // CC-C13b fence/gate normalization: one scale per asset (gate 1.62, picket 1.40), rotY re-seated per run; x/z unchanged
      { asset: 'cemeteryGate', x: 25.8, z: -42.0, rotY: 0.0, scale: 1.62 },
      { asset: 'cemeteryGate', x: 20.1, z: -50.4, rotY: 0.0, scale: 1.62 },
      { asset: 'picketFence', x: 22.1, z: -53.0, rotY: 1.57, scale: 1.40 },
      { asset: 'picketFence', x: -27.4, z: -51.6, rotY: 1.57, scale: 1.40 },
      { asset: 'gravestoneObelisk', x: 13.1, z: -41.5, rotY: 3.73, scale: 1.38 },
      { asset: 'gravestoneObelisk', x: 20.1, z: -40.0, rotY: 0.14, scale: 1.38 },
      { asset: 'stoneCrossTilted', x: -13.5, z: -36.6, rotY: 5.5, scale: 1.22 },
      { asset: 'stoneCrossTilted', x: 18.0, z: -43.1, rotY: 6.16, scale: 1.6 },
      // R2: darkwood light-socket props (doc 61 batches B2/B3)
      { asset: 'banditCampfire', x: 2.5, z: -52, rotY: 0.0, scale: 1.8 },
      { asset: 'lanternWaymarker', x: -6.5, z: -47, rotY: 1.1, scale: 1.9 },
      // CC-B1 (2026-11-07): ruined-chapel landmark, doc 61 P1-2 (WAKE 34) —
      // io/specs/cc-b1-chapel-spec.md. Nave ≈ (0,-58), long axis W-E, BROADSIDE
      // to the south-entry walk: lit altar visible down the 33 m axis. Assembles
      // AROUND the locked ruin rows (archway 8,-58 / buttress -14,-62 /
      // pewBroken 16,-52 / campfire 2.5,-52 / waymarker -6.5,-47) — none moved.
      // Cool monochrome masonry; ONE amber pool from the candelabra (single-accent).
      // K1 west face: 2x wall windows along z at x -18 (IO wake-34 seat pass:
      // -17.5 row line probed DEAD — bonePile (-17.0,-53.1) and graveMoss
      // (-14.4,-66.6) node rings + the reachTreeC at (-10.9,-55.8) leave only
      // z -65..-56.5 clear), planes facing EAST into the nave (rotY 1.57),
      // scale 2.2 (~2.87 m run, ~2.0 m tall each). The ≈ 5 m centre gap is an
      // INTENTIONAL walk-through (marked // gap).
      { asset: 'churchWallWindow', x: -18, z: -63, rotY: 1.57, scale: 2.2 },
      // gap — west face ruined section (walk-through; centre gap ≈ 5 m)
      { asset: 'churchWallWindow', x: -18, z: -58, rotY: 1.57, scale: 2.2 },
      // K2 south fragment: free-standing buttress (IO seat pass: the SW angle
      // is owned by the bonePile node ring + reachTreeC; this seat keeps
      // ≥ 3 m from both node rings and ≥ 1 m from the scattered reach tree)
      { asset: 'churchCornerButtress', x: -11.8, z: -52, rotY: 5.7, scale: 2.0 },
      // K3 north face: 2x wall windows at z -66, planes facing SOUTH into the
      // nave (rotY ≈ 3.14); the ≈ 5.6/7.0 m openings between/beside them are
      // the ruined gable walk-throughs
      { asset: 'churchWallWindow', x: -3.5, z: -66, rotY: 3.14, scale: 2.2 },
      // gap — north face ruined section (walk-through)
      { asset: 'churchWallWindow', x: 3.5, z: -66, rotY: 3.14, scale: 2.2 },
      // K4 interior: pulpit faces WEST toward the nave (rotY -1.57); IO
      // wake-34 FINAL seat (5,-63): the first seat (10.5,-62) failed the NW
      // locked-buttress floor (gap 0.71); (5,-64.5) failed the north-window
      // ring (win3 gap 0.97). FINAL clears win3 1.55, win4 3.25, bandit 3.61,
      // archway 6.26, altar 8.16, beams (raised, exempt), waymarker 2.62
      { asset: 'churchPulpit', x: 5, z: -63, rotY: -1.57, scale: 2.0 },
      // K4: second pew + intact pew REJECTED at review (probe: no legal seat —
      // the archway/stump/node clearance web owns the east interior);
      // churchPewBroken (16,-52) + the banditCampfire camp stand in
      // congregational wear per the scene-01 ossuary anchor
      // K5 ALTAR END: altar face points WEST into the nave; scale 2.2 =>
      // 4.4 m wide, 1.16*2.2 = 2.55 m tall GLB bbox run (table top ≈ 1.16*2.2/2)
      { asset: 'churchAltar', x: 14.5, z: -58, rotY: -1.57, scale: 2.2 },
      // K5: candelabra ON the altar (same x/z, R3 stack exemption — this pair
      // overlaps on purpose). Hosted-stack seat: y = altar-top plane below.
      // Measured GLB groundMinY (cc-b1 trimesh probe) = -0.5974 at scale 1 =>
      // altar top at 2.2 = (1.1612 + 0.5974) * 2.2 ≈ 3.867 m above its ground
      // plane; candelabra groundMinY -1.0042 * 0.45 ≈ -0.452 re-seats its feet
      // to that plane: y ≈ 3.415. (No-probe fallback was y 2.1; the measured
      // value wins per spec R3.)
      { asset: 'candelabra', x: 14.5, z: -58, rotY: -1.57, scale: 0.45, y: 3.415 },
      // K6 gable fragment ABOVE the altar end: broken window in the collapsed
      // gable (scene-01 moonbeam read), raised + noCollide (raised-row grammar);
      // floor-level gable seating was probed and REJECTED (collides with the
      // LOCKED pewBroken + altar circle). IO wake-34 FINAL: altar-stack x/z
      // (14.5,-58) y 2.15 — V-WAKE34 A1: y/nocollide rows are R1/R2-exempt;
      // the R3 interior rule (raised circle not covering altar/pulpit centres
      // within 1 m) is scoped to WALKABLE-FLOOR raised rows (beams); the stack
      // pair + gable window sit INSIDE the altar's own circle by design
      { asset: 'churchWindowFrame', x: 14.5, z: -58, rotY: 1.57, scale: 1.0, y: 2.15, noCollide: true },
      // K7 roof: 2x churchRoofBeam ACROSS the nave (rotY ≈ ±1.57 so the ~1.98 m
      // length runs along z), scale 7.2 => ~14.2 m span (seats z -65..-51),
      // raised y 3.9/4.0, noCollide (CC-C8 raised-row grammar) — the surviving
      // west-half rafters over the nave
      { asset: 'churchRoofBeam', x: -6, z: -58, rotY: 1.57, scale: 7.2, y: 4.0, noCollide: true },
      { asset: 'churchRoofBeam', x: -2, z: -58, rotY: -1.57, scale: 7.2, y: 3.9, noCollide: true },
      // K8 fallen rafter: GROUND debris — keeps its collider circle (r ≈ 2.57 m
      // at 2.6), no y, no noCollide. IO wake-34 FINAL seat (7,-69) rotY 2.5
      // north face — old (−9,−55) failed campfire/bandit floors; (18,-49.5)
      // failed the yewTree (15.1,-49.5) + mossBoulder (17.1,-52.8) rings.
      // FINAL clears: win4 0.61 (wall floor 0.6), yewTree (13.4,-70.9) 2.32,
      // pulpit 2.67, bandit 8.8, ghoul 16.5, campfire 15.0, archway 11.05,
      // BC door 14.7, keepOut ellipse e 0.886
      { asset: 'churchRoofBeam', x: 7, z: -69, rotY: 2.5, scale: 2.6 },
      // K9 nave dressing: west-half rubble; IO wake-34 FINAL seats (probe
      // floors vs LOCKED buttress/fallenLog rings)
      { asset: 'rubblePile', x: -13.5, z: -59.5, rotY: 0.7, scale: 1.3 },
      { asset: 'rubblePile', x: -6.4, z: -64, rotY: 4.1, scale: 1.2 }
    ],
    // Stage 2 gather nodes: darkwood band (|x| < 42, z -82..-31), clear of
    // props 3-4m / enemies 5m / spawn 6m, 6m apart (gen_gather_nodes.py)
    nodes: [
      { type: 'graveMoss', x: -32.9, z: -39.1 },
      { type: 'graveMoss', x: 38.3, z: -57.4 },
      { type: 'graveMoss', x: -33.7, z: -62.2 },
      { type: 'graveMoss', x: -14.4, z: -66.6 },
      { type: 'graveMoss', x: -12.7, z: -48.1 },
      { type: 'bonePile', x: 31.7, z: -63.2 },
      { type: 'bonePile', x: -41.7, z: -54.4 },
      { type: 'bonePile', x: -17.0, z: -53.1 },
      { type: 'bonePile', x: -2.7, z: -52.4 }
    ]
  },

  // CC-C2 (io/missions/2026-10-07-cc-c2-region-shell.md, docs/planning/62):
  // Region C, Forest of the Old King. Its OWN disc (center (0, -366), playable
  // radius groundRadius - world.playerMargin = 278.5) north of the shared A/B
  // disc; C spans z -646..-86. Reached ONLY through the B/C door on B's north
  // edge (plane z = -86, window |x - doorX| <= doorHalfWidth; region-defs
  // connections[1]). Tutorial law: the door is locked while the day/night
  // clock is dormant (first camp Save and Heal = beginCycle). FLAT stub ground
  // (heightfield = CC-C4). Every row below is PROPOSED, Nicko tunes.
  regionC: {
    id: 'forest_of_the_old_king',
    name: 'Forest of the Old King',
    center: { x: 0, z: -366 },        // PROPOSED, Nicko tunes (doc 62 sec 1 arithmetic)
    groundRadius: 280,                // PROPOSED, Nicko tunes (R-62.2 band 250-300; A/B read world.groundRadius 90)
    groundY: -0.05,                   // PROPOSED, Nicko tunes (stub disc under B's y = 0: no z-fight). CC-C4: with terrain.enabled C walks on the heightfield mesh; this disc survives only as the flat SKIRT under/outside the 560 m mesh square (visual radius 400), never walked
    groundColor: 0x1a2116,            // PROPOSED, Nicko tunes (CC-C3 old-king floor: deeper mossy loam, dominant; CC-C2 0x1e2319)
    groundColor2: 0x28261a,           // PROPOSED, Nicko tunes (CC-C3 deeper leaf-litter umber, secondary; CC-C2 0x2c2a1d)
    groundSeed: 1662061217,           // PROPOSED, Nicko tunes (ground canvas PRNG seed)
    // CC-C4a FLORA PASS (R-62.7, io/missions/2026-10-08-cc-c4a-flora-roads.md):
    // Round E scatter ON for C through per-region override rows laid over
    // CONFIG.scatter (region-manager whScatterCfg: one level deep, object keys
    // merge, arrays/numbers replace). A/B carry no override row = CONFIG.scatter
    // itself, byte-identical. Instances seat on WH_GROUND.heightAt (exact).
    // TYPO LAW (assets.js grep 2026-10-08): bushA bushB bramble whBushSnare
    // grassTuft mossBoulder deadTree are manifest keys; moonbell bracken
    // leaves pebbles stonefrags stoneSingle are NOT (GLBs on disk, no manifest
    // row) - their layers are SKIPPED until IO adds the rows; each is then
    // one groundLayers row (moonbell colonies, leaves/pebbles spreads) or a
    // freeBushes asset row (bracken). "Roses" v1 = the snare bush's ash-rose
    // vertex paint in the giant rings + bushB/bramble + grass colonies.
    scatterOverrides: {
      // CC-C4b floraMaxH: no scatter instance (trees, rings, bushes, grass,
      // colonies) on ground higher than this (natural hills top out at hMax 5
      // + the Stone pad 2.7): the cliff band stays bare rock. PROPOSED, Nicko tunes
      clear: { spawnM: 14, floraMaxH: 6 },  // PROPOSED, Nicko tunes (arrival glade stays open ground)
      // the Stone plaza (assembly + ring road) keeps its breathing room;
      // CC-C4b: the three notch mouths (window halfWidth 10 + shoulder 8)
      keepOut: [{ regionId: 'forest_of_the_old_king', x: 0, z: -366, rx: 30, rz: 30 },
        { regionId: 'forest_of_the_old_king', x: 0, z: -596, rx: 18, rz: 18 },
        { regionId: 'forest_of_the_old_king', x: 240, z: -366, rx: 18, rz: 18 },
        { regionId: 'forest_of_the_old_king', x: -240, z: -366, rx: 18, rz: 18 },
        // CC-C8: the rot mother's outcrop face (no random trunks / bushes in it)
        { regionId: 'forest_of_the_old_king', x: -136, z: -219, rx: 22, rz: 18 }],
      // NO auto trees: giants are hand rows (CC-C3), the 55 m law holds
      treesExtra: { targetCount: { forest_of_the_old_king: 0 } },
      bushes: {
        // free bushes in the gaps (bracken weight 3 lands with its manifest row)
        assets: [['bramble', 1, 1.6, 2.4], ['bushB', 2, 1.0, 1.6], ['bushA', 2, 0.9, 1.4]],
        // rings at EVERY giant: radius = trunk r (width * scale / 2 * 0.25,
        // scale-aware) * radiusFrac; bigger bodies than A/B so a ring reads
        // at the base of a 50 m giant. Snare (ash-rose roses) weighted 2.
        // count [2, 4] (brief proposed [3, 6]): the 2M tri ledger (cullShowFrac row)
        // pathM: rings keep scatter.clear.pathM (6 m) off every road centerline
        atTreeRing: { count: [2, 4], radiusFrac: [1.1, 1.8], pathM: 6,
          assets: [['bushA', 1, 1.2, 2.0], ['bushB', 1, 1.4, 2.4], ['whBushSnare', 2, 1.4, 2.2]] },
        // CC-C4b: x 0.8144 = the playable disc's share below floraMaxH (the
        // bare ring would otherwise push its share inward: same interior
        // density as C4a, the 2M ledger holds). C4a: freeBushes 40, grass 320,
        // tuftColonies clusters 36.
        freeBushes: 33
      },
      grass: { count: 261 },
      // ground colonies (region-manager whScatterPlan step 5): clusters of
      // perCluster items within spreadM; nearTreeFrac of the colony seeds
      // start in a giant's trunk band (treeBandFrac x trunk r), the rest in
      // clearings. v1 = grass-tuft colonies; moonbell/leaves/pebbles rows
      // join here once manifest keys exist.
      groundLayers: [
        { id: 'tuftColonies', asset: 'grassTuft', clusters: 29, perCluster: [3, 8],
          spreadM: 5, height: [0.5, 0.95], nearTreeFrac: 0.5, treeBandFrac: [2.2, 4.0] }
      ]
    },
    spawn: { x: 0, z: -96 },          // PROPOSED, Nicko tunes (10 m inside C's south rim, the L0 glade)
    gravityY: -22,
    fogColor: 0x59625b,               // PROPOSED, Nicko tunes (deep-forest green-grey)
    fogDensity: 0.033,                // PROPOSED, Nicko tunes (denser than B's 0.024; d95 ~52 m)
    ambientLightLevel: 0.5,           // PROPOSED, Nicko tunes
    // B/C door (region-defs connections[1]; region-manager door window +
    // gate-at-the-line; game.js gate predicate !dayNight.dormant + toast)
    door: {
      planeZ: -86,                    // PROPOSED, Nicko tunes (B occupies z >= -86, C z <= -86)
      doorX: 0,                       // PROPOSED, Nicko tunes
      doorHalfWidth: 4,               // PROPOSED, Nicko tunes (window = A/B chokepoint width 8)
      suspendDepthM: 3,               // PROPOSED, Nicko tunes (radial clamp suspended within this of the plane, in the window)
      interactM: 6,                   // PROPOSED, Nicko tunes (E near the arch while locked -> reason toast)
      hintM: 12,                      // PROPOSED, Nicko tunes (gate-hint band around the plane)
      // door arch: mirrors boundaryWall.arch's row shape (b3Gate measured
      // constants copied); VISUAL ONLY - no colliders, the gate logic is the door
      arch: { asset: 'b3Gate', x: 0, z: -86, rotY: Math.PI,   // PROPOSED, Nicko tunes (faces north)
        fitOpening: 5.2, openingFrac: 0.3428, openingCenterFrac: 0.0059,
        depthScale: 0.45 },
      wallGapPadM: 0,                 // PROPOSED, Nicko tunes (ring wall segments meeting window + this are not built; 0 = 3 segments, gap hidden behind the arch pillars)
      text: {
        locked: 'Rest at a camp first - the forest beyond still sleeps.',
        prompt: 'E - Examine the arch',                       // PROPOSED, Nicko tunes
        hint: 'Enter the Forest of the Old King',              // PROPOSED, Nicko tunes
        hintLocked: 'The forest beyond still sleeps',          // PROPOSED, Nicko tunes
        hintBack: 'Back to the Darkwood'                       // PROPOSED, Nicko tunes
      }
    },
    // CC-C4b NOTCH SOFT BLOCKERS (terrain.rim.notches blocker rows; game.js
    // tryNotch + the interact prompt): E within interactM of a mouth names the
    // reason (dormancy-toast style); the hold line is wh-ground holdAtNotch.
    notchText: {
      interactM: 5,                                            // PROPOSED, Nicko tunes
      locked: 'The road beyond is lost. For now.',             // PROPOSED, Nicko tunes
      prompt: 'E - Examine the road'                           // PROPOSED, Nicko tunes
    },
    // CC-C5 WOLF PACKS: 3 packs x 4 (CONFIG.enemy.wolfPacks loops). packId =
    // the pack row; waypointPhase = the patrol rank (slot = rank x 6 m behind
    // the lead along the loop, alternating 2 m lateral). Rows = enemy.js
    // packSlot at lead arc 0, derived offline (scratch/cc-c5/spawn_rows.js):
    // spread max 8.46 / 9.08 / 9.13 m from the pack centroid (< regroupRadius
    // 12), so no member spawns regrouping. Region C only (A/B rows untouched).
    enemies: [
      { type: 'wolf', x: 190.0, z: -318.0, packId: 'east', waypointPhase: 0 },
      { type: 'wolf', x: 188.8, z: -324.2, packId: 'east', waypointPhase: 1 },
      { type: 'wolf', x: 193.5, z: -329.7, packId: 'east', waypointPhase: 2 },
      { type: 'wolf', x: 189.3, z: -333.9, packId: 'east', waypointPhase: 3 },
      { type: 'wolf', x: -190.0, z: -420.0, packId: 'west', waypointPhase: 0 },
      { type: 'wolf', x: -184.3, z: -417.2, packId: 'west', waypointPhase: 1 },
      { type: 'wolf', x: -182.9, z: -410.1, packId: 'west', waypointPhase: 2 },
      { type: 'wolf', x: -175.9, z: -408.7, packId: 'west', waypointPhase: 3 },
      { type: 'wolf', x: -25.0, z: -520.0, packId: 'north', waypointPhase: 0 },
      { type: 'wolf', x: -18.8, z: -521.2, packId: 'north', waypointPhase: 1 },
      { type: 'wolf', x: -13.4, z: -516.4, packId: 'north', waypointPhase: 2 },
      { type: 'wolf', x: -6.9, z: -519.6, packId: 'north', waypointPhase: 3 },
      { type: 'bandit', x: -103.9, z: -469.5 },   // CC-C16b camp 1 guard 1
      { type: 'bandit', x: -108.7, z: -470.1 },   // CC-C16b camp 1 guard 2
      { type: 'bandit', x: -106.1, z: -468.7 },   // CC-C16b camp 1 guard 3
      { type: 'bandit', x: 120.2, z: -446.0 },   // CC-C16b camp 2 guard 1
      { type: 'bandit', x: 115.4, z: -446.6 },   // CC-C16b camp 2 guard 2
      { type: 'bandit', x: 118.0, z: -445.2 },   // CC-C16b camp 2 guard 3
      { type: 'bandit', x: -205.6, z: -243.4 },   // CC-C16b camp 3 guard 1
      { type: 'bandit', x: -210.4, z: -244.0 },   // CC-C16b camp 3 guard 2
      { type: 'bandit', x: -207.8, z: -242.6 },   // CC-C16b camp 3 guard 3
      { type: 'bandit', x: 146.4, z: -534.3 },   // CC-C16b camp 4 guard 1
      { type: 'bandit', x: 141.6, z: -534.9 },   // CC-C16b camp 4 guard 2
      { type: 'bandit', x: 144.2, z: -533.5 },   // CC-C16b camp 4 guard 3
      { type: 'wolf', x: -89.9, z: -336.7, packId: 'sw', waypointPhase: 0 },
      { type: 'wolf', x: -78.4, z: -328.0, packId: 'sw', waypointPhase: 1 },
      { type: 'wolf', x: -70.9, z: -290.5, packId: 'sw', waypointPhase: 2 },
      { type: 'wolf', x: -86.6, z: -279.6, packId: 'sw', waypointPhase: 3 },
      { type: 'wolf', x: 79.6, z: -186.8, packId: 'se', waypointPhase: 0 },
      { type: 'wolf', x: 115.2, z: -158.5, packId: 'se', waypointPhase: 1 },
      { type: 'wolf', x: 110.4, z: -142.3, packId: 'se', waypointPhase: 2 },
      { type: 'wolf', x: 108.8, z: -127.6, packId: 'se', waypointPhase: 3 },
      { type: 'wolf', x: 62.5, z: -249.5, packId: 'ss', waypointPhase: 0 },
      { type: 'wolf', x: 73.9, z: -256.9, packId: 'ss', waypointPhase: 1 },
      { type: 'wolf', x: 92.1, z: -203.5, packId: 'ss', waypointPhase: 2 },
      { type: 'wolf', x: 74.8, z: -188.5, packId: 'ss', waypointPhase: 3 },
      { type: 'wolf', x: 223.3, z: -482.5, packId: 'nw2', waypointPhase: 0 },
      { type: 'wolf', x: 236.3, z: -473.8, packId: 'nw2', waypointPhase: 1 },
      { type: 'wolf', x: 240.9, z: -461.0, packId: 'nw2', waypointPhase: 2 },
      { type: 'wolf', x: 229.4, z: -440.0, packId: 'nw2', waypointPhase: 3 },
      // CC-C6 BANDIT CAMP GUARDS (doc 62 L4/L5/L6; io/missions/2026-10-09-cc-c6-
      // bandit-camps.md): ordinary bandit rows (AI1 by type), APPENDED after the
      // wolves so saved per-index dead state keeps its wolf rows. Guard spread
      // 10-12 m around each camp fire, >= 5 m from camp props, >= 6 m from every
      // other prop row, >= 88 m from every wolf loop (scratch/cc-c6/camp_probe.js).
      // Loot: the standard CONFIG.drops table (Charlie = same table, no tier).
      { type: 'bandit', x: -53.6, z: -178.3 },     // Alpha (fire -60, -186)
      { type: 'bandit', x: -67.7, z: -179.6 },
      { type: 'bandit', x: -66.0, z: -196.4 },
      { type: 'bandit', x: 85.0, z: -240.6 },      // Bravo (fire 95, -236)
      { type: 'bandit', x: 102.7, z: -242.4 },
      { type: 'bandit', x: 100.1, z: -225.1 },
      { type: 'bandit', x: -130.5, z: -500.5 },    // Charlie (fire -140, -506)
      { type: 'bandit', x: -144.2, z: -496.9 },
      { type: 'bandit', x: -151.3, z: -510.1 },
      { type: 'bandit', x: -138.1, z: -516.8 }
      // CC-C8: the CC-C7 rotmother row (index 22) is GONE - she is instanced by
      // her lair record inside the den (CONFIG.regionD.lairs), not a C row.
      // CC-EC1 COVEN ACOLYTES (doc 34): 2 caster rows APPENDED at the array END
      // (row-index persistence law: append-only, indices 50/51 after the CC-C6
      // Charlie bandit rows). SW moor pair between the SW camps and the den
      // mouth lane, away from camps / pack loops / the den door. Clearance
      // verified vs the full check set (scratch/cc-ec1/clearance.py, 123
      // members): min 38.4m (row 1) / 30.1m (row 2) - nearest member the sw
      // wolf-pack loop point (-112.5,-276.1); >25m to every camp guard, camp
      // fire, wolf waypoint/row and the den door interactAt (-163.4,-202.6).
      // NOTE: comma-first continuation below - the last pre-existing row above
      // stays byte-identical (append-only diff law: zero '-' lines anywhere).
      ,{ type: 'coven', x: -118.4, z: -238.2 },
      { type: 'coven', x: -99.2, z: -249.1 }
      // CC-WM1 redseam: the CONTESTED light state (doc 42 Part 5 WHO — the ore
      // is why the fight is there). 3 bandit squatters bivouacking in the
      // scar (no fire row this round; WM1-A3 spacing verified in
      // scratch/cc-wm1/clearance_wm1.py).
      ,{ type: 'bandit', x: 56.5, z: -580.5 },   // redseam squatter 1 (CC-WM1)
      { type: 'bandit', x: 61.5, z: -580 },     // redseam squatter 2 (CC-WM1)
      { type: 'bandit', x: 59, z: -574.5 }      // redseam squatter 3 (CC-WM1)
    ],
    // CC-C3 ANCIENT FOREST (R-62.6, io/missions/2026-10-07-cc-c3-ancient-forest.md):
    // hand-placed rows, no runtime random. CC-C2's 120-tree 8-10 band is
    // REPLACED (not tuned). 68 trees = 6 king-specimen giants (scale 28-30,
    // hand anchors on the door->Stone lane + flanking the Stone) + 62 ancient
    // band (scale 16-26; yewTree 60% / witchwoodTree 40%), min tree-to-tree
    // spacing 55.00 m (self-checked on the pasted rows), + 20 treeStump (scale
    // 2.4-3.4, >= 14 m from trunks, >= 30 m apart). Generated once offline
    // (mulberry32 seed 20261008, tight-fill dart throw: best of 60 valid
    // darts per placement, rounded to 0.1 m BEFORE the spacing test) and
    // pasted. Rows cover the FULL playable disc (<= 274.5 m from C's center =
    // 4 m inside the playable rim); clear of the arrival glade (18 m from
    // spawn), the lantern (6 m), the door->glade->Stone silhouette lane
    // (|x| < 12, z > -330) and the Old King's Stone (50 m from center = the
    // ~30 m assembly + 20 m breathing room).
    propCullM: 274.5,                 // PROPOSED, Nicko tunes (CC-C3: GENERATION contract only = rows reach the full disc, rim - 4 m; the frame budget is cullDistanceM)
    // CC-C3 per-frame visibility cull (region-manager cullProps): EVERY row in
    // props (scatter, stumps, lantern, Stone) hides past cullDistanceM from
    // the PLAYER and re-shows inside cullDistanceM * cullShowFrac (hysteresis).
    // FOG-CULL COHERENCE: FogExp2 transmittance exp(-(d * density)^2) <= 1/255
    // (one 8-bit level) at d >= sqrt(ln 255) / density = 2.354 / density:
    // 94.2 m at the THINNEST C fog (day 0.025), 71.3 m at night 0.033. Show
    // band 156.4 m and hide band 170 m are both past it: no visible pop.
    // LEDGER (doc 61:44, 2M drawn tris): tris per GLB (measured) yewTree
    // 28243, witchwoodTree 28084, treeStump 8109, mourningStatue 21384,
    // cemeteryGate 20585, mossBoulder 21599, lanternPost 2500; worst-case
    // full 170 m circle anywhere on the playable disc (2 m grid) = 49 props /
    // 1,119,299 tris = 56% of 2M at (105.5, -394.5); arrival glade 16 props /
    // 344,814; Stone ring 43 props / 949,682 (all placed: 101 / 2,337,856).
    // Frustum culling only lowers these.
    cullDistanceM: 170,               // PROPOSED, Nicko tunes (hide band, m from the player)
    cullShowFrac: 0.92,               // PROPOSED, Nicko tunes (show band = cullDistanceM * this)
    // CC-C4a SCATTER CELLS: C's instanced scatter is bucketed per asset into
    // scatterCellM grid cells; each cell's InstancedMesh joins cullProps as ONE
    // object (centroid + radius r): hidden past scatterCullM + r from the
    // player, shown inside scatterCullM * cullShowFrac + r. Fog coherence: an
    // instance can only be seen within 94.2 m (thinnest-fog 1/255 depth) of the
    // camera, <= 94.2 + 14 (camMaxDistance) = 108.2 m from the player; the show
    // band 110.4 + r is past it - no visible pop. NO per-instance culling.
    // LEDGER (measured GLB tris; CC-C3 rows + CC-C4a rows): deadTree 30174
    // (brief assumed ~2k: hence 10 rows, not ~24), mossBoulder 21599 (20 field
    // rows + fork slab, not ~40); instanced bushA 2321, bushB 2836, whBushSnare
    // 3000, bramble 2288, grassTuft 848. Plan: 229 ring + 40 free bushes, 320
    // grass + 36 tuft colonies (195) = 784 instances / 1,178,820 tris in 143
    // cell meshes (max cell r 65 m). WORST CASE (2 m grid over the playable
    // disc): props in 170 m + live cells = 1,821,626 at (-14.5, -462.5) (61
    // props = 1,419,156 + 37 cells) + terrain 39,200 + road ribbons 2,256 =
    // 1,863,082 = 93.2% of 2M. Draw calls there: 61 props + 37 cells + 6
    // roads + terrain. Without cells (5 whole-disc layers, never distance-
    // culled) the same plan peaks at 2,637,176 - over budget.
    // CC-C4b LEDGER: + 12 scree mossBoulder rows (<= 4 within 170 m of any
    // playable point = + 86,396) + 3 notch ribbons (180 tris) - 20 cliff-band
    // rows; scatter counts scaled to the non-ring share (same interior
    // density): worst case <= 1,863,082 + 86,576 = 1,949,658 = 97.5% of 2M
    // (upper bound - the dropped rows only lower it). Terrain tris unchanged.
    scatterCellM: 90,                 // PROPOSED, Nicko tunes
    scatterCullM: 120,                // PROPOSED, Nicko tunes
    // CC-C3 world-edge fix: the visual disc (fog formula = 336 m) left the
    // edge only ~43 m from a rim camera (camMaxDistance 14 outward) - visible
    // through day fog 0.025. Floor the visual radius so the edge sits past
    // the 1/255 fog depth (94.2 m) from ANY reachable camera:
    // 400 - (278.5 + 14) = 107.5 m. A/B leave it unset (formula unchanged).
    // CC-C4b SKYLINE (R-62.8): the rim ring now owns the world edge. From the
    // farthest reachable spot on every bearing (the cliff guard's foot, or a
    // notch's hold line) with the camera 10 m up, the sight line to the skirt
    // edge (r 400) is cut by the ring on 328/360 bearings; the 32 open ones
    // (3 notches + the glade valley) end >= 121.5 m away (T day 0.025 =
    // 1e-4, past the 1/255 depth 94.2 m). Fog rows UNCHANGED: FogExp2 is
    // opaque at 110 m (T night 1.9e-6, day 5.2e-4; even 0.026 gives 2.8e-4)
    // and at 240 m for any density in the proposed 0.026-0.028 band, so a
    // lower density buys no ring visibility. The ring reads two ways: up
    // close (the glade valley walls 40 m from spawn, T day 0.37 / night
    // 0.17) and as SILHOUETTE - fog-saturated terrain renders fog colour
    // against the UNfogged sky dome (game.js setupSky), so the crest
    // (25.7-37.7 m, 5.9-8.6 deg above the Stone's horizon) cuts a jagged
    // fog-colour skyline instead of the flat fog/horizon line.
    visualGroundMinRadius: 400,       // PROPOSED, Nicko tunes
    // CC-C4 HEIGHTFIELD (R-62.1, io/missions/2026-10-08-cc-c4-heightfield-landing.md;
    // js/wh-ground.js). Field constants = the CC-C1 spike EXACTLY (seed 1337,
    // playtest-approved): fBm 4 oct, wavelength 45, lacunarity 2, gain 0.45,
    // remap clamp((n - 0.22) / 0.57) * 5. Mesh PlaneGeometry(560, 560, 140, 140)
    // centered on C's disc (39,200 tris), built once at region load; ground
    // y = the B-TRI sampler over the same Float32 grid (exact to the render).
    // Only regions carrying an enabled terrain row walk on a heightfield
    // (WH_GROUND.has): A/B have none and run the flat y = 0 path untouched.
    terrain: {
      enabled: true,
      S: 140,                         // spike verdict (S=180 rejected: +65% tris)
      plane: 560,                     // = 2 * groundRadius (covers the disc, z -646..-86)
      seed: 1337,
      baseWavelength: 45,
      octaves: 4,
      lacunarity: 2.0,
      gain: 0.45,
      hMax: 5,
      nLo: 0.22,                      // ~p1 of fbm01 at seed 1337 (spike)
      nHi: 0.79,                      // ~p99
      // ARRIVAL GLADE pocket (world coords): flat h inside r, smoothstep blend
      // to the raw hills by r + blend. Spike FLAT_R / FLAT_BLEND / FLAT_H moved
      // from the plane center to the glade: the door (z -86) -> glade lane is
      // flat 0.4 (raw hills here are ~4.65 m: the pocket is a hollow of calm).
      pocket: { x: 0, z: -96, r: 25, blend: 20, h: 0.4 },
      // OLD KING'S STONE pad (world coords): h null = the UNflattened height at
      // the pad center (h(0, -366) = 1.404). r 28 covers the whole assembly
      // (statue, boulder ring r 16, gate pair 25.3 m out); raw ground inside r
      // 28 spans 0.89..2.73, so every piece sits on one level. PROPOSED, Nicko tunes
      stonePad: { x: 0, z: -366, r: 28, blend: 16, h: null },
      // RIM FADE (builder decision, logged): the 560 m mesh SQUARE meets the
      // r 280 disc at 4 points, so the playable rim (278.5) is <= 1.5 m from
      // the mesh edge. Heights fade to 0 between r from..to so the mesh edge is
      // flush with the flat skirt (groundY) instead of a floating cliff lip.
      // CC-C4b RIM MOUNTAINS (R-62.8, io/missions/2026-10-08-cc-c4b-rim-mountains.md;
      // wh-ground makeField ridge term): the fade above stays (the notch beds +
      // the mesh edge keep C4's flush-to-skirt ground); a ridge is ADDED: foot
      // from +- footJitterM (lump noise), smoothstep rise over blend to peakH *
      // (0.75 + 0.45 * lump) (lump = 2-octave value noise, salt seed +
      // lumpSalt, wavelength lumpWavelength), faded to 0 over the last
      // edgeFadeM before the 560 m square's edge, cut by the notch windows.
      // cliffSlopeDeg = the CLIFF GUARD (game.js slopeGuard): no uphill step
      // onto ground steeper than this (rolls + switchbacks included; natural
      // C terrain tops out ~19 deg, so it binds only on the ring). Stone
      // vertex band: ridge vertices lerp to meshColorStone over
      // stoneFromH..stoneToH (moss foothills, stone upper slopes).
      // NOTCHES (the King's Roads' C4a mouths): window halfWidth on the notch
      // axis (center -> mouth), smoothstep shoulder; blocker rows hold the
      // player notchHoldM past the mouth (wh-ground holdAtNotch) + E toast
      // (notchText). The 'door' notch is the arrival glade's valley (the B/C
      // door + the spine stay on C4's ground; no blocker). All PROPOSED, Nicko tunes.
      rim: { from: 240, to: 280, blend: 30, peakH: 34, cliffSlopeDeg: 38,
        footJitterM: 6, lumpWavelength: 70, lumpSalt: 7919, edgeFadeM: 15,
        stoneFromH: 6, stoneToH: 16, notchShoulderM: 8, notchHoldM: 0,
        notches: [
          { id: 'north', x: 0, z: -596, halfWidth: 10, blocker: true },
          { id: 'east', x: 240, z: -366, halfWidth: 10, blocker: true },
          { id: 'west', x: -240, z: -366, halfWidth: 10, blocker: true },
          { id: 'door', x: 0, z: -86, halfWidth: 30, shoulder: 18 }
        ] },
      // SLOPE GUARD (game.js clampPlayerToBounds): an uphill move is blocked
      // when dh > climbFactor * sprintSpeed * dt (the spike's maxStepPerFrame,
      // uphill only) = tan(cap) = climbFactor * sprintSpeed / speed: sprint
      // (10) ~31 deg, walk (6) ~45 deg (stepSlopeCapDeg). Natural C terrain
      // tops out ~19 deg: a safety net that almost never binds. Rolls exempt.
      // CC-C4b: the rim ring's faces run 52-74 deg (> every cap); the cliff
      // guard (rim.cliffSlopeDeg) closes the switchback/roll/slow-walk gaps.
      // KNOWN QUIRK (spike): a walker can climb steeper than a runner (v1 OK).
      climbFactor: 0.6,
      stepSlopeCapDeg: 45,            // PROPOSED (walk-pace equivalent of climbFactor 0.6; informational)
      camMinAboveGround: 0.8,         // PROPOSED, Nicko tunes (camera floor over the terrain under it)
      propFootR: 1.2,                 // PROPOSED, Nicko tunes (prop seat = min ground at center + 4 points at this r)
      meshColorMoss: 0x2c4424,        // low ground (spike)
      meshColorStone: 0x8c7b5e,       // high ground (spike)
      // CC-C4b: the flat skirt under/outside the mesh square takes the stone
      // colour (the ring now owns the world edge; through a notch the skirt
      // reads as the mountains' rock floor fading into fog). PROPOSED, Nicko tunes
      skirtColor: 0x8c7b5e,
      debugAssert: false,             // true: rebuild the grid once at load + log the hash check
      gridHash: '7ca52bd3'           // FNV-1a of this row's S=140 grid (CC-C4b rim mountains; CC-C4 flat-rim field = 8ae6983, spike's own = c5a19f53)
    },
    // CC-C4b: rows marked '// C4b-CLIFF' seated on the new ring at a slope
    // steeper than the sprint cap (31 deg: their footY seat would float the
    // downhill side of the trunk) - 14 giants, 2 dead trees, 2 stumps, 2
    // boulders; '// C4b-NOTCH' = the yew standing in the east notch bed (C4a
    // note). Commented out, not deleted (restore = uncomment). Crest rows
    // (slope <= 31 deg) stay: giants on the skyline. All PROPOSED, Nicko tunes.
    props: [
      // L0 glade furniture: lantern post at the spawn glade (light socket)
      { asset: 'lanternPost', x: 3.0, z: -99.0, rotY: 0.0, scale: 2.535 },
      // OLD KING'S STONE (CC-C3 5.4): kit assembly at C's center (0, -366) on
      // the flat stub ground (y 0). CC-C4 READER: these rows are the y-anchor
      // - the heightfield lifts the whole assembly to h(0, -366). Props stay
      // ordinary rows (existing collider path, no new collision code).
      // m3 statue facing the approach (+z), m1 gate pair flanking the lane
      // 24 m south (rotY mirrored), m9 boulder ring r 16 open to the south.
      { asset: 'mourningStatue', x: 0.0, z: -366.0, rotY: 0.00, scale: 11.0 },
      { asset: 'cemeteryGate',  x: -8.0, z: -342.0, rotY: 0.30, scale: 5.5 },
      { asset: 'cemeteryGate',  x: 8.0, z: -342.0, rotY: -0.30, scale: 5.5 },
      { asset: 'mossBoulder',   x: 10.3, z: -353.7, rotY: 0.60, scale: 2.10 },
      { asset: 'mossBoulder',   x: 15.5, z: -361.9, rotY: 2.10, scale: 1.60 },
      { asset: 'mossBoulder',   x: 15.0, z: -371.5, rotY: 4.40, scale: 2.40 },
      { asset: 'mossBoulder',   x: 9.2, z: -379.1, rotY: 1.20, scale: 1.80 },
      { asset: 'mossBoulder',   x: 0.0, z: -382.0, rotY: 3.30, scale: 2.50 },
      { asset: 'mossBoulder',   x: -9.2, z: -379.1, rotY: 5.50, scale: 1.70 },
      { asset: 'mossBoulder',   x: -15.0, z: -371.5, rotY: 0.20, scale: 2.20 },
      { asset: 'mossBoulder',   x: -15.5, z: -361.9, rotY: 2.80, scale: 1.50 },
      { asset: 'mossBoulder',   x: -10.3, z: -353.7, rotY: 4.90, scale: 2.00 },
      // CC-C17 ROW SHAPE LAW: every live giant row below carries cullM 140 (the v2
      // brief's C4b-giant shape; hide 140 / show 128.8 m > the 94.2 m fog reach = no
      // visible pop). Ledger relief for the C17 set (scratch/cc-c17/apply_giant_cull.py).
      // king specimen giants (R-62.6 rare band 28-30): lane + Stone approach anchors
      { asset: 'yewTree',       x: -28.0, z: -296.0, rotY: 5.91, scale: 29.00, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 30.0, z: -238.0, rotY: 0.19, scale: 28.41, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -26.0, z: -178.0, rotY: 4.65, scale: 28.21, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 24.0, z: -128.0, rotY: 1.94, scale: 28.73, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -56.0, z: -404.0, rotY: 5.65, scale: 29.93, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 56.0, z: -404.0, rotY: 1.91, scale: 28.67, cullM: 140 },   // CC-C17 shape
      // ancient band (R-62.6 scale 16-26, min spacing 55 m)
      { asset: 'yewTree',       x: 86.4, z: -461.4, rotY: 4.40, scale: 20.19, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 35.9, z: -498.1, rotY: 3.28, scale: 20.74, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -55.0, z: -348.3, rotY: 1.52, scale: 24.40, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -109.2, z: -337.1, rotY: 5.97, scale: 16.98, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'yewTree',       x: 79.8, z: -120.5, rotY: 1.76, scale: 17.44 },
      { asset: 'yewTree',       x: -50.1, z: -245.3, rotY: 3.37, scale: 21.49, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 103.5, z: -513.8, rotY: 4.77, scale: 22.99, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -126.7, z: -281.9, rotY: 4.90, scale: 23.08, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -141.2, z: -382.4, rotY: 2.69, scale: 21.34, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 83.4, z: -220.7, rotY: 0.58, scale: 19.02, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 73.1, z: -559.7, rotY: 4.38, scale: 23.50, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -81.1, z: -164.7, rotY: 1.76, scale: 22.24, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 135.9, z: -560.5, rotY: 0.46, scale: 22.61, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -117.3, z: -227.3, rotY: 2.84, scale: 25.03, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 84.7, z: -614.0, rotY: 0.30, scale: 18.29, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 111.3, z: -406.2, rotY: 3.47, scale: 19.09, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 56.0, z: -349.0, rotY: 5.87, scale: 24.35, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 15.1, z: -446.0, rotY: 2.01, scale: 19.14, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'witchwoodTree', x: -51.9, z: -115.1, rotY: 0.97, scale: 24.73 },
      // C4b-CLIFF { asset: 'yewTree',       x: 27.9, z: -626.2, rotY: 3.88, scale: 20.17 },
      { asset: 'witchwoodTree', x: 166.7, z: -514.8, rotY: 2.29, scale: 17.33, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -19.3, z: -499.0, rotY: 2.08, scale: 17.17, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 82.6, z: -276.2, rotY: 3.71, scale: 20.35, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 10.4, z: -551.8, rotY: 2.47, scale: 24.72, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'yewTree',       x: 213.5, z: -485.0, rotY: 0.29, scale: 24.29 },
      { asset: 'witchwoodTree', x: 133.6, z: -133.8, rotY: 0.83, scale: 23.07, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 257.7, z: -451.6, rotY: 0.40, scale: 21.53, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -176.1, z: -254.5, rotY: 5.39, scale: 20.42, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -172.3, z: -199.5, rotY: 1.21, scale: 20.27, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'witchwoodTree', x: 170.5, z: -175.1, rotY: 4.18, scale: 25.92 },
      { asset: 'witchwoodTree', x: -174.5, z: -312.4, rotY: 6.28, scale: 19.49, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 215.3, z: -208.5, rotY: 4.54, scale: 21.10, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'yewTree',       x: -128.5, z: -135.7, rotY: 3.79, scale: 23.96 },
      { asset: 'yewTree',       x: -70.6, z: -476.1, rotY: 0.66, scale: 17.22, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 153.1, z: -460.7, rotY: 4.43, scale: 24.56, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 166.7, z: -405.7, rotY: 3.46, scale: 21.21, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -178.2, z: -424.2, rotY: 3.80, scale: 18.06, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'witchwoodTree', x: 234.8, z: -262.1, rotY: 0.64, scale: 22.96 },
      { asset: 'yewTree',       x: -225.0, z: -453.3, rotY: 3.29, scale: 18.43, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -124.3, z: -436.8, rotY: 2.66, scale: 21.83, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 229.5, z: -404.2, rotY: 1.94, scale: 21.67, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 191.0, z: -297.9, rotY: 2.52, scale: 23.34, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 172.1, z: -242.9, rotY: 1.81, scale: 22.22, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 213.9, z: -351.0, rotY: 5.37, scale: 19.05, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: -225.1, z: -281.7, rotY: 5.06, scale: 24.34, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 134.1, z: -353.5, rotY: 3.67, scale: 25.62, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'witchwoodTree', x: -27.4, z: -626.8, rotY: 1.85, scale: 16.17 },
      // C4b-CLIFF { asset: 'yewTree',       x: -223.2, z: -508.4, rotY: 2.75, scale: 16.17 },
      // C4b-CLIFF { asset: 'witchwoodTree', x: -82.5, z: -615.5, rotY: 2.89, scale: 19.50 },
      { asset: 'yewTree',       x: -44.9, z: -574.4, rotY: 4.00, scale: 25.82, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -233.6, z: -398.8, rotY: 1.10, scale: 18.37, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'witchwoodTree', x: -257.6, z: -326.4, rotY: 3.82, scale: 22.80 },
      // C4b-CLIFF { asset: 'yewTree',       x: -133.9, z: -595.6, rotY: 1.92, scale: 18.84 },
      { asset: 'yewTree',       x: -172.1, z: -487.9, rotY: 3.54, scale: 25.24, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -87.1, z: -528.6, rotY: 1.31, scale: 19.80, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -153.6, z: -544.1, rotY: 0.28, scale: 24.45, cullM: 140 },   // CC-C17 shape
      // C4b-CLIFF { asset: 'yewTree',       x: 254.5, z: -313.8, rotY: 4.53, scale: 17.00 },
      { asset: 'yewTree',       x: 136.1, z: -293.7, rotY: 4.93, scale: 22.37, cullM: 140 },   // CC-C17 shape
      { asset: 'witchwoodTree', x: 47.4, z: -179.1, rotY: 3.90, scale: 24.15, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: 27.0, z: -298.1, rotY: 3.88, scale: 17.84, cullM: 140 },   // CC-C17 shape
      { asset: 'yewTree',       x: -224.8, z: -216.6, rotY: 5.98, scale: 22.85, cullM: 140 },   // CC-C17 shape
      // C4b-NOTCH { asset: 'yewTree',       x: 272.4, z: -369.0, rotY: 3.76, scale: 25.93 },
      // ancient stumps (R-62.6 scale 2.4-3.4)
      // C4b-CLIFF { asset: 'treeStump',     x: -194.5, z: -194.7, rotY: 4.64, scale: 3.00 },
      { asset: 'treeStump',     x: -37.3, z: -478.7, rotY: 3.45, scale: 2.61 },
      { asset: 'treeStump',     x: -141.2, z: -470.1, rotY: 1.37, scale: 2.55 },
      { asset: 'treeStump',     x: 119.6, z: -318.7, rotY: 0.05, scale: 2.43 },
      { asset: 'treeStump',     x: 92.5, z: -112.4, rotY: 3.46, scale: 2.81 },
      { asset: 'treeStump',     x: 104.0, z: -389.0, rotY: 2.57, scale: 3.04 },
      { asset: 'treeStump',     x: -34.9, z: -448.5, rotY: 4.96, scale: 3.24 },
      { asset: 'treeStump',     x: -91.3, z: -260.5, rotY: 2.28, scale: 2.85 },
      { asset: 'treeStump',     x: 57.2, z: -511.2, rotY: 4.62, scale: 2.64 },
      { asset: 'treeStump',     x: -146.0, z: -306.7, rotY: 1.93, scale: 3.22 },
      // C4b-CLIFF { asset: 'treeStump',     x: 45.6, z: -112.6, rotY: 0.08, scale: 2.64 },
      { asset: 'treeStump',     x: 158.4, z: -313.6, rotY: 2.58, scale: 3.06 },
      { asset: 'treeStump',     x: 74.5, z: -338.4, rotY: 1.59, scale: 2.61 },
      { asset: 'treeStump',     x: 91.7, z: -558.7, rotY: 5.30, scale: 3.02 },
      { asset: 'treeStump',     x: 31.1, z: -144.7, rotY: 1.03, scale: 3.01 },
      { asset: 'treeStump',     x: -49.0, z: -183.3, rotY: 0.64, scale: 2.54 },
      { asset: 'treeStump',     x: 183.7, z: -278.0, rotY: 4.57, scale: 2.49 },
      { asset: 'treeStump',     x: -101.6, z: -580.6, rotY: 2.41, scale: 2.93 },
      { asset: 'treeStump',     x: -156.7, z: -245.8, rotY: 5.95, scale: 3.31 },
      { asset: 'treeStump',     x: 162.8, z: -232.1, rotY: 3.84, scale: 2.96 },
      // CC-C4a BOULDER FIELDS (R-62.7): 2 king boulders (scale 8-10) + 18 in 5 fields
      // of 3-5 (field lead 3.5-6, mates 1.5-4.5) in the gaps between giants: >= 3 m
      // edge gap to trunks, 4 m to other props, 42 m from the Stone, off the CC-C3
      // silhouette lane, road centerline >= max(6, r + halfWidth + 3). Generated once
      // offline (mulberry32 seed 20261008 ^ 0xC4A, best-candidate field centers).
      { asset: 'mossBoulder',      x: -124.1, z: -180.9, rotY: 1.94, scale: 8.84 },
      { asset: 'mossBoulder',      x: -99.0, z: -396.6, rotY: 5.21, scale: 9.77 },
      // C4b-CLIFF { asset: 'mossBoulder',      x: -88.9, z: -118.9, rotY: 0.63, scale: 4.18 },
      // C4b-CLIFF { asset: 'mossBoulder',      x: -104.2, z: -116.7, rotY: 3.50, scale: 2.07 },
      { asset: 'mossBoulder',      x: -101.1, z: -113.4, rotY: 3.32, scale: 1.70 },
      { asset: 'mossBoulder',      x: 43.9, z: -577.8, rotY: 2.59, scale: 4.98 },
      { asset: 'mossBoulder',      x: 36.4, z: -580.4, rotY: 4.93, scale: 4.31 },
      { asset: 'mossBoulder',      x: 41.5, z: -592.6, rotY: 4.02, scale: 2.63 },
      { asset: 'mossBoulder',      x: 46.9, z: -596.2, rotY: 1.35, scale: 2.81 },
      { asset: 'mossBoulder',      x: 35.9, z: -595.0, rotY: 4.30, scale: 2.88 },
      { asset: 'mossBoulder',      x: 24.2, z: -199.5, rotY: 1.48, scale: 4.14 },
      { asset: 'mossBoulder',      x: 16.3, z: -194.6, rotY: 3.65, scale: 2.04 },
      { asset: 'mossBoulder',      x: 19.6, z: -209.1, rotY: 0.46, scale: 1.93 },
      { asset: 'mossBoulder',      x: -84.8, z: -208.2, rotY: 1.25, scale: 5.17 },
      { asset: 'mossBoulder',      x: -90.7, z: -207.4, rotY: 1.07, scale: 1.51 },
      { asset: 'mossBoulder',      x: -75.5, z: -202.1, rotY: 1.78, scale: 2.13 },
      { asset: 'mossBoulder',      x: -80.8, z: -199.4, rotY: 1.59, scale: 2.47 },
      { asset: 'mossBoulder',      x: 130.8, z: -494.4, rotY: 5.81, scale: 5.59 },
      { asset: 'mossBoulder',      x: 123.9, z: -488.7, rotY: 0.35, scale: 3.54 },
      { asset: 'mossBoulder',      x: 134.5, z: -487.8, rotY: 4.21, scale: 3.11 },
      // CC-C4a NORMAL DEAD TREES (A/B size 8-9.85: the age contrast), >= 30 m to any
      // tree/boulder (min 38.8), CC-C3 zones (glade, lane, Stone 50 m, rim 4 m), road
      // centerline >= 8 m + trunk. Ring hosts (deadTree is in scatter ringHosts).
      { asset: 'deadTree',         x: -21.2, z: -430.2, rotY: 2.77, scale: 9.36 },
      // C4b-CLIFF { asset: 'deadTree',         x: -193.5, z: -550.8, rotY: 0.85, scale: 8.71 },
      { asset: 'deadTree',         x: 136.9, z: -199.8, rotY: 6.04, scale: 8.29 },
      // C4b-CLIFF { asset: 'deadTree',         x: -160.3, z: -158.0, rotY: 1.38, scale: 9.25 },
      { asset: 'deadTree',         x: -40.5, z: -534.1, rotY: 3.41, scale: 9.36 },
      { asset: 'deadTree',         x: 99.2, z: -173.9, rotY: 5.66, scale: 8.05 },
      { asset: 'deadTree',         x: -209.5, z: -346.3, rotY: 3.28, scale: 8.29 },
      { asset: 'deadTree',         x: -70.9, z: -306.2, rotY: 2.98, scale: 9.23 },
      { asset: 'deadTree',         x: 173.7, z: -338.1, rotY: 2.74, scale: 9.80 },
      { asset: 'deadTree',         x: -111.3, z: -560.1, rotY: 0.67, scale: 8.79 },
      // CC-C4a FORK MARKER (UNLIT): a standing moss slab beside the spine at the
      // ring's south junction - stands in for b3-waymarker (its only manifest key,
      // lanternWaymarker, carries a lightSockets row: a prop row would light the fork)
      { asset: 'mossBoulder',      x: -6.5, z: -326.0, rotY: 1.57, scale: 2.40 },
      // CC-C15 (Nicko 2026-10-20): the 3 CC-C12 den-trail lanternWaymarker
      // sign rows are REMOVED (den relocated to the SW rim; no trail signs).
      // CC-C4b SCREE FOOT (R-62.8): 12 rockfall boulders at the ring's foot (local
      // r 225-240, seat slope <= 22 deg over the footprint, no ridge under them):
      // one flanking each side of the N/E/W notch mouths (lat 14-23 m) + 6 spread
      // along the foot (best-candidate). Road centerline >= max(6, r + 2.2 + 3),
      // >= 9 m + r from trunks, 4 m edge gap to other props, the glade valley
      // left open. Generated once offline (mulberry32 seed 20261008 ^ 0xC4B).
      { asset: 'mossBoulder',      x: 17.7, z: -592.8, rotY: 0.17, scale: 2.41 },
      { asset: 'mossBoulder',      x: -19.5, z: -592.3, rotY: 2.12, scale: 3.48 },
      { asset: 'mossBoulder',      x: 232.7, z: -349.0, rotY: 5.95, scale: 2.25 },
      { asset: 'mossBoulder',      x: 230.8, z: -382.3, rotY: 0.66, scale: 3.69 },
      { asset: 'mossBoulder',      x: -233.2, z: -382.0, rotY: 4.00, scale: 2.94 },
      { asset: 'mossBoulder',      x: -239.4, z: -350.8, rotY: 4.71, scale: 3.36 },
      { asset: 'mossBoulder',      x: -57.3, z: -143.4, rotY: 2.74, scale: 3.88 },
      { asset: 'mossBoulder',      x: 139.5, z: -173.0, rotY: 5.92, scale: 3.05 },
      { asset: 'mossBoulder',      x: -167.5, z: -528.4, rotY: 1.24, scale: 3.91 },
      { asset: 'mossBoulder',      x: 163.2, z: -533.8, rotY: 2.27, scale: 2.79 },
      { asset: 'mossBoulder',      x: -179.6, z: -214.3, rotY: 6.08, scale: 3.75 },
      { asset: 'mossBoulder',      x: 195.7, z: -255.0, rotY: 5.23, scale: 3.35 },
      // CC-C6 BANDIT CAMPS (doc 62 L4/L5/L6, C-local -> world = z - 366): m15
      // fire (B's scale; cook station row at the SAME x/z in CONFIG.cooking
      // .stations) + 2 m16 bedrolls head-to-fire (GLB long axis = local x) at
      // 3.9 m on the camp's back side + a stump seat + a rubble pile; the open
      // side faces the King's Road (Alpha/Charlie +x, Bravo -x). Light dressing
      // on purpose: stump 8.1k / rubble 2k tris (fallenLog 20.8k + mossBoulder
      // 21.6k per camp would break the C4b 2M worst-case ledger near Charlie).
      // Every row: road edge >= 47 m, local r <= 198 (rim foot 240), seat slope
      // <= 8.8 deg, >= 6 m edge gap to every other prop row, wolf loops >= 96 m
      // from each fire (scratch/cc-c6/camp_probe.js). All PROPOSED, Nicko tunes.
      // L4 Alpha (-60, +180 local)
      { asset: 'banditCampfire',   x: -60.0, z: -186.0, rotY: 0.00, scale: 1.8 },
      { asset: 'banditBedroll',    x: -63.4, z: -184.1, rotY: 3.65, scale: 1.1 },
      { asset: 'banditBedroll',    x: -63.4, z: -187.9, rotY: 2.63, scale: 1.1 },
      { asset: 'treeStump',        x: -58.2, z: -182.9, rotY: 0.53, scale: 1.3 },
      { asset: 'rubblePile',       x: -58.8, z: -190.4, rotY: 1.10, scale: 1.0 },
      // L5 Bravo (+95, +130 local)
      { asset: 'banditCampfire',   x: 95.0, z: -236.0, rotY: 3.14, scale: 1.8 },
      { asset: 'banditBedroll',    x: 98.4, z: -237.9, rotY: 0.51, scale: 1.1 },
      { asset: 'banditBedroll',    x: 98.4, z: -234.1, rotY: 5.77, scale: 1.1 },
      { asset: 'treeStump',        x: 93.2, z: -239.1, rotY: 3.67, scale: 1.3 },
      { asset: 'rubblePile',       x: 93.8, z: -231.6, rotY: 4.24, scale: 1.0 },
      // L6 Charlie (-140, -140 local)
      { asset: 'banditCampfire',   x: -140.0, z: -506.0, rotY: 0.00, scale: 1.8 },
      { asset: 'banditBedroll',    x: -143.4, z: -504.1, rotY: 3.65, scale: 1.1 },
      { asset: 'banditBedroll',    x: -143.4, z: -507.9, rotY: 2.63, scale: 1.1 },
      { asset: 'treeStump',        x: -138.2, z: -502.9, rotY: 0.53, scale: 1.3 },
      { asset: 'rubblePile',       x: -138.8, z: -510.4, rotY: 1.10, scale: 1.0 },
      // CC-C8 THE ROT MOTHER'S OUTCROP (io/missions/2026-10-12-cc-c8-rotmother-den.md
      // sec 1): the CC-C7 open-nest b6Bones rim (6 rows) is REPLACED by a rock
      // outcrop centred C-local (-136, +147) = world (-136, -219), ~65 m NE of
      // the old glade, its black doorway facing SW (toward the glade). Rows
      // generated offline (scratch/cc-c8/gen_den.py; front axis U = (-0.6, -0.8)).
      // Seated by the standard prop seat (whGroundFeed footY, propFootR 1.2).
      // Wall rows: scale = length scale, sy / sz = height / thickness scales,
      // y = sink, wall = collider circles r 0.45 along the segment (the
      // boundaryWall per-segment tech; region-manager whPropColliders): x3 on
      // the 5.6 m recess sides, x4 on the 6.4 m back, x6 on the 10 m facades
      // (gap <= 1.0 m < the 1.4 m player body - the C2 x3 is per 4 m segment).
      // noCollide = a raised row (the lintel) that takes no ground collider.
      // tint = a per-row material multiply (rot egg sacs; region-manager clones
      // the material). cullM = per-row hide band (the scatter-cell fog rule:
      // 120 + the 0.92 show band = 110.4 m > the 108.2 m fog-visible reach):
      // the outcrop's 21.6k-tri boulders + 20.6k gates leave C's 2M ledger
      // beyond 120 m instead of 170 m. Site: nearest trunk row (yew -117.3,
      // -227.3) 20.5 m from the centre. All PROPOSED, Nicko tunes.
      // -- CC-C15 SW RELOCATION (Nicko 2026-10-20): the whole outcrop moved to
      //    the rim-mountain foot, SW quadrant (outcrop centre (-168.3, -197.7),
      //    bearing 225 r 238; den centre (-181.0, -185.0), r 256). Rows = the
      //    shipped CC-C8 TRIM block rigidly transformed (translate to the new
      //    opening + rotate by the new FACE 1.71). Same tri set = ledger flat.
      { asset: 'whWallA', x: -160.7, z: -195.1, rotY: 2.36, scale: 5.27, sy: 19.48, sz: 2.00, y: -0.4, wall: 6, cullM: 120 },
      { asset: 'whWallB', x: -167.8, z: -208.0, rotY: 2.36, scale: 5.27, sy: 19.26, sz: 2.00, y: -0.4, wall: 6, cullM: 120 },
      { asset: 'whWallA', x: -160.7, z: -200.3, rotY: 3.92, scale: 2.95, sy: 16.88, sz: 2.00, y: -0.4, wall: 3, cullM: 120 },
      { asset: 'whWallB', x: -163.5, z: -205.2, rotY: 3.92, scale: 2.95, sy: 16.69, sz: 2.00, y: -0.4, wall: 3, cullM: 120 },
      { asset: 'whWallA', x: -159.8, z: -204.1, rotY: 2.36, scale: 3.37, sy: 16.88, sz: 2.00, y: -0.4, wall: 4, cullM: 120 },
      { asset: 'cemeteryGate',     x: -174.5, z: -200.9, rotY: 5.62, scale: 5.20, cullM: 120 },
      { asset: 'mossBoulder',      x: -171.6, z: -194.3, rotY: 5.90, scale: 1.60, y: 7.0, noCollide: true, cullM: 120 },
      { asset: 'mossBoulder',      x: -181.5, z: -188.8, rotY: 1.91, scale: 1.40, cullM: 120 },
      { asset: 'bramble',          x: -171.4, z: -198.3, rotY: 5.50, scale: 1.80, cullM: 120 },
      { asset: 'bramble',          x: -168.3, z: -192.2, rotY: 0.51, scale: 2.10, cullM: 120 },
      { asset: 'bramble',          x: -170.6, z: -200.4, rotY: 1.81, scale: 1.40, cullM: 120 },
      { asset: 'bramble',          x: -165.7, z: -192.0, rotY: 3.11, scale: 2.40, cullM: 120 },
      { asset: 'bramble',          x: -167.7, z: -198.6, rotY: 4.41, scale: 1.60, cullM: 120 },
      { asset: 'bramble',          x: -165.1, z: -195.4, rotY: 5.71, scale: 1.50, cullM: 120 },
      { asset: 'bramble',          x: -169.3, z: -189.3, rotY: 5.38, scale: 2.00, cullM: 120 },
      { asset: 'bramble',          x: -170.3, z: -187.8, rotY: 0.72, scale: 1.60, cullM: 120 },
      { asset: 'graveMound',       x: -167.9, z: -200.4, rotY: 5.50, scale: 1.10, tint: 0x6f7a4a, cullM: 120 },
      { asset: 'graveMound',       x: -164.9, z: -193.4, rotY: 1.31, scale: 1.10, tint: 0x6f7a4a, cullM: 120 },
      { asset: 'graveMound',       x: -172.2, z: -200.8, rotY: 3.41, scale: 1.10, tint: 0x6f7a4a, cullM: 120 },
      { asset: 'graveMound',       x: -162.5, z: -192.3, rotY: 5.51, scale: 1.10, tint: 0x6f7a4a, cullM: 120 },
      // CC-C13b stone-ruin clusters (existing assets; probed scratch/cc13b_probe.cjs): C1 north of the old den approach, C2 west of the spawn glade
      { asset: 'churchArchway',        x: -101.0, z: -207.0, rotY: 2.6, scale: 1.7 },
      { asset: 'churchCornerButtress', x: -104.5, z: -205.0, rotY: 1.2, scale: 1.5 },
      { asset: 'stoneSteps',           x: -100.5, z: -210.5, rotY: 0.4, scale: 1.1 },
      { asset: 'rubblePile',           x: -98.5,  z: -203.5, rotY: 2.9, scale: 1.2 },
      { asset: 'mossBoulder',          x: -104.0, z: -210.0, rotY: 4.1, scale: 1.05 },
      { asset: 'rubblePile',           x: -31.0,  z: -139.0, rotY: 0.8, scale: 1.4 },
      { asset: 'churchCornerButtress', x: -33.0,  z: -143.5, rotY: 2.2, scale: 1.4 },
      { asset: 'mossBoulder',          x: -29.0,  z: -144.0, rotY: 5.0, scale: 1.0 },
      { asset: 'stoneCrossTilted',     x: -26.5,  z: -146.5, rotY: 3.0, scale: 1.55 },
      // CC-C16b DENSIFY: 4 bandit camp fires (CC-C6C kind campfire, night-only atmospheric; the STARTING tutorial fire stays the only cookable one)
      { asset: 'banditCampfire', x: -106.1, z: -472.1, rotY: 0.00, scale: 2.02, cullM: 140 },   // CC-C16b camp 1 fire
      { asset: 'banditCampfire', x: 118.0, z: -448.6, rotY: 0.70, scale: 2.02, cullM: 140 },   // CC-C16b camp 2 fire
      { asset: 'banditCampfire', x: -207.8, z: -246.0, rotY: 1.40, scale: 2.02, cullM: 140 },   // CC-C16b camp 3 fire
      { asset: 'banditCampfire', x: 144.2, z: -536.9, rotY: 2.10, scale: 2.02, cullM: 140 },   // CC-C16b camp 4 fire
      // CC-C17 FARM HOMESTEAD (v2 trimmed set; io/missions/2026-10-20-cc-c17b-integration-v2.md
      // step 2): cottage + well + a front yard (6 ok-fence-post rail sections + 2 ok-fence-
      // stonewall + ok-fence-gate + 2 ok-fence-corner-v2 brackets) + the gate lanternPost.
      // Site: cottage (150.5, -256.7), yard centre (150.4, -263.7) = bearing 124 r 182 from
      // the Stone, east of the spine; probe scratch/cc-c17/gen_farm.py (deterministic grid
      // scan bear 60-180 x r 150-200 step 2, no RNG): centre -> props 30.0 (yew 172.1,-242.9),
      // roads 104.3 (eastRoad), fires 62.0 (Bravo), loops 67.2 (east), zones clear; every row
      // >= 23.3 m to props / 96.7 to roads / 57.3 to loop segments; ground span 1.4 m.
      // Scales: cottage 3.68 (7.0 m) / well 1.26 (2.4 m) / gate 1.32 / corner-v2 1.5 (brief) /
      // rail section 1.85 (1.2 m tall, 3.5 m long: the GLB's 1.9 units are its LENGTH) /
      // stonewall 2.5 (= len 4.75 / 1.9). wall = segment colliders along local X (C8 tech).
      // cullM 120 (prop band). Barn/silo/haybales DEFERRED (tri budget). PROPOSED, Nicko tunes.
      { asset: 'okFarmCottage', x: 150.5, z: -256.7, rotY: 3.15, scale: 3.68, cullM: 120 },   // CC-C17 farm cottage, door +Z faces the east road (N)
      { asset: 'okFarmWell', x: 154.9, z: -264.7, rotY: 3.75, scale: 1.26, cullM: 120 },   // CC-C17 farm well, in the yard
      { asset: 'okFenceGate', x: 150.4, z: -269.7, rotY: 3.15, scale: 1.32, wall: 2, cullM: 120 },   // CC-C17 farm yard gate (front line)
      { asset: 'okFencePost', x: 147.4, z: -269.7, rotY: 3.15, scale: 1.85, wall: 3, cullM: 120 },
      { asset: 'okFencePost', x: 143.9, z: -269.6, rotY: 3.15, scale: 1.85, wall: 3, cullM: 120 },
      { asset: 'okFencePost', x: 153.4, z: -269.7, rotY: 3.15, scale: 1.85, wall: 3, cullM: 120 },
      { asset: 'okFencePost', x: 156.9, z: -269.7, rotY: 3.15, scale: 1.85, wall: 3, cullM: 120 },
      { asset: 'okFenceCornerV2', x: 141.7, z: -269.6, rotY: 3.15, scale: 1.50, cullM: 120 },   // CC-C17 farm corner-v2 bracket W
      { asset: 'okFenceCornerV2', x: 159.1, z: -269.7, rotY: 0.00, scale: 1.50, cullM: 120 },   // CC-C17 farm corner-v2 bracket E
      { asset: 'okFenceStonewall', x: 141.7, z: -266.5, rotY: 4.72, scale: 2.50, wall: 4, cullM: 120 },
      { asset: 'okFenceStonewall', x: 159.1, z: -266.6, rotY: 4.72, scale: 2.50, wall: 4, cullM: 120 },
      { asset: 'okFencePost', x: 141.8, z: -262.2, rotY: 4.72, scale: 1.85, wall: 3, cullM: 120 },
      { asset: 'okFencePost', x: 159.2, z: -262.3, rotY: 4.72, scale: 1.85, wall: 3, cullM: 120 },
      { asset: 'lanternPost', x: 148.2, z: -271.3, rotY: 3.15, scale: 2.535, cullM: 120 },   // CC-C17 farm gate beacon (amber = safety)
      // CC-C10 FARM BARN (io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md step 5): ONE
      // ok-farm-barn row behind the cottage. Probe scratch/cc-c10/probe_barn.js (deterministic
      // 1 m grid scan within 60 m of the cottage, no RNG; nearest gate-clear slot): props 26.1
      // (cottage), fires 41.5 (camp 95,-236), roads 133.7 (eastRoad), wolf loops 52.1 (ss);
      // seat span 0.45 m over r 5 (5.2 deg). Scale 5.5 (~10.4 m long, ~7 m tall); rotY faces
      // the east road (N) like the cottage. cullM 140 (giant row). PROPOSED, Nicko tunes.
      { asset: 'okFarmBarn', x: 136.5, z: -234.7, rotY: 3.15, scale: 5.50, cullM: 140 },   // CC-C10 farm barn (behind the cottage)
      // CC-C17 RUIN ACCENT (v2 step 3): okRuinArch + 2 okRuinColumn ADDED to the CC-C13b C1
      // cluster (churchArchway -101, -207 rows; kept as-is, no removals). Probe scratch/cc-c17/gen_ruin.py
      // (deterministic slot scan, no RNG): arch on the cluster's WSW side, opening facing the
      // cluster; columns 6 m either side along the arch's X (no interpenetration). Cluster
      // envelope (8 rows): centre (-105.3, -205.1) r 9.1 - nearest non-cluster prop 14.7 m =
      // the C4a boulder field (brief-sanctioned tight cluster); each new row >= 20.6 m to every
      // non-cluster prop, roads >= 111, loops >= 69, den opening 58. Scales 3.79 / 3.95 (7.2 /
      // 7.5 m). cullM 120. PROPOSED, Nicko tunes.
      { asset: 'okRuinArch', x: -111.2, z: -201.7, rotY: 2.10, scale: 3.79, cullM: 120 },   // CC-C17 ruin arch (7.2 m), opening faces the cluster
      { asset: 'okRuinColumn', x: -114.2, z: -206.9, rotY: 2.80, scale: 3.95, cullM: 120 },   // CC-C17 ruin column (7.5 m) flanking the arch
      { asset: 'okRuinColumn', x: -108.2, z: -196.5, rotY: 4.70, scale: 3.95, cullM: 120 },   // CC-C17 ruin column (7.5 m) flanking the arch
      // CC-C17 SENTINEL TREES (v2 step 4): 2 okTreeOak framing the den approach + 1 okTreePine
      // at the N road bend. The brief's nominal slots fail the 26 m gate (bearing 210: boulder
      // 17.8 m; bearing 240: camp-3 fire 8.0 m; (-15, -570): scree boulder 22.7 m), so each
      // row = the NEAREST clear slot (scratch/cc-c17/gen_trees.py, deterministic scan, no RNG):
      // props >= 26, fires >= 26, road >= 8 + trunk, den opening >= 26, seat slope <= 31 deg.
      // Oaks: bearing 208 r 235 (props 26.3, den 69.0) + bearing 245 r 221 (props 26.4, fire
      // 27.6, den 79.1); pine: road 10.4, props 26.1. ~1.9-unit GLBs: oak 13 / 12.5 (~24 m),
      // pine 12 (~22 m). cullM 140 (tall: culls past the prop band). PROPOSED, Nicko tunes.
      { asset: 'okTreeOak', x: -110.3, z: -158.5, rotY: 2.34, scale: 13.00, cullM: 140 },   // CC-C17 den-approach sentinel oak (nominal bearing 210 r 232; nearest clear slot)
      { asset: 'okTreeOak', x: -200.3, z: -272.6, rotY: 0.88, scale: 12.50, cullM: 140 },   // CC-C17 den-approach sentinel oak (nominal bearing 240 r 232; nearest clear slot)
      { asset: 'okTreePine', x: -13.0, z: -567.0, rotY: 1.20, scale: 12.00, cullM: 140 },   // CC-C17 N road bend pine (nominal -15, -570; nearest clear slot)
      // CC-C17 SPOOKY DRESSING (v2 step 5; existing manifest assets). Den corridor (bearing-225
      // band, r 200-235, mutual spacing >= 26.1 m): 2 deadTree (one per side of the approach
      // axis) + skullPile (15 m off the doorway) + 2 blightcap. A 26 m gate vs every prop is
      // infeasible in this band (3 of 3,321 grid points), so the dressing gate = >= 10 m to every
      // prop row (min 11.4), doorway >= 12, stains >= 4 + r, axis lateral 6-32 m (the walking
      // line stays open), camp-3 guards >= 12; seeded search random.Random(20261020), 4000 draws.
      // Ring fragment: 3 mossBoulder (2.8 / 2.2 / 2.5) on an 8 m arc, half-swallowed (y = -0.3 x
      // height), centre bearing 200 r 244 (nearest gate-clear slot to r 238; centre -> props
      // 27.0, rows >= 19.2; slope <= 5.8 deg). scratch/cc-c17/gen_spooky.py. PROPOSED, Nicko tunes.
      { asset: 'deadTree', x: -144.7, z: -180.8, rotY: 1.10, scale: 8.60, cullM: 140 },   // CC-C17 den-corridor dead tree (N of the approach)
      { asset: 'deadTree', x: -176.5, z: -233.0, rotY: 3.40, scale: 9.20, cullM: 140 },   // CC-C17 den-corridor dead tree (S of the approach)
      { asset: 'skullPile', x: -148.7, z: -206.6, rotY: 2.40, scale: 1.20, cullM: 120 },   // CC-C17 den-corridor skull pile (nearest the mouth)
      { asset: 'blightcap', x: -149.8, z: -233.5, rotY: 0.50, scale: 1.40, cullM: 120 },   // CC-C17 den-corridor blightcap
      { asset: 'blightcap', x: -123.1, z: -199.6, rotY: 2.20, scale: 1.60, cullM: 120 },   // CC-C17 den-corridor blightcap
      { asset: 'mossBoulder', x: -76.3, z: -140.4, rotY: 0.90, scale: 2.80, y: -1.18, cullM: 120 },   // CC-C17 ring fragment (half-swallowed, sink 0.3 x height)
      { asset: 'mossBoulder', x: -80.7, z: -144.2, rotY: 3.10, scale: 2.20, y: -0.93, cullM: 120 },   // CC-C17 ring fragment (half-swallowed, sink 0.3 x height)
      { asset: 'mossBoulder', x: -86.6, z: -144.1, rotY: 5.00, scale: 2.50, y: -1.05, cullM: 120 },   // CC-C17 ring fragment (half-swallowed, sink 0.3 x height)
      // west_hollow_den CC-WD1: the west pack's DEN SITE (doc 41 Family 1, first
      // den body; io/specs/cc-wd1-west-wolfpack-den-spec.md; art anchor
      // concept-05-night-ambush - moonlit hollow, indigo/charcoal base, NO new
      // warm accents: den dressing = bone/bare-earth neutrals). Hollow center
      // (-194,-451), south of the west pack patrol loop (nearest prop row/
      // patrol stop 25.96 m); site probe: y 1.2-2.0, slope <= 8.6 deg over 1 m;
      // clearance.py CLEARED (G-1..G-7). Thicket mouth arc (3 deadTree,
      // NE-facing) / hollow rim (3 mossBoulder, SW arc) / the LARDER (2
      // skullPile + buriedCoffin = a past victim's cache) / chewed-earth
      // rubble (2 rubblePile).
      { asset: 'deadTree', x: -190, z: -446, rotY: 5.60, scale: 1.70 },   // west_hollow_den thicket mouth E
      { asset: 'deadTree', x: -197, z: -445, rotY: 5.90, scale: 1.90 },   // west_hollow_den thicket mouth mid (tallest, the mouth's gate)
      { asset: 'deadTree', x: -201, z: -445, rotY: 0.40, scale: 1.40 },   // west_hollow_den thicket mouth W
      { asset: 'mossBoulder', x: -199, z: -455, rotY: 0.80, scale: 1.80 },   // west_hollow_den rim SW
      { asset: 'mossBoulder', x: -196, z: -458, rotY: 2.10, scale: 2.00 },   // west_hollow_den rim S
      { asset: 'mossBoulder', x: -201, z: -451, rotY: 4.60, scale: 1.30 },   // west_hollow_den rim W
      { asset: 'skullPile', x: -189, z: -454, rotY: 0.30, scale: 1.20 },   // west_hollow_den larder pile 1
      { asset: 'skullPile', x: -187, z: -452, rotY: 2.80, scale: 1.00 },   // west_hollow_den larder pile 2
      { asset: 'buriedCoffin', x: -186, z: -456, rotY: 1.20, scale: 1.60 },   // west_hollow_den larder: the past victim's cache
      { asset: 'rubblePile', x: -189, z: -449, rotY: 5.10, scale: 1.10 },   // west_hollow_den chewed earth SE
      { asset: 'rubblePile', x: -186, z: -446, rotY: 0.90, scale: 1.00 },   // west_hollow_den chewed earth E
      // east_hollow_den CC-ED1: the east pack's DEN SITE (doc 41 Family 1,
      // second den body; io/specs/cc-ed1-east-wolfpack-den-spec.md; art anchors
      // concept-05-night-ambush + day-05-ambush - moonlit hollow, indigo/charcoal
      // base, den dressing = bone/bare-earth neutrals, NO new warm accents).
      // Hollow center (210,-445), south of the east pack patrol loop (southern
      // extremity (205,-398), nearest prop row 41.77 m; site probe: y 0.05-1.42,
      // slope <= 8.7 deg over 1 m; clearance_ed1.py CLEARED G-1..G-7). Thicket
      // mouth arc (3 deadTree, N-facing) / hollow rim (3 mossBoulder, S arc) /
      // the LARDER (2 skullPile + buriedCoffin = a past victim's cache) /
      // chewed-earth rubble (2 rubblePile).
      { asset: 'deadTree', x: 206, z: -440, rotY: 5.60, scale: 1.70 },   // east_hollow_den thicket mouth W
      { asset: 'deadTree', x: 213, z: -439, rotY: 5.90, scale: 1.90 },   // east_hollow_den thicket mouth mid (tallest, the mouth's gate)
      { asset: 'deadTree', x: 217, z: -440, rotY: 0.40, scale: 1.40 },   // east_hollow_den thicket mouth E
      { asset: 'mossBoulder', x: 215, z: -449, rotY: 0.80, scale: 1.80 },   // east_hollow_den rim S
      { asset: 'mossBoulder', x: 208, z: -452, rotY: 2.10, scale: 2.00 },   // east_hollow_den rim SW
      { asset: 'mossBoulder', x: 217, z: -445, rotY: 4.60, scale: 1.30 },   // east_hollow_den rim E
      { asset: 'skullPile', x: 205, z: -448, rotY: 0.30, scale: 1.20 },   // east_hollow_den larder pile 1
      { asset: 'skullPile', x: 203, z: -446, rotY: 2.80, scale: 1.00 },   // east_hollow_den larder pile 2
      { asset: 'buriedCoffin', x: 202, z: -450, rotY: 1.20, scale: 1.60 },   // east_hollow_den larder: the past victim's cache
      { asset: 'rubblePile', x: 205, z: -443, rotY: 5.10, scale: 1.10 },   // east_hollow_den chewed earth W
      { asset: 'rubblePile', x: 202, z: -440, rotY: 0.90, scale: 1.00 },   // east_hollow_den chewed earth NW
      // CC-WM1 redseam: mined-scar dressing (doc 42 Part 5 WORKED SITE; art
      // anchor day/night-01-darkwood: cold stone light vs dark veg, moss
      // reclaiming the scar). 7-boulder quarried bank arc SW->N + 3 talus
      // tails + 2 stumps + 2 leaners = the forest reclaiming the pit.
      { asset: 'mossBoulder', x: 54, z: -586, rotY: 4.2, scale: 1.90 },   // redseam quarried bank S boulder (CC-WM1)
      { asset: 'mossBoulder', x: 59, z: -587, rotY: 5.3, scale: 2.10 },   // redseam quarried bank SE boulder (CC-WM1)
      { asset: 'mossBoulder', x: 64, z: -585, rotY: 0.6, scale: 1.80 },   // redseam quarried bank E boulder (CC-WM1)
      { asset: 'mossBoulder', x: 67, z: -581, rotY: 1.4, scale: 1.60 },   // redseam quarried bank E boulder 2 (CC-WM1)
      { asset: 'mossBoulder', x: 67.5, z: -575, rotY: 2.7, scale: 2.00 }, // redseam quarried bank NE boulder (CC-WM1)
      { asset: 'mossBoulder', x: 65, z: -570, rotY: 3.5, scale: 1.70 },   // redseam quarried bank N boulder (CC-WM1)
      { asset: 'mossBoulder', x: 60, z: -567, rotY: 4.9, scale: 1.50 },   // redseam quarried bank NNW boulder (CC-WM1)
      { asset: 'rubblePile', x: 57.5, z: -588, rotY: 2.1, scale: 1.20 },  // redseam talus tailing S (CC-WM1)
      { asset: 'rubblePile', x: 60.5, z: -578.5, rotY: 5.0, scale: 1.00 }, // redseam talus tailing center (CC-WM1)
      { asset: 'rubblePile', x: 51.5, z: -570, rotY: 3.3, scale: 1.10 },  // redseam talus tailing W (CC-WM1)
      { asset: 'treeStump', x: 49.5, z: -578, rotY: 1.1, scale: 1.30 },   // redseam clearing stump W (CC-WM1)
      { asset: 'treeStump', x: 66.5, z: -573, rotY: 5.8, scale: 1.20 },   // redseam clearing stump E (CC-WM1)
      { asset: 'deadTree', x: 47, z: -585, rotY: 2.4, scale: 1.60 },      // redseam scar-lip leaner SW (CC-WM1)
      { asset: 'deadTree', x: 68, z: -578, rotY: 5.9, scale: 1.40 },      // redseam scar-lip leaner E (CC-WM1)
    ],
    // west_hollow_den CC-WD1: the den LARDER cache nodes (doc 41 Family 1: the
    // den's loot identity is what the beast ate; CONFIG.gather bonePile, boneShard
    // x2 yield, respawn 150). FIRST C gather nodes: C had no nodes key before this
    // round. Node seats ride the new gather.js WH_GROUND terrain seat (2 lines).
    nodes: [
      { type: 'bonePile', x: -192.5, z: -461 },   // west_hollow_den larder cache S (by the rim boulders)
      { type: 'bonePile', x: -184, z: -450 },   // west_hollow_den larder cache E (by the coffin)
      { type: 'bonePile', x: -204, z: -453.5 },   // west_hollow_den outer scatter W
      { type: 'bonePile', x: -198.5, z: -441 },   // west_hollow_den thicket mouth approach NE
      // east_hollow_den CC-ED1: the east den's LARDER cache nodes (doc 41
      // Family 1 loot-identity law; CONFIG.gather bonePile, boneShard x2 yield,
      // respawn 150 - SAME type, no new node type, no new item, no new recipe).
      // Node seats ride the CC-WD1 gather.js WH_GROUND terrain seat (already
      // landed; NO code changes this round).
      { type: 'bonePile', x: 208.5, z: -455 },   // east_hollow_den larder cache S (by the rim boulders)
      { type: 'bonePile', x: 199.5, z: -446 },   // east_hollow_den larder cache W (by the coffin)
      { type: 'bonePile', x: 220, z: -447.5 },   // east_hollow_den outer scatter E
      { type: 'bonePile', x: 214.5, z: -435 },   // east_hollow_den thicket mouth approach N
      // CC-WM1 redseam: the rich seam's 8 vein nodes (doc 42 Part 5 entry
      // tier; dense cluster worth many trips, deplete/recover per doc 06 node
      // rules; squatters' bowl floor + bench foot + lips). WM1-A3 seats.
      { type: 'ironVein', x: 53, z: -577 },     // CC-WM1 redseam vein 1 (bowl floor W)
      { type: 'ironVein', x: 55.5, z: -573.5 },  // CC-WM1 redseam vein 2 (bowl floor E of fire)
      { type: 'ironVein', x: 61, z: -572 },      // CC-WM1 redseam vein 3 (bowl floor NE)
      { type: 'ironVein', x: 64, z: -575.5 },    // CC-WM1 redseam vein 4 (E bench foot)
      { type: 'ironVein', x: 63.5, z: -582 },    // CC-WM1 redseam vein 5 (SE bowl lip)
      { type: 'ironVein', x: 57, z: -584 },      // CC-WM1 redseam vein 6 (S bowl lip)
      { type: 'ironVein', x: 51.5, z: -581.5 },  // CC-WM1 redseam vein 7 (SW bowl lip)
      { type: 'ironVein', x: 50, z: -574 },      // CC-WM1 redseam vein 8 (W bowl floor)
    ],
    // CC-C8 ROT MOTHER'S DOORWAY dressing (sec 1-2; region-manager buildRegion
    // -> WH_Enemy.buildRotStains). The CC-C7 pool / light / fog rows MOVED into
    // the den (CONFIG.regionD.rotLair). What stays outside: a SECOND rot pool
    // (the C7 pool params, radius 5, darker) at the mouth + a 3-blob stain
    // trail stepping from the mouth toward the map interior. NO light. The
    // doorway void = a black card in the recess (reads as the den's dark).
    // enter = the E-to-enter interact (game.js tryDenDoor; region-defs C<->D
    // door.interact): prompt within interactM of the opening centre.
    // All PROPOSED, Nicko tunes.
    // CC-C15: stains/void moved with the outcrop (mouth pool at the SW
    // opening; the trail steps SE away from the doorway into the forest).
    rotLair: {
      stains: [
        { x: -167.8, z: -199.6, radius: 5.0 },     // mouth pool
        { x: -178.1, z: -190.4, radius: 1.8 },     // trail
        { x: -186.1, z: -182.5, radius: 1.4 },
        { x: -196.9, z: -180.0, radius: 1.0 },
      ],
      pool: { segments: 28, rings: 4, lift: 0.08,
        color: 0x141c10, color2: 0x222d15, speck: 0x3d4c22, textureSeed: 20261013, edgeFeather: 0.3 },
      void: { x: -160.4, z: -203.6, rotY: 2.36, width: 4.6, height: 9.0, color: 0x000000 },
      cullM: 120                      // stains + void hide past this from the player (the outcrop rows' band)
    },
    // CC-C10 FARMER NPC (io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md; js/npc.js
    // WH_NPC): one static placeholder body in the CC-C17 homestead yard, seated on the
    // heightfield (WH_GROUND.footY), shown + talkable only while C is active and the
    // player is inside cullM. E / touch USE within interactM opens the dialog panel
    // (game.js interact chain, after tryNotch). Probe scratch/cc-c10/probe_npc.js:
    // cottage 8.8 m, nearest prop 5.2 m (stonewall W), slope 3.8 deg over 1 m.
    // Body = the RAW rigged dwarf smith GLB (IO ruling B3b: art-law waiver, placeholder
    // for Astrabot; bind pose, no mixer). Direction copy = WEST (IO ruling B2: the den
    // mouth is due west of the farmstead); "the Old King's Barrow" = the Region D den
    // door (IO ruling B1, lore naming). PROPOSED, Nicko tunes.
    npc: {
      asset: 'farmerBody',
      x: 146.5, z: -264.5,            // PROPOSED, Nicko tunes (yard, W of the well, inside the gate)
      rotY: 3.15,                     // PROPOSED, Nicko tunes (faces the yard gate / the east road, N)
      footR: 0.4,                     // footY seat radius (m)
      bodyHeight: 1.8,                // PROPOSED, Nicko tunes (normalized height, = world.characterHeight)
      interactM: 3,                   // PROPOSED, Nicko tunes (talk range, m)
      cullM: 120,                     // PROPOSED, Nicko tunes (hidden past this from the player: the prop band)
      name: 'Farmer Aldric',
      labelLiftM: 0.35,               // name plate height above the head (m)
      labelM: 14,                     // PROPOSED, Nicko tunes (name plate shows within this, m)
      dialog: {
        // line1 -> line2 -> line3 on Continue; reaching line3 activates the quest
        line1: 'Hunter! Thank the old gods. They took my daughter - dragged her off in the night.',
        line2: 'Into the Old King\'s Barrow, the den in the hillside due west of here. Follow the setting sun past the dead trees.',
        line3: 'Bring her home. Whatever it costs. I will watch the road for you.',
        repeat: 'The barrow door, hunter. Bring her home.',
        // CC-AF2: repeat line by Standing tier (io/specs/cc-af2-affinity-dialog-spec.md rule 3).
        lineAffinityGood: 'Aldric: \'You are welcome at any fire in the camp, hunter. Word of the daughter travels further than you think.\'',
        lineAffinityDark: 'Aldric: \'The camp watches its fires when you pass, hunter. I have my daughter thanks to you — I will not watch too closely.\'',
        // CC-C11: rescue and homecoming copy (Nicko tunes).
        lineRescue: 'You are safe now. Go to your father; I will follow.',
        lineRescued: 'She is home, hunter. You have given me back my world.',
        lineComplete: 'My daughter is home. The chest at your camp is yours to use.',
        cont: 'Continue',
        close: 'Close',
        hint: 'Esc close',
        prompt: 'E - Talk to Farmer Aldric'                    // PROPOSED, Nicko tunes (B9 house style)
      }
    },
    // CC-C10 QUEST SEED: findDaughter. 'active' on the farmer's line 3 (js/npc.js);
    // 'complete' is CC-C11's job. Rides the additive save block questState
    // (game.js setupSaveHooks; schema v1, an older profile = 'available').
    quest: {
      id: 'findDaughter',
      states: ['available', 'active', 'complete'],
      // CC-C11: two further stages of the same three-state quest.
      hudRescued: 'Return to Farmer Aldric - his daughter is safe',
      hudComplete: 'Daughter home - camp chest unlocked',
      rescuedToast: 'The daughter is safe. Return to Farmer Aldric.',
      rescuePrompt: 'E - Search the sarcophagus',
      rescueInteractM: 3,
      hudText: 'Find the farmer\'s daughter - Old King\'s Barrow (W)'   // PROPOSED, Nicko tunes (B2 / B11)
    }
  },

  // CC-C8 (io/missions/2026-10-12-cc-c8-rotmother-den.md sec 3-6): Region D,
  // THE ROT MOTHER'S DEN. The smallest region: its OWN flat disc (radius 34,
  // the A/B flat-disc path - NO terrain row, heightAt 0) centred world
  // (-175, -271). A separate 2D pocket: it overlaps C's ground in world
  // coords but is never built beside it (one active region; C waits hidden).
  // Reached ONLY through the C<->D door (region-defs connections[2]): E at
  // the outcrop doorway (door.interact) crosses in; the walk-back plane at
  // the ring's mouth (door.planeZ inside the door window) crosses out. Both
  // land on door.land rows (the outcrop and the den mouth are ~60 m apart in
  // world coords: x is NOT preserved like B/C). No dormant-clock gate.
  // Every row below is PROPOSED, Nicko tunes.
  regionD: {
    id: 'rot_den',
    name: "The Rot Mother's Den",
    center: { x: -186, z: -180 },     // CC-C16a: cave body buried behind the mouth (r 263, ridge band)     // CC-C15 SW relocation (bearing 225, r 256 from C center)     // = the CC-C7 nest (C-local (-175, +95))
    groundRadius: 34,
    groundY: 0,                       // flat disc (C is hidden while D is active: no z-fight)
    groundColor: 0x12160e,            // wet black loam
    groundColor2: 0x1d2414,           // rot-moss secondary
    groundSeed: 1662061218,
    scatter: false,                   // hand rows only (no Round E scatter in the den)
    spawn: { x: -156, z: -190 },                      // CC-C16a                      // CC-C15      // inside the mouth (a death here without a camp)
    gravityY: -22,
    // sec 4 DARKNESS: d95 = sqrt(-ln 0.05) / 0.12 = 14.4 m (the far wall is a
    // black thought); the hemi fill = hemiBaseIntensity x 0.06. The always-
    // dark sky / moon / exposure row is CONFIG.dayNight.constantPhases.rot_den.
    fogColor: 0x05070a,
    fogDensity: 0.12,
    ambientLightLevel: 0.06,
    // C<->D door (region-defs connections[2]). planeZ = the ring mouth's outer
    // face (den-local z -24.6); the window = the 4.6 m ring gap. walkFrom: the
    // plane crossing exists ONLY from the den side (in C the line runs through
    // the forest: no crossing, no clamp, no scatter clear there). interact =
    // the outcrop doorway's E hook (C side). land = where a crossing INTO each
    // region puts the player + what they face. fadeSec = the black dip
    // (the death overlay element, non-lethal): fadeIn before the E cross,
    // fadeOut after either cross (E: 0.3 + 0.5 = 0.8; walk-out: 0 + 0.8).
    door: {
      planeZ: -215.2,                      // CC-C16a: the mouth plane, dug into the ridge band
      doorX: -150.8,                      // CC-C16a: mouth x on the plane
      doorHalfWidth: 3.0,             // the 4.6 m gap's walkable lane between the ring's end colliders is +-2.65: every way out crosses
      suspendDepthM: 0,
      wallGapPadM: 0,
      interactM: 3.5,
      interactAt: { x: -163.4, z: -202.6 },   // CC-C16a: mouth centre (faces the map centre)   // CC-C15: the SW outcrop opening centre (C)     // the outcrop opening centre (C)
      land: {
        forest_of_the_old_king: { x: -163.4, z: -202.6, faceX: 0.0, faceZ: -366.0 },
        rot_den: { x: -185.8, z: -180.2, faceX: -185.8, faceZ: -180.2 }
      },
      fadeIn: 0.3,
      fadeOut: 0.5,
      exitFadeOut: 0.8,
      text: { prompt: 'E - Enter the den' }
    },
    enemies: [],
    // the CC-C7 lair row, re-homed (homeRegionId 'rot_den'): the boss is
    // instanced from here AFTER the enemy rows (index 0 = her); the rot spawn
    // append after her at runtime. Position = CONFIG.enemy.rotmother.lair
    // (den-local (0, +6)) in world coords.
    lairs: [
      { type: 'rotmother', x: -185.8, z: -180.2 }
    ],
    // DEN BUILD (sec 3; scratch/cc-c8/gen_den.py). Flat ground: every row sits
    // at y 0 (+ its sink). Cavern = 10 vinestone ring segments r 24 (per-axis:
    // scale = the 15 m chord, sy = heightM 9, sz = thickness scale 2.4; wall =
    // r 0.45 colliders every <= 2 m - the den is CLOSED except the mouth), the
    // exit gap at den-local (0, -24) = the open-arch pattern (no segment
    // there). 4 mossBoulder shoulders, the brood furniture, the nest's 5 egg
    // sacs (moved INSIDE from the open lair).
    props: [
      // CC-C11: seed CC-C11-20261025-01; den-local (-15,-5); probe_sarc.js PASS.
      { asset: 'stoneSarcophagus', x: -201, z: -185, rotY: 0.4, scale: 1.2 },
      // -- cavern ring: 10 segments, exit gap between the first and the last
      { asset: 'whWallA', x: -165.5, z: -188.5, rotY: 2.72, scale: 7.84, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -176.1, z: -198.0, rotY: 2.12, scale: 7.84, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -179.6, z: -211.9, rotY: 1.51, scale: 7.84, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -174.5, z: -225.2, rotY: 0.91, scale: 7.84, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -162.7, z: -233.3, rotY: 0.30, scale: 7.84, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -148.5, z: -233.3, rotY: 5.98, scale: 7.84, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -136.7, z: -225.2, rotY: 5.38, scale: 7.84, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -131.6, z: -211.9, rotY: 4.77, scale: 7.84, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -135.1, z: -198.0, rotY: 4.17, scale: 7.84, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -145.7, z: -188.5, rotY: 3.56, scale: 7.84, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      // -- 4 mossBoulder shoulders at the wall foot (r 20.5-21.5), clear of the mouth
      //    (CC-C8 TRIM 2: kept the 2 gap flankers, the 2.30 row + the nest-adjacent 1.80; 5 cut)
      { asset: 'mossBoulder',      x: -163.1, z: -287.7, rotY: 0.00, scale: 1.60 },
      { asset: 'mossBoulder',      x: -155.5, z: -264.7, rotY: 1.40, scale: 1.80 },
      { asset: 'mossBoulder',      x: -195.4, z: -277.8, rotY: 4.90, scale: 2.30 },
      { asset: 'mossBoulder',      x: -186.9, z: -287.7, rotY: 5.60, scale: 2.40 },
      // -- brood furniture: 4 stone-steps (crypt kit), 2 skull-piles, 3 egg sacs, 6 blightcap
      { asset: 'stoneSteps',       x: -187.0, z: -285.0, rotY: 0.00, scale: 1.20 },
      { asset: 'stoneSteps',       x: -161.5, z: -283.0, rotY: 1.10, scale: 1.10 },
      { asset: 'stoneSteps',       x: -192.0, z: -267.0, rotY: 2.20, scale: 1.30 },
      { asset: 'stoneSteps',       x: -159.0, z: -263.0, rotY: 3.30, scale: 1.20 },
      { asset: 'skullPile',        x: -184.0, z: -288.0, rotY: 4.40, scale: 1.00 },
      { asset: 'skullPile',        x: -164.5, z: -253.0, rotY: 5.50, scale: 1.10 },
      { asset: 'graveMound',       x: -190.0, z: -277.0, rotY: 0.32, scale: 1.10, tint: 0x6f7a4a },
      { asset: 'graveMound',       x: -160.0, z: -274.0, rotY: 1.42, scale: 1.00, tint: 0x6f7a4a },
      { asset: 'graveMound',       x: -181.0, z: -251.5, rotY: 2.52, scale: 1.20, tint: 0x6f7a4a },
      { asset: 'blightcap',        x: -182.5, z: -282.0, rotY: 3.62, scale: 0.90 },
      { asset: 'blightcap',        x: -167.0, z: -286.5, rotY: 4.72, scale: 1.10 },
      { asset: 'blightcap',        x: -191.5, z: -259.0, rotY: 5.82, scale: 1.20 },
      { asset: 'blightcap',        x: -158.0, z: -256.0, rotY: 0.63, scale: 0.80 },
      { asset: 'blightcap',        x: -171.0, z: -252.0, rotY: 1.73, scale: 1.00 },
      { asset: 'blightcap',        x: -187.5, z: -272.0, rotY: 2.83, scale: 0.90 },
      // -- the nest (den-local (0, +6) = world (-175, -265)): 5 egg sacs ring r 7.5
      { asset: 'graveMound',       x: -177.2, z: -257.8, rotY: 0.00, scale: 1.10, tint: 0x6f7a4a },
      { asset: 'graveMound',       x: -182.5, z: -264.9, rotY: 1.70, scale: 1.10, tint: 0x6f7a4a },
      { asset: 'graveMound',       x: -177.4, z: -272.1, rotY: 3.40, scale: 1.10, tint: 0x6f7a4a },
      { asset: 'graveMound',       x: -169.0, z: -269.5, rotY: 5.10, scale: 1.10, tint: 0x6f7a4a },
      { asset: 'graveMound',       x: -168.9, z: -260.7, rotY: 0.52, scale: 1.10, tint: 0x6f7a4a }
    ],
    // THE NEST dressing (enemy.js lair build; the CC-C7 regionC.rotLair rows
    // MOVED here): the rot pool (C7 params, radius 12 -> 10, color2 shifted
    // sicker), the green fog cards, and the nest light (intensity 2.4 -> 1.6,
    // height 1.6 -> 1.2). The light is HERS: Enemy.lairSockets drops it while
    // the nest is cleared, the re-arm relights it (and the fog cards with it).
    rotLair: {
      pool: { radius: 10, segments: 40, rings: 6, lift: 0.08,
        color: 0x1f2a17, color2: 0x3b4a1a, speck: 0x5f7a2a, textureSeed: 20261012, edgeFeather: 0.22 },
      light: { height: 1.2, intensity: 1.6, color: 0x7fbf4f },
      fog: { cards: 10, radiusMin: 2.5, radiusMax: 9.0, heightMin: 0.5, heightMax: 1.6,
        width: 3.6, height: 1.5, opacity: 0.16, color: 0x7f9f55, driftSpeed: 0.12, showWithinM: 70 },
      cullM: 170                      // pool + fog hide past this from the player (never, in a 34 m disc)
    }
  },

  // CC-AD1 veil_crypt: The Old Throne's Crypt (io/specs/cc-ad1-veil-crypt-spec.md;
  // art anchor concept-08-veil-spire):
  // THE OLD THRONE'S CRYPT (doc 47 strata V1) - a hand-authored interior pocket
  // region reached from C's north-rim notch through a CC-C8-shaped tomb door
  // (region-defs connections[3]). The row below is shaped EXACTLY on regionD
  // (same key set, new values); PROPOSED seats, Nicko tunes). ART LAW: basalt
  // charcoal 0x121418 ground, bruised-purple 0x0a0810 fog, ONE crimson accent
  // (the albetar blightcap caps); dressing uses existing manifest assets ONLY
  // (whWallA/whWallB/stoneSarcophagus/stoneSteps/skullPile/blightcap/
  // mossBoulder/rubblePile - manifest keys listed here for the build note).
  regionE: {
    id: 'veil_crypt',
    name: "The Old Throne's Crypt",
    center: { x: 0, z: -596 },        // the north notch's mouth coordinate; the crypt disc lands beneath
    groundRadius: 20,                 // den is 34; a tighter pocket per the art anchor. PROPOSED
    groundY: 0,                       // flat disc (C is hidden while E is active: same law as the den)
    groundColor: 0x121418,            // basalt charcoal
    groundColor2: 0x171a20,           // slate-purple shadow secondary
    groundSeed: 1662061219,
    scatter: false,                   // hand rows only (no Round E scatter in the crypt)
    spawn: { x: 0, z: -604 },                         // the landing row's crypt end (crypt-local (0,-8))
    gravityY: -22,                    // den's value
    // sec DARKNESS: d95 = sqrt(-ln 0.05) / 0.13 = 13.3 m (the far wall is a
    // black thought). Region row fog/fill/ambient only - no constantPhase row
    // added this round (spec sec 5 excluded surface).
    fogColor: 0x0a0810,
    fogDensity: 0.13,
    ambientLightLevel: 0.07,
    // C<->E door (region-defs connections[3]). Shaped EXACTLY on regionD.door
    // above. veil_crypt law: same one-conn-one-door shape, the walk-back plane
    // exists ONLY from the crypt side. planeZ = the crypt-side mouth (crypt-local z -16 = world -612);
    // the window = the 4.8 m gap between the ring's end colliders (walkable
    // lane +-2.4: every way out crosses). walkFrom: the plane crossing exists
    // ONLY from the crypt side (walk-back; in C the line runs underground: no
    // crossing, no clamp, no scatter clear there). interact = the notch
    // mouth's E hook (C side). land = where a crossing INTO each region puts
    // the player + what they face. fadeSec = the black dip (the death overlay
    // element, non-lethal): E-descend 0.3 + 0.5; walk-out 0 + 0.8.
    door: {
      planeZ: -612,                       // crypt-local z -16
      doorX: 0,
      doorHalfWidth: 2.4,             // the tomb mouth (den is 3.0). PROPOSED
      suspendDepthM: 0,
      wallGapPadM: 0,
      interactM: 3.5,
      interactAt: { x: 0, z: -596 },   // C side: the notch mouth itself - E there enters the crypt
      land: {
        forest_of_the_old_king: { x: 0, z: -596, faceX: 0, faceZ: -366 },
        veil_crypt: { x: 0, z: -604, faceX: 0, faceZ: -604 }
      },
      fadeIn: 0.3,
      fadeOut: 0.5,
      exitFadeOut: 0.8,
      text: { prompt: 'E - Descend into the crypt' }
    },
    // 2 veil_crypt coven casters (CC-EC1 behavior contract: keep-distance ON
    // inside the
    // crypt). Crypt-local (5,4) / (-6,6) = world (5,-592) / (-6,-590); each
    // >= 8.0 m from the spawn/land row and from each other (13.0 / 15.23 /
    // 11.18 m), >= 4 m walk-clear of the ring (valspec-verified margins).
    enemies: [
      { type: 'coven', x: 5, z: -592 },
      { type: 'coven', x: -6, z: -590 }
    ],
    // CRYPT BUILD (scratch/cc-ad1/solve_geometry.py - the gen_den ring math
    // scaled to r 18). Flat ground: every row sits at y 0 (+ its sink). Cavern
    // = 8 vinestone ring segments (per-axis: scale = the 13.96 m chord, sy =
    // heightM 9, sz = thickness 2.4; wall = 7 r 0.45 colliders ~ every 2 m -
    // the crypt is CLOSED except the tomb mouth), the door gap at world
    // (0, -612) = the open-arch pattern (no segment there). Dressing: the
    // ALBETAR (sarcophagus + steps plinth, crypt-local (0,6), rotY facing the
    // door), dignified-dead scatter (the blightcap caps are the ONE crimson
    // accent), mossBoulder shoulders + a rubble flanker by the mouth. Every
    // row >= 4.34 m walk-clear of the ring (margin 4.0 + collider r 0.45).
    props: [
      // -- the albetar: 1 sarcophagus + 2 steps as a plinth at crypt-local (0,6)
      { asset: 'stoneSarcophagus', x: 0, z: -590, rotY: 0.00, scale: 1.20 },
      { asset: 'stoneSteps',       x: -1.0, z: -588.2, rotY: 0.60, scale: 1.10 },
      { asset: 'stoneSteps',       x: 1.0, z: -588.2, rotY: 5.68, scale: 1.10 },
      // -- veil_crypt cavern ring: 8 segments, door gap between the first and the last
      { asset: 'whWallA', x: 8.3, z: -612.0, rotY: 5.80, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallB', x: 17.0, z: -601.8, rotY: 5.04, scale: 7.35, sy: 11.55, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallA', x: 16.4, z: -588.5, rotY: 4.28, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallB', x: 6.7, z: -579.3, rotY: 3.52, scale: 7.35, sy: 11.55, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallA', x: -6.7, z: -579.3, rotY: 2.76, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallB', x: -16.4, z: -588.5, rotY: 2.00, scale: 7.35, sy: 11.55, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallA', x: -17.0, z: -601.8, rotY: 1.24, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      // -- CC-AD2: the whWallB at (-8.3, -612.0) is ERASED this round — its
      //    slot is the crypt's west aisle aperture (the mourners below flank
      //    it; region-defs connections[4] hook). No other ring row moves.
      // -- veil_crypt dignified dead: 2 skull piles, 4 blightcaps, 2 moss
      //    boulders, and a
      //    rubble flanker near the tomb mouth (crypt-local (-7,-3)); every row
      //    >= 4 m walk-clear of the ring (16 - rho), >= 4.45 m from every wall
      //    collider, >= 6 m from spawn/land, >= 5 m from covens — the full
      //    table re-verified by scratch/cc-ad1/solve_geometry.py (ALL PASS)
      { asset: 'skullPile',   x: -11, z: -600, rotY: 4.40, scale: 1.00 },
      { asset: 'skullPile',   x: -11, z: -593, rotY: 5.50, scale: 1.00 },
      { asset: 'blightcap',   x: 11, z: -599.5, rotY: 3.62, scale: 0.90 },
      { asset: 'blightcap',   x: 6, z: -586.5, rotY: 4.72, scale: 0.90 },
      { asset: 'blightcap',   x: -10, z: -596, rotY: 5.82, scale: 0.90 },
      { asset: 'blightcap',   x: 11, z: -592, rotY: 0.63, scale: 0.90 },
      { asset: 'mossBoulder', x: -9, z: -603.5, rotY: 2.00, scale: 2.20 },
      { asset: 'mossBoulder', x: 9, z: -603.5, rotY: 4.90, scale: 2.20 },
      // -- CC-AD2 the west aisle: the crypt ring's west-south arch piece
      //    (whWallB (-8.3,-612.0)) is ERASED — its slot is the aperture;
      //    the kneeling mourner pair flanks the opening (the processional
      //    gap; the E-side hook of the galleries door sits at (-14.5,-596),
      //    radius 3.5, region-defs connections[4]). Probe: aperture lane
      //    walkable (no ring collider within 1.5 m of x [-16,-13] z
      //    [-597.5,-594.5]), mourners >= 4 m from the remaining ring
      //    colliders, >= 5 m from covens, >= 6 m from the crypt spawn/land
      //    rows (scratch/cc-ad2/solve_geometry.py, ALL PASS).
      { asset: 'rubblePile',  x: -7, z: -599, rotY: 5.80, scale: 0.90 },
      // -- CC-AD2 the west aisle mourners: the pair is appended AFTER the AD1
      //    flanker rows, per the spec's "append mourner pair" (A-5). Seats are
      //    the compliant scan (spec seats blocked: aperture lane + ring
      //    colliders; scratch/cc-ad2/solve_geometry.py, ALL PASS).
      { asset: 'mourningStatue', x: -12.35, z: -589.15, rotY: 2.60, scale: 0.90 },
      { asset: 'rubblePile',     x: -14.25, z: -597.55, rotY: 1.20, scale: 1.10 }
    ]
  },

  // CC-AD2 veil_galleries: THE ERASED GALLERIES (io/specs/cc-ad2-veil-galleries-spec.md;
  // art anchors concept-08-veil-spire + concept-05-night-ambush):
  // doc 47 strata V2 - a hand-authored interior pocket region chained off the
  // crypt's WEST flank through a CC-AD1-shaped tomb door (region-defs
  // connections[4]). The row below is shaped EXACTLY on regionE
  // (same key set, new values); PROPOSED seats, Nicko tunes. ART LAW: basalt
  // 0x11131a ground one step colder than the crypt's 0x121418, bruised-purple
  // 0x0a0810 fog one step tighter (d95 12.0 m "the galleries swallowed the
  // light"), ambient 0.055 one step darker, ONE crimson accent = the
  // blightcap caps; dressing uses existing manifest assets ONLY (whWallA/
  // whWallB/mourningStatue/skullPile/blightcap/mossBoulder/rubblePile -
  // manifest keys listed here for the build note; NO new accent colors).
  regionF: {
    id: 'veil_galleries',
    name: "The Erased Galleries",
    center: { x: 0, z: -640 },        // 44 m due west-ward of the crypt center along -z; the galleries sit under C's west rim band
    groundRadius: 26,                 // crypt is 20; the galleries are one stratum wider - still a tight pocket. PROPOSED
    groundY: 0,                       // flat disc (C/E hidden while F is active: one-active-region law)
    groundColor: 0x11131a,            // basalt, one step colder than the crypt
    groundColor2: 0x16181f,           // shadow secondary
    groundSeed: 1662061329,           // FRESH - floor pattern must DIFFER from the crypt's 1662061219
    scatter: false,                   // hand rows only (no Round E scatter in the galleries)
    spawn: { x: 0, z: -650 },                         // the landing row's galleries end (10 m deep)
    gravityY: -22,                    // den's value
    // sec DARKNESS: d95 = sqrt(-ln 0.05) / 0.145 = 12.0 m (the far wall is a
    // black thought, one step quieter than the crypt's 13.3). Region row
    // fog/fill/ambient only - no constantPhase row (excluded surface).
    fogColor: 0x0a0810,
    fogDensity: 0.145,
    ambientLightLevel: 0.055,
    // E<->F door (region-defs connections[4]). Shaped EXACTLY on regionE.door.
    // veil_galleries law: same one-conn-one-door shape, the walk-back plane
    // exists ONLY from the galleries side. planeZ = the galleries mouth
    // (z -640); the window = the 4.4 m gap lane (|x| <= 2.2) between the
    // ring's end colliders (walkable lane: every way out crosses).
    // walkFrom: the plane crossing exists ONLY from the galleries side
    // (walk-back; in E the line runs underground: no crossing, no clamp).
    // interact = the crypt's WEST aisle aperture hook (E side, probe-verified
    // clear of the crypt dressing). land = where a crossing INTO each region
    // puts the player + what they face. fadeSec = the black dip: F-descend
    // 0.3 + 0.5; walk-out 0 + 0.8.
    door: {
      planeZ: -662,                       // the galleries mouth plane (CC-H1a: south-rim grammar, 4 m inside the r26 south rim -666)
      doorX: 0,
      doorHalfWidth: 2.2,             // the tomb-mouth lane (crypt 2.4). PROPOSED
      suspendDepthM: 0,
      wallGapPadM: 0,
      interactM: 3.5,
      interactAt: { x: -14.5, z: -596 },   // E side: the crypt's west aisle aperture
      land: {
        veil_crypt:      { x: 0, z: -604, faceX: 0, faceZ: -604 },
        veil_galleries:  { x: 0, z: -650, faceX: 0, faceZ: -650 }
      },
      fadeIn: 0.3,
      fadeOut: 0.5,
      exitFadeOut: 0.8,
      text: { prompt: 'E - Descend into the galleries' }
    },
    // 2 veil_galleries GHOUL wardens (doc 34 undead grammar: no dodge, no
    // parry, relentless, zone denial). Galleries-local computed to world;
    // each >= 8.0 m from spawn/land, >= 12.5 m from each other (12.51),
    // >= 4.45 m walk-clear of the ring (scratch/cc-ad2/solve_geometry.py).
    enemies: [
      { type: 'ghoul', x: -6, z: -636 },
      { type: 'ghoul', x: 6.5, z: -635.5 }
    ],
    // GALLERIES BUILD (scratch/cc-ad2/solve_geometry.py - the crypt ring math
    // on an r 22 chord-circle). Flat ground: every row sits at y 0 (+ its
    // sink). Pantheon = 8 whWall ring segments per the crypt's 45-deg cadence
    // (per-axis: scale = chord, sy = heightM, sz = thickness 2.4; wall = 7 r
    // 0.45 colliders ~ every 2 m - the galleries are CLOSED except the
    // mouth), the gap at world (0, -640) = the open-arch pattern (segment
    // angular position 22.5 deg OMITTED; the gap lane |x| <= 2.2 at the
    // z -640 plane). Dressing: THE ERASED FIGURE (the ONE mourningStatue,
    // "names once stood"), dignified-dead erasure scatter (the blightcap caps
    // are the ONE crimson accent), mossBoulder shoulders + a rubble flanker
    // by the mouth. Every row >= 4.0 m raw of the ring colliders (margin
    // 4.0 + collider r 0.45).
    props: [
      // -- THE ERASED FIGURE: the ONE headless plinth statue, "names once stood"
      { asset: 'mourningStatue', x: 7, z: -641, rotY: 4.00, scale: 1.00 },
      // -- veil_galleries basalt ring: 7 segments, the EAST mouth gap between
      //    the first and the last (segment angular position 22.5 deg OMITTED)
      { asset: 'whWallA', x: 8.42, z: -619.67, rotY: 3.53, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallB', x: -8.42, z: -619.67, rotY: 2.75, scale: 7.35, sy: 11.55, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallA', x: -20.33, z: -631.58, rotY: 1.96, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallB', x: -20.33, z: -648.42, rotY: 1.18, scale: 7.35, sy: 11.55, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallA', x: -8.42, z: -660.33, rotY: 0.39, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallB', x: 8.42, z: -660.33, rotY: 5.89, scale: 7.35, sy: 11.55, sz: 2.40, y: -0.2, wall: 7 },
      { asset: 'whWallA', x: 20.33, z: -648.42, rotY: 5.11, scale: 7.35, sy: 11.69, sz: 2.40, y: -0.2, wall: 7 },
      // -- veil_galleries erasure dressing: 2 skull piles, 2 blightcaps (the
      //    ONE crimson accent), 2 moss boulders, and a rubble flanker near
      //    the mouth; every row >= 4 m raw of the ring colliders, >= 6 m
      //    from spawn/land, >= 5 m from BOTH ghouls, >= 4 m from each other
      //    (scratch/cc-ad2/solve_geometry.py, ALL PASS)
      { asset: 'skullPile',   x: -10, z: -630, rotY: 4.40, scale: 1.00 },
      { asset: 'skullPile',   x: -12, z: -645, rotY: 5.50, scale: 1.00 },
      { asset: 'blightcap',   x: 11, z: -632, rotY: 3.62, scale: 0.90 },
      { asset: 'blightcap',   x: 10.5, z: -646, rotY: 4.72, scale: 0.90 },
      { asset: 'mossBoulder', x: -9, z: -650, rotY: 2.00, scale: 2.20 },
      { asset: 'mossBoulder', x: 9, z: -650, rotY: 4.90, scale: 2.20 },
      { asset: 'rubblePile',  x: -7, z: -641, rotY: 5.80, scale: 0.90 }
    ]
  },

  // ============================== CC-H1 LORD'S HOLD =============================
  // CC-H1 (doc 64 slot H1; doc 66 sec 8 recipe instance): the FIRST surface hold
  // hub, reached from C's north road. Shaped EXACTLY on regionF's sibling block
  // (Io spec sec 2; scratch/cc-h1/seat_scan.py frozen seat; amendments A/B/C
  // applied). First big disc (r 126 vs F's 26), first constantPhase-free
  // daylight-capable pocket, first zero-enemy region (a hub, not a hunt: the
  // garrison lives in H2). The hold disc sits fully OUTSIDE C's world footprint
  // (C's disc spans to z -646; the hold's south edge z -696 leaves a 50 m gap);
  // H1 is a FLAT disc with NO terrain row, so its ground has zero world-coords
  // overlap - the one-active-region law hides C while H1 is active.
  regionG: {
    id: 'lords_hold',
    name: "Lord's Hold",               // double-quoted: the raw apostrophe
    center: { x: 0, z: -822 },
    groundRadius: 126,                 // playRadius 124.5 (r 126 minus playerMargin 1.5)
    groundY: 0,                        // flat disc
    groundColor: 0x2f3339,             // cold stone slate
    groundColor2: 0x26292e,            // shadow secondary
    groundSeed: 1662061440,            // FRESH - differs from the landed 1662061217/1218/1219/1329
    scatter: false,                    // hand rows only: the hold yard is deliberately open
    spawn: { x: 0, z: -711 },          // just inside the south gate (death without a camp)
    gravityY: -22,                     // every landed region's value
    // sec DARKNESS: density 0.08 -> d95 = sqrt(-ln 0.05)/0.08 ~ 21.6 m: the
    // generous footprint READS across the yard; the hold runs the shared
    // day/night clock (NO constantPhase row - doc 66 sec 2 surface hold law).
    fogColor: 0x8a8f96,
    fogDensity: 0.08,
    ambientLightLevel: 0.10,
    // C<->G door (region-defs connections[5]). Shaped EXACTLY on regionF.door: the
    // walk-back plane exists ONLY from the hold side. planeZ = the gate plane
    // (4 m inside the disc's south edge z -696: walk-out law); the window =
    // the 9 m lane; interact = ON C's north road landing band (seat_scan.py
    // hook (5.0, -500), 96.1 m clear of the crypt hook AND the notch mouth,
    // every C prop >= 6.0 m, standable rC 134.1 <= 278.5). land = per-destination
    // rows (x NOT preserved per the D/E/F law). fadeSec = the black dip.
    door: {
      planeZ: -700,                      // the gate plane (tail 4 inside the south edge -696)
      doorX: 0,
      doorHalfWidth: 4.5,                // the walk-in window |x| <= 4.5
      suspendDepthM: 0,
      wallGapPadM: 0,
      interactM: 3.5,
      interactAt: { x: 5.0, z: -500 },   // C side: ON the north road landing band
      land: {
        forest_of_the_old_king: { x: 5, z: -500, faceX: 5, faceZ: -488 },
        lords_hold:           { x: 0, z: -711, faceX: 0, faceZ: -802 }
      },
      fadeIn: 0.3,
      fadeOut: 0.5,
      exitFadeOut: 0.8,
      text: { prompt: "E - Enter Lord's Hold" }
    },
    // enemies: ZERO rows (a hub, not a hunt; the garrison lives in H2's round)
    enemies: [],
    // CC-H1 THE CURTAIN WALL + hold dressing (io spec sec 2; every row >= 4.0 m raw
    // of the ring colliders, >= 6.0 m from spawn, >= 4.0 m mutual - the
    // licensed lanternPost/parapet pair sits at exactly 4.00; probes:
    // scratch/cc-h1/seat_scan.py + scratch/cc-h1/clearance.py).
    props: [
      { asset: 'whWallA', x: 4.4, z: -696.08, rotY: 3.18, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 13.17, z: -696.69, rotY: 3.25, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 21.88, z: -697.91, rotY: 3.32, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 30.48, z: -699.74, rotY: 3.39, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 38.94, z: -702.17, rotY: 3.46, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 47.2, z: -705.17, rotY: 3.53, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 55.23, z: -708.75, rotY: 3.6, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 63.0, z: -712.88, rotY: 3.67, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 70.46, z: -717.54, rotY: 3.74, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 77.57, z: -722.71, rotY: 3.8, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 84.31, z: -728.36, rotY: 3.87, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 90.64, z: -734.47, rotY: 3.94, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 96.52, z: -741.01, rotY: 4.01, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 101.94, z: -747.94, rotY: 4.08, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 106.85, z: -755.23, rotY: 4.15, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 111.25, z: -762.85, rotY: 4.22, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 115.11, z: -770.75, rotY: 4.29, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 118.4, z: -778.91, rotY: 4.36, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 121.12, z: -787.27, rotY: 4.43, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 123.25, z: -795.8, rotY: 4.5, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 124.77, z: -804.46, rotY: 4.57, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 125.69, z: -813.21, rotY: 4.64, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 125.69, z: -830.79, rotY: 4.78, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 124.77, z: -839.54, rotY: 4.85, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 123.25, z: -848.2, rotY: 4.92, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 121.12, z: -856.73, rotY: 4.99, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 118.4, z: -865.09, rotY: 5.06, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 115.11, z: -873.25, rotY: 5.13, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 111.25, z: -881.15, rotY: 5.2, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 106.85, z: -888.77, rotY: 5.27, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 101.94, z: -896.06, rotY: 5.34, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 96.52, z: -902.99, rotY: 5.41, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 90.64, z: -909.53, rotY: 5.48, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 84.31, z: -915.64, rotY: 5.55, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 77.57, z: -921.29, rotY: 5.62, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 70.46, z: -926.46, rotY: 5.69, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 63.0, z: -931.12, rotY: 5.76, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 55.23, z: -935.25, rotY: 5.83, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 47.2, z: -938.83, rotY: 5.9, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 38.94, z: -941.83, rotY: 5.97, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 30.48, z: -944.26, rotY: 6.04, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: 21.88, z: -946.09, rotY: 6.11, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: 13.17, z: -947.31, rotY: 6.18, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      // CC-H2 (doc 64 slot H2): the two south-pole flank rows ERASED 2026-11-07
      // — the garrison breach; the plane rides z -948 (regionH door row), the
      // aperture lane stays |x| <= 4 (probe: scratch/cc-h2/seat_scan.py).
      { asset: 'whWallA', x: -13.17, z: -947.31, rotY: 0.1, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -21.88, z: -946.09, rotY: 0.17, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -30.48, z: -944.26, rotY: 0.24, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -38.94, z: -941.83, rotY: 0.31, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -47.2, z: -938.83, rotY: 0.38, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -55.23, z: -935.25, rotY: 0.45, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -63.0, z: -931.12, rotY: 0.52, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -70.46, z: -926.46, rotY: 0.59, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -77.57, z: -921.29, rotY: 0.66, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -84.31, z: -915.64, rotY: 0.73, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -90.64, z: -909.53, rotY: 0.8, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -96.52, z: -902.99, rotY: 0.87, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -101.94, z: -896.06, rotY: 0.94, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -106.85, z: -888.77, rotY: 1.01, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -111.25, z: -881.15, rotY: 1.08, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -115.11, z: -873.25, rotY: 1.15, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -118.4, z: -865.09, rotY: 1.22, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -121.12, z: -856.73, rotY: 1.29, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -123.25, z: -848.2, rotY: 1.36, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -124.77, z: -839.54, rotY: 1.43, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -125.69, z: -830.79, rotY: 1.5, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -126.0, z: -822.0, rotY: 1.57, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -125.69, z: -813.21, rotY: 1.64, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -124.77, z: -804.46, rotY: 1.71, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -123.25, z: -795.8, rotY: 1.78, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -121.12, z: -787.27, rotY: 1.85, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -118.4, z: -778.91, rotY: 1.92, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -115.11, z: -770.75, rotY: 1.99, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -111.25, z: -762.85, rotY: 2.06, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -106.85, z: -755.23, rotY: 2.13, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -101.94, z: -747.94, rotY: 2.2, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -96.52, z: -741.01, rotY: 2.27, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -90.64, z: -734.47, rotY: 2.34, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -84.31, z: -728.36, rotY: 2.41, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -77.57, z: -722.71, rotY: 2.48, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -70.46, z: -717.54, rotY: 2.55, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -63.0, z: -712.88, rotY: 2.62, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -55.23, z: -708.75, rotY: 2.69, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -47.2, z: -705.17, rotY: 2.76, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -38.94, z: -702.17, rotY: 2.83, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -30.48, z: -699.74, rotY: 2.9, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -21.88, z: -697.91, rotY: 2.97, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallA', x: -13.17, z: -696.69, rotY: 3.04, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 },
      { asset: 'whWallB', x: -4.4, z: -696.08, rotY: 3.11, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },
      // -- CC-H1 THE WAR-TABLE HUB (the hold's identity, 82 m up the lane from
      //    the gate): ONE stoneSteps dais plinth at (0, -780). No table-shaped
      //    asset in the manifest - the gap is RECORDED in the build note (doc 66
      //    sec 8): the dais + banners carry the tableau v1.
      { asset: 'stoneSteps', x: 0, z: -780, rotY: 0, scale: 1.4 },
      // -- 4x banditCampfire braziers at the hub square (8.0 m from the hub,
      //    11.3 m mutual): lightSockets.banditCampfire (hf 0.55, intensity 3.2)
      //    = the amber accent. AMENDMENT B: the warm FAMILY is FIVE sockets -
      //    these 4 + the gate lanternPost below (intensity 9.0), one family.
      { asset: 'banditCampfire', x: -5.66, z: -776.34, rotY: 0, scale: 1.8 },
      { asset: 'banditCampfire', x: 5.66, z: -776.34, rotY: 0, scale: 1.8 },
      { asset: 'banditCampfire', x: -5.66, z: -787.66, rotY: 0, scale: 1.8 },
      { asset: 'banditCampfire', x: 5.66, z: -787.66, rotY: 0, scale: 1.8 },
      // -- CC-H1 banner dressing on the gate approach: 6x okFenceStonewall low
      //    parapet walls flanking the lane (x -13.5/-6.5/6.5/13.5 at
      //    z -702/-704/-706, alternating sides; both seat columns clear of
      //    the 4.5 m window).
      { asset: 'okFenceStonewall', x: -13.5, z: -702, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: -6.5, z: -704, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: 6.5, z: -702, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: 13.5, z: -704, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: -13.5, z: -706, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: 13.5, z: -706, rotY: 6.24, scale: 1.2 },
      // -- CC-H1 barracks corner: 3x whTent (>= 4 m mutual, >= 30 m off the lane)
      { asset: 'whTent', x: 38, z: -796, rotY: 1.2, scale: 1.0 },
      { asset: 'whTent', x: 44, z: -802, rotY: 1.8, scale: 1.0 },
      { asset: 'whTent', x: 32, z: -804, rotY: 0.9, scale: 1.0 },
      // -- CC-H1 chapel corner: archway facing the yard + 2 buttresses flanking
      { asset: 'churchArchway', x: -40, z: -800, rotY: 3.14, scale: 2.2 },
      { asset: 'churchCornerButtress', x: -49, z: -804, rotY: 3.5, scale: 2.0 },
      { asset: 'churchCornerButtress', x: -49, z: -796, rotY: 2.8, scale: 2.0 },
      // -- CC-H1 yard dressing: 4 mossBoulders + 2 rubble piles scattered wide
      { asset: 'mossBoulder', x: 20, z: -830, rotY: 1.94, scale: 1.5 },
      { asset: 'mossBoulder', x: -22, z: -826, rotY: 0.73, scale: 2.2 },
      { asset: 'mossBoulder', x: 52, z: -842, rotY: 4.82, scale: 1.7 },
      { asset: 'mossBoulder', x: -58, z: -838, rotY: 2.43, scale: 1.9 },
      { asset: 'rubblePile', x: 12, z: -724, rotY: 3.30, scale: 1.1 },
      { asset: 'rubblePile', x: -16, z: -736, rotY: 5.10, scale: 1.1 },
      // -- CC-H1 gate lanternPost at (6.5, -706): THE spec's own correction
      //    (x 2.5 sat INSIDE the 4.5 m window; 6.5 keeps the lane clear).
      //    lightSockets.lanternPost: hf 0.76, intensity 9.0.
      { asset: 'lanternPost', x: 6.5, z: -706, rotY: 4.72, scale: 2.535 }
    ],
  },

  // ============================== CC-H2 GARRISON KEEP ==============================
  // CC-H2 (doc 64 slot H2; doc 66 sec 2-8 recipe instance): the garrison
  // courtyard layer chained off the lord's hold (G <- H, the E/F chain
  // stepped one link). First H-chain TWO-SIDED door: the breach in G's south
  // curtain is a physical plane on BOTH sides (B/C grammar, no walkFrom/no
  // interact; suspendDepthM 4 lifts BOTH disc clamps - H1a lesson: with 0 the
  // plane sits outside both playable rims and the breach dies one-way).
  // Art anchors: concept-06-siege-council + char-04-bannerman-dark (cold
  // stone #3A424D, ONE amber family; crimson banned this round).
  regionH: {
    id: 'fort_garrison',
    name: 'Garrison Keep',
    center: { x: 0, z: -1024 },
    groundRadius: 80,                 // playRadius 78.5 (r 80 minus playerMargin 1.5)
    groundY: 0,                       // flat disc (one-active-region law)
    groundColor: 0x33363c,            // garrison slate: one step COLDER than G's 0x2f3339 (H2 = service stratum)
    groundColor2: 0x2a2d33,           // shadow secondary
    groundSeed: 1662061651,           // FRESH - differs from every landed seed (1217/1218/1219/1329/1440)
    scatter: false,                   // hand rows only
    spawn: { x: 0, z: -955 },         // just past the breach, inside the mouth throat
    gravityY: -22,                    // every landed region's value
    // sec DARKNESS: density 0.068 -> d95 = sqrt(-ln 0.05)/0.068 ~ 25.4 m; the
    // courtyard reads across its whole yard. Shared day/night clock (NO
    // constantPhase row - surface-adjacent hold stratum, doc 66 sec 2 law).
    fogColor: 0x7d8289,
    fogDensity: 0.068,
    ambientLightLevel: 0.09,
    // G<->H door (region-defs connections[6]). Shape: the CC-C2 B/C row for
    // the CONNECTION KEYS (two-sided physical plane, no walkFrom, no
    // interact), the landed E/F/H1 door rows for every DATA key (door-window
    // lane, land rows, fades). planeZ -948 = 4 m inside the H2 rim (-944),
    // 1.5 m inside G's playable south rim (-946.5): reachable BOTH ways with
    // suspendDepthM 4 (inOpenDoorBand lifts both disc clamps inside the
    // window). Arch: null (open breach). gatedTo: null (dormant-clock law
    // does not apply). NO text row (B/C precedent: no interact = no prompt).
    door: {
      planeZ: -948,
      doorX: 0,
      doorHalfWidth: 4.0,             // the breach lane |x| <= 4
      suspendDepthM: 4,               // CRITICAL: both-side reach (H1a trap)
      wallGapPadM: 0,
      land: {
        fort_garrison: { x: 0, z: -955, faceX: 0, faceZ: -1100 },   // land INTO H2 = the spawn row, facing the war-table heart
        lords_hold:    { x: 0, z: -941, faceX: 0, faceZ: -822 }     // walk-back INTO G, facing the hold heart
      },
      fadeIn: 0.3,
      fadeOut: 0.5,
      exitFadeOut: 0.8
    },
    // 2 bandit sentries (the garrison lives HERE - doc 64 H1 note law).
    // >= 8.0 m from spawn/land, mutual 21.0, >= 4.45 m walk-clear of the ring
    // (both ~30.0), every prop >= 5.0 m clear (props_scan.py).
    enemies: [
      { type: 'bandit', x: -10, z: -975 },
      { type: 'bandit', x: 11, z: -976 }
    ],
    props: [
      // -- CC-H2 DRESSING (scratch/cc-h2/props_scan.py, ALL PASS; every row >= 4.0 m
      //    raw of BOTH rings, >= 6.0 m from spawn/land rows, >= 4.0 m mutual,
      //    >= 5.0 m from both sentries, rho <= 78.5)
      // -- armory corner (east); the 2 whCampkit rows CARRY LIGHT (lightSockets.
      //    whCampkit is LIVE: hf 0.25, intensity 3.2 - BV-001 IO adjudication
      //    2026-11-07, option b: the light law is ONE warm FAMILY, not a socket
      //    count - H1 Amendment B precedent), so the amber family is FOUR sockets:
      //    lanternPost 9.0 + banditCampfire 3.2 + whCampkit 3.2 x2.
      { asset: 'whTent', x: 44, z: -1058, rotY: 5.75, scale: 1 },
      { asset: 'whCampkit', x: 38, z: -1052, rotY: 0.5, scale: 1 },
      { asset: 'whCampkit', x: 41, z: -1064, rotY: 1.2, scale: 1 },
      { asset: 'okRuinColumn', x: 52, z: -1050, rotY: 5.9, scale: 1.4 },
      // -- dungeon mouth corner (west)
      { asset: 'stoneSteps', x: -46, z: -1064, rotY: 1.57, scale: 1.3 },
      { asset: 'skullPile', x: -50, z: -1050, rotY: 4.4, scale: 1 },
      { asset: 'b6Bones', x: -42, z: -1076, rotY: 2.4, scale: 1 },
      { asset: 'rubblePile', x: -34, z: -1072, rotY: 5.8, scale: 1.1 },
      // -- war-table hub (the H1 dais trick: no table asset in the manifest - the
      //    dais + torch pair carry the tableau v1)
      { asset: 'stoneSteps', x: 0, z: -1097, rotY: 0, scale: 1.4 },
      { asset: 'torch', x: 4, z: -1093, rotY: 0, scale: 1 },
      { asset: 'torch', x: -4, z: -1093, rotY: 0, scale: 1 },
      // -- the mid-yard sentry brazier + gate lantern + armory campkits: THE ONE
      //    AMBER FAMILY, FOUR sockets total (lightSockets.banditCampfire hf 0.55
      //    intensity 3.2 + lightSockets.lanternPost hf 0.76 intensity 9.0 +
      //    lightSockets.whCampkit hf 0.25 intensity 3.2 x2 - one warm FAMILY,
      //    H1 Amendment B law; BV-001 resolved option b 2026-11-07). Crimson
      //    banned (art anchors this round). NOTE: 'torch' has NO lightSockets
      //    row - pure dressing.
      { asset: 'banditCampfire', x: 0, z: -990, rotY: 0, scale: 1.8 },
      { asset: 'lanternPost', x: 6.5, z: -954, rotY: 4.72, scale: 2.535 },
      // -- yard scatter
      { asset: 'mossBoulder', x: 26, z: -1000, rotY: 2, scale: 2 },
      { asset: 'mossBoulder', x: -24, z: -1030, rotY: 4.9, scale: 2.2 },
      { asset: 'rubblePile', x: 58, z: -992, rotY: 3.62, scale: 1.1 },
      // -- breach throat flankers (INSIDE H2, flanking the mouth lane; every row
      //    >= 4.0 m raw of EVERY remaining G ring collider, >= 16.0 m off H2's own
      //    ring, >= 4.0 m mutual from the manifest above)
      { asset: 'okFenceStonewall', x: 10, z: -968, rotY: 0, scale: 1.2 },
      { asset: 'okFenceStonewall', x: -10, z: -968, rotY: 0, scale: 1.2 },
      { asset: 'whWallB', x: 14.99, z: -945.42, rotY: 3.33, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 24.72, z: -947.92, rotY: 3.46, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 34.06, z: -951.61, rotY: 3.58, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 42.87, z: -956.45, rotY: 3.71, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 50.99, z: -962.36, rotY: 3.83, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 58.32, z: -969.24, rotY: 3.96, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 64.72, z: -976.98, rotY: 4.08, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 70.1, z: -985.46, rotY: 4.21, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 74.38, z: -994.55, rotY: 4.34, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 77.49, z: -1004.1, rotY: 4.46, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 79.37, z: -1013.97, rotY: 4.59, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 80.0, z: -1024.0, rotY: 4.71, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 79.37, z: -1034.03, rotY: 4.84, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 77.49, z: -1043.9, rotY: 4.96, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 74.38, z: -1053.45, rotY: 5.09, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 70.1, z: -1062.54, rotY: 5.22, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 64.72, z: -1071.02, rotY: 5.34, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 58.32, z: -1078.76, rotY: 5.47, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 50.99, z: -1085.64, rotY: 5.59, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 42.87, z: -1091.55, rotY: 5.72, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 34.06, z: -1096.39, rotY: 5.84, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 24.72, z: -1100.08, rotY: 5.97, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 14.99, z: -1102.58, rotY: 6.09, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 5.02, z: -1103.84, rotY: 6.22, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -5.02, z: -1103.84, rotY: 0.06, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -14.99, z: -1102.58, rotY: 0.19, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -24.72, z: -1100.08, rotY: 0.31, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -34.06, z: -1096.39, rotY: 0.44, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -42.87, z: -1091.55, rotY: 0.57, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -50.99, z: -1085.64, rotY: 0.69, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -58.32, z: -1078.76, rotY: 0.82, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -64.72, z: -1071.02, rotY: 0.94, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -70.1, z: -1062.54, rotY: 1.07, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -74.38, z: -1053.45, rotY: 1.19, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -77.49, z: -1043.9, rotY: 1.32, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -79.37, z: -1034.03, rotY: 1.45, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -80.0, z: -1024.0, rotY: 1.57, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -79.37, z: -1013.97, rotY: 1.7, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -77.49, z: -1004.1, rotY: 1.82, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -74.38, z: -994.55, rotY: 1.95, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -70.1, z: -985.46, rotY: 2.07, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -64.72, z: -976.98, rotY: 2.2, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -58.32, z: -969.24, rotY: 2.32, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -50.99, z: -962.36, rotY: 2.45, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -42.87, z: -956.45, rotY: 2.58, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -34.06, z: -951.61, rotY: 2.7, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -24.72, z: -947.92, rotY: 2.83, scale: 5.29, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -14.99, z: -945.42, rotY: 2.95, scale: 5.29, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'b6Bones', x: 46, z: -1076, rotY: 2.4, scale: 1 },       // armory-corner dead-arms clutter
      { asset: 'rubblePile', x: 36, z: -1042, rotY: 0, scale: 1 },      // rubble between kits and boulder
      { asset: 'okFenceStonewall', x: -66, z: -1024, rotY: 1.57, scale: 1 },  // west ossuary partition
      { asset: 'graveMound', x: -58, z: -1008, rotY: 0, scale: 1 }      // ossuary mound
    ],
    nodes: [
      { type: 'bonePile', x: -56, z: -1032 },   // ossuary corner W heap
      { type: 'bonePile', x: -63, z: -1044 },   // ossuary corner SW heap
      { type: 'bonePile', x: -50, z: -1044 },   // ossuary corner S heap
      { type: 'ironVein', x: 66,  z: -1042 },   // armory ore store E
      { type: 'ironVein', x: 58,  z: -1050 },   // armory ore store W
      { type: 'bonePile', x: 22,  z: -1046 },   // armory-yard wreckage heap
      { type: 'bonePile', x: -20, z: -992 },    // yard wreck heap W
      { type: 'bonePile', x: -13, z: -986 },    // breach approach flank (W of lane)
      { type: 'bonePile', x: 13,  z: -986 },    // breach approach flank (E of lane)
      { type: 'bonePile', x: 44,  z: -996 },    // yard-edge ossuary tail
      { type: 'ironVein', x: 44,  z: -1022 }    // yard-edge ore cache
    ]
  },

  regionI: {
    id: 'armory_deep',
    name: "The Armory Deep",
    center: { x: 0, z: -1120 },       // 8 m further south than regionH's center (0,-1024); chained pocket
    groundRadius: 18,                 // E is 20; D is 34; the pocket reads one stratum tighter. PROPOSED
    groundY: 0,                       // flat disc (H hidden while I is active: one-active-region law)
    groundColor: 0x101218,            // basalt, one step colder than H2's stone
    groundColor2: 0x14161c,           // shadow secondary
    groundSeed: 1662061654,           // FRESH: must not equal C 1662061217 / D ...218 / E ...219 / F ...1329 / G ...1440 / H ...1651
    scatter: false,                   // hand rows only (D/E/F pattern)
    spawn: { x: 0, z: -1128 },        // the landing row's I end (E-mirror: local (0,-8))
    gravityY: -22,                    // E/D's value
    fogColor: 0x0a0810,               // E's veil fog
    fogDensity: 0.13,                 // E's value (d95 = 13.3 m: the chamber is one black thought)
    ambientLightLevel: 0.07,          // E's value
    door: {
      planeZ: -1136,                  // I-local -16 (E-mirror: 2 m inside the r18 south rim -1138)
      doorX: 0,
      doorHalfWidth: 3.0,             // the E/F grammar (2.4/2.2) widened ONE step for a two-sided breach lane. PROPOSED
      suspendDepthM: 0,               // E/F/D value: the plane sits INSIDE the disc; no clamp lift needed
      wallGapPadM: 0,
      walkFrom: 'armory_deep',        // ONE-SIDED: the plane crosses ONLY from the I side (C/E grammar: H keeps no walkFrom)
      interact: {
        from: 'fort_garrison',        // the H-side hook (E's C-side notch-mouth pattern)
        x: -7.5, z: -1088.5, radius: 3.5
      },
      land: {
        fort_garrison: { x: 0, z: -1083.99, faceX: 0, faceZ: -1097 },   // +0.01 m: torch walk-clear >= 8.85; facing H2's war-table dais
        armory_deep:   { x: 0, z: -1128, faceX: 0, faceZ: -1120 }    // INTO I = the spawn row, facing the bier hall
      },
      fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
      text: { prompt: 'E - Descend into the armory' }
    },
    enemies: [
      { type: 'ghoul', x: -6.3, z: -1117 },
      { type: 'ghoul', x: 6.3, z: -1117 }
    ],
    props: [
      // -- the bier dais (E's albetar plinth pattern, hall center-north)
      { asset: 'stoneSarcophagus', x: 0, z: -1118.5, rotY: 0.00, scale: 1.20 },
      { asset: 'stoneSteps',       x: -2.4, z: -1115.7, rotY: 0.60, scale: 1.10 },
      { asset: 'stoneSteps',       x: 2.4, z: -1115.7, rotY: 5.68, scale: 1.10 },
      // -- supply yard west: campkit + tent + fence + the crimson lantern
      { asset: 'lanternPost',      x: 6.4, z: -1127.2, rotY: 5.2, scale: 1 },
      { asset: 'skullPile',        x: -6.9, z: -1127.2, rotY: 4.4, scale: 1 },
      { asset: 'whCampkit',        x: -9.9, z: -1123.6, rotY: 0.3, scale: 1 },
      { asset: 'whCampkit',        x: 9.9, z: -1123.0, rotY: 5.9, scale: 1 },
      { asset: 'whTent',           x: -12.1, z: -1120.6, rotY: 1.2, scale: 1 },
      { asset: 'whTent',           x: 12.1, z: -1120.0, rotY: 5.2, scale: 1 },
      // -- the crimson pair: 2 blightcap caps (the ONE accent family;
      //    'blightcap' has NO lightSockets key: dark flowers by design)
      { asset: 'blightcap',        x: -12.4, z: -1117.6, rotY: 3.62, scale: 0.90 },
      { asset: 'blightcap',        x: 12.4, z: -1117.3, rotY: 0.63, scale: 0.90 },
      // -- ruined columns flanking the hall's north wall
      { asset: 'okRuinColumn',     x: -9.4, z: -1117.5, rotY: 5.9, scale: 1.4 },
      { asset: 'okRuinColumn',     x: 9.4, z: -1117.0, rotY: 5.9, scale: 1.4 },
      // -- CC-H2b CAVERN RING: full 10-row closure (the D/E/F closed-cavern
      //    law; the plane exits THROUGH the ring's south point -1138 which
      //    backs the door like E's -612/-614 pair). scale = chord/1.899
      //    (chord 11.12 = 2*18*sin(18 deg) => 5.8581); centers k*36 deg;
      //    rotY = bearing + PI. NO omission, NO window probe: the ring is
      //    closed behind the plane like E's crypt mouth; the door lane
      //    (|x|<=3 at z -1136) clears the NEAREST ring collider (the
      //    south-point row (0,-1138)) by ~1.55-1.60 m — the governing
      //    >= 1.0 m lane clearance (BV-002, Testerbot 11-07: my earlier
      //    5.85 'nearest' figure named the wrong rows; geometry unchanged).
      { asset: 'whWallA', x: 0, z: -1102, rotY: 3.14, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 10.58, z: -1105.44, rotY: 3.77, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 17.12, z: -1114.44, rotY: 4.4, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 17.12, z: -1125.56, rotY: 5.03, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: 10.58, z: -1134.56, rotY: 5.65, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: 0, z: -1138, rotY: 6.28, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -10.58, z: -1134.56, rotY: 6.91, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -17.12, z: -1125.56, rotY: 7.54, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallA', x: -17.12, z: -1114.44, rotY: 8.17, scale: 5.8581, sy: 11.69, sz: 2.40, y: -0.2, wall: 8 },
      { asset: 'whWallB', x: -10.58, z: -1105.44, rotY: 8.8, scale: 5.8581, sy: 11.55, sz: 2.40, y: -0.2, wall: 8 }
    ]
  },

  regionJ: {
    id: 'veil_spire_approach',
    name: "The Spire Approach",
    center: { x: 0, z: -700 },        // 60 m deeper than F's center (0,-640); x-0 chain, mirror I's 8+ m pocket gap: J's north rim -660 vs F's ring north point -662 is the SAME one-active-region tolerance I/H landed (2-4 m overlaps)
    groundRadius: 40,                 // doc 64 H3 boss-tier space: 2.2x F's 26, 2x I's 18. PROPOSED, Nicko tunes
    groundY: 0,                       // flat disc (F hidden while J is active: one-active-region law)
    groundColor: 0x0d0f15,            // basalt, one step colder than F's 0x11131a
    groundColor2: 0x111318,           // shadow secondary
    groundSeed: 1662061763,           // FRESH: must not equal any landed seed (1217/1218/1219/1329/1440/1651/1654)
    scatter: false,                   // hand rows only (D/E/F/I law)
    spawn: { x: 0, z: -730 },         // the landing row's J end (I-mirror: local (0,-30) lands 30 m deep, 8 m inside the far-wall plane)
    gravityY: -22,                    // every landed region's value
    // sec DARKNESS: density 0.15 -> d95 = sqrt(-ln 0.05)/0.15 = 11.61 m:
    // one stratum quieter than F's 12.0. Region row fog/fill/ambient only.
    fogColor: 0x0a0810,               // the veil fog family
    fogDensity: 0.15,
    ambientLightLevel: 0.05,          // F is 0.055; J is one step deeper
    door: {
      planeZ: -738,                   // J-local -38 (I-mirror: 2 m inside the far SOUTH rim -740; the plane exits THROUGH the ring's south point row)
      doorX: 0,
      doorHalfWidth: 2.2,             // F's tomb-mouth lane
      suspendDepthM: 0,               // E/F/D/I value: the plane sits INSIDE the disc; no clamp lift needed
      wallGapPadM: 0,
      walkFrom: 'veil_spire_approach', // ONE-SIDED: the plane crosses ONLY from J (conn[7] grammar: F keeps no walkFrom)
      interact: {
        from: 'veil_galleries',       // the F-side hook (conn[7] H-side pattern)
        x: 7.5, z: -654, radius: 3.5  // inside F's south rim (-666), 12 m north of it; probe-verified clear of every F prop, ring collider, ghoul, and F's own land row
      },
      land: {
        veil_galleries:       { x: 2, z: -652, faceX: 2, faceZ: -644 },   // walk back INTO F just north of the hook, facing the galleries' heart
        veil_spire_approach:  { x: 0, z: -730, faceX: 0, faceZ: -700 }    // INTO J = the spawn row, facing the gauntlet head monolith
      },
      fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
      text: { prompt: 'E - Descend toward the spire' }
    },
    // STATUE GAUNTLET wardens (doc 34 undead grammar, 2 rows, ghoul type):
    // wide stance clears the processional; each >= 8 m from spawn/land,
    // >= 12.5 m apart (30.0), >= 4.45 m walk-clear of the ring
    enemies: [
      { type: 'ghoul', x: -15, z: -708 },
      { type: 'ghoul', x: 15, z: -708 }
    ],
    // CC-H4: the Scar-Reader nests at the wake-21-reserved boss space (0,-709),
    // 9.0 m south of the spire-root column (its collider), inside the vault ring.
    // SHAPE NOTE (V-5/N-2): the row CARRIES x/z (regionD legacy shape) because
    // the live constructor path consumes them - region-manager buildRegion
    // (~1912) passes row e.x/e.z straight into new WH_Enemy(.., e.x, e.z);
    // a bare { type } row's undefined x/z would seat the body at world (0,0)
    // (THREE r185 Vector3 defaults x=z=0) and NaN her on revive. The NEST
    // itself (pool / light / fog / save letter 'J') is derived from
    // CONFIG.enemy.scarreader.lair via lairNest regardless - the two agree.
    lairs: [
      { type: 'scarreader', x: 0, z: -709 }
    ],
    // CC-H4 nest dressing: the pact-scar pool + crimson light/fog (the
    // concept-08 accent family); textureSeed 20261107 FRESH (den pool 20261012,
    // ground 1651/1654, J groundSeed 1662061763).
    rotLair: {
      pool: { radius: 9, segments: 40, rings: 5, lift: 0.08,
        color: 0x1a0f12, color2: 0x2a1116, speck: 0x5a2028, textureSeed: 20261107,
        edgeFeather: 0.22 },
      light: { height: 1.3, intensity: 1.7, color: 0xd85050 },
      fog: { cards: 8, radiusMin: 2.0, radiusMax: 7.0, heightMin: 0.4, heightMax: 1.4,
        width: 3.2, height: 1.3, opacity: 0.15, color: 0x8a4550, driftSpeed: 0.12,
        showWithinM: 70 },
      cullM: 170
    },
  props: [
    // -- THE GAUNTLET: two mourners per side watching the processional
    { asset: 'mourningStatue', x: -7, z: -712, rotY: 4.00, scale: 1.00 },
    { asset: 'mourningStatue', x:  7, z: -712, rotY: 5.28, scale: 1.00 },
    { asset: 'mourningStatue', x: -7, z: -704, rotY: 4.00, scale: 1.00 },
    { asset: 'mourningStatue', x:  7, z: -704, rotY: 5.28, scale: 1.00 },
    { asset: 'stoneSteps',     x: -2.4, z: -718, rotY: 0.60, scale: 1.10 },
    { asset: 'stoneSteps',     x:  2.4, z: -718, rotY: 5.68, scale: 1.10 },
    // -- THE SPIRE ROOT (boss-tier heart, north end of the hall)
    { asset: 'okRuinColumn', x: 0, z: -700, rotY: 0.00, scale: 2.40 },
    { asset: 'okRuinColumn', x: -8, z: -696, rotY: 0.30, scale: 1.40 },
    { asset: 'okRuinColumn', x:  8, z: -696, rotY: 5.98, scale: 1.40 },
    // -- the crimson pair: 2 blightcap caps (the ONE accent family with the lamp)
    { asset: 'blightcap', x: -12, z: -692, rotY: 3.62, scale: 0.90 },
    { asset: 'blightcap', x:  12, z: -692, rotY: 0.63, scale: 0.90 },
    // -- the ONE crimson lamp (regionI's family; NOT near the ghouls)
    { asset: 'lanternPost', x: -6, z: -724, rotY: 5.20, scale: 1 },
    // -- erasure scatter (F's grammar): 2 skull piles, 1 moss boulder
    { asset: 'skullPile',   x: -13, z: -723, rotY: 4.40, scale: 1.00 },
    { asset: 'skullPile',   x: -5,  z: -668, rotY: 3.60, scale: 1.00 },
    { asset: 'mossBoulder', x: 0,   z: -672, rotY: 2.00, scale: 2.20 },
    // -- CC-H3 VAULT RING: full 10-row closure (the I ring math on groundRadius
    //    40: chord 24.7216 = 2*40*sin(18 deg) => scale 13.019 = chord/1.899;
    //    centers k*36 deg on the r40 circle, listed clockwise from north;
    //    rotY = 3.14 + k*0.6283; NO omission: the ring is closed behind the
    //    plane like I/E's mouth. The walk-back lane (|x| <= 2.2 at z -738)
    //    clears the south-point row (0,-740) colliders by 2.00 - 0.45 = 1.55 m
    //    -- the governing >= 1.0 m lane clearance, same figure I's verdict carries)
    { asset: 'whWallA', x: 0,     z: -660,    rotY: 3.14, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: 23.51, z: -667.64, rotY: 3.77, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: 38.04, z: -687.64, rotY: 4.40, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: 38.04, z: -712.36, rotY: 5.03, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: 23.51, z: -732.36, rotY: 5.65, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: 0,     z: -740,    rotY: 6.28, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: -23.51, z: -732.36, rotY: 6.91, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: -38.04, z: -712.36, rotY: 7.54, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallA', x: -38.04, z: -687.64, rotY: 8.17, scale: 13.019, sy: 11.69, sz: 2.40, y: -0.2, wall: 9 },
    { asset: 'whWallB', x: -23.51, z: -667.64, rotY: 8.80, scale: 13.019, sy: 11.55, sz: 2.40, y: -0.2, wall: 9 }
  ]
  },

  // CC-H5 tithe_vaults: THE VAULTS pocket, the J-mirror (delve strata V4).
  // Art anchor inherited per the art-block ruling - the Veil chain keeps its
  // ancestors' frame (concept-08-veil-spire + char-04-bannerman); the 36-set
  // has no tithe-vault frame and the provider is hard-blocked this wake.
  regionK: {
    id: 'tithe_vaults',
    name: "The Tithe Vaults",
    center: { x: 0, z: -880 },        // 180 m deeper than J's center (0,-700): one clean
                                      // stratum gap; K's north rim -846 vs J's ring south
                                      // point -740 = 106 m of unrendered dark (the
                                      // one-active-region law makes the gap invisible)
    groundRadius: 34,                 // PROPOSED (I's 18 x1.9, below J's boss-tier 40)
    groundY: 0,                       // flat disc
    groundColor: 0x0b0d12,            // one step colder than J's 0x0d0f15
    groundColor2: 0x0e1013,
    groundSeed: 448271909,            // FRESH: differs from every landed seed
                                      // (1217/1218/1219/1329/1440/1651/1654/1662061763)
    scatter: false,                   // hand rows only (D/E/F/I/J law)
    spawn: { x: 0, z: -856 },         // ADJ-E: pairs with the plane -848 (spawn 8 m
                                      // SOUTH of the walk-back plane: walk-EXIT faces
                                      // south into the vault, and the crossing cannot
                                      // re-trigger). SPEC FIX: sec 3/5's pair (-844
                                      // plane / -856 spawn, 12 m) left the plane OUTSIDE
                                      // the disc (above) and the landing row ON the
                                      // walk-back plane's line (ping-pong). The nearest
                                     // zealot (0,-865) still sits 9.0 m from the landing
                                      // row - the >= 8.0 spawn floor ADJ-E defends
    gravityY: -22,                    // every landed region's value
    // sec DARKNESS: density 0.16 -> d95 = sqrt(-ln 0.05)/0.16 = 10.82 m:
    // one stratum quieter than J's 11.61. Region row fog/fill/ambient only.
    fogColor: 0x0a0810,               // the veil fog family
    fogDensity: 0.16,
    ambientLightLevel: 0.045,         // J is 0.05; K is one step deeper
    door: {
      planeZ: -848,                   // the walk-OUT plane, 2 m inside the north rim
                                      // (-848 vs rim -846 - the J-mirror pair law).
                                      // SPEC FIX (sec 3's -844): -844 sat 2 m OUTSIDE
                                      // the rim (-846 rim < -844 plane), unreachable
                                      // from inside K under the CC-C2 rim clamp (door
                                      // connections carry no plane clamp and
                                      // suspendDepthM 0 gives no door-band extension);
                                      // every landed plane sits INSIDE its region's
                                      // disc (J conn[7] -662 vs rim -660, conn[8]
                                      // -738 vs rim -740)
      doorX: 0,
      doorHalfWidth: 2.2,             // the F/J tomb-mouth lane
      suspendDepthM: 0,               // E/F/D/I/J value: the plane sits INSIDE the disc
      wallGapPadM: 0,
      walkFrom: 'tithe_vaults',       // ONE-SIDED: the plane crosses ONLY from K
                                      // (conn[8] grammar: J keeps no walkFrom)
      interact: {
        from: 'veil_spire_approach',  // the J-side hook (conn[8] F-side pattern)
        x: 7.5, z: -678, radius: 3.5  // 7.5 m NE of the spire-root colonnade approach,
                                      // INSIDE J's north half; probe-verified clear of
                                      // every J row (nearest: mossBoulder 9.60 m)
      },
      land: {
        veil_spire_approach: { x: 2, z: -682, faceX: 2, faceZ: -700 },
                                      // walk back INTO J beside the hook, facing the
                                      // spire root hall; 20.0 m south of J's walk-out
                                      // plane -662 (the |dz| arithmetic, N-check)
        tithe_vaults:  { x: 0, z: -856, faceX: 0, faceZ: -880 }
                                      // INTO K = the spawn row (8 m south of the
                                      // plane; no re-trigger), facing the vault gate
      },
      fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
      text: { prompt: 'E - Descend into the tithe vaults' }
    },
    // THE ZEALOT PACKS + the drifted dead (doc 47 V4 encounters; doc 34):
    // zealots defend the vault's north approach, ghouls drift the deeper
    // coin rows. Zealot type = the CONFIG.enemy.zealot row (bandit chassis
    // + guard grammar; NO engine edits - bodyByType/animVariantByType map
    // it onto the banditBody manifest). Seats: each >= 8 m from spawn/land,
    // mutual >= 15.13, >= 4.45 m ring walk-clear (ghouls rho 29 -> 5.0),
    // >= 5 m from every non-ring prop row (the N-5 colonnade binding is
    // healed - see the in-row note; the probe re-derives every floor).
    enemies: [
      { type: 'zealot', x: -15, z: -863 },  // SPEC FIX (valspec N-5 binding): the sec-3
      { type: 'zealot', x:  15, z: -863 },  // seats (+-9,-876) sat 4.12 m from the dais
                                            // colonnade (+-8,-872), below the >= 5.0
                                            // enemy-vs-prop floor; moved to the north-
                                            // wall pack line: props >= 5.39, mutuals
                                            // >= 15.13, spawn >= 16.55, ring-clear 11.33
      { type: 'zealot', x: 0, z: -865 },    // ADJ-E: 9.0 m from the landing row (>= 8)
      { type: 'ghoul', x: -11, z: -892 },
      { type: 'ghoul', x:  11, z: -892 }
    ],
    // CC-H5: the captain nests at the vault gate dais (0,-872), 16 m south
    // of the spawn row (0,-856) and 8.0 m north of the relocated colossus
    // (0,-880; SPEC FIX see its row). SHAPE NOTE: the row CARRIES x/z (the
    // CC-H4 note applies verbatim: region-manager buildRegion passes
    // row e.x/e.z straight into new WH_Enemy(.., e.x, e.z); the NEST itself
    // (pool / light / fog / save letter 'K') derives from
    // CONFIG.enemy.tithecaptain.lair via lairNest - the two agree).
    lairs: [
      { type: 'tithecaptain', x: 0, z: -872 }
    ],
    // The debt-glow pool at the gate (the H4 scar-pool pattern; the ONE
    // crimson family's engine half - colors chosen inside the 0xd85050
    // crimson family; textureSeed FRESH (448271910 = groundSeed + 1;
    // distinct from every landed seed incl. J's pool 20261107).
    rotLair: {
      pool: { radius: 8, segments: 40, rings: 5, lift: 0.08,
        color: 0x1a0f12, color2: 0x2a1116, speck: 0x5a2028, textureSeed: 448271910,
        edgeFeather: 0.22 },
      light: { height: 1.3, intensity: 1.6, color: 0xd85050 },
      fog: { cards: 8, radiusMin: 2.0, radiusMax: 7.0, heightMin: 0.4, heightMax: 1.4,
        width: 3.2, height: 1.3, opacity: 0.15, color: 0x8a4550, driftSpeed: 0.12,
        showWithinM: 70 },
      cullM: 170
    },
    // CC-H5b Traps as Authored Hazards (io/specs/cc-h5b-hazards-spec.md B1):
    // the vault's OWN flame vents, hand-placed as a puzzle. Independent
    // per-vent phase machine idle 6.0 / warn 1.5 / blast 0.9 / linger 0.6
    // (9.0 s cycle); vents DE-SYNC phase-0 (+ 1.3 s x index, C5: reset at
    // every region build). radiusM is the LETHAL damage seat;
    // warnRadiusM / blastRadiusM are the cards' VISUAL reach; heightM floats
    // the card over the pipe. cueHex = THE ONE crimson accent
    // (matches tithecaptain.cueHot). SEAT AMENDMENT (disclosed in the build
    // note): vent 2 sat (x -6.0, z -894) in the spec B1 literal table - its
    // center stood 1.10 m from the mourningStatue (-6,-896) edge, below the
    // >= 2.0 prop-edge floor; per the spec's amendment law ("a probe failure
    // amends the seat, never the law") it moves to (-4.5,-899), which clears
    // every B1 floor (scratch/cc-h5b/probe_placement.py prints the table).
    hazards: {
      vents: [
        { x: -5.5, z: -864 },  // antechamber choke lane, left of the spawn walk-in
        { x:  6.5, z: -869 },  // central floor, between antechamber and boss seat
        { x: -4.5, z: -899 },  // boss-approach left flank (AMENDED, was -6.0,-894)
        { x:  3.0, z: -897 }   // boss-approach right flank (asymmetric: harder read)
      ],
      idleSec: 6.0,             // dormant
      warnSec: 1.5,             // telegraph (crimson card grow + light wick)
      blastSec: 0.9,            // flame card at full + light at peak
      lingerSec: 0.6,           // cooldown fade (harmless, dim)
      radiusM: 2.0,             // LETHAL radius (damage seat), centered on the pipe
      warnRadiusM: 1.1,         // visual radius the crimson card reaches at warn end
      blastRadiusM: 2.0,        // visual radius the ember card reaches at blast start
      heightM: 2.2,             // card float above ground (visual only)
      damage: 14,               // hp per blast shot, once per player per vent-cycle
      hitStop: 0.10,            // s of module-scoped hit-stop on an applied hit
      cueHex: 0xd84a4a,         // THE ONE crimson accent (matches tithecaptain cueHot)
      cardIdleHex: 0x8a2a20,    // idle ember dim red-brown (always visible vent eye)
      cardBlastHex: 0xff8a3c,   // blast flame core (still inside the crimson family)
      shakeM: 0.12,             // camera shake magnitude on a player hit (shake-channel scale)
      staggerMeters: 4.0        // player knockback distance, away from the vent center
    },
    props: [
      // -- THE VAULT GATE: mourning-statuette guards watching the dais
      //    (the J gauntlet family continues; the processional ends here)
      { asset: 'mourningStatue', x: -6, z: -888, rotY: 4.00, scale: 1.00 },
      { asset: 'mourningStatue', x:  6, z: -888, rotY: 5.28, scale: 1.00 },
      { asset: 'mourningStatue', x: -6, z: -896, rotY: 4.00, scale: 1.00 },
      { asset: 'mourningStatue', x:  6, z: -896, rotY: 5.28, scale: 1.00 },
      { asset: 'stoneSteps',     x: -2.4, z: -893, rotY: 0.60, scale: 1.10 },
      { asset: 'stoneSteps',     x:  2.4, z: -893, rotY: 5.68, scale: 1.10 },
      // -- the vault-gate colonnade: flank pair on the dais + the great root
      //    south of the seat. Root seat fix: the spec row put it at (0,-876),
      //    4.0 m north of the captain's seat - its own footprint bound the
      //    boss-seat clear circle at 2.85 m (< the 6.0 AMEND-1 law); (0,-880)
      //    restores it to 6.85 m (the pillar's own 1.15 map radius becomes the
      //    binding obstacle; the pre-audit's 7.0 m zealot reading is the
      //    no-footprint map's number - disclosed in the build note).
      { asset: 'okRuinColumn', x: -8, z: -872, rotY: 0.30, scale: 1.40 },
      { asset: 'okRuinColumn', x:  8, z: -872, rotY: 5.98, scale: 1.40 },
      { asset: 'okRuinColumn', x:  0, z: -880, rotY: 0.00, scale: 2.40 },
      // -- the ONE crimson family (lamp + caps; the pool is its engine half)
      { asset: 'lanternPost', x: -13, z: -882, rotY: 5.20, scale: 1 },
      { asset: 'blightcap',   x: -13, z: -868, rotY: 3.62, scale: 0.90 },
      { asset: 'blightcap',   x:  13, z: -868, rotY: 0.63, scale: 0.90 },
      // -- erasure scatter (J's grammar): 2 skull piles, 1 moss boulder
      { asset: 'skullPile',   x: -16, z: -896, rotY: 4.40, scale: 1.00 },
      { asset: 'skullPile',   x:   8, z: -908, rotY: 3.60, scale: 1.00 },
      { asset: 'mossBoulder', x: -14, z: -872, rotY: 2.00, scale: 2.20 },
      // -- CC-H5 VAULT RING: full 10-row closure, the J ring math on
      //    groundRadius 34: chord 21.0136 = 2*34*sin(18 deg) =>
      //    scale 11.067 = chord/1.899; centers k*36 deg on the r34 circle,
      //    clockwise from north (x = 34 sin a, z = -880 - 34 cos a),
      //    rotY = 3.14 + k*0.6283. NO omission: the ring is closed behind
      //    the plane. SPEc-FIG FIX: rows re-derived to the strict 2dp circle
      //    (sec 3's literals carried up to 2.01 m drift, rho 34.68 on row 2;
      //    valspec V-3/N-2 law: rho == 34.0 +- 0.05 on LANDED rows + chord
      //    uniformity within 0.02 - the literal table is context, not law).
      //    The walk-OUT lane (|x| <= 2.2 at the plane -848) clears the
      //    north-point row (0,-846) colliders by 2.00 - 0.45 = 1.55 m edge
      //    distance -- the governing >= 1.0 m lane clearance (the J ring's
      //    landed figure, carried by the J-mirror geometry).
      { asset: 'whWallA', x:   0.00, z: -846.00, rotY: 3.14, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:  19.98, z: -852.49, rotY: 3.77, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x:  32.34, z: -869.49, rotY: 4.40, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:  32.34, z: -890.51, rotY: 5.03, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x:  19.98, z: -907.51, rotY: 5.65, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:   0.00, z: -914.00, rotY: 6.28, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x: -19.98, z: -907.51, rotY: 6.91, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x: -32.34, z: -890.51, rotY: 7.54, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x: -32.34, z: -869.49, rotY: 8.17, scale: 11.067, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x: -19.98, z: -852.49, rotY: 8.80, scale: 11.067, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 }
    ]
  },

  // CC-H6 THE REMAINS (io/specs/cc-h6-remains-spec.md sec 2): delve strata
  // V5 off the Tithe Vaults. Key-set law: L carries NO traps block and NO
  // rotLair (doc 47 S5 "the chamber is a duel, not a gauntlet" + "the
  // chamber is clean" - traps belong to the machine Vaults V4, a debris
  // pool contradicts the clean chamber); every other K key carried with
  // new values. All tunables PROPOSED (Nicko tunes).
  regionL: {
    id: 'the_remains',
    name: 'The Remains',
    center: { x: 0, z: -1064 },   // 184 m deeper than K (0,-880): one stratum
                                  // gap; K south rim -914 vs L north rim -1034
                                  // = 120 m unrendered dark (conn[9] pattern)
    groundRadius: 30,             // PROPOSED (duel chamber: smaller than K 34)
    groundY: 0,                   // flat disc
    groundColor: 0x090b10,        // one step colder than K 0x0b0d12
    groundColor2: 0x0c0e11,
    groundSeed: 559043117,        // FRESH: differs from every landed seed
    scatter: false,               // hand rows only (D/E/F/I/J/K law)
    spawn: { x: 0, z: -1044 },    // 8 m SOUTH of the walk-back plane -1036
                                  // (conn[9] ADJ-E mirror: crossing cannot
                                  // re-trigger); landing row = spawn row
    gravityY: -22,                // every landed region's value
    fogColor: 0x090710,           // the veil fog family, one step deeper
    fogDensity: 0.17,             // d95 = 1.7306/0.17 = 10.18 m: one stratum
                                  // quieter than K (0.16 -> 10.82)
    ambientLightLevel: 0.04,      // K is 0.045; L one step deeper
    door: {
      planeZ: -1036,              // 2 m inside the north rim -1034 (mirror law:
                                  // every landed plane sits INSIDE its disc)
      doorX: 0,
      doorHalfWidth: 2.2,         // the F/J/K tomb-mouth lane
      suspendDepthM: 0, wallGapPadM: 0,
      walkFrom: 'the_remains',    // ONE-SIDED: plane crosses ONLY from L
      interact: { from: 'tithe_vaults', x: 7.5, z: -854, radius: 3.5 },
      //   ^ the K-side hook, east of K's mouth lane, INSIDE K's interior;
      //   probe: >= 4.0 m from every K collider (ring, props, enemy rows;
      //   ALSO >= 2.0 m outside the captain's lairRadius 16 circle about
      //   (0,-872): dist 19.5 m).
      land: {
        tithe_vaults:  { x: 2, z: -858, faceX: 0, faceZ: -880 },
        //   walk back INTO K beside the hook, facing the vault dais; >= 8 m
        //   south of K's plane -848, on K's home side (z <= -848). 6.8 m from
        //   the hook (J's landed mirror figure: no instant re-prompt, the
        //   E-zone is 3.5 m).
        the_remains:   { x: 0, z: -1044, faceX: 0, faceZ: -1060 }
        //   INTO L = the spawn row, facing the chancel / boss nest (16 m off:
        //   the K edge - no instant aggro on the landing fade).
      },
      fadeIn: 0.3, fadeOut: 0.5, exitFadeOut: 0.8,
      text: { prompt: 'E - Descend into the remains' }
    },
    enemies: [],                  // doc 47 S5: the chamber holds no trash pool
    lairs: [
      { type: 'lastchancel', x: 0, z: -1060 }
      //   ^ the CC-H5 note applies verbatim: the row CARRIES x/z and the NEST
      //   derives from CONFIG.enemy.lastchancel.lair via lairNest - two agree.
      //   K-MIRROR SPACING: the seat sits 16.0 m south of the landing row
      //   (0,-1044), matching K's landed edge (landing 16 == aggro 16: no
      //   instant aggro on arrival).
    ],
    props: [
      // -- CC-H6 VAULT RING: K's 10-row closure carried down on groundRadius
      //    30: chord 18.5410 = 2*30*sin(18 deg) => scale 9.7630 = chord/1.899;
      //    centers k*36 deg on the r30 circle, clockwise from north
      //    (x_k = 30 sin((180-36k) deg), z_k = -1064 - 30 cos((180-36k) deg)),
      //    rotY = 3.14 + k*0.6283, whWallA/B alternating starting A,
      //    sy 11.69 (A) / 11.55 (B), sz 2.40, y -0.2, wall 10.
      //    SPEC-FIG FIX (the CC-H5 precedent): rows RE-DERIVED to the strict
      //    2dp circle - rho == 30.0 +- 0.05 on all 10 LANDED rows + chord
      //    uniformity <= 0.02 (the sec-2b literal table is context, not law).
      //    NO omission (K law: the ring is closed behind the plane).
      //    The walk-OUT lane (|x| <= 2.2 at the plane -1036) clears the
      //    north-point row (0,-1034) colliders by 2.00 - 0.45 = 1.55 m edge
      //    distance - the K landed figure carried by the mirror geometry
      //    (the governing >= 1.0 m lane clearance).
      { asset: 'whWallA', x:   0.00, z: -1034.00, rotY: 3.14, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:  17.63, z: -1039.73, rotY: 3.77, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x:  28.53, z: -1054.73, rotY: 4.40, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:  28.53, z: -1073.27, rotY: 5.02, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x:  17.63, z: -1088.27, rotY: 5.65, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x:   0.00, z: -1094.00, rotY: 6.28, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x: -17.63, z: -1088.27, rotY: 6.91, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x: -28.53, z: -1073.27, rotY: 7.54, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallA', x: -28.53, z: -1054.73, rotY: 8.17, scale: 9.763, sy: 11.69, sz: 2.40, y: -0.2, wall: 10 },
      { asset: 'whWallB', x: -17.63, z: -1039.73, rotY: 8.79, scale: 9.763, sy: 11.55, sz: 2.40, y: -0.2, wall: 10 },
      // -- THE REMAINS: the working's shell at the chamber's south center
      { asset: 'stoneSarcophagus', x: 0, z: -1086, rotY: 0.00, scale: 1.60 },
      // -- melted colonnade flank pair (K dais grammar carried down one stratum)
      { asset: 'okRuinColumn', x: -7, z: -1064, rotY: 0.30, scale: 1.40 },
      { asset: 'okRuinColumn', x:  7, z: -1064, rotY: 5.98, scale: 1.40 },
      // -- hooded sentinels flanking the chancel approach (H3/H5 processional)
      { asset: 'mourningStatue', x: -4, z: -1052, rotY: 4.00, scale: 0.60 },
      { asset: 'mourningStatue', x:  4, z: -1052, rotY: 5.28, scale: 0.60 },
      // -- approach steps
      { asset: 'stoneSteps', x: -2.4, z: -1068, rotY: 0.60, scale: 1.10 },
      { asset: 'stoneSteps', x:  2.4, z: -1068, rotY: 5.68, scale: 1.10 },
      // -- erasure scatter (J/K grammar)
      { asset: 'skullPile',   x: -14, z: -1076, rotY: 4.40, scale: 1.00 },
      //   SEAT AMENDMENT: the sec-2b literal (12,-1084) sat 0.11 m from the
      //   RE-DERIVED k=4 ring band segment (0.44 from its engine collider
      //   seat); per the amendment law (CC-H5b precedent: a probe failure
      //   amends the seat, never the law) it moves to (12,-1090), raw >= 4.73.
      //   The WEST+EAST blightcap literals (13,-1046) fail the same law
      //   (2.30/2.79 m inside the k=9/k=1 band dips) and amend to (+-16,
      //   -1047) - see their rows.
      { asset: 'skullPile',   x:  12, z: -1090, rotY: 3.60, scale: 1.00 },
      { asset: 'mossBoulder', x: -13, z: -1052, rotY: 2.00, scale: 2.20 },
      // -- the ONE crimson family (lamp + caps; K's family continued)
      { asset: 'lanternPost', x: -13, z: -1058, rotY: 5.20, scale: 1 },
      { asset: 'blightcap', x: -16, z: -1047, rotY: 3.62, scale: 0.90 },  // SEAT AMENDMENT: the (-13,-1046) mirror pair sat 2.30/2.79 m inside the k=9/k=1 band dips (band minimum reaches radius 21.4 from center) and every nearer seat is blocked by the mossBoulder's mutual 2.0; (+-16,-1047) clears every band segment >= 4.92 raw (law floor 4.0) and every mutual >= 2.98
      { asset: 'blightcap', x:  16, z: -1047, rotY: 0.63, scale: 0.90 }
    ]
  },

  // Round E (io/missions/2026-10-05-cc-roundE-veg.md): seeded vegetation
  // scatter, built by region-manager whScatterPlan. PARAMETERS ONLY - no
  // placement tables: every position is a pure function of this block, the
  // region's CONFIG props/spawn/enemies/nodes, the dirt-path sway and the
  // measured asset footprints. Extra trees are normal props WITH trunk
  // colliders; bushes + grass have NO collider and render as one
  // InstancedMesh per asset per region (matrices written once at build).
  scatter: {
    enabled: true,
    seed: 20261005,
    clear: {                          // rejection radii (m) shared by the layers
      spawnM: 5,                      // region player spawn
      pathM: 6,                       // dirt-path centerline (trees + free bushes)
      gateM: 8,                       // chokepoint gate point (+ the collider corridor)
      enemyM: 4,                      // CONFIG enemy spawns (trees + free bushes)
      nodeM: 2.5,                     // gather nodes (trees + free bushes)
      edgeM: 2                        // inset from the playable rim / boundary plane
    },
    // keep-out ellipses for trees + free bushes (grass/rings still allowed):
    // region A cemetery yard + its tree ring = the gather-node graveyard zone
    // (scratch/gen_gather_nodes.py in_graveyard) - open combat ground stays open.
    keepOut: [
      { regionId: 'hold_outskirts', x: 0, z: 10, rx: 36, rz: 33 },
      // CC-B1 (2026-11-07): ruined-chapel nave at region-B centre (footprint
      // x -16..17, z -66..-50) — Round-E scatter trees/bushes never spawn
      // inside. Grass stays (moss floor inside the ruin reads canon). WAKE-34
      // IO amendment: rx 21 rz 12.5 — the re-seated west wall (x -18) and the
      // K2 free-standing buttress (-11.8,-52) sit inside, whole ruin covered.
      { regionId: 'darkwood_edge', x: 0, z: -58, rx: 21, rz: 12.5 }
    ],
    treesExtra: {
      minSpacingM: 7,                 // to every tree (CONFIG + scatter)
      propClearM: 4,                  // beyond any CONFIG prop's collider radius
      candidates: 32,                 // best-candidate samples per tree: emptiest spot wins
      targetCount: { hold_outskirts: 14, darkwood_edge: 10 },
      // [asset, weight, heightMinM, heightMaxM]; scale = height / measured height
      assets: [
        ['youngBirch', 3, 8.5, 11.5],
        ['youngDeadTree', 2, 6.0, 9.0],
        ['yewTree', 2, 15.5, 18.5],
        ['witchwoodTree', 1, 15.5, 18.5],
        // Round I: reach-tree variants at witchwood weight (io/roundI-provenance.md)
        ['reachTreeA', 1, 15.5, 18.5],
        ['reachTreeB', 1, 15.5, 18.5],
        ['reachTreeC', 1, 15.5, 18.5],
        ['deadTree', 1, 13.5, 16.5]
      ]
    },
    bushes: {
      // [asset, weight, heightMinM, heightMaxM]
      // Round H: free bushes = the Meshy bramble (rollback rows:
      // [['bushA', 3, 0.7, 1.0], ['bushB', 2, 0.9, 1.3]])
      assets: [['bramble', 1, 1.4, 2.0]],
      selfRadiusFrac: 0.5,            // own radius = half-width * this (overlap is fine)
      // every tree gets [min,max] bushes at radiusFrac x its TRUNK collider radius
      ringHosts: ['yewTree', 'livingOak', 'witchwoodTree', 'deadTree', 'youngAsh',
        'youngBirch', 'youngDeadTree', 'reachTreeA', 'reachTreeB', 'reachTreeC'],
      // ring bushes draw from their own rows (Round G: Nicko's snare bush;
      // rollback = the bushA/bushB rows noted on B.assets above)
      atTreeRing: { count: [2, 4], radiusFrac: [1.1, 1.6],
        assets: [['whBushSnare', 1, 1.0, 1.4]] },
      freeBushes: 20                  // per region, open ground
    },
    grass: {
      asset: 'grassTuft',
      count: 220,                     // per region
      height: [0.35, 0.6],            // m
      pathPadM: 0.4                   // beyond the path half-width
    }
  },

  // CC-C4a THE KING'S ROADS (R-62.7): per-region road rows (region-manager
  // whRoadsFor / whRoadLine / buildRoad). A's road stays CONFIG.world.dirtPath
  // (NOT migrated - the smaller diff: whRoadsFor lists it first for A and every
  // reader measures it with whDistToPath exactly as before). Rows here: a
  // waypoint centerline (points, Catmull-Rom, 2 m resample) or a closed ring,
  // + a lateral sine sway ramped to 0 over swayRampM at both ends; the ribbon
  // seats on the heightfield (+ lift; ring/branches lifted apart so the
  // overlapping junction decals never z-fight). Keep-outs: the scatter's
  // pathM band (trees/free bushes) and halfWidth + grass.pathPadM (grass,
  // rings, colonies); camp.js refuses a deploy inside halfWidth + pathBand.
  // UNLIT LAW: no light rows exist for roads; the one fork marker is a stone.
  // Waypoints were nudged off the brief's proposal onto gentler ground (max
  // 10 m grade: spine 8.9 deg, ring 1.7, N 4.2, E 4.7, W 10.4) and >= 8 m
  // from every tree centerline (tightest: W road vs witchwood (-55, -348.3)
  // 8.2 m). The ring sits at r 34, not ~16: r 16 IS the CC-C3 boulder ring
  // and the gate pair spans r 20-30.5, so the ring runs outside the assembly
  // and the spine continues straight through the gate pair (stoneApproach).
  // CC-C4b NOTCH MOUTHS = the last point of north/east/west (0, -596),
  // (240, -366), (-240, -366): the roads stop there, inside the playable
  // rim; NO blocker/toast in C4a (the rim clamp holds the player). C4b
  // carves the rim notches + adds the soft blockers. Note for C4b: yewTree
  // (272.4, -369) stands on the east road's notch line. All PROPOSED, Nicko tunes.
  roads: [
    { id: 'kingsRoad', regionId: 'forest_of_the_old_king',   // glade -> the ring's south point
      points: [[0, -88], [-2.5, -104], [4, -138], [2, -168], [4, -215], [-3, -255],
        [0, -300], [0, -332]],
      halfWidth: 2.2, swayAmp: 7, swayPeriod: 90, swayRampM: 24,
      lift: 0.10, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'stoneApproach', regionId: 'forest_of_the_old_king', // straight through the gate pair
      points: [[0, -332], [0, -352]],
      halfWidth: 2.2, swayAmp: 0,
      lift: 0.10, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'stoneRing', regionId: 'forest_of_the_old_king',     // the crossroads around the Stone
      ring: { x: 0, z: -366, r: 34 },
      halfWidth: 2.2, swayAmp: 0,
      lift: 0.16, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'northRoad', regionId: 'forest_of_the_old_king',     // C4b notch mouth (0, -596)
      points: [[0, -400], [-3, -420], [-12, -460], [5, -500], [-5, -540], [0, -596]],
      halfWidth: 2.2, swayAmp: 6, swayPeriod: 90, swayRampM: 24,
      lift: 0.13, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'eastRoad', regionId: 'forest_of_the_old_king',      // C4b notch mouth (240, -366)
      points: [[34, -366], [62, -356], [100, -370], [150, -368], [200, -368], [240, -366]],
      halfWidth: 2.2, swayAmp: 6, swayPeriod: 90, swayRampM: 24,
      lift: 0.13, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'westRoad', regionId: 'forest_of_the_old_king',      // C4b notch mouth (-240, -366)
      points: [[-34, -366], [-66, -362], [-100, -370], [-150, -357], [-200, -370], [-240, -366]],
      halfWidth: 2.2, swayAmp: 6, swayPeriod: 90, swayRampM: 24,
      lift: 0.13, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    // CC-C4b NOTCH BEDS: each branch road continues 30 m past its mouth down
    // the notch axis (straight, no sway), past the soft blocker's rim line
    // into fog: the ground there is C4's faded bed (wh-ground rim fade
    // 240..280), so the bed descends toward the skirt. Separate rows so the
    // branch rows above stay byte-identical; lift 0.14 (between branch 0.13
    // and ring 0.16) so the shared mouth edge never z-fights.
    { id: 'northNotch', regionId: 'forest_of_the_old_king',
      points: [[0, -596], [0, -626]],
      halfWidth: 2.2, swayAmp: 0,
      lift: 0.14, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'eastNotch', regionId: 'forest_of_the_old_king',
      points: [[240, -366], [270, -366]],
      halfWidth: 2.2, swayAmp: 0,
      lift: 0.14, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 },
    { id: 'westNotch', regionId: 'forest_of_the_old_king',
      points: [[-240, -366], [-270, -366]],
      halfWidth: 2.2, swayAmp: 0,
      lift: 0.14, tileLengthMeters: 3.0, repeatAcrossWidth: 1, textureSeed: 20261008 }
    // CC-C15 (Nicko 2026-10-20): the temporary denTrail + denTrailNotch rows
    // are REMOVED - the den is relocated to the SW rim mountain foot and the
    // Old King's Roads are once again the only roads (CC-C4a geometry intact).
  ],

  // CC-AE1 (io/specs/cc-ae1-night-raids-spec.md): night raid director over
  // the Old King's Roads. Values PROPOSED, Nicko tunes. Doc 34 §6 night road
  // row = the party; doc 41 R3 = 1-2 concurrent per region, V1 = 2 max with
  // 1 alive at a time. All thresholds are consumed by js/ambush.js only.
  raid: {
    regionId: 'forest_of_the_old_king',
    warnSec: 2.0,                 // doc 34: cue fires 2.00s before spawn resolves
    warnLine: 'Something stalks the road behind you.',
    party: { banditCount: 2, wolfCount: 1 },   // doc 34 night road row (low end)
    spawnBandM: [14, 17.5],       // lateral off road centerline (18m radii law)
    roadSeekRadiusM: 25,          // rear-anchor -> nearest road sample max distance
    rearSpreadDeg: 60,            // rear-arc bearing jitter (yaw + PI +- this)
    seatSlideM: 6,                // per-retry slide along the road when a seat fails
    seatRetries: 3,
    seatMaxSlopeTan: 0.45,        // seat rejection slope (WH_GROUND.slopeTan)
    seatMinPropM: 3.0,            // seat rejection: CONFIG prop rows clearance
    nearFireExclusionM: 50,       // one number everywhere: player-check gate AND seat gate (A-1 evidence)
    notchMouthExclusionM: 26,     // A-1: no seats within this of a branch road's terminal point IN ITS NOTCH ARC (north (0,-596) / east (240,-366) / west (-240,-366)); kingsRoad exempt
    seatMinRoadRenderedM: 14,     // AE1-A: rendered-road distance floor (SWAYED geometry, window.WH_RegionGeom.distToRoad - the road the player sees); polyline fallback only when WH_RegionGeom is absent
    minPlayerDistM: 14,           // AE1-A: seat-to-PLAYER straight-line floor (pop-in guard; worst poly-band case measured 8.96 m with player on a sway bulge)
    stoneRingExclusionR: 40,      // seat rejection radius around the Stone (0, -366)
    checkSec: 20,                 // trigger check cadence while eligible
    triggerChance: 0.25,          // per check roll (debugForce bypasses)
    partiesPerNightMax: 2,        // doc 41 R3: 1-2 concurrent per region; V1 = 2 max, 1 alive at a time
    cooldownSec: 180,             // after a raid ends (wipe or leash-out)
    debugForce: false,            // Nicko dev knob (dayNight.debugTimeScale pattern)
    debugMute: false              // dev knob: silence the state toasts below
  },

  // CC-H5b Traps as Authored Hazards (io/specs/cc-h5b-hazards-spec.md B2):
  // global primitive block, sibling of CFG.raid. Values consumed by
  // js/hazards.js only. hitCooldownSec is the per-player GLOBAL re-hit gate
  // (across vents - one vent cannot chain into the next inside the gate);
  // toastText = the one-time first-hit cue (inventoryUI.toast, session-scoped).
  hazards: {
    enabled: true,
    regionIds: ['tithe_vaults'],  // gate: only these regions run vents
    hitCooldownSec: 0.5,          // per-player global re-hit gate (all vents)
    toastText: 'The vault flares!',  // one-time first-hit cue (inventoryUI toast)
    firstHitOnly: true
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

  // Round F (io/missions/2026-10-05-cc-roundF-wall.md): vine-on-stone wall
  // ring around the shared disc + a wall along the boundary plane, with a
  // gate arch over the chokepoint. PARAMETERS ONLY: region-manager
  // whWallPlan derives every segment from this block + measured footprints
  // (seeded mulberry32; mirror: scratch/wall_mirror.py). World-level: built
  // once at boot, never disposed by region swaps.
  boundaryWall: {
    enabled: true,
    seed: 20261006,
    radius: 87.5,                     // ring centerline (playable rim 88.5)
    minRadius: 86.5,                  // radial jitter never pulls a segment inside this
    segmentLengthUnits: 4.0,          // world meters per segment INSTANCE (X scale)
    overlapM: 0.2,                    // segment count uses length - overlap so ends butt
    heightM: 7.2,                     // world height (Y scale only; Round G 3x of 2.4 so the camera can't see over)
    depthScale: 0.7,                  // Z scale = X scale * this (~0.7 m thick)
    sinkM: 0.05,                      // bury the base slightly into the ground
    assets: ['whWallA', 'whWallB'],   // MANIFEST keys, alternated
    jitter: { radial: 0.7, rotJitterDeg: 4 },  // radial: circular 1-2-1 smoothed
    chordZ: -25,                      // boundary-plane wall line
    chordFromX: 4.0,                  // from the corridor edge outward...
    chordToRim: true,                 // ...to the ring intercept (x ~ +-83.85)
    collider: { r: 0.45, perSegment: 3 },  // circles along each segment's axis
    // exclusion sweep vs CONFIG props (both regions): collider r + clearM;
    // ring segments nudge inward in nudgeStepM steps up to nudgeMaxM, then
    // drop (chord segments drop). maxDrops is the expected ceiling (logged).
    exclusion: { clearM: 0.5, nudgeStepM: 0.25, nudgeMaxM: 1.0, maxDrops: 2 },
    arch: {
      asset: 'b3Gate', x: 0, z: -25, rotY: 0,
      fitOpening: 5.2,                // scale so the clear opening is >= this (m)
      // measured from the GLB (scratch/gate_opening.py on b3-gate-open):
      // narrowest clear gap in the walkable band / ext X, its center / ext X,
      // opening apex above the floor / ext Y, ext Z / ext X.
      openingFrac: 0.3428, openingCenterFrac: 0.0059, apexFrac: 0.6454,
      depthFrac: 0.6338,
      depthScale: 0.45,               // Z squash: 9.6 m deep at uniform scale -> ~4.3 m
      // pillar blocks = opening edge .. outer half-width, full depth; ringed by
      // leg circles (r, spacing) + a corner plug at each doorway mouth corner,
      // set just outside the opening so the lane == the arch opening.
      legs: { r: 0.6, spacingM: 1.0 },
      plugCorners: true, plugR: 0.5
    },
    // hung height = heightM * scale (0.9 m: the measured gate is ~1.9x the
    // briefed ~8 m arch, so the briefed 0.5 m read as a speck at 6.8 m)
    lantern: { asset: 'whLanternHang', heightM: 0.75, scale: 1.2,
               topBelowApexM: -0.05 },  // hook top 5 cm INTO the apex stone (attached)
    // CC-B2 (doc 61 P1-3, io/specs/cc-b2-gate-forecourt-spec.md): gate
    // forecourt dressing - iron-fence runs tying the arch into the chord wall
    // line + paired lantern posts flanking the approach. World-level,
    // additive-only (region-manager whWallPlan section 6, stream 'wall:forecourt').
    // fromX is NOT taken here: whWallPlan computes it at plan time as
    // max(chordFromX, arch.halfWidth + archPadM + clearM) so the fence always
    // starts OUTSIDE the arch pillar face, never inside it.
    forecourt: {
      fence: {
        asset: 'ironFenceSection',      // church-kit; C13b scale law 1.35
        cornerAsset: 'ironFenceCorner', // terminus piece on each side
        scale: 1.35,
        z: -22.9,                       // forecourt line (4.1 m in front of the chord)
        fromX: 0,                       // sentinel: plan-time max(chordFromX, hw+1.9)
        toX: 20.0,                      // outward end
        overlapM: 0.05                  // count uses span/(len - overlap) so ends butt
      },
      posts: [
        { asset: 'lanternPost', x: -6.2, z: -20.5, rotY: 0, scale: 2.535 },  // v3 scale law (roundL)
        { asset: 'lanternPost', x:  6.2, z: -20.5, rotY: 0, scale: 2.535 }
      ],
      archPadM: 1.2,                    // pillar-face clearance: fromX >= halfWidth + this
      clearM: 0.7                       // ...plus this (spec: max(chordFromX, hw+1.2+0.7))
    }
  },

  preWarm: {
    distance: 30,                     // build neighbor when player is this close to boundary
    hysteresis: 20                    // dispose pre-warm when player is this much farther away
  },

  // P1-3 gate-cross region crossfade (io/specs/P1-3-crossfade-ground-split-spec.md
  // sec "Crossfade"; consumed only by game.js regionFadeTick): a walked A/B
  // gate crossing eases the fog color/density + hemi fill intensity from the
  // crossed-from region's live values to the new region's rows over
  // durationSec instead of applyRegionLighting's instant write. Den door
  // (conn.door), forceCross and switchTo crosses keep the instant path.
  // All magic numbers flow from this row.
  sceneFade: {
    durationSec: 1.5
  },

  // P1-7 (doc 61): layered atmosphere. The chunk installer bakes height-fog
  // constants before the first compile; mist cards supersede the old plane.
  atmos: {
    enabled: true,
    heightFog: {
      enabled: true,
      yBase: 0.0,
      yScale: 6.0,
      minFrac: 0.35,
      moonTint: 0.45,
      moonColorHex: 0x778da9
    },
    mistCards: {
      enabled: true,
      regionId: 'darkwood_edge',
      count: 9,
      yMin: 0.6, yMax: 2.6,
      sizeMin: 7.0, sizeMax: 14.0,
      opacityMin: 0.05, opacityMax: 0.10,
      colorHex: 0xc5c9cc,
      radiusFrac: 0.75,
      seed: 1234
    },
    recede: { enabled: true, mult: 0.55, lerpRate: 3.0 }
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
    rollIFrameWindow: 0.433,          // EPR1: s of i-frames (ER medium roll = 13 frames @ 30 Hz)
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
    // R-64.2 (Nicko 10-09): 8 -> 2.0. Regen is Wisdom's domain:
    // 2.0 base * (1 + 0.05 * wisdomPoints) * other mults (blocking 0.5)
    // 0 wis = 2.0/s; 10 wis = 3.0/s; 10 wis blocking = 1.5/s
    focusRegenPerSec: 2.0,            // focus regen per second after delay
    focusRegenDelay: 0.5,             // seconds after spend before regen resumes
    castFocusTaxMult: 1.25,           // spell focus tax while weapon in main hand
    // P1-4a (io/specs/p1-4a-camera-pullin-spec.md 6): camera obstruction
    // pull-in — player.js updateCamera samples the target->want segment
    // against the active region's propColliders circles (exempt never
    // occludes, the C14 trunk law sets an occluder's top) and pulls the
    // camera IN to the cleared distance. enabled: false = the pre-change
    // orbit math exactly (single early-out, no allocation).
    cameraPull: { enabled: true, camRadiusM: 0.45, skinM: 0.30, samples: 6,
      trunkTopFrac: 0.45, minFloor: 0.0 }
  },

  // v8: pointer-lock mouse bind camera (io/specs/mouse-bind-cam-spec.md 4)
  mouse: {
    pointerLockSensMult: 0.85,      // bound-mouse multiply on mouseSensDegPerPx
    autoBindOnCanvasClick: true,    // LMB on canvas while unbound: attack + rebind
    // 10-05 inventory Order A reconcile: the inventory screen (any overlay
    // that calls player.setInputSuspended) owns the cursor while open
    unbindOnUiOpen: true,           // opening the screen unbinds a bound mouse
    rebindOnUiClose: false          // closing the screen rebinds an unbound mouse
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

  // AB1 (2026-10-07) player-mappable action bar: keys 1-5 / tap select the
  // slot's binding. kind 'spell' = a learned spell (belt list above) bound
  // to the main hand (Shift = off hand); kind 'item' = a gear item equipped
  // into its native hand through the Q-swap window. defaults = boot map,
  // the player rebinds any slot (right-click / long-press -> picker); the
  // map persists in localStorage under lsKey (invalid entries fall back to
  // that slot's default). Bindable items = gear with a hand mount (no
  // consumables / food / ingredients / valuables).
  actionbar: {
    slots: 5,
    defaults: [ { kind: 'spell', id: 'firebolt' }, { kind: 'spell', id: 'radiance' },
                { kind: 'item', id: 'roundShield' }, { kind: 'item', id: 'magicGlove' },
                { kind: 'item', id: 'torch' } ],
    lsKey: 'wh-actionbar-v1',
    longPressMs: 400,                 // touch / mouse hold on a slot = rebind picker
    pickerExclude: ['bandage']        // consumables stay on R/T; gear-only picker
  },

  // C4 (2026-10-06) save profile (js/save.js WH_SAVE): ONE rolling profile
  // in localStorage under lsKey, every save overwrites. Written by the camp
  // menu Save / Save and Heal and on page quit (once a cycle has begun);
  // death writes nothing. Schema v1 = { v, ts, player, inventory, cooking,
  // camp, world } - fresh world spawns (trees / nodes / enemies) are never
  // saved. version guards future migrations (a mismatched v loads as none).
  // L1 (2026-10-07): + optional leveling block (WH_LEVEL.capture) - an
  // ADDITIVE field, so version stays 1 on purpose: pre-L1 profiles still
  // load (no block = fresh level 1) and nothing old is invalidated.
  // R-64.5 (2026-10-09): + optional class block { id } (the NEW GAME
  // class pick) - additive too, version stays 1; no block = no class.
  save: {
    lsKey: 'wh-save-v1',
    version: 1,
    text: {
      saved: 'Saved.',
      noSave: 'No save yet',
      load: 'LOAD',                   // camp menu row (dim until a save exists)
      continue: 'CONTINUE',           // boot overlay rows (only when a save exists)
      newGame: 'NEW GAME'
    }
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

  // CC-EC1: enemy spell registry (sibling of spell.*, NOT inside it - the
  // player spell registry stays untouched; WH_SPELLS.spawnEnemyBolt reads
  // this). ONE caster bolt for now (doc 34 sec 5 analog). kind 'projectile'
  // is the spells.js projectile family (spawnEnemyBolt rejects other kinds).
  enemySpell: {
    covenBolt: {
      kind: 'projectile',
      focusCost: 0,                   // enemy: no focus pool
      damage: 14,
      speed: 16,
      hitRadius: 0.8,                 // circle test vs player (+ CONFIG.player.radius LIVE value)
      maxRange: 22,                   // lifetime = maxRange / speed; == coven castRange
      castWindup: 0.55,               // == coven attackPhase.windup (the glow grows over it)
      castCooldown: 2.6,              // seconds between bolt spawns (gates the re-cast)
      schoolColor: 0x4fd8c8,          // art law: the ONE cyan accent (char-09 anchor; no red/orange)
      name: 'Coven Bolt', glyph: 'CB',
      // ED-3 (recorded deviation): these rows LAND here but stay INERT this
      // round - the coven bolt carries NO pooled light (light.js and the
      // player-firebolt light pool untouched). Kept so the numbers ride the
      // spec verbatim for a later light pass.
      light: { color: 0x4fd8c8, intensity: 6.0, distance: 9, decay: 2, flickerPct: 8 },
      projectileLight: { color: 0x4fd8c8, intensity: 2.0, distance: 6, decay: 2, flickerPct: 10 }
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
      },
      ai1: {                           // AI1 2026-10-07: lock-on / strafe / decision loop
        decisionSeconds: 0.4,          // PROPOSED, Nicko tunes - decision loop cadence while in the strafe band
        alwaysKnowsRadius: 4.0,        // PROPOSED, Nicko tunes - engages even in darkness inside this range
        strafeBandInner: 3.4,          // PROPOSED, Nicko tunes - inside this -> give ground (back out)
        strafeBandOuter: 7.0,          // PROPOSED, Nicko tunes - outside this -> close (existing chase path)
        strafeSpeedMult: 0.75,         // PROPOSED, Nicko tunes - x moveSpeed while circling
        strafeDirFlipSeconds: 1.8,     // PROPOSED, Nicko tunes - orbit direction flips at most this often
        attackRadius: 2.4,             // PROPOSED, Nicko tunes - == attackRange on purpose; do not drift
        attackBias: 0.55,              // PROPOSED, Nicko tunes - per decision tick, chance to press the attack
        guardChance: 0.45,             // PROPOSED, Nicko tunes - per decision tick while the player attacks it
        guardRespondRadius: 6.0,       // PROPOSED, Nicko tunes - must be this close to react at all
        guardSecondsMax: 1.6,          // PROPOSED, Nicko tunes - guard posture hard cap
        guardArcDeg: 50,               // PROPOSED, Nicko tunes - guard front arc HALF-angle (== hitArcDeg)
        guardDamageMult: 0.5           // PROPOSED, Nicko tunes - locked by Nicko Q1: real mitigation, melee
                                       // AND firebolt (fromDir arc in takeDamage)
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
      },
      ai1: { guardMode: 0 }            // PROPOSED, Nicko tunes - 0 = zombie stays a zombie (every AI1 branch skips)
    },
    // CC-C5 WOLVES OF THE OLD KING (doc 62 sec 5.1, io/missions/2026-10-08-cc-c5-wolf-packs.md).
    // Pursuit predator: fastest chaser, light stagger, AI1 hunt shapes reused
    // (strafe band = the pack orbit, decision loop = the relay lunge). The
    // attack is the WH_Wolf_Attack1 lunge bite (0.7 s): windup = the rear
    // shift, active = the snap (anim.js wolf attackSegs). All PROPOSED, Nicko tunes.
    wolf: {
      hpMax: 38.0,
      moveSpeed: 4.6,
      chaseSpeed: 7.5,                // fastest enemy (pursuit predator)
      attackDamage: 9.0,
      attackRange: 2.1,
      attackCooldown: 1.2,
      sightRadius: 15.0,
      leashRadius: 40.0,              // pack members: from the hunt anchor on the loop
      staggerTime: 0.25,              // light
      radius: 0.6,
      aggroPingInterval: 0.2,
      attackPhase: {
        windup: 0.35,                  // rear shift (clip 0..0.24 s)
        active: 0.10,                  // the snap (clip 0.24..0.39 s)
        recover: 0.45,
        hitArcDeg: 45,
        trackDegPerSec: 220
      },
      ai1: {
        decisionSeconds: 0.35,
        alwaysKnowsRadius: 4.0,
        strafeBandInner: 2.6,
        strafeBandOuter: 6.0,
        strafeSpeedMult: 0.8,
        strafeDirFlipSeconds: 1.4,
        attackRadius: 2.1,             // == attackRange
        attackBias: 0.7,
        guardChance: 0.2,
        guardRespondRadius: 5.0,
        guardSecondsMax: 0.8,
        guardArcDeg: 45,
        guardDamageMult: 0.5
      },
      // NIGHT BOLDNESS: sightRadius x this while game.dayNight.phase reads
      // 'night' (dawn / day / dusk = x 1). The landed clock only, no state.
      nightBoldnessMult: 1.5,
      // body (region-manager buildRegion): standing height in m (the measured
      // GLB 1.19 raw -> ~0.80 scale: ~1.6 m nose-to-tail). CC-C10 (Nicko
      // ruling 2026-10-20): the shipped rig's nose points model +Z (bone
      // head z +0.65, visible mesh ear/skull cluster z +0.68) - the C5
      // "-Z nose" read was wrong, so the old bodyYawDeg: 180 pin (which
      // DOUBLED the correction and made wolves lead with their rear) is
      // REMOVED; no override row = enemies face local +Z like everything else.
      bodyHeight: 0.95,
      // PACK MACHINERY (enemy.js WH_Enemy.buildPacks / updatePacks). Pack
      // state is DERIVED at buildRegion from the alive members (never saved).
      pack: {
        leashFromCentroid: 26,         // a patrol member farther than this from the alive centroid regroups (Run)...
        regroupRadius: 12,             // ...until back within this; no aggro while regrouping (solo-pull refusal)
        packAggroSpread: 40,           // BINDING pack-pulls-pack: one member engages -> every alive member within this joins
        membersInFlight: 2,            // relay lunge: at most this many in windup / snap at once; the rest orbit
        slotSpacingM: 6,               // patrol slots trail the lead by rank x this along the loop (= wolfPacks spawnSpread)
        slotLateralM: 2,               // odd ranks step this far right, even ranks left (rank 0 on the line)
        patrolPace: 0.85,              // the lead slot advances at moveSpeed x this (members catch up at moveSpeed)
        slotHoldM: 6,                  // the lead slot waits while any alive member trails its slot by more
        slotGain: 1.5                  // follow speed = min(moveSpeed, slot distance x this) (no stop-go)
      }
    },
    // CC-EC1 COVEN ACOLYTE (doc 34 enemy caster + magicDefense hook activation;
    // io/specs/cc-ec1-coven-acolyte-spec.md). PALETTE LAW (art anchor
    // art-direction/concepts/char-09-coven-wizard.png): charcoal/deep-teal
    // robes, ONE cyan accent per frame (0x4fd8c8 family), NO red/orange on
    // the acolyte or its bolt. HOOK LAW: the coven bolt's magicDefense is
    // applied exactly ONCE at the game.js enemy-bolt call site (player.js's
    // resolveIncomingHit untouched). Ranged caster: the FSM 'attack'
    // state is the CAST CYCLE (enemy.js coven branch), not melee - the melee
    // numbers below are wired to zero (attackDamage 0 / attackRange 0 /
    // attackCooldown 0) so no melee harm ever lands. movementSpeed < bandit:
    // it drifts, it casts, it backs away - it does not brawl. All PROPOSED,
    // Nicko tunes.
    coven: {
      hpMax: 60.0,
      moveSpeed: 3.4,
      chaseSpeed: 4.6,                // slower than the bandit's 5.0 press
      attackDamage: 0.0,              // melee disabled in v1: harm is the bolt only
      attackRange: 0,                 // no melee reach at all
      attackCooldown: 0,              // cast cadence owns re-cast (covenBolt.castCooldown)
      sightRadius: 20.0,
      leashRadius: 40.0,
      staggerTime: 0.45,              // staggers like bandits; a stagger cancels an in-flight cast
      radius: 0.7,
      aggroPingInterval: 0.2,
      attackPhase: {                  // the cast cycle clock (enemy.js coven branch)
        windup: 0.55,                 // == enemySpell.covenBolt.castWindup: the cyan glow grows...
        active: 0.12,                 // ...the bolt spawns at THIS entry (windup expiry), no melee harm
        recover: 0.85,                // post-spawn hold, then the attack-hold re-cast gate
        hitArcDeg: 50,                // unused by the cast branch (no melee hit check) - kept for shape parity
        trackDegPerSec: 180
      },
      castRange: 22.0                 // = enemySpell.covenBolt.maxRange: enter/hold the cast inside this
    },
    // CC-C7 ROT MOTHER + ROT SPAWN (doc 62 sec 5.2, R-62.4 repeatable nest boss;
    // io/missions/2026-10-12-cc-c7-rotmother-behavior.md sec 2). The first
    // block of each row is the BRIEF ROW VERBATIM (its keys + numbers); enemy.js
    // cfgFor maps hp / dmg / speed / aggro onto the engine keys (hpMax /
    // attackDamage / moveSpeed + chaseSpeed / sightRadius) once per type. The
    // second block = engine tunables the brief row leaves to the builder
    // (brief sec 3 AoE 3.2 m / 180-deg arc, leash, body radius, phase edges).
    // lair = region-local (x, y=z) in region lair.region (CC-C8: 'D', the den;
    // regionD.rotLair = the nest dressing; lair.flag = the save-key letter).
    // scale = the literal body scale on the raw GLB (rotmother 1.90 m tall
    // raw -> ~4.2 m; rotspawn 1.36 m raw -> ~1.1 m). Bodies are UNRIGGED: the
    // anim.js RIGID_CLIPS placeholder set plays (bandit 6-clip pattern).
    // poison = poison-lite v1 (game.js applyPlayerPoison: dps + slow for
    // duration; a re-apply REFRESHES, never stacks). slow 0.45 = -45% move.
    rotmother: {
      name: 'Rot Mother', hp: 460, dmg: 26, speed: 1.6, aggro: 9,
      // CC-C8: re-homed into the den - den-local (0, +6) in region 'D' (=
      // world (-175, -265)); flag 'C' keeps the save key rotmother_cleared_C
      // byte-equal (a pre-C8 cleared profile still loads cleared)
      lair: { x: 0, y: 6, region: 'D', flag: 'C' }, scale: 2.2,
      pattern: 'boss-slam', slamCooldown: 3.4, slamWindup: 1.15,
      poison: { dps: 3.5, duration: 4.0, slow: 0.45 },   // poison-lite v1
      rearm: { days: 3, trigger: 'proximity', radius: 14 },
      loot: [{ mat: 'rot-silk', n: [2, 4] }, { mat: 'rot-gland', n: [1, 2] }],
      minions: { asset: 'rotspawn', cap: 3, interval: 7.0, range: 6.0,
                 dieOnMasterDeath: true },
      // -- engine tunables (beyond the brief row). All PROPOSED, Nicko tunes.
      radius: 1.1,                    // body circle (separation / firebolt / sweep reach)
      leashRadius: 16,                // from the nest: kited farther -> lumbers home
      staggerTime: 0.35,              // only a parry stagger lands (superArmor below)
      superArmor: true,               // ordinary hits flinch her but never cancel a slam / stagger her (damage unchanged)
      lairRadius: 14,                 // minion spawner runs while the player is this close to the nest (= rearm.radius)
      engageRange: 2.6,               // a slam starts when the player is this close (and the cooldown is up)
      slamRadius: 3.2,                // brief sec 3: AoE radius on impact (+ player radius)
      slamArcDeg: 180,                // brief sec 3: FULL front arc (half-angle 90)
      slamActive: 0.15,               // impact window (one damage check at entry)
      slamRecover: 0.9,               // heavy recovery (the punish window)
      slamTrackDegPerSec: 50,         // windup tracking (slow: a side-step beats it)
      slamKnockbackM: 2.4,            // landed slam shoves the player this far...
      slamKnockbackSec: 0.25,         // ...over this long
      barLiftM: 2.2,                  // HP bar sits this much higher (a 4.2 m body)
      riseSec: 1.6,                   // re-arm: the 'spare' rise clip length
      poisonText: 'Rot poison - your limbs go heavy'   // toast on a fresh poison (not on a refresh)
    },
    rotspawn: {
      name: 'Rot Spawn', hp: 26, dmg: 5, speed: 2.4, aggro: 14, scale: 0.8,
      pattern: 'chase-melee', loot: [{ mat: 'rot-silk', n: [0, 1] }],
      // -- engine tunables (beyond the brief row). All PROPOSED, Nicko tunes.
      radius: 0.45,
      attackRange: 1.3,
      leashRadius: 24,                // from its spawn point
      staggerTime: 0.3,
      lunge: true,                    // brief sec 4 'tiny lunge' = the ghoul hop (CONFIG.anim.ghoulHop) at attack entry
      attackPhase: { windup: 0.35, active: 0.10, recover: 0.55, hitArcDeg: 50, trackDegPerSec: 240 },
      corpseLingerSec: 8,             // a looted / empty corpse leaves the scene after this
      maxCorpses: 4,                  // and never more than this many lie around (oldest goes first)
      riseSec: 0.8                    // spawn: the 'spare' emerge clip length
    },
    // CC-H4 (2026-11-07): THE SCAR-READER, first warden of the Veil delve
    // (doc 47 V3 THE PACT-SCAR + boss remix law: ghoul pool (45 hp / 8 dmg) x
    // boss weights, size factor 3.0, kit verbs re-costed - all PROPOSED, Nicko
    // tunes): hp 400 (~x8.9 pool), dmg 22 (~x2.75), wider slam arc (210 vs the
    // mother's 180) tracked faster (70 vs 50 deg/s), venom one step hotter
    // (dps 4.0 vs 3.5). crimson slam telegraph (concept-08: the ONE accent
    // family extends into the boss cue; a row WITHOUT these keys renders the
    // shared green pair - AMB-3 per-element fallback, rotmother path equal).
    // Minions are GHOULS (doc 47 V3 'undead drawn to the wound') - NO new
    // minion type this round; scarlings-as-new-type belongs to a later delve
    // round. Second boss-slam lair: lair = region-local (x, y=z) in region J,
    // flagPrefix = the save-key prefix (scarreader_cleared_J); regionJ.lairs
    // CARRIES x: 0, z: -709 (regionD legacy shape - see the regionJ note: the
    // Enemy constructor consumes row x/z for the BODY, lairNest consumes .lair
    // for the nest/pool/light/save letter 'J').
    scarreader: {
      name: 'The Scar-Reader', hp: 400, dmg: 22, speed: 4.8, aggro: 16,
      pattern: 'boss-slam',
      slamRadius: 7.5, slamArcDeg: 210, slamWindup: 1.05, slamActive: 0.22,
      slamRecover: 1.15, slamCooldown: 5.5, slamTrackDegPerSec: 70,
      engageRange: 7.5,
      poison: { dps: 4.0, duration: 5.0, slow: 0.5 },   // scar venom (poison-lite v1)
      poisonText: 'Scar venom burns in the wound',
      slamKnockbackM: 6.0, slamKnockbackSec: 0.32,
      cueDark: 0x1a0508, cueHot: 0xd84a4a,              // crimson slam telegraph
      scale: 3.0,                                        // doc 47 size-factor law
      lair: { x: 0, y: -9, region: 'J', flagPrefix: 'scarreader' },   // world (0,-709)
      lairRadius: 16,
      rearm: { days: 3, trigger: 'proximity', radius: 14 },
      loot: [{ mat: 'rot-silk', n: [2, 4] }, { mat: 'rot-gland', n: [1, 2] }],
      minions: { asset: 'ghoul', cap: 2, interval: 7.0, range: 5.0,
                 dieOnMasterDeath: true },               // undead drawn to the wound
      radius: 1.3,
      corpseLingerSec: 10, maxCorpses: 12,
      riseSec: 1.4
    },

    // CC-H5 zealot (Veil Faithful trash pack; bandit chassis + guard grammar):
    // doc 47 V4 "Veil Faithful zealot packs defending the devotion they
    // welcome" (doc 04 pack grammar via the bandit chassis ai1; doc 34
    // soldier guard verbs). Bandit baseline, leaner hp (fasting fanatics).
    // NO pattern key: cfgFor returns the row as-is (engine law, enemy.js
    // cfgFor) - a plain-attack trash body; ai1 rides via ai1For (enemy.js
    // reads cfg.ai1 independent of pattern). All PROPOSED, Nicko tunes.
    zealot: {
      hpMax: 60.0,
      moveSpeed: 3.6,
      chaseSpeed: 5.0,
      attackDamage: 12.0,
      attackRange: 2.4,
      attackCooldown: 1.4,
      sightRadius: 16.0,
      leashRadius: 34.0,
      staggerTime: 0.4,
      radius: 0.7,
      aggroPingInterval: 0.2,
      attackPhase: { windup: 0.7, active: 0.12, recover: 0.8,
        hitArcDeg: 50, trackDegPerSec: 180 },        // bandit's values verbatim
      ai1: { decisionSeconds: 0.4, alwaysKnowsRadius: 4.0,
        strafeBandInner: 3.4, strafeBandOuter: 7.0, strafeSpeedMult: 0.75,
        strafeDirFlipSeconds: 1.8, attackRadius: 2.4, attackBias: 0.55,
        guardChance: 0.45, guardRespondRadius: 6.0, guardSecondsMax: 1.6,
        guardArcDeg: 50, guardDamageMult: 0.5 }      // bandit's ai1 verbatim
        // == the parry/discipline grammar comes from the landed AI1 guard
        // machinery; no engine edits (enemy.js ai1For reads cfg.ai1).
    },

    // CC-H5 tithecaptain (THE TITHE CAPTAIN - the vault-gate warden): doc 47
    // V4 "a zealot-captain warden at the vault gate (faction-soldier boss:
    // doc 04/34 soldier grammar, parry-capable, smaller readable window than
    // the player's)". ENGINE LAW (enemy.js:152): the lair machinery (save
    // flag / 3-day re-arm / minions) attaches only to pattern 'boss-slam'
    // rows - the captain therefore rides a boss-slam chassis TUNED
    // SOLDIER-DISCIPLINED (the CC-H4 precedent: the Scar-Reader rode the
    // same chassis): a narrow, fast-tracked shock-slam = the disciplined
    // shield-wall read, NOT a wild AoE. Guard ai1 (parry-capable, smaller
    // window than the bandit's) rides ALONGSIDE the slam (ai1For reads
    // cfg.ai1 independent of pattern). All PROPOSED, Nicko tunes.
    tithecaptain: {
      name: 'The Tithe Captain', hp: 320, dmg: 20, speed: 4.2, aggro: 16,
      pattern: 'boss-slam',
      slamRadius: 4.2, slamArcDeg: 100, slamWindup: 0.85, slamActive: 0.18,
      slamRecover: 0.9, slamCooldown: 3.8, slamTrackDegPerSec: 110,
      engageRange: 4.2,
      cueDark: 0x1a0508, cueHot: 0xd84a4a,              // the chain's crimson cue family
      scale: 2.1,                                        // soldier boss vs the 3.0 beast tier
      lair: { x: 0, y: 8, region: 'K', flagPrefix: 'tithecaptain' },
                                                   // world (0,-872), key tithecaptain_cleared_K
      lairRadius: 16,
      rearm: { days: 3, trigger: 'proximity', radius: 14 },
      loot: [{ mat: 'stolenCoin', n: [1, 3] }],    // THE TITHE: the collection itself
      minions: { asset: 'zealot', cap: 2, interval: 7.0, range: 5.0,
                 dieOnMasterDeath: true },         // his gate guard answers him
      radius: 1.0,
      corpseLingerSec: 10, maxCorpses: 8,
      riseSec: 1.4,
      barLiftM: 2.2,
      ai1: { decisionSeconds: 0.4, alwaysKnowsRadius: 4.5,
        strafeBandInner: 3.6, strafeBandOuter: 7.5, strafeSpeedMult: 0.7,
        strafeDirFlipSeconds: 2.0, attackRadius: 4.2, attackBias: 0.5,
        guardChance: 0.6, guardRespondRadius: 6.0, guardSecondsMax: 1.8,
        guardArcDeg: 45, guardDamageMult: 0.5 }    // smaller readable window: 45 vs 50 deg
    },

    // CC-H6 THE LAST CHANCEL (io/specs/cc-h6-remains-spec.md sec 5; doc 47
    // V5 warden concept 3: Veil Faithful zealot-captain boss at the remains'
    // threshold; doc 04/34 faction-soldier grammar at boss scale,
    // parry-capable, disciplined reads). ENGINE LAW (enemy.js:152): lair
    // machinery attaches only to pattern 'boss-slam' rows - the captain's
    // precedent carries verbatim: boss-slam chassis TUNED SOLDIER-DISCIPLINED
    // (the narrow fast-tracked shock-slam = the disciplined shield-wall
    // read), guard ai1 rides ALONGSIDE. All PROPOSED (Nicko tunes).
    lastchancel: {
      name: 'The Last Chancel', hp: 400, dmg: 24, speed: 4.2, aggro: 18,
      pattern: 'boss-slam',
      slamRadius: 4.6, slamArcDeg: 100, slamWindup: 0.8, slamActive: 0.18,
      slamRecover: 0.85, slamCooldown: 3.4, slamTrackDegPerSec: 120,
      engageRange: 4.6,
      cueDark: 0x1a0508, cueHot: 0xd84a4a,              // the chain's ONE crimson family
      scale: 2.3,                                        // soldier boss one step over K's 2.1
      lair: { x: 0, y: 4, region: 'L', flagPrefix: 'lastchancel' },
                                                   // world seat (0,-1060); save key
                                                   // lastchancel_cleared_L (letter
                                                   // derivation via the lairFlag
                                                   // machinery is region-letter-generic:
                                                   // K precedent). y 4 derives the nest
                                                   // from regionL center (0,-1064): nest
                                                   // = center + y (K law: y 8 on center
                                                   // -880 gave seat -872) = (0,-1060) -
                                                   // the lairs row, this derivation, and
                                                   // the K-mirror 16.0 m landing spacing
                                                   // all agree.
      lairRadius: 16,
      rearm: { days: 3, trigger: 'proximity', radius: 14 },
      loot: [{ mat: 'stolenCoin', n: [2, 5] }],    // the LAST tithe
      // SOLO-DUEL LAW + CENSUS FINDING: lairTick reads M.interval from
      // cfg.minions UNGUARDED (enemy.js ~1285-1290) - a boss row with NO
      // minions block crashes every lairTick. Engine edit REJECTED (all-
      // config law): the row carries the cap-0 no-spawn minions row instead.
      minions: { asset: 'zealot', cap: 0, interval: 999.0, range: 5.0 },
      //   cap 0: alive(0) < cap(0) is false EVERY tick - the spawner never
      //   fires (doc 47 S5: the chamber is the duel, not a gauntlet).
      radius: 1.0,
      corpseLingerSec: 10, maxCorpses: 8,
      riseSec: 1.4,
      barLiftM: 2.4,
      ai1: { decisionSeconds: 0.35, alwaysKnowsRadius: 5.0,
        strafeBandInner: 4.0, strafeBandOuter: 8.2, strafeSpeedMult: 0.75,
        strafeDirFlipSeconds: 1.8, attackRadius: 4.6, attackBias: 0.55,
        guardChance: 0.65, guardRespondRadius: 6.0, guardSecondsMax: 1.9,
        guardArcDeg: 42, guardDamageMult: 0.5 }    // smaller window: captain 45
    },

    // CC-C5: enemy type -> manifest body + anim.js VARIANTS key (was the
    // bandit/ghoul ternaries in region-manager buildRegion / enemy setBody;
    // an unknown type keeps the old fallbacks: ghoulBody / 'bandit').
    // CC-C7: + the unrigged rot bodies; rigidAnimByType = their anim.js
    // RIGID_CLIPS placeholder set (no skeleton, so no animVariantByType row).
    // CC-EC1: + the coven caster (elf-dawn-refuser rig; variant 'bandit' over
    // its universal 6-clip set - anim.js universal-name fallback covers the
    // rest, ~5 benign anim warns per coven body; death IS universal WH_Death).
    bodyByType: { bandit: 'banditBody', ghoul: 'ghoulBody', wolf: 'wolfBody',
      rotmother: 'rotmotherBody', rotspawn: 'rotspawnBody', coven: 'covenBody',
      scarreader: 'scarreaderBody',                       // CC-H4: the scar-reader wears the rot chassis
      zealot: 'banditBody', tithecaptain: 'banditBody',   // CC-H5: zealot chassis family (bandit manifest); the captain too (symmetry law)
      lastchancel: 'banditBody' },                 // CC-H6: the Last Chancel wears the bandit manifest (soldier-boss chassis law)
    animVariantByType: { bandit: 'bandit', ghoul: 'zombie', wolf: 'wolf', coven: 'bandit',
      zealot: 'bandit', tithecaptain: 'bandit',
      lastchancel: 'bandit' },
    rigidAnimByType: { rotmother: 'rotmother', rotspawn: 'rotspawn', scarreader: 'rotspawn' },   // CC-H4: crawler variant (scene-02 anchor)
    // CC-C5 WOLF PACKS (doc 62 L7/L8/L9 dens): closed patrol loops (world x,
    // z; walked in row order, last -> first). Each loop crosses its King's
    // Road branch (east / west / north) twice; designed offline against the
    // landed heightfield + prop rows (scratch/cc-c5/loops_probe.js): max r
    // from C's center 223.5 / 225.1 / 224.6 (rim foot 240 - jitter 6),
    // ground 0.16..3.08 / 2.05..5.00 / 1.87..4.63 m, max grade 9.5 / 10.5 /
    // 9.8 deg, >= 7.4 m from every prop row. Spawn rows live in
    // regionC.enemies (packId + waypointPhase = the patrol rank).
    wolfPacks: [
      { id: 'east', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // L7 Wolf den East
        waypoints: [[190, -318], [214, -322], [222, -340], [220, -372], [205, -398],
          [178, -388], [166, -360], [192, -334]] },
      { id: 'west', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // L8 Wolf den West
        waypoints: [[-190, -420], [-215, -418], [-224, -388], [-224, -362], [-200, -358],
          [-178, -340], [-166, -372], [-172, -402]] },
      { id: 'north', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,  // L9 Wolf den North
        waypoints: [[-25, -520], [-30, -548], [-62, -562], [-50, -585], [-25, -586],
          [10, -578], [25, -545], [12, -515]] },
      // CC-C16b densify packs (sw/se/ss/nw2): 4 more packs, loops probed >= 30 m
      // from every old loop point, >= 60 m from all fires, >= 36 m off roads.
      { id: 'sw', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // CC-C16b densify pack 1
        waypoints: [[-89.9, -336.7], [-78.4, -328.0], [-70.9, -290.5], [-86.6, -279.6], [-112.5, -276.1], [-140.3, -293.6], [-141.4, -322.0], [-122.7, -329.6]] },
      { id: 'se', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // CC-C16b densify pack 2
        waypoints: [[79.6, -186.8], [115.2, -158.5], [110.4, -142.3], [108.8, -127.6], [61.1, -118.7], [56.4, -130.3], [45.7, -161.7], [65.2, -193.3]] },
      { id: 'ss', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // CC-C16b densify pack 3
        waypoints: [[62.5, -249.5], [73.9, -256.9], [92.1, -203.5], [74.8, -188.5], [69.7, -181.7], [37.7, -203.8], [17.8, -224.5], [38.3, -254.6]] },
      { id: 'nw2', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // CC-C16b densify pack 4
        waypoints: [[223.3, -482.5], [236.3, -473.8], [240.9, -461.0], [229.4, -440.0], [213.5, -436.9], [199.7, -452.5], [198.2, -467.8], [200.4, -482.0]] }
    ],
    separationPush: 6.0,              // circle push-out strength
    holdAtBoundaryMargin: 1.5         // enemies stop this far before the boundary
  },

  hud: {
    regionNameFadeSeconds: 2.6,
    deathFadeSeconds: 0.8,
    fpsUpdateInterval: 0.5,
    // 2026-10-03 boot loading screen: overlay fade-out duration in ms.
    bootOverlayFadeMs: 900,
    // HP1: enemy health bars (HUD DOM projected above the head). Visible when
    // damaged this life OR the lock-on target; fade out once fsm 'dead'.
    hpbars: {
      widthPx: 46,               // PROPOSED, Nicko tunes
      heightPx: 6,               // PROPOSED, Nicko tunes
      heightAboveHeadM: 2.3,     // PROPOSED, Nicko tunes - world Y offset above enemy pos
      fadeStartM: 16,            // PROPOSED, Nicko tunes - distance where dimming begins
      fadeEndM: 32,              // PROPOSED, Nicko tunes - distance of minimum opacity
      minOpacity: 0.45,          // PROPOSED, Nicko tunes - alpha at fadeEndM+
      hideBeyondM: 40,           // PROPOSED, Nicko tunes - no bars past this
      scaleNearM: 6,             // PROPOSED, Nicko tunes - full width at/below this
      scaleFarM: 30,             // PROPOSED, Nicko tunes - width shrinks toward scaleFar, floor 0.8
      deathFadeSec: 1.2          // PROPOSED, Nicko tunes - fade-out once fsm 'dead'
    },
    // HP2: day/night clock (top-center circular dial). Hidden while the day
    // clock is dormant; needle = timeOfDay * 360deg clockwise from top (wake).
    dayClock: {
      sizePx: 64,                // PROPOSED, Nicko tunes
      topPx: 14,                 // PROPOSED, Nicko tunes - #wh-hud top offset
      frameColor: '#5a5344',     // PROPOSED, Nicko tunes - same family as .bar-outer
      daySeg: '#8a6b3a',         // PROPOSED, Nicko tunes - right half tint (day, amber-muted)
      nightSeg: '#23283a',       // PROPOSED, Nicko tunes - left half tint (night, blue-grey)
      needleColor: '#d8c9a0',    // PROPOSED, Nicko tunes - single accent
      needleLenFrac: 0.42        // PROPOSED, Nicko tunes - needle length x radius
    }
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
  // v3: procedural animation feel. Since whanim2 pose values drive
  // only the rigid stand-in fallback (skinned bodies play animRt
  // clips; whanim2 stage fractions = combat FSM clock for both paths).
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
    // Flat load timeout: the sky textures (daynight.js) only since 2026-10-11;
    // manifest GLBs use the size-scaled assetTimeout* rows below.
    timeoutMs: 20000,
    // Grey-stand-in resilience: rigged body loads retry on fetch/parse errors
    // with linear backoff before the stand-in swap; 0 disables retry. Failure
    // banner names asset + cause in console and HUD (see js/assets.js).
    bodyRetryCount: 2,                // extra attempts per rigged body (default on)
    bodyRetryDelayMs: 750,            // backoff base; delay = base * attempt#
    // 2026-10-11 asset pipeline (io/missions/2026-10-11-asset-pipeline.md):
    // the phone pipe is ~1 MB/s shared (Tailscale), so 50 parallel fetches
    // under a flat 20 s abort timed every big GLB out. Per-attempt timeout =
    // clamp(assetTimeoutMsPerMb x sizeMB, min, max), sizeMB = Content-Length
    // / 1e6 (bytes received so far while unknown; min before headers);
    // retries inherit the size learned by the first attempt.
    assetTimeoutMsPerMb: 6000,
    assetTimeoutMinMs: 20000,
    assetTimeoutMaxMs: 120000,
    criticalPoolSize: 4,              // concurrent fetches while bootCritical loads
    streamPoolSize: 6,                // concurrent fetches for the rest, after boot
    stallLineAfterMs: 8000,           // boot overlay 'slow link' line past this per asset
    // Boot barrier: the game enters once THESE settle (loaded or stand-in);
    // every other manifest name streams in after and late-swaps any stand-in
    // handed out meanwhile. Derived from region A's boot build (the
    // scratch/asset_pipeline_report.md derivation): game.js boot (playerBody;
    // setupHandMeshes instances EVERY gear mesh: longsword, dagger,
    // roundShield, torch), player.js setBody (playerDagClips clips),
    // enemy.js bandit setBody (handAxe), region-manager buildRegion(A)
    // (props, scatter trees, bramble/whBushSnare/grassTuft instanced,
    // banditBody/ghoulBody enemies) + buildWorld (whWallA/B, b3Gate,
    // whLanternHang) - and whWallPlan/whScatterPlan read the footprint of
    // EVERY region A AND B prop (plan.complete gates the wall and the
    // scatter), so all of those are boot-critical too. whTent/whCampkit:
    // CONTINUE restores deployed kit sites (camp.js makePiece extracts kit
    // nodes - a stand-in cannot late-swap a node). Largest first (pool
    // order). Deferred: bushA, bushB (region C scatter), banditBedroll,
    // ironFenceCorner (unreferenced at boot).
    // CC-C5: wolfBody (2.08 MB) is boot-critical too - CONTINUE restores a
    // region C save straight into buildRegion(C), and a late-swapped rigged
    // body gets the mesh but never its clips (or its measured scale).
    // CC-C7: b6Bones (0.87 MB, nest props: region C's scatter / collider
    // plans need every prop footprint) + rotmotherBody (0.74 MB, a C row:
    // CONTINUE into C builds her at boot). rotspawnBody stays deferred - the
    // spawner instances it at runtime and a rigid body late-swaps cleanly.
    // CC-C8: b6Bones OUT (no row uses it now); the den kit IN (crypt
    // stoneSteps 0.36 MB + skullPile 0.50 MB, blightcap: a CONTINUE saved inside
    // the den builds regionD at boot and its collider table needs every
    // footprint). rotmotherBody stays: CONTINUE into D builds her at boot.
    bootCritical: [
      'playerBody', 'banditBody', 'ghoulBody', 'wolfBody', 'playerDagClips', 'bramble',
      'whCampkit', 'whTent', 'yewTree', 'livingOak', 'youngAsh', 'cemeteryGate',
      'torch', 'mossBoulder', 'witchwoodTree', 'mourningStatue', 'deadTree',
      'fallenLog', 'reachTreeA', 'lanternWaymarker', 'picketFence', 'treeStump',
      'b3Gate', 'lanternPost', 'youngBirch', 'whWallB', 'banditCampfire',
      'whWallA', 'reachTreeB', 'reachTreeC', 'youngDeadTree', 'whLanternHang',
      'graveMound', 'dagger', 'grassTuft', 'rubblePile', 'stoneCrossTilted',
      'roundShield', 'ironFenceSection', 'churchCornerButtress',
      'gravestoneObelisk', 'churchPewBroken', 'buriedCoffin', 'handAxe',
      'churchArchway', 'whBushSnare', 'longsword', 'rotmotherBody', 'stoneSteps',
      'skullPile', 'blightcap'
    ],
    // MAGANIM (doc 65 R-65.3): caster-implement registry (v1; future caster
    // weapons append here). BOTH hands holding one of these = the caster body
    // variant (anim.js setVariant: WH_Mag_* idle / locomotion / reactions /
    // death); one = warrior body. Presentation tunables ride along:
    // backwardDot = move dir . facing below this (lock-on) plays the Back
    // clips; largeHitFraction = a hit >= this x hpMax plays ReactLarge.
    // CAST1H: castShotSpeed = the 1H cast shot's timeScale (Cast2H stays 1);
    // a single-glove main-hand projectile cast fires at fire1HFraction of the
    // clip: windup = max(castWindup, fire1HFraction * cast1HClipSeconds /
    // castShotSpeed) = 0.46 * 2.3 / 1.5 = 0.71 s after accept.
    caster: {
      items: ['magicGlove'],
      backwardDot: -0.5,              // PROPOSED: ~120 deg+ off facing
      largeHitFraction: 0.2,          // PROPOSED: 20 hp of 100
      castShotSpeed: 2.25,            // PROPOSED: Nicko 10-10 second order, +50% on top
                                      // of the first 1.5 (fire = 0.46 * 2.3 / 2.25 = 0.47 s)
      fire1HFraction: 0.46,           // PROPOSED: R_Hand peak f32/70 of WH_Mag_Cast1H
                                      // (scratch/mag_cast_peak.json, FK measured)
      cast1HClipSeconds: 2.3,         // native clip duration (70 frames @ 30fps)
      castUpperBody: true,            // PROPOSED: Nicko 10-10 - cast 1H torso-only,
                                      // legs keep the locomotion while the shot runs
      // Waist split of the player rig's 20 animated nodes (every clip is a dense
      // bake of all 20; scratch/glb_bone_census2.py -> mag_cast_track_partition.json:
      // 42/42 clips 12 upper + 8 lower, overlap none). Arms parent Chest, Chest
      // parents Spine; legs parent Hips, Hips parents Root.
      castUpperNodes: ['Spine', 'Chest', 'Neck', 'Head', 'L_Shoulder', 'L_UpperArm',
                       'L_Forearm', 'L_Hand', 'R_Shoulder', 'R_UpperArm',
                       'R_Forearm', 'R_Hand'],
      castLowerNodes: ['Hips', 'Root', 'L_Thigh', 'L_Shin', 'L_Foot', 'R_Thigh',
                       'R_Shin', 'R_Foot']
    },
    // R4 kill switch: true swaps the 3 rigged body atlases for the committed
    // 512px pixelated PNGs at postload; false = original 2048 atlas path.
    pixelatedBodies: true,
    standInColor: 0x777777,
    // Round J (io/roundJ-provenance.md): the Meshy reach-trees are open-
    // bottomed shells whose root tips hang below the trunk floor, so
    // groundAlign (lowest vertex -> y=0) stood them on those tips with sky
    // under the trunk (0.27/0.80/0.39m median gap at scale 10). Extra sink
    // in GLB units (scales with every placement + scatter scale) = p75 of the
    // trunk-underside height (scratch/roundJ_underside.py). {} = old look.
    groundSink: { reachTreeA: 0.0312, reachTreeB: 0.0878, reachTreeC: 0.0500 },
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
    // dagger (DAG B2): 0.35m target / 1.8867 measured height (raw ext 0.3643 x
    // 1.8867 x 0.3479; scratch/dagger_measure.json, scratch/measure_dagger.py)
    // = scale 0.1855 - the smallest weapon in the game.
    weaponTargetHeight: { longsword: 1.05, handAxe: 0.6, roundShield: 1.0, torch: 0.62,
                          dagger: 0.35 },
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
    // holder 0, already correct. dagger (DAG B2): grip butt normalized to the
    // origin in Phase A -> 0 (scratch/dagger_measure.json gripHolderY 0.0).
    weaponMount: { rollDeg: 0, enabled: true,
                   gripHolderY: { longsword: 1.637, handAxe: 0, dagger: 0 } },
    // 10-04 left-hand shield mount (scratch/measure_shield.py, L_Hand at
    // WH_Idle frame 0). Vectors are L_Hand-local. faceAxis: where the boss
    // side (raw +Z) points = body-left turned 20 deg toward forward, level.
    // upAxis: where the disc's raw +Y points = world up. rollDeg: extra turn
    // about hand-local +Z (weaponMount convention). offset: hand-local spot
    // the shield's back-most point sits on = fist centroid [0.018, 0.078,
    // 0.021] pushed 0.042 (fist depth) + 0.01 along faceAxis; the L_Thigh
    // clears that plane by 0.027 at idle.
    shieldMount: { faceAxis: [-0.876, 0.4, 0.271], upAxis: [-0.327, -0.903, 0.277],
                   rollDeg: 0, offset: [-0.028, 0.099, 0.035] },
    // Stage 2 S3 torch hand mount (nativeHand.torch = left; mirrored for the
    // right hand like the shield). scratch/measure_torch_grip.py: the shaft
    // is a Y-symmetric stick, butt at holder y 0, narrowest (the hand wrap)
    // at holder y 0.38-0.57, head flaring 1.14-1.80 (amber cap from 1.54).
    // headAxis: L_Hand-local direction the torch head points - hand +Z is the
    // fist's grip-forward axis (the longsword blade's mapping), so the torch
    // is carried like a raised blade. offset: the fist centroid (casterGlow
    // handOffset). gripHolderY / lightHolderY are RAW GLB units along the
    // shaft (they scale with the mesh): the fist lands on gripHolderY, the
    // hand's follow light sits at lightHolderY (the flame, not the fist).
    torchMount: { headAxis: [0, 0, 1], rollDeg: 0, offset: [0.018, 0.078, 0.021],
                  gripHolderY: 0.5, lightHolderY: 1.7,
                  // Raised-arm torch carry (S3 tweak 10-06): the shaft stands
                  // near-vertical instead of riding like a blade. Bone-lift
                  // overlay in player.applyTorchCarryPost (post-mixer, additive,
                  // eased by easeSec both ways, only on the hand holding the
                  // torch). Measured on combat-chain.glb: bind shaft = 86deg
                  // off vertical; lift 65 + bend 15 -> 20deg, a natural carry
                  // lean with the flame up and clear of the fist. Right hand
                  // mirrors with the SAME sign (verified 19.4deg).
                  carry: { liftDeg: 65, bendDeg: 15, easeSec: 0.25,
                           // MESH-space dir the shaft must map to for TRUE
                           // vertical: tgt = q_head^-1 * t_hand, where
                           // t_hand = M^T * world+Y at full lift (verified:
                           // L lands exact vertical; R via the mount mirror
                           // lands 0.7deg off - rig asymmetry)
                           straightenAxis: [-0.3271, 0.9396, 0.101] } }
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
// EPR1 (io/specs/devbot-spec-wh-erparity-combat.md, 2026-10-06) replaces the
// windup / roll rules above with per-move data (ER-style cancel matrix):
//  - move.cancel = EARLIEST point each input type may interrupt the swing,
//    as a fraction of windup+strike+recover: dodge = a queued dodge (pressed
//    in any stage) rolls out; guard = a held RMB raises the block while the
//    swing plays out; move = walk restores to combat.er.moveCancelWalkMult x
//    player.walkSpeed. The light (chain) column stays chainOpenSec.
//  - LMB in windup: ignored before move.bufferFrom x windup, buffered from
//    it; such a press starts its inputBufferSec lifetime at the strike.
//  - move.rootMotion = cumulative forward metres per stage [start, end]
//    (frame-anchored, player.js applyRootMotion) x lunge (legacy multiplier,
//    1.0); moves without a table keep the legacy strike lunge (metres).
window.WH_CONFIG.moveset = {
  idlePose: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
  banditStageMult: 1.6,
  enemyWeapon: { bandit: 'handAxe' },
  playerWeapon: 'longsword',        // which weapons[] entry the player wields
  inputBufferSec: 0.65,             // buffered LMB lifetime (strike/recover presses); RoundD: 0.65 = worst-case hold (thrust finisher: strike remainder 0.43 + full recover 0.17 = 0.60) + one 20fps frame (0.05) - no mash expiring
  weapons: {
    longsword: {
      chainCap: 3,
      // Nicko's order: swipe right->left, swipe left->right, THRUST, reset.
      chain: ['slashR2L', 'slashL2R', 'thrust'],
      // movement speed multiplier per swing stage (windup keeps 0.3 creep)
      moveMultWhileAttacking: { windup: 0.3, strike: 0, recover: 0 },
      bladeAxisY: -1,               // mesh-local blade axis (-Y tip, see setWeapon)
      // Round D: durations derived from Mixamo impact frames (scratch/swordpack_probe4_rD.json); totals equal clip durations.
      // EPR1 (spec 3.2-3.3; DESIGN values, playtest-tunable): cancel / bufferFrom /
      // rootMotion per move; lunge (was 0.8 / 0.8 / 1.4 m) is now the 1.0 table multiplier.
      moves: {
        slashR2L: { pose: 'm2', windup: 0.57, strike: 0.20, recover: 0.73,
                    chainOpenSec: 0.20,
                    damage: 34, range: 3.2, halfAngleDeg: 70, lunge: 1.0,
                    staminaCost: 15, damageGhoulMult: 1.15,
                    cancel: { dodge: 0.90, guard: 0.95, move: 0.65 }, bufferFrom: 0.5,
                    rootMotion: { windup: [0, 0], strike: [0, 0.9], recover: [0.9, 1.0] } },
        slashL2R: { pose: 'm1', windup: 0.80, strike: 0.26, recover: 0.61,
                    chainOpenSec: 0.26,
                    damage: 34, range: 3.2, halfAngleDeg: 70, lunge: 1.0,
                    staminaCost: 15, damageGhoulMult: 1.15,
                    cancel: { dodge: 0.90, guard: 0.95, move: 0.65 }, bufferFrom: 0.5,
                    rootMotion: { windup: [0, 0], strike: [0, 0.9], recover: [0.9, 1.0] } },
        // thrust = narrow, longer reach, more damage, heavier recover
        thrust:   { pose: 'm4', windup: 0.40, strike: 0.43, recover: 0.17,
                    chainOpenSec: 0.40,   // last move: full recover anyway
                    damage: 40, range: 3.8, halfAngleDeg: 22, lunge: 1.0,
                    staminaCost: 20, damageGhoulMult: 1.15,
                    cancel: { dodge: 0.90, guard: 0.95, move: 0.80 }, bufferFrom: 0.5,
                    rootMotion: { windup: [0, 0], strike: [0, 1.5], recover: [1.5, 1.7] } }
      }
    },
    // Quick 2-hit hatchet chain: faster, shorter, lower damage per hit.
    handAxe: {
      chainCap: 2,
      chain: ['hack', 'chop'],
      moveMultWhileAttacking: { windup: 0.4, strike: 0, recover: 0 },
      bladeAxisY: 1,                // axe bit along mesh-local +Y (as enemy.js)
      // EPR1 F3: neutral cancel columns mirroring the longsword slashes; no bufferFrom
      // (windup LMB stays ignored) and no rootMotion table (legacy lunge metres).
      moves: {
        hack: { pose: 'claw', windup: 0.10, strike: 0.14, recover: 0.22,
                chainOpenSec: 0.08,
                damage: 22, range: 2.6, halfAngleDeg: 60, lunge: 0.5,
                staminaCost: 10, damageGhoulMult: 1.15,
                cancel: { dodge: 0.90, guard: 0.95, move: 0.65 } },
        chop: { pose: 'm3', windup: 0.12, strike: 0.14, recover: 0.30,
                chainOpenSec: 0.30,
                damage: 27, range: 2.7, halfAngleDeg: 35, lunge: 0.7,
                staminaCost: 12, damageGhoulMult: 1.15,
                cancel: { dodge: 0.90, guard: 0.95, move: 0.65 } }
      }
    },
    // DAG (io/missions/2026-10-09-dagger.md B1; DESIGN values, playtest-tunable):
    // DAGTUNE2 (io/missions/2026-10-09-dagger-tune2.md, Nicko 10-09 tuning: x2
    // clocks, half damage -> chain 1.46 -> 2.92 s, damage 50 -> 25, DPS 34.2 ->
    // ~8.6). The deliberate identity inversion: the dagger is no longer
    // fast-DPS, it is the low-damage bleed-delivery weapon. DAGANIM2
    // (io/missions/2026-10-10-dag-swipes.md, Nicko 10-10 "three quick swipes,
    // right left then right", no crouch): clips rebuilt from the standing
    // swordpack slash / slash (3) at 0.25 / 0.25 / 0.52 s and every clock row
    // below scaled by new/old clip length (x0.25/0.38, slash 3 x0.52/0.70) ->
    // chain 2.92 -> 2.04 s; damage, stamina, bleed and cancel fractions
    // untouched. Three side-to-side swipes, then the pause (slash 3's 0.71
    // recover) and the reset to chain[0]. handAxe dialect: no
    // bufferFrom (windup LMB ignored), no rootMotion table (legacy lunge metres).
    // Poses (stand-in pivot only): m2 = slash-r2l, m1 = slash-l2r (the longsword
    // slash shapes). The rigged body plays WH_DagSlashR2L / WH_DagSlashL2R /
    // WH_DagSlashR2Lb (combat-dagger.glb; clips 0.25 / 0.25 / 0.52 s, stretched
    // onto the CONFIG clocks below by anim.js seekAttack - the x2 slow-down
    // lives here only, no re-bake)
    // through anim.js MOVE_NAMES, ONLY while this moveset is the wielded weapon
    // (clip source: assets.js MANIFEST.playerDagClips, merged in player.setBody).
    // PHASE CLOCK (full clock, every recover played out):
    //   dagger    (0.13+0.16+0.21)*2 + (0.15+0.18+0.71) = 0.50 + 0.50 + 1.04 = 2.04 s
    //             for 7.5+7.5+10 = 25 dmg (12.3 dmg/s), stamina 7+7+9 = 23
    //             (was (0.20+0.24+0.32)*2 + (0.20+0.24+0.96) = 2.92 s / 25 dmg;
    //             before DAGTUNE2 1.46 s / 50 dmg)
    //   handAxe   (0.10+0.14+0.22) + (0.12+0.14+0.30) = 0.46 + 0.56 = 1.02 s for
    //             22+27 = 49 dmg (48.0 dmg/s), stamina 10+12 = 22
    //   longsword (0.57+0.20+0.73) + (0.80+0.26+0.61) + (0.40+0.43+0.17) = 4.17 s
    //             for 34+34+40 = 108 dmg (25.9 dmg/s), stamina 15+15+20 = 50
    // The trades: range 1.9 is the SHORTEST reach (handAxe 2.6-2.7, longsword
    // 3.2-3.8) and stamina 7 / slash the CHEAPEST (handAxe 10-12, longsword
    // 15-20); the dagger pays in reach AND raw damage - its payoff is bleed
    // (CONFIG.combat.bleed; main-hand ticks scale with the halved dealt damage).
    // cancel fractions unchanged (they ride the scaled clocks). Worked example
    // (fraction of windup+strike+recover): slash 1 = 0.50 s, move-cancel at
    // 0.65 x 0.50 = 0.325 s (0.035 s into the 0.21 recover, i.e. right after the
    // 0.29 s strike ends). Two-hit dart: slash 1 chained in full (0.50) + slash 2
    // cut at 0.325 = 0.825 s for 15 dmg / 14 stamina, then walk out at
    // moveCancelWalkMult. Slash 3: 0.65 x 1.04 = 0.676 s, so walking out skips
    // 1.04 - 0.676 = 0.364 s of the 0.71 pause. (longsword slashR2L move-cancel:
    // 0.65 x 1.50 = 0.975 s.) Dodge 0.90 x 0.50 = 0.45 s, guard 0.95 x 0.50 =
    // 0.475 s.
    // dagSlashR2Lb's range / halfAngleDeg / lunge / damageGhoulMult (the brief
    // leaves them unset) repeat slash 1's.
    dagger: {
      chainCap: 3,
      chain: ['dagSlashR2L', 'dagSlashL2R', 'dagSlashR2Lb'],
      moveMultWhileAttacking: { windup: 0.4, strike: 0, recover: 0 },   // handAxe row
      bladeAxisY: 1,                // scratch/dagger_measure.json bladeAxisY (+Y tip, grip butt at origin)
      moves: {
        dagSlashR2L:  { pose: 'm2', windup: 0.13, strike: 0.16, recover: 0.21,
                        chainOpenSec: 0.21,
                        damage: 7.5, range: 1.9, halfAngleDeg: 55, lunge: 0.4,
                        staminaCost: 7, damageGhoulMult: 1.15,
                        cancel: { dodge: 0.90, guard: 0.95, move: 0.65 } },
        dagSlashL2R:  { pose: 'm1', windup: 0.13, strike: 0.16, recover: 0.21,
                        chainOpenSec: 0.21,
                        damage: 7.5, range: 1.9, halfAngleDeg: 55, lunge: 0.4,
                        staminaCost: 7, damageGhoulMult: 1.15,
                        cancel: { dodge: 0.90, guard: 0.95, move: 0.65 } },
        // the third cut ends in THE PAUSE (0.71 recover), then the chain resets
        dagSlashR2Lb: { pose: 'm2', windup: 0.15, strike: 0.18, recover: 0.71,
                        chainOpenSec: 0.71,   // last move: full recover anyway
                        damage: 10, range: 1.9, halfAngleDeg: 55, lunge: 0.4,
                        staminaCost: 9, damageGhoulMult: 1.15,
                        cancel: { dodge: 0.90, guard: 0.95, move: 0.65 } }
      }
    }
  }
};

// EPR1 (2026-10-06, io/specs/devbot-spec-wh-erparity-combat.md): ER-parity input
// grammar shared by every move (per-move cancel / bufferFrom / rootMotion are on the
// CONFIG.moveset moves above). Seconds are the number of record; harness gates
// convert at the 1 / loop.maxDt = 20 Hz game clock (EPR1-A1).
window.WH_CONFIG.combat = {
  er: {
    dodgeHoldSec: 0.35,             // Space held >= this (inclusive: 7 frames @20 Hz) = sprint, release no roll; shorter = dodge on release
    guardRaiseSec: 0.13,            // block accept -> blockActive for the hit checks (~ER 4-frame raise)
    moveCancelWalkMult: 0.5,        // walk from move.cancel.move to the swing's end, x player.walkSpeed
    backstep: {                     // keyboard dodge tap with no move direction, from neutral
      duration: 0.30,               // s, backwards hop along facing
      speedMult: 0.9,               // x player.walkSpeed
      iframes: 0.20,                // s
      staminaCost: 20
    }
  },
  // DAGBLEED (io/missions/2026-10-09-dagger-bleed.md, Nicko 10-09): dagger
  // bleed = damage over time on an enemy. DESIGN CONTEXT: the parry proc is
  // the signature skill reward (a dagger opens the parry window with no
  // shield; shield parries never bleed). The 15% main-hand proc is ~+7%
  // sustained over a full chain, but ~2x payoff on a lone stab + dart out.
  // Tick basis = tickFraction x the PROCCING hit's dealt damage (parry: the
  // parried swing's raw, pre-mitigation amount - cut with the enemy's own
  // force), every tickSec for durationSec, routed through
  // Enemy.prototype.takeDamage (bleed can kill). One instance per enemy; a
  // re-proc resets the clock and the newer force replaces the older.
  bleed: {
    parryChance: 0.50,        // Nicko 10-09: successful parry w/ dagger equipped
    hitChance: 0.15,          // dagger main-hand landed hits
    tickFraction: 0.5,        // per-second tick = half the proccing hit's dealt damage
    durationSec: 5,           // Nicko: every second for 5 seconds
    tickSec: 1,
    refresh: 'reset',         // re-proc RESETS the 5 s timer; never stacks (Nicko-picked)
    // OFF-HAND RIDER. INERT v1: nothing reads it and enabled stays false -
    // the literal "dagger in the off hand gives 50% bleed on hits" version
    // measured +70% sustained longsword DPS (IO math, rejected). The future
    // hook is the melee sweep proc site (game.js) once an off-hand dagger
    // exists (the dagger is right-hand only today; that branch will read
    // riderOffHand when it lands - not built here).
    riderOffHand: { enabled: false, chance: 0.50 },
    // Bleed ring under a bleeding enemy (game.js updateBleedMarkers, the
    // riposteMarker lazy-mesh pattern): shown exactly while enemy.bleed is up.
    ring: {
      color: 0xb3241e,              // blood red (riposte ring stays amber)
      radius: 0.70,                 // inside the riposte ring (0.85) so both read
      width: 0.12,
      segments: 12,                 // low-poly = chunky/pixel read
      opacity: 0.85,
      yOffset: 0.035                // above ground, under the riposte ring (z-fight)
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
    block:    { x: 0.90, y: 0.65 },
    // S3b: USE = the E key (pickup, then gather; future chests/doors).
    // Above-left of attack, clear of sprint and the camera pad.
    interact: { x: 0.74, y: 0.38 }
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
      ingredient: 0x7cb860,         // stage 2: moss green (gathered cooking ingredients)
      food: 0xc07a3a                // C1: cooked food (warm broth brown)
    }
  }
};

// Stage 2 (Nicko 10-05): enemy drops. ONE shared pool for both enemy types
// (bandit + ghoul drop exactly the same things). Every kill: the guaranteed
// stack, plus a bonusChance roll into the weighted bonusPool (weight / sum).
// Cooking ingredients NEVER drop from enemies (gather nodes + wild animals
// only). Order S4 (Nicko 10-05): drops are stored on the corpse; boxes are
// player G-drops only. The roll lands in enemy.corpseLoot and is looted off
// the body (CONFIG.corpseLoot) - no WorldItems box ever spawns from a kill.
window.WH_CONFIG.drops = {
  bonusChance: 0.20,                // per kill
  bonusPool: [                      // weighted pick (torch most common, glove rare)
    { id: 'torch', weight: 50 },
    { id: 'bandage', weight: 30 },
    { id: 'magicGlove', weight: 8 }
  ],
  guaranteed: { id: 'stolenCoin', count: 1 }
};

// Order S4 (Nicko 10-05): the corpse IS the loot container (js/corpse-loot.js
// WH_CORPSE_LOOT). While enemy.corpseLoot is non-empty the body shows a soft
// additive gold glow (billboard + ground pool) with unlit sparks rising off
// it; USE / E (game.js interact: box pickup > corpse > gather node) moves
// everything that fits into the inventory, the rest stays on the body. An
// emptied corpse fades its effect out and is plain forever after.
// NO PointLights on corpses, ever - the light budget (CONFIG.playerLight /
// lightPool) is unchanged; the additive glow reads at night on its own.
// LIFETIME (playtest): unlooted loot lives only as long as the corpse object -
// a region rebuild / reset recreates the corpse empty and the loot vanishes.
// REAL-GAME PERSISTENCE attaches here later: store corpseLoot in the region
// state (RegionLogic.stateFor(...).enemies) next to the 'dead' flag.
window.WH_CONFIG.corpseLoot = {
  lootRadius: 1.6,                  // m from the corpse centre (same feel as pickupRadius)
  promptText: 'USE - Loot',         // touch + desktop wording (E and USE share interact)
  lootToast: 'Looted: {list}',      // {list} = 'Stolen Coin x1, Torch x1'
  partialSuffix: ' - Inventory full',   // appended when something stayed on the body
  fullText: 'Inventory full',       // nothing fit: corpse keeps glowing
  appearDelaySec: 0.6,              // effect starts this long after the kill (corpse settles)
  fadeInSec: 0.4,
  fadeOutSec: 0.5,                  // looted-empty fade
  glowColor: 0xd8b24a,              // gold = coin / human accent family
  glowOpacity: 0.55,                // peak additive strength
  glowPulseSec: 2.4,                // one gentle breath
  glowPulseMin: 0.6,                // opacity trough (fraction of peak)
  glowScale: 1.5,                   // billboard size (m) ~ the torso
  glowHeight: 0.45,                 // billboard centre over the ground (m)
  groundGlow: { radius: 0.95, opacity: 0.45 },   // flat additive pool under the body (0 opacity = off)
  sparks: {
    count: 14,                      // pool size per active corpse (recycled)
    riseSpeed: 0.45,                // m/s
    drift: 0.12,                    // m/s max sideways wander
    lifetimeSec: 2.2,               // each spark's rise (fades in, then out at the top)
    lifetimeJitter: 0.35,           // +- fraction
    spawnRadius: 0.45,              // m disc over the body they rise from
    size: 0.07,                     // m (attenuated points)
    color: 0xffd27a
  }
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
  // DAG (2026-10-09): the Magician's starting blade (class-extra kit row,
  // CONFIG.startingClasses). Melee like the longsword: the right hand swings
  // the CONFIG.moveset.weapons.dagger chain and trains the Short Blade line.
  // Right hand only v1: a left-hand melee never swings, and with no melee
  // wielded right the left mount would read the longsword's blade axis.
  dagger:         { id: 'dagger', name: 'Dagger', glyph: 'DG',
                    category: 'gear', stackCap: 1, kind: 'melee', moveset: 'dagger', mesh: 'dagger',
                    hands: ['right'], equipHint: 'rightHand' },
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
  // Stage 2: mesh 'torch' (MANIFEST.torch) on CONFIG.assets.torchMount; one
  // instance per hand, so torch + torch shows two torches and two lights.
  // Drop source: CONFIG.drops.bonusPool. Not in the Q swap pair.
  torch:          { id: 'torch', name: 'Torch', glyph: 'TR',
                    category: 'gear', stackCap: 1, kind: 'torch', mesh: 'torch',
                    hands: ['left', 'right'], equipHint: 'leftHand',
                    light: { color: 0xffa040, intensity: 10.5, distance: 15,
                             decay: 2, flickerPct: 7 } },
  // Stage 2 enemy drop (CONFIG.drops.guaranteed). 'valuable' = new category;
  // vendor / currency systems are NOT built - it only stacks for now.
  stolenCoin:     { id: 'stolenCoin', name: 'Stolen Coin', glyph: 'SC',
                    category: 'valuable', stackCap: 999 },
  // CC-C7 Rot Mother materials (doc 62 R-62.4 farmable nest loop; rows
  // CONFIG.enemy.rotmother / rotspawn .loot). Crafting is NOT built: they
  // stack as valuables until a crafting ruling lands (the 'valuable' tip +
  // colour; no new inventory category). flavor = the tooltip line; dropLog =
  // the one-time journal toast on the first loot of each (game.js).
  'rot-silk':     { id: 'rot-silk', name: 'Rot-Silk', glyph: 'RS',
                    category: 'valuable', stackCap: 99, material: true,
                    flavor: 'Damp grey thread, spun to swaddle young that never woke',
                    dropLog: 'Rot-Silk: she wove it soft, and wrapped each one as if it might still breathe.' },
  'rot-gland':    { id: 'rot-gland', name: 'Rot-Gland', glyph: 'RG',
                    category: 'valuable', stackCap: 99, material: true,
                    flavor: 'A swollen sac, still warm, still trying to make milk',
                    dropLog: 'Rot-Gland: it kept working after everything else in her had given up.' },
  // Stage 2 cooking ingredients: ONLY from gather nodes (CONFIG.gather) and,
  // in a later stage, wild animals - never enemy drops. Default stackCap.
  forestHerb:     { id: 'forestHerb', name: 'Forest Herb', glyph: 'FH', category: 'ingredient' },
  deadwood:       { id: 'deadwood', name: 'Deadwood', glyph: 'DW', category: 'ingredient' },
  wildMushroom:   { id: 'wildMushroom', name: 'Wild Mushroom', glyph: 'WM', category: 'ingredient' },
  graveMoss:      { id: 'graveMoss', name: 'Grave Moss', glyph: 'GM', category: 'ingredient' },
  boneShard:      { id: 'boneShard', name: 'Bone Shard', glyph: 'BS', category: 'ingredient' },
  // CC-WM1 redseam: smelting raw (doc 42 Part 5; icon = glyph fallback IO, icon lane later).
  ironOre:        { id: 'ironOre', name: 'Iron Ore', glyph: 'IO', category: 'ingredient' },
  // C1 cooked food (CONFIG.cooking). category 'food' = eaten from the
  // inventory screen (select + E / EAT). useHint.buff keys CONFIG.cooking
  // .buffs (absent = edible, no buff). weight = item weight (no carry
  // system reads it yet). flavor = tooltip line.
  graveSoup:      { id: 'graveSoup', name: 'Grave Soup', glyph: 'GS', category: 'food',
                    weight: 20, useHint: { kind: 'eat', buff: 'graveSoup' },
                    flavor: 'Earthy, bitter, strangely fortifying' },
  blandMush:      { id: 'blandMush', name: 'Bland Mush', glyph: 'BM', category: 'food',
                    weight: 15, useHint: { kind: 'eat', buff: 'blandMush' },
                    flavor: 'A sad grey mush' },
  // CC-WB1: war-effort requisition paper (doc 42 Part 3). New category
  // 'document' (plain string, no system reads it yet - stolenCoin 'valuable'
  // precedent); glyph fallback law, no icon PNG (ironOre WH1-W2 precedent).
  warOrder:       { id: 'warOrder', name: 'War Requisition', glyph: 'WO',
                    category: 'document', desc: 'Garrison order: 6 iron ore for the war effort.' },
  // CC-WB3 strata board (js/strataeffort.js): requisition paper row mirroring
  // the warOrder row exactly (document category, glyph-fallback law, no PNG).
  strataOrder:    { id: 'strataOrder', name: 'Strata Requisition', glyph: 'SR',
                    category: 'document', desc: 'Strata order: rot-silk + rot-gland from the delve strata.' }
};

// C1 (io/missions/2026-10-05-cc-c1-cooking.md): cooking at a fire station.
// CAMP GROWTH LAW: stations are DATA rows (id, region, prop asset + coords,
// interact radius, fuel) in a generic registry (js/cooking.js
// WH_COOKING.stations) - C3's deployed campfire registers the same row
// shape, nothing here is special-cased to the bandit fire. Only rows listed
// in stations cook; every other fire (region A dressing fire) is inert.
window.WH_CONFIG.cooking = {
  interactRadius: 2.5,              // m from the station prop to cook / refuel
  channelSeconds: 3,                // cook channel; stand still (move / hit / Cancel interrupts)
  // keys that break a running channel (movement + roll; player.js bindings)
  interruptKeys: ['KeyW', 'KeyA', 'KeyS', 'KeyD', 'Space'],
  // C2: day buffs last buffs[].days in-game days (CONFIG.dayNight
  // dayLengthSec, counted down by the day clock). FALLBACK ONLY: if the
  // daynight module is missing, 1 day = this many REAL seconds.
  buffDurationFallbackSec: 480,
  fire: {
    startFuelSec: 240,              // stations with startLit begin with this much fuel (generous for the playtest)
    burnPerCookSec: 10,             // fuel spent per cook (channel + margin), deducted at cook start
    burnTickSec: 1,                 // passive burn loop step: fuel drops this much every this many seconds
    refuelCooks: 4,                 // 1 deadwood refuels to burnPerCookSec * refuelCooks seconds
    fuelItem: 'deadwood',           // the fuel ingredient (never a cook slot)
    burntLightIntensity: 0          // light-pool socket intensity while burnt out (0 = dark)
  },
  // CC-C6C kinds (Nicko ruling 2026-10-11): 'cookFire' = cookable, fuel /
  // refuel / deadwood rules (the player's C3 kit fire rides it from
  // CONFIG.camp.modules.fire). 'campfire' = an atmospheric bandit fire: lit
  // exactly while the clock phase is 'night' (dormant clock = out), never
  // cookable, never refuels, no fuel burn (startLit / fuel stay inert); E
  // = text.promptCampfire + text.campfireToast only. CC-C9 (Nicko ruling
  // 2026-10-20): the Region B STARTING bandit fire is NOT an atmospheric
  // campfire - CC-C6C was over-applied there; the C3 world-camp ruling kept
  // it the tutorial's DESIGNATED cooking station, so it rides 'cookFire'
  // again. Future designated cook stations also ride 'cookFire'.
  stations: [
    // Region B bandit campfire (prop banditCampfire x 2.5, z -52). CC-C9
    // (Nicko ruling 2026-10-20): this is the ONE bandit fire that cooks - the
    // tutorial's designated cooking station (C3 world-camp ruling) beside the
    // tent; cooking here teaches the first recipe and arms the CAMP kit.
    { id: 'banditFire', kind: 'cookFire', regionId: 'darkwood_edge',
      asset: 'banditCampfire', x: 2.5, z: -52, startLit: true },
    // CC-C6 Region C bandit camp fires (props banditCampfire at these exact
    // x/z: socketIntensity matches station <-> prop within 0.01 m). CC-C6C
    // night-only atmospheric holds for THESE (not for the tutorial fire).
    { id: 'banditFireA', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: -60.0, z: -186.0, startLit: true },    // L4 Alpha
    { id: 'banditFireB', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: 95.0, z: -236.0, startLit: true },     // L5 Bravo
    { id: 'banditFireC', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: -140.0, z: -506.0, startLit: true },
    { id: 'banditFireD1', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: -106.1, z: -472.1, startLit: true },    // CC-C16b camp 1
    { id: 'banditFireD2', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: 118.0, z: -448.6, startLit: true },    // CC-C16b camp 2
    { id: 'banditFireD3', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: -207.8, z: -246.0, startLit: true },    // CC-C16b camp 3
    { id: 'banditFireD4', kind: 'campfire', regionId: 'forest_of_the_old_king',
      asset: 'banditCampfire', x: 144.2, z: -536.9, startLit: true },    // CC-C16b camp 4    // L6 Charlie
  ],
  // Recipes: exactly 3 ingredients, order-free, no preview ever. Any other
  // trio at a fire = fallbackResult (the gamble's waste). known flips true on
  // the first successful cook (session-only; C4 save writes it).
  recipes: [
    { id: 'graveSoup', name: 'Grave Soup',
      ingredients: ['graveMoss', 'wildMushroom', 'boneShard'],
      result: 'graveSoup', effect: 'graveSoup', known: false }
  ],
  fallbackResult: 'blandMush',
  // Buffs (first buff system). One instance per id; re-eating refreshes the
  // duration (no stacking); different ids coexist. stat 'hpMax' adds amount
  // to CONFIG.player.hpMax for days in-game days. dayMeal: true = the day's
  // ONE stat meal (doc 10): a second dayMeal meal the same day is eaten but
  // grants nothing (text.alreadyAteToast); a new day (clock wrap / C3 rest)
  // clears the slot. kind 'hot' = heal over time: rate HP every tickSec for
  // durationSec REAL seconds (never day-scaled, never meal-capped), gain
  // clamped to hpMax.
  buffs: {
    graveSoup: { label: 'Grave Soup', glyph: 'GS', stat: 'hpMax', amount: 20,
                 days: 1, dayMeal: true },
    blandMush: { label: 'Bland Mush', glyph: 'BM', kind: 'hot', rate: 2,
                 tickSec: 1, durationSec: 30 }
  },
  hint: {
    noMushroomText: 'Mushrooms favor the dead...',   // cryptic by intent (CEMETERY ECOLOGY)
    hintItem: 'wildMushroom'        // shown once per session when the bag holds none
  },
  text: {
    promptCook: 'E - Cook',
    promptBurnt: 'Fire burnt out - E to add Deadwood (fuel)',
    promptLow: 'Fire too low - E to add Deadwood (fuel)',
    promptCampfire: 'E - Warm your hands',                                // CC-C6C: bandit campfire (flavor only)
    campfireToast: "The bandits' fire - it offers nothing to a stranger.",   // CC-C6C: E at a bandit campfire
    refuelToast: 'The fire takes.',
    noFuelToast: 'You need Deadwood to feed the fire',
    addWoodBtn: 'ADD WOOD',
    tooLowToast: 'The fire is too low to cook',
    needThreeToast: 'Add three ingredients',
    missingToast: 'Missing ingredients',
    cookedToast: 'Cooked: {name}',
    learnedToast: 'Recipe learned: {name}',
    interruptToast: 'Cooking interrupted',
    eatToast: 'Ate {name}',
    alreadyAteToast: 'You have already eaten today',   // C2 meal cap (dayMeal buff refused)
    kitToast: 'Campsite kit acquired'
  },
  toastChainSec: 2.0,               // gap between chained toasts (cooked -> learned -> kit)
  // C1 campsite-kit moment: the CAMP HUD button revealed on the first recipe
  // learned; a press enters camp placement (C3, CONFIG.camp / js/camp.js).
  // left / bottom px from the viewport's bottom-left (right of the INV button).
  kitButton: { label: 'CAMP', glyph: '▲', left: 76, bottom: 20 },
  // HUD buff chip row under the bars (icon + remaining time)
  buffHud: { warnSec: 30 }          // chip blinks under this many seconds left
};

// C3 (io/missions/2026-10-06-cc-c3-sleep-tent.md): camps (js/camp.js
// WH_CAMP). A camp is a set of MODULE ROWS - each row = one prop + one
// interact hook ('cook' registers a CONFIG.cooking station row through
// Cooking.addStation, same shape as the bandit fire; 'sleep' opens the TENT
// MENU: Save / Save and Heal). Future modules (storage chest, craft bench,
// warp camp) are new rows + a new hook, nothing else. The deployed kit is
// session-only (C4 save rides after); sites live on the camp manager, never
// in region content, so region swaps never eat them.
window.WH_CONFIG.camp = {
  interactRadius: 2.5,              // m from a sleep module to open the tent menu (cooking feel)
  // One row per visual piece; swapping in the Astrabot wh-campkit GLB is a
  // one-line edit per piece (glb = an assets.js manifest name; tent: null =
  // the procedural dark-canvas A-frame placeholder below).
  assets: {
    // CK1 (Nicko 10-07): kit stone-ring firepit + kit bedroll (node = a
    // whCampkit node, camp.js makePiece). Rollback = glb 'banditCampfire' /
    // 'banditBedroll', no node.
    fire:    { glb: 'whCampkit', node: 'firepit', scale: 1.0 },
    bedroll: { glb: 'whCampkit', node: 'bedroll', scale: 1.0 },
    // C3.1c: the REAL tent = Nicko's Meshy generation (door +Z on the GLB,
    // rotY rows aim it). Scale 2.2 lifts the ~1.9m raw mesh to tent size.
    // CK1: the kit tent stays unwired (optional swap: { glb: 'whCampkit', node: 'tent' }).
    tent:    { glb: 'whTent', scale: 2.2 },
    pegs:    { glb: 'whCampkit', node: 'pegs', scale: 1.6 }   // PROPOSED - Nicko tunes: ring vs the whTent footprint
  },
  tentPlaceholder: { width: 2.0, length: 2.4, height: 1.4, color: 0x2e2a24, poleColor: 0x4a3b2a },
  // The deployable kit (fire + bedroll + tent). offset = [right, back] m in
  // the site frame (back = away from where the player stood when placing);
  // rotY = extra yaw on top of the site yaw (tent: door faces the fire).
  // Sleep modules sit > cooking.interactRadius from the fire so the fire
  // keeps its cook prompt and the bedroll / tent keep theirs.
  modules: [
    { id: 'fire', hook: 'cook', asset: 'fire', offset: [0, 0], rotY: 0,
      station: { kind: 'cookFire', startLit: true } },   // fuel = CONFIG.cooking.fire rules
    { id: 'bedroll', hook: 'sleep', asset: 'bedroll', offset: [3.0, 1.0], rotY: Math.PI / 2 },
    { id: 'tent', hook: 'sleep', asset: 'tent', offset: [0, 3.6], rotY: 0, menuAnchor: true },
    // CK1: decorative kit pegs ring riding the tent spot (hook 'none' = inert)
    { id: 'pegs', hook: 'none', asset: 'pegs', offset: [0, 3.6], rotY: 0 }
  ],
  respawnStepM: 1.5,                // respawn = the menu anchor + this far toward its door (clear of the fire ring)
  // WORLD CAMPS: module rows bound to a fixed world spot (no kit, no deploy).
  // Tutorial anchor: the TENT beside the Region B bandit fire (x 2.5 z -52).
  // C3.1c (Nicko 10-06): tent moved OPPOSITE its first spot - mirrored
  // through the fire center (x 0 -> 5.0, z -49.4 -> -54.6), respawn spot
  // mirrored with it; door rotY -0.77 aims the +Z door AT the fire.
  // The bandit fire itself stays the CONFIG.cooking station - sleep-only here.
  worldCamps: [
    { id: 'banditCamp', regionId: 'darkwood_edge',
      modules: [
        { id: 'tent', hook: 'sleep', asset: 'tent', x: 5.0, z: -54.6, rotY: -0.77 }
      ],
      respawn: { x: 6.0, z: -55.7 }, face: { x: 2.5, z: -52 } }
  ],
  deploy: {
    maxSites: 1,                    // one kit: a new deploy packs up the old site (fire fuel starts fresh)
    maxReachM: 9,                   // ghost stays within this of the player
    startAheadM: 4,                 // ghost start: this far ahead of the player
    pathBand: 2.5,                  // m beyond the dirt path half-width (gather on_path margin)
    // clearances: CONFIG.gather.placement (props / trees / enemies / spawn /
    // node spacing) + CONFIG.scatter.clear (gateM, edgeM) + scatter.keepOut,
    // tested at every module of the kit; other camps count as props
    ghostColor: 0xd23a2a,
    ghostOpacity: 0.45,
    ghostOkColor: 0x3ad26a          // FIX 10-06b: green = placeable right now
  },
  // CC-C11: the chest follows deployed kit pegs (offset in site frame, not world coordinates).
  chest: { offset: [2.2, 1.8], interactM: 2.5, capacity: 24, slotsX: 6, slotsY: 4,
    prompt: 'E - Open the chest', title: 'CAMP CHEST', deposit: 'Deposit', withdraw: 'Withdraw',
    empty: 'Empty', close: 'Close', hint: 'Select a bag slot to deposit; select a chest slot to withdraw. Esc close.' },
  sleepFadeSec: 0.6,                // Save and Heal: fade to black, rest, fade back
  text: {
    prompt: 'E - Camp',
    menuTitle: 'CAMP',
    save: 'Save',
    saveHeal: 'Save and Heal',
    cancel: 'Cancel',
    savedToast: 'Respawn point set',
    restedToast: 'You wake at dawn - Day {day}',
    // CC-C11 (Nicko ruling 2026-10-20): Save and Heal refused before dusk/night
    sleepGate: 'Cannot sleep, it is not yet Dusk/Night.',
    placingToast: 'Choose open ground - click / E to camp, Esc / CAMP to cancel',
    placedToast: 'Camp set up',
    refuseToast: 'No room to camp here - {why}',
    why: {
      edge: 'too close to the edge', gate: 'too close to the gate', path: 'too close to the path',
      keepOut: 'too close to the graveyard', spawn: 'too close to the trailhead',
      tree: 'too close to a tree', prop: 'something is in the way', enemy: 'enemies nearby',
      node: 'too close to forage', camp: 'too close to another camp'
    }
  }
};

// CC-WB1 (doc 42 Part 3, doc 37-C11 lifecycle): war-effort requisition board -
// a CONTRACT LOOP anchored at the hold (region A, south road). The board hands
// out ONE Requisition paper per in-game day; filling it means mining ironOre
// at Redseam (CC-WM1, already live) and turning 6 ore in at the board for a
// coin reward. Module js/wareffort.js (WH_WarEffort); state rides the save
// wrap (B-5), NOT localStorage this round.
window.WH_CONFIG.warEffort = {
  lsKey: 'wh_wareffort_v1',            // unused this round; state rides the save-wrap (B-5)
  boardSeat: { regionId: 'hold_outskirts', x: 5.9, z: -15.5, rotY: 3.14 },
    // PROPOSED, Nicko tunes. Pre-spec lock BY DATA: scratch/cc-wb1/site_scan.js —
    // (6.7,-14.5) chosen then shifted to (5.9,-15.5): > 4.6 m from every
    // regionA static prop (nearest originally 3.34 m bandit row = enemy, 8.09 m
    // statics; clearance re-verified at final seat: nearest static
    // mossBoulder (10.5,-14.5) = 5.36 m), 88.6 m from spawn, on the south
    // road sight-line (churchArchway x=8 z=-58), 566.8 m from the Redseam
    // seam center. Region A is FLAT (WH_GROUND.has = false by design; board
    // sits y=0).
  rotYFacesRoadNorth: true,            // PROPOSED: papers face the incoming traveler
  requisition: {
    itemId: 'warOrder',                // B-2
    oreItemId: 'ironOre',              // CC-WM1 item, already live
    oreRequired: 6,                    // PROPOSED, Nicko tunes (8 veins, ~1 E-dig each)
    reward: { id: 'stolenCoin', count: 3 },  // PROPOSED, Nicko tunes; reward authority = THIS table only (37-C11)
    title: 'War Requisition',
    offerText: 'The garrison wants iron for the war. Bring 6 iron ore to this board.',
    doneText: 'Requisition filled. The quartermaster marks the board.'
  },
  ladder: {                            // CC-WB2 (doc 42 Part 2; all PROPOSED, Nicko tunes)
    basePay: 0.5,                      // coins per quota ore (WB1: 6 ore = 3 coins exactly)
    overBonusStepPct: 10,              // +10% per item over quota
    overBonusCapPct: 100,              // per-item bonus rate cap (+100%)
    repeatQuotaGrowthPct: 50,          // re-post growth per resolution
    repeatQuotaCapMult: 3,             // quota cap = 3x base (18 ore at base 6)
    repeatBasePayStepPct: 15,          // +15% base pay per repeat
    overDoneText: 'Requisition filled. The quartermaster pays a bonus for the extra iron.'
  }
};

// CC-WB3 (doc 42 Part 3, delve-chain loop 2026-11-11): strata requisition
// board - the CC-WB1 board grammar re-dressed at Lord's Hold (region G, the
// war table hub). Idle press hands ONE Strata Requisition paper per in-game
// day; filling it means holding rot-silk >= 4 AND rot-gland >= 2 (CC-C7 delve
// harvest, CONFIG.items rows already live) and turning the exact quota in at
// the board for a coin reward. NO ladder math (WB2 ladder stays WB1-only) and
// no over-band: fixed CONFIG pay per fill. Module js/strataeffort.js
// (WH_StrataEffort, WB1 API surface); state rides the save-wrap (B-5) exactly
// like the war board.
window.WH_CONFIG.strataEffort = {     // CC-WB3; PROPOSED, Nicko tunes
  boardSeat: { regionId: 'lords_hold', x: 6.0, z: -782.0, rotY: 4.712 },
    // PROPOSED, Nicko tunes. Faces west toward the gate lane; 5.67 m clear of
    // both dais braziers, 6.3 m east of the stoneSteps dais, 40.4 m radial
    // (rim 124.5), 78 m off both door planes (z -700 / -948). Verified vs
    // CONFIG regionG props (io/specs/cc-wb3-strata-board-spec.md).
  itemId: 'strataOrder',              // CC-WB3 paper item, row above
  mats: [
    { id: 'rot-silk',  quota: 4 },
    { id: 'rot-gland', quota: 2 }
  ],
  reward: { id: 'stolenCoin', count: 5 },   // PROPOSED, Nicko tunes
  title: 'Strata Requisition',
  offerText: 'The quartermaster wants rot-silk and rot-gland from the delve strata below.',
  doneText: 'Strata requisition filled. The quartermaster marks the board.'
};

// C2 (io/missions/2026-10-05-cc-c2-daynight.md): day/night cycle
// (js/daynight.js WH_DAYNIGHT). One cycle = dawn > day > dusk > night over
// dayLengthSec. Each phase row is the look the phase HOLDS; the first
// blendSec (C3.1: real seconds) of every phase smoothsteps from the previous
// row into it (no pops), the rest holds the row exactly. TUTORIAL LAW: the clock boots
// DORMANT on startPhase (frozen, night = today's look) and only free-runs
// after beginCycle() (C3: the first sleep).
window.WH_CONFIG.dayNight = {
  // CYCLE LAW (Nicko 10-06): dawn 5min > DAY 45min > dusk 5min > NIGHT 45min
  // = 100min total. Day and night are EQUAL on purpose (mechanics, not tone):
  // the Dark Court flip makes night a full playable "day" for that faction
  // (sleep during the day; dusk = the Dark Court's morning), so night can
  // never be short downtime. Dawn/dusk stay short transition sessions.
  // C3.1 SLOW TRANSITION: the first blendSec (90s) of dawn/dusk eases from
  // the neighbouring phase (organic, not the old blendFrac jump); the rest
  // of the window holds its row. Light rows (this block) only - sky panos
  // cross-fade on their own CONFIG (skyPool.blendSec).
  // C4+ dev knob: point a DEV build's dayNight.debugTimeScale at a number to
  // speed the CLOCK (beginCycle still owns the start - no auto-start hatch).
  // FIX 10-06b (real arithmetic, was inverted/double-counted): per-phase
  // seconds dawn 300 + day 2700 + dusk 300 + night 2700 = 6000s = 100min.
  dayLengthSec: 6000,
  daySegmentSec: 2700,              // Nicko tuning: day 2700s / night 2700s real
  startPhase: 'night',              // dormant look (locked until beginCycle)
  order: ['dawn', 'day', 'dusk', 'night'],
  // phase start as a fraction of the cycle; beginCycle() starts at dawn (0)
  // dawn 0..0.05 (300s), day 0.05..0.50 (2700s = 45min),
  // dusk 0.50..0.55 (300s), night 0.55..1.0 (2700s = 45min)
  bounds: { dawn: 0, day: 0.05, dusk: 0.5, night: 0.55 },
  blendFrac: 0.5,                   // LEGACY pano window; replaced by blendSec below
  blendSec: 90,                     // C3.1: the slow transition (real seconds)
  // Row keys: hemi colors + hemiFillMult (x hemiBaseIntensity x region
  // ambientLightLevel x regionBFillMult), the ONE directional (moon by
  // night, sun by day - no new light objects) color / intensity / azimuth /
  // elevation, exposureMult (x renderer.toneMappingExposure), fog per region
  // id (cem* = regionA cemeteryFog ramp target), sky dome colors, star
  // visibility, sky disc (moon / sun sprite) colors + opacity.
  phases: {
    // NIGHT = TODAY'S APPROVED LOOK. Every value is copied verbatim from
    // CONFIG.lighting / regionA / regionA.cemeteryFog / regionB / sky; mults
    // are exactly 1. daynight.js verifies this match at boot (console.warn).
    night: {
      hemiSkyColor: 0x4a5a80, hemiGroundColor: 0x16181e, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.9, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 1.0,
      fog: {
        hold_outskirts: { color: 0x9aa0a3, density: 0.012, cemColor: 0x7f8ea6, cemDensity: 0.030 },
        darkwood_edge: { color: 0x6f7477, density: 0.024 },
        // CC-C2 Region C deep-forest fog (night = CONFIG.regionC verbatim). PROPOSED, Nicko tunes
        forest_of_the_old_king: { color: 0x59625b, density: 0.033 }
      },
      zenithColor: 0x070a18, horizonBand: 0x2b3350, horizonGlow: 0x8f98ad,
      stars: 1.0,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 1.0
    },
    // dawn: low cold-rose light from the east, mist still heavy
    dawn: {
      hemiSkyColor: 0x6a6878, hemiGroundColor: 0x1e1c1e, hemiFillMult: 1.5,
      lightColor: 0xc9a88e, lightIntensity: 0.8, azimuthDeg: 80, elevationDeg: 10,
      exposureMult: 1.0,
      fog: {
        hold_outskirts: { color: 0xa29a98, density: 0.011, cemColor: 0x8e8c9c, cemDensity: 0.026 },
        darkwood_edge: { color: 0x77736f, density: 0.021 },
        // CC-C2 Region C deep-forest fog (night = CONFIG.regionC verbatim). PROPOSED, Nicko tunes
        forest_of_the_old_king: { color: 0x5f6660, density: 0.030 }
      },
      zenithColor: 0x262c44, horizonBand: 0x6e5e66, horizonGlow: 0xa8948a,
      stars: 0.35,
      discColor: 0xf0d2b0, discGlowColor: 0xb08870, discOpacity: 0.9
    },
    // day: pale overcast daylight - gothic but readable, darkwood ash/olive
    // palette (no blue sky, no saturation)
    day: {
      hemiSkyColor: 0x8a929c, hemiGroundColor: 0x2a2a22, hemiFillMult: 2.4,
      lightColor: 0xd8d0bc, lightIntensity: 1.25, azimuthDeg: 160, elevationDeg: 50,
      exposureMult: 1.0,
      fog: {
        hold_outskirts: { color: 0xa4a8a6, density: 0.008, cemColor: 0x9aa1a8, cemDensity: 0.020 },
        darkwood_edge: { color: 0x80857f, density: 0.017 },
        // CC-C2 Region C deep-forest fog (night = CONFIG.regionC verbatim). PROPOSED, Nicko tunes
        forest_of_the_old_king: { color: 0x6a716a, density: 0.025 }
      },
      zenithColor: 0x56606e, horizonBand: 0x868d92, horizonGlow: 0xa9adab,
      stars: 0.0,
      discColor: 0xf0e6cc, discGlowColor: 0xb8ae94, discOpacity: 0.85
    },
    // dusk: sun sinks west, bruised-rose band, mist thickens back
    dusk: {
      hemiSkyColor: 0x5e5a6e, hemiGroundColor: 0x1a181c, hemiFillMult: 1.4,
      lightColor: 0xc0907a, lightIntensity: 0.75, azimuthDeg: 250, elevationDeg: 10,
      exposureMult: 1.0,
      fog: {
        hold_outskirts: { color: 0x9c9496, density: 0.012, cemColor: 0x868aa0, cemDensity: 0.027 },
        darkwood_edge: { color: 0x726e6c, density: 0.022 },
        // CC-C2 Region C deep-forest fog (night = CONFIG.regionC verbatim). PROPOSED, Nicko tunes
        forest_of_the_old_king: { color: 0x5c625c, density: 0.031 }
      },
      zenithColor: 0x1c2238, horizonBand: 0x664e58, horizonGlow: 0x9c8478,
      stars: 0.25,
      discColor: 0xe8b894, discGlowColor: 0xa07060, discOpacity: 0.9
    }
  },
  // CC-C8 ALWAYS-DARK (io/missions/2026-10-12-cc-c8-rotmother-den.md sec 4):
  // an area with a constant row shows it EVERY frame it is the sky area -
  // no clock math (the clock itself runs on untouched: dormant law intact).
  // daynight.js reads it in one branch (areaId === a constantPhases key).
  // Same keys as a phase row. rot_den: moon 0, hemi fill = the region's
  // ambientLightLevel 0.06 (mult 1: the 0.06 is not applied twice), exposure
  // 0.75, a near-black dome underlay (no pano paints it), stars 0.15, disc
  // 0.2; fog = regionD's own row. All PROPOSED, Nicko tunes.
  constantPhases: {
    rot_den: {
      hemiSkyColor: 0x1a2030, hemiGroundColor: 0x08090b, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.75,
      fog: { rot_den: { color: 0x05070a, density: 0.12 } },
      zenithColor: 0x020305, horizonBand: 0x05070a, horizonGlow: 0x0a0d12,
      stars: 0.15,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.2
    },
    /* CC-C8-EXT constant rows for the six underworld strata — the clock keeps
       running outside; these interiors hold ONE look every frame
       (see doc 64 registry note). */
    // Veil Crypt (E): first underworld stratum, above the Galleries.
    // No pano or moon; faint stars sit behind the concept-08 smog.
    // All PROPOSED, Nicko tunes.
    veil_crypt: {
      hemiSkyColor: 0x171c2a, hemiGroundColor: 0x07080a, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.75,
      fog: { veil_crypt: { color: 0x0a0810, density: 0.13 } },
      zenithColor: 0x02030a, horizonBand: 0x080612, horizonGlow: 0x0e0a16,
      stars: 0.15,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.2
    },
    // Veil Galleries (F): one stratum below the Crypt, colder and darker.
    // No pano or moon; stars stay faint behind concept-08 smog.
    // All PROPOSED, Nicko tunes.
    veil_galleries: {
      hemiSkyColor: 0x151a26, hemiGroundColor: 0x06070a, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.75,
      fog: { veil_galleries: { color: 0x0a0810, density: 0.145 } },
      zenithColor: 0x020307, horizonBand: 0x070510, horizonGlow: 0x0d0914,
      stars: 0.12,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.15
    },
    // Armory Deep (I): E-family dark pocket below the open garrison.
    // No pano or moon; faint stars remain behind concept-08 smog.
    // All PROPOSED, Nicko tunes.
    armory_deep: {
      hemiSkyColor: 0x171c2a, hemiGroundColor: 0x07080a, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.75,
      fog: { armory_deep: { color: 0x0a0810, density: 0.13 } },
      zenithColor: 0x02030a, horizonBand: 0x080612, horizonGlow: 0x0e0a16,
      stars: 0.15,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.2
    },
    // Spire Approach (J): deeper than the Galleries, above the Vaults.
    // No pano or moon; stars hide behind concept-08 citadel smog.
    // All PROPOSED, Nicko tunes.
    veil_spire_approach: {
      hemiSkyColor: 0x141823, hemiGroundColor: 0x050609, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.72,
      fog: { veil_spire_approach: { color: 0x0a0810, density: 0.15 } },
      zenithColor: 0x010305, horizonBand: 0x06040d, horizonGlow: 0x0b0812,
      stars: 0.10,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.12
    },
    // Tithe Vaults (K): one stratum below the Spire Approach.
    // No pano or moon; faint stars sit behind concept-08 smog.
    // All PROPOSED, Nicko tunes.
    tithe_vaults: {
      hemiSkyColor: 0x12161f, hemiGroundColor: 0x040507, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.72,
      fog: { tithe_vaults: { color: 0x0a0810, density: 0.16 } },
      zenithColor: 0x010204, horizonBand: 0x050309, horizonGlow: 0x090610,
      stars: 0.08,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.10
    },
    // The Remains (L): deepest stratum, duel chamber below the Vaults.
    // No pano or moon; stars barely show behind concept-08 smog.
    // All PROPOSED, Nicko tunes.
    the_remains: {
      hemiSkyColor: 0x101419, hemiGroundColor: 0x030406, hemiFillMult: 1.0,
      lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30,
      exposureMult: 0.70,
      fog: { the_remains: { color: 0x090710, density: 0.17 } },
      zenithColor: 0x010203, horizonBand: 0x040307, horizonGlow: 0x080510,
      stars: 0.06,
      discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0.08
    }
  },
  // C2b (io/missions/2026-10-06-cc-c2b-skydome-pools.md) WH_SKYPOOL: painted
  // panorama pools for the dome (js/daynight.js SkyPool). Each phase shows
  // one pano from its pool, cross-faded over the same blendSec window as
  // the lighting (C3.1: real seconds, skyPool.blendSec). Paths are repo-relative and ride WH_ASSETS.resolveUrl like
  // the GLBs. 10-06 HD re-emit (Nicko: skies too pixelated): NO posterize,
  // smooth 2048x682 JPEGs; night = v2 moon-contract set (moon LOW-LEFT,
  // yawDeg 29). Bottom edge = horizon, top = zenith. Rows above = LIGHTING;
  // panos only paint.
  pools: {
    day: ['art-direction/textures/sky2v2/sky2-day.jpg',       // approved A
          'art-direction/textures/sky2v2/sky3-dayB.jpg',
          'art-direction/textures/sky2v2/sky3-dayC.jpg',
          'art-direction/textures/sky2v2/sky3-dayD.jpg'],
    dawn: ['art-direction/textures/sky2v2/sky2-dawn.jpg',     // approved A
           'art-direction/textures/sky2v2/sky3-dawnB.jpg',
           'art-direction/textures/sky2v2/sky3-dawnC.jpg',
           'art-direction/textures/sky2v2/sky3-dawnD.jpg'],
    dusk: ['art-direction/textures/sky2v2/sky2-dusk.jpg',     // approved A
           'art-direction/textures/sky2v2/sky3-duskB.jpg',
           'art-direction/textures/sky2v2/sky3-duskC.jpg',
           'art-direction/textures/sky2v2/sky3-duskD.jpg'],
    night: ['art-direction/textures/sky2v2/sky2v2-nightA.jpg',
            'art-direction/textures/sky2v2/sky2v2-nightB.jpg',
            'art-direction/textures/sky2v2/sky2v2-nightC.jpg']
  },
  // ROTATION LAW (Nicko 10-06): variant = (dayCounter + areaPoolOffset[area])
  // % pool.length; dayCounter = full clock wraps since beginCycle (0 on the
  // dormant night). One new offset per new area.
  // 10-06 Nicko PLAYTEST: offsets zeroed - EVERY area plays the same variant
  // per day (day 1 = A skies everywhere, then B, C, D by day count) so each
  // cycle's feel can be judged directly. Restore per-area variation by
  // setting distinct offsets (e.g. darkwood_edge: 2).
  areaPoolOffset: { hold_outskirts: 0, darkwood_edge: 0, forest_of_the_old_king: 0 },   // CC-C2: C row PROPOSED, Nicko tunes
  skyPool: {
    // pano yaw (deg about +y). 10-06 moon reposition: v2 night panos carry
    // the moon at u ~0.22 (LOW-LEFT contract); yaw 29 puts it ~18 deg to the
    // player's LEFT of the path (-z) - "above the graveyard path" (Nicko).
    // All three v2 nights use the same contract so one yaw lines them up.
    yawDeg: 29,
    blendSec: 90,                   // C3.1: pano cross-fade = the slow transition
    areaFadeSec: 1.0,               // region-cross variant swap (brief value)
    preloadFrac: 0.2,               // load the NEXT phase's pano in this first part of a phase
    cacheMax: 6                     // textures alive at once (LRU, shown panos pinned)
  }
};

// Stage 2 (Nicko 10-05): static gather nodes (js/gather.js WH_GATHER).
// Placements live in regionA/regionB .nodes. E harvests the nearest READY
// node within interactRadius; a full inventory refuses (node stays ready).
// A harvested node goes dormant and respawns after its type's timer; each
// node's timer is jittered by respawnJitterPct so nodes never sync.
//
// RESPAWN ECONOMY - REAL-GAME DESIGN INTENT (persist this):
//   common node types respawn once per REAL DAY, rare types once per REAL
//   WEEK, by wall-clock time regardless of in-game time; a respawning node
//   reappears at a RANDOM free spot from its type's placement pool (the
//   region's nodes entries of that type, reshuffled). The day/week economy
//   arrives with the real game. THIS PLAYTEST runs economy.mode 'playtest':
//   per-type respawnSec on the game clock, nodes return in place.
//   mode 'real' = realSec[rarity] on Date.now() (model wired, not tuned).
window.WH_CONFIG.gather = {
  interactRadius: 1.6,              // same as pickupRadius feel
  promptText: 'E - Gather {name}',
  gatherToast: 'Gathered {name} x{n}',
  fullText: 'Inventory full',       // reuse
  respawnJitterPct: 15,             // +-% per respawn so timers stagger (AC S4)
  fadeSec: 0.5,                     // harvest fade-out / respawn fade-in (scale + sink)
  economy: {
    mode: 'playtest',               // 'playtest' (respawnSec, game clock) | 'real' (realSec, wall clock)
    realSec: { common: 86400, rare: 604800 },   // REAL DAY / REAL WEEK
    reshuffleOnRespawn: false       // real game: true (random free pool spot); playtest: in place
  },
  // !!! PLAYTEST AID ONLY (Nicko 10-05 canon) !!! In the REAL game gather
  // nodes DO NOT GLOW - players spot them by eye among the bushes / grass
  // added later. playtestGlow true adds a small unlit marker mesh with a
  // bob/pulse above each READY node. NO per-node PointLights, ever (the
  // light budget stays: 4 pool lights + flame cards + player lights).
  // Real game = playtestGlow false: nodes render as plain flora-adjacent
  // props. The base mesh here is a PLACEHOLDER for the later bush/grass art
  // asset mission - node meshes are not this order's art pass.
  playtestGlow: true,
  // Node placement rules (the scratch/gen_gather_nodes.py clearances, now
  // CONFIG rows). C3 camp deploy reads these SAME rows (CONFIG.camp.deploy)
  // with CONFIG.scatter.clear (gate / rim) + scatter.keepOut + the dirt path.
  placement: {
    treePropM: 4,                   // to a tree-class prop (treeMatch on the asset name)
    propM: 3,                       // to any other prop
    treeMatch: 'tree|oak|ash|yew|witchwood',
    enemyM: 5,                      // to an enemy spawn
    spawnM: 6,                      // to the region's player spawn
    spacingM: { hold_outskirts: 9, darkwood_edge: 6 }   // node-to-node, per region
  },
  marker: {
    size: 0.16,                     // octahedron radius (m, times node scale)
    height: 0.95,                   // float height over the ground (m)
    bobAmp: 0.08,                   // m
    bobHz: 0.6,
    pulseMin: 0.75,                 // scale pulse trough (fraction)
    pulseHz: 1.1
  },
  base: {
    radius: 0.32,                   // placeholder clump radius (m, times node scale)
    height: 0.28,
    colorMult: 0.45                 // clump tint = glowColor * this (dull, flora-adjacent)
  },
  nodeTypes: {
    herbBundle:      { name: 'Herb Bundle', rarity: 'common', yield: { id: 'forestHerb', count: 2 },
                       respawnSec: 90, glowColor: 0x66aa55, scale: 1.0 },
    deadwoodPile:    { name: 'Deadwood Pile', rarity: 'common', yield: { id: 'deadwood', count: 3 },
                       respawnSec: 180, glowColor: 0x998855, scale: 1.0 },
    mushroomCluster: { name: 'Mushroom Cluster', rarity: 'common', yield: { id: 'wildMushroom', count: 2 },
                       respawnSec: 120, glowColor: 0xaa99cc, scale: 0.85 },
    graveMoss:       { name: 'Grave Moss', rarity: 'common', yield: { id: 'graveMoss', count: 2 },
                       respawnSec: 150, glowColor: 0x77bbaa, scale: 1.0 },
    bonePile:        { name: 'Bone Pile', rarity: 'common', yield: { id: 'boneShard', count: 2 },
                       respawnSec: 150, glowColor: 0xbbbbaa, scale: 1.0 }
      // CC-WM1 redseam: the rich iron seam gather node (doc 42 Part 5 entry tier).
      ,ironVein:        { name: 'Iron Vein', rarity: 'common', yield: { id: 'ironOre', count: 3 },
                       respawnSec: 240, glowColor: 0x8f5a33, scale: 1.15 }
  }
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
  nativeHand: { longsword: 'right', roundShield: 'left', magicGlove: 'left', torch: 'left',
                dagger: 'right' },
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
                perHand: true, windupScale: 1.8 },
  // R-64.3 (Nicko 10-09) ITEM-STAT registry: gear pieces may carry
  // stats: { magicDefense: <fraction> } (pct: true = shown as a percent).
  // WH_LEVEL.magicDefense() totals it over the equipped hands. INERT v1:
  // no gear ships with it and nothing consumes it - the future hook is the
  // enemy-caster damage branch (enemy casters do not exist yet; that branch
  // will read WH_LEVEL.magicDefense() when they land - not built here).
  itemStats: {
    magicDefense: { label: 'Magic Defense', pct: true }
  }
};

// R-64.4 (Nicko 10-09) starting classes, picked on the NEW GAME path only
// (CONTINUE never re-kits). Every row is BUILT FROM the single-kit rows
// above - inventory.startingItems, equip.defaultHands, belt.defaultSpells,
// actionbar.defaults stay the data source AND the no-class fallback (that
// fallback = today's exact kit). kit = grid rows (hands are pulled OUT of
// it at boot), hands = { right, left }, spells = the learned-spell belt
// (null = not known), belt = the action-bar defaults (null = empty slot).
// lines = the two picker text lines (hands | kit + spell knowledge).
// Wanderer casts nothing v1 (right hand = attack chain); magic is the
// Magician's lane. Bandage x1 both; actionbar.pickerExclude unchanged.
window.WH_CONFIG.startingClasses = (function (C) {
  var KIT = C.inventory.startingItems, HANDS = C.equip.defaultHands;
  var SPELLS = C.belt.defaultSpells, BAR = C.actionbar.defaults;
  function kitRow(id, nth) {        // the nth (0-based) startingItems row of id
    return KIT.filter(function (r) { return r.id === id; })[nth || 0];
  }
  function barSlot(id) {            // the actionbar.defaults entry for id
    return BAR.filter(function (e) { return e.id === id; })[0] || null;
  }
  var none = SPELLS.map(function () { return null; });
  return {
    order: ['wanderer', 'magician'],
    wanderer: {
      label: 'Wanderer',
      lines: ['Longsword right, shield left', 'Torch, bandage - no spells'],
      kit: [kitRow('longsword'), kitRow('roundShield'), { id: 'torch', count: 1 }, kitRow('bandage')],
      hands: { right: HANDS.right, left: barSlot('roundShield').id },
      spells: none,
      belt: [null, null, barSlot('roundShield'), barSlot('torch'), null]
    },
    magician: {
      label: 'Magician',
      lines: ['Dagger right, magic glove left', 'Bandage - knows Firebolt + Radiance'],
      // DAG (2026-10-09): the dagger is a CLASS-EXTRA row (not in
      // inventory.startingItems, so the no-class fallback kit is unchanged).
      // MAGICLASS (2026-10-11): dagger in the right hand, one glove left (the
      // second glove stays in the grid); the left glove casts the off binding
      // (slot 0 = Firebolt) with the mirrored Cast1H_L shot.
      kit: [{ id: 'dagger', count: 1 }, kitRow('magicGlove', 0), kitRow('magicGlove', 1),
            kitRow('bandage')],
      hands: { right: 'dagger', left: HANDS.left },
      spells: SPELLS.slice(),
      belt: [barSlot(SPELLS[0]), barSlot(SPELLS[1]), null, null, null]
    }
  };
})(window.WH_CONFIG);

// Inventory screen (DOM modal). While open, player movement/combat input is
// suspended (the world keeps running).
window.WH_CONFIG.inventoryUI = {
  openKey: 'KeyI',
  closeKeys: ['KeyI', 'Escape'],
  dropKey: 'KeyG',                  // drop 1 of the selected stack; Shift+G = whole stack
  pickupKey: 'KeyE',                // world: collect the nearest item entity in pickupRadius
  useKey: 'KeyE',                   // C1: screen open = eat the selected food stack
  useLabel: 'EAT',                  // C1: grid use button (touch path)
  gridCols: 6,                      // 24 slots -> 6 x 4
  toastSeconds: 1.8,                // "Dropped X x1" / "Inventory full" toast lifetime
  // Order B: clickable HUD button, same toggle as the I key. left / bottom
  // are px from the viewport's bottom-left corner.
  openButton: { enabled: true, label: 'INV', left: 16, bottom: 20 }
};

// QJR-1 journal core (Nicko MorROWIND order 2026-11-06; all PROPOSED,
// Nicko tunes). Sits in the HUD row right of INV (16) and CAMP (76).
window.WH_CONFIG.journal = {
  button: { glyph: '☰', label: 'JOURNAL', left: 152, bottom: 20 },
  openKey: 'KeyJ',
  text: {
    title: 'JOURNAL',
    empty: 'No entries yet. The road will give you words.',
    dayStamp: 'Day {day} - {source}',
    seedTitle: "The farmer's daughter",
    seedBody: "Farmer Aldric: the Old King's Barrow, west past the dead trees. Bring her home.",
    seedSource: 'Farmer Aldric',
    toastNew: 'Journal: ',
    hint: 'Esc close',
    searchPlaceholder: 'Search the journal...',
    searchNoMatch: 'Nothing in the journal matches.'
  },
  topics: {
    // QJR-3: remaining content voices (board clerk + camp folk), A1 verbatim
    // from io/specs/qjr-3-content-wiring-spec.md.
    requisition: {
      id: 'war-effort-requisition',
      title: 'Requisition papers',
      source: 'The quartermaster',
      body: "I took requisition papers from the war board. The quartermaster wants iron for the front - full quota pays coin, excess pays a bonus. The garrison's hunger grows with every report from the pass."
    },
    firstFill: {
      id: 'war-effort-first-fill',
      title: 'Iron delivered',
      source: 'The quartermaster',
      body: 'Haul delivered at the war board. The quartermaster marked the tally and paid coin for the quota, a bonus for the extra. The garrison feeds the forge, the forge feeds the war.'
    },
    campRest: {
      id: 'camp-first-rest',
      title: 'Taken in at the camp',
      source: 'Camp folk',
      body: "The camp folk shared their fire and patched my wounds - for coin or kindness, they did not say. They whisper about the barrow west of the dead trees, the Old King's Barrow, where the mist keeps its own accounts."
    },
    rescue: {
      id: 'rescue-findDaughter',
      title: "The farmer's daughter",
      body: 'Rescue: I found Aldric\'s daughter by the stone sarcophagus in the Old King\'s Barrow. She is safe and walking to her father\'s farm.',
      source: "Aldric's daughter"
    },
    complete: {
      id: 'quest-findDaughter-complete',
      title: "The farmer's daughter",
      body: "Aldric: 'She is home, hunter. You have given me back my world.' The road is quiet again.",
      source: 'Farmer Aldric'
    },
    // CC-AF1 camp folk crossing voices (verbatim from
    // io/specs/cc-af1-camp-affinity-spec.md A; APPEND ONLY, single-line strings)
    campAffinityGood: {
      id: 'camp-affinity-good',
      title: 'The honored fire',
      body: 'The camp folk tend my fire a little brighter - word of good deeds travels ahead of me. The garrison claps shoulders on my way through; the moors keep their distance.',
      source: 'Camp folk'
    },
    campAffinityDark: {
      id: 'camp-affinity-dark',
      title: 'The watched fire',
      body: 'The camp folk keep to their tents now. My fire burns low and red, and the shadows between the wagons watch me back. Word of my deeds travels too - the wrong kind.',
      source: 'Camp folk'
    },
    // CC-WB3 (io/specs/cc-wb3-strata-board-spec.md): the strata board's single
    // journal topic, requisition voice ~ QJR-3's requisition/firstFill rows.
    // ONE topic, appended on award AND on fill (js/strataeffort.js).
    strata: {
      id: 'strata-requisition',
      title: 'Strata requisition',
      source: 'The quartermaster',
      body: 'I took a strata requisition from the Lord\'s Hold board. The quartermaster wants rot-silk and rot-gland from the delve strata below the rot nests - full quota pays coin. Whatever sleeps in the deeper strata stirs when it is robbed.'
    }
  }
};

// QJR-4 BESTIARY CODEX (io/specs/qjr-4-bestiary-spec.md, 2026-11-07; all
// PROPOSED, Nicko tunes) - the hunter's own field book, one codex page per
// enemy type. Rides the J panel (buttonless); page strings are drafted per
// the ledger law (doc 44/51: no creditor, no signatory, no terms; the
// pact/tithe/Veil-witnessed-fact rule) in field-note voice. Art anchor:
// concept-06-siege-council (sacred-archive codex) + concept-01-darkwood
// (beast field-guide in a hunter's hand). Accents map to the EXISTING
// palette tokens via CSS classes .codex-accent-<accent> (style.css EOF).
window.WH_CONFIG.journal.bestiary = {
  buttonless: true,           // no own HUD button, rides the J panel (js/journal.js tab row)
  killToastEvery: 5,          // toast on first kill + every 5th kill of a type
  text: {
    tabBestiary: 'BESTIARY',
    tabJournal: 'JOURNAL',
    killsLabel: 'slain:',      // lowercase in-world voice
    seenStamp: 'Day {day}',
    hiddenFooter: '{n} beasts remain undescribed.',
    lockedTitle: 'Unknown beast',
    lockedSigil: '—',
    searchPlaceholder: 'Search the bestiary...',
    nomatch: 'Nothing in the bestiary matches.',
    killToast: 'Bestiary: {title} - slain x{n}',
    killToastTitleUnseen: 'Bestiary: first kill - {title}',
    killEveryLabel: 'Bestiary: {title} - slain x{n}',
    seenToast: 'Bestiary: witnessed - {title}',
    hint: 'Esc close'
  },
  // The ten codex pages keyed by enemy type (spec 2.2/2.8). Ledger law:
  // killed as witnessed fact only; tithes/pacts named only as things seen,
  // never as terms owed to a named creditor.
  entries: {
    bandit: { title: 'The Sloppy Blade', sigil: '†', accent: 'bone',
      page: 'A moor man with a knife he does not clean. He fights for coin and takes it in tithes I have seen collected at crossroads. When his blade fails he swings harder, not smarter.' },
    ghoul: { title: 'Grave-Hungry Ghoul', sigil: '☠', accent: 'ash',
      page: 'It digs where the ground smells wrong and eats what the ground gives. Wounds weep rot; I burn the clothes after. It hops the fence-lines at dusk, always hungry, never full.' },
    wolf: { title: 'Rot Wolf', sigil: '❂', accent: 'amber',
      page: 'A wolf wearing the blight like a second pelt. They run in a loop around the carrion fields and pull no one down alone. The pack turns as one head.' },
    coven: { title: 'Coven Witch', sigil: '✶', accent: 'crimson',
      page: 'She keeps the old fire under her tongue and will not come to arm\'s length. The bolt she throws burns the same colour as the Veil storms I watched as a boy. I keep my shield raised and my distance longer.' },
    zealot: { title: 'Veil-Touched Zealot', sigil: '☀', accent: 'crimson',
      page: 'It walked into the Veil mist and walked out still chanting. It calls its wounds proof of keeping. Whatever pact it keeps, it keeps it out loud and alone.' },
    rotmother: { title: 'The Rot Mother', sigil: '✿', accent: 'crimson',
      page: 'She nests where the rot is thickest and the land goes quiet around her. I have seen her spawn walk the nests she keeps. When she falls the stains stay in the ground for days.' },
    rotspawn: { title: 'Rot Spawn', sigil: '✿', accent: 'ash',
      page: 'Small, quick, and born already rotten. They scatter when their mother is struck and return when she does not. Best kept burning at the nest\'s edge.' },
    scarreader: { title: 'The Scar-Reader', sigil: '〰', accent: 'crimson',
      page: 'It reads the cut lines on its own arms like a ledger and pays in the same coin. I saw it mark a fresh scar before striking. Its slams land wide, so I roll through, not away.' },
    tithecaptain: { title: 'The Tithe Captain', sigil: '⚖', accent: 'crimson',
      page: 'I have watched its carts take grain and iron at the crossroads and leave receipts no one can read. It counts everything twice. I have never seen it pay.' },
    lastchancel: { title: 'The Last Chancel', sigil: '♆', accent: 'crimson',
      page: 'A chancel that outlived its congregation, and something that wears it like a robe. At its threshold I have heard the tithes being counted. I have not yet stepped inside.' }
  }
};

// CC-AF1 CAMP AFFINITY (docs 12 + 11 + 44/45; Nicko MorROWIND order
// 2026-11-07) - doc 12's single visible good<->evil axis as a deed-driven
// standing score, js/affinity.js WH_AFF. The kit camp fire tints with the
// tier; ambient world fires stay amber. EVERY NUMBER IS PROPOSED, NICKO
// TUNES (doc 12 ruling pass working values).
window.WH_CONFIG.affinity = {
  // doc 12 ruling pass working values (PROPOSED, Nicko tunes): |s| >= 80 sworn,
  // >= 50 honored/feared, else neutral. tier() = first row (desc) with minScore <= s.
  ladder: [
    { id: 'sworn-dark',  minScore: -80, label: 'Sworn of the Dark', fire: 0xff2a2a },
    { id: 'feared',      minScore: -50, label: 'Feared', fire: 0xff5a3c },
    { id: 'neutral',     minScore: -49, label: 'Neutral', fire: null },
    { id: 'honored',     minScore: 50,  label: 'Honored', fire: 0xffdf8a },
    { id: 'sworn-light', minScore: 80,  label: 'Sworn of the Dawn', fire: 0xfff2c8 }
  ],
  // deeds: event id -> delta. Kill ids mirror CONFIG.leveling.xpSources keys;
  // every re-armed kill pays again (the XP law). rescue/warEffortFill repeat by
  // their own event semantics (rescue is once by quest state; the fill is per day).
  deeds: {
    rescue_findDaughter: 25,   // witnessed good deed: the daughter home
    warEffortFill: 10,          // the garrison is the light war's belly
    strataFill: 10,             // CC-WB3: the delve harvest feeds the same front (same delta as warEffortFill)
    kill_ghoul: 4,              // blight cleansing
    kill_rotmother: 4,
    kill_rotspawn: 2,
    kill_scarreader: 8,         // CC-H4: the hunter's trade vs the Fall's machinery
    kill_wolf: 0,               // wildlife; row explicit so the map is total
    kill_bandit: -4,            // moor men of the underworld kin; unwarranted blood
    kill_coven: 8               // the hunter's trade against the covens
  },
  clamp: 100,                   // score hard clamp [-100, +100] (PROPOSED)
  campTint: { enabled: true },   // kit fires only; ambient world fires stay amber
  text: {
    secTitle: 'STANDING',
    scoreFmt: '{score} standing',
    barNeutral: '#8a8577'       // v1 bar fill follows tier via cls, see C-UI
  }
};


// L1 (2026-10-07, io/missions/2026-10-07-cc-l1-leveling.md) LEVELING -
// js/leveling.js WH_LEVEL. Layer 1 (doc 07): XP -> character level -> 5
// stat points per level -> the NINE stats (list LOCKED). Layer 2 (doc 18):
// three skill lines rank by use, per-rank primary passives only (NO tier-up
// menus this round). LEVEL DOES NOT SCALE POWER (doc 07 lock): the level is
// a point budget; nothing reads the level number except the point grant.
// EVERY NUMBER BELOW IS PROPOSED, NICKO TUNES (doc 07 RULING PASS: XP
// budgets / stat caps are GDD tuning against a playable build). Level 1
// with 0 points spent = today's numbers exactly (all bonuses start at 0).
window.WH_CONFIG.leveling = {
  pointsPerLevel: 5,                // doc 07 LOCKED (5 stat points per level)
  maxLevel: 50,                     // PROPOSED ceiling (XP past it just banks)
  // xpForNext(level) = round(base * level ^ exp)   PROPOSED, Nicko tunes
  //   L1->2 100, L2->3 283, L3->4 520, L4->5 800, L5->6 1118, L10->11 3162
  xpCurve: { base: 100, exp: 1.5 },
  // XP per source (PROPOSED, Nicko tunes). Kills key 'kill_' + enemy.type;
  // discover_* = first-of-kind, once per character (ids kept in the save).
  // No quest XP (L1 ruling).
  xpSources: {
    kill_bandit: 35,                // bandit hpMax 70
    kill_ghoul: 25,                 // ghoul hpMax 45
    kill_wolf: 20,                  // CC-C5: wolf hpMax 38 (same ~0.53 x hpMax law)
    kill_rotmother: 240,            // CC-C7: rotmother hp 460 (same law; every re-armed kill pays again)
    kill_rotspawn: 14,              // CC-C7: rotspawn hp 26 (withered on her death = no kill, no XP)
    kill_scarreader: 200,           // CC-H4: scarreader hp 400 (the ~0.5 x hpMax law)
    kill_coven: 30,                 // CC-EC1: coven hp 60 (same ~0.5 x hpMax law)
    gather: 5,                      // per harvested node
    cook_meal: 15,                  // per finished cook (recipe or Bland Mush)
    recipe_learn: 40,               // the first cook of a recipe (stacks with cook_meal)
    discover_region: 50,            // first entry into a region (the boot region is pre-known)
    discover_node: 10,              // first harvest of each gather node type
    discover_foe: 25                // first kill of each enemy type (stacks with kill_*)
  },
  // L1.1 (Nicko 10-07 tuning: pools 1/pt, stat renames, Wisdom rebuilt):
  //   health    +1 max HP per point            (100 base, buffs stack on top)
  //   stamina   +1 max stamina per point       (100 base)
  //   focus     +1 max focus per point         (100 base)
  //   speed     +1% walk / sprint per point    (cap +25%; roll / backstep untouched)
  //   dexterity +1% melee crit per point       (cap 50%; crit = x critMult damage)
  //   defense   +1% damage reduction per point (cap 60%, mission row)
  //   wisdom    +1% magic damage AND +5% magic regen per point. History: L1.1
  //             (doc 15 canon) paired damage with +1% magic defense; R-64.1
  //             (Nicko 10-09) swapped the second half to regen - magic defense
  //             is now an ITEM stat (CONFIG.equip.itemStats, gear total via
  //             WH_LEVEL.magicDefense()). Regen = focusRegenPerSec * (1 + 0.05
  //             * wisdomPoints) * other mults; the Focus stat stays pool-only.
  //   carry     +5% stack size per point       (stacks without their own stackCap: 60 -> 63 -> 66..)
  //   luck      +1% extra drop / gather roll per point (cap 50%)
  stats: ['health', 'stamina', 'focus', 'speed', 'precision', 'ward', 'wisdom', 'carry', 'luck'],
  statCurves: {
    health:    { label: 'Health',       perPoint: 1,    cap: null, caption: '+{v} max HP' },
    stamina:   { label: 'Stamina',      perPoint: 1,    cap: null, caption: '+{v} max stamina' },
    focus:     { label: 'Focus',        perPoint: 1,    cap: null, caption: '+{v} max focus' },
    speed:     { label: 'Speed',        perPoint: 0.01, cap: 0.25, caption: '+{pct}% move speed' },
    precision: { label: 'Dexterity',    perPoint: 0.01, cap: 0.50, caption: '{pct}% crit chance' },
    ward:      { label: 'Defense',      perPoint: 0.01, cap: 0.60, caption: '-{pct}% damage taken' },
    wisdom:    { label: 'Wisdom',       perPoint: 0.01, cap: null, caption: '+{pct}% magic damage, +{pct}% magic regen',
                 magicRegenPerPoint: 0.05 },
    carry:     { label: 'Carry Weight', perPoint: 0.05, cap: null, caption: '+{pct}% stack size' },
    luck:      { label: 'Luck',         perPoint: 0.01, cap: 0.50, caption: '{pct}% bonus drop roll' }
  },
  critMult: 1.5,                    // PROPOSED: precision crit damage multiplier
  critFlashSeconds: 0.18,           // gold screen-edge flash on a crit (#wh-block-flash.crit)
  // Skill lines (doc 15 canonical lines for the three prototype verbs; the
  // brief's working names longsword / block / spell school map to them).
  // id -> { name, perUse rank XP per use kind, passives }. Passive value =
  // (rank - 1) * perRank, clamped to +-max (PROPOSED, Nicko tunes):
  //   longBlade      damage +1%/rank (max +60%), attack stamina -0.4%/rank (max -35%)
  //   shieldDefense  block stamina drain -0.5%/rank (max -40%),
  //                  parry window +0.0005 s/rank (max +0.05 s = rank 100, mission cap)
  //   pyromancy      spell damage +1%/rank (max +60%), focus cost -0.4%/rank (max -35%)
  //   shortBlade     (DAG 2026-10-09, doc 15 canon #1 "fast, crit-flavored")
  //                  dagger damage +2%/rank (max +60%, reached at rank 31),
  //                  crit chance +1%/rank (max +35%) added to the precision
  //                  melee crit roll (game.js) on dagger hits. No stamina
  //                  passive v1: the attack-stamina hook reads the wielded
  //                  weapon's line, so a dagger swing gets x1 (no Long Blade
  //                  discount). Ranks by landed dagger hits.
  skillLines: {
    longBlade: { name: 'Long Blade', perUse: { hit: 1 },
      passives: { damage: { perRank: 0.01, max: 0.60 }, staminaCost: { perRank: -0.004, max: 0.35 } },
      caption: '+{damage}% damage, -{staminaCost}% attack stamina' },
    shieldDefense: { name: 'Shield / Defense', perUse: { block: 1, parry: 2 },
      passives: { blockDrain: { perRank: -0.005, max: 0.40 }, parryWindow: { perRank: 0.0005, max: 0.05 } },
      caption: '-{blockDrain}% block drain, +{parryWindowMs}ms parry' },
    pyromancy: { name: 'Pyromancy', perUse: { cast: 1 },
      passives: { damage: { perRank: 0.01, max: 0.60 }, focusCost: { perRank: -0.004, max: 0.35 } },
      caption: '+{damage}% spell damage, -{focusCost}% focus cost' },
    shortBlade: { name: 'Short Blade', perUse: { hit: 1 },
      passives: { damage: { perRank: 0.02, max: 0.60 }, critChance: { perRank: 0.01, max: 0.35 } },
      caption: '+{damage}% damage, +{critChance}% crit chance' }
  },
  // DAG: which line a landed melee hit trains + takes passives from, by the
  // wielded CONFIG.moveset weapon id (WH_LEVEL.weaponLine). Unlisted =
  // longBlade (today: every sweep is a Long Blade swing, handAxe included).
  weaponLines: { dagger: 'shortBlade' },
  // DAG: doc 18 tier table (docs/planning/18-skill-progression-mechanics.md
  // LAYER 2: NOVICE 1-24, APPRENTICE 25-49, ADEPT 50-74, EXPERT 75-99,
  // GRANDMASTER 100). Display only v1 (skill row caption prefix); the
  // tier-up technique menus are later doc work. from = first rank of the tier.
  tiers: [ { name: 'Novice', from: 1 }, { name: 'Apprentice', from: 25 },
           { name: 'Adept', from: 50 }, { name: 'Expert', from: 75 },
           { name: 'Grandmaster', from: 100 } ],
  // Which line a completed cast trains + takes passives from. Radiance is
  // light magic (doc 15 Holy Wards, not a prototype line this round): null =
  // no line. PROPOSED - set radiance: 'pyromancy' to have it train too.
  spellLines: { firebolt: 'pyromancy', radiance: null },
  // Rank curve (doc 18 LOCKED shape: full speed to 50, ~2x slower by 75,
  // ~3x by 95, no decay). rank XP to the next rank = perRank * slow(rank),
  // slow = 1 below slowFrom, else 1 + (rank - slowFrom) / slowSpan
  //   -> rank 75 = 2.0x, rank 95 = 2.8x. 5 uses per rank early: rank 50 at
  //   ~245 uses, Grandmaster (100) at ~740 uses. PROPOSED, Nicko tunes.
  rankCurve: { perRank: 5, slowFrom: 50, slowSpan: 25, maxRank: 100 },
  text: {
    levelUp: 'Level {n} reached - +{pts} stat points',
    rankUp: '{name} rank {n}',
    allocateHint: 'ALLOCATE',       // CHARACTER tab badge while points are pending
    levelLabel: 'Lv {n}',           // HUD XP pip label
    crit: 'CRIT'
  },
  levelToastSeconds: 2.6,           // #wh-level-toast lifetime
  rankToastSeconds: 1.6
};
// CC-LS1 (doc 61 P1-1): blob contact shadows - one shared geometry+texture,
// pooled meshes riding actor ground (pos.y) un-bobbed; fade+shrinks on lift.
window.WH_CONFIG.contacts = {
  poolSize: 24,        // player + live enemies worst case
  textureSize: 128,
  radiusBase: 0.55,    // fallback when body meta width is missing
  groundOffset: 0.02,  // doc 61 law: y = 0.02 over ground
  maxLift: 3.2,        // lift at which a blob vanishes
  minScale: 0.55,      // distant/bounce floor so the blob never pops out
  maxOpacity: 0.42
};
