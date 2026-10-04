# Mixamo Animation Integration Campaign (Nicko order, 2026-10-04/05)

Source: https://www.mixamo.com/#/ — Nicko provides login; MFA code to his email.
Goal: replace our one-gait-fits-all authored clips with Mixamo's free library
(retargeted onto the shared 20-bone rig), priority = walk/run/idle variety,
then any other gaps found in the sweep.

## Nicko's pack assignments (2026-10-05, BINDING)
- Bandit (orc-male-warrior.rigged.glb, enemy.js 'bandit' type): Pro Melee Axe Pack
- Undead (undead-ghoul-male.rigged.glb, enemy.js 'ghoul' type): Not So Scary Zombie
  Pack (24 anims, Nicko-uploaded 10-05; supersedes Scary Zombie Pack which was
  bot-blocked) + Zombie_Attack.fbx single
- Player (human-hunter-male.combat-chain.glb): Pro Sword And Shield Pack (51, uploaded)
  + locomotion/idle/death singles — NOT YET ASSIGNED; wiring brief later

## Status 2026-10-05 (after Nicko hand-delivered the packs)
- All 123 FBX staged: scratch/mixamo-fbx/{axepack 47, swordpack 51, zombienotscary 24, singles 1}
- FBX inventory: FBX 7.7 (7700), 65-bone mixamorig rigs, 30fps. Bone map proven 1:1
  onto WH 20-bone rig (fingers/toes dropped, Spine1->Spine, Spine2->Chest).
- SINGLE-CLIP PROOF PASSED on bandit: constraint+bake retarget of standing idle
  (WH_Idle_Melee, 200 fcurves), old 6 clips byte-shape-identical + WH_Walk intact on
  single bake, pose render QA PASS (natural orc idle, no twist).
- Multi-clip loop bug hit (clips 2+ bake 0 fcurves; nla.bake strip-push clobbers
  original tracks; hand-strips need action_slot). Full diagnosis + hints in
  io/astrabot-brief-mixamo-retarget.md.
- ASTRABOT DISPATCHED (deleg_8b6720d5, prof astrabot) to stabilize the loop, bake
  bandit+ghoul (7 clips each), verify, QA-render, commit dev, report.
- ASTrabot LANDED (30m cap hit at the summary step; worktree truth verified): 4
  commits on dev e20d68d/1fa07f2/41935dc/7cbca33, both .mixamo.glb baked (7 clips
  each, 13/body total), pushed. verify reports pass:true both bodies; strongest
  invariant proof = BIN-chunk prefix byte-identical + append-only JSON.
- TESTERBOT (opus-5.5 via claude-code, independent) VERDICT: PARTIAL.
  A/B/D/F/G PASS with independent GLB parser re-derivation. E PARTIAL:
  WH_Hit_Large_L + WH_Attack_Horiz bandit mid-frames show torso/cape mesh collapse
  (Spine bends 47/31deg; skin weights, not keys). Also: WH_Death_Zombie (agony
  source) ends standing not dead; clip-name doc drift (WH_Hit_Reaction ->
  WH_Hit_Zombie, WH_StandUp -> WH_StandUp_Zombie); my 'full-file sha identity'
  wording wrong -> use BIN-prefix + append-only JSON. Nicko decisions 10-05:
  CLAMP-REBAKE the 2 bandit clips; zombie death LEAVE UNWIRED (rigid-fall stays).
- FIX ROUND LANDED (partially; 429 truncated it): 9d09af3 doc fixes + b599cc1
  clamp commit (25deg Spine/Chest, scope verified: 4 channels changed, 776
  identical). TESTERBOT E RE-AUDIT: FAIL (correctly).
  ESCALATION: cape slabs appear in IDLE too => orc cape skin-weight defect at
  rest pose affects ALL 8 bandit clips; clamps cannot fix. b599cc1's commit msg
  (Attack_Horiz "fixed") falsified; report retracted+corrected in c2ae186.
  STATUS: bandit Mixamo set PARKED from wiring; ghoul set READY.
