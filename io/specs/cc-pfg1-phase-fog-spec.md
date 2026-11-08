# CC-PFG1 — Open-Air Phase-Fog Rows (doc 64 registered gap) — IO Spec (v2)

Round: 2026-11-08 wake 43. Lane: the wake-42 journal-designated NEXT LANE —
regionG (lords_hold) and regionH (fort_garrison) run NO fog override in any
day/night phase: applyDayNight writes S.fog[rid] only when it exists
(game.js:1962-1966), so inside these two regions scene fog freezes at the
region-row values entered with, while hemi/moon/sky keep following the
clock. The underworld strata got their fix in CC-C8-EXT (wake 42);
open-air holds are still clock-frozen in fog only. This round closes the
doc-64-registered gap for surface holds.

## Scope law

CC-C8-EXT precedent (wake 42): CONFIG-only, additive rows. Two files change:

1. prototype/js/CONFIG.js — one fog-entry addition inside each of the four
   phase rows' `fog` objects: key `lords_hold` + key `fort_garrison`
   (darkwood_edge + forest_of_the_old_king already exist on all four
   rows; hold_outskirts carries cemColor/cemDensity which the G/H entries
   MUST NOT carry — copyRow gates hasCem on cemColor presence,
   daynight.js:58-60).
   8 total fog entries (4 rows x 2 regions). Zero lines removed, zero
   lines edited. Zero other CONFIG keys touched. NO constantPhases row:
   both are open-air surface holds under the doc 66 sec 2 surface law
   (shared clock; constant rows are for sealed strata only).

2. docs/planning/64-region-registry.md — registry-note edit on the G and H
   rows only (the CC-C8-EXT allowlist precedent): extend the fog sentence
   of each row with the phase-fog note per A11. No other registry edits.
   Zero region-defs.js, save.js, game.js, daynight.js lines — the engine
   already reads an arbitrary key set on the phase rows' fog objects
   (copyRow iterates row.fog; lerpRow iterates b.fog), so this is
   data-only.

## The night rows == the region rows (verbatim law; byte-frozen)

- night.fog.lords_hold    = { color: 0x8a8f96, density: 0.08 }
- night.fog.fort_garrison = { color: 0x7d8289, density: 0.068 }

These equal CONFIG.js regionG.fogColor/fogDensity and regionH
fogColor/fogDensity exactly, so the dormant night hold and every natural
night are bit-identical to the approved pre-round look in both regions.

## PROPOSED values (all — Nicko tunes; authoritative table)

| phase  | lords_hold fogColor/fogDensity | fort_garrison fogColor/fogDensity |
|--------|-------------------------------|-----------------------------------|
| night  | 0x8a8f96 / 0.08               | 0x7d8289 / 0.068                  |
| dawn   | 0x9c9184 / 0.068              | 0x8b827a / 0.058                  |
| day    | 0xa2a8ab / 0.045              | 0x9aa0a3 / 0.038                  |
| dusk   | 0x84807a / 0.088              | 0x78736c / 0.076                  |

Design intent: cold slate family through the clock; dawn lifts as morning
mist burns off (seige-council warm-grey tint, cold base); day is pale
overcast ash (aerial perspective); dusk thickens back toward the night
row (bannerman-dark). Warm amber/crimson accents stay in the torch/brazier
light pool rows — fog stays neutral. One accent per frame law carried.

## Acceptance criteria

- A1: node --check prototype/js/CONFIG.js exit 0.
- A2: fog-key census: each of the four phase rows' fog object contains
      EXACTLY the 5 keys {hold_outskirts, darkwood_edge,
      forest_of_the_old_king, lords_hold, fort_garrison} — 20 fog-key
      instances across the 4 rows.
- A3: night entries byte-verbatim: night row contains
      'lords_hold: { color: 0x8a8f96, density: 0.08 }' and
      'fort_garrison: { color: 0x7d8289, density: 0.068 }' (hex-literal
      law; grep -F the exact substrings).
- A4: dawn/day/dusk entries match the authoritative table above, hex
      literals only, decimal densities (0.068 / 0.058 / 0.045 / 0.038 /
      0.088 / 0.076).
