# CC-B1 buildsummary — ruined chapel landmark, region B (wake 34, 2026-11-07)

DISCLOSED DEVIATION (HUSK LAW, 2 child deaths): Devbot child #1 stalled+froze
(deleg_2d233e37, max_iterations early without completing), continuation child
#2 died (deleg_25ea3eb0, max_iterations + provider stall). IO executed the
build inline per the primary rule "2 deaths = IO builds inline with disclosed
deviation". Validation = the Testerbot-authored valspec cc-b1-chapel-valspec.md
(W-T trimesh table) executed via scratch/cc-b1_probe.cjs (authored by child #1
on the valspec, amended inline per the V-WAKE34 amendments block; amendment
authorship disclosed in both files).

## Landed
- prototype/js/assets.js: 7 manifest rows (churchWallWindow, churchWindowFrame,
  churchRoofBeam, churchAltar, churchPulpit, churchPew, candelabra), all
  -pixelated.glb paths, exact files verified on disk + git-tracked.
- prototype/js/CONFIG.js lightSockets: ONE new key `candelabra` hf 4.69
  intensity 5.5 (IO amendment: computeFireSockets rides ground level —
  h = groundHeight*scale*hf = 0.891*4.69 ≈ 4.18 m = altar-top stack seat
  3.415 + 0.76 flame; row y NOT read by the socket path).
- prototype/js/CONFIG.js regionB props CC-B1 block: 14 rows (K1 2x west wall
  window x -18 @ z -63/-58 with >2.5 m gap; K2 free-standing SW buttress
  (-11.8,-52); K3 2x north wall window @ z -66 with gap; K4 pulpit (5,-63),
  pew DROPPED — no legal seat (probe + audit); K5 altar (14.5,-58) + candelabra
  stack y 3.415 (measured groundMinY seating; no-probe fallback was 2.1, the
  measured value wins per R3); K6 gable windowFrame ABOVE altar y 2.15
  noCollide (moonbeam-above-altar, scene-01 anchor); K7 2x raised roof beams
  (noCollide, y 4.0/3.9); K8 fallen rafter FINAL (7,-69) rotY 2.5 ground
  debris, keeps collider; K9 2x rubble (−13.5,−59.5 / −6.4,−64)).
- prototype/js/CONFIG.js scatter.keepOut: darkwood_edge ellipse rx 21 rz 12.5
  @ (0,-58) (AMENDED from rx 17 rz 10 — west wall + K2 inside).
- ALL locked existing rows untouched (archway, NW buttress, pewBroken,
  campfire, waymarker, stumps, boulders, logs, trees).
- scratch/cc-b1_probe.cjs: mirror-table probe, amendments A1-A6 applied
  (raised-row ground-check exemption, stack exemption, A5 stump exemption,
  R5 comment-tolerant regex + m flag, R6 rx 21/rz 12.5, R3 walkable-floor
  re-scope, K-seat final seats, R4 look-back window 14).

## Probe verdict (final run)
PASS exit 0: 14 chapel rows clear R1 lanes (BCdoor/ABchoke/nodes/enemies/
campfire/waymarker), R2 mutual (worst NEW-vs-existing edge gap 0.93 m vs
floor 0.8), R3 raised discipline (exactly 3 noCollide rows), R4 single new
socket + warm-family comment, R5 manifest 7/7 exact paths, R6 every ground
row inside the keepOut ellipse, R7 tri ledger 11,998 faces at scale 1
(landmark budget ≤ 30k; ~12k consumed by the landmark ≈ headroom 18k).

 Seats as final (x,z): K1a (-18,-63) K1b (-18,-58) K2 (-11.8,-52)
 K3a (-3.5,-66) K3b (3.5,-66) K4 pulpit (5,-63) K5 altar (14.5,-58)
 candelabra (14.5,-58,y3.415) K6 windowFrame (14.5,-58,y2.15,raised)
 K7a beam (-6,-58,y4.0) K7b beam (-2,-58,y3.9) K8 rafter (7,-69)
 K9a rubble (-13.5,-59.5) K9b rubble (-6.4,-64)

## Rejected seats (for the record)
- Pew at (5.5,-62): archway edge 0.72 < 0.8; no other pew seat passed the
  stump/node/archway web → pew dropped, pewBroken + camp stand in.
- Buttress at (-13.5,-54.5): bonePile node ring 2.87 < 3.
- West wall at x -17.5 line: node rings (graveMoss/bonePile) + reachTreeC.
- Rafter (-9,-55): campfire 0.37 / bandit 0.80; (18,-49.5): yewTree+
  mossBoulder rings → final (7,-69).
- Gable at floor: pewBroken + altar collisions → raised y 2.15.

## Build
python3 tools/build_v8.py → prototype/builds/v8-playable.html 3,577,418 bytes,
CC-B1 marker grep 4 hits, deterministic stamp (HEAD author time).
