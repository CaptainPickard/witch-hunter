# AB1 CHANGE ORDER BRIEF - ACTION BAR EQUIP + SPELL BELT + PIXEL ICONS (v2)

Order: Nicko 2026-10-06 playtest arc, after C3.1c tent landed. Builder:
Claude Code CLI print-mode, model opus, --allowedTools "Read,Write,Edit,Bash"
(io profile home: HOME=/home/hermeswebui/.hermes/profiles/io/home,
PATH=$HOME/.local/bin:/app/venv/bin:$PATH, claude at $HOME/.local/bin).
Dispatch ONLY on Nicko's explicit GO. All work in the /tmp/wh-worldfeat
worktree (branch feat/world-visuals). One change order at a time.
v2: Nicko answered Q1-Q4 - rulings below are DECIDED, no guessing left.

## Goal

Make the bottom action bar REAL, ICONIC, and PLAYER-MAPPABLE. Six upgrades,
all riding the Order B/C machinery that is already live (see STATE; do not
rebuild it):

1. ITEM SLOTS: the bar carries item slots (shield, magic glove, torch by
   default). Selecting an item slot EQUIPS that item into its hand role,
   replacing whatever the hand role holds. This is the DIRECT-SELECT
   version of the existing Q swap - reuse the qSwap machinery
   (CONFIG.equip.qSwap, toggleLoadout, equipItem/unequipHand, refusal
   toasts), do not build a parallel system.
2. PLAYER-MAPPABLE BAR (Nicko Q2): NO hardcoded slot roles. Every slot can
   be bound by the PLAYER to any learned spell OR any owned gear item.
   Boot defaults = [Firebolt, Radiance, roundShield, magicGlove, torch],
   but rebinding is a first-class player action:
   - DESKTOP: right-click a bar slot -> binding picker panel opens
     (learned spells section + owned gear section, icons + names); click an
     entry -> that slot is bound to it. Esc / picker X / clicking elsewhere
     closes it.
   - TOUCH: press-and-HOLD a bar slot (~400ms, CONFIG actionbar.longPressMs)
     -> same picker; tap an entry to bind. Distinguish tap (select) from
     hold (rebind) cleanly; a held slot must NOT fire its select action.
   - PERSISTENCE: the map survives reloads in localStorage (key per
     CONFIG.actionbar.lsKey), same pattern as touch-controls placement
     (touch-controls.js loadState/saveState). C4 save-profile migration is
     a later order - localStorage is the sanctioned prototype mechanism.
3. SPELL BELT: when a slot is bound to a learned spell and the magic glove
   is the equipped implement, selecting that slot binds the spell to the
   main hand (Order C selectBeltSlot / pressBeltKey path). The selected
   spell's slot shows ACTIVE (school-color border) and LMB casts it
   (right-hand glove cast through handButton('lmb')). Shift+Digit keeps the
   Order C off-hand bind semantics for spell slots (off binding = dashed
   outline + L badge, existing). Item-bound slots refuse Shift+Digit off
   binds ('not a spell').
4. GLOVE-GATING: when the glove is NOT equipped, SPELL-bound slots go DARK
   (visually disabled, cannot be cycled/selected - refusal flash like
   empty slots). No implement, no spells. Re-equipping re-lights them.
   (#wh-belt.stowed dim already exists per-hand - extend to per-slot
   unpressable state.)
5. ICONS: replace ALL text-abbreviation slots with pixel art icons per the
   ICON PLAN below - item icons (shield, magic glove, longsword, torch,
   potions, food) and spell icons (firebolt, radiance), across the action
   bar, consumable slots, CHARACTER tab, inventory grid, and buff chips.
6. TOUCH PARITY: the bar works via touch - tap = select (equip / bind
   spell), hold = rebind picker.

## DECIDED RULINGS (Nicko, 2026-10-06 clarify form - LOCKED)

- Q1 NAME: FIREBOLT. No Fireball naming anywhere; CONFIG.spell.firebolt
  name 'Firebolt' stays as implemented.
- Q2 MAP: "i dont want them auto mapped for me, i want to be able to map
  them myself, give player choice to what they want to map the action bar
  for" - the bar is player-mappable per Goal #2; boot defaults are a
  convenience, not a contract. Rebind UX = right-click (desktop) /
  long-press (touch) -> picker panel.
- Q3 REPLACE SEMANTICS: swap-parity - when a slot select replaces the item
  in a hand, the replaced item returns to the INVENTORY (qSwap parity:
  equipItem pulls from inventory, unequipHand returns to grid; refusal
  toast when the incoming item is not in inventory). Never destroy, never
  drop-to-ground on replace.
