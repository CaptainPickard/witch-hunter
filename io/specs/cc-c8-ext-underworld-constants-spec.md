# CC-C8-EXT — Underworld Always-Dark Completion (constantPhases × 6)

**Route:** IO spec -> Testerbot valspec -> Devbot build -> Testerbot verdict -> IO
commit+push. Branch feat/world-visuals, worktree /tmp/wh-worldfeat. Build via
tools/build_v8.py. Children NEVER touch git (NO-GIT clause).

## 0. One-line intent

CONFIG-key map for this round (verified live this wake, regionFogRows.json):
veil_crypt = regionE, veil_galleries = regionF, armory_deep = regionI,
veil_spire_approach = regionJ, tithe_vaults = regionK, the_remains = regionL.
(Some planning docs use per-round slot letters like "G armory_deep" / "H3"
Spire Approach — those are doc slot names, NOT CONFIG keys; this spec and
the valspec use CONFIG keys + region ids exclusively. lords_hold = regionG
and fort_garrison = regionH are open-air and stay OUT of this round.) These
six strata currently run the OPEN-SKY day/night clock: once the clock runs
(post first camp rest), a daytime entry floods them with day hemi fill
(S.hemiFillMult 2.4), a day sun disc (opacity 0.85), lit stars-out and full
exposure — inside sealed crypts and vaults that canon says are "one black
thought." Fix: give each the CC-C8 constantPhases treatment the Den already
has, so their look is ONE constant row every frame, clock-independent.

Precedent: doc 64 region-registry line 43-44 states the gap verbatim:
"daynight.js: constantPhases.<regionId> = an always-dark sky row (rot_den
today; E/F ran WITHOUT one so far — region fog/ambient only)."

Mechanism is PROVEN in production (rot_den): DayNight.tick's constant-row
override (daynight.js `constantRow(areaId)` + the tick override at
daynight.js:493-504) rewrites the whole look-state with CONFIG row values
every frame; SkyPool.setArea retires pano layers in constant areas
(daynight.js:391). ZERO new runtime code — this round is CONFIG rows + docs.

## 1. Art anchor (law 1)

concept-08-veil-spire.png (viewed 2x this wake, full + zoomed crop on the
citadel): dark monochrome palette (charcoal/slate/muted violet) + ONE blood
red accent; lighting reads "eclipse" — no natural sun/moon; the analysis
ruling: "Adding a traditional celestial map (bright stars, a clear moon, or a
sun) would break the scene's logic... stars should feel like they are BEHIND
the smog, not above it" and any disc should be "underexposed, appearing as a
muted, pale disc rather than a light source." The constant rows below encode
exactly that: moon intensity 0, stars low (0.06-0.15 per stratum), disc
opacity low (0.08-0.2), exposure pulled down (0.70-0.75).

## 2. Exact change (CONFIG.js only)

In CONFIG.dayNight.constantPhases (the block that today holds rot_den ONLY),
ADD six sibling rows after rot_den, same shape. All creative values are
PROPOSED, Nicko tunes (codebase convention). Per-stratum gradient discipline:
each deeper stratum is one step colder/darker (matching how fog densities and
groundColor were stepped by the CC-H chain).

Shared skeleton (rot_den-kin, from rot_den's authored row):
- hemiFillMult: 1.0            (ambientLightLevel must not be applied twice)
- lightColor: 0xa8bce6, lightIntensity: 0.0, azimuthDeg: 0, elevationDeg: 30
- exposureMult: 0.75 (E/F/G) -> 0.72 (J/K) -> 0.70 (L)
- fog map: single inner key = the region id, color/density VERBATIM from the
  region's own CONFIG row (fogColor/fogDensity — these are approved look
  values, not proposals):
  - veil_crypt            color 0x0a0810 density 0.13
  - veil_galleries        color 0x0a0810 density 0.145
  - armory_deep           color 0x0a0810 density 0.13
  - veil_spire_approach   color 0x0a0810 density 0.15
  - tithe_vaults          color 0x0a0810 density 0.16
  - the_remains           color 0x090710 density 0.17

