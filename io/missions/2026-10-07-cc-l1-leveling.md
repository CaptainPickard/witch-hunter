# L1 CHANGE ORDER BRIEF - LEVELING: XP, LEVELS, 9 STATS, 3 SKILL BY-USE LINES

Order: Nicko 2026-10-07 (after C4 save profile verdict "everything working
fantastically"). Builder: Claude Code CLI print-mode, model opus,
--allowedTools "Read,Write,Edit,Bash", run from /tmp/wh-worldfeat.

## Goal
The action-bar arc made the witch hunter playable; this arc makes him GROW.
Layer-1 leveling (doc 07 locked): XP earns character levels; each level
grants 5 stat points allocated across the NINE locked stats with live
mechanic wiring. Plus THREE skill lines leveling by use (no tier-up menus,
no techniques this round). Enemy AI combat depth is the NEXT order after
Nicko playtests this - not in scope here.

## Locked rulings (Nicko's exact terms)
- "1, then 2" = Layer-1 (XP -> level -> 5 stat points -> nine-stat
  allocation) AND three skill lines leveling by use. NO tier-up menus yet.
- ALL NINE stats are LIVE this round: Health->hpMax, Stamina->staminaMax,
  Focus->focusMax, Speed->move speed, Precision->crit chance,
  Ward->damage reduction, Wisdom->spell power + focus, Carry Weight->
  inventory stack caps, Luck->drop roll bonus. CONFIG curves, all numbers
  visible in code comments.
- XP sources: kills (per-enemy), gather node pickups, cooking a meal /
  learning a recipe, first-of-kind discovery. No quest XP.
- Skill lines DO NOT tier up this round: ranks accumulate per use with
  per-rank primary-passive effects only (doc 18 curve shape).
- SEQUENTIAL: enemy AI is a separate later order (Nicko plays first).
- LEVEL DOES NOT SCALE POWER (doc 07 lock): the level number is a point
  budget; stats and skills are the power. No enemy scaling by level.

## Canon to read FIRST (audit numbers are the contract)
- docs/planning/07-leveling-progression.md (locked: 9 stats, 5 pts/level,
  Morrowind philosophy, no level power-scaling).
- docs/planning/18-skill-progression-mechanics.md (rank curve shape;
  per-rank primary passives; diminishing past 50; no decay).
- docs/planning/15-skill-lines.md (the 28-line list: pick the canonical
  line ids for the three prototype verbs - longsword attacks, shield
  block, spellcasting school - and use THEIR canonical names).
- All XP costs, stat curve values, and rank rates are PROPOSED CONFIG
  rows (doc 07 line ~103: tuned against play). Mark every table
  "PROPOSED, Nicko tunes" in comments. NEVER invent LOCKED status.

## STATE (verified 2026-10-07 03:30Z)
- feat/world-visuals tip 70a678c (C4 save landed + VERIFIED SERVING;
  Nicko verdict: "everything is working fantastically"). Worktree clean.
- C4 SURFACE (this order EXTENDS it, do not break): window.WH_SAVE
  (prototype/js/save.js), CONFIG.save.lsKey 'wh-save-v1' schema v1,
  camp menu Save/Save-and-Heal/LOAD, boot CONTINUE/NEW GAME, quit
  persist. The builder's dormant rule: a save restores dormant ONLY on
  day 0 + start phase. C4.1 (IO amend): Save-and-Heal checkpoints the
  WAKE state (camp.js after rest()), never pre-rest.
- AB1 surface: player.selectActionSlot (player.js ~792), actionbar
  CONFIG block lsKey 'wh-actionbar-v1', binding picker + icons via
  window.WH_ICONS (js/icons-data.js). Frozen files this order:
  prototype/js/icons/*.png + icons-data.js content.
- Enemy hooks: enemy.js takeDamage -> fsm 'dead' -> corpse/loot flow.
- Gather hooks: js/gather.js node pickup; Cooking hooks: js/cooking.js
  cook completion + recipe.known learn moment (line ~462).
- Save schema: CONFIG.save in CONFIG.js (~718); save.js WH_SAVE module.
- Blast radius (code-review-graph impact, worktree graph, --depth 3,
  files CONFIG/enemy/player/game/cooking/gather/save/style/index):
  ~120 nodes directly changed, 0 impacted within 3 hops, 0 additional
  files. INJECTED PER LAW (dispatch-prompt law: numbers live HERE).

## SCOPE - implementation contract
S1 MODULE js/leveling.js (window.WH_LEVEL):
  - state: xp, level, pendingPts, alloc {health, stamina, focus, carry,
    precision, ward, speed, luck, wisdom}, ranks {longsword, block,
    <canon spell school line from doc 15>}.
  - awardXP(source, amount): source in CONFIG.leveling.xpSources keys
    (kill_bandit, kill_ghoul, gather, cook_meal, recipe_learn,
    discover_*). Level-ups can chain; each grants +5 pendingPts; toast
    "Level N reached - +5 stat points" (CONFIG.text row).
  - xpForNext(level): CONFIG curve (PROPOSED table or formula row).
  - APIs game.js reads: statTotal(key) = base curve + alloc[key]
    (total including points, per CONFIG.leveling.statCurves perPoint
    values); skillRank(line) -> int; skillMult(line, effect) -> the
    per-rank multiplier the mechanics read.
S2 STAT WIRING (all nine, CONFIG.leveling.statCurves perPoint rows):
  - Health: hpMax. Stamina: staminaMax. Focus: focusMax. These join the
    C1 buff math in game.js applyBuffStats (~419): hpMax = CONFIG base +
    buff bonus + stat bonus. Respect buff expiry clamp behavior.
  - Speed: player move multiplier (player.js moveSpeed consumption -
    find walkSpeed/sprint use; do NOT break EPR1 dodge/sprint curves).
  - Precision: melee crit chance (additive %; on crit apply CONFIG
    multiplier to the damage number before enemy.takeDamage).
  - Ward: incoming damage reduction % (cap 60 - CONFIG row) applied in
    player.takeDamage after enemy damage numbers.
  - Wisdom: spell power multiplier (spells.js damage + focus pool
    contributes via focus stat separately).
  - Carry Weight: stackable stackCap multiplier (inventory.js caps at
    pickup/join; CONFIG items defaultStackCap 60).
  - Luck: bonus roll on drops/gather bonus tables (CONFIG.drops bonus
    paths): extra-roll chance = luck * curve. Keep deterministic code
    paths - Math.random use stays explicit and commented.
S3 SKILL LINES BY USE (3 lines, doc 15 canonical ids):
  - longsword: melee hits landed (player.attack chain connect) grant
    rank XP. Per-rank passive: attack stamina cost reduction + damage
    mult curve (doc 18 shape, CONFIG rows).
  - block: successful blocks/parries grant rank XP. Per-rank: block
    stamina drain reduction + parry window tiny extension (cap +
    0.05s max at rank 100 - show curve in CONFIG).
  - spell school (doc 15 canon name for caster spells): successful
    casts grant rank XP. Per-rank: spell damage mult + focus cost
    reduction curve.
  - Rank XP curve CONFIG.leveling.rankCurve; diminishing past 50 per
    doc 18. NO tier menus. CHARACTER tab shows rank + progress bar per
    line (existing inv-spell row pattern).
S4 CHARACTER TAB UI (inventory.js renderCharacter):
  - LEVEL row: level, xp bar to next, pendingPts badge (+ ALLOCATE
    hint when pendingPts > 0).
  - Nine stat rows: name, total, +/- buttons (pendingPts spend/recoup,
    click sound-free DOM), perPoint effect caption from CONFIG.
  - Three skill rows: rank, progress bar, passive caption.
  - Game input suspension: the inventory screen pattern already covers
    it (game.js onOpenChange) - reuse, no new gates.
S5 C4 SAVE EXTENSION (save.js + CONFIG.save):
  - Add optional 'leveling' block: {xp, level, pendingPts, alloc,
    ranks}. Load-safe defaults when absent (older saves keep loading -
    additive, non-breaking). Schema stays v1 with additive fields
    (comment the decision; do NOT bump the version string).
  - On restore: reapplied through applyBuffStats/statTotals (S2 paths),
    never duplicating C4 fields.
S6 HUD IN-GAME: slim XP pip above the HP bar (existing bar DOM
  pattern, style.css) + level-up toast path (game.js toast fn).

## FILES
- NEW: prototype/js/leveling.js + index.html script tag (after
  save.js, BEFORE player.js - boot order matters: leveling must exist
  before player construction reads statTotals; verify the actual
  first-read site and place the tag accordingly).
- EDIT: CONFIG.js (CONFIG.leveling block + xpSources + statCurves +
  rankCurve + text rows), player.js (crit/ward/speed/move hook sites),
  enemy.js (death -> awardXP kill row - emit through a game.js hook,
  NOT a direct WH_LEVEL import inside enemy class), game.js (applyBuff
  extension, hooks, toast), cooking.js (cook+learn XP hooks), gather.js
  (gather XP hook), inventory.js (CHARACTER tab), save.js, style.css,
  index.html. NO OTHER FILES. Frozen: js/icons* (content), js/camp.js,
  js/touch-controls.js, js/spells.js (spell damage read is CONFIG-side).
- BUILD + COMMIT LAW: commit after EACH unit (S1+S2 / S3+S4 / S5 / S6+
  bundle), python3 tools/build_v8.py from repo root per unit with a
  marker grep (grep -c '<MARKER>' prototype/builds/v8-playable.html >
  0), push origin feat/world-visuals after every commit, BEFORE every
  commit: git fetch + confirm origin tip == local tip (ASTRABOT CHILD
  IS LANDING ASSET COMMITS IN PARALLEL - if it moved: git rebase
  origin/feat/world-visuals, re-verify syntax, continue). Commit
  identity CaptainPickard <pickard.nicko@gmail.com>.

## HARD LAWS (verbatim repeats)
- NO automated game runs of any kind - no harness, no headless browser,
  no chromium, no smoke passes. Nicko's playtest is the ONLY acceptance.
- Syntax validation = playwright driver node --check per edited file
  (/usr/local/lib/python3.12/site-packages/playwright/driver/node).
- Never touch /workspace/witch-hunter checkout, dev, main, docs/,
  scratch/, art-direction/, io/missions (except reading), MANIFEST.
- Never read/commit scratch/.mixamo-credentials.txt or
  .mixamo-storage.json.
- Stop-and-report if origin gains commits outside your units on files
  you own.
- One change order scope: NO enemy AI work, NO new enemy families, NO
  skill tier menus, NO prestige/NG+.

## ACCEPTANCE (Nicko's playtest list)
- L1: starting combat feels identical (level 1 baseline = today's
  numbers; no power shift before points are spent).
- L2: kill bandits/ghouls -> XP pip fills -> level up toast -> 5
  pending points visible in CHARACTER tab.
- L3: spend points: Health visibly raises max HP (C1 buff clamp intact),
  Focus raises pool, Speed feels faster, Precision crits visibly (a
  bigger number/flash on crit), Ward reduces a known hit, Wisdom makes
  firebolt hit harder, Carry Weight raises a stack cap, Luck eventually
  bonus-drops (probabilistic - confirm chance rows exist).
- L4: sword fights raise the longsword rank; holding blocks raises
  block rank; casting raises the school rank; ranks affect their
  passives visibly at low ranks.
- L5: save at camp -> reload via CONTINUE -> level/xp/alloc/ranks all
  restored; an OLD pre-L1 save (no leveling block) still loads.
- L6: death -> LOAD returns the saved leveling state (no XP dupes).
- L7: AB1 bar/picker, C4 camp/menu flows, cook icons: zero regression.

## FINAL REPORT (<= 50 lines)
- commits table (sha | unit), marker greps, syntax check list,
  CONFIG rows added (names only), watch items (anything not verified
  at runtime), and the exact stat-curve defaults chosen for Nicko to
  tune in playtest.