- Q4 ICON DELIVERY: individual PNGs wired via a generated js/icons-data.js
  data-URI registry that all slots consume. Works on both serve surfaces,
  build tool inlines it like other JS, no fetch/cache path.
- MAGIC CANON (Nicko 10-05, binding): spells are learned knowledge
  (books/scrolls teach them); NO consumable spell charges; casting requires
  an equipped implement - magic glove < wand < staff (power tiers); belt
  select among learned spells only. The kit entries fireboltCharge /
  radianceCharge from the 10-05 inventory order are retired placeholders -
  no charge mechanic of any kind.
- Art law: the pixel register - 512 source max, NEAREST downscale, 5-bit
  posterize, darkwood palette, ONE accent per icon (amber = human
  fire/spells, cyan reserved for magic, red pact).
- NO HARNESS LAW (Nicko): no automated game runs, no headless browser smoke
  passes, no harness of any kind. Syntax validation = node --check on
  edited JS only, using the playwright driver node at
  /usr/local/lib/python3.12/site-packages/playwright/driver/node. Nicko's
  playtest on the WebUI Playtest button is the ONLY acceptance test.

## STATE (IO census, verified 2026-10-06 ~21:50 UTC)

- Repo /workspace/witch-hunter (host /root/projects/witch-hunter, one shared
  .git). Worktree /tmp/wh-worldfeat on feat/world-visuals, CLEAN, HEAD
  187e882 (brief v1 + census) == origin/feat/world-visuals (host fetch
  verified; container git fetch is broken by design - fetch URL is an SSH
  alias that only resolves host-side).
- Serving: 8793 flips at /tmp/wh-playtest-share/current ->
  releases/9f832869f83286404200 (RELATIVE symlink target per fix 0d48bb6;
  the flip updates on the build commit of this order); bundle
  prototype/builds/v8-playable.html returns 200 host-curl. /playtest-feat/
  on 8787 serves this worktree LIVE.
- Blast radius (code-review-graph impact --repo /tmp/wh-worldfeat --depth 3,
  files prototype/js/CONFIG.js prototype/js/player.js prototype/js/game.js
  prototype/js/touch-controls.js prototype/js/inventory.js
  prototype/style.css; graph 215 files / 1782 nodes / 23739 edges):
  145 nodes directly changed, 0 nodes impacted within 3 hops, 0 additional
  files affected. (+ js/icons-data.js is NEW - unmapped, additive.)
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
  banking. THE MACHINERY ITEM SLOTS REUSE (generalize: resolve target from
  the pressed slot instead of the fixed pair - a selectItemEquip(id)
  helper with identical window/block/combo/armed semantics; toggleLoadout
  may route through it).
- js/player.js:931-951 equipItem(id, hand, inventoryOnly, force): gear +
  hands check, mesh-required refusal for dormant shields/swords, countOf
  decrement, inventory.hasRoomFor refusal path.
- js/player.js:954-962 unequipHand(hand): return to grid, Inventory full
  refusal.
- js/player.js:721-756 Order C per-hand cast state + selectBeltSlot(i,
  role): empty-slot refusal flash, bindings[role]=i, regrip window,
  onSpellSelected callback. SPELL SLOT SELECTION CALLS THIS.
- js/player.js:761-768 pressBeltKey: dropPendingCast + selectBeltSlot.
- js/player.js:838-855 capability flags: hasCaster, casterHand,
  isCasterHand, hasShield. The glove-gate predicate lives here.
- js/player.js:884-889 handAction(hand): right melee -> attack, caster ->
  cast, left shield -> block, else null. LMB already casts the glove hand.
- js/player.js:987-996 updateCastState: activeLoadout derivation
  (left === qSwap[0] ? 1 : left === qSwap[1] ? 2 : 0), applyHandVisuals,
  onHandsChanged. AB1: the HUD reads these + the per-slot map for bar
  active states.
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
  btnRelease; :65-82 loadState/saveState localStorage pattern (fraction
  payloads). Belt-slot pointer handling lives on the HUD DOM (game.js
  element), not in the touch layer; the touch BUTTON layer needs no
  regression only.
- index.html:41-61 script order: vendor, moveset, CONFIG, region-defs,
  assets, anim, spells, inventory, cooking, daynight, light, gather,
  corpse-loot, player, enemy, region-manager, camp, touch-controls, game.
  js/icons-data.js loads after CONFIG.js, before player.js (data-only, no
  deps).

## SCOPE (implementation contract)

