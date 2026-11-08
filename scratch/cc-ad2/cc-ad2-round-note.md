# CC-AD2 ROUND NOTE (IO, 2026-11-06, Autopilot wake)

Lane: doc 47 Veil strata V2 — THE ERASED GALLERIES, chained off the landed
crypt (regionE, The Old Throne's Crypt, center (0,-596) r 20).

Design work this wake (pre-spec, design-only):

## 1. The walk (playtest-visible)

The crypt's ALBETAR plinth gains ONE prop sibling: a collapsed processional
gap in the crypt's WEST ring wall (two extra ring segments pulled / one wall
row deleted), with a kneeling statue pair (mourningStatue + rubblePile) at
the opening — the tomb's west aisle. E there (CFG hook world (-14.5, -596),
radius 3.5) dips to black and crosses E -> F: THE ERASED GALLERIES.

Walk-back: the galleries' mouth plane at z = -640, ONLY from the galleries
side (walkFrom F), identical to the crypt's law.

## 2. What the player finds in F (doc 47 strata V2 theme)

- Own flat disc r 26 center (0, -640) (F lives under the west rim band of
  C's rim ring; same "beneath the floor" fiction as the crypt; one-active-
  region law held: C and E hidden while F is active).
- Basalt ring (8 whWallA/B rows on chord-circle r 22, 7 colliders each,
  gap window AT the z = -640 plane, x 0 +- 2.2 — the tomb-mouth lane).
- Fog/fill: fogColor 0x0a0810, fogDensity 0.145 (d95 12.0 m — tighter than
  the crypt's 0.13; the galleries are "the far wall is a black thought"
  plus one step quieter), ambientLightLevel 0.055, ground 0x121418 /
  0x171a20, groundSeed FRESH (1662061329) so the floor's blotch pattern
  differs from the crypt's.
- Enemies: 2 GHOULS (doc 34 undead grammar zone-denial walkers, "undead
  wardens of the galleries"). The crypt's coven casters need no re-pose;
  ghouls close and hold — erasure pressure on foot.
- Dressing (doc 47 V2: "galleries where names once stood and do not
  anymore", doc 19's erased statue field underground sibling):
  mourningStatue (the ONE featureless plinth figure — the erased statue),
  2 skullPile, 2 blightcap, 2 mossBoulder, rubblePile — all clearance-law
  rows, PROPOSED.

## 3. Art anchor (PRIMARY art law)

APPROVED anchor used: concepts/concept-08-veil-spire.png + day-08-veil-spire.png
(the erased statue field is V2's SURFACE sibling — same headless plinth
statues, blood-on-ash accent law) + concept-05-night-ambush.png (fog tiers
1/2/3 for interior depth). Palette carried into F rows: obsidian/ash greys,
bruised-purple shadows, ONE crimson accent = blightcap caps (same rule as
the crypt).

NEW interior frame (this probe's plan): concept-11-veil-galleries.png
(portrait establishing shot) — BLOCKED this wake: io profile image_gen pins
provider openai-codex + model gpt-image-2-high; Codex auth.json holds only
an expired (2026-07-17) ChatGPT-plan OAuth token and no API key, so the API
400s ("gpt-5.5 model is not supported when using Codex with a ChatGPT
account"). Config change to the io profile is outside cron scope. Opened as
an open thread; the build round references the 4 APPROVED anchors instead.

## 4. Probe result (pre-spec law)

scratch/cc-ad2/solve_geometry.py — 3 of 6 constraint groups verified live
against regionE's LANDED numbers (E dressing clearances from the proposed
west-aperture hook at (-14.5,-596): nearest dressing 4.5 m, ring 6.3 m,
covens 10.4/19.9 m, inside crypt r 18; and F-center/ring separation from E
ring: exactly 4.0 m). The remaining 3 groups (F shell, ring gap, enemies/
props) are the SPEC's rows to fill and the Devbot probe re-run's job once
the CONFIG rows exist.
