# C1 CHANGE ORDER - COOKING AT THE DARKWOOD BONFIRE (stage 3, cooking arc)

Builder: Claude Code print-mode, model opus, allowedTools Read/Write/Edit/Bash.
Dispatch wording: include the no-harness law verbatim ("no headless browser
runs of any kind - no game-loop harness, no chromium smoke pass; syntax checks
only").

## GOAL
Cooking ships playable end to end at ONE station: the bandit campfire in Region
B (darkwood_edge, prop banditCampfire at x:2.5, z:-52). First-try Trio = Grave
Soup. Success teaches the recipe (one-click re-cook), grants the campsite-kit
moment (inert HUD button stub; deploy is C3), and bakes the first food buffs.

## LAWS (all standing, none waivable)
- NO automated runs of the game: no harness, no headless browser, no chromium
  smoke. Syntax checks only (playwright driver node --check per edited file).
- ONE change order: C1 scope only. No day/night cycle, no campsite deploy, no
  chest/bench work, no save system (C2-C4 own those).
- OTHER SESSION ACTIVE IN THIS REPO: work ONLY in the /tmp/wh-worldfeat
  worktree on feat/world-visuals. NEVER touch /workspace/witch-hunter (dev
  checkout), the dev or main branches, 8793 container state, or any branch
  except feat/world-visuals. BEFORE starting: reconcile with remote
  (fetch https://github.com/CaptainPickard/witch-hunter.git feat/world-visuals
  and compare tip). If the tip moved with changes in prototype/ or tools/,
  STOP and report to IO. Commit in small units and push immediately after
  each (git push origin feat/world-visuals; HTTPS creds in credential store).
- Commit identity: CaptainPickard <pickard.nicko@gmail.com>.
- Never read/commit scratch/.mixamo-credentials.txt or .mixamo-storage.json.
- Player copy: never the word "free".
- CONFIG-first: every tunable number lives in CONFIG with a comment.

## CAMP GROWTH LAW (design canon, Nicko 10-05 - binds C3 and every camp order after)
The campsite system is MODULAR and GROWS. From C1 onward, camp-facing code is
written as data-driven modules (per-module {id, prop asset, interact hook,
CONFIG row}), never hard-wired into camp logic. Roadmap already decided:
- C3 deploys the starter kit: campfire + bedroll + tent (3 modules).
- Quest-gated additions follow: STORAGE CHEST and CRAFT BENCH modules (gated
  by quests; bench = doc 05 station tier 1 Field Kit).
- Over time the camp scales LARGER in footprint and content: more tents,
  more modules, eventually NPC-inhabited - the full WARP CAMP (docs 09/11/50:
  tiers, cook's tent kitchen, retinue, decoration prestige).
Implementation consequence for C1: name the systems for reuse (CONFIG.cooking,
a camp-module-friendly interact registry) and do NOT special-case the bandit
fire in a way C3 must unwind.

## EXPLORATION-REWARD LAW (design canon, Nicko 10-05)
The game rewards exploration with capability, never handouts. Region B has NO
mushroom nodes BY DESIGN: players who explore Region A to its fullest earn the
wildMushrooms that make Grave Soup possible. NEVER "fix" missing ingredients
by adding nodes to a region whose identity is scarcity. Future mechanics keep
this shape: capability is earned through the world, not the menu.

## CEMETERY ECOLOGY (design canon, Nicko 10-05)
Wild mushrooms and grave moss grow ONLY around burial grounds: cemeteries,
graveyards, church ruins. C1 makes the world tell that truth. Region A has a
cemetery yard (gravestones/stone crosses ~ x -15..20, z 10..25) but its 4
mushroomCluster nodes sit far from it (x 38..68 east field + one at x -60 west)
- RELOCATE those 4 to FOREST GROUND AROUND the cemetery: woodland spots near
the gravestone ring, outside the fence lines, never inside the open yard
interior (the gen_gather_nodes in_graveyard rule: yard = open combat ground).
Honor the gather clearances (props 3-4m, enemy spawns 5m, player spawn 6m,
nodes 6-9m apart, dirt path +2.5m). Region B graveMoss nodes already hug its
church/graveyard props: leave them. The hint "Mushrooms favor the dead..."
stays cryptic by intent - an allusion, not a map pin.

## STATE (verified 2026-10-05, feat tip after mouse-bind Order A landed)
- feat/world-visuals worktree /tmp/wh-worldfeat clean at 21cebb2 (mouse-bind
  Order A landed: build v8). Build tool is now tools/build_v8.py ->
  prototype/builds/v8-playable.html. Do NOT touch the mouse/pointer-lock keys.
- Serving: 8793 host container + WebUI /playtest-feat/ both serve the worktree
  live (no-store). No deploy step for game files; do a build commit (below).
- Existing hooks C1 builds on:
  - Interact: game.js interact() = box pickup > corpse > gather, E key +
    touch USE. Cooking is a new branch on this chain (nearest lit cooking
    fire within radius).
  - Items: CONFIG.js items registry (bandage pattern for a usable item);
    ingredients forestHerb/deadwood/wildMushroom/graveMoss/boneShard exist
    (category 'ingredient'); cooking ingredients never drop from enemies.
  - Gather: js/gather.js WH_GATHER. Region A nodes: herbBundle x6,
    deadwoodPile x4, mushroomCluster x4 (yield wildMushroom x2 each).
    Region B nodes: graveMoss x5, bonePile x4 ONLY - and that sparity is
    CANON (see EXPLORATION-REWARD LAW). Do not add Region B nodes.
  - Vitals: CONFIG.player hpMax 100, hpRegenPerSec 0.0 (no passive regen).
    HUD hp bar computes from p.hp/p.hpMax (auto-adapts to bigger hpMax).
  - No buff system exists anywhere - C1 introduces it.
  - No day/night cycle: buffs use real-seconds duration for now (fallback
    constant becomes 1 in-game day when C2 lands).

## SCOPE - C1 ONLY
1. FIRE FUEL (Region B banditCampfire only; Region A dressing fire untouched
   and INERT as today).
   - CONFIG.cooking.fire: startFuelSec (bandit fire starts lit, generous for
     the playtest: default 240), burnPerCookSec (fuel consumed per cook =
     channel + margin, default 10), burnTick (1s decay loop in game update).
   - Lit fire = existing flicker light + flame visuals as today. Fuel hits 0:
     light intensity to 0 (CONFIG knob), interact prompt becomes
     "Fire burnt out - E to add Deadwood (fuel)".
   - E on a burnt fire with deadwood in inventory: consume 1 deadwood, refuel
     to burnPerCookSec x CONFIG.refuelCooks (default 4), relight, toast
     "The fire takes."
2. COOKING STATION + UI (js/cooking.js new file; hooks in game.js).
   - E near lit banditCampfire (radius CONFIG, 2.5m): opens COOK panel
     (full-modal, same patterns as the character screen).
   - Panel: 3 ingredient slots. Click an inventory ingredient to fill the
     next open slot (deadwood is FUEL, not a cook slot); click a slot to
     clear. NO dish preview (gamble). Buttons: Cook, Cancel.
   - Learned-recipe list section: once a recipe is known, click it to
     auto-fill its slots from inventory and start the channel.
   - If the player has NO wildMushroom in inventory, the panel shows the
     one-time-per-session hint line: "Mushrooms favor the dead..."
     (cryptic per Nicko; the truth it alludes to is the CEMETERY ECOLOGY law).
3. RECIPES + DISCOVERY (CONFIG.cooking.recipes).
   - Grave Soup: graveMoss + wildMushroom + boneShard. Result item graveSoup
     ('food', glyph 'GS', weight 20). Effect: +20 max HP for 1 in-game day
     (pre-C2: CONFIG.cooking.buffDurationFallbackSec = 480 real seconds,
     comment notes it converts to day-length in C2). Stacks nothing: one
     instance max (re-eat refreshes duration). Needs 1 of each ingredient.
   - Bland Mush: any other trio at a campfire. Result item blandMush ('food',
     glyph 'BM', weight 15). Edible, grants NO buff, flavor copy
     "A sad grey mush". The gamble's waste.
   - Discovery: first successful Grave Soup cook sets recipes.graveSoup.known
     = true + toast "Recipe learned: Grave Soup". Recipe knowledge persists
     for the session; C4 save will write it.
   - Extensible: recipes[] rows carry {id, name, ingredients[3], result,
     effect}; known flag; unknown trio = Bland Mush path. No preview ever.
4. CHANNELLED COOK.
   - CONFIG.cooking.channelSeconds = 3. Player stands still; progress bar in
     the cook panel (keep panel open during the channel).
   - Interrupt: movement input, damage, fire dying mid-channel, Cancel.
     Interrupt = ingredients returned in full, fuel for that cook refunded,
     toast "Cooking interrupted". No partial results.
   - Fuel: deduct burnPerCookSec at cook start. Fire must have >= channel
     length of fuel to start (else prompt says the fire is too low).
5. FOOD USE + BUFF LAYER (first buff system).
   - Usable food via the existing inventory use path (bandage pattern).
   - Eating graveSoup: buff {stat 'hpMax', amount +20} while active. Effective
     hpMax = CONFIG base + active buffs; clamp current hp inside new max.
     Buff row on HUD (icon + remaining time), CONFIG-driven label "Grave Soup".
6. CAMPSITE-KIT MOMENT (stub only): on first successful cook (same beat as
   recipe learn), toast "Campsite kit acquired" and reveal a small HUD
   campsite button (camp icon, CONFIG-styled). C1 it is INERT: click shows
   tooltip toast "Set up camp - needs open ground (coming soon)". C3 owns
   real deploy. No inventory item is granted (kit is a UI button, per design).
7. TUTORIAL TOASTS (minimal, no quest system): the fireside interact prompt
   is the tutorial ("E to cook"); no quest beats in C1.

## ACCEPTANCE (Nicko playtest, his verdict is the gate)
A1. Bandit campfire in Region B: E opens the cook panel while lit.
A2. Cooking graveMoss+wildMushroom+boneShard yields Grave Soup, learns the
    recipe, shows the campsite-kit toast + inert HUD button once.
A3. Wrong trio yields Bland Mush; ingredients consumed; Bland Mush edible,
    no buff.
A4. Recipe known: one-click cook from the recipe list when ingredients exist.
A5. Channel: moving/cancelling/taking a hit within 3s interrupts, ingredients
    return, fire fuel refunded.
A6. Fuel: fire burns down over time (visible light-out); E + deadwood
    relights; cooking blocked when burnt out or too low on fuel.
A7. Eating Grave Soup: HP bar max visibly extends (+20), HUD buff chip with
    countdown. No other stat moves. Bandage still works as before.
A8. Region A campfire (dressing) unchanged; no other fire cooks. No NEW node
    types anywhere; Region A mushroom clusters now sit around the cemetery
    yard (CEMETERY ECOLOGY), clear of the yard interior.
A9. Cook panel without mushrooms in the bag shows the cryptic hint
    "Mushrooms favor the dead..." (once per session).
A10. All edited files pass node --check; v8 bundle contains C1 markers.

## FILES
- prototype/js/CONFIG.js (CONFIG.cooking block + graveSoup/blandMush items;
  regionA mushroomCluster coords relocated per CEMETERY ECOLOGY; NO mouse
  keys, NO new node types)
- prototype/js/cooking.js (NEW; declared in index.html script order +
  tools/build_v8.py concatenation list, before game.js, after inventory.js)
- prototype/js/game.js (interact branch, fuel tick hook, buff application)
- prototype/js/inventory.js (food use path, cook panel inventory calls)
- HUD buff chip row - follow the existing HUD file layout; do not restructure
- prototype/index.html, prototype/style.css (panel + button + chip)
- tools/build_v8.py only if the concat list needs the new file
- io/missions/2026-10-05-cc-c1-cooking.md (this file, already committed)

## COMMITS (feat/world-visuals, push after each)
1. feat(cooking): CONFIG cooking block + graveSoup/blandMush items
2. feat(cooking): station fuel + cook channel + panel (js/cooking.js + hooks)
3. feat(cooking): buff layer + food use + HUD buff chip + kit stub
4. build: v8 bundle (worktree only) - run tools/build_v8.py in the worktree;
   grep -c graveSoup prototype/builds/v8-playable.html must be non-zero
5. After push: refresh the host clean checkout for 8793 ONLY after checking
   the remote tip still equals the pushed sha:
   host-side `git -C /tmp/wh-worldfeat-clean checkout --detach <new-sha>`,
   then curl the bundle for HTTP 200. Report both surface states.

## REPORT (<= 50 lines)
Files + CONFIG knobs added (with defaults), fuel/channel numbers, commits
table, push + serving confirmation, watch items (anything you could not
verify without running the game).