# CC-AF1 — CAMP AFFINITY v1 (docs 12 + 11 + 44/45) — IO SPEC + BUILD CARD

Branch/worktree: /tmp/wh-worldfeat (feat/world-visuals). Build tool: tools/build_v8.py
(newest; deterministic-stamp law). NO-GIT: children NEVER commit or push. No harness
runs, no headless browser smoke tests. Nicko's playtest is the acceptance bar for
playability; Testerbot validates CODE with probes.

## Framing (art law)
Anchors: art-direction/concepts/camp-good-affinity.png, camp-dark-affinity.png,
camp-neutral-affinity.png (viewed this wake). Palette law extracted:
- good fire = pale gold / white-gold (camp-good: "bright gold or pale yellow",
  brazier gold trim),
- dark fire = ember-crimson / blood-crimson (camp-dark: crimson pools),
- neutral = keep the standing pool amber (0xffc27a), camp-neutral cold-teal is NOT
  adopted for the fire (that is lantern color, not fire; the fire stays amber).
The SYSTEM this round: doc 12's single visible good<->evil axis (locked; tier names
from the A proposal + the 2026-09-14 ruling pass thresholds) landing on the
prototype as a DEED-DRIVEN standing score, a CHARACTER-tab STANDING readout, the
player's kit camp fire tinting with the standing tier, and journal lines from the
camp folk on tier crossing (QJR-3 topic pattern). Doc 12 "axis on the inventory
screen" (doc 11 Moral Reputation Axis RESOLVED) is the design mandate; thresholds
are the ruling-pass working values (PROPOSED, Nicko tunes).

## Scope (additive-only; ZERO deletions anywhere)
1. NEW prototype/js/affinity.js
2. CONFIG.js: new window.WH_CONFIG.affinity block + journal.topics +2 rows
3. index.html: +1 script tag (affinity.js after leveling.js)
4. game.js: +1 guarded kill-deed line in storeCorpseLoot; +guarded color forward in
   computeFireSockets; +affinity capture/restore lines in setupSaveHooks
5. wareffort.js: +1 guarded deed line at the fill-success site
6. npc.js: +1 guarded deed line in tryRescue
7. camp.js: fireProps() rows carry the tier color (guarded)
8. inventory.js: STANDING section in renderLeveling (guarded add)
9. style.css: small additive block for the standing bar (EOF append)

## A — CONFIG.affinity block (exact shape; Devbot types it verbatim)
```js
window.WH_CONFIG.affinity = {
  // doc 12 ruling pass working values (PROPOSED, Nicko tunes): |s| >= 80 sworn,
  // >= 50 honored/feared, else neutral. tier() = first row (desc) with minScore <= s.
  ladder: [
    { id: 'sworn-dark',  minScore: -80, label: 'Sworn of the Dark', fire: 0xff2a2a },
    { id: 'feared',      minScore: -50, label: 'Feared', fire: 0xff5a3c },
    { id: 'neutral',     minScore: -49, label: 'Neutral', fire: null },
    { id: 'honored',     minScore: 50,  label: 'Honored', fire: 0xffdf8a },
    { id: 'sworn-light', minScore: 80,  label: 'Sworn of the Dawn', fire: 0xfff2c8 }
  ],
  // deeds: event id -> delta. Kill ids mirror CONFIG.leveling.xpSources keys;
  // every re-armed kill pays again (the XP law). rescue/warEffortFill repeat by
  // their own event semantics (rescue is once by quest state; the fill is per day).
  deeds: {
    rescue_findDaughter: 25,   // witnessed good deed: the daughter home
    warEffortFill: 10,          // the garrison is the light war's belly
    kill_ghoul: 4,              // blight cleansing
    kill_rotmother: 4,
    kill_rotspawn: 2,
    kill_wolf: 0,               // wildlife; row explicit so the map is total
    kill_bandit: -4,            // moor men of the underworld kin; unwarranted blood
    kill_coven: 8               // the hunter's trade against the covens
  },
  clamp: 100,                   // score hard clamp [-100, +100] (PROPOSED)
  campTint: { enabled: true },   // kit fires only; ambient world fires stay amber
  text: {
    secTitle: 'STANDING',
    scoreFmt: '{score} standing',
    barNeutral: '#8a8577'       // v1 bar fill follows tier via cls, see C-UI
  }
};
```
## A — CONFIG.journal.topics +2 (camp folk voices, verbatim rows; APPEND ONLY)
```js
campAffinityGood: {
  id: 'camp-affinity-good',
  title: 'The honored fire',
  body: "The camp folk tend my fire a little brighter - word of good deeds travels
ahead of me. The garrison claps shoulders on my way through; the moors keep their
distance.",
  source: 'Camp folk'
},
campAffinityDark: {
  id: 'camp-affinity-dark',
  title: 'The watched fire',
  body: "The camp folk keep to their tents now. My fire burns low and red, and the
shadows between the wagons watch me back. Word of my deeds travels too - the wrong
kind.",
  source: 'Camp folk'
}
```
(Single-line strings; no newlines inside the JS litterals.)

## B — js/affinity.js (new module; expose window.WH_AFF)
IIFE like leveling.js (pure state, no DOM beyond journal calls; no imports beyond
WH_CONFIG / WH_JOURNAL guarded). API:
- score() -> current integer score (0 on fresh)
- tier() -> the ladder row per the desc-scan above (neutral row fire = null)
- tierFire() -> hex or null (null = caller falls back to the pool default)
- deed(id, times) -> adds deeds[id] * (times|1) clamped to +-clamp; unknown id or
  delta 0 = no-op returning false; returns true and fires _crossCheck() on change.
- crossed(tierId) -> true/false (once-map, save-ridden)
- capture() -> { score: n, crossed: plainObject }; restore(data|null|undefined) ->
  replaces state exactly (missing = 0 / {}); never throws on garbage rows.
