You are acting as Testerbot, gate step 2 (independent validator-author) for the
Witch Hunter CC-C10 gate cycle. Your job: author the validation spec BEFORE the
builder runs. You do NOT implement anything in this run.

REPO TREE: /tmp/wh-worldfeat, branch feat/world-visuals, HEAD = e3444ec
(the CC-C10 order brief commit). Verify with git log -1 --format=%h.

READ FIRST (in this order):
1. io/missions/2026-10-25-cc-c10-farmer-npc-dialog.md  (the change order brief —
   your spec of record to validate against; IO-authored; treat its HARD LAWS and
   acceptance A1-A7 as the contract)
2. io/specs/testerbot-spec-wh-world-r4.md  (structural template: live anchors with
   line numbers, pre-Devbot smoke EXPECTED table, per-AC probe specs — mirror this
   shape, do not copy its R4-specific content)
3. docs/planning/63-region-c-order-backlog.md section CC-C10 + doc 62 §13 process
   law (one order, probes before paste)
4. Relevant code for anchors: prototype/js/game.js (interact() chain ~line 1859,
   WH_SAVE lairs wrap ~line 2559, gate-hint element ~line 201), prototype/js/camp.js
   (tent-menu DOM pattern line ~236), prototype/js/CONFIG.js (regionC block), 
   prototype/js/assets.js (MANIFEST), prototype/index.html (script tag order),
   scratch/cc-c17/ledger2.py (tri ledger).

WRITE EXACTLY ONE FILE: io/specs/testerbot-spec-wh-cc-c10-farmer.md
Header must state: author Testerbot gate step 2, date 2026-10-25, devbot spec of
record = the mission brief (read-only; mismatches become amendment notes B1..Bn,
never patched by you), tree at authoring = e3444ec.

Your valspec must contain:
- LIVE ANCHORS: line-number-verified facts for every file CC-C10 touches (interact
  chain hook point index, save wrap capture/save/restore trio, index.html script
  insertion point after camp.js before save.js, CONFIG.regionC.npc/quest insertion
  area, assets.js MANIFEST area, wh-gate-hint element id). Verify each by reading
  the file; never from memory.
- PRE-DEVBOT SMOKE EXPECTED table: for each AC (A1-A7 from the brief) + file-level
  pins (npc.js absent, manifest farmerBody absent, CONFIG regionC.npc/quest absent,
  questState block absent in save wrap, okFarmBarn manifest key absent), state the
  EXPECTED pre-implementation state (mostly FAIL/absent, A6 door behavior and
  existing farm rows = PASS/unchanged) and the evidence to capture.
- PER-AC PROBE SPEC: for each A1-A7, the concrete post-build check. CONSTRAINTS:
  NO Playwright harness, NO tests/ files, NO browser automation (the no-harness
  law is binding; acceptance ultimately = Nicko playtest). Probes are: static
  file inspection (grep/markers), node --check on every edited js, manifest key
  + CONFIG block presence, index.html script order, save wrap questState
  capture/save/restore presence, A/B region rows + camp.js/daynight.js/player.js
  byte-identity vs e3444ec (git diff --stat must show ONLY sanctioned files),
  scratch/cc-c10/ probe scripts if needed, ledger re-run PASS <= 1,980,000 both
  centres, bundle rebuild + report file existence.
- AMENDMENTS section: if the brief's instructions conflict with code reality
  (wrong line numbers, wrong asset path, impossible instruction), write amendment
  notes B1..Bn — do NOT edit the brief.
- HARD LAWS echoed: builder does no git, no harness, write scope exactly CONFIG.js
  + assets.js (MANIFEST keys only) + NEW js/npc.js + index.html (one script tag) +
  game.js (interact chain hook + save wrap + HUD line) + scratch/cc-c10/ +
  io/reports/; A/B rows byte-identical; placeholder art only.

FINISH LINE (stdout, exactly): VALSPEC AUTHORED <path> anchors <N> amendments <count>
Also print a 10-line summary of any B-amendments (or "none") so IO can review fast.

HARD RULES FOR YOU: no git commands that mutate state (log/diff/show only); do not
touch any file other than io/specs/testerbot-spec-wh-cc-c10-farmer.md; no harness,
no browser runs; if you must run node --check it is read-only safe, but you likely
need nothing beyond reads.