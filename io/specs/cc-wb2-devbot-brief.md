# CC-WB2 Devbot build brief

Round: cc-wb2 (doc 42 Part 2 ladder on the landed CC-WB1 board).
Worktree: /tmp/wh-worldfeat (branch feat/world-visuals, HEAD a4d3736).
Build: python3 tools/build_v8.py from the repo root (exit 0 required).
No harness runs, no headless browser smoke tests - node one-shots only
(THREE shim + fake harness, /tmp/wb1_smoke.js precedent).

## LAWS (hard, from PRIMARY.md)

1. ART LAW: the board already exists; add NO new art assets. Tally pins =
   iron 0x6e6a63, no red anywhere (red = pact/danger), no second emissive.
2. NO-GIT: you NEVER commit, push, stage, or branch. You write code ONLY.
   git add/commit/push are IO-only. You may run git diff/status (read-only)
   to obey file-census laws.
3. File law: you touch ONLY prototype/js/CONFIG.js and
   prototype/js/wareffort.js (plus the built artifact via the build tool).
   game.js and index.html must remain byte-identical (their landed
   capture/restore/prompt/interact hooks already call WH_WarEffort, so the
   ladder rides them with zero wiring).
4. One scene root: the tally is a sub-group inside the EXISTING board root
   'cc-wb1-war-effort-board'. No new roots, no new DOM elements, no new
   script tags.
5. Integer arithmetic only (spec S-2 law): all money math in integer
   milli-units (m4), payouts computed exactly per S-2, round-half-up to
   coins ((payM4 + 5000) / 10000 floored). No floats in money state.
6. Nicko's playtest is the acceptance bar: no automated playtest of play-
   ability. Your node one-shots test LOGIC (payout rows, save round-trip),
   which is code QA, not playtest.

## Sources of truth

- Full spec: /tmp/wh-worldfeat/io/specs/cc-wb2-ladder-spec.md (exact
  arithmetic, quota table, pinned payout rows you must reproduce).
- Validation spec: /tmp/wh-worldfeat/io/specs/cc-wb2-ladder-valspec.md
  (you do NOT write it; Testerbot does; but READ it and self-check every
  group before finishing).
- Existing board code: /tmp/wh-worldfeat/prototype/js/wareffort.js
  (the module you are editing; keep its IIFE shape, its el() helper, its
  CONFIG-driven text law - every player-facing string stays in CONFIG).
- Doc 42 Part 2: /tmp/wh-worldfeat/docs/planning/42-*.md (the bands).

## Build steps

1. CONFIG.js: add the `ladder` key inside CONFIG.warEffort exactly per
   spec S-1 (7 fields, values verbatim, PROPOSED-tuning comments kept).
2. wareffort.js:
   a. repeatIndex int on the logic object; resolve() increments once per
      fill; rollNewDay (new-day reset path) does NOT touch it; restore()
      accepts it with clamping (non-negative int; missing/foreign = 0);
      WB1 3-key payloads restore clean as repeatIndex 0.
   b. quota at award/turn-in time = quotaQ(repeatIndex) per S-2
      (min(round(6 * 1.5^r), 18)); prompt string shows it.
   c. turn-in: when carried ore (countOf ironOre) >= quota, remove ALL
      carried ore of that id (haul grammar), pay per S-2 exact ints, add
      stolenCoin count to inventory via the SAME accessor WB1 uses today
      (do not invent a new one - mirror the landed code path).
      Below quota: the landed insufficient toast, nothing removed.
      Toast: x >= 1 -> CFG.warEffort.ladder.overDoneText, else the landed
      requisition.doneText.
   d. repeat tally pins per spec S-3 (sub-group in the board root, iron,
      render cap 8, rebuilt on resolve and restore; NOT on new-day reset).
   e. capture() payload gains repeatIndex (4 keys total).
3. Self-check: replicate every valspec group V-1..V-9 as local node
   one-shots (scratch OUTSIDE the worktree, e.g. /tmp/wb2_selfcheck.js);
   show ALL PASS lines in your report. The pinned payout table rows a..m
   must print exact matches.
4. Run python3 tools/build_v8.py; verify CC-WB2 marker count >= 6 in
   prototype/builds/v8-playable.html.

## Report back (final message)

- Files changed (paths + line deltas).
- Self-check output: the full PASS list + payout table results.
- Build output line + marker count.
- Explicit statement: game.js / index.html untouched (shas before/after).
- Any deviation from spec (expect 0; if a landed pattern conflicts with
  the spec, STOP and report the conflict instead of deciding).
