# AB1 CHANGE ORDER BRIEF - ACTION BAR EQUIP + SPELL BELT + PIXEL ICONS

Order: Nicko 2026-10-06 playtest arc, after C3.1c tent landed. Builder:
Claude Code CLI print-mode, model opus, --allowedTools "Read,Write,Edit,Bash"
(io profile home: HOME=/home/hermeswebui/.hermes/profiles/io/home,
PATH=$HOME/.local/bin:/app/venv/bin:$PATH, claude at $HOME/.local/bin).
Dispatch ONLY on Nicko's explicit GO. All work in the /tmp/wh-worldfeat
worktree (branch feat/world-visuals). One change order at a time.

## Goal

Make the bottom action bar REAL and ICONIC. Five upgrades, all riding the
Order B/C machinery that is already live (see STATE; do not rebuild it):

1. ITEM SLOTS: the bar carries item slots (shield, magic glove at minimum,
   torch welcome). Selecting an item slot EQUIPS that item into its hand
   role, replacing whatever the hand role holds. This is the DIRECT-SELECT
   version of the existing Q swap - reuse the qSwap machinery
   (CONFIG.equip.qSwap, toggleLoadout, equipItem/unequipHand, refusal
   toasts), do not build a parallel system.
2. SPELL BELT: when the magic glove is the equipped implement, keys 1 and 2
   select (cycle) between the two learned spells (firebolt, radiance). The
   selected spell's slot shows ACTIVE and LMB casts it (existing Order C
   per-hand cast: bindings.main -> right-hand glove cast on LMB).
3. GLOVE-GATING: when the glove is NOT equipped the spell slots go DARK
   (visually disabled, cannot be cycled) - no implement, no spells.
   Re-equipping re-lights them. (#wh-belt.stowed dim already exists per-hand
   - extend it to per-slot unpressable state.)
4. ICONS: replace ALL text-abbreviation slots with pixel art icons per the
   ICON PLAN below - item icons (shield, magic glove, longsword, torch,
   potions, food) and spell icons (firebolt, radiance), across the action
   bar, consumable slots, CHARACTER tab, inventory grid, and buff chips.
5. TOUCH PARITY: the bar works via touch - tapping a slot = selecting it.

## LOCKED RULINGS (Nicko's exact terms - do not reinterpret)

- MAGIC CANON (Nicko 10-05, binding): spells are learned knowledge
  (books/scrolls teach them); NO consumable spell charges; casting requires
  an equipped implement - magic glove < wand < staff (power tiers); belt
  select among learned spells only. The kit entries fireboltCharge /
  radianceCharge from the 10-05 inventory order are retired placeholders -
  no charge mechanic of any kind.
- "This is the direct-select version of the existing Q swap - reuse the
  qSwap machinery, do not build a parallel system." (AB1 order)
- "when the glove is NOT equipped, the spell slots go DARK (visually
  disabled) and cannot be cycled - no implement, no spells. Re-equipping
  re-lights them." (AB1 order)
- Art law: the pixel register - 512 source max, NEAREST downscale, 5-bit
  posterize, darkwood palette, ONE accent per icon (amber = human
  fire/spells, cyan reserved for magic, red pact).
- NO HARNESS LAW (Nicko): no automated game runs, no headless browser smoke
  passes, no harness of any kind. Syntax validation = node --check on
  edited JS only, using the playwright driver node at
  /usr/local/lib/python3.12/site-packages/playwright/driver/node. Nicko's
  playtest on the WebUI Playtest button is the ONLY acceptance test.

## PENDING NICKO - resolve at dispatch, never guess

- Q1 SPELL NAME: order chat said "fireball"; the implemented spell is
  firebolt (CONFIG.spell.firebolt, name 'Firebolt'). Confirm UI/name
  surfaces say Firebolt. IO rec: keep Firebolt as implemented.