- A5: git diff CONFIG.js = exactly +8 data lines (the 8 entries) plus the
      ONE mandated comment line (A10). No other CONFIG edits.
- A6: git diff game.js / daynight.js / region-defs.js / save.js = EMPTY.
- A7: node --check all four engine files exit 0 unchanged (sanity).
- A8: registry edit confined to the G and H rows.
- A9: build_v8 deterministic x2 (two runs, identical sha256 of
      v8-playable.html).
- A10: marker: the comment line
      `// CC-PFG1 phase-fog rows: G/H phase-keyed fog entries (doc 64 gap). PROPOSED, Nicko tunes`
      sits immediately above the night row's lords_hold entry, AND the
      build probe (IO-run, pre-dispatch) proves whether CONFIG.js comment
      lines carry into the bundle (v8-playable.html). If they carry:
      grep the bundle for 'CC-PFG1' >= 1. If they do not carry: the marker
      line ALSO goes into game.js above applyDayNight as a comment-only
      line (a +1 line game.js deviation from A6, disclosed in the build
      summary), and the bundle grep still must find 'CC-PFG1' >= 1.
      IF neither carries, the round lands without a bundle marker
      (disclosed; marker law is practice, not PRIMARY).
- A11: registry note names the mechanism in one line: "phase-fog rows key
      the per-region fog entry into each day/night phase row;
      applyDayNight writes fog for keyed regions each frame (the freeze
      gap this round closes); night entry = the region's own
      fogColor/fogDensity verbatim so the dormant night hold is
      bit-identical to the approved look."

## Interplay proofs (why this is safe — for the valspec census)

- applyDayNight (game.js:1962-1966): writes fog for keyed regions each
  frame; unkeyed regions freeze at entry state. This round keys G/H.
- copyRow/lerpRow iterate row.fog keys (daynight.js:57-60 / 78-84) —
  arbitrary key sets ride existing machinery; hasCem gated on cemColor
  presence; G/H entries carry NO cemColor/cemDensity keys.
- Night hold bit-identical: copyRow exact-state law (state = row exactly).
- Phase fades: 90s blendSec smoothstep rides the rows — G/H fog now eases
  with the phase (previously never moved).
- Region crossfade (regionFadeTick, P1-3): runs between applyDayNight and
  cemeteryFogTick, eases fog from the crossed-FROM live state to the
  arrived region's row via regionFadeTargets (reads region.fogColor/
  fogDensity — UNCHANGED rows). Arrivals restore the entered-at look;
  the phase write then owns every non-fade frame. No snapshot capture;
  no conflict.
- atmosphereTick re-base law (P1-7 Amend 7): external-change detection
  re-captures the fog writer's base when density changes externally —
  the new per-frame phase writes are just another external writer; recede
  multiplies the settled density and cannot compound.
- cemeteryFogTick is region-A-only — never touches G/H.
- Dormant boot: startPhase 'night'; state = the night row exactly
  (copyRow); dormant override in the tick wrapper is dormant-independent
  (wake 42 A8 trace) — dormant G/H renders the verbatim region rows =
  the pre-round look. No visual difference possible at boot.
- No save-file key touched (save.js untouched; no regionId changes; no
  new save keys).

## Gate order
IO spec -> Testerbot valspec (child, BEFORE Devbot) -> Devbot build ->
Testerbot independent verdict -> IO commit+push -> build+flip. Children
NEVER push (NO-GIT). No harness runs, no headless browser smoke tests
(PRIMARY law 2: Nicko's playtest is the acceptance bar). Valspec writes
static proofs + census greps only. Children work in /tmp/wh-worldfeat
on feat/world-visuals.

## Art anchor law
Anchors viewed this wake: concept-06-siege-council (cold blues vs warm
orange torch pockets; layered ground-creep + aerial perspective) +
char-04-bannerman-dark (heavy clinging fog; crimson-ember accents kept
OUT of fog, emissive rows only). Palette law: ONE accent per frame; fog
stays the neutral slate family.
