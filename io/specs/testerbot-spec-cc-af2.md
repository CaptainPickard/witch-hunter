# TESTERBOT SPEC — CC-AF2: affinity-reactive Farmer Aldric repeat dialog (written BEFORE Devbot starts)

Author: Testerbot (independent validator-author). Date: 2026-11-07.
Target: /tmp/wh-worldfeat (feat/world-visuals), HEAD at authoring **f1cefd0**
(`git -C /tmp/wh-worldfeat log -1 --format=%h` = f1cefd0; `origin/feat/world-visuals`
currently == HEAD — `git ls-tree origin/feat/world-visuals prototype/js/CONFIG.js prototype/js/npc.js`
gives the v8 baseline blob shas to record). IO spec of record:
io/specs/cc-af2-affinity-dialog-spec.md (read-only; acceptance letters A-I reused below).
Laws: Testerbot validates CODE with static checks + node probes only — NO harness, NO
headless browser, NO server. Children (Devbot, Testerbot) NEVER commit or push (NO-GIT;
IO is the sole committer). I write only this spec file now; all validation runs AFTER
Devbot's build. "v8" below = the origin/feat/world-visuals blob at f1cefd0 (includes
CC-AF1; the AF1 rescue-deed line in npc.js tryRescue :240 is baseline, not AF2 scope).

## LIVE ANCHORS (line-verified by reading at f1cefd0)

- A1 npc.js showLine() :157-167. `var last = ...` :158; the repeat/text assignment
  :159 `dlg.line.textContent = lineIdx < 0 ? D.repeat : D['line' + (lineIdx + 1)];`
  = THE AF2 choice site. Sentinel if-lines :161-163 (`-2 -> D.lineRescued`,
  `-3 -> D.lineComplete`, `-4 -> D.lineRescue`) must stay DIRECT reads (never routed
  through the tier helper). `'active'` assignment :166 unchanged (exactly one site).
- A2 npc.js openDialog() :204-215. :206 `lineIdx = quest === Q.states[0] ? 0 : -1;`
  (= where the repeat/resolved repeat is selected); :208 active+rescued -> -2;
  :211 complete -> -3. Bodies byte-identical to v8 after Devbot (openDialog is NOT
  an AF2 edit site per IO rule 5).
- A3 npc.js questStateDetail() :278-280 `return { state: quest, rescued: rescued };`
  = save schema v1 (H). restoreQuest() :283-291 unchanged. tryRescue() :231-242
  carries the CC-AF1 `if (window.WH_AFF) window.WH_AFF.deed('rescue_findDaughter');`
  :240 — must survive untouched.
- A4 CONFIG.js regionC.npc.dialog block :1287-1301: line1 :1289, line2 :1290,
  line3 :1291, **repeat :1292 `'The barrow door, hunter. Bring her home.'`** (the
  byte-identity anchor), lineRescue :1294, lineRescued :1295, lineComplete :1296,
  cont :1297, close :1298, hint :1299, prompt :1300. quest block :1306-1316
  (id findDaughter; states available/active/complete). The TWO new keys append
  inside `dialog { ... }` (any sibling-safe position; APPEND ONLY per IO rule 3).
- A5 CONFIG.js CONFIG.affinity ladder (CC-AF1 landed): sworn-dark -80, feared -50,
  neutral -49, honored +50, sworn-light +80. npc.js must decide ONLY on tier ID
  strings — grep proves no score read (`score(`, `minScore`, numeric 50/-50 literals)
  in the npc.js diff.

## F-PINS — PRE-DEVBOT "NOT BUILT" CENSUS (record at validation start; each MUST show the not-built pattern; post-build the same greps flip)

| Pin | Check (from worktree root /tmp/wh-worldfeat) | Expected pre-Devbot |
|----|----|----|
| F1 | `grep -cn "lineAffinityGood\|lineAffinityDark" prototype/js/CONFIG.js` | 0 hits |
| F2 | `grep -cn "tier()" prototype/js/npc.js` and `grep -cn "CC-AF2" prototype/js/npc.js` | 0 each |
| F3 | `git diff origin/feat/world-visuals --stat -- prototype/js/CONFIG.js prototype/js/npc.js` | empty (origin==f1c==HEAD, worktree clean of code diffs) |
| F4 | repeat literal anchor `grep -n "The barrow door, hunter. Bring her home." prototype/js/CONFIG.js` | exactly :1292 (v8 bytes) |
| F5 | `grep -cn "lineIdx === -1" prototype/js/npc.js` | 1 (showLine :159 assignment context; openDialog uses the `< 0` compare) |

## V-1 STATIC CENSUS (post-build)