- NEXT OPTIONS (Nicko decides): (a) ghoul wiring brief now (ghoul set is clean,
  Testerbotted); (b) orc cape skin-weight fix round (Astrabot, mesh edit + vision
  loop, then re-render 16 frames + re-QA); (c) jump to player sword-pack round.
  After cape fix: re-render, re-run Testerbot E, then wire bandit set.

## Current state (verified 2026-10-05, dev 30c815c)

- Canonical body: art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb
  9 clips: WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run, WH_SlashL2R,
  WH_SlashR2L, WH_Thrust, WH_Walk. 20 bones.
- 11 rigged bodies total; 10 still carry the bare 6 (no chain attacks).
- Consumers: prototype/js/anim.js (CharacterAnim: NAMES map idle/walk/run/
  attack/hit/death + MOVE_NAMES slashR2L/slashL2R/thrust), player.js + enemy.js
  both mount it; enemies without WH_Death take a procedural rigid fall.
- Roll is procedural (player.js rollTimer/rollDir), no WH_Roll clip.
- Runtime contract (binding): NO root motion (gameplay owns translation);
  clips start/end in idle/guard pose; one-shot clips end in hold pose for
  state chains; no resampling at export (preserve Mixamo fps? -> see Risks).

## Mixamo facts (to verify live)

- License: free for commercial use inside games/video; raw FBX files must not
  be redistributed as assets. We store RETARGETED GLB clips inside our repo.
- Mixamo rig: 65-bone standard humanoid, T/A-pose skeleton, root motion
  embedded in "In Place" off variants -> must select In Place checkbox (or
  strip root motion on retarget), then bake to our 20-bone topology.
- Login: Adobe ID + MFA code to Nicko's email (mfa-portal-crawl discipline:
  one continuous session, paste code fast, never resend-spam; session dies
  with the browser process -> plan ALL downloads per session).

## Pipeline (per this repo's proven pattern)

1. SCOUT (logged-in browser session): list candidate Mixamo animations per
   category with names, IDs, URLs. Bring side-by-side preview list to Nicko
   BEFORE any download-heavy work.
2. DOWNLOAD: FBX (skin=none, without-skin so only the animation), In Place.
3. RETARGET (headless Blender 4.5.4, /opt/blender-4.5.4-linux-x64):
   import FBX, constrain/bake Mixamo skeleton -> our 20-bone names
   (exact contract names), verify channel counts = bone count x 3.
4. APPEND to canonical GLB via scratch/glb_append_clips.py pattern with the
   byte-identity proof gate (base BIN sha256 prefix; every pre-existing JSON
   entry unchanged; expected clip total; numpy re-parse array_equal).
5. QA contact sheets per clip into scratch/<feature>-clips-qa/.
6. Runtime: extend anim.js NAMES map (and MOVE_NAMES if any new attack
   variants); no MOVE_NAMES collisions with state clips.
7. IO gate: Testerbot validation spec -> Devbot -> Testerbot PASS -> commit.

## Clip naming contract (new)

- Locomotion variants: WH_Walk_<name>, WH_Run_<name>, WH_Idle_<name> etc.
- CharacterAnim picks a variant per body (e.g. enemy class) or random index;
  never rename existing 9 clips (consumers depend on exact names).

## Per-body variant matrix (from code sweep)

- Player (human-hunter-male): 9 clips + variants (walk variety, sprint, idle).
- Enemies: ghoul + orc-male-warrior (walk/run variety = biggest visual win).
- NPCs: dwarf-male-smith (idle variety), elf-dawn-refuser-male, etc.
- Females (orc-female, vampire-female, human-hunter-female, dwarf-female):
  currently share male-authored gaits; Mixamo adds proper variants.

## Risks / gotchas

- Mixamo MFA session dies with browser process: download ALL candidates in
  the one session or re-login later (space days per mfa-portal-crawl).
- Root motion in FBX must be stripped or "In Place" checked.
- Bone-name mapping: Mixamo mixamorig:* vs our 20-bone names; ONE mapping
  table, verified against the real GLB, reused for every body.
- NO root motion and clean in/out (start/end in idle pose) may need Blender
  trim/cleanup after retarget.
- 30fps Mixamo source -> do not resample; carry source fps.
- License: keep a download log (name, date, category) for attribution
  hygiene; do not commit raw Mixamo FBX (store retargeted GLB only).