S1 CONFIG (js/CONFIG.js): add WH_CONFIG.actionbar block:
  slots: 5,
  defaults: [ {kind:'spell', id:'firebolt'}, {kind:'spell', id:'radiance'},
              {kind:'item', id:'roundShield'}, {kind:'item', id:'magicGlove'},
              {kind:'item', id:'torch'} ],
  lsKey: 'wh-actionbar-v1',
  longPressMs: 400,
  pickerExclude: ['bandage']  // consumables stay on R/T; gear-only picker
Do not touch belt defaults semantics; WH_CONFIG.belt stays the LEARNED
spell list that spell-bound slots read. Bindable item universe = gear
category with mesh (kind melee/shield/caster/torch); consumables/food/
ingredients/valuables are NOT bar-bindable (they stay inventory/R/T).

S2 PLAYER (js/player.js): new selectActionSlot(i, shift) called from the
Digit parsing path (replacing the direct pressBeltKey call), reading the
RUNTIME map (see S3 ownership - player owns map validation, HUD owns
editing):
- slot kind 'spell' -> pressBeltKey(i, shift ? 'off' : 'main') (existing
  Order C semantics; shift on an item-bound slot = refusal 'not a spell').
- slot kind 'item' -> direct equip: resolve hand from CONFIG.items[id]
  .hands + nativeHand (shield/torch/glove native left; longsword right),
  then: item already equipped in that hand = no-op (already active); item
  in inventory (countOf >= 1) = equip via the shared pendingQSwap-style
  window (selectItemEquip(id) helper with toggleLoadout's exact window/
  endBlock/endCombo/armed-banking semantics); item NOT owned = refusal
  toast '(name) not in inventory'.
- Glove-gate for spell slots: when !p.hasCaster() (existing predicate),
  spell presses refuse exactly like empty slots (refusal flash) - HUD
  shows those slots dark (S3/S4).
- Keep consumables R/T and all other keybinds untouched.

S3 HUD + RUNTIME MAP + PICKER (js/game.js): 
- Load/validate/save the map (localStorage lsKey; validate each entry
  kind/id; invalid or unknown = fall back to that slot's default; corrupt
  JSON = full defaults). Map mutation API on the HUD layer; player.js
  reads via a getter (single source of truth, no duplication).
- Belt DOM becomes icon-driven: each slot's text node -> icon element
  (js/icons-data.js registry). Item slots show their item icon; spell
  slots show spell icons; active spell gets the existing school-color
  border treatment; the equipped item's slot gets an ACTIVE treatment
  (S4); spell-bound slots get .dark when stowed (S2 rule).
- Binding picker panel: opens on slot right-click (desktop) / long-press
  (touch, longPressMs). Sections: LEARNED SPELLS (from p.getKnownSpells())
  and GEAR (inventory grid gear rows). Entries = icon + name; click binds
  that entry to the pending slot, saves the map, refreshes the bar, closes
  the picker. Esc / X button / outside click closes. Picker obeys
  inputSuspended (never opens under the inventory screen) and p.state
  'alive'. While the picker is open, suspend combat input like the
  inventory screen does (same inputSuspended path or scoped equivalent).
- Digit keys still select slots 1-5 (mappable map), Shift+Digit off-binds
  spell slots.

