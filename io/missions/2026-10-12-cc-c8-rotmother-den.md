# CC-C8: THE ROT MOTHER'S DEN — BLACK DOORWAY CAVERN INSTANCE (change order, R-62.9)

Rulings (Nicko, 2026-10-12): E-to-enter at the mouth; boulder-outcrop "mountain"
NE of the lair glade; small rot trail outside (nest/boss/light INSIDE);
torch-light vs her sickly-green glow (true black elsewhere); persistent den
(the 3-day re-arm + cleared flag carry over).

## THE SHAPE (one sentence)
A rock outcrop ~15 m tall rises NE of the lair glade; a black doorway (moss +
bramble twigs, m1-gate-based) opens in its face; E at the mouth crossfades the
player into the DEN — a separate dark region (regionD) whose cavern holds the
nest, the Rot Mother, and her spawn; the fight happens in the dark, lit only
by torch/firebolt and her nest's faint green.

## 1. THE OUTCROP (region C, NE of the lair glade)
- Position: lair C-local (-175, +95) = world (-175, -271); outcrop CENTER
  C-local (-136, +147) = world (-136, -219) (~65 m NE of the glade center,
  off the direct wolf-patrol line, min 20 m from nearest giant trunk row).
- Build (existing kit only; NO new GLBs): 7 mossBoulder (scale 1.4-2.2)
  in a horseshoe against a core of 5 ring-wall segments (whWallA/B, the C2
  ring tech: per-segment colliders r 0.45, x3 each), footprint ~30 x 24 m,
  tallest ~15 m (3 stacked segment rows, scale 2). Seat every piece on
  WH_GROUND.heightAt (propFootR 1.2, the standard seat).
- The DOORWAY faces SW (toward the glade): m1 gate pair flanking (scale 5.2,
  opening ~4.6 m), 6 bramble (1.4-2.4) + 4 egg sacs (graveMound scale 1.1,
  rot-paint tone) clustered AT the mouth, 1 mossBoulder (1.6) as the lintel
  mass. Bramble + stain = the blackened face.
- Rot stain (the trail): a SECOND rot ground pool (same CC-C7 pool params,
  radius 5, darker) at the mouth plus a 3-blob stain trail (radius 1.8/1.4/1.0)
  stepping from the glade edge toward the doorway. No light outside anymore.
- Slope guard: boulder colliders + a keepOut scatter row (rx 22 rz 18) keep
  random trunks/bushes out of the outcrop's face.

## 2. ENTER RULE (E-to-enter, no pause, no menu)
- Interact family: same promptFor/interact pipeline as notch examine rows.
  Prompt appears within 3.5 m of the doorway center: "E - Enter the den".
  Pressing E: the door crossing fires (below), plus a 0.8 s crossfade:
  black overlay dip (existing deathFade overlay element, non-lethal variant),
  a single wooden-breath audio cue is OUT of scope v1 (no audio pipeline yet).
- No E requirement to EXIT: the den's exit mouth is a walk-back plane
  (crossing out is instant, same fade).