## Open items (fill during scout)

- [ ] Candidate list per category (Nicko picks)
- [ ] Bone mapping table verified vs canonical GLB
- [ ] FPS / timeline normalization check
- [ ] Which bodies get which variants
## Round A landed (2026-10-05): ghoul Mixamo wiring

Brief: io/astrabot-brief-ghoul-wire.md. Commits c8f0b44 (wiring), cebf636
(harness + evidence) on dev.

Wiring diffs:
- prototype/js/assets.js: ghoulBody -> races_regen/rigged/
  undead-ghoul-male.mixamo.glb (13 clips). Texture path unchanged. Rollback:
  undead-ghoul-male.rigged.glb.
- prototype/js/anim.js: `CharacterAnim(body, clips, options)`; with
  `options.variant` set, the clip names come from the static
  `CharacterAnim.VARIANTS` table. `zombie` = idle/walk/run/attack/hit ->
  WH_*_Zombie, death = WH_Death (canonical), moves = {} (no chain clips).
  Each instance keeps its own `names`/`moveNames`, and getState reports
  through them. If an override clip is missing from the GLB, that slot
  falls back to the default NAMES clip and logs a warning.
- prototype/js/enemy.js setBody: ghoul -> `{variant: 'zombie'}`, bandit ->
  default map (no change). Player unchanged.
- WH_Death_Zombie stays unwired and WH_StandUp_Zombie stays parked (Nicko's
  decisions). The bandit Mixamo set is still parked (cape defect, Round B).

Evidence: scratch/verify_ghoul_wire.py ->
scratch/ghoul-wire-evidence/ghoul-wire-evidence.json (21/21 PASS) plus
ghoul-{idle,run,attack,hit,death}.png and player-bandit-smoke.png.
Assertions passed: 13 clips; rest/walk/chase/attack/damage play the matching
WH_*_Zombie clip; death plays WH_Death (WH_Death_Zombie never active) and the
corpse settles; dropping WH_Walk_Zombie falls back to WH_Walk with a warning;
bandit uses only the legacy map; player chain clips resolve and an attack
plays WH_SlashR2L; no console errors or pageerrors (only the browser's own
favicon.ico 404).
Harness notes: entry is prototype/index.html via prototype/server.py on a
free port. Headless swiftshader runs at about 1-2 fps (same on the baseline),
so each phase waits until its sampled clip shows up instead of using a fixed
sleep. builds/v7-playable.html was not rebuilt; it was already stale before
this round (it has no combat-chain clips either).

## Round B landed (2026-10-05): orc cape-fix pipe-through + bandit wiring

Contract: io/cc-round-b-contract.md. Commits: dev 4ae54fa (rebake) + 47e397d
(wiring); feat/world-visuals 5d1a095 + bd8938d + cee616a (build). Both pushed.
8793 serves cee616a.

Pipe-through: orc-male-warrior.mixamo.glb is now baked from
scratch/mixamo-fbx/capefix/orc-male-warrior.rigged.glb, with the same 7-clip
bandit map and the 25deg clamp (Attack_Horiz/Hit_Large_L). The fixed mesh is
canonical plus 2 appended accessors (JOINTS_0 373, WEIGHTS_0 374), and only
the primitive's two attribute indices change. The append route needed no
change because it remaps by node name and never touches meshes or skins. The
canonical .rigged.glb was not modified.
- Weight-fix change: a jaw gate (|x|<0.15, in front of the Head joint). The
  shipped fix had moved ~560 jaw verts rigidly to the shoulders/Neck/Chest,
  which made a beak-stretched jaw in walk. orc-weight-fix.json was regenerated
  from the script (7367 verts changed). The old 4025 report was stale.
- verify_retarget.py --mesh-fix (37/37 PASS): checked against the ORIGINAL
  .rigged.glb. All 6 originals are byte-identical. All 7 new clips have 60
  channels, 20 nodes, dense 30fps, and quaternion norm error <5e-7.
  test_mixamo_retarget.py: 10/10 OK (bandit in mesh-fix mode plus 2 new
  negatives).