- S-C CONFIG diff law: `git diff origin/feat/world-visuals -- prototype/js/CONFIG.js`
  (or `git diff` vs recorded blob) is +lines ONLY inside regionC.npc.dialog. Exactly
  two added string keys `lineAffinityGood:` / `lineAffinityDark:`; each value is ONE
  line (no newline inside the JS literal) and matches the IO rule 3 copy BYTE-wise:
  good = `Aldric: 'You are welcome at any fire in the camp, hunter. Word of the daughter travels further than you think.`
  (quoted Aldric line), dark = `Aldric: 'The camp watches its fires when you pass, hunter. I have my daughter thanks to you — I will not watch too closely.'`
  Zero `-` lines anywhere in the CONFIG diff minus header lines (verify
  programmatically, PRINT THE COUNT; it must be 0). No sibling key reorder: the
  v8 :1289-1301 rows remain byte-identical in place (F4 anchor repeats).
  Also: CONFIG.affinity / journal.topics / camp block untouched (diff shows nothing there).
- S-D npc.js diff law: bounded to (a) the small helper (IO rule 5 names it e.g.
  `repeatLine()` — RECORD actual name) declared as an IIFE-private function, (b) one
  call inside showLine() reached ONLY for `lineIdx === -1` (the :159 assignment becomes
  a helper read; assert the helper is NOT called for any other lineIdx), (c) a
  `// CC-AF2:` comment line at the choice site. No other hunks: sentinel if-lines
  :161-163 byte-identical, openDialog :204-215 byte-identical, tryRescue :240 intact,
  restoreQuest/questStateDetail untouched. Tier decision = `window.WH_AFF && ...`
  presence + `.tier()` call; selection maps 'honored'/'sworn-light' -> good,
  'feared'/'sworn-dark' -> dark; no score read (S-C/S-D greps above, PRINT counts).
  Copy strings in npc.js: at most the four tier IDs (`'honored'`, `'sworn-light'`,
  `'feared'`, `'sworn-dark'`) or a small CONFIG map (e.g. CONFIG.affinity.dialogMap
  append — either per rule 5; RECORD which landed and validate that choice).
- S-E cross-module PRES: `git diff origin/feat/world-visuals --stat` shows ONLY
  prototype/js/CONFIG.js, prototype/js/npc.js (+ io/specs|reports scratch IO side).
  js/affinity.js, js/camp.js, js/game.js, js/journal.js, index.html = zero diff. No
  new files under prototype/js. NO commits by children (`git log -1` still f1cefd0
  unless IO already landed; any landed commit author = IO identity, NEVER Devbot).
- S-F syntax: `node --check prototype/js/npc.js && node --check prototype/js/CONFIG.js`
  exit 0 x2 (node v22.22.3 is on PATH here; c10 precedent scratch/cc-c10/probe_dialog.js).

## V-2 PROBE RECIPE (behavior; post-build; ONE file scratch/cc-af2/probe_affinity_dialog.js)

Pattern = the proven C10 harness scratch/cc-c10/probe_dialog.js (offline `node`,
no browser): stub `globalThis.window = globalThis`, minimal DOM `document.createElement`
/`getElementById` stub set, require `prototype/vendor/three.classic.js` + `CONFIG.js`
+ `wh-ground.js`, stub `WH_ASSETS`/`WHSkeletonUtils`, require `npc.js`, take
`window.WH_NPC`. Extensions for AF2:
- Load the REAL `prototype/js/affinity.js` (landed CC-AF1) so `window.WH_AFF` is
  genuine; set `window.WH_JOURNAL` = append-collector `{ appends: [], append(id,t,b,s){ this.appends.push(id); } }`.
- State control per case: call `WH_NPC.init(gameStub)` once (gameStub as in c10 with
  regionManager.logic.activeId = C region id), then per case:
  `WH_NPC.restoreQuest({ findDaughter: { state: '<available|active|complete>', rescued: <false|true> } })`
  and `WH_AFF.restore({ score: <n>, crossed: {} })` (capture/restore API replaces
  state exactly). Read the shown text the c10 way: `dlg.children[0].children[1].textContent`
  (inv-panel child 1 = .npc-dialog-line).
- Stub-tier edge cases are made by REPLACING window.WH_AFF per case (save the real
  module ref first, restore after): `{ tier: () => undefined }`, `{}` (no tier),
  `{ tier: () => ({}) }` (object without id) — all must fall back to D.repeat.
- Each case prints exactly one line: `PASS <tag> <letter>:` or `FAIL <tag> <letter>: <got vs want>`.

CASE TABLE (want = the CONFIG-keyed string actually shown; assert also lineIdx side effects where noted):

