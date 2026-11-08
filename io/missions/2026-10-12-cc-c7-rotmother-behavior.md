# CC-C7 ROT MOTHER + ROT SPAWN — BEHAVIOR DELTA (asset lane complete, this doc = wiring spec)

Status: ASSETS SHIPPED (feat/world-visuals @ 50c0038). This round wires them.
Executor: Astrabot (Claude Code dispatch). IO validates after via Testerbot.

## Assets (consume EXACTLY these)
- Boss: art-direction/3d/assets/races/rotmother-pixelated.glb
  (17,573 tris, bbox x 0.967 / y-depth 1.9 / z-height 0.908 in glTF space;
  treat Y-up standard; ground = min-y of bbox).
- Minion: art-direction/3d/assets/races/rotspawn-pixelated.glb (2,094 tris).
- Raw-texture twins exist (rotmother.glb / rotspawn.glb) — do NOT use in game.
- No rigs. V1 placeholder = the bandit 6-clip retarget pattern (idle/walk/
  attack/hit/death + 1 spare), scale-approximated; real rig round LATER.

## 1. Nest lair (region C local coords)
- Site: L3 clearing at (-175, +95) C-local (doc 62 §5.2).
- Flatten + rot-ground pool radius 12 (same material family as the C5/C6
  ground pools; dark swamp tone), 5-8 bone/rib props from the existing
  asset set scattered (no new assets).
- Ambient: slow green fog particles + dim rot-light (reuse bandit-campfire
  light pipeline, green tint, always-on).

## 2. CONFIG.enemy rows (data.js)
rotmother: {
  name: 'Rot Mother', hp: 460, dmg: 26, speed: 1.6, aggro: 9,
  lair: {x: -175, y: 95, region: 'C'}, scale: 2.2,
  pattern: 'boss-slam', slamCooldown: 3.4, slamWindup: 1.15,
  poison: {dps: 3.5, duration: 4.0, slow: 0.45},   # poison-lite v1
  rearm: {days: 3, trigger: 'proximity', radius: 14},
  loot: [{mat: 'rot-silk', n: [2, 4]}, {mat: 'rot-gland', n: [1, 2]}],
  minions: {asset: 'rotspawn', cap: 3, interval: 7.0, range: 6.0,
            dieOnMasterDeath: true},
}
rotspawn: {
  name: 'Rot Spawn', hp: 26, dmg: 5, speed: 2.4, aggro: 14, scale: 0.8,
  pattern: 'chase-melee', loot: [{mat: 'rot-silk', n: [0, 1]}],
}
- Materials rot-silk + rot-gland: register in the mat registry + drop-log
  (gross-but-tragic descriptors).

## 3. Boss combat (enemy.js / combat pattern module)
- Heavy slams: windup 1.15s (telegraph = body lean + ground shadow cue),
  impact = AoE 3.2 radius 180-deg front arc, knockback + poison-lite apply
  (damage + slow ONLY — no DOT stacking rules in v1).
- Between slams: slow lumber chase (speed 1.6).
- Damage intake: same as bandit pipeline (no new resistances in v1).
- Death: all live Rot Spawns die with her (dieOnMasterDeath).

## 4. Minion spawner
- While mother alive + player within lair radius: spawn 1 Rot Spawn / 7s
  from 6m around her, cap 3 alive.
- Spawn behavior: chase-melee, tiny lunge, dies on her death.

## 5. 3-day re-arm
- On her death: lair marked cleared (save flag rotmother_cleared_<region>).
- In-game day counter +3 -> lair re-arms (she respawns) IF the player is
  within 14m of the lair (proximity trigger); otherwise re-arms on first
  entry after day-3.
- Loot re-rolls per re-arm.

## 6. Placeholder clip set (v1)
- Reuse the bandit 6-clip retarget pattern: idle / walk / slam(attack) /
  hit / death + spare. Rot Spawn: idle / walk / attack / death.
- Clip scale: mother 1.0 (slow feel comes from pattern timing), spawn 1.3.

## 7. Validation spec (Testerbot)
- CONFIG rows present + schema-consistent (save/load round-trip).
- Slam AoE hits player only in front arc; poison slow applies + expires.
- Minion cap enforced (never > 3 alive); all die on mother death.
- 3-day re-arm triggers exactly once per cycle; loot re-rolls.
- Perf: lair scene loads = no dropped frames vs baseline (asset 17.5k tris
  x1 + 3x 2k).
- No edits outside data.js / enemy.js / the clip wiring file / game.js
  registration + the lair scatter JSON.