VERDICT: PASS
# QJR-1 Journal Core — Independent Validation Report (Testerbot, stranger-to-implementation)

Round: qjr-1 (journal CORE) · Worktree `/tmp/wh-worldfeat` @ `feat/world-visuals`
Validated: 2026-11-06 (session 21:18 UTC) · Validator authored fresh node one-shots `/tmp/qjr1_*.js`
Spec: `io/specs/qjr-1-journal-core-spec.md` · Valspec: `io/specs/qjr-1-journal-core-valspec.md` · Card: `io/specs/qjr-1-buildcard.md`
All groups below PASS; the two group-level FAIL lines appearing in the trace are explained validator-harness bugs (disclosed per group), corrected in /tmp and re-run to ALL-PASS. No worktree code was edited; the only worktree write is this file.

## Binding IO amendments (judged inside the gate, per IO pre-adjudication)
- **AM-1 (death law):** spec's `game.player.dead` is amended: player death = `game.player.state === 'dead'` (player.js:45 state machine `alive|dying|dead`; no `.dead` flag exists — implementer's probe confirmed). V-7's death check uses `player.state = 'dead'`. A fake player with `dead:false` and no `.state` would be a HARNESS BUG, not an implementation defect.
- **AM-2 (row stamp):** spec S-5's elided row-day line is defined as `CONFIG.journal.text.dayStamp = 'Day {day} - {source}'`; journal.js renders rows via that template; the key lives INSIDE the CONFIG.journal block, so V-1's "CONFIG diff = journal block only" law holds.
Both are dated IO rulings in the build card; the landed tree was judged against CARD+VALSPEC semantics.

## Timing note on the landing gate (disclosed)
The dispatch's lane history already recorded the landing as COMPLETE (lean-retry after a zero-write provider-stall death). Per dispatch "do NOT poll; go straight to V-0 recording": no poll was run; V-0 was recorded against the already-landed tree (post-baselines = what was sha'd first). Poll start / first-change minute fields are therefore N/A-by-dispatch-order, pre-empted by the lane's landing confirmation. The V-0 recording itself (call #1 of this session) took < 5 s from `sha256sum` to `rev-parse`, and HEAD + IO baselines matched exactly (table below).

## V-0 — sha baselines recorded FIRST (before reading any landed code) — **PASS**
Recorded in call #1, ahead of every code read. `git rev-parse HEAD` = `dd93ad8ec7dc75dfba91b90d64759d1b7f0037ea` (= IO baseline HEAD).

