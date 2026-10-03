# World R7 asset session — 2026-10-01 (IO direct; art pipeline, not a devbot round)

## Scope executed
Doc 61 section 6 batch plan, second Meshy credit window, unblocked by
Nicko's key rotation (new key stored env/file-only; old exposed key
superseded, never hardcoded again since 395c5d8) + top-up to 3000
credits. Grimdark discipline: every prompt parented on
refs/darkwood-concept.jpeg, art-bible palette law (one accent per
frame; cyan=magic, amber=human fire, red=disease/danger), thumbnail-
standard vision QA before commit, v3 pixelation (512px NEAREST +
5-bit posterize, normals injected/verified byte-level) before ship.

## Batches landed (all on feat/world-visuals, pushed, remote-verified)
- B1 biome retry (doc 59 ordered): M10 bramble, M19 moss drape,
  M20 mud puddle, M21 gnarled roots — commit 71dae10 — 60cr QA 4/4.
- B6 scatter kit: bones / leaf litter / pebbles / headstone fragments /
  mushrooms — 72752ef; bracken v1 FAIL (shattered shards) -> retry ref
  r2 (connected fronds, QA PASS) -> mesh r2 PASS -> commit e8cf53a set.
  90cr total.
- B2 harvest+encounter: moonbell, grave-moss, hemlock, blightcap,
  bandit campfire (builtin LIGHT SOCKET), bedroll, coven witch totem,
  glade mote shrine (EMISSIVE-ready) — a91fa94/e8cf53a/6288a03 —
  moonbell v1 FAIL (floating droplets detached the bell) -> retry ref
  r2 QA PASS -> mesh PASS. 135cr total.
- B3 landmarks: ruined spire (skyline hero), mausoleum gate
  (Region A chokepoint asset the region system lacked), gallows,
  lantern waymarker (LIGHT SOCKET), rest shelter (P1-10 camp anchor),
  standing-stone SINGLE (retired the failed fused-ring mesh; the ring
  is instanced at runtime 4-6x per stone) — 0810e49/695efbd/9a178f5 —
  105cr.
- B-tex (0 credits): 6 particle sprites (ember/mote/firefly retry 1/
  ash/fog puff/leaf, 128px trimmed RGB-on-black for additive) + 4
  skyline alpha layers (keep ruin / ridge watchtower / dead treeline /
  monolith field, 2048w, mask QA 4/4) — 5df916b/4294bef/801eeaa.

## QA/unship record
33 items processed; 3 hard FAILs caught pre-commit (bracken v1,
moonbell v1, stones ring fused) and resolved via the doc 59 one-retry
rule (2) or redesign+unship (1: ring -> runtime instancing). Numeric
atlas scans clean (0 saturated strays, no white holes).

## Credits
390 of 3000 spent this window (all first-try SUCCEEDED except the
three QA-retried conversions; no 400 credit loss). PARKED: B4 camp
decor 240cr + B5 gear 90cr — both gated on the rest-space round (P1-10)
landing AND Nicko's session-window ruling (700/session standing cap).

## Provider quirk (documented in doc 59 for all future batches)
Back-to-back spaced submits (65-70s apart) return empty-body HTTP 400
after a burst window; a single cold attempt succeeds with an identical
payload. Standing rule: serial submit -> settle -> submit. Zero credits
lost to 400s.

## Handoff to code rounds
Runtime wire-in of everything above rides the world rounds R2-R6
(R2 lighting rig incl. lantern + 4-socket pool; R3 pixelation + decals;
R4 pixelated bodies; R5 collision; R6 region lifetime) — driven by the
hourly finisher cron (2c7556f7f609) once the blender-anim session
lands dev. Branch discipline: world commits go feat/world-visuals only;
dev checkout belongs to the anim session until it lands.

— IO, 2026-10-01 05:40Z