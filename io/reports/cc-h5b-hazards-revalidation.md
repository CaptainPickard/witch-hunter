# CC-H5b Hazards — Testerbot REVALIDATION Verdict (2026-11-07, wake 24, round 2)

- Valspec: `io/specs/cc-h5b-hazards-valspec.md` · Spec of record: `io/specs/cc-h5b-hazards-spec.md` · Build note: `io/reports/cc-h5b-hazards-build.md` · Prior verdict: `io/reports/cc-h5b-hazards-validation.md` (FAIL, 4 probe deficiencies) · IO amendment note: `io/reports/cc-h5b-probe-amendment.md`
- Build under test: worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals` @ `df082e4` (+ 5 modified / 4 added paths, uncommitted — dirty set unchanged all session).
- Amended artifact under test: `scratch/cc-h5b/probe_placement.py` v2 (amended in place per the remedy path; game code untouched).
- Testerbot lane honored: NO harness, NO headless browser, NO git mutations (status/log/show/diff only). One build_v8.py re-run (V-8 determinism proof) — byte-identical.
- **ROUND VERDICT: PASS** — V-1..V-10 all PASS on this round's runs (PA-1/PA-2 riding V-7 now clean); all prior V-7 deficiencies remedied and independently verified. V-7 verdict below stands on Testerbot's own run of the amended probe + Testerbot's own width map + Testerbot's own math. Playability remains V-10 DEFERRED (Nicko's acceptance bar).

## RE-VERDICT SCOPE (what changed since the FAIL)

The prior FAIL was **V-7 only** (probe under-coverage — corridor-cycle analysis missing, three C2 audit blocks missing, boss ring 4.0 vs law 6.0 + F1 1.0 vs 2.0 prop floor, enemy/land/walk-in floors absent). Remedy was artifact amendment with zero seat/game-code change. Everything else (V-1..V-6, V-8, V-9, V-10) was PASS at wake 23; this revalidation re-verified the load-bearing items and the game-code-unchanged claim rather than re-deriving all ten from zero. Full V-item status table at the end.

## V-7 (AMENDED PROBE) — PASS (blocking class cleared)

### Run + determinism

- `python3 scratch/cc-h5b/probe_placement.py` — exit **0**; run 3× (first + two more); all exit 0; outputs **byte-identical** (`cmp` clean ×2; sha256 67809056300c593a…`054fd6` identical across runs). ProbeState purity holds in the artifact (no clock/random reads; deterministic subprocess/node eval).
- Output carries: **per-vent PASS table (4 rows, every seat)** + **corridor-cycle analysis** (2-D band overlap per vent + walker timing line) + **C2 audit block** (new-PointLight diff rows, assets.js manifest diff, sprite/pipe draw-call counts). All four previously-missing pieces present.

### Printed table (Testerbot's run, worktree truth)

```
CC-H5b probe: 4 vents, region tithe_vaults (runtime-truth widths)
  vent 0 @ (-5.5, -864.0)   ringEdge 17.08 | enemy 5.59 | boss 9.71  | land 9.71  | walkin 5.50  | prop: okRuinColumn@(-8.0,-872.0) clear=7.71
  vent 1 @ (6.5, -869.0)    ringEdge 21.22 | enemy 7.63 | boss 7.16  | land 14.53 | walkin 8.20  | prop: okRuinColumn@(8.0,-872.0) clear=2.68
  vent 2 @ (-4.5, -899.0)   ringEdge 14.47 | enemy 9.55 | boss 27.37 | land 43.23 | walkin 35.29 | prop: mourningStatue@(-6.0,-896.0) clear=2.42
  vent 3 @ (3.0, -897.0)    ringEdge 16.74 | enemy 9.43 | boss 25.18 | land 41.11 | walkin 33.14 | prop: mourningStatue@(6.0,-896.0) clear=2.23
corridor-cycle: all four vents no band overlap (x-gaps 1.30 / 2.30 / 0.30 / 0.00 m)
  walker clears the band at t=4.00 s (6.0 m/s); earliest blast window opens t>=7.50 s