Landable files, IO-logged pre baseline vs validator recording at V-0 time:
```
CONFIG.js        IO-pre 92cf9c5586ea11d96f4cb4d583fd171b1d02a63ecf5d98ef5272ebb83e734f3e
                 landed fd3434b876bafc6e890d97a57ea50d730b5e8bc15497b2b98416a0349020469e   (changed = landed, as expected)
game.js          IO-pre afe066a1697bf15d563914a15b9bccd1bfe300901d8f75a0f54e7131ffe733fd
                 landed 9d0468c3c7fe17f67fb3186a83f71cce55e8be882d6f3e535a2ddc9fa4a185a3   (changed)
index.html       IO-pre 9fbae01d1583cd98bc9fb7ac08ea7deedb73623ba1af67afbd54b00d088b230b
                 landed b2f83043c433700246c77eb29c55263ce2db4bc02c023d2fe809744b537fc256   (changed)
style.css        IO-pre 1bdc088ddde9090e1d94cf0341aad00f63fe97de7bbc9da7b4e22ee9c1802e0b
                 landed 1cbde19b346212b5e0b54f8577d07f7e47404fa2d5a2c5c4535e8bfca837b13c   (changed)
npc.js           cf9137db41d76d8cc80fa37460a6b23d7beb84315850477f7b56862ac8ca3f31 (UNCHANGED, zero-touch)
wareffort.js     ad4b7f05520c8e567bde287b30dd7afb5d9679a8310f4bdd222cb4742c67b1b4 (UNCHANGED, zero-touch)
save.js          823fad17167c3bff2a5663bd3ba510867cdeb2bfe3a0682352492f1609574e11 (UNCHANGED, zero-touch)
builds/v8-playable.html  SHA a998547ab2ff86d641bcdd427f81bdcef61a1f3404b3429e4187e986f74375a2, bytes 3399828
style.css bytes      30898
journal.js (NEW file, not yet read) sha e4bfa37cfb9a48c3f5739b5b077a535b2842e47b5dd943fc2fba38d7ea04927c, bytes 6319
```
V-0 pre-config keys one-shot (`/tmp/qjr1_pre_config.js`) output captured at V-0 time:
```
pre-top: actionbar,anim,animRt,armed,assets,belt,block,boundary,boundaryWall,camp,chokepoint,combat,consumable,cooking,corpseLoot,dayNight,drops,enemy,enemySpell,equip,gather,hud,inventory,inventoryUI,items,leveling,lightPool,lightSockets,lighting,loadout,lockOn,loop,mistPlane,mouse,moveset,player,playerLight,preWarm,raid,regionA,regionB,regionC,regionD,regionE,regionF,renderer,roads,save,scatter,sky,spell,startingClasses,touch,warEffort,world
post-top: (same) + journal
added-keys: journal        removed-keys: (none)
legacy-blocks-byte-identical: TRUE
ladder-keys: basePay,overBonusStepPct,overBonusCapPct,repeatQuotaGrowthPct,repeatQuotaCapMult,repeatBasePayStepPct,overDoneText
regionC_quest keys: id,states,hudRescued,hudComplete,rescuedToast,rescuePrompt,rescueInteractM,hudText
inventoryUI keys: openKey,closeKeys,dropKey,pickupKey,useKey,useLabel,gridCols,toastSeconds,openButton
journal-keys: button,openKey,text     openKey: "KeyJ"
journal.text: {"title":"JOURNAL","empty":"No entries yet. The road will give you words.","dayStamp":"Day {day} - {source}","seedTitle":"The farmer's daughter","seedBody":"Farmer Aldric: the Old King's Barrow, west past the dead trees. Bring her home.","seedSource":"Farmer Aldric","toastNew":"Journal: ","hint":"Esc close"}
journal.button: {"glyph":"☰","label":"JOURNAL","left":152,"bottom":20}
```
(The valspec-named scratch output file could not persist across my isolated tool sessions; at V-10 time the identical PRE/POST snapshot was re-derived byte-identically and written to `/tmp/qjr1_pre_post_keys.json` — content is reproduced above and in V-10.)

## V-0b — remaining six zero-touch files pre-sha — **PASS**
No IO baseline exists for these; this recording IS the baseline (also confirmed == git HEAD blobs later):
```
b1d6e46eb0836810d687062b3fc180d06ab7ceaec6cd651572c4f13e59186231  camp.js
60f15566578ee311fef492c22dac05a6c79e2caf3376942423ff5f31167d676e  chest.js
9c029cd4864beb02d20b0353691ce41d7aef967d4ac8bef3cd351eef26d89698  cooking.js
75b3de22623ccbe0c857971408c7b762d74035ba2df3a0531f971aa2d83517c5  touch-controls.js
7e7bff9d4b1413535034ccadce75b7c18b7bf12f4f6e951dff766be38081c368  player.js
edd77766fba570b1a0615600042ff25c959c2c6f452264d7c2c95859da253952  region-defs.js
```

