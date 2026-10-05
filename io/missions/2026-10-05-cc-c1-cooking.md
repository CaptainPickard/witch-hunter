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
  tent/bedroll work, no save system (C2-C4 own those).
- OTHER SESSION ACTIVE IN THIS REPO: work ONLY in the /tmp/wh-worldfeat
  worktree on feat/world-visuals. NEVER touch /workspace/witch-hunter (dev
  checkout), the dev or main branches, 8793 container state, or any branch
  except feat/world-visuals. BEFORE starting: reconcile with remote
  (`git -C /tmp/wh-worldfeat fetch https://github.com/CaptainPickard/
  witch-hunter.git feat/world-visuals` then compare tip). If the tip moved
  with changes outside io/missions, STOP and report to IO. Commit in small
  units and push immediately after each (git push origin feat/world-visuals;
  HTTPS remote credentials are in the credential store).
- Commit identity: CaptainPickard <pickard.nicko@gmail.com>.
- Never read/commit scratch/.mixamo-credentials.txt or .mixamo-storage.json.
- Player copy: never the word "free".
- CONFIG-first: every tunable number lives in CONFIG with a comment.

## STATE (verified 2026-10-05, feat tip before this brief)
- feat/world-visuals worktree /tmp/wh-worldfeat clean at the brief's parent.
- Serving: 8793 host container + WebUI /playtest-feat/ both serve the worktree
  live (no-store). No deploy step for game files; do a build commit (below).
- Existing hooks C1 builds on:
  - Interact: game.js interact() = box pickup > corpse > gather, E key +
    touch USE. Cooking is a new branch on this chain (nearest lit cooking
    fire within radius).
  - Items: CONFIG.js items registry (bandage pattern for a usable item);
    ingredients forestHerb/deadwood/wildMushroom/graveMoss/boneShard exist
    (category 'ingredient'); cooking ingredients never drop from enemies.
  - Gather: js/gather.js WH_GATHER; Region B nodes today = graveMoss x5 +
    bonePile x4 ONLY (no mushrooms in B - fix in scope below).
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
3. RECIPES + DISCOVERY (CONFIG.cooking.recipes).
   - Grave Soup: graveMoss + wildMushroom + boneShard. Result item graveSoup
     ('food', glyph 'GS', weight 20). Effect: +20 max HP for 1 in-game day
     (pre-C2: CONFIG.cooking.buffDurationFallbackSec = 480 real seconds,
     comment notes it converts to day-length in C2). Stacks nothing: one
     instance max (re-eat refreshes duration).
   - Bland Mush: any other trio at a campfire. Result item blandMush ('food',
     glyph 'BM', weight 15). Edible, grants NO buff, flavor copy
     "A sad grey mush". The gamble's waste.
   - Discovery: first successful Grave Soup cook sets recipes.graveSoup.known
     = true + toast "Recipe learned: Grave Soup". Recipe knowledge persists
     for the session; C4 save will write it.
   - Extensible: recipes[] rows carry {id, name, ingredients[3], result,
     effect}; known flag; unknown trio = Bland Mush path. No preview ever.
4. CHANNELLED COOK.
   - CONFIG.cooking.channelSeconds = 7. Player stands still; progress bar in
     the cook panel (or HUD top-center if panel must close - keep panel open).
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
6. GATHER NODE FIX (data): add 2-3 mushroomCluster nodes to regionB.nodes in
   the existing darkwood band (|x| < 42, z -82..-31), obeying the band's
   clearance rules (props 3-4m, enemies 5m, spawn 6m, nodes 6m apart). Extend
   scratch/gen_gather_nodes.py or hand-place with a checked-clearance script;
   commit the chosen coords in CONFIG. Target: mushrooms findable within an
   easy walk of the bandit campfire.
7. CAMPSITE-KIT MOMENT (stub only): on first successful cook (same beat as
   recipe learn), toast "Campsite kit acquired" and reveal a small HUD
   campsite button (camp icon, CONFIG-styled). C1 it is INERT: click shows
   tooltip toast "Set up camp - needs open ground (coming soon)". C3 owns
   real deploy. No inventory item is granted (kit is a UI button, per design).
8. TUTORIAL TOASTS (minimal, no quest system): first approach to the lit
   bandit fire: "The fire still burns. E to cook." (fireside prompt suffices -
   use the standard interact prompt; extra hint toast only if trivial).

## ACCEPTANCE (Nicko playtest, his verdict is the gate)
A1. Bandit campfire in Region B: E opens the cook panel while lit.
A2. Cooking graveMoss+wildMushroom+boneShard yields Grave Soup, learns the
    recipe, shows the campsite-kit toast + inert HUD button once.
A3. Wrong trio yields Bland Mush; ingredients consumed; Bland Mush edible,
    no buff.
A4. Recipe known: one-click cook from the recipe list when ingredients exist.
A5. Channel: moving/cancelling/taking a hit interrupts, ingredients return,
    fire fuel refunded.
A6. Fuel: fire burns down over time (visible light-out); E + deadwood
    relights; cooking blocked when burnt out or too low on fuel.
A7. Eating Grave Soup: HP bar max visibly extends (+20), HUD buff chip with
    countdown. No other stat moves. Bandage still works as before.
A8. Region A campfire (Region A dressing) unchanged; no other fire cooks.
A9. All edited files pass node --check; build bundle contains C1 markers.

## FILES
- prototype/js/CONFIG.js (cooking block, items, regionB mushroom nodes)
- prototype/js/cooking.js (NEW; declared in index.html script order +
  tools/build_v7.py concatenation list, before game.js, after inventory.js)
- prototype/js/game.js (interact branch, fuel tick hook, buff application)
- prototype/js/inventory.js (food use path, cook panel inventory calls)
- prototype/js/hud.js or the HUD section it owns existing equivalents
  (buff chip row) - follow the file layout that exists; do not restructure
- prototype/index.html, prototype/style.css (panel + button + chip)
- tools/build_v7.py only if the concat list needs the new file
- io/missions/2026-10-05-cc-c1-cooking.md (this file, already committed)
- scratch/ placement-checkscript allowed (committed if repo-pattern says so)

## COMMITS (feat/world-visuals, push after each)
1. feat(cooking): CONFIG cooking block + graveSoup/blandMush + regionB
   mushroom nodes
2. feat(cooking): station fuel + cook channel + panel (js/cooking.js + hooks)
3. feat(cooking): buff layer + food use + HUD buff chip + kit stub
4. build: v7 bundle (worktree only) - run tools/build_v7.py in the worktree;
   grep -c graveSoup prototype/builds/v7-playable.html must be non-zero
5. After push: refresh the host clean checkout for 8793 ONLY if the other
   session has not moved the tip:
   host-side `git -C /tmp/wh-worldfeat-clean checkout --detach <new-sha>`,
   then curl the bundle for HTTP 200. Report both surface states.

## REPORT (<= 50 lines)
Files + CONFIG knobs added (with defaults), fuel/channel numbers, node coords
added + clearance math summary, commits table, push + serving confirmation,
watch items (anything you could not verify without running the game).