## 3. THE DEN = regionD (new smallest region; reuses the C2 region tech)
- CONFIG.regionD: { id: 'rot_den', name: "The Rot Mother's Den",
  center: world (-175, -271) - BUT the den is a SEPARATE 2D pocket: its own
  disc radius 34 (own ground canvas, pool texture), NOT coplanar in C: the
  region-defs connection C->D is a DOOR-type connection (the only existing
  door pattern) with planeCoord = a line OUTSIDE both discs' overlap: the
  door window is the ONLY place the plane exists (insideChokepoint semantics
  unchanged). Player world pos maps across exactly like B/C.
- Den interior build (all existing kit, seated on its own flat ground):
  cavern = 10 whWall ring segments (radius ~24, scale 2.4, heightM 9) +
  9 mossBoulder (1.6-2.4) shoulder mass + ceiling read: the sky shows
  regionD's DARK pano (see 4) and the ring's top edge reads as rock against
  it; 4 stone-steps (crypt kit) + 2 skull-piles + 3 egg sacs (graveMound)
  + 6 blightcap mushrooms (m14, manifest row needed - one assets.js row,
  same-class as b6Bones' addition in C7) scattered as the brood furniture.
- The NEST center: local (0, +6) from the den center: the rot POOL (radius
  10, the CC-C7 pool params, color2 shifted sicker) + the green LIGHT
  (intensity 2.4 -> 1.6, height 1.2) MOVE INSIDE + 5 egg sacs ring + the
  Rot Mother's spawn anchor = exactly the current lair module, re-homed.
- Exit mouth: the doorway ring break at local (0, -24) facing the entry:
  a 4.6 m gap in the wall ring (the ring builder's open-arch pattern),
  bramble-framed, stepping back out = the C-side crossing.
- Colliders: ring segments per-segment circles (existing tech) + boulders.
  The den is CLOSED except the mouth: no other exits.

## 4. DARKNESS (the fight in the dark)
- regionD ambientLightLevel: 0.06 (C is 0.5; the night floor is ~0.4 feel).
- regionD fog: color 0x05070a, density 0.12 (d95 ~ 24 m: the far wall is a
  black thought) - set on applyRegionLighting via the new region row.
- SKY: regionD sky-variant = the underlay (near-black dome, stars 0.15,
  disc 0.2 opacity) - daynight's SkyPool already supports per-area panos;
  regionD registers an 'always-dark' phase constant (no clock): hemi fill
  0.06, moon 0, exposure 0.75. The dome never shows a sun/moon cycle inside.
- LIGHT SOURCES INSIDE: the player's torch (both hands possible), firebolt
  in-flight glow + impact, and the nest light (sickly green 0x7fbf4f).
  The Rot Mother + rot spawns are UNLIT by any region light: their pixelated
  textures read only in the player's light radius - silhouette-first.
- Her nest light DIES with her death (the lair module already owns it);
  re-arm relights it. While cleared-and-not-rearmed: the den is a black
  empty vault (the exit mouth is the only geometry visible).

## 5. PERSISTENCE + THE MOVED LAIR
- The CC-C7 lair module (spawner 7 s / cap 3 / 6 m ring, re-arm 3-day /
  14 m proximity / rotmother_cleared_flag, dieOnMasterDeath, loot roll)
  moves to regionD homeRegionId 'rot_den' VERBATIM: homeRegionId and the
  lair world coords are the only changes; the save block shape is unchanged
  (still rotmother_cleared_<region> = dayOfDeath).
- The rot spawn spawner anchor + nest furniture + egg sacs + the green light
  all live INSIDE regionD now.
- Outside (region C): the regionC.enemies rotmother ROW IS REMOVED
  (the boss is instanced by her lair record inside the den, not a C row);
  the rot trail pool + stain + doorway props replace the open lair dressing.
  The regionC.rotLair prop block DELETES the old pool/light/fog (they moved);
  it GAINS the outcrop + doorway + stain rows.
- Save compat: a pre-C8 profile (cleared flag + per-index dead state) still
  loads: the lair record re-homes deterministically; her dead state rides
  the den's enemy roster (fresh region, fresh list, flag decides armed or
  not, same as v1 logic).

## 6. CONFIG SURFACE (the full row list to touch)
- CONFIG.regionD (new): id/name/center/groundRadius 34/groundY/groundColor/
  seeds/fog/ambient/sky pool row/lighting row/enemies []/props [den build]/
  lairs [the CC-C7 lair row, homeRegionId 'rot_den'].
- CONFIG.regionC: rotLair block re-shaped (outcrop + doorway + trail; the
  pool/light/fog rows DELETE), regionC.enemies: the rotmother row REMOVED,
  keepOut gains the outcrop scatter row.
- CONFIG.dayNight: regionD phase constant (always-dark row) + fog.fog entry.
- CONFIG.lighting: nothing (the region row's own values are read directly).
- region-defs.js: regions.regionD registered (side -1, own disc), ONE new
  connection C<->D door-type (plane between the discs, door window only).
- game.js: applyRegionLighting reads regionD (null-guard the hemi/moon
  branch), the E-to-enter interact hook (prompt + cross trigger + the
  crossfade reuse), dayNight.setSkyArea handles regionD's constant phase.
- enemy.js: lair module homeRegionId + coords only; no new combat logic.
- assets.js: +blightcap manifest row (one line, same class as C7's b6Bones).
- FORBIDDEN (unchanged): save.js semantics, player.js movement/camera,
  data flow, docs, art-direction, style.css, index.html, camp/cooking/daynight
  internals (daynight gains ONE always-dark branch read, no clock changes).

## 7. TRIS LEDGER
- Outcrop: 5 wall segs (~1,200) + 8 boulders (~8k) + gate pair (~4k) +
  brambles (~3k) + egg sacs (~1.5k) ~= 18k tris
- Den: 10 segs (~2,400) + 9 boulders (~9k) + furniture (~6k) + nest pool +
  egg sacs ~= 18k tris
- Region budget C: current lair dressing (~2k: pool + fog + light) replaced
  by ~20k (outcrop + trail) = +18k. Total addition ~= +36k (1.8% of C's
  ~2M ledger). All existing culled by the same prop-cull path.

## 8. VALIDATION SPEC (Testerbot, before builder starts)
a. CONFIG.regionD exists (id rot_den, radius 34, ambient 0.06, fog 0x05070a/
   0.12); connection C<->D registered door-type; regionC rotmother row GONE;
   rotLair gains outcrop/doorway/trail and LOSES pool/light/fog.
b. Den build rows: 10 ring segs + 9 boulders + furniture + nest pool r 10 +
   light 1.6 + exit gap at the ring; all seated rows carry the standard seat.
c. Lair: homeRegionId == 'rot_den', nest local (0, +6) == world (-175, -265);
   spawner/re-arm/flag/loot params byte-equal to the C7 values.
d. E-to-enter: prompt within 3.5 m of the doorway; E triggers cross + 0.8 s
   fade; exit walk-back crossing exists; no pause/menu anywhere.
e. Darkness: regionD registers an always-dark phase (moon 0, hemi 0.06,
   exposure 0.75), sky underlay shows stars 0.15; her + spawns carry NO
   region light; nest light dies on her death, relights on re-arm.
f. Save: rotmother_cleared flag + per-index den roster round-trip; pre-C8
   profile loads with the nest armed (default) or cleared (flag honored).
g. SCOPE: diff touches ONLY CONFIG.js, region-defs.js, region-manager.js
   (if the connection needs a builder hook), assets.js, enemy.js, game.js,
   bundle html, io/missions docs, scratch tools. FORBIDDEN: save.js,
   player.js, camp.js, cooking.js, style.css, index.html, docs/planning.
h. node --check on every edited js; bundle rebuilt; tris ledger delta
   reported (target <= 40k new tris); no harness, no browser, no game run.
i. (Runtime, watch-items only): fade timings, doorway sightline into the den,
   torch radius vs the 24 m cavern, her 4.2 m body vs the cavern scale,
   wolf/bandit approaches unaffected outside.

## 9. EXECUTOR NOTES (Astrabot)
- The ring/wall + door-plane tech is PROVEN (C2 ring, B/C door); the den is
  a re-dress, not new tech. The ONE genuinely new mechanic is the E-to-enter
  doorway interact -> door crossing + fade: build it as a notch-examine-style
  interact hook that CALLS the tickTransition cross (or an explicit
  forceCross helper added to region-manager logic + a thin game.js bind).
- The always-dark region phase: one constant row daynight reads when
  areaId === 'rot_den' (no clock math); keep the dormant-clock law intact.
- Do not fight the heightfield: the den is flat (groundY) - the terrain row
  (terrain.enabled) is for C only; D uses the flat disc path (heightAt 0),
  which is the A/B path (proven).
- Estimated 2 dispatch turns of CONFIG data + 3 of JS wiring + build/bundle.