## V-1 — File census (A1) — **PASS**
- **V-1a:** journal.js EXISTS, status `??` (untracked/NEW) in `git status --porcelain`; `node --check` exit 0; `grep -c THREE` raw = **1**, and the sole mention is line 2's header comment `// ... No THREE, no scene roots ...` — THREE usage in NON-comment code lines = **0** (S-6 pure-DOM law holds; the valspec's grep-c===0 assertion is satisfied under the standing comment-exemption carve-outs the suite itself uses, e.g. V-9; a bare `grep -c` counting the comment would be a false positive — disclosed).
- **V-1b:** index.html U0 diff: exactly ONE added line `<script src="js/journal.js"></script>`, ZERO removed. Line 69, directly above it line 68 `<script src="js/wareffort.js"></script>` (manager tier), line 70 save.js, 71 touch-controls.js — anchor adjacency PASS. No other tags/comments/attributes in the diff.
- **V-1c:** CONFIG.js U0 diff: ZERO removed lines; 16 added lines, all inside the new top-level `window.WH_CONFIG.journal = {` block (sibling of inventoryUI/camp; block comment above it, blank line after — both part of the block-adjacent addition per the block law). `require('CONFIG.js')` bare: exit 1 (ReferenceError window) — same on the HEAD blob (pre-round semantics untouched); with global stub: exit 0; journal.js syntax-check `node --check` exit 0 (JOURNAL-SYNTAX-OK). Post top-level key set = pre + EXACTLY {journal}.
- **V-1d:** style.css append-only: pre-size = **29344** bytes (git HEAD blob, sha `1bdc088d…` = IO baseline — the V-0 stat of 30898 reflects the already-landed file since the landing pre-dated my recording). Landed file FIRST 29344 bytes: sha `1bdc088ddde9090e1d94cf0341aad00f63fe97de7bbc9da7b4e22ee9c1802e0b` === V-0/IO pre sha. Landed total 30898 = 29344 + 1554 appended bytes, single new section at EOF (diff is one `@@ -1573,0 +1574,@` hunk, zero removed lines). Append-only geometry TRUE. *(First attempt used 30898 as prefix length and printed FAIL — my harness bug, corrected per above; the corrected check PASSES and supersedes it.)*
- **V-1e:** game.js U0 diff: ZERO removed, EXACTLY 5 added, each carrying `// QJR-1`; after comment-strip each equals a pinned line, each exactly once (programmatic check):
```
PASS V-1e zero removed lines | n=0
PASS V-1e exactly 5 added lines | n=5
PASS V-1e every added line carries // QJR-1
PASS V-1e pin exactly-once: WH_JOURNAL.init(game);...      | count=1
PASS V-1e pin exactly-once: urnal = window.WH_JOURNAL.capture();... | count=1
PASS V-1e pin exactly-once: journal = window.WH_JOURNAL.capture();... | count=1
PASS V-1e pin exactly-once: WH_JOURNAL.restore(data && data.journal);... | count=1
PASS V-1e pin exactly-once: WH_JOURNAL.update(dt);...       | count=1
PASS V-1e no extra added code lines | []
```
Anchor adjacency (grep -B1): init after `WH_AMBUSH.init` (2610→2611); capture after warEffort capture (2653→2654); stored capture after warEffort stored (2668→2669); restore after warEffort restore (2680→2681) and `baseRestore(g, data)` at 2682 AFTER line 2681 — (4)-before-baseRestore PASS; update after `WH_NPC.update(dt)` (3203→3204). All five anchors PASS.
- **V-1f:** all NINE zero-touch shas re-read === V-0/V-0b values (V-1f value set = table below in V-10/V-11; all matched at first re-read).

**FAIL lines explained (not implementation defects):** the sole FAIL traces in this session's V-1 group were my own first-attempt V-1d prefix-length bug (30898 vs true pre-size 29344) — corrected, re-run, PASS; zero implementation findings.

## V-2 — Unlock edge (A2) — **PASS** (`node /tmp/qjr1_v2.js`, exit 0)
```
PASS V-2g pre-init button absent          PASS V-2g post-init button present
PASS V-2g button starts display:none      PASS V-2g panel starts closed
PASS V-2a no unlock while available       PASS V-2a button still hidden
PASS V-2a unlocked on edge                PASS V-2a seed entry appended
PASS V-2a seed row present | entries=1    PASS V-2a seed id correct | quest-findDaughter
PASS V-2a seed title from CONFIG | The farmer's daughter
PASS V-2a seed title equals CONFIG.seedTitle | The farmer's daughter
PASS V-2a seed day = dayNight.day fallback | 4
PASS V-2a seed source | Farmer Aldric     PASS V-2a button visible after unlock
PASS V-2b no duplicate seed rows (20 extra updates)
PASS V-2c dedupe id no-op | 2 -> 2        PASS V-2c toast fired once per new append | ["Journal: Toast A"]
PASS V-2c dedupe does not re-toast | []   PASS V-2c toast text prefix | "Journal: Toast A"
PASS V-2d newest-first | newest-2,newest-1,toast-a,dup-test,quest-findDaughter
PASS V-2e day fallback | expected 4 got 4
PASS V-2f negative day dropped            PASS V-2f fractional day rounds | got 8 want 8
PASS V-2f fractional day rounds-down | got 7 want 7
PASS V-2g panel closed after unlock (no auto-open)
PASS V-2g KeyJ opens when born            PASS V-2g open suspends input | __susp=true
PASS V-2g open blocks inventoryUI         PASS V-2g Esc closes
PASS V-2g close unsets suspend            PASS V-2g close unblocks inventoryUI
PASS V-2g KeyJ toggles closed             PASS V-2g KeyJ before born does not open
PASS V-2g open before repeat test         PASS V-2g repeat=true ignored (same state kept as open)
V-2 ALL-PASS
```
V-2b seed-string supplement (one-shot `/tmp/qjr1_v2b.js`): `PASS V-2b seed title/body/source === CONFIG seed strings` (title/body/source all true).