- Q2 SLOT MAP: IO rec = 1 Firebolt / 2 Radiance / 3 Shield / 4 Magic Glove
  / 5 Torch. Variant = 5 Longsword instead of 5 Torch (torch is the night
  utility swap; longsword is right-hand native and already permanently in
  hand at boot). PENDING his pick.
- Q3 REPLACE SEMANTICS: when a select replaces the item in a hand, the
  replaced item returns to the INVENTORY (qSwap parity, equipItem pulls
  from inventory, unequipHand returns to grid; refusal toast when the
  incoming item is not in inventory). PENDING his confirmation vs empty
  hand / destroy.
- Q4 ICON DELIVERY: IO rec = individual PNGs authored in the asset lane +
  a generated js/icons-data.js (data-URI registry) that all slots consume.
  Works on both serve surfaces, build tool inlines it like other JS, no
  fetch/cache path. Alternatives on offer: CSS sprite atlas +
  background-position, or individual fetched PNGs. PENDING his pick.

## STATE (IO census, verified 2026-10-06 ~21:50 UTC)

- Repo /workspace/witch-hunter (host /root/projects/witch-hunter, one shared
  .git). Worktree /tmp/wh-worldfeat on feat/world-visuals, CLEAN, HEAD
  9f83286 == origin/feat/world-visuals (host fetch verified; container git
  fetch is broken by design - fetch URL is an SSH alias that only resolves
  host-side).
- Serving: 8793 flips at /tmp/wh-playtest-share/current ->
  releases/9f832869f83286404200 (RELATIVE symlink target per fix 0d48bb6);
  bundle prototype/builds/v8-playable.html returns 200 host-curl.
  /playtest-feat/ on 8787 serves this worktree LIVE.
- Blast radius (code-review-graph impact --repo /tmp/wh-worldfeat --depth 3,
  files prototype/js/CONFIG.js prototype/js/player.js prototype/js/game.js
  prototype/js/touch-controls.js prototype/js/inventory.js
  prototype/style.css; graph 215 files / 1782 nodes / 23739 edges):
  145 nodes directly changed, 0 nodes impacted within 3 hops, 0 additional
  files affected.
- Boot state: CONFIG.equip.defaultHands = { right: 'longsword',
  left: 'magicGlove' }; grid starts with shield + bandage + glove #2;
  belt = ['firebolt','radiance',null,null,null]; bindings main=0/off=0;
  activeLoadout=1; Q pair = ['magicGlove','roundShield'].
- Main checkout /workspace/witch-hunter sits on feat/mouse-bind-cam with
  uncommitted churn owned by another lane - NEVER touch that checkout.
- Worktree graph for this order (already built): repo /tmp/wh-worldfeat,
  alias wh-worldfeat.

## EXISTING MACHINERY (Order C landed 2026-10-05 - AB1 UPGRADES it)

Anchors in prototype/ (line numbers at 9f83286):

- js/player.js:337-367 keybind listener: Backquote mouse-bind, Space dodge
  latch, KeyF lock, KeyQ toggleLoadout (line 357), Digit prefix parsing
  lines 360-363 -> pressBeltKey(n-1, e.shiftKey ? 'off' : 'main'), KeyR/KeyT
  consumables (365-366). AB1: Digit routing becomes the ACTION-BAR select
  path; Shift+Digit keeps the Order C off-hand bind semantics.
- js/player.js:697-716 toggleLoadout: qSwap target resolution
  (hands.left === pair[0] ? pair[1] : pair[0]), inventory.countOf(target)
  refusal, pendingQSwap + toggling window, endBlock + endCombo + armed
  banking. THE MACHINERY ITEM SLOTS REUSE.
- js/player.js:931-951 equipItem(id, hand, inventoryOnly, force): gear +
  hands check, mesh-required refusal for dormant shields/swords, countOf
  decrement, inventory.hasRoomFor refusal path.
- js/player.js:954-962 unequipHand(hand): return to grid, Inventory full
  refusal.