- onChange: null hook (game.js / inventory wiring sets it; fired after a real
  change INCLUDING a tier change).
- Crossing check (_crossCheck): on entering honored (score >= 50) the FIRST time,
  append journal topic campAffinityGood via WH_JOURNAL (guarded, QJR-3 call shape:
  append(id, title, body, undefined, source)); on entering feared (score <= -50)
  the FIRST time, append campAffinityDark. Sworn tiers add NO extra topic in v1
  (the once-map keys are 'camp-affinity-good' / 'camp-affinity-dark', so a later
  sworn crossing does not refire the topic; the crossing MAP records nothing
  extra). The once-map persists in the save (campAffinityGood/dark keys) and
  NEVER resets on its own — the courts remember.

## C — Integration sites (each guarded, existing patterns, no behavior change when WH_AFF is absent)
1. index.html: `<script src="js/affinity.js"></script>` immediately AFTER leveling.js.
2. game.js storeCorpseLoot (one line, after the awardXP/discover pair):
   `if (window.WH_AFF) window.WH_AFF.deed('kill_' + enemy.type);`
3. wareffort.js fill-success site (right after the JT.firstFill append,
   ~line 218): `if (window.WH_AFF) window.WH_AFF.deed('warEffortFill');`
4. npc.js tryRescue (right after the JT.rescue append):
   `if (window.WH_AFF) window.WH_AFF.deed('rescue_findDaughter');`
5. game.js computeFireSockets: inside the props loop, the socket object gains its
   color ONLY when the prop row carries one:
   `if (p.color !== undefined) s.color = p.color;` (s = the socket being pushed).
   poolTick already honors tgt.color (CC-C7 pattern) — the pool tick is NOT edited.
6. camp.js Camp.prototype.fireProps: when the affinity block is live
   (`window.WH_AFF && window.WH_AFF.tierFire()`), every returned row gains
   `color: <tierFire>`; when null / module absent, rows stay exactly as today.
   Scope = kit fireRows only (fireProps already returns only kit sites). The 21
   ambient banditCampfire CONFIG props are NOT touched - other people's fires.
7. game.js setupSaveHooks: capture adds `affinity: window.WH_AFF ? WH_AFF.capture()
   : undefined`; restore calls `window.WH_AFF && WH_AFF.restore(data.affinity);`
   (leveling-restore pattern; undefined = fresh 0).
8. inventory.js renderLeveling: a STANDING section (guarded on WH_AFF) rendered at
   the BOTTOM of the col (after SKILLS): the tier label + the signed score (scoreFmt),
   plus a small standing bar whose fill class mirrors the tier
   (`aff-bar fill-neutral / fill-honored / fill-feared / fill-sworn-light /
   fill-sworn-dark`). WH_AFF.onChange -> the same re-render the leveling column
   already uses (wire in game.js where WH_LEVEL.onChange is set; guarded single call,
   affinity may be absent).

## D — style.css (EOF append)
```css
/* CC-AF1 standing (doc 12 axis): the CHARACTER tab STANDING block */
.aff-bar { ... one row of the lvl-bar pattern ... }
.aff-fill.fill-neutral      { background:#8a8577; }
.aff-fill.fill-honored      { background:#e3b64f; }
.aff-fill.fill-feared       { background:#b0472f; }
.aff-fill.fill-sworn-light  { background:#efe3ad; }
.aff-fill.fill-sworn-dark   { background:#8f1f1f; }
```
(Exact selectors/margins Devbot follows from the neighboring .lvl-* rows; keep it
small.)

## Acceptance criteria (Testerbot verifiable)
- A1: js/affinity.js exists as specified (API surface exact; no DOM besides guarded
  WH_JOURNAL appends); CONFIG.affinity row set + topic ids match this spec exactly.
- A2: deed() math: +25 rescue once, +10 per fill, kill deltas per map; clamp at
  +-100 both directions; unknown/zero ids no-op (probe each).
- A3: tier() exactness: 49->neutral(null fire), 50->honored, 80->sworn-light,
  -50->feared, -80->sworn-dark, -49->neutral, 0->neutral (probe table).
- A4: hooks present and guarded (no crash if WH_AFF deleted); sites exactly as C1-C8.
- A5: fireProps color only on kit rows and only when live; tierFire null -> no color
  key; ambient CONFIG fires untouched (grep counts unchanged for banditCampfire rows).
- A6: socket color forward present; poolTick untouched (diff shows no edit there).
- A7: capture/restore ride: capture carries {score, crossed}; restore(undefined) = 0/{};
  death->LOAD replaces exactly (no dupes).
- A8: STANDING section renders; class switch per tier; renders no row when WH_AFF absent.
- A9: journal crossing appends exactly once per tier per lifetime of the save; no
  refire across save/load; appends carry day stamp via the journal core.
- A10: build_v8 run by Devbot inside the worktree: exit 0; marker grep on
  prototype/builds/v8-playable.html for 'WH_CONFIG.affinity', 'WH_AFF',
  'camp-affinity-good', 'Sworn of the Dawn'; index.html diff = +1 script line;
  overall diff has ZERO deletion lines (git diff --stat / -U0 check).
- A11: NO commits or pushes by any child (IO only).

## Out of scope (explicit)
Sworn-tier behavior (favors, faction dialogue, paladin hunts), war-effort standing
gates, doc 11 pose/emote unlocks, the Allegiance Gambit (denial counters), NG+ tilt.
V1 = the axis ledger + reading + the two crossing journal lines + the kit fire tint.

## Report
Devbot: summary + file list + build exit/marker lines. Testerbot: PASS/FAIL verdict
with evidence; save under io/reports/ per convention and say nothing to Nicko.
