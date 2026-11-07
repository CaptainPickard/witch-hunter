# CC-AF2 Affinity Dialog — Independent Testerbot Validation Report

- Round: CC-AF2 (affinity-reactive camp-NPC dialogue)
- Date: 2026-11-07
- Validator: Testerbot (independent; build claims NOT trusted)
- Worktree: /tmp/wh-worldfeat (branch feat/world-visuals)
- Baseline: HEAD f1cefd0 ("build: v8 bundle from CC-AF1 source (stamp 322ac1c)") — identical to origin/feat/world-visuals for both audited files
- Diff audited: uncommitted worktree changes vs HEAD, files prototype/js/CONFIG.js + prototype/js/npc.js
- Probe: /tmp/cc-af2-val/af2_probe.js (offline node; DOM + THREE + WH_CONFIG/WH_ASSETS/WH_GROUND/WH_JOURNAL stubs; real affinity.js for WH_AFF; drive of the full WH_NPC API)
- Byte checks: /tmp/cc-af2-val/bytecheck.js (quote-exact string-literal comparison v8 blob vs worktree)
- Constraint compliance: NO-GIT (nothing committed/pushed), no harness runs, no browser smoke; probe files live ONLY in /tmp/cc-af2-val (worktree clean of probes)

## V-1 static diff audit — PASS

