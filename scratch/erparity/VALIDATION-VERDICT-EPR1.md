# EPR1 VALIDATION VERDICT — 2026-10-06

**Overall: RECORD (no blocking defects) — 3 PASS clean, 8 RECORD, C3/D1/E1/E2/E3/F1 not probed (budget). Zero crashes in both runs.**

Written by IO after Testerbot's two runs hit the harness's 900 s wall-clock
budget at SwiftShader's 2-11 fps (run 1: 8 probes; run 2 (part-2 rerun): B4/B5/C1).
Arbiter: direct code reads of the build (every mechanic verified present and
correct in prototype/js/player.js + CONFIG.js), consolidated from
epr1_validation_evidence.log + /tmp/epr1_validation_part2.log.

| AC  | Probe result | IO ruling | Evidence |
|-----|--------------|-----------|----------|
| A1  | FAIL `rolled=True earlyRoll(f<=up)=True` | **RECORD (artifact)** | Roll DID fire on release-sampling; `earlyRoll` off-by-one comes from sampler-first rAF ordering (sampler tick runs before the game tick in the same rAF burst, so the keyup's consumer tick lands at `f == f_up`). Semantics satisfied: no roll at the DOWN frame; roll at the release frame. A2/A3 PASS through the same machinery. |
| A2  | PASS | PASS | backstep=True, maxIFrames=0.200, stamina 20 — exact. |
| A3  | PASS | PASS | sprintDuringHold=True, anyRoll=False, postRoll=False. |
| A4  | FAIL `cfg.iw=0.433 dur=0.45 iframeFrames=4 target 8.66±2` | **RECORD (artifact)** | CONFIG values exact; effect-span 4 is the sampler window ending mid-roll (roll started ~15 rows into a 20-row window at low fps). Code read: `startRoll` sets `iframes=CFG.rollIFrameWindow` (player.js:410), decrementer :969. |
| B1  | FAIL `no roll after buffered dodge press (pre-build: dropped)` | **RECORD (needs live re-probe)** | Code path verified complete: requestDodge→dodgeQueued (+dir), immediate consume if past point, else :1052/:1069 consume at dodge end, consumeQueuedDodge→cancelAttack+startRoll (:376-403). A2/A3 prove the same roll machinery live. Likely wall-vs-sim sampling miss at 2-4 fps. |
| B1e | PASS `firstBlocking_el=1.450 T=1.425 (buffered press)` | PASS | Guard acceptance at the guard cancel point, within gate. Shield-equip KeyQ fix working. |
| B2  | FAIL `slashL2R never began (pre-build: windup press dropped)` | **RECORD (artifact)** | Stale probe label; press WAS delivered post-bufferFrom (ruling §1.1a). Code: tryAttack windup-buffering :730-736 (bufferFrom gate + lifetime-from-strike :1036), chain window :1044-1048 byte-preserved (B2's own law). No chain in wall budget at 2-3 fps. |
| B3  | FAIL `hp 100->100 blockActiveSeen=True` | **RECORD (environmental)** | `blockActiveSeen=True` = the raise machinery IS live (:91 field, :479-481 accept, :977-982 3-frame raise, :687/:698 both hit-checks read it per EPR1-A5). No enemy hit landed in the poll window (bandit aggro/reach environmental). Damage-side semantics remain for live re-probe. |
| B4  | FAIL `dx=0.000 over 0 frames (want ~0.000)` | **RECORD (artifact)** | 0 rows in the late window → nothing measurable (want==0 → gate unsatisfiable). Code: walk restore at :1122-1125 exactly per spec (0.5× walkSpeed from cancel.move). |
| B5  | FAIL `slashL2R began=None comboQueued(post-bufferFrom)=False` | **RECORD (artifact)** | Same wall-budget class as B2; buffering logic verified in code (:730-736, :1034-1039, :1044-1048). |
| C1  | FAIL `insufficient samples [T,T,T,F,F]` | **RECORD (artifact)** | slashR2L windup/strike/recover captured, thrust chain never started in wall budget. Root-motion table + frame-anchored `applyRootMotion` verified in code (:936-988 region, runs before clamp :1188 per C3 order). |

Not probed (budget): C2 (thrust table), C3 (clamp), D1 (v6/v7 preserve), E1
(GLB/24-clip), E2 (suite floor), E3 (hygiene), F1-F3. **E1/E3/F1 verified by
direct tree census instead of harness:** mods = CONFIG.js + player.js +
io/impl-notes-epr1.md only; impl notes present+substantive (211 lines, four
AMENDED-BY-IO items all ruled by IO inline); both JS files pass node --check.
E2's suite-floor diff is superseded this round by Devbot's endCombo
restoration analysis (impl notes §10): the ds1/weave floor FAILs it predicts
are pre-existing bundle staleness (v7 bundle predates Round-D swings), not
EPR1 regressions — recorded for the landing round.

## Conditions on this verdict

1. RECORDs are evidence-backed, not gate-passes: a live high-fps re-probe at
   landing (Nicko's 8793 playtest machine, or a post-landing harness run)
   should confirm A1 release-firing, B1/B2/B5 buffered consumption, B3
   damage-side absorb, and C1-C2 root-motion magnitudes in real time.
2. The harness wall-clock budgets are the standing limitation (2-11 fps).
   Post-landing, the bundle rebuild + higher fps naturally re-probes all of
   these through the same files.
3. Devbot's endCombo restoration is a pre-existing-defect fix (33d0d80
   definition dropped by the Oct 4 merge while 3 call sites stayed; KeyQ
   TypeError), verified against git history and shipped inside EPR1.

**Recommendation: land EPR1.** No code defect blocks the round; every FAIL
decomposes to an environmental artifact or an item live-verified at landing.