| Case | Setup before openDialog() | want |
|----|----|----|
| S1 (A) | available; real WH_AFF score 80 (honored) | D.line1 |
| S2 (A) | available; score -80 (sworn-dark) via restore then advance through line3? no — fresh restore available | D.line1 |
| S3 (C) | active(rescued:false); score 50 | D.lineAffinityGood |
| S4 (D) | active; score -50 | D.lineAffinityDark |
| S5 (order-2 map) | active; score 80 -> sworn-light | D.lineAffinityGood |
| S6 (order-2 map) | active; score -80 -> sworn-dark | D.lineAffinityDark |
| S7 (B+byte-identity) | active; score 0 (neutral) | D.repeat, and the shown string is BYTE-IDENTICAL to the v8 repeat literal (probe reads the origin blob? no — assert `line() === D.repeat` AND V-3 byte check below covers the CONFIG side) |
| S8 (F) | active; `delete window.WH_AFF` before openDialog() | D.repeat, NO exception (try/catch must catch nothing) |
| S9 (F) | active; WH_AFF replaced by `{ tier: () => undefined }` / `{}` / `{ tier: () => ({}) }` (3 sub-cases) | D.repeat, no throw |
| S10 (E) | complete(rescued:true); score 80 | D.lineComplete (sentinel -3, NOT good line) |
| S11 (E) | complete; score -80 | D.lineComplete |
| S12 (G) | active+rescued:true openDialog path -> lineIdx -2 | D.lineRescued even with score 50 (tier never swaps sentinels) |
| S13 (G) | rescue seam: set activeId = C.regionD.id, player.pos at the stoneSarcophagus row x/z, restore active; call WH_NPC.tryRescue() with score -50 | returns true; shown line = D.lineRescue (-4), NOT dark line; quest stays 'active' with rescued=true (openDialog next shows -2) |
| S14 (per-open re-decision) | active: open (neutral -> D.repeat), closeDialog(), WH_AFF score 50, openDialog() again | second open shows D.lineAffinityGood (no caching of the choice; helper re-evaluates each open) |
| S15 (H) | restoreQuest({findDaughter:{state:'active',rescued:false}}) from a synthetic OLD v1 save block | no throw; WH_NPC.questState() === 'active'; WH_NPC.questStateDetail() deep-equals `{ state:'active', rescued:false }` — exactly TWO keys, no new fields |

PASS bar: S1-S15 all print PASS; any FAIL line = the letter it belongs to fails.
Probe file committed as working-tree scratch only (NO-GIT); validator re-runs it:
`node scratch/cc-af2/probe_affinity_dialog.js /tmp/wh-worldfeat` exit 0.

## V-3 BYTE-IDENTITY CHECK (neutral repeat vs v8 CONFIG)

1. `git -C /tmp/wh-worldfeat ls-tree origin/feat/world-visuals prototype/js/CONFIG.js`
   -> record the v8 blob sha (pre-build).
2. `git -C /tmp/wh-worldfeat show origin/feat/world-visuals:prototype/js/CONFIG.js | sed -n '1287,1301p' > /tmp/dialog_v8.txt`
3. Extract the current dialog block (same line-scan keyed on the `dialog: {` ... `quest: {`
   markers, NOT fixed numbers, since the two appended keys shift rows) and diff:
   `diff /tmp/dialog_v8.txt <(current dialog block)` -> ONLY `>` addition lines for
   lineAffinityGood/lineAffinityDark (+ any new comment); zero `<` removal lines.
4. Extract both `repeat:` literals (v8 show + current file) with grep, strip
   whitespace, `cmp` the two strings -> byte-identical (`The barrow door, hunter.
   Bring her home.`). PRINT both extracted strings in the report.
5. Same extraction for lineRescue/lineRescued/lineComplete/cont/close/hint/prompt/
   line1-3: byte-identical to v8 (sentinels + UI copy untouched).

## V-4 VERDICT FORMAT (report = io/reports/2026-11-07-cc-af2-affinity-dialog-validation.md)

Header: recorded shas (HEAD, origin blob shas of CONFIG.js + npc.js), then one line
per acceptance letter, PASS/FAIL with its single strongest evidence line (grep count
or probe PASS line or diff count), then:

```
A: PASS|FAIL — <evidence>
B: PASS|FAIL — <evidence incl. byte-identity cmp result>
C: PASS|FAIL — <evidence>
D: PASS|FAIL — <evidence>
E: PASS|FAIL — <evidence>
F: PASS|FAIL — <evidence (absent + 3 falsy sub-cases)>
G: PASS|FAIL — <evidence (-4 tryRescue + -2/-3 open paths)>
H: PASS|FAIL — <evidence (S15 + schema grep: no new questStateDetail fields)>
I: PASS|FAIL — <evidence (CONFIG +2 keys single-line, npc bounded, zero `-` lines in-scope)>
VERDICT: PASS
```
or `VERDICT: FAIL (letters: ...)`. Any scope leak beyond CONFIG.js/npc.js, any
`-` line inside the two files' diffs, any child commit, or any FAIL letter = FAIL.
Static PASS = "ready for Nicko's playtest", never "accepted". Keep the report under
~120 lines. NO messaging Nicko. NO-GIT: this spec write + the report are the only
files I create.

## PRE-DEVBOT NOTE (this spec's state)

Written BEFORE Devbot's CC-AF2 build; F1-F5 were read not-built at f1cefd0 to pin the
baselines. Nothing validated yet; V-1..V-4 execute only after Devbot's diff lands.