S4 CSS (prototype/style.css): belt slots grow to hold icon art (keep row
footprint similar; image-rendering pixelated), .belt-slot.dark state,
active treatment for the equipped item slot, picker panel styling in the
darkwood chrome (rgba dark panel, #d8b24a accents, pixelated entry icons),
long-press visual feedback optional. No HUD repositioning.

S5 ICON REGISTRY (js/icons-data.js NEW + wiring): data-URI map id -> png.
Wire ALL glyph surfaces: belt slots, consumable slots, CHARACTER tab hands
+ spell tiles, inventory grid inv-glyph spans, buff chips (buff id ->
matching food item icon), picker entries. Fallback: unknown id -> previous
glyph text (never blank). The PNGs themselves are PRE-LANDED by IO before
builder dispatch (IO/asset lane this order).

S6 TOUCH (js/touch-controls.js or the game.js HUD DOM path): bar slot
pointerdown/tap = the same select path as Digit keys (respect
inputSuspended and p.state 'alive'; swallow the event so it never reaches
the canvas LMB/attack path or the auto-rebind); long-press = picker.
Edit-mode placement of the touch layer is NOT extended for the bar in this
order (bar is HUD DOM, always visible).

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
  glove icon is generated in the 2D pass below. Torch icon carries the
  amber flame accent (wait - amber = human fire per canon: firebolt/torch
  amber; radiance pale gold; glove cyan as MAGIC); shield/sword stay
  darkwood steel/wood tones.
- Spell icons: OPTION A has no meshes, so plan a 2D generation pass:
  image_generate (IO-side tool, produces base art to pixelize) and/or
  procedural pixel grids authored as PNGs. Firebolt = amber flame dart,
  Radiance = pale gold burst. Spell icons must read at 24px HUD size.
- Deliverable (DECIDED Q4): individual PNGs wired via a generated
  js/icons-data.js data-URI registry - all slots/entries consume the
  registry; build tool inlines it; no fetch/cache path.
- The icon generation is IO/asset-lane work (NOT the code builder) - IO
  generates + commits the PNGs and js/icons-data.js BEFORE the builder is
  dispatched; the builder only wires the registry.
- Icon list for this order (16): roundShield, magicGlove, longsword, torch,
  healthPotion, bandage, graveSoup, blandMush, firebolt, radiance,
  wildMushroom, graveMoss, boneShard, forestHerb, deadwood, stolenCoin.
  Inventory grid shows all of these; bar defaults show firebolt/radiance/
  shield/glove/torch (+ any item the player binds); picker shows spells +
  owned gear; buff chips map buff ids to their food item icons.

## FILES

- js/CONFIG.js (actionbar block; no belt semantics change)
- js/player.js (Digit routing -> selectActionSlot; selectItemEquip helper
  reusing qSwap machinery)
- js/game.js (belt DOM + update loop icons/active/dark + runtime map +
  binding picker)
- js/icons-data.js NEW (data-URI registry; PNGs pre-landed by IO; loads
  after CONFIG.js)
- prototype/style.css (belt icon sizes, dark/active states, picker panel)
- js/touch-controls.js (belt tap/long-press handling if not fully in the
  game.js DOM path)
- prototype/builds/v8-playable.html (build commit via tools/build_v8.py)
- io/missions/2026-10-07-cc-ab1-actionbar-spells.md (this brief)

## ACCEPTANCE (Nicko's playtest list - his verdict is the gate)

A1 The bar shows pixel icons, not letters: item icons (shield/glove/torch
   defaults) + spell icons (firebolt/radiance); inventory grid and
   CHARACTER tab read as icons; buff chips show food icons; picker
   entries carry icons + names.
A2 Tapping 1 selects Firebolt (slot lights with school color), tapping 2
   selects Radiance; LMB casts the selected spell through the glove hand.
A3 Tapping 3 puts the shield in the offhand (replacing the glove, glove
   back in inventory), tapping 4 puts the glove back (shield returns); the
   swap uses the same 0.8s window/rhythm as Q - timing feels identical.
A4 Tapping 5 equips the torch in the offhand; torch light behavior
   unchanged from today.
A5 With glove unequipped (shield + torch state), spell-bound slots (1-2)
   are DARK and pressing them flashes the refusal; re-equipping the glove
   re-lights them and LMB casts again.
A6 Selecting an item slot whose item is NOT in inventory refuses with a
   toast and changes nothing. Replacing a hand item returns it to the
   inventory (swap-parity, Q3).
A7 REBIND (Q2): right-click (desktop) / press-and-hold (touch) a slot ->
   picker opens with learned spells + owned gear; binding an entry
   re-icons that slot; the new map selects correctly (spells cast, items
   equip); the map PERSISTS across a page reload; corrupt/invalid storage
   falls back to defaults without breaking the bar.
A8 Touch: tapping a bar slot selects it (spell or equip); long-press opens
   the picker; a long-press never fires the select action; attack taps
   never double-fire from bar touches.
A9 No regression: Q swap, Shift+Digit off-bind, R/T consumables, block,
   dodge, night lighting, camp menu, sleep wake-snap all behave exactly as
   in C3.1c. Icons stay crisp (pixelated upscale, no blur) at playtest HUD
   size.

## COMMIT UNITS + LAWS

- Commit identity: CaptainPickard <pickard.nicko@gmail.com>.
- Commit units: (1) icons asset lane pre-landed by IO BEFORE dispatch (PNGs
  + js/icons-data.js); (2) builder wiring commit(s) (CONFIG/player/game/
  CSS/touch); (3) build commit: python3 tools/build_v8.py from repo root +
  marker greps: grep -c "AB1" prototype/builds/v8-playable.html > 0 AND
  grep -c "icons-data" prototype/builds/v8-playable.html > 0 AND the
  bundle contains a data: URI (grep -c "data:image/png" > 0).
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

## IO NEXT STEPS AFTER BUILDER PASSES (post-build, before/at handoff)

1. Verify worktree truth per the change-order loop (log/status/marker
   greps/node --check reruns), then host-side: python3
   /root/projects/witch-hunter/tools/wh_release_flip.py <new-sha> and
   host-curl /current/prototype/builds/v8-playable.html = 200.
2. Handoff: both URLs + playtest flow keyed to A1-A9 + watch items.
3. Nicko verdict = the gate.