Wiring: anim.js VARIANTS.bandit = WH_Idle_Melee / WH_Walk_Melee /
WH_Run_Melee / WH_Attack_High / WH_Hit_Large_L / WH_Death (canonical), moves
{}. enemy.js passes {variant:'bandit'}. assets.js banditBody ->
orc-male-warrior.mixamo.glb; rollback is .rigged.glb. Static check:
scratch/check_bandit_wire.py (esprima parse + VARIANTS AST + clips present).
No game-loop runs.

Proof stills (Nicko decides by playing): scratch/capefix-proof/rest.png,
walk_mid.png (frame 11), attack_mid.png (WH_Attack_High frame 32).
- Rest and walk: no slabs; face normal.
- Attack mid-swing: the pre-fix forearm slab fans are gone. A residual flat
  cape/lat panel still stretches from the raised right upper arm to the hip.
  Watch for it in the bandit's overhead swing.
- Known: assets.js still expects 6 banditBody clips, so it now logs a
  13-clip warning, the same as the ghoul.

## Round C landed (2026-10-05): player sword-and-shield wiring

Contract: io/cc-round-c-contract.md. Commits: dev 75db4ee (rebake), fa4123a
(wiring), 7613a73 (build). feat/world-visuals: 534f5ef, ea24492, 81803f7
(build). Both branches are pushed, and 8793 serves 81803f7. Host check:
html 200, WH_SwordIdle x1, combat-sword.glb 200 at 5364580 B.

Deviation (on purpose): combat-chain.glb is already different on the two
branches. dev has 9 clips. feat has 13, because Order D added WH_ShieldRaise,
WH_ShieldImpact, WH_ParrySwipe and WH_GuardBreakStagger, and feat's anim.js
CLIP_NAMES uses them. So each branch's combat-sword.glb is baked from its OWN
combat-chain.glb: dev ends up with 21 clips, feat with 25. Baking feat from the
9-clip base would have removed Order D from the served build. feat assets.js
CHARACTERS.playerBody 13 -> 25. Neither combat-chain.glb changed (sha
9ca71111 dev, 48a342d0 feat).

Curation: the swordpack names are generic ("idle (2)", "turn"). There are no
"looking"/"90" labels, so scratch/swordpack_probe.py tells the variants apart
by motion. Mixamo faces -Y, and +X is the character's left. The 12 picks are in
scratch/mixamo_player.json:
- WH_SwordIdle: idle (3.7s)
- WH_SwordWalk: walk (-Y = forward)
- WH_SwordRun: run (forward)
- WH_SwordWalkBack: walk (2)
- WH_SwordIdleAlt: idle (2) (7.5s fidget)
- WH_ShieldBlockIdle: block idle
- WH_ShieldCrouchIdle: crouch block idle
- WH_SwordStrafeL / R: strafe (2) / strafe (walk speed)
- WH_SwordTurnL / R: turn (2) +99deg / turn -99deg
- WH_SwordCrouchIdle: crouch idle

Left out: attacks/slashes (the chain system owns these), jump, kick, casting,
power up, draw/sheath, death, impacts, 180 turns, and crouch-walk variants.

Bake and verify: same mixamo_retarget.py flags as bandit. The temporary
.mixamo.glb is copied to combat-sword.glb because of the script's output-name
guard. verify_retarget.py PASS: 37/37 on dev, 41/41 on feat.
- Every original clip is byte-identical (BIN prefix plus append-only JSON).
- The 12 new clips have 60 channels, 20 nodes, 30fps, and quaternion norm
  error <5e-6.
- New flags: --original-count N, and --held-pose for WH_ShieldCrouchIdle. Its
  0.007 rotation span is a genuine held pose, so its motion floor is .001
  instead of .01.
- test_mixamo_retarget.py: 11/11, adding a player-pair test that includes a
  negative case without --held-pose.

Wiring: VARIANTS.sword maps idle/walk/run to WH_SwordIdle / WH_SwordWalk /
WH_SwordRun. attack, hit and death stay canonical. moves IS MOVE_NAMES (the
same object), so the feat moveNames === MOVE_NAMES identity check still holds.
player.js passes {variant:'sword'}, and assets.js playerBody now points to
combat-sword.glb. Static check: scratch/check_player_sword_wire.py PASS on both
branches. The bandit check still passes. No game runs.

