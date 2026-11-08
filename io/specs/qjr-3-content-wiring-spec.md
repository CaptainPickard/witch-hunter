# QJR-3 — Journal content wiring: board clerk + camp folk (IO spec)

Date: 2026-11-06. Author: IO. Branch: feat/world-visuals. Worktree: /tmp/wh-worldfeat.
Gate: Testerbot valspec BEFORE Devbot build; Testerbot verdict AFTER; IO commits/pushes.
Acceptance bar: code QA by Testerbot (node one-shots, no harness runs, no headless
browser); playability acceptance = Nicko's own playtest, out of scope here.

## Goal

Backfill the journal (QJR-1 core, QJR-2 capture/search, both landed on e694562)
with the remaining existing-content voices named in the backlog: the war board's
clerk ("board clerk") and the camp folk, plus one setting/lore line that anchors
findDaughter. No new systems, no new NPCs/bodies, no CSS changes.

## Context (ground truth census, 2026-11-06)

- Journal core: prototype/js/journal.js — WH_JOURNAL = { init, update, capture,
  restore, append, isBorn, isOpen, closeForTest }. append(id, title, body, day,
  source) dedupes by id, stamps day (game.dayNight.day or arg), newest first.
- QJR-2 capture sites (the pattern this round copies): prototype/js/npc.js
  - openDialog() rescued->complete: `if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.complete.id, JT.complete.title, JT.complete.body, undefined, JT.complete.source);`
  - tryRescue(): same guard shape with JT.rescue.
  - Guard law: module-local `var JT = window.WH_CONFIG.journal && window.WH_CONFIG.journal.topics;`
- Topics registry: prototype/js/CONFIG.js `window.WH_CONFIG.journal.topics` (only
  rescue + complete exist today).
- War board: prototype/js/wareffort.js IIFE. Award branch = tryOpen() idle path
  (after `logic.active = true; logic.postedDay = dayNumber();` + offer toast, the
  `added < 1` refusal returns early). Fill branch = tryOpen() active path, only
  past the `have < quota` refusal and the defensive remove check, right where
  resolve()/setPapersVisible(false) run. Headless-safe module (no DOM panel).
- Camp: prototype/js/camp.js. saveAndHeal() holds a dusk/night gate
  (`K.text.sleepGate` toast on refusal); refused daytime rests must NOT capture.
  Plain save() (respawn only) must NOT capture. K = CONFIG.camp, CFG = CONFIG.
