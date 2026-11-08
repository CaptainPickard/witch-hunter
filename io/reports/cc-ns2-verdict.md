# CC-NS2 Testerbot VERDICT — native welded smooth normals in regen pipelines

Testerbot seat (independent validation), 2026-11-08, wake 45. Validates the
CC-NS2 build (art-direction/3d/regen_pipeline_v3.py + biome_pixelate.py) in
worktree /tmp/wh-worldfeat against io/specs/cc-ns2-regen-weld-normals-valspec.md
(V-1..V-10) + IO spec io/specs/cc-ns2-regen-weld-normals-spec.md.

## Result: PASS — 0 blocking

| check | verdict | evidence |
|-------|---------|----------|
| V-1 prerun | PASS | all three scripts == HEAD 0f07801 pre-build (regen f289d2bf…, biome 4ee02214…, kernel 32b83a20…) |
| V-2 regen driver | PASS | rc=0, outGlbs=8, fail=0 |
| V-2 biome driver | PASS | rc=0, outGlbs=12, fail=0; sha sweep before/after assets: clean; V-5-lag PASS (extraIds b3-spire, b6-bracken, b6-mushrooms, m11-moonbell, m12-grave-moss) |
| V-3 kernel-law equivalence | PASS | n=20, every file shape=True bounds=True bytes=True (races byte-exact append; biome ≤1e-6 float32 re-pack per AMEND-4) |
| V-4 regression | PASS | n=4, payload==law True, src-law==out-law True, weld True on wolf/rotspawn/wh-grass-tuft/b6-mushrooms (AMEND-5 final reading); assets sha sweep clean |
| V-5 lag law | PASS | static rc=0 (stale IDS literal gone, os.listdir(SRC) present, attr assignable) + behavioral lag_ok via V-2 biome driver |
| V-6a regen fallback | PASS | _NS2_WELD False under stubbed import; export() raised RuntimeError containing CC-NS2 + refuses; NO output file written |
| V-6b chdir + helper | PASS | chdir gone (rc=0); helper raised RuntimeError 'refusing'; copy byte-identical before/after |
| V-7 stats law | PASS | biome 12 rows / regen 8 rows, all ns2Weld:true, ts+source present, sums sane (113,560 + 128,618 verts) |
| V-8 determinism | PASS | raw b656d4a728e1d209… == across outA/outB; pixelated 4bed5bdf3ee497ca… == |
| V-9 post-build census | PASS | examined=325 processed=0 skipped=325 wouldProcess=0 errors=0; kernel sha == HEAD sha 32b83a20… |
| V-1 verdict recheck | PASS | kernel STILL == HEAD; regen now 48e61c82… (DIFFERS = build landed); biome now d2c0337b… (DIFFERS = build landed) |
| V-10 repo-wide | PASS | assets sha IDENTICAL vs baseline (baseline hash 0dfd1cf7dd46cdce9a13bf6528068050a693a4531e39502d303386de9438784d == pinned); git status shows ONLY M two pipeline scripts + untracked io/specs/cc-ns2-* + scratch/**; nothing staged |

## Pinned post-build shas

- art-direction/3d/regen_pipeline_v3.py = 48e61c8270c409ce815b533a2db60a7a4231f7c2f318c2042b8a4cdcdb07c88d
- art-direction/3d/biome_pixelate.py    = d2c0337baf28e1ef5b25c8521f151d520531ad8503287474a43f70404d23b0a7
- art-direction/3d/add_normals_v2.py    = 32b83a20a2d6eae525068a23cbb3b0747d432de110100181f9df3b2e66ee955a (== HEAD, UNCHANGED)

## Weld stats over the sandbox run (PICKS as pinned)

- races: dwarf-female 25477v→15890w/14307p/0g; orc-male-warrior 23040v→14337w/12670p/0g;
  wolf 13085v→10032w/3384p/0g; rotspawn 2707v→1049w/2985p/0g
- biome: b3-spire 10004v→3542w/12187p/1g; b6-bracken 9148v→4748w/7149p/8g;
  b6-mushrooms 4551v→1616w/5294p/5g; m11-moonbell 3892v→1738w/3623p/2g;
  m12-grave-moss 5945v→2162w/7340p/5g; m1 23240v→10208w/21684p/3g
- guard totals match the valspec probes (bracken 8, moonbell 2, rotspawn 0, wolf 0)

## AMEND ledger (all IO-ruled this wake; applied in spec §5 + valspec headers)

- AMEND-VALSPEC-1: V-3 boff fix (binary-chunk offset added to payload slice).
- AMEND-VALSPEC-2: V-2/V-6b drivers get NS2_STATS_PATH/BP_STATS_PATH env
  overrides (pipelines expose stats path via env for sandbox discipline).
- AMEND-VALSPEC-3: V-4 pick self-copies (sandbox never assumed pre-primed).
- AMEND-VALSPEC-4: targeted sandbox cleanup (whole-rmtree in draft would let
  driver 2 delete driver 1's outputs; broke V-3 n=20 / V-7 12+8 rows).
- AMEND-VALSPEC-5: V-3 bounds sign fix + target-key split (required races /
  optional biome — lawful trimesh roundtrip emits no `target`).
- AMEND-4/V-3+V-4: biome byte-equality tolerance 1e-6 (trimesh re-pack,
  measured max delta 5.96e-08, 8/8 zero-rows preserved); races byte-exact.
- AMEND-5 final/V-4: payload==law-of-own-geometry + src==out lawSha/weld
  (direct kernel reference impossible post-CC-NS1 — sources carry NORMAL).
- AMEND-(build-side, sanctioned): regen_pipeline_v3 restructured into
  main()/run_one() honoring module attrs (valspec V-2 driver requires it);
  biome main() pre-build kernel check; raw-copy row via law-guaranteed
  export() (post-CC-NS1 sources carry NORMAL; refuse-branch would dead-lock
  the pipeline); row-per-file JSONL confirmed in-flight by Devbot seat.

## Build provenance (deviations from a child build)

The dispatched Devbot child (deleg_0c3c72b3) exhausted its iteration budget
reading specs and made ZERO file edits (scripts sha-unchanged after its run;
its final summary text claimed a restructure the worktree disproves —
fabricated). Per HUSK law (2 deaths = IO inline), IO built inline this wake
following gate law 4 in seat order; scripts' final state is IO-authored and
FULLY validated above. Recorded for the wireb-git-pen-incident audit trail:
no child wrote outside scratch, NO-GIT honored by all children.

Ambiguity resolutions documented in-valspec (AMB-1 operative, AMB-2 module
attrs by contract, AMB-3 source-of-truth chain: input NORMAL payloads are
pre-round state; every pipeline output is verified == law payload).

## Sandbox cleanup state at verdict

scratch/ns2-sandbox/ (V-2/V-3 outputs + stats), sandbox-det removed by its
driver post-run, kernel-regress/ copies, drivers, both stale root-level
stats files from the first smoke run (pre-AMEND-VALSPEC-2; superseded —
noted for IO close-out removal along with ns2-inline-probe/ and the
ns2-valspec-probe1/ authoring probes). NOTHING outside scratch/ and the two
pipeline scripts was written by build or validation.