- git diff --stat vs HEAD: exactly prototype/js/CONFIG.js (+3 −0) and prototype/js/npc.js (+11 −0); no other file modified anywhere in the tree (git status --porcelain: only these two `M `; zero deletions in either diff; pure-additive confirmed both by signed-line count and by hunk-map line surgery: deleting the added lines from the worktree files reproduces the v8 blobs byte-exactly (`CONFIG stripped === v8: true`, `npc stripped === v8: true`).
- Bounded: CONFIG.js is a single hunk (@@ after `repeat:` line), 3 added lines; npc.js two hunks (@@ −156,0 +157,10 and @@ −163,0 +174,2), 11 added lines.
- IO copy verified: the two appended CONFIG keys decode EXACTLY to spec rule-3 strings — lineAffinityGood DECODED-EXACT: true (111 chars), lineAffinityDark DECODED-EXACT: true (124 chars, em-dash preserved, M-bM-^@M-^T UTF-8 in raw diff).
- No sibling edits: whole CONFIG diff = 1 hunk = 3 added lines (comment + 2 keys); diff hunk-map strip === v8 proves nothing else moved; all v8 sibling dialog keys byte-identical (see V-4).
- No tier-literal leakage beyond allowed ids: npc.js added lines contain only 'honored' / 'sworn-light' / 'feared' / 'sworn-dark'; no dialogMap added to CONFIG (option chosen: literals in npc.js, permitted by spec rule 5 "either is acceptable").
- NPC score reads: ZERO — grep of all 11 added npc.js lines for score|minScore|ladder|crossed: no matches (exit=1 = clean). Decision is on `t.id` only.
- No WH_AFF.score() / affinity-internal reads in npc.js anywhere: `grep WH_AFF` in worktree npc.js returns only the pre-existing tryRescue deed line (v8, byte-unchanged, line 242) plus the new repeatLine guard.
- Sentinels untouched: negative lineIdx handlers (-2 lineRescued / -3 lineComplete / -4 lineRescue) are byte-identical to v8 (worktree lines 171–173 = v8 lines 161–163 modulo shift); no new negative sentinel branches; the v8 fallback `lineIdx < 0 ? D.repeat : ...` remains.
- Header comments present: `CC-AF2:` at the CONFIG copy block (1) and at both npc.js choice sites (2).
- Syntax: `node --check` npc.js + CONFIG.js → SYNTAX_OK.

## V-2 behavioral probe — PASS (18/18)

Probe output (actual run, node /tmp/cc-af2-val/af2_probe.js, exit 0):

```
PASS S1 available@sworn-light -> line1 {"tier":"sworn-light"}
PASS S2 available@honored -> line1 {"tier":"honored"}
PASS S3 available@feared -> line1 {"tier":"feared","score":-50}
PASS S4 available@sworn-dark -> line1 {"tier":"sworn-dark","score":-100}
PASS S5 active+neutral -> repeat byte-identical v8 {"got":"The barrow door, hunter. Bring her home."}
PASS S6 active honored -> lineAffinityGood {"tier":"honored"}
PASS S7 active feared -> lineAffinityDark {"tier":"feared"}
PASS S8 active sworn-light -> lineAffinityGood {"tier":"sworn-light"}
PASS S9 active sworn-dark -> lineAffinityDark {"tier":"sworn-dark"}
PASS S10 WH_AFF deleted -> repeat no throw {"threw":false,"got":"The barrow door, hunter. Bring her home."}
PASS S11 tier() falsy & tierless -> repeat no throw {"falsy":["null=repeat","undefined=repeat","0=repeat","=repeat","false=repeat"],"tierless":"The barrow door, hunter. Bring her home."}
PASS S12 complete@sworn-light -> lineComplete {"tier":"sworn-light"}
PASS S13 complete@sworn-dark -> lineComplete {"tier":"sworn-dark"}
PASS S14 rescue@sworn-dark -> -4 lineRescue untouched {"rp":true,"tr":true,"got":"You are safe now. Go to your father; I will follow."}
PASS S14b rescue->open: -2 lineRescued + quest complete {"got":"She is home, hunter. You have given me back my world.","state":"complete"}
PASS S15 reopen re-decides on tier change {"honored":true,"feared":true,"neutral":true}
PASS S15b v1 restores available/active/complete/bogus->available {"v1available":"available","v1active":"active","v1complete":"complete","bogusTo":"available"}
PASS H questStateDetail keys = state,rescued only {"state":"available","rescued":false}
=== TOTAL: 18/18 cases passed ===
```

Probe-engineering notes (honest record):
- Feared requires EXACT score −50 (tier() = greatest minScore ≤ score over rows sworn-dark@−80, feared@−50, neutral@−49, honored@50, sworn-light@80; at −52 the ladder correctly reports sworn-dark because −80 ≤ −52 while −50 > −52 holds only for sworn-dark's window). Probe tuned to exact −50 via warEffortFill +3×10 / kill_bandit −20×4.
- The rescued return-talk completes the quest only ONCE (−4 → −2 on the open after rescue, then −2 → −1 on later opens); probe's S14b asserts exactly two opens.
- WH_AFF restore semantics honored in the probe: restore(undefined) resets to score 0, crossed {}.

## V-3 neutral repeat byte-identity vs v8 blob — PASS

- v8 repeat line extracted from `git show f1cefd0:prototype/js/CONFIG.js` = worktree line (REPEAT_CMP_IDENTICAL, byte compare via cmp): `repeat: 'The barrow door, hunter. Bring her home.',`
- The only other `repeat:` in the file (a texture field, `repeat: 12`) is also byte-identical, so no wrong anchor was compared.
- Runtime: S5 probe case shows the neutral dialog text is byte-equal both to D.repeat in CONFIG and to the v8 string hardcoded from the blob.

## V-4 sibling key identity vs v8 blob — PASS

bytecheck.js result (quote-exact single-line string-literal comparison, escape-aware, against `git show f1cefd0:prototype/js/CONFIG.js`):

```
BYTE-IDENT repeat (len 40)
BYTE-IDENT lineRescue (len 51)
BYTE-IDENT lineRescued (len 53)
BYTE-IDENT lineComplete (len 60)
BYTE-IDENT cont (len 8)
BYTE-IDENT close (len 5)
BYTE-IDENT hint (len 32)
BYTE-IDENT prompt (len 20)
BYTE-IDENT line1 (len 81)
BYTE-IDENT line2 (len 81)
BYTE-IDENT line3 (len 65)
NEW-ONLY   lineAffinityGood inV8=false inCur=yes
NEW-ONLY   lineAffinityDark inV8=false inCur=yes
RESULT: V-4-IDENTITY-PASS
```
Note: len 81 for line2 in this pass vs the 18-char report line in the probe (probe line2 len 18 = truncated); the authoritative length is 81 here (bytecheck compares full literals, no truncation).

Sibling CONFIG structure untouched: dialog block sibling lines (lineRescue line and below) identical; the CONFIG hunk-map strip test already proved whole-file equality with v8 after removing exactly the 3 added lines.

## Acceptance letters

- A: PASS — S1..S4: quest 'available' → line1 at sworn-light / honored / feared / sworn-dark; tier-agnostic (probe cases S1–S4).
- B: PASS — S5: active + neutral (score 0) repeat line byte-identical to CONFIG.regionC.npc.dialog.repeat AND to the v8 blob string.
- C: PASS — S6/S8: honored (+50) → lineAffinityGood (also sworn-light S8 mapping good-side).
- D: PASS — S7/S9: feared (−50) → lineAffinityDark (also sworn-dark S9 mapping dark-side).
- E: PASS — S12/S13: quest 'complete' → lineComplete at +100 (sworn-light) and −100 (sworn-dark), tier-agnostic.
- F: PASS — S10/S11: WH_AFF deleted and tier() falsy variants (null/undefined/0/''/false) plus tierless {} → D.repeat, zero throws.
- G: PASS — S14: rescue (−4) lineRescue; S14b: rescue→open → −2 lineRescued + quest 'complete'; −2/−3/−4 never tier-swapped even while tier is sworn-dark (sworn-dark rescue case S14 + S14b evidence).
- H: PASS — questStateDetail keys exactly {state, rescued} (no new fields); S15b: restore of v1-style flat blocks (string findDaughter keys) works: available/active/complete, bogus→available; save schema untouched (CONFIG diff contains no save-schema keys).
- I: PASS — CONFIG diff = exactly 2 appended dialog keys (single-line, append-only, comment allowed; sibling keys byte-identical, hunk-strip === v8); npc.js diff bounded to repeatLine helper + lineIdx===−1 call + header comments (11 added lines, 2 hunks, minus-lines=0).

## VERDICT: PASS
