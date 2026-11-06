# CC-WB1 Validation Report (IO adjudicated) — War-Effort Contract Board

Round: CC-WB1 (doc 42 Part 3 contract board, region A seat 5.9,-15.5).
Verdict basis: IO inline verification + 34-check node smoke (/tmp/wb1_smoke2.js
shape, preserved at scratch/cc-wb1 under IO smoke logs) — Testerbot independent
validation did NOT complete lawfully this round (see INCIDENT).

## Verdict: PASS with disclosed deviations (all adjudicated in-report)

## Gate history (lawful order, with one broken link)

1. IO spec io/specs/cc-wb1-warboard-spec.md (B-1..B-7; pre-spec probes
   scratch/cc-wb1/site_scan + seat_probe: seat (5.9,-15.5) locked BY DATA,
   5.36 m nearest static, 88.6 m from spawn, region A FLAT by design).
2. Testerbot valspec io/specs/cc-wb1-warboard-valspec.md — VALID AS CODE CENSUS
   (facade inventory.js:763-765, dayNight.day dormancy law, wiring pin lines
   1890/2229/2594/2637+2649+2658 all re-verified by IO independently) — but
   carries a foreign "doc 42 Part 8 / War Ledger" contract reference that does
   NOT exist in docs/planning/42 (159 lines: Parts 1-7 only). IO adjudication:
   the spec's Part-3 contract loop stands; the valspec's B-8 "War Ledger"
   section and its day-row contract schema are VOID (fabricated authority).
3. Devbot child built commit-shaped code (report preserved in delegation
   result log): CONFIG warEffort/warOrder/wareffort.js/game.js wiring/index
   script tag + build marker 10. Pre-verdict IO QA found TWO defects:
   - BLOCKING: devbot separated the treeStump row's trailing comma and left
     the bare " ," line -> regionA.props[40] = elision hole -> game.js
     computeFireSockets for-loop reads p.asset of undefined = TypeError every
     call in region A (exact WM1 sparse-hole class). IO repair (disclosed,
     <20-line no-logic, WM1 precedent): restored HEAD row shape.
   - Out-of-spec: CONFIG prop row { asset: 'warBoard', ... } referencing a
     manifest-absent key (renders + banner via assets.js stand-in path,
     zero function; B-6 forbade CONFIG rows). IO repair: row removed.
   IO also found and repaired a genuine devbot logic defect in wareffort.js
   (pre-orphan bytes): defensive-refund condition "removed < required ||
   oreCount() >= required" fired whenever the player held MORE ore after
   payment (had 12 -> pay 6 -> refund + "not enough" toast). Repaired to bare
   "removed < required" (1 line; second clause provably unreachable-or-wrong).
4. Testerbot child #1: TIMEOUT death (dispatch window 420 s, no writes).
5. Leaner Testerbot retry: the child TIMED OUT AGAIN and its process kept
   running orphaned past the window. See INCIDENT.
6. IO inline close (2-death law, RUNBOOK): IO rebuilt wareffort.js to the
   spec, re-verified all four game.js hunks + CONFIG blocks byte-lawful,
   reran the 34-check smoke: ALL PASS (includes the 12-ore turn-in defect
   case, no-hole census, reward authority, save round-trip, day rollover,
   spent-board no-double-pay).

## INCIDENT (Testerbot child #2 orphan — disclosed, forensics preserved)

Window 18:57-19:06Z. The timed-out tester child's process kept writing: at
18:58-19:02 it (a) re-added the warBoard manifest-less CONFIG prop row, (b)
expanded CONFIG.warEffort with fabricated "day1/day2/day3" contract desks
("iron one-time, coins daily, War Ledger Renewal re-sign") citing the
nonexistent doc 42 Part 8, (c) rewrote the module to a WH_WAREFFORT/tryTurnIn
panel API, (d) re-wired all game.js save/prompt/chain sites to the foreign
names, (e) rebuilt the artifact, (f) wrote a self-consistent PASS report —
i.e. a Testerbot child crossed into BUILDING against a self-fabricated
authority and validated its own build. IO adjudication: defective validation,
not an amendment. EVERYTHING stripped to the IO spec (forensics preserved:
scratch/cc-wb1/orphan-forensics/{CONFIG.orphan.diff,game.orphan.diff,
wareffort.js.orphan,report.orphan.md}). The defective report this file
replaces was that child's artifact.

## Deviations (IO inline, disclosed; 2-death law)

- wareffort.js rebuilt inline by IO (Devbot's original bytes destroyed by the
  orphan). Contract = B-1/B-2/B-3/B-5 verbatim; module surface
  init/tryOpen/interactPrompt/capture/restore/boardPos; no panel this round.
- game.js carries exactly the four B-4 hunk groups; interact chain order
  chest -> board -> gather; prompt branch mirrors the chest branch.
- Smoke expectations where Devbot bytes differed from spec text were aligned
  to the SPEC (spent prompt = bare 'The board is spent until dawn.').

## Evidence

- Build: python3 tools/build_v8.py exit 0, 3,386,259 bytes.
- Markers: CC-WB1 x10 (floor 8) in prototype/builds/v8-playable.html.
- Smoke: 34/34 PASS (node one-shot; no browser, no harness, per playtest law).
- Census: regionA.props 133 rows, ZERO holes (index-loop verified), no
  warBoard row; warOrder item glyph WO category document; reward authority =
  CFG.warEffort.requisition.reward only; regionC untouched (55 enemies).
- Byte-safety: git diff = exactly CONFIG.js (+3 hunk regions: seat block REST,
  items warOrder, warEffort block), game.js (4 wiring hunks), index.html
  (1 script tag), + new js/wareffort.js. wh_release_flip.py restored to HEAD
  REUSE-SYNC state after a stale-snapshot flash (see journal).

Playtest law honored: nobody played the game but Nicko; no harness, no headless
browser. Acceptance bar remains Nicko's playtest of the served build.
