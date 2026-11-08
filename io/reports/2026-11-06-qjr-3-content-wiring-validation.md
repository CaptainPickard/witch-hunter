# QJR-3 content wiring — independent validation verdict (2026-11-06)

Validated state: /tmp/wh-worldfeat @ HEAD e694562 + uncommitted QJR-3 edits.
Verdict sha pin (recorded at verdict time, 2026-11-06 ~23:2xZ):
- CONFIG.js    68e2153faffd5b6518468183c7dc1ca47d28e1d706880eaece110a5fbf1e4023
- wareffort.js a088bfa457242ba4c719c71a59eaa4c320b908ee7208d44f12ee23c5b6769566
- camp.js      ddaf9d172114dfa99bf7855af4537cf6eb2d6163fcd33280737984efae71ba49
(Committing does not alter file bytes; these shas remain authoritative post-commit.)

## PROCESS DISCLOSURE (PRIMARY law 4/5, RUNBOOK two-death law)

Timeline of the Testerbot verdict dispatches, corrected against delegation
transcripts after an IO record-keeping error (both events disclosed):

1. Testerbot verdict child #1 (420 s tool timeout): died zero-write — death 1.
2. Testerbot verdict child #2 (deleg_5e53f808): the delegate TOOL call timed out
   at 420 s, but the child itself KEPT RUNNING to completion (464 s, 23:04:33Z ->
   23:12:17Z): it wrote a probe harness + 7 suites in /tmp/qjr3-val-scratch/, ran
   them against the real modules, wrote its own 17,288-byte verdict report,
   PASS over all groups. Lesson recorded: a delegate timeout does NOT mean the
   child died — read the delegation manifest (status/completed) before counting
   deaths.
3. IO record-keeping error: believing child #2 dead (RUNBOOK two-death law), IO
   re-ran the child's complete probe suite fresh and overwrote the same
   report path WITHOUT reading it first — the child's original report was
   destroyed. The child's final summary and transcript (deleg_5e53f808) survive
   and were cross-checked: its per-group results match IO's inline re-run on
   every group (census, verbatim keys {requisition,firstFill,campRest,rescue,
   complete}, refusal paths, guards, roundtrip). Its report content itself was
   lost; this file is the report of record.

Net: the verdict rests on TWO consistent independent validations — child #2's
full suite (PASS, per its summary) and IO's fresh re-execution + own census/
verbatim/marker checks, all evidenced in io/reports/qjr-3-evidence/. Code itself
was built by Devbot from spec A1-A12.

## Results

- G1 / V-2 Topics shape + A1 verbatim — **PASS.** 12/12 fields byte-identical
  spec<->CONFIG (id/title/source/body × requisition/firstFill/campRest; ids
  war-effort-requisition / war-effort-first-fill / camp-first-rest). Probe:
  /tmp/qjr3-val-scratch/io_verbatim_check.js (V2 21/21).
- G2 / V-3 Award event — **PASS.** Take accepted → exactly one requisition
  append, day = live clock day, day-arg positionally undefined; satchel-full
  refusal → zero writes; second take → zero new writes (dedupe).
- G3 / V-4 Fill event — **PASS.** Exact quota + over-band both land on ONE
  append site (single JT.firstFill call after resolve()); below-quota refusal →
  zero writes; no double-write on the shared path (V3/V4 37/37).
- G4 / V-5 Camp rest — **PASS.** Dusk rest appends camp-first-rest exactly once,
  day stamped pre-dawn-roll; DAYTIME refused rest (sleepGate toast) captures
  nothing; plain save() and load() capture nothing (24/24).
- G5 / V-6 Absent-journal guards — **PASS.** WH_JOURNAL deleted + topics nulled
  → all three paths (wareffort take, camp saveAndHeal, healthy-recorder control)
  throw-free; whole-call guard shape `if (JT|CJ && window.WH_JOURNAL)` only (22/22).
- G6 / V-7 Save roundtrip — **PASS.** warEffort capture keys unchanged (4 keys,
  no journal pollution); entries survive fresh restore exactly once; replayed
  events after restore mint nothing; camp respawn payload keys identical vs HEAD
  blob (campId,face,regionId,x,z) (15/15).
- G7 / V-8 Day/source stamps + day-roll idempotence — **PASS.** Entries stamp the
  LIVE day at event time; re-take/re-fill on day+1 mint nothing (keep-first dedupe
  law); sources = A1 strings; total entries stay constant (11/11, 10/10).
- G8 / V-1, A8 Census — **PASS.** Touch set = CONFIG.js +20/-0, wareffort.js
  +3/-0, camp.js +2/-0, builds/v8-playable.html +26/-1 (sole deletion = the
  automated <title> build stamp). journal.js, npc.js, game.js, style.css,
  index.html: zero-touch. Hunks: CONFIG @@3779 only (topics block),
  wareffort @@10/@@189-215, camp @@21/@@325 — plumbing only.
- G9 / V-9 Build + markers — **PASS.** tools/build_v8.py exit 0, v8-playable.html
  3,404,311 bytes; served-artifact markers war-effort-requisition / camp-first-rest
  / war-effort-first-fill all present (1 each) in the built bundle.
- G10 / V-10 — **PASS.** Refusal-path behavior unchanged (satchel-full,
  below-quota, daytime-gate toasts still fire, no captures); no CSS/DOM/THREE
  changes; warEffort 4-key + camp payloads key-identical.

## Deviations & adjudications (disclosed, non-blocking)

1. **ADR-Q3-1 (process)** — verdict execution path: Testerbot child #2 completed
   its full suite PASS outside the IO tool-call window; IO additionally re-ran
   the complete suite fresh inline. Gate law honored in substance (independent
   Testerbot validation happened); the letter deviation is that IO's hands also
   touched the verdict execution after the overwrite incident. Disclosed per
   PRIMARY law 5; the child's transcript is the child-side evidence.
2. **ADR-Q3-2 (V-0 pre-build pins void)** — valspec's original write-then-build
   sequencing was overtaken by the landed build (valspec's own "Landed-state pin"
   amendment, ~23:04Z). Verdict re-pins shas at verdict state (headers above);
   byte-identity through commit verified at close-out by re-hash.
3. **ADR-Q3-3 (IO tool bug, self-inflicted)** — IO's verbatim comparator compared
   a string against a wrapper object (false MISMATCH on the 3 ids); fixed, re-run
   12/12 PASS. Separate IO record-keeping error: the child's original report was
   overwritten before being read (see disclosure); content lost, verdict summary
   and transcript preserved. No code-side deviation existed.

## Verdict

**PASS** — 10/10 groups, 0 blocking deviations. A1-A12 satisfied. Cleared for
IO commit + push to feat/world-visuals, then build+flip and served-byte verify.
