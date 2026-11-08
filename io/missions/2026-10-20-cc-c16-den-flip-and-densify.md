# CC-C16 · Den cave-mouth flip + map densification (4 camps, 4 wolf packs)

## 1. RULINGS (Nicko, 2026-10-20)
- "turn it so that the entrance is facing the center of the map, and bury the
  back right up against the mountain/side of the map wall, so it feels like a
  cave-like entrance on the side of a hill."
- "fill out the whole of the map with more enemies, i want 4 more bandit
  camps and 4 more wolf packs scattered about the area."

## 2. CC-C16a DEN FLIP (geometry law)
- Outcrop centre stays at r 238, bearing 225 = (-168.3, -197.7).
- mouth U' = unit(outcrop -> MAP CENTRE (0, -366)) = (+0.707, -0.707) (SE,
  toward the Stone / the ring road). FACE = atan2(U'.x, U'.z) = +2.36 rad.
- den centre = OC - U' * 24.7 = (-185.8, -180.2) = cw(263, 225) - the cave
  body sits BEHIND the mouth, at r 263 = INSIDE the rim-mountain band
  (ridge foot 240): the cave reads as dug into the hillside. Region D is a
  standalone pocket (its own disc + hidden build), so a r 34 disc at r 263
  is legal; C is hidden while D is active.
- All shipped C15 outcrop/den rows rotate by dROT = FACE_new - FACE_shipped
  = 2.36 - (-0.79) = ~3.15 rad (180 deg) about the outcrop centre; stains
  re-aimed (trail steps from the map interior toward the mouth).
- Door: interactAt / lands / lair / mouth plane recomputed from U'.
- C-side approach: the ring road SW arc (r 34 around the Stone) -> SW cross-
  country to the outcrop (~240 m, inside the playable rim).

## 3. CC-C16b SQUAD SITES (generator-gated)
- 4 bandit camps at r 130-190, bearings ~30/150/260/330 (each = the CC-C6
  pattern: cook-fire prop + cooking.stations row (kind campfire, night-only
  atmospheric per CC-C6C - the STARTING fire stays the only tutorial cook
  fire; new camp fires are atmospheric like Alpha/Bravo/Charlie) + 2 bedrolls
  + stump + rubble + 3-4 bandit guards with packless patrol offsets).
- 4 wolf packs, loops r 170-220, bearings ~10/100/190/285, 8 waypoints each,
  4 members + phases 0-3 (CC-C5 pattern).
- probe gates (offline, mulberry32 seeded): every camp >= 60 m from every
  other camp/fire, >= 96 m from every wolf loop, >= 47 m from road
  centrelines, >= 30 m from props/trees, out of the arrival glade (r 60 of
  spawn) + Stone (r 60 of 0,-366) + the den approach corridor (bearing 225
  band), slope <= 8.8 deg, r <= 240 (rim foot). Wolf loops additionally
  >= 60 m from other loops, >= 96 m from every camp.
- TRI budget: +4 camps ~ 2k-10k each (stump/rubble/bedroll/fire) + no new
  body GLBs -> verify total C <= 2M with the ledger probe after paste.

## 4. SCOPE
TOUCH: CONFIG.js (regionD orient rows, regionC.enemies +16 wolves,
wolfPacks +4, cooking.stations +4 fires, regionC.props +4 camp dressing
blocks), scratch/cc-c16/(gen_squad.py + probes), bundle rebuild.
NO: engine js files (enemy.js pack machinery + camp dressing readers are
data-driven already), C13b/C15 landed rows.

## 5. ACCEPTANCE
- node --check + bundle rebuilt + marker greps.
- gen_squad probe: ALL CLEAR printed (no violations).
- ledger probe: C worst-case circle <= 2,000,000.
- commit + push + 8793 flip + serve verify (a72c51c -> new sha).