- js/player.js:721-756 Order C per-hand cast state + selectBeltSlot(i,
  role): empty-slot refusal flash, bindings[role]=i, regrip window, 
  onSpellSelected callback. AB1 SPELL SLOTS CALL THIS.
- js/player.js:761-768 pressBeltKey: dropPendingCast + selectBeltSlot.
- js/player.js:838-855 capability flags: hasCaster, casterHand,
  isCasterHand, hasShield. The glove-gate predicate lives here.
- js/player.js:884-889 handAction(hand): right melee -> attack, caster ->
  cast, left shield -> block, else null. LMB already casts the glove hand.
- js/player.js:987-996 updateCastState: activeLoadout derivation
  (left === qSwap[0] ? 1 : left === qSwap[1] ? 2 : 0), applyHandVisuals,
  onHandsChanged. AB1: the HUD reads these for bar active states.
- js/game.js:263-285 belt DOM build: #wh-belt, 5 .belt-slot (text digits),
  spell-divider, 2 consumable slots, loadout pips I/II.
- js/game.js:505-538 belt update loop: stowed toggle from p.hasCaster(),
  main binding solid school-color border, off binding dashed + L badge,
  filled/selected/off-bound classes, consumable charges, loadout pips.
- prototype/style.css:312-408: #wh-belt, .belt-slot 30px, .filled,
  .selected, .consumable, .off-bound (+ ::after 'L' badge), #wh-belt.stowed
  opacity 0.45 + divider 'S' badge.
- js/CONFIG.js:699-708 WH_CONFIG.belt (slots 5, defaultSpells, regrip 0.3);
  :658-659 firebolt def (schoolColor 0xff7722, name Firebolt, glyph 'FB');
  :684-685 radiance def (schoolColor 0xffd9a0, name Radiance, glyph 'RD');
  :1265-1321 WH_CONFIG.items (magicGlove/longsword/roundShield/torch/
  bandage/healthPotion-consumable/graveSoup/blandMush/ingredients, each
  with a text glyph); :1698-1709 WH_CONFIG.equip (defaultHands, twoHand,
  qSwap, nativeHand).
- js/inventory.js:199-213 + 360-361 inv-glyph spans; :387-388 spellGlyph;
  :409-445 CHARACTER tab hand slots + spell binding tiles (glyphs);
  :482-484 gear rows.
- js/touch-controls.js:29 controls order array; :172-176 LABELS (glyph
  unicode); :597-618 btnPress (attack -> p.handButton('lmb', true), block
  -> 'rmb', dodge -> tryRoll, lockon, interact, sprint toggle); :620-625
  btnRelease. AB1: belt-slot taps handled on the HUD DOM itself; the touch
  BUTTON layer only needs no regression.
- index.html:41-61 script order: vendor, moveset, CONFIG, region-defs,
  assets, anim, spells, inventory, cooking, daynight, light, gather,
  corpse-loot, player, enemy, region-manager, camp, touch-controls, game.
  Any new icon registry script loads after CONFIG.js, before game.js
  (data-only, no deps).

## SCOPE (implementation contract)

S1 CONFIG (js/CONFIG.js): add WH_CONFIG.actionbar block - slot map per Q2
(the 5 slots, each { kind: 'spell'|'item', id }), plus icon registry ids.
Do not touch belt defaults semantics; belt remains the spell list
(defaultSpells) that spell slots read. Add WH_ICONS id list if Q4 picks a
registry-driven map.

S2 PLAYER (js/player.js): new selectActionSlot(i, shift) called from the
Digit parsing path (replacing the direct pressBeltKey call):
- slot kind 'spell' -> pressBeltKey(i, shift ? 'off' : 'main') (existing
  Order C semantics preserved; Shift+Digit still off-binds).
- slot kind 'item' -> direct equip: resolve hand (items config: shield and
  glove native left, torch native left, longsword right), target item must
  be in inventory (countOf >= 1) else refusal toast (same text shape as
  toggleLoadout), then reuse the pendingQSwap + toggling window path so
  equip timing, block drop, combo reset, and armed banking behave exactly
  like Q (single shared code path - a selectItemEquip(id) helper that
  toggleLoadout also routes through where semantics match).