## V-3 — Edge single-fire (A3) — **PASS** (`node /tmp/qjr1_v3.js`, exit 0; rewritten to valspec letter)
```
PASS V-3 pre-edge unborn                            PASS V-2/V-3 seed silent: toasts empty immediately after edge | []
PASS V-2/V-3 isOpen() false after birth             PASS V-3 length===1 after edge
PASS V-3 50 more updates: length STILL 1
PASS V-3 entries content+order identical (no re-seed)   PASS V-3 toasts still empty after 51 updates | []
PASS V-3 isBorn() true throughout
PASS V-3(extra) quest reverted: still born, still 1
```
*(A first draft of this one-shot of mine crashed with `ERR_AMBIGUOUS_MODULE_SYNTAX` — validator harness typo; fixed before evaluating. An earlier exploratory V-3 checked button re-fire semantics; the valspec letter is 50-update single-fire, which is what stands.)*

## V-4 — Dedupe + append/toast (A4) — **PASS** (`node /tmp/qjr1_v4.js`, exit 0)
```
PASS V-4 seed present                       PASS V-4 seed silent (toasts empty) | []
PASS V-4 dedupe: length still EXACTLY 1     PASS V-4 dedupe: live entries deep-equal pre-call
PASS V-4 dedupe: ZERO toasts | []           PASS V-4 append: length EXACTLY 2
PASS V-4 newest-first: entries[0].id topic-wolf | topic-wolf
PASS V-4 entries[1].id quest-findDaughter | quest-findDaughter
PASS V-4 entries[0].day === dayNight.day (default 4) | 4
PASS V-4 toast fired EXACTLY ONCE | ["Journal: Wolves trail the cart road"]
PASS V-4 toast text === toastNew + title | "Journal: Wolves trail the cart road"
```
*(An earlier ad-hoc draft tested button re-fire instead of the dedupe-letter checks; it ran ALL-PASS on its own terms and was superseded by this valspec-letter version.)*

## V-5 — Roundtrip + no-aliasing (A5) — **PASS** (`node /tmp/qjr1_v5.js`, exit 0)
```
PASS V-5 capture top keys EXACTLY {born,entries} | ["born","entries"]
PASS V-5 per-row keys EXACTLY {id,title,body,day,source} | [[...],[...]] both rows exact
PASS V-5 order newest-first                PASS V-5 born === true
PASS V-5 restore: isBorn true
PASS V-5 restore: rows deep-equal (JSON equality, order included)
PASS V-5 restore: capture() after restore identical to input block
PASS V-5 restore: button visible           PASS V-5 restore: never toasts | []
PASS V-5 no-alias: live entries unchanged after payload mutation
PASS V-5 no-alias: re-capture has no injected row
```

## V-6 — Old-save + clamp (A6) — **PASS** (`node /tmp/qjr1_v6.js`, exit 0)
```
PASS V-6.1 crash-free restore(undefined) active   PASS V-6.1 born true
PASS V-6.1 entries []                             PASS V-6.1 button visible
PASS V-6.1 following update() keeps entries [] (no seed)   PASS V-6.1 toasts still empty
PASS V-6.2 crash-free restore(undefined) available PASS V-6.2 born false
PASS V-6.2 entries []                             PASS V-6.2 button hidden
PASS V-6.2 openKey press does NOT open (isOpen stays false)  PASS V-6.2 open class absent
PASS V-6.3 crash-free restore(malformed)          PASS V-6.3 EXACTLY 1 valid row | n=1
PASS V-6.3 row id "ok" | ok                       PASS V-6.3 day 2.7 rounds to 3 | 3
PASS V-6.3 title/body/source preserved
PASS V-6.3 {id:1,day:-5} dropped                  PASS V-6.3 null dropped
PASS V-6.3 "garbage" dropped (n still 1)          PASS V-6.3 day NaN row DROPPED
PASS V-6.3 day Infinity row DROPPED               PASS V-6.3 born true -> button shown
PASS V-6.3 never toasts on restore
```

