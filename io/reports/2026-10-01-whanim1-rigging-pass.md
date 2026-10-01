# whanim1 Rigging Build — Independent Testerbot Validation Report

- **Round:** whanim1 (Witch Hunter 10-character rigging + retune)
- **Valspec of record:** `/home/hermeswebui/.hermes/profiles/io/specs/testerbot-spec-whanim1-rigging.md`
- **Repo:** `/workspace/witch-hunter`, branch `dev`
- **Validator of record:** `tools/rigging/scripts/verify_wh_glb.py` invoked via `tools/rigging/scripts/bl.sh` (Blender 4.3.2)
- **Validated by:** Testerbot (independent re-run of every §2 procedure; Devbot's own VERIFY PASS lines treated as evidence, never proof)
- **Date:** 2026-10-01

## Per-AC Verdict Table

| AC | Procedure | Verdict | Key Evidence |
|----|-----------|---------|--------------|
| A1 | Hygiene set-difference vs frozen baseline | **PASS** | porcelain=72 lines; subtraction = empty set; `.gitignore` diff adds exactly `tools/rigging/blends/`, nothing else; blends dir absent from porcelain (ignored, not untracked) |
| A2 | 10 source GLB sha256 unchanged | **PASS** | All 10 match frozen sha256s (a9bf9dbf…, 6b012a7d…, bd49a691…, 10997f6c…, ed0549f5…, e595c84b…, 365a4a45…, 5922c3fd…, a1e3817…, b37b344a…) |
| A3 | Per-GLB extended validator VERIFY PASS | **PASS** | Testerbot re-ran the validator on all 10 rigged GLBs against their sources: rc=0, 43/43 ok lines each, tail `VERIFY PASS` each. My logs: `/tmp/testerbot-logs/testerbot-<stem>.verify.log` |
| A4 | Clip set = exactly the 6 WH clips | **PASS** | Independent GLB JSON parse: every char has exactly {WH_Idle, WH_Walk, WH_Run, WH_Attack1, WH_Hit, WH_Death}, no extras/renames |
| A5 | Attack1 0.500±0.02s; Hit 0.333±0.02s | **PASS** | Attack1 = 0.500s, Hit = 0.3333s on all 10 (independent parse, max input time per clip) |
| A6 | Root static (0 drift) all clips | **PASS** | 60/60 Root-drift lines ok ("max drift 0.00e+00") in my runs (6 clips × 10 chars) |
| A7 | Idle/Walk/Run loop closure (Hips first==last) | **PASS** | 30/30 loop-closure lines ok in my runs (3 clips × 10 chars); Hips returns to start 0.00e+00, sway < 0.05 |
| A8 | Excursion floors (retune proof) | **PASS** | human-hunter-male: Walk L/R_Thigh **0.4475 rad ≥ 0.30**; Attack1 L_UpperArm **1.0720 ≥ 1.0**, R_UpperArm **1.8470 ≥ 1.0**. Retune proven vs UNtuned reference-sample.glb (Attack1 L_UpperArm 0.4363→1.0720, R 2.7839→1.8470 balanced; Walk thigh 0.4166→0.4475). Full 60-row roster table below. Excursion mode present in every run (not behind a flag) |
| A9 | Ghoul honest outcome | **PASS** (full pass, not conditional) | Ghoul GLB exists and passed A3–A8 identically to all others (rc=0, 43/43, VERIFY PASS, excursions present, textures identical). No known-fail needed |
| A10 | Manifest complete + preview dirs | **PASS** | `tools/rigging/rig-manifest.md`: 11 sections (10 chars + first human-male attempt 02:24:40Z, append-only), each with Overrides/VERIFY PASS/preview path/verify log path/anomalies. All 10 preview dirs contain the standard 13-file frame set |
| A11 | Git log untouched | **PASS** | HEAD = eacff4aed406ba9ef736cb42309d75d0f3445bda; top-3 log unchanged (eacff4a/8e8a015/395c5d8); reflog shows no new commits/resets; refs = dev+main only, 0 tags; nothing staged (staged_bytes=0) |
| A12 | Texture sha unchanged per output | **PASS** | 10/10 "image bytes bit-identical" ok lines in my verify runs (source vs rigged, sha256 match) |

**Suite counts (Testerbot's own executed checks): passed 701 / failed 0.**

## A8 Roster-wide excursion table (rad, from Testerbot's own verify runs)

All 10 characters are batch-clones of the tuned human-male animation set (human-male-tuned, batch-applied per valspec §A5 rationale), so per-clip values are uniform across the roster. No character shows a suspicious "0.01 rad walk thigh" — the minimum Walk thigh excursion anywhere is 0.4475 rad, well above the 0.30 floor.

| char | Walk L/R_Thigh | Run L/R_Thigh | Attack1 L/R_UpperArm | Attack1 L/R_Thigh | Hit Spine | Death L_Thigh |
|------|----------------|--------------|----------------------|-------------------|-----------|---------------|
| human-hunter-male | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| dwarf-female | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| dwarf-male-smith | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| elf-dawn-refuser-male | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| human-hunter-female | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| orc-female | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| orc-male-warrior | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| undead-ghoul-male | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| vampire-female | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |
| vampire-male-noble | 0.4475 / 0.4475 | 0.7386 / 0.7386 | 1.0720 / 1.8470 | 0.2430 / 0.2081 | 0.1723 | 0.6106 |

Retune proof (rigged vs UNtuned `tools/rigging/reference-sample.glb`): Walk thigh 0.4166 → 0.4475; Attack1 L_UpperArm 0.4363 → 1.0720 (now above the 1.0 floor); Attack1 R_UpperArm 2.7839 → 1.8470 (over-wound windup balanced).

*Full 60-row table: `/tmp/testerbot-logs/excursion-table.md`* (all ten characters identical per-clip values; verified programmatically — none below floors).

## §3 Post-build Vision QA (independent renders + reads)

Rendered my own preview sets with the standard frame spec to the sanctioned new subdir `tools/rigging/previews/testerbot-qa/{human-hunter-male, undead-ghoul-male, dwarf-female, orc-male-warrior}/` (validator render mode, tail `VERIFY PASS` per run). My renders are **pixel-identical to Devbot's shipped previews** (0.00% diff, max delta 0 on 16 same-frame pairs) — Devbot's preview evidence is honest, not staged.

### human-hunter-male (tuned reference — minimum required)
| Frame read | Verdict | Notes |
|---|---|---|
| REST:1 front | PASS | Natural A-pose, no breakage, cloak drape clean |
| WH_Walk f8 vs f23 front | PASS | Frames objectively differ (9604 px changed >10 gray, 6.5%); vision model initially read both as "static" from the front — investigated, not waved through |
| WH_Walk f8 vs f23 side | PASS | Both read mid-stride; objective tiebreaker run (below) |
| WH_Attack1 f5 vs f9 front | PASS | f5 windup (right arm raised high, torso twisted left) vs f9 recovery (arm swept down/out, torso unwound) — **clearly different, reads correctly** |
| WH_Attack1 f5 vs f9 side | PASS | 9059 px changed (6.1%) |
| WH_Death:36 front | PASS | Prone face-down collapse, limbs splayed naturally, no candy-wrapper joints |

**Vision-model ambiguity investigated and resolved (important methodology note):** On the front/side walk pair, the vision model read both f8 and f23 as similar "standing/left-leg-forward" poses. Per valspec §3.2 this is exactly the defect class that cannot be waved through, so I ran **objective motion extraction** instead of accepting a weak read:
- Keyframe probe (`/tmp/testerbot-logs/keyframe_probe.py`): at f8 (t=0.267s) L_Thigh pitch +25.64° vs R_Thigh −25.64°; at f23 (t=0.767s) they swap exactly. Anti-phase by construction.
- Blender runtime foot-position test (`/tmp/testerbot-logs/stride_test.py`): L_Foot moves **+0.695** units forward while R_Foot moves **−0.698** (f23 vs f8) — a full stride-swap. Ghoul +0.701/−0.701, dwarf +0.684/−0.684, orc +0.674/−0.681. **All four QA'd characters have objectively alternating, living walks.** The vision reads were a silhouette L/R-mirroring ambiguity (f23 is the half-cycle mirror of f8), not a dead pose.
- Attack objective test (`/tmp/testerbot-logs/attack_test.py`): R_Hand travels 0.73–1.40 units between windup and strike frames on all four characters; z drops ~0.7–0.8 units (a real swing arc).

### undead-ghoul-male (known-risk hunched build — minimum required)
| Frame read | Verdict | Notes |
|---|---|---|
| REST:1 | PASS | Hunched shamble posture retained, no breakage |
| WH_Walk f8 vs f23 side | PASS | Different stride phases confirmed by vision read (right leg forward at f23 vs left at f8) **and** objective anti-phase foot swap (+0.701/−0.701) |
| WH_Attack1 f5 vs f9 front | PASS | f5 right arm raised high above head (windup) vs f9 swept down/out — clearly different |
| WH_Death:36 front | PASS | Face-down prone fall, arms flung in V, plausible collapse, mesh cohesive |

### Spot-checks (2 extra per protocol: dwarf-female humanoid-dress, orc-male-warrior bulky)
- **dwarf-female:** walk f8/f23 side views both read "left leg forward" (the same silhouette-mirror ambiguity); objective foot test proves anti-phase (+0.684/−0.684). Skirt deformation smooth, no clipping errors. Attack pair: 1.3 unit hand travel, windup→sweep. PASS.
- **orc-male-warrior:** walk f8 reads natural stride, minor LBS knee/boot volume loss noted (cosmetic, not breakage). Attack f5/f9 front pair differs 11% pixel-changed; vision read of f9 side view flagged sword/hip clipping — but the orc's weapon is a parented prop (not skinned to arm bones), so this is expected prop-follow behavior, not a skinning defect; hand travel 0.75–1.40 units confirms the swing. PASS with cosmetic notes.

### Skinning-artifact watch (valspec §3.2)
Cloak/skirt clipping through legs during wide strides noted on human male and dwarf female — this is the expected cloak-thigh weight coupling already documented in the runbook's anomaly notes class ("pending preview inspection; geometry/texture checks passed"), is cosmetic, does not affect the ACs, and is runtime-tunable. No collapsed joints, no garbled geometry, no exploded vertices observed on any frame read.

## §4 Honest-partial evaluation

- Ghoul: **full PASS** — exists and passed identically to all others. No conditional verdict needed; §4 ghoul-only partial does not apply.
- No other character missing, no validator check failed, hygiene clean, sources frozen, git untouched, excursion tooling present, floors met, clip/duration/root/loop checks green, vision QA found no dead pose (objective motion evidence overrode an ambiguous silhouette read, in Devbot's favor, with data).
- **No tolerance stacking.** Every AC is a clean PASS.

## §6 VERDICT JSON

```json
{
  "round": "whanim1",
  "per_ac": {
    "A1": "PASS",
    "A2": "PASS",
    "A3": "PASS",
    "A4": "PASS",
    "A5": "PASS",
    "A6": "PASS",
    "A7": "PASS",
    "A8": "PASS",
    "A9": "PASS",
    "A10": "PASS",
    "A11": "PASS",
    "A12": "PASS"
  },
  "evidence": [
    "/tmp/testerbot-logs/testerbot-*.verify.log (10 files, Testerbot's own validator runs, all rc=0 43/43 VERIFY PASS)",
    "/tmp/testerbot-logs/excursion-table.md (60-row roster excursion table)",
    "/tmp/testerbot-logs/keyframe_probe.py + output (thigh anti-phase proof)",
    "/tmp/testerbot-logs/stride_test.py + output (world-space foot anti-phase, 4 chars)",
    "/tmp/testerbot-logs/attack_test.py + output (world-space hand travel, 4 chars)",
    "/tmp/testerbot-logs/reference-sample.verify.log (UNtuned sample excursions, retune proof)",
    "tools/rigging/previews/testerbot-qa/{human-hunter-male,undead-ghoul-male,dwarf-female,orc-male-warrior}/ (48 renders, pixel-identical to Devbot's)",
    "tools/rigging/rig-manifest.md",
    "tools/rigging/logs/*.verify.log (Devbot's runs, corroborated)",
    "tools/rigging/previews/<stem>/ (10 dirs, standard frame set)"
  ],
  "suite": { "checks_passed": 701, "checks_failed": 0 },
  "secrets_clean": true,
  "verdict": "PASS",
  "notes": "Ghoul full PASS — no conditional path needed; all 10 rigged GLBs passed my independent 43-check validator runs (rc=0 each), excursion floors met on the human male (Walk thigh 0.4475>=0.30, Attack1 upper-arm 1.0720/1.8470>=1.0) and the retune is proven against the untuned reference sample. Vision QA: walk/attack frame pairs differ visibly and pose plausibly on human-hunter-male and undead-ghoul-male (plus dwarf-female and orc-male-warrior spot-checks); where the vision model initially read the walk pair as similar from the front, I resolved it with objective world-space foot/hand extraction proving anti-phase strides (+/-0.70 units) on all four QA'd characters — the ambiguity was silhouette mirroring, not a dead pose. My renders are pixel-identical to Devbot's previews (evidence honest). Cosmetic-only notes: cloak/skirt leg clipping during wide strides, minor LBS knee volume loss on orc; runtime-tunable, not blockers. Devbot hit its 30-min wall-clock limit before writing a final summary; its in-repo manifest+logs+GLBs are complete and consistent. IO should commit and push."
}
```