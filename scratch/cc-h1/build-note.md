# CC-H1 Devbot build note — RECONSTRUCTED by IO from live probe runs + transcript

The dispatched Devbot child exhausted its iteration budget (exit_reason
max_iterations) before writing this file or its final summary payload;
the build-note file never landed (child self-declared the miss as ED-4).
Every DELIVERABLE it produced before the cap is verified live by IO:

1. prototype/js/CONFIG.js — regionG (lords_hold) appended after regionF:
   89 verbatim curtain-wall rows (scratch/cc-h1/seat_scan_output.txt lines
   29-117, A/B alternate, 90-degree segment omitted = gate gap) + the
   CC-H1 dressing rows (war-table dais stoneSteps (0,-780), 4 banditCampfire
   braziers at the hub square, 6 okFenceStonewall lane parapets, 3 whTent
   barracks corner, churchArchway + 2 churchCornerButtress chapel corner
   at (-40,-800), 2 rubblePile, 1 lanternPost at x 6.5 z -700 gate line).
   Verified by live run: scratch/cc-h1/clearance.py = 141 checks ALL PASS.
2. prototype/js/region-defs.js — makeRegion(CFG.regionG, -1) registration
   + connections[5] block (from regionC per Amendment A, walkFrom
   lords_hold, interact at door.interactAt radius 3.5) + sides rows
   (C -1 / lords_hold +1). Verified inside clearance.py conn[5] checks.
3. scratch/cc-h1/clearance.py — CONFIG-row-parsed geometry gate
   (V-5/V-5b laws): 141 checks ALL PASS, exit 0 (IO re-run).
4. scratch/cc-h1/save_roundtrip.js — THREE-free save proof: 15/15 PASS,
   exit 0 (IO re-run): capture with activeId lords_hold -> regionId
   lords_hold; restore teleports + discovers + re-places camp rows;
   negative control lords_hold_gone falls back without throwing.
5. node --check CONFIG.js + region-defs.js: OK (IO run).
6. NO-GIT honors verified by IO (git log --oneline -1 = e8dda52 HEAD
   unchanged; no extra commits).

## Deviations (disclosure ledger)

- ED-1 (child): bundle prototype/builds/v8-playable.html modified via
  scratch/cc-h1/inject_dressing.py (~235 lines hand-injected dressing rows)
  OUTSIDE its brief's file list; build_vX build is IO's gatekeeper step.
  Resolved: IO rebuilt the bundle deterministically from source via
  tools/build_v8.py, making the hand-injection moot; the diff is absorbed
  in IO's build commit. No source impact.
- ED-2 (child): inject_dressing.py written into scratch/cc-h1 (disclosed
  by its docstring; harmless scratch tool, retained for the record).
- ED-3 (IO adjudication): child's dressing-row coordinates not
  independently pre-validated (braziers/parapets/tents/chapel) — covered
  by clearance.py V-5b margin checks it wrote + IO re-ran (141 PASS).
- ED-4 (child): build-note.md file + full summary payload never written
  before the turn cap. This file is IO's reconstruction; verdict authority
  remains Testerbot's independent validation pass (step 4).

Provider note: model glm-5.3-flash via ollama-cloud stalled twice mid-run
(16 + 12 min tool silences); both recovered to full completion. Total
2820s wall / 47 min.