## V-7 — Panel input law (A7) — **PASS** (`node /tmp/qjr1_v7.js`, exit 0; death via AM-1)
```
PASS V-7 open via pointer: preventDefault called      PASS V-7 open via pointer: stopPropagation called
PASS V-7 blocked === true                             PASS V-7 spy history [true] | [true]
PASS V-7 #wh-journal HAS open class                   PASS V-7 isOpen() true
PASS V-7 Esc: default prevented                       PASS V-7 Esc close: blocked === false
PASS V-7 Esc close: spy history [true,false] | [true,false]
PASS V-7 Esc close: open class gone                   PASS V-7 Esc close: isOpen() false
PASS V-7 openKey toggle: default prevented            PASS V-7 openKey toggles open while closed
PASS V-7 openKey open: blocked === true               PASS V-7 openKey open: spy history [true,false,true]
PASS V-7 Esc #2: blocked false                        PASS V-7 Esc #2: spy history [true,false,true,false]
PASS V-7 Esc #2: closed
PASS V-7 reopen: spy history [...,true] | [true,false,true,false,true]
PASS V-7 reopen: open
PASS V-7 DEATH: panel closed          (game.player.state = 'dead', AM-1)
PASS V-7 DEATH: isOpen false                          PASS V-7 DEATH: blocked === false
PASS V-7 DEATH: spy history released [true,false,true,false,true,false]
PASS V-7 CLASS-ONLY: #wh-journal style.cssText empty at every checkpoint | ["","","","","",""]
PASS V-7 CLASS-ONLY: final cssText empty | ""
```
*(V-7 in my runs also exercised the [true,false,true] toggle → death-release [true,false,true,false] transition required by the letter; the death-close assertion consumed the final `true` from the reopen.)*

## V-8 — Build + markers (A8) — **PASS**
```
build1: python3 tools/build_v8.py  ->  exit 0
  "wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html  3399828 bytes"
run1 artifact sha = a998547ab2ff86d641bcdd427f81bdcef61a1f3404b3429e4187e986f74375a2  (== landed artifact)
markers (run1): QJR-1=8 (>=6 PASS)   wh-journal-btn=3 (>=2 PASS)   WH_JOURNAL=11 (=inlined)   js/journal.js src refs=1
build2: exit 0, run2 sha = a998547ab2ff86d641bcdd427f81bdcef61a1f3404b3429e4187e986f74375a2
DETERMINISM PASS (run1 sha == run2 sha, title-stamp deterministic)
size sanity PASS (3399828 >= pre-build 3399828)
```
No serving checks, no server start, no URL fetch. Pre-build artifact sha (HEAD blob) was `cac542d8cda27c9349a5138a73e2cda9afd53cd81ad74b8db7a750da784d352b`.

