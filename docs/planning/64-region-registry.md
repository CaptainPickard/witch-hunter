# 64 - Region Registry (census + open slots for the castle/hold phase)

Status: REGISTERED, census 2026-11-06 (IO autopilot wake 14, tree tip d5da65a,
CONFIG.js 3936 lines). Companion to docs 49 (world GDD) + 61 (world audit) +
62/63 (region C). Companion to the instanced-region recipe doc (planned next
wake). Companion census note: io/REGION-CENSUS-2026-11-06.md (same day, prior
tip; numbers there are superseded by this doc where they differ).
RECIPE LANDED 2026-11-07 (wake 15): docs/planning/66-instanced-region-recipe.md
— every slot claim below is now spec-from-template (doc 66 sec 2-8); H1's
claim sheet is doc 66 sec 8.

Purpose (Nicko directive 2026-11-06, "instanced areas"): every live region and
pocket is registered here with its exact CONFIG keys, and RESERVED slot rows
below give the castle/hold phase a numbered set of claimable instances. When a
new instanced area lands, its row moves from RESERVED to LIVE in this doc —
the registry diff IS the phase ledger. Recipe doc (next) turns each entry into
a spec-from-template.

## 1. Machinery census (what an instance inherits today)

- CONFIG region row (CONFIG.js): id/name/spawn/center/groundRadius/groundY/
  gravity/fogColor/fogDensity/ambientLightLevel + props/enemies/lairs.
