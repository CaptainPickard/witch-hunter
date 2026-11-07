# QJR-4 Bestiary Journal (kill-log + first-sight codex) — IO Spec

> Self-audit fixes (2): sec 2.8 killToastEvery comment now explicitly
> defines cadence = first kill + every Nth (N=5). sec 2.5 notes the per-type
> collapse semantics (fresh instances register, but the codex row set is
> per-type; a second instance of an already-witnessed type adds nothing).

Issued: 2026-11-07 (wake 31). IO = Nicko Pickard standing autopilot.
Branch: feat/world-visuals. Worktree: /tmp/wh-worldfeat. Build tool: v8 (newest
in tools/ at dispatch: tools/build_v8.py). Art anchors: concept-06-siege-council
+ concept-01-darkwood + concept-05-night-ambush (vision-QA'd wake 31).

## 1. Mission

Add a BESTIARY to the in-game journal (Nicko MorROWSIND order continues). The
player documents what he fights: one codex page per enemy type, inked in the
hunter's own hand. Two triggers, both event-driven, zero per-frame scans:

- KILL (primary): an acknowledged killing blow lands -> the codex entry gets a
  KILLS tally. "Acknowledged kill" = the blow that moves hp from > 0 to <= 0
  is dealt by the player (melee sweep, firebolt, enemy-bolt reflect path) —
  the same rule corpse loot already uses (Enemy.onKilled fires from
  enemy.js takeDamage; withered/saved-restored dead do NOT count).
- FIRST SIGHT (secondary): a live enemy first crosses INTO the player's
  existing sight radius (the idle->aggro/chase transition in
  Enemy.prototype.update) -> entry unlocks in a "witnessed" state (seen, 0
  kills), one toast per enemy type per save.

No HUD clutter: the codex is a tab inside the existing J journal panel.

## 2. Scope — build exactly this

### 2.1 New module prototype/js/bestiary.js (IIFE, same grammar as journal.js)

window.WH_BESTIARY with: init(g), update(dt), capture(), restore(block),
sightOf(typeKey), killsOf(typeKey), appendKill(enemy), appendSight(enemy),
isBorn(), isOpen(), closeForTest(). Module-level 'use strict'. NO THREE, no
scene roots, no new assets, no texture, no GLB, no audio.

### 2.2 Codex content table — CONFIG.js CONFIG.journal.bestiary (A9 law)

All player-facing strings live in CONFIG (never literals in js). Table =
CONFIG.journal.bestiary.entries keyed by enemy type: bandit, ghoul, wolf,
coven, zealot, rotmother, rotspawn, scarreader, tithecaptain, lastchancel.
Per entry: { title, sigil, page (the hunter's field note, 1-2 sentences,
ledger-compliant: may reference the pact/tithe/Veil as witnessed facts only,
NEVER the creditor), accent } where accent is one of the existing palette
tokens ('amber', 'crimson', 'bone', 'ash') as plain strings mapped in CSS
classes .codex-accent-<accent>. Sigils are TEXT glyphs (single unicode
glyph or 1-3 char ligature), NOT images.

### 2.3 Enemy payload

appendKill(enemy) / appendSight(enemy) take the live enemy object and read
enemy.type (the CONFIG.enemy key); unknown types are silently ignored (no
crash, no entry). Enemy cfg.name exists only for bosses; codex titles come
from the codex table, never from cfg.name.

### 2.4 Kill hook (small, single line, in prototype/js/enemy.js)

In Enemy.prototype.takeDamage, at the exact site where the killing blow is
ACKNOWLEDGED (the hp<=0 branch that fires Enemy.onKilled), AFTER the
onKilled handoff, add one guarded hand-off mirroring the onKilled pattern:

  if (window.WH_BESTIARY) window.WH_BESTIARY.appendKill(this);

Add ONE declaration next to the existing `Enemy.onKilled = null;` line:
`// QJR-4: bestiary kill hand-off (set by game.js, mirrors onKilled)` — the
init pattern (module attaches itself on window; game.js does nothing). Zero
other edits to enemy.js. The existing comment block above the onKilled call
must stay byte-identical elsewhere.

### 2.5 Sight hook (in prototype/js/bestiary.js, not enemy.js)

appendSight is called from bestiary.js's own update(dt), NOT from enemy.js:
bestiary.update keeps a module-level map of enemy -> witnessed, and scans
 NOTHING. Design: enemy.js keeps a single per-enemy flag written in the
 idle->aggro / idle->chase transition site (TWO sites in
 Enemy.prototype.update, lines ~517 and ~520: this.setFsm('aggro') and
 this.setFsm('chase') inside the canPull path) — add ONE line at each site,
 guarded: if (window.WH_BESTIARY) window.WH_BESTIARY.appendSight(this);
 appendSight itself is idempotent per enemy instance (Set semantics on the
 enemy object ref): repeated aggro/chase transitions on the same live mob
 add nothing; a mob that breaks aggro and later re-aggros does NOT need a
 second entry (already in the Set). NEW instances (a re-armed Rot Mother, a
 fresh pack) register independently — per-instance Set, not per-type. The
 per-TYPE witnessed set derives from instances via enemy.type.

### 2.6 Save roundtrip (pattern: journal capture/restore, game.js 2688-2723)

capture() -> { born: bool, witnessed: [typeKey...], kills: {typeKey: int},
days: {typeKey: firstSeenDay} }. restore(block) is additive-safe: missing
block = fresh empty codex (button hidden), malformed rows dropped, negative
kill counts dropped. Save-wrap wiring rides the EXACT existing journal
pattern in game.js (three sites: data.<key> capture, stored.<key> explicit
storage write, restore read) with key 'bestiary'. NO schema version bump
(additive, schema v1 law).

### 2.7 UI: a second tab in the J panel (prototype/js/journal.js + style.css)

The existing journal panel gains a tab row: JOURNAL | BESTIARY. journal.js
owns the DOM (it already owns the panel); bestiary.js registers content via
window.WH_BESTIARY and journal.js calls it. Rules:
- Tab row is two text tabs: 'JOURNAL' (default, active on open) and
  'BESTIARY'; CONFIG-driven labels CONFIG.journal.text.tabJournal /
  tabBestiary added to existing text block (A9).
- Active tab styling reuses the existing .inv-tab/.inv-tab.active grammar
  (same tokens as inventory tabs); NO new color literals in CSS — palette
  tokens only from the existing sheet (#0f0c09, #2a231b, #4a4034, #2a241c,
  #5a5344, #d8d2c0, #14110e, #e3dcc4, #d8b24a amber, #b0472f crimson,
  #c9a94a, parchment #e3dcc4/#d3c8a8, ink #221c15/#2a231b).
- Bestiary page = parchment page like journal-page (reuse .journal-page
  class + a .bestiary-page modifier for its own rows). Row grammar per
  enemy type: [sigil glyph] [title] [KILLS: n] [seen stamp: 'Day N - slain:
  m' when kills>0]. Undiscovered rows show LOCKED rows ('—' glyph, title
  'Unknown beast') so the ledger reads as an in-world codex with holes —
  locked rows show NOTHING but the sigil placeholder and the count of
  hidden entries as a single footer line ('N beasts remain undescribed.').
- Art-law compliance: parchment + ink + ONE accent per row (sigil tinted by
  entry accent class); zero gradients, zero glow, one accent per frame law
  respected (page background stays parchment; accents live only on sigils).
- Search box applies to the BESTIARY tab too (filters on title + page text;
  nomatch line reuses journal-nomatch grammar). J key open/close + Esc are
  UNCHANGED (same panel, same key law).
- The BESTIARY tab is hidden entirely until born (first sight or first
  kill); the tab row shows a single JOURNAL tab until then. journal button
  position/behavior untouched.
- Touch: the tabs are pointerdown-driven like the existing journal button
  (QJR-2 TC-FIX1 pattern: pointerdown focus/activation, stopPropagation,
  preventDefault, tabIndex -1).

### 2.8 CONFIG keys (new block CONFIG.journal.bestiary)

window.WH_CONFIG.journal.bestiary = {
  buttonless: true,           // no own HUD button, rides the J panel
  killToastEvery: 5,          // toast on every 5th kill of a type
  text: {
    tabBestiary: 'BESTIARY',
    tabJournal: 'JOURNAL',
    killsLabel: 'slain:',      // lowercase in-world voice
    seenStamp: 'Day {day}',
    hiddenFooter: '{n} beasts remain undescribed.',
    lockedTitle: 'Unknown beast',
    searchPlaceholder: 'Search the bestiary...',
    nomatch: 'Nothing in the bestiary matches.',
    killToast: 'Bestiary: {title} - slain x{n}',
    killToastTitleUnseen: 'Bestiary: first kill - {title}',
    killEveryLabel: 'Bestiary: {title} - slain x{n}',
    seenToast: 'Bestiary: witnessed - {title}',
    hint: 'Esc close'
  },
  entries: {
    bandit:    { title: 'The Sloppy Blade', sigil: '†', accent: 'bone',
                 page: "..." },
    ghoul:     { title: 'Grave-Hungry Ghoul', sigil: '☠', accent: 'ash', ... },
    wolf:      { title: 'Rot Wolf', sigil: '❂', accent: 'amber', ... },
    coven:     { title: 'Coven Witch', sigil: '✶', accent: 'crimson', ... },
    zealot:    { title: 'Veil-Touched Zealot', sigil: '☀', accent: 'crimson', ...},
    rotmother: { title: 'The Rot Mother', sigil: '✿', accent: 'crimson', ... },
    rotspawn:  { title: 'Rot Spawn', sigil: '✿', accent: 'ash', ... },
    scarreader:{ title: 'The Scar-Reader', sigil: '〰', accent: 'crimson', ... },
    tithecaptain: { title: 'The Tithe Captain', sigil: '⚖', accent: 'crimson', ... },
    lastchancel:{ title: 'The Last Chancel', sigil: '♆', accent: 'crimson', ... }
  }
}
Copy tone LAW: field-note voice, terse, first-person hunter, ledger-
compliant (no creditor, no signatory name; the pact/tithe/Veil as witnessed
facts only; doc 44/51 govern). Devbot drafts 10 page strings (1-2 sentences
each); Testerbot reviews them against the ledger law lines in this spec
sec 2.8 + doc 51 identity section.

### 2.9 Kill toast cadence

Toast at: first kill of a type, then every killToastEvery-th kill of that
type (5, 10, 15...). Toast text from CFG text strings; route through the
existing game.inventoryUI.toast (journal.js toast() pattern). Kill #1 of a
type that was previously only witnessed: use killToastTitleUnseen shape.
When a kill is of a type with NO codex entry (unknown type): totally
silent.

### 2.10 Boot + lifecycle (game.js, 1 line per site, mirroring journal)

- index.html: <script src="js/bestiary.js"></script> AFTER js/journal.js
  (alphabetical order in the boot list is not law; position AFTER journal).
- game.js boot init site (the 'QJR-1: journal core' init call @~2643): add
  window.WH_BESTIARY.init(game) guarded, AFTER the journal init line.
- update loop line (the journal update line @~3263): add
  window.WH_BESTIARY.update(dt) guarded, adjacent to the journal update.
- capture sites (data.<key> + stored.<key>): key 'bestiary'; restore site
  reads data.bestiary.
- closePanel death law: journal closePanel() on player death already
  closes the whole panel; bestiary has no own state beyond the tab — the
  journal's existing death close covers it. On player death with the
  bestiary tab ACTIVE, the panel closes (journal death law governs the
  whole panel).

## 3. Acceptance criteria (Testerbot checks each)

A-1 Codex unlock: fresh save, NO journal interactions: bestiary is hidden
    from the tab row until the player witnesses or kills the first enemy.
A-2 First sight: approach a live bandit (any enemy) until the existing idle
    path fires setFsm('aggro'); a witnessed row appears in the codex (seen
    stamp, 0 kills), toast fires once, and re-aggroing the same instance
    does not duplicate (idempotent per instance). A fresh second instance
    of the same type adds no new row (per-type collapse), only no change.
A-3 First kill: land the killing blow on a witnessed-type enemy -> kills
    tally +1, row updates in place, toast 'first kill' only on the
    witnessed-first-kill crossover (kill of an unseen type still unlocks
    the row as slain x1 AND witnessed in one event; no duplicate toasts).
A-4 Kill attribution: a withered minion death (lair withered=true path) or
    a save-restored dead corpse does NOT increment any tally (the hook only
    fires on the takeDamage acknowledgement site, which those paths bypass).
A-5 Cadence: kills 2-4 of a type are silent; kill 5 toasts (then 10, 15).
A-6 Save roundtrip: save -> reload -> witnessed set, kill counts, first
    days ALL survive byte-identical; a save from BEFORE this round loads
    without error (no bestiary key = empty codex, no crash, journal
    untouched).
A-7 Unknown type / malformed: appendKill on an enemy whose type has no
    codex entry is silent; restore with malformed/undefined blocks drops
    them and leaves journal/bestiary independent (malformed bestiary block
    must not poison the journal capture).
A-8 UI integration: J opens the panel; tabs switch via pointerdown; the
    BESTIARY tab respects the locked-row footer grammar; search filters
    bestiary rows with the nomatch grammar; Esc closes the whole panel;
    death closes the panel. No horizontal scrollbars; panel fits 320px
    width (same as journal).
A-9 Art law: page = parchment tokens only; sigils tinted by accent classes
    mapped from existing palette tokens; zero new color literals outside
    the existing token set; one accent per row.
A-10 A9 law: every player-facing string (titles, sigils, labels, toasts,
    footer, locked title, nomatch, search placeholder) lives in
    CONFIG.journal.bestiary.text / entries; zero literals in bestiary.js.
    Journal CFG strings untouched (journal.text stays byte-identical).
A-11 Zero regression: journal tab still behaves exactly as before (QJR-1/2/3
    acceptance preserved: unlock edge, append, search body rows, KeyJ guard
    in search, tc focus). enemy.js edits limited to the FOUR guarded one-
    line hand-offs specified (kill site 1 + sight sites 2 + the comment
    line near Enemy.onKilled = null). No other engine files touched.
    game.js edits limited to init/update/capture/restore/index.html lines.
A-12 Build tool: v10 (tools/build_v10.py) used; build lands in
    prototype/builds/v10-playable.html. Devbot runs node --check on ALL
    touched js files + the v10 tool; reports marker grep output.

## 4. Out of scope (deliberate)

- Boss pages get no extra mechanics (no weakness tags, no resistance
  tables) — doc 51 numbers stay on paper; this round is the codex SHELL +
  live tallies.
- No new concept art (anchors exist); no image assets, no icons.
- No achievements, no rewards, no XP hooks.
- Locked-row flavor text stays hidden by design (discovered text only).
- No doc 47/51 stat changes, no CONFIG.enemy edits.

## 5. Law reminders (non-negotiable)

- Work ONLY in /tmp/wh-worldfeat on feat/world-visuals. NO git add/commit/
  push by children (NO-GIT). No harness runs, no headless browser smoke
  tests — Nicko's playtest is the acceptance bar for playability; the
  gate's job is code validation.
- Build AFTER code lands: node syntax check first, then
  python3 tools/build_v8.py; verify the build marker; DO NOT claim
  playable. BUILD-TOOL CENSUS CORRECTION (wake 31): tools/ holds build_v7
  + build_v8; v8 is the CURRENT tool and writes
  prototype/builds/v8-playable.html (tab stamp 'build MM-DD HH:MMZ <sha>').
  There is NO v10/ v9 build script; this round builds with v8 and the
  spec's earlier 'v10' mention is withdrawn. The served file stays
  v8-playable.html so the WebUI button path is unchanged.
- A9 law: strings in CONFIG. One ACCENT per frame. No new assets.
- Report-first law: Devbot writes /tmp/delegation_result_devbot_qjr4.md +
  io/specs/qjr-4-bestiary-buildsummary.md BEFORE finishing; keep the
  summary SHORT (child-death-by-census lesson).
- Config edits ONLY in CONFIG.journal block (+ none elsewhere in CONFIG).
- Journal module ownership: journal.js owns the panel DOM; bestiary.js
  never touches document.body except via journal-provided mount.