Proof stills (scratch/swordwire-proof/, 1024px):
- 01 idle f0: a guard stance, grounded. The torso is turned ~55deg because of
  the shield-side stance (hips yaw -54.5). Idle may look rotated compared with
  walk.
- 02 walk f25 (max ankle spread): a clean stride.
- 03 crouch-block f7: a deep crouch with the shield arm forward. There is no
  shield prop in the render.

Not wired yet (appended only): WalkBack, Strafe L/R, Turn L/R, the block and
crouch idles, and IdleAlt. Each one needs player-state hooks.

## Round D - Mixamo attack clips into the longsword chain (2026-10-05)

ORDERED BY: Nicko 10-05. Replaces the self-authored Blender chain-combo attack
clips with Mixamo sword-pack attacks. Skills honored: witch-hunter-playtest-
serving, no-harness-playtest-gate (no harness runs; Nicko playtests).

ADJUDICATION (blocking, done first): combat FSM phase durations are CONFIG-
FIXED, not clip-duration-derived. getAttackPhase reads this.attackMove (the
CONFIG move-def snapshot taken at startAttack) and slices elapsed into windup/
strike/recover by CONFIG seconds; seekAttack then slices the CLIP by duration
RATIO and warp-matches timeScale to the FSM clock. Mixamo timing therefore
does NOT work automatically: CONFIG was updated per move so a stage boundary
lands on each clip's measured impact frame (timeScale ~= 1, natural rhythm).

CLIP SELECTION (probes: scratch/swordpack_probe_rD/2/3/4_rD.json, committed):
- slashR2L = WH_SS_SlashR2L from "sword and shield slash.fbx" (1.500s):
  in-place, crosses right->left, impact (peak wrist speed 15.6 m/s) at 0.567s.
- slashL2R = WH_SS_SlashL2R from "sword and shield slash (3).fbx" (1.667s):
  in-place, crosses left->right deep forward, impact (11.7 m/s) at 0.800s.
- thrust-slot SUBSTITUTION = WH_SS_Overhead from "sword and shield attack
  (4).fbx" (1.000s): compact in-place overhead chop, impact (9.8 m/s) at
  0.400s. Pack has no true stab; overhead-downward reads as a distinct third
  move, substituted per Nicko's order. Documented here.
- Rejected: slash (5) crouched, slash (4) + attack (2)/(3) 360-400deg spins,
  attack.fbx overhead (3.6m travel + 44deg turn).
NEW CONFIG TIMINGS: slashR2L .57/.20/.73, slashL2R .80/.26/.61, thrust
.40/.43/.17 (windup/strike/recover; totals = clip durations).

BAKE: mixamo_retarget.py per branch, input = that branch's PRE-ROUND-D
combat-sword.glb snapshot (adapted from the contract's combat-chain input -
the script rebuilds all animation data, so chain input would have wiped Round
C's 12 sword-locomotion clips; snapshots verified byte-identical to pre-bake
HEAD). Output = the new combat-sword.glb: dev 24 clips, feat 27 clips.
verify_retarget.py: 40/40 dev, 44/44 feat (re-run by IO independently, zero
fails). All 21/25 prior clips byte-identical (incl. authored chain clips kept
for one-line rollback). test_mixamo_retarget.py 11/11 both branches.

WIRING: MOVE_NAMES values rewired to WH_SS_* (VARIANTS.sword.moves keeps the
SAME object -> feat identity check intact); MOVE_FALLBACK_NAMES keeps the
authored names as a per-slot fallback with console.warn (degraded mis-slice
but playable); playerAttack/seekAttack unchanged; player.js untouched.

AUDIT (Testerbot opus, 3 passes - full FAIL->fix cycle):
1. First audit: FAIL check 2 ONLY. Real catch: the chain-open window counts
   seconds into RECOVER (player.js: stage==='recover' && ph.t >=
   chainOpenSec), and strikes are longer with the new clips, so a strike-phase
   press could expire (old buffer 0.35 < worst 0.52). Checks 1/3/4/5/6 PASS.
