# CC-H5b Hazards — Testerbot Validation Verdict (2026-11-07, wake 23)

- Valspec: `io/specs/cc-h5b-hazards-valspec.md` · Spec of record: `io/specs/cc-h5b-hazards-spec.md` · Build note: `io/reports/cc-h5b-hazards-build.md`
- Build under test: worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals` @ `df082e4` (+ 5 modified / 4 added paths, uncommitted).
- Testerbot lane honored: NO harness, NO headless browser, NO git mutations (status/log/show/diff only). One build_v8.py re-run (V-8) — byte-identical, dirty set unchanged after.
- **ROUND VERDICT: FAIL** — 9/10 V-items PASS (incl. PA-1, PA-2 riding V-7); **V-7 blocking FAIL** (probe under-coverage, undisclosed). Seats themselves verified sound by independent Testerbot re-check; the probe artifact must be amended, not the placement.

## BV-0 PRE-STATE — PASS

- HEAD = `df082e4` (feat/world-visuals); git status additions exactly the expected set: `prototype/js/CONFIG.js`, `game.js`, `region-manager.js`, `prototype/index.html`, `prototype/builds/v8-playable.html`, `prototype/js/hazards.js` (new), `scratch/cc-h5b/`, `io/specs/cc-h5b-hazards-{spec,valspec}.md`, `io/reports/cc-h5b-hazards-build.md`. No foreign dirty paths.
- Pre-floors at df082e4 recorded: `grep -c hazard CONFIG.js` = 0; WH_HAZARDS grep at HEAD empty; hazards.js absent at HEAD; `scratch/cc-h5b/` absent at HEAD. All flipped post-build as expected.

## V-1 CONFIG PARSE + HAZARD BLOCKS — PASS (blocking class cleared)

- Parse OK (node eval): `ventN=4`; seats deep-equal valspec table **with build-note-amended seat 2** `(-4.5,-899)` (valspec B1 literal was `(-6.0,-894)`; amendment is C2-lawful — "a probe failure amends the seat, never the law" — disclosed in build note §SEAT AMENDMENT + CONFIG.js:2349 comment).
- `hk` = exactly the 16 B1 keys; values: cueHex 14174794 = `0xd84a4a` ✓, damage 14 ✓, hitStop 0.1 ✓, staggerMeters 4 ✓, idle/warn/blast/linger 6.0/1.5/0.9/0.6 ✓, radiusM/warn/blast 2.0/1.1/2.0 ✓, heightM 2.2, cardIdleHex 0x8a2a20, cardBlastHex 0xff8a3c, shakeM 0.12 (reserved — disclosed).
- `gk` = exactly the 5 B2 keys: enabled, regionIds ['tithe_vaults'], hitCooldownSec 0.5, toastText 'The vault flares!', firstHitOnly true.
- regionK key-set diff vs df082e4 = ONLY added key `hazards` (sorted diff, single token). Evidence: CONFIG.js:2334-2373 (regionK.hazards), CONFIG.js:2588-2595 (CFG.hazards).

## V-2 LOAD ORDER — PASS

- `node --check` on hazards.js + CONFIG.js both exit 0.
- index.html:79 = ONE `hazards.js` tag; strictly between region-manager(65)…ambush(76)…hazards(79)…game.js(80). Band holds; ambush-relative order ungated per valspec.

## V-3 BUILD HOOK + DISPOSE/TEXTURE LAW — PASS

- (a) `wh-hazards` group name (hazards.js:108), built as region-group child via guarded `onRegionBuilt(regionId, group)` (region-manager.js:1947, inside buildRegion before scene.add); regionIds gate read from CFG (hazards.js:176) — contains tithe_vaults via CONFIG.
- (b) ZERO `new THREE.PointLight` / ZERO `scene.add(` in hazards.js.
- (c) `particle-ember` appears exactly ONCE (hazards.js:12 — shared texture via game.flameCards).
- (d) No png/glb/Loader/load( hits beyond the ember comment; assets.js diff = 0; dispose: guarded `onRegionDisposed` (region-manager.js:1959) + group freed by region-manager's existing traverse.

## V-4 TICK PHASE MACHINE + DE-SYNC — PASS

- Cycle math: 6.0+1.5+0.9+0.6 = **9.0 s** (computed from CONFIG, valspec command). Seq idle→warn→blast→linger; PHASE_NEXT chain (hazards.js:193); per-vent timers + offset budget (hazards.js:204-215).
- De-sync: `t: 0, offset: i * 1.3` (hazards.js:139) — vent i's first idle holds exactly i×1.3 s. PHASE_LEN re-bound from CFG keys at init (hazards.js:334-335).
- `Math.random` in hazards.js: **0 in code** (2 grep hits, both comments — lines 44, 350).

## V-5 DAMAGE LAW — PASS

- Player-hurt call: `g.player.takeDamage(HK.damage)` DIRECT (hazards.js:274) — no attacker arg; `resolveIncomingHit` ABSENT from hazards.js.
- i-frames inherited — player.js:1812-1813 quoted verbatim: `Player.prototype.takeDamage = function (amount) {` / `if (this.iframes > 0 || this.state !== 'alive') return false;` — gated before any hp subtraction; player.js untouched (not in dirty set).
- `hitDone` re-armed at every non-blast phase entry (hazards.js:199) = ONE damage event per vent-cycle; global gate `S.cooldownT = HG.hitCooldownSec` (hazards.js:271) — 0.5 s across ALL vents.
- Knockback OUT to 4.0 m (hazards.js:279-280); toast firstHitOnly-gated (hazards.js:285-290). Channel deviations — both declared per spec C3's "verify at build and disclose": shake reuses existing `triggerShake` (game.js:2625 wiring, amplitude stays CONFIG.anim.shake; shakeM 0.12 reserved); hit-stop = module-scoped `S.stopT` clock (no global hit-stop channel exists in game.js; consumed by nothing this round). Both disclosed in build note §Deviations.

## V-6 LIGHT + POOL DISCIPLINE — PASS

- **POOLTICK-VIRGIN**: poolTick span byte-identical vs df082e4 (cmp clean).
- computeSockets() diff = **0 lines** (cap ≤5 ✓, untouched). The socket rows landed in **computeFireSockets()** (game.js:2896-2904, +6 lines) — the C4-sanctioned fallback location, same convention as the lairSockets push immediately above it; disclosed in build note (C4 fallback + IO disclosure) ⇒ within the disclosed class.
- Rows = warn/blast ONLY (hazards.js:301 `continue` otherwise), carry `noCard: true` + `color: HK.cueHex` (hazards.js:311-312), id `hazardVent#i` — grammar matches lastSockets consumers. Zero rows at rest: idle/linger emit nothing ⇒ pool's 4 slots never stolen.

## V-7 PLACEMENT PROBE RUN + PROBE AUDIT — **FAIL (BLOCKING)**

Probe run: exit 0 ×2; per-vent table (4 seats) printed; two runs byte-identical (cmp clean). PA-1 anti-hardcode: CLEAN (the 3 regex hits are the width TABLE's own `3.0` values — prop-footprint rows, not vent coordinates; advisory z-grep −864/−869/−894/−897: CLEAN). PA-2 seat-source: CLEAN (evals CONFIG.js + region-defs.js at lines 43-44; seats iterated from `K.hazards.vents`, node_expr line 46). Seat 2 = (-4.5,-899) as amended.

**Cause of FAIL — probe under-coverage (PA-1/PA-2 audit, blocking):**
1. **Corridor-cycle analysis MISSING** — spec C2 + valspec V-7 mandate "worst-case vent at max walk speed crossing the corridor during a full idle→warn→blast cycle". Not present. (Corridor itself is safe: no vent has |x|≤2.2 — Testerbot check.)
2. **C2 audit lines MISSING** — the probe prints no no-new-lights grep, no no-new-assets manifest grep, no draw-call/sprite count (≤8 sprites + ≤4 pipe clones).
3. **Placement-law floor weakened**: probe F1 uses **1.0 m** edge floor vs B1's **2.0 m** prop-collider floor — build note §Deviations discloses a *convention* (2 m applied to prop centers vs 1.0 m "real-obstacle" floor) but does NOT disclose that F3 also uses **4.0 m** boss ring vs B1's **6.0 m** keepout, and never states that enemy/land/walk-in/corridor floors are uncovered at all. The disclosed convention covers only the F1 discrepancy; the rest is undisclosed.
4. Uncovered B1 floors (in the trusted artifact): enemy ≥5.0, land ≥4.0, walk-in ≥2.5, corridor-cycle.

- Testerbot independent re-check (seats are sound; the artifact, not the layout, is deficient): vent0 edge 6.84 m, vent1 1.81 m, vent2 1.35 m, vent3 1.16 m (scaled C14 full-footprint colliders; mourningStatue is NOT trunk-class — region-manager.js:361-371 — so 1.16-1.35 m is the honest scaled-edge number; player-block radius ≈ 0.275-0.5 m, all seats clear it). Boss keepout (B1 ≥6.0 m, keepout vs lair (0,-872)): vent0 9.71 m, vent1 7.16 m, vent2 27.37 m, vent3 25.18 m — all ✓ (vent1's raw-center 3.35 m to okRuinColumn(8,-872) is the prop-edge measure, 1.81 m after the 2.2×1.4 scaled foot — not the boss ring). Enemy ≥5.0: vent0 5.59 ✓ (marginal 0.59 m — worth an explicit floor in the probe), vent1 7.63, vent2 9.55, vent3 9.43 ✓. Corridor |x|≤2.2: no vent ✓. Amendment necessity confirmed: original (-6.0,-894) sat 2.00 m from statue (-6,-896) center = 0.00 m scaled edge ⇒ would breach F1 even at 1.0 m.
- Blocking per adjudication ("missing table / PA failure ⇒ BLOCKING" — here the missing corridor-cycle + audit lines are named V-7 asserts; undisclosed floor divergences are not covered by any note paragraph). **Remedy: amend the probe (add corridor-cycle + the three audit blocks + B1's full floor set at the B1 numbers) — no seat or game-code change required.**

## V-8 SYNTAX + REBUILD + MARKER — PASS

- `node --check` CONFIG/hazards/game/region-manager: all OK, no BAD.
- `python3 tools/build_v8.py` exit 0, `wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html 3506486 bytes`.
- Bundle sha12 **ba3d56fa0045 before = after** (3,506,486 bytes, equal to the build note's bytes) — regenerated, not hand-edited; marker grep `CC-H5b` = 9 ≥ 1; WH_HAZARDS ×10 + wh-hazards ×3 present in bundle. Dirty set unchanged post-rebuild.

## V-9 FILE DIFF GATES — PASS (envelope exceedances disclosed)

- Hard zeros: **save 0, enemy 0, light 0, inventory 0, region-defs 0, assets.js 0** (diff line counts vs df082e4) — no blocking breach.
- Envelopes vs actual: CONFIG +49 (spec ≈+45), game.js +17 (spec +2..8), region-manager +7 (spec 0..6), hazards.js 373 lines (C: ~200-260), index.html +3 (F: "+1 script line" = the tag + a 2-line CC-H5b comment, AE1 band style). **All five exceedances are recorded in the build note** (§Files stat table + the IO disclosure naming game.js/region-manager/CONFIG spans and hazards.js 373) per the adjudication rule ⇒ disclosed class, not FAIL. Disclosed deviations honored: triggerShake channel, scoped hit-stop, journal skip, statue floor convention.

## V-10 PLAYABILITY DEFERRAL — PASS — DEFERRED

- `grep -rln "puppeteer|playwright|headless" scratch/cc-h5b/ io/reports/*cc-h5b*` → no matches. No harness/browser run performed. Playability = Nicko's acceptance bar. Recorded: **DEFERRED**.

## DISCLOSURE LEDGER

Disclosed in build note (honored): seat-2 amendment; triggerShake reuse; scoped hit-stop (S.stopT); journal skip; statue-adjacent floor convention; socket rows in computeFireSockets (+6, C4 fallback); hazards.js 373 / game.js +17 / region-manager +7 / CONFIG +49 / index.html +3 line counts; IO-inline probe run (deterministic, no literals).
**Undisclosed and caught (this report):** V-7 probe — corridor-cycle analysis missing; no-new-lights / no-new-assets / draw-call count audit lines missing; boss-ring floor 4.0 m vs law 6.0 m; enemy/land/walk-in floors absent from the artifact.

## VERDICT TABLE

| Check | Verdict | Blocking |
|---|---|---|
| BV-0 | PASS | — |
| V-1 | PASS | cleared |
| V-2 | PASS | |
| V-3 | PASS | |
| V-4 | PASS | |
| V-5 | PASS | |
| V-6 | PASS | |
| V-7 | **FAIL** | **YES** (probe under-coverage; seats independently verified sound) |
| V-8 | PASS | |
| V-9 | PASS | disclosed exceedances |
| V-10 | PASS (DEFERRED) | |
| **Round** | **FAIL** | 1 blocking fail |

Amendment path: extend `scratch/cc5b`… `scratch/cc-h5b/probe_placement.py` to (1) print the corridor-cycle worst-case analysis, (2) add the three C2 audit blocks, (3) enforce B1's numbers (2.0 m prop edge, 6.0 m boss, 5.0 m enemy, 4.0 m land, 2.5 m walk-in) for all four seats — re-run twice, exit 0 both, then this round re-verdicts without touching game code or any seat.