Per-region creative rows (PROPOSED, step-down with depth):

  veil_crypt (E, ambient 0.07, bruised-purple canon):
    hemiSkyColor 0x171c2a, hemiGroundColor 0x07080a,
    zenithColor 0x02030a, horizonBand 0x080612, horizonGlow 0x0e0a16,
    stars 0.15, discColor 0xdfe7f2, discGlowColor 0xa8bce6, discOpacity 0.2

  veil_galleries (F, 0.055, one step colder than E):
    hemiSkyColor 0x151a26, hemiGroundColor 0x06070a,
    zenithColor 0x020307, horizonBand 0x070510, horizonGlow 0x0d0914,
    stars 0.12, discColor 0xdfe7f2, discGlowColor 0xa8bce6, discOpacity 0.15

  armory_deep (G, 0.07, built as E's family per AD1):
    hemiSkyColor 0x171c2a, hemiGroundColor 0x07080a,
    zenithColor 0x02030a, horizonBand 0x080612, horizonGlow 0x0e0a16,
    stars 0.15, discColor 0xdfe7f2, discGlowColor 0xa8bce6, discOpacity 0.2

  veil_spire_approach (J, 0.05):
    hemiSkyColor 0x141823, hemiGroundColor 0x050609,
    zenithColor 0x010305, horizonBand 0x06040d, horizonGlow 0x0b0812,
    stars 0.10, discColor 0xdfe7f2, discGlowColor 0xa8bce6, discOpacity 0.12

  tithe_vaults (K, 0.045):
    hemiSkyColor 0x12161f, hemiGroundColor 0x040507,
    zenithColor 0x010204, horizonBand 0x050309, horizonGlow 0x090610,
    stars 0.08, discColor 0xdfe7f2, discGlowColor 0xa8bce6, discOpacity 0.10

  the_remains (L, 0.04, deepest — the duel chamber):
    hemiSkyColor 0x101419, hemiGroundColor 0x030406,
    zenithColor 0x010203, horizonBand 0x040307, horizonGlow 0x080510,
    stars 0.06, discColor 0xdfe7f2, discGlowColor 0xa8bce6, discOpacity 0.08

Formatting: follow the existing rot_den row layout (2-space indents inside the
constantPhases block, 6-space property indents), each row getting a 3-5 line
comment naming the region, its stratum depth relative to neighbors, the art
anchor rationale (no pano, moonless, stars-behind-smog), and "All PROPOSED,
Nicko tunes." Add one block comment above the first new row: CC-C8-EXT
constant rows for the six underworld strata — the clock keeps running outside;
these interiors hold ONE look every frame (see doc 64 registry note).

## 3. Non-changes (identity guards)

- NO change to CONFIG.dayNight.phases (dawn/day/dusk/night rows), to any
  region CONFIG row, to daynight.js, game.js, region-manager.js, or ANY js
  file. The ONLY code file touched is prototype/js/CONFIG.js.
- NO new phase fog rows for lords_hold / fort_garrison (open-air; that is a
  separate follow-on lane, deliberately NOT packed into this round).
- rot_den row bytes: UNTOUCHED.
- Verify-then-edit: Devbot must confirm at build time that the constantPhases
  block currently contains exactly one row (rot_den) before editing.

## 4. Expected behavior after landing

- While dormant (pre-camp): unchanged for reachable play. TRACE CORRECTED
  during pre-flight (2026-11-08): the constant override in the
  DayNight.prototype.tick wrapper (daynight.js:493-504) runs AFTER coreTick
  and is DORMANT-INDEPENDENT — dormant + constant area = the constant row
  wins (this is correct and proven: the den reachable pre-camp renders its
  constant look; the wrapper's comment "Leaving while dormant puts the frozen
  startPhase row back" describes the constantHeld restore branch, which
  copies D.phases[D.startPhase] when an area WITHOUT a constant row is
  reached while the clock is frozen). The six new rows are unreachable while
  dormant anyway: the veil chain (B/C door) is locked while the clock is
  dormant (gatedTo veil chain law, doc 64 row B), so no dormant player can
  stand in E/F/G/J/K/L. Testerbot must trace the wrapper order exactly this
  way (override dormant-independent; restore branch returns the frozen
  startPhase row) and confirm no behavior change for A/B/C/lords_hold/
  fort_garrison while dormant.
- Clock running: inside any of the six, look == that region's constant row
  every frame (hemi fill = hemiBaseIntensity x ambientLightLevel x 1.0 via
  applyDayNight's region lookup — unchanged formula), fog = region row
  verbatim, exposure = row mult, dome = gradient underlay only (panos retire
  per daynight.js:391), no sun disc swing, stars pinned low.
- Crossing back out to an open region (A/B/C, lords_hold, fort_garrison):
  phase rows resume exactly as today (constantHeld restore branch at
  daynight.js, plus setSkyArea on every transition game.js:1122/1133).

## 5. Rollback

CONFIG-only: deleting the six added rows restores current behavior exactly.
Flag for the round note.

## 6. Testerbot validation scope (code QA, not playtest)

Static + VM checks only (no browser, no harness — PRIMARY law 2):
V1  node --check on prototype/js/CONFIG.js passes.
V2  Evaluating CONFIG.js in a minimal JS VM (stub window + THREE stubs that
    provide Color at constructor only if needed by top-level; CONFIG.js is a
    plain object literal — confirm zero THREE refs at top level, else list
    what stubs were needed) yields an object with
    dayNight.constantPhases having exactly 7 keys: rot_den + the six region
    ids, and rot_den's row byte-equal (string compare of the serialized
    object) to pre-round values.
V3  Each of the six rows: contains ALL keys a phase row requires (every key
    present in the rot_den row: hemiSkyColor hemiGroundColor hemiFillMult
    lightColor lightIntensity azimuthDeg elevationDeg exposureMult fog
    zenithColor horizonBand horizonGlow stars discColor discGlowColor
    discOpacity) — assert key-set equality, no extras.
V4  Each six-row fog map: exactly one inner key equal to its own region id;
    color/density equal to the values in section 2 (byte assertions vs the
    region's CONFIG fogColor/fogDensity where both live in the evaluated
    object).
V5  Stratum ladder: assert stars == [0.15,0.12,0.15,0.10,0.08,0.06] and
    discOpacity == [0.2,0.15,0.2,0.12,0.10,0.08] and exposureMult ==
    [0.75,0.75,0.75,0.72,0.72,0.70] along depth order [E,F,G,J,K,L] ==
    [veil_crypt, veil_galleries, armory_deep, veil_spire_approach,
    tithe_vaults, the_remains] exactly (do NOT over-constrain fog density —
    G sits at 0.13, sibling of E, by design).
V6  hemiFillMult == 1.0 in all six; lightIntensity == 0.0 in all six.
V7  Grep law: `git diff feat/world-visuals -- prototype/js` touches ONLY
    prototype/js/CONFIG.js; `git diff` does NOT modify the rot_den row
    (compare constantPhases.rot_den serialized before/after).
V8  Verify-night guard unaffected: D.phases.night untouched (V2 serialization
    of dayNight.phases.night pre/post equal).
V9  daynight.js dormant-order trace: quote the tick wrapper lines showing the
    dormant branch runs before the constant override, and the ConstantHeld
    restore branch — confirm sections 4's dormant claim against the code.
V10 SkyPool pano retirement: quote daynight.js setArea's constantRow guard —
    confirm panos retire inside the six (no new code needed).
V11 Doc update present: docs/planning/64-region-registry.md lines 43-44 note
    amended (the "E/F ran WITHOUT one" sentence updated to reflect six rows
    landing), in the SAME commit as CONFIG.js per registry-maintenance law.
V12 No other files changed beyond section 6 allowed set: {prototype/js/
    CONFIG.js, docs/planning/64-region-registry.md} (+ io/ docs exempt).

## 7. Round note duties (IO, post-verdict)

commit + push + build_v8 + stamp commit + release flip (background proc law)
+ curl serve-verify (200 + sha match vs worktree) + journal + GOALS backlog
tick. Before/after summary for Nicko: while the clock runs, entering any of
the six now freezes to its stratum look (moonless, fog verbatim, stars faint,
disc faded, dome bare-gradient) instead of drifting day/bright; dormant
tutorial look unchanged; open-air regions unchanged. PROPOSED values — Nicko
tunes live in CONFIG like the WH_POSTPASS dials.