- Glove-gate for spell slots: when !isCasterHand-bearing implement equipped
  (use existing stowed predicate p.hasCaster()), spell digit presses refuse
  exactly like empty slots (existing refusal flash) - and the HUD shows the
  slots dark (S3).
- Keep consumables R/T and all other keybinds untouched.

S3 HUD (js/game.js): belt DOM becomes icon-driven: each slot's text node ->
icon element (js/icons-data.js registry). Item slots show their item icon;
spell slots show spell icons; active spell gets the existing school-color
border treatment; when stowed, spell slots additionally get a .dark class
(unpressable, dimmer than the stowed row, cursor default). Update loop
(game.js:505-538) extended for item-slot active states (the equipped item's
slot highlighted) and .dark toggling.

S4 CSS (prototype/style.css): belt slots grow to hold icon art (keep row
footprint similar; image-rendering pixelated), .belt-slot.dark state,
selected/active treatments for item slots, icon frame consistent with the
darkwood chrome. No HUD repositioning, no new HUD elements.

S5 ICON REGISTRY (js/icons-data.js NEW + wiring): data-URI map id -> png.
Wire ALL glyph surfaces: belt slots, consumable slots, CHARACTER tab hands
+ spell tiles, inventory grid inv-glyph spans, buff chips (buff id ->
matching food item icon), loadout pips may stay I/II text (not
abbreviations). Fallback: unknown id -> previous glyph text (never blank).

S6 TOUCH (js/touch-controls.js or the HUD layer): belt-slot DOM pointerdown
-> same select path as the Digit keys (respect inputSuspended and p.state
'alive' guards; swallow the event so it never reaches the canvas LMB/attack
path or the auto-rebind). Edit-mode placement of the touch layer is NOT
extended for the bar in this order (bar is HUD DOM, always visible).

Out of scope: no new items, no wand/staff tiers, no charge system, no HUD
repositioning, no dev/main merge, no docs/, no CONFIG.mouse, no harness.
Never touch /workspace/witch-hunter main checkout or any other branch.

## ICON PLAN (Nicko's section, verbatim, expanded)

- Art law: icons follow the pixel register - 512 source max, NEAREST
  downscale, 5-bit posterize, darkwood palette, ONE accent per icon
  (amber for human fire/spells, cyan reserved for magic, red pact).
- Item icons: PIPELINE OPTION A (recommended) - render the EXISTING 3D
  GLBs (roundShield, magicGlove, longsword, torch, gravedigger hand props)
  through the proven blender/ortho QA pipeline (scratch/tree_ortho.py
  pattern or roundJ2_base_render.py) at a fixed 3/4 angle and flat light,
  downscale to 48x48 NEAREST, posterize. Zero new art, perfect consistency
  with the world assets.
  IO lane note (verified at census): the render lane has a pure-Python
  ortho precedent (scratch/tree_ortho.py - numpy/trimesh/matplotlib painter
  render, no blender needed) and roundJ2_base_render.py as the blender-CLI
  precedent. GLB reality at 9f83286: round-shield.glb, longsword.glb,
  torch.glb EXIST in art-direction/3d/assets/weapons/; there is NO glove
  mesh anywhere (the worn glove is a placeholder caster-glow), so the
  glove icon is generated in the 2D pass below. Torch icon should carry the
  amber flame accent; shield/sword stay darkwood steel/wood tones.
- Spell icons: OPTION A has no meshes, so plan a 2D generation pass:
  image_generate (IO-side tool, produces base art to pixelize) and/or
  procedural pixel grids authored as PNGs. Firebolt = amber flame dart,
  Radiance = pale gold burst. Spell icons must read at 24px HUD size.
- Deliverable format decision for Nicko: single sprite atlas PNG + CSS
  background-position, or individual PNGs (IO rec: individual PNGs
  authored, delivered as js/icons-data.js data-URI registry - see Q4).