2. Fix 1 (a5a2445/0a14ab8): inputBufferSec 0.35 -> 0.55. Re-audit: FAIL one
   last case - thrust is the LAST move, so a press during its strike must
   survive 0.43+0.17=0.60s to restart the chain.
3. Fix 2 (8f1d46e/a02ab8a): inputBufferSec 0.55 -> 0.65 = 0.60 + one capped
   20fps frame. Re-audit: PASS CHECK 2 -> Round D fully PASS. Both branches
   verified fast-forward.

LANDED (pushed by IO after PASS):
- dev: 4391181 (bake) 8da1aa1 (wiring) a5a2445 8f1d46e (buffer fixes)
- feat/world-visuals: 9491894 9491894 d45401e f3d8300 (build) 0a14ab8 a02ab8a
- Serving: HOST /tmp/wh-worldfeat-clean reset --hard a02ab8a; host curl
  http://localhost:8793/prototype/builds/v7-playable.html = 200, 2658047
  bytes (byte-exact vs worktree build), WH_SS_SlashR2L marker 1,
  inputBufferSec: 0.65 marker 1, old windup 0.14 marker 0.

PROOF STILLS (scratch/roundD-proof/, 1024px, vision-reviewed once each):
- 01-rest.png: clean guard idle, grounded, no clip.
- 02-ss-slashr2l-mid.png t=0.567 and 03-ss-overhead-mid.png t=0.400: the arm
  is raised wide at strike-START (still = first strike frame); the cross-body
  sweep happens later INSIDE the strike windows. consumeAttackSweep applies
  damage across the whole strike stage, so hit registration is unaffected;
  impact-frame alignment is about swing FEEL only. Render artifacts noted:
  cloak clipping through arm/leg, shoulder pinch at raised arm, slight ankle
  distortion at the planted foot.

ROLLBACK: flip MOVE_NAMES values back to WH_SlashR2L/WH_SlashL2R/WH_Thrust
(one line in anim.js) + restore old CONFIG timings/inputBufferSec. Authored
clips remain live in the GLB.

WATCH-ITEMS for playtest: swing cross-body vs impact-frame feel; render
artifacts above; L2R chain cadence vs old rhythm (0.80s windup is much
slower than the old 0.14); the 0.65 input buffer may feel slightly floaty
on chain restarts.

STILL PARKED (unchanged): 9 unhooked baked clips (WalkBack/Strafe L/R/Turn
L/R/idles), bandit cape panel, ~55deg idle stance, kick/cast/draw/sheath
hooks, dev's stale prototype/builds/v7-playable.html (harmless - dev is
served from the checkout).

## Round D2 - lantern light fix (2026-10-05, same session, Nicko order)

Nicko: lanterns are lit but do not illuminate the ground beneath them, and the
light sits outside the lantern object. Root causes (measured):
1. Socket placement had no lateral offset - the pool light sat on the prop's
   center column while both lantern heads hang off-axis (post glass at
   glTF-local x -0.27..-0.09 @ 64-79% H; waymarker glass z +0.23..+0.47 @
   55-79% H). scratch/lantern_head_probe.py (committed) measures vertex bands;
   IO's coarse band centroids were corrected by Claude Code's finer 3%
   slices after its contract render put the light on the bracket.
2. Socket intensities 1.6/1.8/2.4 at decay 2 gave ~0.06-0.6 ground pool vs
   the player torch (10.5). Raised to torch parity: post 9.0, waymarker 9.5,
   campfire 3.2.