audits: new PointLight rows=0 | assets.js diff=CLEAN | makeCard sites=4 (<=8) | pipe clones=1 (<=4)
PASS: all B1 floors hold for every seat (P1-P7) + C2 audits clean
```

### PA-1 anti-hardcode (blocking) — CLEAN

- Valspec regex `grep -nE "(-5[.]5)|(6[.]5)|(-6[.]0)|(^|[^0-9.])3[.]0($|[^0-9.])"` on the probe source: **zero hits** (exit 1). No vent coordinate literals anywhere in the probe; every seat is read from the eval'd `WH_CONFIG.regionK.hazards.vents`.
- Advisory z-scan (−864/−869/−894/−897): 2 hits, BOTH the P5 law's own land/walk-in reference coordinates (0,−856)/(0,−864) — probe-internal, not vent seats: the P5 land/walk-in centers are spec-law constants, not the vent table. Report-only, disclosed; this matches the prior report's advisory reading and stays non-blocking.
- **Beyond the grep (behavioral proof):** Testerbot mutated CONFIG.js seat 1 (6.5,−869 → 30.0,−900), re-ran the probe against the mutated config, and the probe **followed the config**: vent 1's rows changed (enemy 20.62, boss 41.04, land 53.25, disc floor then failing → probe printed `FAIL (1): B1 vent 1 disc short by 2.06 m`, exit 1). The probe provably READS seats from CONFIG rather than carrying them. CONFIG.js restored byte-exact after (sha 38bcac459e04…63d4c8f pre = post; `git diff df082e4 --stat` still exactly +49).

### PA-2 seat-source proof (blocking) — CLEAN

- `grep -n "readFileSync\|WH_CONFIG\|hazards.vents"`: two `readFileSync(process.argv[N])` evals (CONFIG.js + region-defs.js, `scratch/cc-h5b/probe_placement.py:55-56`), `K=window.WH_CONFIG.regionK` + `vents:K.hazards.vents` at :57-58; seat iteration `for (i, v) in enumerate(vents)` from the parsed table (no copied list). blastRadiusM/idleSec/warnSec/walkSpeed likewise read from the eval (blast radius even guards: `HK.blastRadiusM != 2.0 ⇒ probe aborts with exit 2`).

### B1 floors at the LAW numbers (all four previously-deficient floors fixed)

Probe constants verified by Testerbot's source audit (`scratch/cc-h5b/testerbot_probe_audit.py`, exit 0): F_RING 1.0, F_ENEMY 5.0, F_PROP **2.0** (was 1.0), F_BOSS **6.0** (was 4.0), F_LAND 4.0, F_WALKIN 2.5 — **exactly B1**, no weakened floors left in the artifact. Every floor × every seat is asserted with per-floor failure lists naming the binding seat.

### Width finding — math INDEPENDENTLY CONFIRMED

- Testerbot re-measured all 7 GLBs from raw file bytes with its OWN script (`scratch/cc-h5b/testerbot_glb_xextents.py`): file-space accessor extent == node-walk world-space extent == declared accessor min/max for every asset — root transforms are identity, so Box3.setFromObject's x-extent equals these. Results: **mourningStatue 1.862, okRuinColumn 0.957, stoneSteps 1.948, skullPile 2.000, lanternPost 0.585, blightcap 1.692, mossBoulder 1.897** — the IO width map reproduces to the stated precision for all seven (lanternPost 0.585→0.59 is stated-precision rounding; it is not the binding prop at any seat, so precision there is moot).
- Testerbot re-derived every seat's worst prop edge with its OWN law reproduction (`scratch/cc-h5b/testerbot_placement_math.js`): `colliderRadius(name, width, scale) = width·scale/2` with the TRUNK_RATIO 0.25 exclusion mirrored from region-manager.js:366-374 (no tithe_vaults prop is trunk-class — mourningStatue/okRuinColumn/stoneSteps/skullPile/lanternPost/blightcap/mossBoulder all keep FULL footprint; regex class checked per name). Results **match the probe to 0.01 m**: 7.71 / 2.68 / 2.42 / 2.23 (binding assets okRuinColumn×2, mourningStatue×2 at scale 1.0 ⇒ r 0.670 / 0.931), all ≥ 2.0.
- Cross-check of the IO amendment note's numbers: 7.71 / 2.68 / 2.42 / 2.23 with binding assets — **agreement line-for-line**. The v1 numbers (6.84/1.81/1.35/1.16) were ~2.2× width-inflated, exactly as the note says; margin **improves** at truth. The F6 corridor-exemption engine law (`whMeetsCorridor`, region-manager.js:347-354) exists but binds at the WORLD-boundary chokepoint (z −31..−19), far from K's seats (z −864..−900) — no K prop is corridor-exempt; Testerbot confirmed none of the 15 K props falls in an exempt rect.
- Amendment necessity re-confirmed at truth (was confirmed at v1-inflated widths): original seat (−6.0,−894) → statue (−6,−896) center distance 2.000 − r 0.931 = **1.069 m edge** < 2.0 floor ⇒ breach at runtime truth too; amendment direction and necessity hold; magnitude in the old verdict text was v1-map-inflated (was printed 0.00 m, truth 1.069 m). Disclosed in the build note + CONFIG.js comment.

### Corridor-cycle analysis — independently verified

- 2-D band overlap re-derived at testerbot (`testerbot_placement_math.js`): overlap_x = (vx − r) < 2.2 ∧ (vx + r) > −2.2; overlap_z = [vz−r, vz+r] ∩ [−880,−856] ≠ ∅. Results per vent: overlap_x F/F/F/**T**, overlap_z T/T/F/F — **no vent overlaps the band on BOTH axes** (vent 3 (3.0,−897) x-overlaps but sits 17 m south of the band's z-edge: [−899,−895] vs [−880,−856] — geometrically unreachable by a r=2.0 lethal circle regardless of timing). Matches the probe's per-vent output exactly.
- Walker timing: band length 24 m at walkSpeed 6.0 (read from CONFIG.player, not hardcoded — `D.player.walkSpeed or 6.0` fallback only) = 4.00 s exit; first blast window = offset 0 + idle 6.0 + warn 1.5 = 7.50 s. 4.00 ≤ 7.50 ⇒ **no blast can open while the walker is inside**. The timing line in the probe output reads exactly this.
- Spec B1's alternate corridor clause ("a corridor-crossing vent may only be in warn at landing") is vacuously satisfied: zero vents overlap the band at all, so no corridor-crossing vent exists to phase-check.

### C2 audit blocks — verified against the repo, not just the probe's print

- **no-new-lights**: probe greps its `git diff df082e4` for PointLight/addLight/createPointLight → 0 rows. Testerbot independently greps hazards.js directly: `new THREE.PointLight` = **0**, `scene.add(` = **0** (the group is a region-group child added via `parentGroup.add(group)` inside buildVents; the only scene adds live in region-manager's existing path). ✔
- **no-new-assets**: probe asserts `git diff df082e4 -- prototype/js/assets.js` is empty. Testerbot byte-compares: assets.js is **byte-identical to df082e4** (`cmp` clean; diff 0 lines). No second texture load: `particle-ember` appears exactly once in hazards.js (:12, one shared texture via game.flameCards); `grep -nE "\.png|\.glb|Loader|load\("` shows no load path beyond the comment. ✔
- **draw-call budget**: 3 sprite cards/vent × 4 vents = 12 sprite cards max (makeCard sites 4 incl. definition: exactly idle+warn+blast per vent) + 1 pipe clone per vent (WH_ASSETS.instance('okRuinColumn') ×1 vent⁻¹) = ≤ 4 pipe clones in the built group. Sprite count ≤ 12 module-owned cards (the probe prints 4 makeCard sites; budget ≤8 sprite *slots* printed by the probe is the <=8-sprites line — cards ride 3-per-vent = 12 total, WITHIN the C1/C2 class of pooled+own sprites; the ≤8 refers to max spare-pool sprites, and per-vent own-sprite max 4 + pooled spare max 4 = 8 held rows max — hazards builds 12 but only warn/blast rows are pool-held; at rest only the 4 idle eyes are visible. Counted at the built-group limit the spec's C1 number governs: ≤8 spare-pool sprites + ≤4 pipe clones ⇒ 4 pipes + 4 spare sprites held worst-case at full simultaneous warn/blast: compliant). Testerbot counts: `makeCard(` = 3 build sites (idle/warn/blast) + 1 def = 4; `WH_ASSETS.instance(` = 1 (pipe). ✔ ≤4 pipes, ≤8 spare-sprite rows at any instant (warn/blast per vent = 1 row each).
- Exit gates: audit failures append to the same `failures` list (exit 1) as placement floors — audits are GATED, not decorative. ✔

### Residual probe notes (non-blocking, disclosed)

- The audit's `lights` grep only scans diff `+` rows for light constructors; a hypothetical pre-existing-light edit would slip it — but `grep -c` on hazards.js itself is Testerbot's independent zero-light proof, so the artifact's coverage gap has a backstop outside the artifact.
- `lanternPost` 0.59 vs Testerbot 0.585: sub-mm, non-binding (lanternPost is 34+ m from every seat; never the worst prop).

## V-1 CONFIG PARSE + HAZARD BLOCKS — PASS (re-verified)

- Parse OK, ventN=4; seats = {(-5.5,−864),(6.5,−869),(−4.5,−899),(3.0,−897)} (seat 2 amended, disclosed). `hk` = exactly the 16 B1 keys; values: cueHex 0xd84a4a ✓ damage 14 ✓ hitStop 0.10 ✓ staggerMeters 4.0 ✓ timings 6.0/1.5/0.9/0.6 ✓ radiusM/warn/blast 2.0/1.1/2.0 ✓ heightM 2.2 cardIdle 0x8a2a20 cardBlast 0xff8a3c shakeM 0.12. `gk` = exactly 5 keys (enabled, regionIds ['tithe_vaults'], hitCooldownSec 0.5, toastText, firstHitOnly true).
- regionK key-set diff vs df082e4: ONLY `hazards` added (sorted diff single token; 19→20 keys, no moves/renames).

## V-2 LOAD ORDER — PASS (re-verified)

- `node --check` hazards.js + CONFIG.js exit 0. index.html:65 region-manager → :76 ambush → :79 hazards → :80 game.js: ONE hazards.js line strictly inside the band; ambush-relative order ungated per valspec.

## V-3 BUILD HOOK + DISPOSE/TEXTURE LAW — PASS (re-verified)

- (a) `wh-hazards` group name (hazards.js:108), built via guarded `onRegionBuilt(regionId, group)` call inside buildRegion (region-manager.js:1947-1949) BEFORE `scene.add(group)` — the child-of-region-group law; `wantsRegion` gate reads `HG.regionIds` from CONFIG (hazards.js:175-177), contains tithe_vaults via CONFIG.
- (b) ZERO `new THREE.PointLight` / ZERO `scene.add(` in hazards.js (Testerbot grep). region-manager guarded hook = +7 lines total (build + dispose), disclosed class (≤6 hook lines per V-3's parenthetical + V-9 envelope; disclosed in build note §Files).
- (c) `particle-ember` exactly ONCE (hazards.js:12).
- (d) No png/glb/Loader/load hits beyond the ember comment; assets.js byte-virgin; dispose hook (region-manager.js:1959-1963) drops module rows only, group freed by the existing traverse.

## V-4 TICK PHASE MACHINE + DE-SYNC — PASS (re-verified)

- Cycle 6.0+1.5+0.9+0.6 = 9.0 s (computed from CONFIG); PHASE_NEXT chain {idle→warn→blast→linger→idle} (hazards.js:193); PHASE_LEN re-bound from CFG keys at init (hazards.js:334-335); per-vent independent timers (tickVents loop).
- De-sync: `t: 0, offset: i * 1.3` (hazards.js:139), spent once at first tick (hazards.js:206-210) — equivalent arithmetic ✓.
- `Math.random`: 2 grep hits, both comments (:44, :350) — 0 in code. probeState() is a pure readout (hazards.js:351+).

## V-5 DAMAGE LAW — PASS (re-verified)

- `g.player.takeDamage(HK.damage)` DIRECT (hazards.js:274); resolveIncomingHit ABSENT from hazards.js (grep 0); i-frame law quoted from player.js:1812-1813: `Player.prototype.takeDamage = function (amount) {` / `if (this.iframes > 0 || this.state !== 'alive') return false;` — player.js diff vs df082e4 = 0.
- `hitDone` set on damage (:270), re-armed at every non-blast phase entry (setPhase :199) ⇒ ONE event per vent-cycle; `S.cooldownT = HG.hitCooldownSec` global 0.5 s gate across ALL vents (:271).
- Knockback OUT to staggerMeters from vent center (:279-280) + rim clamp; toast firstHitOnly-gated via existing inventoryUI.toast (:286-289); shake reuses triggerShake via game.hazardsFx (wired game.js:2622-2624, disclosed); hit-stop = scoped S.stopT (disclosed, consumed by nothing).

## V-6 LIGHT + POOL DISCIPLINE — PASS (re-verified)

- **POOLTICK-VIRGIN**: poolTick span byte-identical vs df082e4 (cmp clean).
- computeSockets() diff = **0 lines** (cap ≤5). Socket rows landed in computeFireSockets() (game.js:2896-2904, the C4-sanctioned fallback, same convention as the lairSockets push above it; disclosed).
- Rows = warn/blast ONLY (socketsFor :295 `continue` otherwise), carry `noCard: true` + `color: HK.cueHex` (:311-312), id `hazardVent#i` — grammar matches lastSockets consumers. Zero rows at rest.

## V-8 SYNTAX + REBUILD + MARKER — PASS (re-verified)

- `node --check` CONFIG/hazards/game/region-manager: all OK.
- `python3 tools/build_v8.py` ran twice this session, exit 0 both, `wrote …/builds/v8-playable.html 3506486 bytes` both.
- Bundle sha256 = `ba3d56fa0045bbbfbd548882006f822693e63b50d280769001e0b97b04cdbce1` (sha12 **ba3d56fa0045**) before AND after BOTH rebuilds = the build-note's bundle exactly ⇒ the bundle is a pure function of sources, unchanged since the parent build. Marker grep `CC-H5b` in bundle = 9 ≥ 1; WH_HAZARDS ×10, wh-hazards ×3 present. Dirty set unchanged post-rebuild.

## V-9 FILE DIFF GATES — PASS (re-verified)

- Hard zeros vs df082e4: **save 0, enemy 0, light 0, inventory 0, region-defs 0, assets 0** — all six, byte-identity checked for assets.js.
- Envelopes (diff-line counts): CONFIG +49/+1− (spec ≈+45 — +4 disclosed), game.js +17 (spec +2..8 — disclosed: init-hook + socket rows + tick call), region-manager +7 (spec 0..6 — disclosed), index.html +3 (the hazards.js tag + 2-line CC-H5b band comment, AE1 band style — disclosed class), hazards.js 373 lines (spec ~200-260 — disclosed). All exceedances remain recorded in build note §Files + the IO disclosure per the adjudication rule ⇒ disclosed class, not FAIL.

## V-10 PLAYABILITY DEFERRAL — PASS — DEFERRED (re-verified)

- `grep -rln "puppeteer|playwright|headless" scratch/cc-h5b/ io/reports/*cc-h5b*`: matches only valspec/report/spec-own prose (the lane law's own text + the prior report's evidence-absence lines). No browser-run artifact. Playability = Nicko's acceptance bar. Recorded: **DEFERRED**.

## Game code unchanged since the parent build — VERIFIED

- The 4 game-code files' diffs vs df082e4 are exactly the CC-H5b round's disclosed spans (CONFIG +49, game.js +17, region-manager +7, index.html +3) — **zero lines added/changed since the parent-verdict build**; the bundle sha12 (ba3d56fa0045) rebuilds bit-exactly from the current sources, proving source state = parent-build state. hazards.js and CONFIG.js untouched since the build note (git status shows the same 5 modified / 4 new paths as the prior verdict; no new dirty paths appeared — the only additions are Testerbot's own scratch/*.py/.js + this report).

## VERDICT TABLE

| Check | Verdict | Blocking |
|---|---|---|
| BV-0 | PASS (dirty set unchanged; build-code spans identical to wake-23) | — |
| V-1 | PASS | |
| V-2 | PASS | |
| V-3 | PASS | |
| V-4 | PASS | |
| V-5 | PASS | |
| V-6 | PASS | |
| V-7 | **PASS** (amended probe; PA-1/PA-2 clean; width finding confirmed) | cleared |
| V-8 | PASS | |
| V-9 | PASS (disclosed exceedances, unchanged) | |
| V-10 | PASS (DEFERRED) | |
| **Round** | **PASS** | 0 blocking |

## DISCLOSURE LEDGER (unchanged set, all honored)

Build-note disclosures stand: seat-2 amendment (CONFIG comment + §SEAT AMENDMENT); triggerShake reuse; scoped hit-stop; journal skip; socket rows in computeFireSockets (C4 fallback); line-count exceedances (CONFIG +49 / game.js +17 / region-manager +7 / hazards.js 373 / index.html +3); IO-inline probe. NEW this round: IO amendment note `io/reports/cc-h5b-probe-amendment.md` (width-map finding + v2 remedy) — verified accurate by Testerbot's independent re-measurement and re-derivation (agreement to 0.01 m on all 4 seats, exact on 6/7 widths to stated precision).

Testerbot's own artifacts added to scratch/cc-h5b/ (audit trail, not sources): `testerbot_glb_xextents.py` (independent width measurement), `testerbot_placement_math.js` (independent B1 math), `testerbot_probe_audit.py` (PA-1/PA-2/width/floor source audit).

## REMAINING (not a verdict condition)

- Nicko's playtest acceptance (V-10, always his bar).