- The icon generation is IO/asset-lane work (NOT the code builder) - IO
  generates + commits the PNGs and js/icons-data.js BEFORE the builder is
  dispatched; the builder only wires the registry.
- Icon list for this order (16): roundShield, magicGlove, longsword, torch,
  healthPotion, bandage, graveSoup, blandMush, firebolt, radiance,
  wildMushroom, graveMoss, boneShard, forestHerb, deadwood, stolenCoin.
  Inventory grid shows all of these; belt shows shield/glove/torch + the
  two spells; buff chips map buff ids to their food item icons.

## FILES

- js/CONFIG.js (actionbar block; no belt semantics change)
- js/player.js (Digit routing -> selectActionSlot; selectItemEquip helper
  reusing qSwap machinery)
- js/game.js (belt DOM + update loop icons/active/dark)
- js/icons-data.js NEW (data-URI registry; loads after CONFIG.js)
- prototype/style.css (belt icon sizes, dark state, item active states)
- js/touch-controls.js (belt tap handling if not in game.js DOM path)
- prototype/builds/v8-playable.html (build commit via tools/build_v8.py)
- io/missions/2026-10-07-cc-ab1-actionbar-spells.md (this brief - already
  committed by IO before dispatch)

## ACCEPTANCE (Nicko's playtest list - his verdict is the gate)

A1 The bar shows pixel icons, not letters: shield/glove/torch item icons on
   item slots, firebolt + radiance spell icons on spell slots; inventory
   grid and CHARACTER tab read as icons; buff chips show food icons.
A2 Pressing 1 selects Firebolt (slot lights with school color), pressing 2
   selects Radiance; LMB casts the selected spell through the glove hand.
A3 Pressing 3 puts the shield in the offhand (replacing the glove, glove
   back in inventory), pressing 4 puts the glove back (shield returns); the
   swap uses the same 0.8s window/rhythm as Q - timing feels identical.
A4 Pressing 5 equips the torch in the offhand; torch light behavior
   unchanged from today.
A5 With glove unequipped (shield + torch state), slots 1-2 are DARK and
   pressing them flashes the refusal; re-equipping the glove re-lights 1-2
   and LMB casts again.
A6 Selecting a slot whose item is NOT in inventory refuses with a toast and
   changes nothing.
A7 Touch: tapping a bar slot selects it (spell or equip) on the phone
   layer; double-fire of attack taps impossible.
A8 No regression: Q swap, Shift+Digit off-bind, R/T consumables, block,
   dodge, night lighting, camp menu, sleep wake-snap all behave exactly as
   in C3.1c. Icons stay crisp (pixelated upscale, no blur) at playtest HUD
   size.

## COMMIT UNITS + LAWS

- Commit identity: CaptainPickard <pickard.nicko@gmail.com>.
- Commit units: (1) icons asset lane pre-landed by IO (PNGs + js/
  icons-data.js); (2) builder wiring commit(s) (CONFIG/player/game/CSS/
  touch); (3) build commit: python3 tools/build_v8.py from repo root +
  marker grep (grep -c "AB1" prototype/builds/v8-playable.html > 0) and
  grep for icons-data.js inline content.
- PUSH AFTER EVERY COMMIT (feat/world-visuals from this worktree; origin
  push URL is HTTPS credential-store).
- FETCH_HEAD guard: before committing, HEAD must still equal origin
  tip-of-record; if the origin branch gained new prototype/tools commits,
  STOP and report.
- Syntax validation: node --check (playwright driver node) on every edited
  JS file. Nothing else runs.
- Never touch /workspace/witch-hunter checkout, dev, main, docs/,
  CONFIG.mouse, scratch/.mixamo-credentials.txt, .mixamo-storage.json.
- FINAL REPORT <= 50 lines: commits table (sha + subject), per-file
  changes, node --check results, bundle marker counts, watch items.