Changes: CONFIG.lightSockets gains measured offset [x, z] (glTF-local,
pre-rotY, pre-scale; post 0.72/[-0.18,0], waymarker 0.67/[0,+0.35], campfire
centered) + game.js socket placement applies offset with the THREE
obj.rotation.y convention (rotY sign matches region-manager placement; the
feat waymarker's rotY 1.1 makes rotation live) and prop scale.
Deviations (accepted, verified by IO): finer glass slices replaced the
contract's band centroids; rotation-sign correction; dev's copy of the
placement lives in computeSockets (dev/feat divergence, same edit).
Proof stills: scratch/roundD2-proof/ (3, feat) - flame inside post head,
inside waymarker cage, centered campfire; warm ground pools under all three.
Commits: dev 5dea2fc, feat d1d2e0a + build 96e7010 (bundle 2658945 bytes).
light.js lock-light 'world' radius unchanged (intensity-independent).
Parked: shadowless-pool look (game lights never castShadow), pre-existing
aliasing/base-gap asset artifacts visible in stills.

## Round E - world vegetation pass (2026-10-05, Nicko order, same session)

Five Meshy assets (wh-bush-a/b, wh-grass-tuft, wh-tree-birch-young,
wh-tree-dead-young; 117cr of 130 cap incl 9 t2i refs and 1 destroyed
first-mesh reroll on bush-a, caught by ortho QA). Instanced scatter layer
in region-manager.js: seeded deterministic placement (pure function of
CONFIG, mulberry32), extra trees only in empty areas (32 candidate-slot
fill, 14 in A / 10 in B, trunk colliders registered), bush rings [2,4]
around EVERY tree base at [1.1,1.6]x trunk radius (no collision - Nicko
order), free bushes 20 + grass 220 per region (no collision), all
undergrowth via 3 InstancedMeshes per region (~+1.0M tris A, +0.56M B,
3 extra draw calls). Cemetery yard keepOut for trees/bushes; clearances
4m enemies / 2.5m gather / path / spawn / gates. Enemies ignore scatter
trees (enemy.js off-limits this round) - same as all existing props.
Deviation watch-items for playtest: bushes small vs 15-18m trees (knobs:
CONFIG.scatter.bushes.assets heights, atTreeRing.radiusFrac); grass 1
tuft/60sqm reads sparse (knob: grass count); stills at
scratch/roundE-proof/. Wall + lantern-doorway pass = NEXT round (Round F),
scoped separately, not started.
## Round F - boundary wall ring + gate arch (2026-10-05, Nicko order)

Three Meshy assets (54 of 60 credits; 1309 -> 1255): wh-wall-vinestone-a/b
(2.0m vine-on-stone modular segments) + wh-lantern-hang (hanging lantern,
amber emissive glass). Provenance io/roundF-wall-provenance.md; QA
scratch/treeqa/roundF/. The arch reuses b3-gate: its two door leaves stand
nearly closed in the original mesh (13% clear opening - brief's 65% was
wrong), so scratch/gate_open_cut.py derived b3-gate-open-pixelated.glb
(34.28% opening measured); original untouched.

Placement (whWallPlan in region-manager.js, pure seeded function of
CONFIG.boundaryWall, seed 20261006; mirror scratch/wall_mirror.py,
byte-identical across runs AND branches): 145-segment ring at r 87.5
(0 nudged, 0 dropped; closest prop the r-84.8 witchwood cleared 1.32m) +
22 chord segments per side along z=-25 from x=+-4 to the ring intercept.
2 InstancedMeshes (A 95, B 94) = 2 draw calls; built once at world level,
region switches never dispose it.

Gate: b3Gate at (0,-25) scaled so the opening is exactly 5.20m (s 9.223,
Z-squashed 0.45 -> 4.3m deep, apex 6.8m). whLanternHang hangs inside the
apex (hook 5cm into the stone; 0.9m body - brief's 0.6 was a speck at that
height). Light socket CONFIG.lightSockets.b3Gate (intensity 5.0, apex-based)
feeds pool + flame card via a 3-line game.js hook (dev) and computeFireSockets
(feat: also lock-light eligible).

Colliders: 603 = 567 wall circles (3/segment, r .45, max neighbor gap 0.43m
< 1.4m player diameter) + 32 arch-leg circles (r .6) + 4 corner plugs
(r .5). Joined per region by plane side (A 431, B 350).

Watch items: wall draws ~802k tris (Meshy returned 4.1-4.4k vs 2k target -
decimate if mobile fps drops); modular seam between segments is visible
closeup (stone courses don't align - foliage overlap is the fix if it
bothers); Round E proof stills had half-sunk ground objects (renderer
bug, fixed in F's); bundle's three.js static{} parse warning predates
this round, game code parses.