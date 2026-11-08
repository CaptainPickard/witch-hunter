# CC-C13b · CLAUDE CODE IMPLEMENTATION BRIEF - Old King's Forest dressing + wolf-legs live diagnosis

You own IMPLEMENTATION of the area-dressing build-out. The Astrabot lane
(CC-C13a, parallel) DESIGN+GENERATES assets - it delivers GLBs + PNGs +
MANIFEST-DRAFT.md under art-direction, UNTRACKED. Your job: (1) wire the
CURRENTLY SHIPPED assets per the plan below, (2) implement the wolf-legs
live-diagnosis instrumentation handoff, (3) leave CC-C13a's new meshes for a
follow-up wiring round once IO accepts them.

Work on the worktree /tmp/wh-worldfeat (branch feat/world-visuals). LAWS:
- Commit NOTHING. Leave all edits UNTRACKED for IO review (IO is the sole
  git gatekeeper).
- NO harness / NO headless-browser smoke runs. No playwright. No chromium.
- Node --check every touched JS file. Rebuild the bundle with
  python3 tools/build_v8.py at the end (report the byte count).
- Playtest-era copy law: never the word "free"; no hardcoded agent names.

## TASK 1 - FENCE/GATE NORMALIZATION (ships now, existing assets)
Nicko 10-20: "replace the random upscale wood fence and random gates of
different sizes". The 11 offender rows use picketFence at scales 1.29-1.67
and ironFenceSection 1.33-1.36 + cemeteryGate 1.53/1.71:
- CONFIG.js regionA props L201-207 (5 picket + 2 iron) and regionB props
  L433-436 (2 cemeteryGate + 2 picket).
- RE-NORMALIZE every row of the same asset to ONE scale (the row's design
  scale: picketFence -> 1.40, ironFenceSection -> 1.35, cemeteryGate -> 1.62)
  and re-seat them as a coherent line (same rotY per straight run; keep
  existing colliders working by keeping the same x/z - only rotY/scale
  normalize). The farm/ranch fence KIT swap waits for CC-C13a assets.
- Constraint: do not move any row > 2 m (colliders + placement clearances
  were probed); ask IO via the report if a row looks wrong.

## TASK 2 - STONE-RUIN DRESSING (ships now, existing assets)
Region C wants "more stone ruins like structures". Using EXISTING manifest
assets only (mossBoulder scale rows, stoneCrossTilted, gravestoneObelisk,
churchArchway, churchCornerButtress, buriedCoffin, rubblePile, stoneSteps):
- Add a SMALL RUIN CLUSTER near the denTrail's mid-point (approx (-95,-208),
  8-14 m off the trail, clear of every prop >= 6 m and the wall rows) and a
  second cluster near the spawn glade's west (approx (-30,-140), same rules).
- 3-5 rows each (arch/corner/boulder/steps/rubble mixes), rotY varied,
  road/trail centerline >= 4 m + halfWidths.
- PROBE YOUR ROWS offline in plain node (no three): distance check vs every
  existing prop row in regionC's props + scatter tree rows (the same probe
  pattern scratch/cc-c6/camp_probe.js used) - report the min gaps.

## TASK 3 - WOLF-LEGS LIVE DIAGNOSIS HANDOFF (ships now)
wolf-debug.js (CC-C12, shipped commit df4996f) already exposes a ?whdbg=1
chip reading window.WH_GAME regionManager enemies: fsm/spd/clip/timeScale/
weights(WH_Wolf_Walk)/weights(WH_Wolf_Idle)/locomotion. Extend it:
- add W(Hit)/W(Death) + mixer.timeScale + mixer's top 2 weighted actions,
- add enemy.setBody stand-in detection: if the wolf body's mesh name contains
  'standin', print STAND-IN IN PLAY (the streaming late-swap corner),
- add e.rigidAnim truth + a 'CLIPS=n' count from WH_ASSETS.getClips of the
  wolf body name (0 clips = the late-swap/stand-in bug smoking gun),
- keep it inert unless ?whdbg=1 (probe URLSearchParams, no style.css edits -
  inline styles only).
- DO NOT change any game logic in this task. Diagnostics only.

## TASK 4 - INVENTORY + REPORT (no code)
- List every edit + reason, node --check outputs, bundle bytes.
- Report the wolf debug chip's new readout shape so Nicko knows what to
  read back to IO.

OUT OF SCOPE (do NOT touch): wolf CONFIG row (C10 done), camp sleep gate
(C11 done), the roads block (C12 done), regionD, cooking.js, camp.js,
enemy.js. Any new-GLB wiring (farm/ruins/trees from C13a) = follow-up round.

CC-C13a reference: io/missions/2026-10-20-cc-c13a-astrabot-farm-assets.md