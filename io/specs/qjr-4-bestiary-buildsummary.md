# QJR-4 BESTIARY JOURNAL — DEVBOT BUILD SUMMARY

Branch: feat/world-visuals (HEAD 46b3c20 + e1d66d6), worktree /tmp/wh-worldfeat
Built to io/specs/qjr-4-bestiary-spec.md + io/specs/qjr-4-bestiary-valspec.md.
Status: CODE LANDED + BUILD GREEN. Not playtested (no harness, per order).

## Files changed
| file | delta | notes |
|---|---|---|
| prototype/js/bestiary.js | NEW ~290 lines | window.WH_BESTIARY: init/capture/restore/update + appendKill/appendSight/killsOf/sightOf/isBorn/isOpen/setOpen/closeForTest + renderPage (journal mounts it). Zero literals (A9); zero per-frame scanning (update = 2 open-panel DOM checks, spec 2.5). |
| prototype/js/journal.js | +131 / −2 | tab row buildTabs (pointerdown TC-FIX1 pattern), renderCurrentPage dispatcher, openPanel/closePanel tab-state law, birth-edge re-render in update(), search feeds both pages. rebuildRows renamed body = buildJournalRows (net −2 lines are the two renamed call/title lines; every line count identical otherwise). |
| prototype/js/enemy.js | +6 / −0 | 3 guarded one-line hand-offs (appendSight x2 after setFsm('aggro')/'chase' at 517/520; appendKill after onKilled in takeDamage hp<=0 branch) + 2-line comment above `Enemy.onKilled = null;` (now line 1750). No other edits (verified: delta 6 insertions, 0 deletions). |
| prototype/js/game.js | +9 / −0 | 5 guarded sites (init at 2646; capture 2692; stored.bestiary 2712; restore 2730; update 3272) all tagged // QJR-4. Keys `bestiary` wired exactly mirroring the journal pattern in all three save sites. |
| prototype/js/CONFIG.js | +54 / −0 | Single pure EOF insertion (difflib-verified: 1 opcode, 0 OLD lines touched): window.WH_CONFIG.journal.bestiary — 10 entries (title/sigil/accent/page), text block with tab labels, toasts, footer/locked/nomatch/hint strings. journal block byte-identical (prefix check + difflib). |
| prototype/index.html | +2 / −0 | `<script src="js/bestiary.js"></script>` + 1 comment line, AFTER js/journal.js. |
| prototype/style.css | +50 / −0 | EOF append only. .wh-journal-tabs / .wh-journal-tab(.active) reusing inv-tab grammar; .bestiary-* rows; .codex-accent-amber/.codex-accent-crimson/.codex-accent-bone/.codex-accent-ash. 18 hex references, ALL pre-existing tokens (programmatic diff vs HEAD: 0 violations; no gradient/glow code lines). |
| prototype/builds/v8-playable.html | rebuilt | build artifact. |
| io/reports/qjr4_devbot_probe.py, qjr4_a9_probe.py, qjr4_config_verify.py | NEW | build-time verification scripts (IO may keep or discard). |

## Gates
- node --check: bestiary.js / journal.js / enemy.js / game.js / CONFIG.js — all exit 0.
- python3 tools/build_v8.py — exit 0 (3,561,672 bytes).
- grep -c WH_BESTIARY prototype/builds/v8-playable.html → **20** (>= 20 gate PASS).
- sha256(v8-playable.html after final build): 3fd0c5c3c583e89884f9f261735bcc9752ef74c8b48a43b2c7c5a3b8858b2279

## Self-probe (stubbed VM, io/reports/qjr4_devbot_probe.py — 19/19 PASS)
Kill unlock (unknown type silent, +1 tally, first-kill toast, then every 5th), sight-per-type collapse, capture/restore roundtrip incl. garbage-row drop, restore keeps codex born via witnessed rows, all ten entries present, closeForTest tab state reset. A9 audited comment-stripped: bestiary.js holds only DOM/placeholder/format strings; every player-facing string lives in CONFIG.journal.bestiary.

## Design decisions (disclosed)
1. **setOpen in the API** — added beyond the spec's 7 because closePanel (spec 2.7) needs it to unarmed the open-tab state; journal.js pick()/closePanel() sync it. Pure addition, no spec surface harmed.
2. **closeForTest = closePanel** — it owns the tab-state law, which a separate close would have to duplicate.
3. **renderPage on WH_BESTIARY** — render lives in the codex module (owns locked-row/footer grammar); journal.js only hands over its page mount + shared query (spec 2.4/2.7).
4. **bestiary hint line suppressed** (`.bestiary-hint{display:none}`) — spec 2.10 names no hint text for the codex; the journal "Esc close" hint remains the single visible one.
5. **Kill toast cadence**: kill #1 of a type always uses the first-kill shape (killToastTitleUnseen) whether the type was previously witnessed or unlocked by that kill; kills 6/11/... use killEveryLabel (x{n}); unknown types fully silent (valspec 18/19; spec 2.9).
6. **Double-boot guard** in bestiary.js (early return if window.WH_BESTIARY exists) — load-order safety, also documents the module singleton.

## Ledger-law note
10 page strings drafted in witnessed-fact voice; no creditor identity, no signatory name, no pact/tithe terms (tithes appear only as seen carts/receipts/counting; Veil only as the mist walked into). Titles match the spec's 10 verbatim.

## Not done / for IO+Testerbot
- NO git add/commit/push (per order — IO commits).
- No harness runs / headless smoke (per order). Playability unverified; Testerbot drives V-1…V-16.
- Probe scripts under io/reports/ are build-time artifacts, not game code.