- Panel art law: journal panel already complies (darkwood frame #1a1510/#4a4034,
  parchment page #e3dcc4, single amber accent #d8b24a; QJR-1/QJR-2 verdicts).
  concept-04-tavern anchor; no style.css work this round.

## Scope

IN: 3 new topics in CONFIG.journal.topics; 2 append sites in wareffort.js; 1 append
site in camp.js; verbatim copy below; build via tools/build_v8.py; markers land in
built v8-playable.html.
OUT (do not touch): npc.js (findDaughter/rescue/complete already wired — quest lore
is carried by the camp-folk line's wording), style.css, journal.js (no model
changes), any quest/economy logic, toasts/interact copy, save schema (journal block
already persists entries; warEffort/camp payloads unchanged).

## Requirements

A1. CONFIG.journal.topics gains exactly 3 objects. Copy VERBATIM (escaping JS-safe):
  requisition:
    id: 'war-effort-requisition'
    title: 'Requisition papers'
    source: 'The quartermaster'
    body: "I took requisition papers from the war board. The quartermaster wants iron for the front - full quota pays coin, excess pays a bonus. The garrison's hunger grows with every report from the pass."
  firstFill:
    id: 'war-effort-first-fill'
    title: 'Iron delivered'
    source: 'The quartermaster'
    body: 'Haul delivered at the war board. The quartermaster marked the tally and paid coin for the quota, a bonus for the extra. The garrison feeds the forge, the forge feeds the war.'
  campRest:
    id: 'camp-first-rest'
    title: 'Taken in at the camp'
    source: 'Camp folk'
    body: "The camp folk shared their fire and patched my wounds - for coin or kindness, they did not say. They whisper about the barrow west of the dead trees, the Old King's Barrow, where the mist keeps its own accounts."
A2. A9 law: append call sites reference only CONFIG fields (JT.requisition.*,
  JT.firstFill.*, JT.campRest.*) — no inline player-facing strings at call sites.
A3. wareffort.js adds module-local `var JT = CFG.journal && CFG.journal.topics;  // QJR-3`
  beside the other registry vars (top of IIFE).
A4. wareffort.js award branch: after the paper is actually awarded (the
  `logic.active = true` path — NOT the satchel-full refusal), fire
  `if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.requisition.id, JT.requisition.title, JT.requisition.body, undefined, JT.requisition.source);  // QJR-3`
  Guard shape identical to npc.js QJR-2 sites (whole call gated, not inner fields).
A5. wareffort.js fill branch: after a successful fill (post-resolve(); both the
  exact-quota and the over-band toast path share one site), fire the same guard
  shape with JT.firstFill.*. One id — the over-band path must not double-write.
A6. camp.js adds module-local `var CJ = CFG.journal && CFG.journal.topics;  // QJR-3`
  and fires inside saveAndHeal() AFTER the dusk/night gate passes (refused daytime
  rest never captures):
  `if (CJ && window.WH_JOURNAL) window.WH_JOURNAL.append(CJ.campRest.id, CJ.campRest.title, CJ.campRest.body, undefined, CJ.campRest.source);  // QJR-3`
A7. Guard law everywhere: append must be a no-op when WH_JOURNAL or topics are
  absent (headless one-shots, old bundles). No crashes from a missing journal.
A8. Zero-touch: no deletions; every addition tagged `// QJR-3` (CONFIG block may
  carry the tag once, on the topics comment); no edits outside CONFIG.js topics
  block, wareffort.js (2 sites + 1 var), camp.js (1 site + 1 var).
A9. Day/source stamping rides journal.append defaults (day = game.dayNight.day at
  event time; no day argument passed).
A10. Idempotence across save/load: entries dedupe by id; repeat takes/fills/rests
  must not mint duplicates; restored old saves (journal block without the new
  ids) gain entries only via fresh events.
A11. Build marker: built v8-playable.html must contain 'war-effort-requisition'
  and 'camp-first-rest' (bundled CONFIG). tools/build_v8.py must run clean.
A12. No new CSS, no DOM changes, no THREE/scene changes. Panel polish item of
  QJR-3 is satisfied by prior compliance (cite QJR-2 verdict; no code).

## Acceptance criteria (Testerbot)

V-1 Zero-touch census passes: only CONFIG.js, wareffort.js, camp.js touched;
  net deletions = 0; A8 tag present.
V-2 Topics shape: 3 new topic objects with exact ids/titles/sources/bodies per A1;
  no collision with rescue/complete ids; strings match this spec verbatim (modulo
  JS escaping and the em-dash/hyphen spelling shown).
V-3 Award event: simulated take fires exactly requisition; satchel-full refusal
  fires nothing; second take fires nothing (dedupe + journal idempotence).
V-4 Fill event: simulated exact-quota fill fires firstFill once; over-band fill
  fires firstFill (not a second entry); not-enough-ore refusal fires nothing.
V-5 Camp rest: saveAndHeal (dusk gate passed) fires camp-rest once; daytime
  refused rest fires nothing; plain save() fires nothing; load fires nothing.
V-6 Absent-journal guards: modules still run with WH_JOURNAL deleted from window
  (no throws) in node one-shot smokes.
V-7 Roundtrip: one shot that takes + fills + rests, captures the journal block,
  restores into a fresh game — entries survive exactly once, no phantom dupes;
  warEffort capture/restore and camp profile payloads unchanged (schema intact).
V-8 Day stamps: entries carry the current game day; source strings per A1.
V-9 Build+marker: build_v8.py exit 0; both markers greppable in the built HTML.
V-10 No CSS/DOM/scene changes (A12) and no interact-chain behavior changes.

## Deliverables

- Code in /tmp/wh-worldfeat on feat/world-visuals (children NEVER push — NO-GIT).
- Testerbot valspec: io/specs/qjr-3-content-wiring-valspec.md (written BEFORE build).
- Testerbot verdict: io/reports/2026-11-06-qjr-3-content-wiring-validation.md.
- IO: commit+push, build+flip, verify served bytes, journal, GOALS tick.