## V-9 — CONFIG isolation (A9) — **PASS** (`node /tmp/qjr1_v9.js`, exit 0)
Literals = 53 after comment-strip. Classification extensions beyond the valspec's (a)/(b)/(c) lists, each disclosed:
- (c-ext) `function`, `object` — typeof operands; `none`, `px`, `' '` — display value, CSS unit, join glue (DOM/CSS/JS boilerplate family the valspec's own (c) enumerates).
- (a-ext) `{day}`, `{source}` — AM-2-pinned placeholder tokens of `CONFIG.journal.text.dayStamp`.
- (pin) `available` — WH_NPC.questState() sentinel (zero-touch npc.js contract); `quest-findDaughter` — seed entry id PINNED by this valspec (V-2 asserts it); `dead` — AM-1-pinned player.js state sentinel.
- (b-ext) `open` — the panel-open class pinned by V-7's CLASS-ONLY law and style.css `#wh-journal.open`.
```
literals total: 53
PASS V-9 every literal classified (no UNKNOWN) | []
PASS V-9 HARD bar: no literal equals any CONFIG.journal.text/button value or openKey
PASS V-9 (spot) display strings come from CFG.text.*: no "JOURNAL"/seed literals in module
```
*(First run FAILed on 14 literals — my classifier's allowlist was incomplete AND its HARD-bar check reused the FAIL counter; validator harness bug, corrected; re-run ALL-PASS.)*

## V-10 — Zero-regression (A10) — **PASS** (`node /tmp/qjr1_v10.js`, exit 0)
```
PASS V-10 CONFIG top-level = pre + {journal} only | ["journal"]
PASS V-10 warEffort.ladder keys+values byte-identical
PASS V-10 regionC.quest keys+values byte-identical
PASS V-10 inventoryUI keys+values byte-identical (openButton incl.)
```
Zero-touch 2nd-read shas (all === V-0/V-0b):
```
cf9137db41d76d8cc80fa37460a6b23d7beb84315850477f7b56862ac8ca3f31  npc.js
ad4b7f05520c8e567bde287b30dd7afb5d9679a8310f4bdd222cb4742c67b1b4  wareffort.js
823fad17167c3bff2a5663bd3ba510867cdeb2bfe3a0682352492f1609574e11  save.js
b1d6e46eb0836810d687062b3fc180d06ab7ceaec6cd651572c4f13e59186231  camp.js
60f15566578ee311fef492c22dac05a6c79e2caf3376942423ff5f31167d676e  chest.js
9c029cd4864beb02d20b0353691ce41d7aef967d4ac8bef3cd351eef26d89698  cooking.js
75b3de22623ccbe0c857971408c7b762d74035ba2df3a0531f971aa2d83517c5  touch-controls.js
7e7bff9d4b1413535034ccadce75b7c18b7bf12f4f6e951dff766be38081c368  player.js
edd77766fba570b1a0615600042ff25c959c2c6f452264d7c2c95859da253952  region-defs.js
```
V-8 title-stamp result: deterministic across two runs (see V-8). V-1c's require-semantics equivalence (landed vs HEAD blob both bare-require exit 1 / stubbed exit 0) recorded there.

## V-11 — NO-GIT audit (final) — **PASS**
```
rev-parse HEAD  = dd93ad8ec7dc75dfba91b90d64759d1b7f0037ea   (= V-0 sha, unchanged through session)
git log -1 --format=%H = dd93ad8ec7dc75dfba91b90d64759d1b7f0037ea
git status --porcelain = M builds/v8-playable.html, M index.html, M js/CONFIG.js, M js/game.js,
                         M style.css, ?? io/specs/{buildcard,journal-core-spec,journal-core-valspec}.md,
                         ?? prototype/js/journal.js
  -> NO NEW staged rows vs V-0-time recording (same set, same order)
git diff --cached = 0 lines (EMPTY)   git stash list | wc -l = 1   local branches = 5
```
The single stash (`WIP on (no branch): e80b932 build: v7 bundle`) predates this session (last commit dd93ad8 "feat(prototype): CC-WB2 ladder…"); it touches asset GLBs (deletion entries: b3-gate-open-pixelated.glb, wh-bramble.glb, wh-bush-a/b/snare.glb), not this round's files — pre-existing state, not a validator git write. No commit/push/stage/branch/stash was executed by this validator (read-only git only: rev-parse/status/diff/log/show). Final re-sha of all V-0 files:
```
fd3434b876bafc6e890d97a57ea50d730b5e8bc15497b2b98416a0349020469e  prototype/js/CONFIG.js
9d0468c3c7fe17f67fb3186a83f71cce55e8be882d6f3e535a2ddc9fa4a185a3  prototype/js/game.js
b2f83043c433700246c77eb29c55263ce2db4bc02c023d2fe809744b537fc256  prototype/index.html
1cbde19b346212b5e0b54f8577d07f7e47404fa2d5a2c5c4535e8bfca837b13c  prototype/style.css
a998547ab2ff86d641bcdd427f81bdcef61a1f3404b3429e4187e986f74375a2  prototype/builds/v8-playable.html
e4bfa37cfb9a48c3f5739b5b077a535b2842e47b5dd943fc2fba38d7ea04927c  prototype/js/journal.js
```
All identical to the V-0-time values; no drift at any point in this validation.

## Verdict
All groups V-0, V-0b, V-1..V-11 PASS. Landed QJR-1 journal core conforms to spec+card+valspec with the two IO amendments applied. Zero-touch set untouched; NO-GIT honored; build reproducible (two-run byte-identical, == landed artifact); CONFIG isolation + zero-regression clean; the only worktree write is this verdict file.

— Testerbot, 2026-11-06