- region-defs.js: makeRegion() derives runtime regions; A/B share the plane-0
  boundary (z = CONFIG.boundary.z = -25) with a chokepoint (centerX 0, width 8);
  every later region is an OWN-DISC "pocket" reached by a DOOR connection with:
  door{planeZ, doorX, doorHalfWidth, suspendDepthM, wallGapPadM, interactM,
  interactAt, land{perRegion x,z,faceX,faceZ}, fadeIn/fadeOut/exitFadeOut,
  text.prompt} + walkFrom (plane exists ONLY in the named region's side) +
  per-connection sides table (connections[i].sides). Helper API:
  connectionBetween / insideDoorWindow / isMember / otherEnd / sideIn /
  connectionsOf / planeIn / sideOfPlane / mapPositionAcross.
- region-manager.js: logic cross (portalNear/forceCross E hook + walk-back
  plane crossing), one-active-region + neighbor PREWARM (preWarmDistance,
  dispose past the neighbor's own plane), per-region build/dispose, clamps.
- wh-ground.js: WH_GROUND.heightAt — A/B/D/E/F read FLAT groundY discs; C is
  the fbm heightfield with per-region 2D pocket rows (glade pocket
  {x0,z-96,r25,blend20,h0.4}, stonePad {x0,z-366,r28,blend16,h:null},
  den/outcrop digging at the D/E mouths). Rim fade 240..280->skirt + rim
  mountain ridge term on C.
- save.js: additive per-message save blocks carry regionId (player
  P.regionId, camp K.respawn.regionId, message-scoped world region) with
  validRegion() guards — the pattern any new instance's save roundtrip uses.
- daynight.js: constantPhases.<regionId> = an always-dark sky row (rot_den
  today; E/F ran WITHOUT one so far — region fog/ambient only). CC-C8-EXT
  (2026-11-08) landed six constant rows: veil_crypt, veil_galleries,
  armory_deep, veil_spire_approach, tithe_vaults, the_remains; the E/F gap
  above is historical, and these underworld interiors now hold one look.
- Scatter (CONFIG.scatter): A/B/C only; D/E/F scatter:false (hand rows only).

## 2. LIVE region table (values from CONFIG.js @ d5da65a)

| # | id | name | geometry | reach | enemies | notes |
|---|----|------|----------|-------|---------|-------|
| A | hold_outskirts | Hold Outskirts | shared disc r90, z>-25 side | start region | 11 rows (bandit/ghoul) | cemeteryFog ramp zone (keepOut ellipse 0,10 r36/33); camp+board hub; Round H spawn south wall path |
| B | darkwood_edge | Darkwood Edge | shared disc r90, z<-25 side | A<->B plane z=-25 chokepoint (x0 w8) + tutorial gate law | 3 (2 ghoul, 1 bandit) | B/C door in B north rim: planeZ -86, doorX 0, halfWidth 4, gatedTo veil chain law (locked while clock dormant), arch b3Gate @ (0,-86) rotY PI |
| C | forest_of_the_old_king | Forest of the Old King | OWN disc r280 @ (0,-366), fbm heightfield (hMax 5, nLo 0.22/nHi 0.79 seed 1337), rim fade + rim mountains, 3 notch mouths (0,-596 / ±240,-366) | B/C door planeZ -86 (from B) | 55 rows: 28 wolf (7 packs × 4: east/west/north/sw/se/ss/nw2), 25 bandit (C16b 4 camps × 3, C6 3 camps, redseam squatters 3), 2 coven (EC1) | roads kingsRoad/stoneApproach/stoneRing/north/east/west + 3 notch beds; glade + stonePad pockets; keepOut rows; raid (AE1 night raids) lives here; wolfPacks table; L0-L9 layout |
| D | rot_den | The Rot Mother's Den | OWN flat disc r34 @ (-186,-180), groundY 0 | C-side E hook at outcrop (-163.4,-202.6) interactM 3.5; walk-back plane z -215.2 window ±3.0 | lairs: rotmother @ (-185.8,-180.2) (nest furniture, rotLair pool/fog/light rows) | 10-ring cavern whWallA/B (exit gap north), scatter false, constantPhases.rot_den (always-dark: hemiFillMult 1, exposureMult 0.75, stars 0.15), door fades 0.3/0.5/0.8, prompt 'Enter the den' |
| E | veil_crypt | The Old Throne's Crypt | OWN flat disc r20 @ (0,-596) | C-side E hook at north notch mouth (0,-596); walk-back plane z -612 (crypt-local -16) window ±2.4 | 2 coven @ (5,-592) (-6,-590) | AD1 strata V1 (doc 47); basalt 0x121418 ground, bruised-purple 0x0a0810 fog, ONE crimson accent (albetar blightcap caps); NO constantPhase row yet; dressing stoneSarcophagus/stoneSteps/skullPile/rubblePile/mossBoulder; prompt 'Descend into the crypt'; door fades 0.3/0.5/0.8 |
| F | veil_galleries | The Erased Galleries | OWN flat disc r26 @ (0,-640) | E-side E hook at crypt west aisle aperture (-14.5,-596); walk-back plane z -640 window ±2.2 | 2 ghoul wardens @ (-6,-636) (6.5,-635.5) | AD2 strata V2 chained off the crypt; 8-segment whWall pantheon ring (22.5deg segment OMITTED, gap lane |x|<=2.2); THE ERASED FIGURE mourningStatue (names once stood); NO constantPhase row yet |

Non-region POCKETS on C's heightfield (live terrain rows, not regions):
glade pocket (0,-96,r25,blend20,h0.4), Old King's Stone pad (0,-366,r28,
blend16,h:null=unflattened 1.404), den/outcrop dig + notch windows on the rim
ridge term; C keepOut ellipses: (0,-366) r30, (0,-596) r18, (±240,-366) r18,
(±136..0,-219) r22/18 rows.

Sites on C (no region row; CONFIG dressing + enemy rows only): CC-WM1 Redseam
mine @ (54..67,-574..-587) (doc 42 P5 worked site), CC-C6 bandit camps Alpha
(-60,-186 fire) / Bravo (95,-236) / Charlie (-140,-506), CC-C16b densify
camps 1-4 + wolf packs sw/se/ss/nw2.

Connections table snapshot (region-defs.js): [0] A/B plane0 chokepoint;
[1] B/C door planeZ -86 gatedTo veil law; [2] C/D door planeZ -215.2 walkFrom
rot_den; [3] C/E door planeZ -612 walkFrom veil_crypt; [4] E/F door planeZ
-640 walkFrom veil_galleries. All door conns carry sides tables; land rows
per region (x NOT preserved across C/D-style chains).

## 3. RESERVED slots (castle/hold phase — claim from here)

Naming rule: castle/hold instances take id prefixes hold_ (surface holds) or
fort_ (fortified sites); pocket interiors keep the D/E/F style (one-word
place names: redseam_shaft, chapel_under, etc.). Slots are UNBUILT; claiming
one = write its CONFIG region row + door conn + registry row move.

| slot | reserved for | anchor concept | suggested geometry class | notes |
|------|--------------|----------------|--------------------------|-------|
| H1 | **LIVE — Lord's Hold (surface, doc 48 endgame base), landed 2026-11-07 CC-H1** | concept-06-siege-council | OWN disc r126 LANDED (claim range 120-160), FLAT (no terrain row — heightfield + courtyard pad pockets = H2 scope) | LANDED seat: center (0,-822), spawn (0,-711), gate lane |x|<=4.5 at z -700, door planeZ -700 (conn[5], from regionC walkFrom lords_hold), war-table hub dais (0,-780), 4 braziers + gate lantern = 5 warm sockets one amber family, 89-row curtain wall + 1068 colliders; clearance 141-check PASS, save roundtrip 15/15 PASS; garrison rows (enemies) = H2. **CC-H1a CORRECTION 11-07 (see doc 66 sec 10): conn[5] sides C +1 / G -1 — the landed D-symmetry table was inverted (P0: one-way door); playtest gate before Nicko = walk IN + walk OUT both directions**; **CC-PFG1 phase-fog rows (2026-11-08, PROPOSED, Nicko tunes): lords_hold keyed into each day/night phase-row fog object (night 0x8a8f96/0.08 = the region's own fogColor/fogDensity verbatim); applyDayNight per-frame writer for keyed regions closes the fog-freeze gap (fog was clock-frozen at region-row entry values); dormant night bit-identical |
| H2 | **LIVE — Garrison Keep courtyard layer, landed 2026-11-07 CC-H2** | concept-06-siege-council + char-04-bannerman-dark | chained OFF H1 LANDED (G<-H chain, the E/F chain stepped one link), flat disc r80 | LANDED seat: center (0,-1024), spawn (0,-955), breach lane \|x\|<=4 at planeZ -948, door conn[6] TWO-SIDED walk-through (B/C grammar: physical plane BOTH sides, no walkFrom/interact; suspendDepthM 4 lifts both disc clamps — with 0 the plane sits outside both playable rims, the H1a trap); the mouth = the two ERASED G curtain pole rows (4.4/-4.4 @ -947.92), 48-row ring wall 8 + 384 colliders, 18 dressing rows, 2 bandit sentries (-10,-975)/(11,-976), amber family 4 sockets (brazier + lanternPost + whCampkit x2); clearance 146-check PASS + verdict probes 132/53 PASS; armory/dungeon-mouth dressing = H2b content scope; **CC-PFG1 phase-fog rows (2026-11-08, PROPOSED, Nicko tunes): fort_garrison keyed into each day/night phase-row fog object (night 0x7d8289/0.068 = the region's own fogColor/fogDensity verbatim); applyDayNight per-frame writer for keyed regions closes the fog-freeze gap; dormant night bit-identical. **H2b ARMORY DEEP
      chamber LANDED 2026-11-07 (wake 20): regionI 'armory_deep' pocket
      disc r18 center (0,-1120) chained off H's south side via conn[7]
      (ONE-SIDED E/F grammar: walkFrom armory_deep + interact hook on H at
      (-7.5,-1088.5) r 3.5; sides H -1 / I +1, the E-mirror); bier dais
      (sarc + 2 steps tableaux) under the ONE crimson lantern + 2 ghouls +
      13 dressing rows + 10-row closed cavern ring; groundSeed 1662061654;
      landH (0,-1083.99) 1-cm shift adjudicated non-blocking (ADJ-1);
      clearance 95-check PASS, verdict io/reports/2026-11-07-cc-h2b-armory-deep-validation.md |
| H3 | **LIVE — The Spire Approach (deeper-strata pocket, doc 47 Sun-strata mood / doc 48), landed 2026-11-07 CC-H3 (wake 21)** | concept-08-veil-spire | OWN disc r40 LANDED (boss-tier = 2.2x F, 2x I), chained off veil_galleries via conn[8] (F<-J chain, ONE-SIDED E/F grammar: walkFrom veil_spire_approach + interact hook on F at (7.5,-654) r 3.5; sides F -1 / J +1, the I-mirror) | LANDED seat: center (0,-700), spawn/landJ (0,-730), door planeZ -738 (lane \|x\|<=2.2, south-point clearance 1.55 m); statue GAUNTLET = 4 mourners + 2 steps pairs flanking the processional, spire-root okRuinColumn triad (0,-700)/(-8,-696)/(8,-696), ONE crimson family (lanternPost (-6,-724) + 2 blightcaps), 2 ghouls (-15,-708)/(15,-708) 30 m apart, 15 dressing rows + 10-row closed vault ring (90 colliders, ring diameter 80); groundColor 0x0d0f15 (one step colder than F), groundSeed 1662061763, fog 0.15 d95 11.6 m, ambient 0.05; clearance 231-check PASS; **V-9 AMEND-1: clear circle 6.68 m at (0,-709) — spec-author's original 12 m @(0,-702) sat inside the root column's collider, re-ruled post-build**; verdict io/reports/2026-11-07-cc-h3-spire-approach-validation.md; **H3-warden extension CC-H4 (2026-11-07 wake 22): THE SCAR-READER boss-slam lair LANDED at the reserved root space — CONFIG.enemy.scarreader (hp 400 boss-slam r 7.5 210-deg crimson cue, ghoul minions x2, scarreader_cleared_J save flag) + regionJ lairs/rotLair (scar-pool dressing, light 0xd85050, seed 20261107) + enemy.js save-prefix generalization (back-compat rotmother_cleared_*) + per-instance cue colors; verdict io/reports/2026-11-07-cc-h4-scar-reader-validation.md (29/29 PASS)** |
| H4 | Chapel Under (interior pocket) | new piece needed before build | flat disc r30 off any hold | one-accent rule + erased-figure motif continuation |
| H5 | War Camp (surface) | new piece needed before build | OWN disc r90-120 | siege staging between A/C; quartermaster/board affinity |
| H6 | **LIVE — The Remains (delve strata V5, chain endgame off the Tithe Vaults), landed 2026-11-07 CC-H6 (wake 25)** | concept-08-veil-spire + char-04-bannerman-dark (provider retry failed 11-07: gpt-5.5/Codex ChatGPT-account 400 stands; set anchors inherited per blocker fallback) | OWN disc r30 LANDED (duel chamber, doc 47 S5: no trash pool, boss-warden only), chained off tithe_vaults via conn[10] (J<-K one-sided grammar: walkFrom the_remains + interact hook on K at (7.5,-854) r3.5; sides K +1 / L -1) | LANDED seat: center (0,-1064), spawn/landL (0,-1044), door planeZ -1036 (lane \|x\|<=2.2, south-point clearance 1.55 m); 10-row closed whWall ring RE-DERIVED 2dp (rho 30.0+-0.05, chord 18.5410, scale 9.7630, rotY ladder k=3/k=9 = 5.02/8.79); 13 props: stoneSarcophagus working-shell (0,-1086) (SPEC-FIG FIX: spec -1078 bound the boss-seat clear circle at 2.75 < 6.0; landed 7.28), melted colonnade pair, mourning pair 0.60, steps pair, skulls (-14,-1076)/(12,-1090), mossBoulder, lanternPost + blightcap pair (±16,-1047) — THE ONE crimson family; CONFIG.enemy.lastchancel — THE LAST CHANCEL (doc 47 V4 zealot-captain at boss scale: hp 400, boss-slam r4.6 arc100 windup 0.8 track 120 dps, scale 2.3, cap-0 minions block = lairTick crash-guard, lastchancel_cleared_L save flag; lair trio (0,-1060), 16.0 m landing-vs-aggro spacing); clearance probe 44/44 PASS x2 byte-identical (d1a96710) + save roundtrip 18/18 (e532061e incl. key round-trip); verdict io/reports/2026-11-07-cc-h6-remains-validation.md (CH-1..6 6/6 PASS, deviations 5/5 adjudicated) |

Slot law: ONE claim per build round; concept-art anchor FIRST (law 1); every
claim lands through the full gate (spec -> valspec -> build -> verdict -> IO
commit) and flips a numbered slot row LIVE here in the same commit.

## 4. Registry maintenance

- Update this doc in the SAME commit as any CONFIG region row change (add,
  retune center/radius/fog, land-row moves).
- The census note io/REGION-CENSUS-2026-11-06.md stays as the discovery
  artifact; this doc is the living ledger.
- Deviations found during census: none — all live regions matched their
  spec docs (63 CC-C*, 47 AD1, AD2 reports) at d5da65a. Doc 61's "region
  model" row predates C (two-region world) and is historical, not current.
