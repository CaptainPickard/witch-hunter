# 37-B - Cross-Document Consistency Audit (2026-09-13)

Scope: doc 37 read in full. Locked planning references checked by targeted sections. Existing files are read-only. Findings distinguish incompatible rules from missing integration contracts. A newer explicit exception is not automatically a contradiction.

## B1 - MEDIUM unexplored: Capture is a new defeat branch, not a death-penalty reversal

- Doc 37, Session rulings 7 and Part 3c, "The trigger (RULING 7, locked): monsters hold grudges as factions" (lines 42-49, 438-459): capture is explicitly NON-DEATH, strips recoverable gear, and loses no currency or XP.
- Doc 04, "Decisions (locked with Nicko)" (lines 8-9, 13-17): XP/currency drops ON DEATH, with tavern/warp-camp respawn. Doc 35, G15, "Core run-back rule" (lines 215-232): death drops unspent currency plus 25 percent of current-level XP; gear stays untouched; a new death replaces the old corpse.
- These rules can coexist because capture does not kill the player. The unresolved contract is dispatch: capture must bypass death, corpse replacement, insurance consumption, and anchor respawn. Death during escape must still run G15. Doc 35 G13, "Save triggers" and "Save data model" (lines 123-145), do not define saving the capture, hoard, or escape state. Doc 37 also attributes the 25 percent number to doc 04, although G15 owns it.
- Resolution: Add an explicit non-death capture branch with atomic capture/hoard persistence, preserve any prior corpse and insurance, and retain G15 for actual deaths.

## B2 - LOW polish: Ruling 11 preserves the regional cap but abbreviates the crossing rule

- Doc 37, Session ruling 11 and Part 5, "Session rulings", ruling 11 (lines 62-64, 715-718): better rarity within the fixed regional tier band is called compliance with doc 06's crossing rule; "Faction keys" repeats that no key crosses the band (lines 825-830).
- Doc 06, "LOOT ECONOMY", "2. Rarity-vs-Tier distribution (the crossing rule)" (lines 119-132): "LOW-TIER GEAR SPANS ALL RARITIES; HIGH-TIER GEAR LIVES ONLY AT HIGH RARITY"; T1-T2 Common through Named, T3 mostly Uncommon/Rare with some Named, T4 Rare/Named only, T5 Named only and story-attached. The same section separately fixes each region's tier band.
- No direct contradiction: increasing rarity inside a band can obey both constraints. The cap alone is not the entire crossing rule and does not specify the allowed rarity distribution at each tier.
- Resolution: Cite and enforce both the regional tier cap and doc 06's tier-to-rarity matrix for every stratum and key overlay.

## B3 - MEDIUM unexplored: Procedural named-item odds lack the authored-relic boundary

- Doc 37, Part 5, "Session rulings", ruling 11; "The gate rule"; and "Open Questions", item 23 (lines 715-718, 747-749, 1022-1023): escalating strata improve named-item odds, Gate III opens named-item chance, and deep-boss guaranteed named drops remain open.
- Doc 06, "LOOT ECONOMY", "2. Rarity-vs-Tier distribution" and "4. Hunter's Relics (named items)" (lines 122-126, 155-163): Named T2 stories exist, but Hunter's Relics are all T5, hand-authored, "never random drops", fixed to an acquisition story, and never duplicated.
- Doc 06 already blurs Named rarity and the relic subtype. Doc 37 does not identify which it rolls. Randomly rewarding a T5 Hunter's Relic in a starter-region stratum would violate both the authored source and regional cap; rolling ordinary Named-band content need not.
- Resolution: Distinguish Named rarity from Hunter's Relics and exclude relics from procedural odds except explicitly authored, unique acquisition sites in eligible bands.

## B4 - MEDIUM unexplored: Faction keys conflate moral affinity, faction standing, and allegiance

- Doc 37, Session rulings 13-14 and Part 5, "Faction keys" / "Key tiers" (lines 67-88, 819-824, 840-860, 890-906): keys use axis-compatible sales; neutral purchases are described as the neutral player's advantage; all families progress friendly/honored/sworn under "doc 12's tier ladder".
- Doc 12, "Neutral Path" (lines 54-59): neutrals may trade with light cities but cannot align. "The Neutral Court" (lines 158-168): accepts ANY affinity. "IO Proposals", A and "Open Questions", 1 (lines 170-174, 193-195): the axis ladder is explicitly a proposal, not a locked vendor ladder.
- Doc 06, "LOOT ECONOMY", "3. Vendor economy" (lines 134-153): specific holy/dark goods are axis-gated; neutral brokers sell to anyone; neutral standing lowers prices and deepens stock.
- Excluding deep-evil buyers from Guild service is consistent with doc 12, "Design Consequences", 4 (lines 71-75). Neutral keys are not locked to neutral morality by the cited rules. A neutral-only sale interpretation, or requiring moral allegiance for neutral T3 stock, would conflict. Fenced Coven Keys are a new bypass, not an established doc 12 rule.
- Resolution: Specify moral access, faction-stock standing, and allegiance as separate predicates; keep neutral vendors open to every affinity and explicitly rule on fenced-key use.

## B5 - MEDIUM unexplored: Permanent dungeon wounds lack a save and rest boundary

- Doc 37, Session ruling 15 and Part 5, "The Cleared-Wound Rule and the Situation system", 15A (lines 89-102, 920-929): destroyed rooms, bridges, and boss corpses persist; the dungeon does not respawn its old self but gets new tenants. "What I would add", "THE LAYER BOSS RULE" and "SCAVENGER SPOILS" (lines 987-995) nevertheless retain doc 35's inhabitant respawn economy.
- Doc 35, G13, "Save triggers" (lines 128-136): the locked dungeon-clear delta writes ONLY at the dungeon EXIT trigger. "Save data model" / "Checkpoint grammar consistent with doc 09" (lines 138-153, proposed): kills since the last save, including bosses, revert on reload; rest respawns dungeon inhabitants except bosses.
- Doc 37 does not say whether permanent destruction starts immediately or after a committed exit, nor whether rest restores old tenants before long-timer recolonization. Its unconditional wording can contradict the exit-only lock if interpreted as immediate durable clearing. The detailed rest model is proposed, not a second locked ruling.
- Resolution: Define destruction commit timing and rest versus recolonization precedence, preserving exit-only dungeon-clear writes unless Nicko explicitly supersedes them.

## B6 - LOW polish: Parked ghost corpses must not become extra recovery corpses

- Doc 37, Part 5, "PARKED WORKING IDEAS" (lines 955-958): previous corpses as permanent set pieces and dead-speaking one's own old corpse are explicitly NOT baked.
- Doc 35, G15, "Core run-back rule" and "Edge cases" (lines 223-232, 242-243): only the newest player recovery corpse survives; previous drops are permanently lost; player corpse loot is separate from NPC grave goods and has no light-reputation cost.
- No current contradiction because the ghost idea is parked. Implementation would conflict if old set pieces retained recoverable player drops or recreated them through dead-speech.
- Resolution: If adopted, define ghosts as non-loot memory actors separate from the single G15 corpse and specify their interaction with the digging reputation rule.

## B7 - MEDIUM unexplored: Vendetta succession needs a ruler predicate, not just an heirless noble

- Doc 37, Part 3, "The loop", "THE VENDETTA GRAVE", and Part 4, catalog 25 (lines 207-227, 682-689): a target may be "a person of importance, a noble without an heir"; its death feeds regicide and can trigger the hold's "Sundering and capture"; "only the world's cascade is not optional".
- Doc 13, "Trigger Anatomy", 1 (lines 25-27): succession concerns "the hold's ruler (king, lord, matriarch)" or "main noble". "Open Questions", 6 (lines 116-117), gives the exact resolved condition: "cascade only with no suitable heirs". "Trigger Anatomy" (lines 37-40) opens an INVASION WINDOW in which defense is still possible.
- Heirless ruler assassination is consistent with that rule. Killing any heirless minor noble is not sufficient. "No heir" also omits the distinct case of existing but unsuitable heirs. Doc 13 does not name a Sundering conquest state or guarantee immediate capture.
- Resolution: Require death of the current ruler and no suitable successor, then dispatch doc 13's invasion window rather than unconditional ownership change.

## B8 - MEDIUM unexplored: Timer-rerolled CONTESTED lacks an authoritative war-state guard

- Doc 37, Session ruling 15B and Part 5, "The Cleared-Wound Rule and the Situation system" (lines 95-99, 931-947): every dungeon's situation is "re-rolled on long timers"; CONTESTED is "two powers inside, the tier-3 key state" and determines occupants, quests, and usable keys. Part 5, "Key tiers", "TIER RULES" (lines 903-910), instead seeds tier-3 availability from war state.
- Doc 13, "Core Principle" (lines 7-18) and "Trigger Anatomy" (lines 23-40): conquest is triggered by world conditions and goes through INVASION WINDOW. Doc 20, "The World Ledger" (lines 26-44): one authoritative state owns war momentum and hold ownership; "QUESTS ARE REACTIONS, NOT ROLLS" and "quest logic of its own does not exist".
- As written, a timer can independently create the same faction-war state the key system requires the ledger to authorize. CONTESTED is not doc 13's named hold state. A local random situation is compatible only if constrained by ledger predicates and kept distinct from hold ownership, which the current rule does not specify.
- Resolution: Reroll only ledger-eligible local situations, derive faction-war eligibility from war state, and prohibit situation rolls or key purchases from directly flipping holds.

## B9 - MEDIUM unexplored: Level keys gate access but do not inherently scale combat power

- Doc 37, Part 5, "Session rulings", 10 and "The gate rule" (lines 710-714, 724-752): doors read character level 10/20/30/40; lockpicking can bypass them; the opened layer matches the player's level.
- Doc 07, "Two-Layer Model", Layer 1 (lines 33-43): level grants stat points and "does NOT directly scale combat power"; the number is a point budget, not a damage stat. Doc 04, "Decisions" (lines 4-7), fixes regional difficulty and allows entry into endgame regions without region tier gating. Doc 34, "6. Spawn Table", closing rule (lines 234-235), forbids player-level-scaled tables.
- A fixed-content door threshold is not a damage multiplier and does not by itself violate doc 07. It does introduce a new use for the point-budget number. "The gate opens on the layer matching your level" is ambiguous between selecting fixed strata and scaling one persistent stratum to its visitor. The latter would violate fixed difficulty; the former need not. Region access and dungeon-depth access are different scopes.
- Resolution: Specify immutable per-stratum encounter tables and use level only as an access check, with no visitor-level scaling or relocking of unlocked strata.

## B10 - MEDIUM unexplored: Spine immunity already answers the Vendetta target question

- Doc 37, opening scope (lines 8-9), Part 3, "The loop", "THE VENDETTA GRAVE" (lines 207-227), and "Open Questions", 9 (lines 1066-1069): tissue-only generation can select an important noble, while the explicit question asks whether a bound dead's killer may be a spine NPC and notes that immunity says NO.
- Doc 20, "The Two-Tier Quest Architecture" (lines 10-24) and "Progression Safety Rules", "SPINE IMMUNITY" (lines 188-192): procedural systems write only tissue; no procedural event may kill, displace, or de-spawn a spine NPC; thrones, Signer, sect founders, and Hidden Court elders are off-limits to conquest consequences.
- This is an acknowledged missing guard, not permission to violate the spine. A bound dead cannot name a spine NPC as the actionable assassination target of this generated frame. The lock does not prohibit every lore mention of a spine NPC, but any such authored testimony must not generate a kill objective or a destructive cascade.
- Resolution: Filter targets and all cascade victims against spine immunity, close open 9 as already answered, and reserve spine-related testimony for authored non-destructive hooks.

## B11 - HIGH contradiction: Slice grave-digging introduces a revenant outside the locked roster

- Doc 37, "Slice scoping", IN SLICE (lines 1029-1034): Quiet Parish digging includes "keeper risk and revenant wake risk"; proposed proof archetypes include THE NIGHT HAUNTER (lines 1035-1037), whose catalog entry uses a ghost or wight (Part 4, item 9, lines 616-619).
- Doc 34, "5. Slice-1 Bestiary", sections 5.1-5.4 and "7. Open Items for Nicko", 1 and 3 (lines 123-203, 239-245): locked roster is Bandit, Rot Wolf, Grave Ghoul, and Rot-Mother. "6. Spawn Table" (lines 214-218) wakes Grave Ghouls from disturbed graves, not revenants.
- The explicit revenant wake adds an enemy outside the locked roster unless revenant is merely an alias for Grave Ghoul, which neither document states. The ghost/wight archetype is only proposed but would widen the same conflict if accepted unchanged.
- Resolution: Use the existing disturbed Grave Ghoul for slice digging, defer ghost/wight content, and require an explicit roster change for a separate revenant.

## B12 - MEDIUM unexplored: Doc 37's quest slice and doc 31's combat slice are different deliverables

- Doc 37, "Slice scoping" (lines 1025-1041): includes rumor tiers, bounties, grave digging, multiple quest archetypes, and an end-to-end World Ledger loop.
- Doc 31, "1. Slice Definition" and "IN / OUT" (lines 15-21, 42-46, 56-68): "not a quest demo"; quests, factions, moral axis, World Ledger, procedural interiors, and stealth are explicitly deferred; tavern service is a door stub.
- These scope lists cannot describe the same build. Important provenance: doc 31's status (lines 3-13) still marks the general scope and numbers PROPOSED; only the engine and Rot-Mother inclusion are explicitly locked there. The mismatch is real, but the entire combat-only scope must not be falsely reported as a Nicko lock.
- Resolution: Name doc 37's proof as a later quest slice, or obtain an explicit scope supersession with the added dependencies and acceptance tests.

## B13 - MEDIUM unexplored: Warren goblins require a later bestiary, not expansion by citation

- Doc 37, Part 3c, "The trigger" and "The four endings" (lines 438-459, 545-573): adds goblin kidnappers, a king, rival warrens, and persistent monster-faction grievances. Part 5, "The gate rule" (lines 744-746), says "doc 34's bestiary widens". "Slice scoping" (lines 1025-1041) does not explicitly allocate the Warren, gates, or situations to a milestone.
- Doc 34, title, "5. Slice-1 Bestiary", and "7. Open Items", 1 (lines 1, 114-117, 239-241): owns the slice roster only, not a comprehensive full-game monster list. Goblins are absent from the locked Bandit/Rot Wolf/Grave Ghoul/Rot-Mother set.
- A full-concept goblin society does not contradict a slice-only roster. Treating this chain or Gate II as authorization to add goblins to slice 1 would. New faction perception, kidnapping, dialogue, and feud behavior have no allocated implementation scope here.
- Resolution: Mark the Warren and expanded strata explicitly post-slice, and give the full-game goblin society its own bestiary and faction-behavior specification.

## B14 - MEDIUM unexplored: Warden floor claims need a non-conquest boundary

- Doc 37, Part 5, "Faction keys", WARDEN KEY and CLAIM RULE (lines 795-802, 831-836): excavation keys deepen faction presence and retain claims until another key is used; the text calls this "the conquest system's smallest unit" and "taking a floor". "Key tiers", Warden T3 (lines 854-860), puts Warden holdouts in a three-way fight.
- Doc 19, "THE RELIQUARY WARDENS" (lines 138-151): the Wardens are "a tiny, non-conquering faction" of neutral archivists with donation, recovery, authentication, and ruin-key functions. Doc 13, "Reconquest and the Living Nobility" (lines 53-68), ties territorial conquest to political ownership and land grants.
- Defending an excavation is consistent with non-conquest. Treating every Warden key as political acquisition is not. The shared claim rule currently makes no distinction between archaeological access and territorial ownership.
- Resolution: Give Warden keys non-sovereign excavation licenses and defensive presence, with no conquest ownership, land grants, or hold momentum effect.

## B15 - MEDIUM unexplored: Procedural deep rewards need the spine-only endgame-power exclusion

- Doc 37, Part 5, "The Deep Table" and "Key tiers" (lines 773-786, 878-883): procedural deep layers host Dark Pacts content, late-game blight content, and "one-time pact opportunities"; "The gate rule" (lines 730-752) gates descent through level or lockpicking.
- Doc 21, "PROGRESSION-SAFETY ADDENDUM for the spine" (lines 119-130): "Spine chains are the only content that may hard-gate ENDGAME POWER"; apex access is affinity-keyed and cannot require completionist tissue play. Doc 20, "The Two-Tier Quest Architecture" (lines 17-24), makes every tissue quest disposable.
- The new deep rewards are not explicitly apex powers, so this is not a demonstrated contradiction. Their relationship to apex chains is unspecified. An exclusive apex unlock behind an optional generated deep or faction-clear prerequisite would violate the spine rule.
- Resolution: Exclude apex and mandatory ending unlocks from procedural deep reward tables; authored spine hooks may use these sites without making tissue completion a prerequisite.

## Checked alignments and source coverage

- Doc 37 was read in full, including rulings 14-15, the ninth-pass replayability section, slice scoping, and all listed open questions. Each comparison source was searched and its relevant sections read.
- Grave reputation is consistent: doc 37 Session ruling 3 and Part 3, "CONSENT TEXTURE" (lines 22-24, 236-242) retain doc 06, "Decisions", GRAVE-LOOTING (lines 9-11). Warden sanction or consent does not waive light-reputation loss.
- Frame library is consistent: doc 37 Part 4 count and template list (lines 691-694) reproduce doc 21, "Frame Library First Pass" (lines 115-117). Eight templates do not cap the number of archetypes. Doc 37's 26 archetypes are not 26 new frame templates. Doc 20, "The Quest Frame Grammar" and "Expiry: Fails-Forward" (lines 46-93), support consequence tags, multiple endings, and restless-grave follow-ups. The broken refusal sentence in doc 37 (lines 222-224) is editorial, not a conflicting cross-document rule.
- Necro-aristocracy is consistent: doc 37 Part 3c, "The trial" (lines 461-471), explicitly uses doc 22's bureaucracy as an analogy; Part 4, GRAVE-GOODS RETRIEVAL (lines 661-664), extends the legal texture. Doc 22, "THE UNDEAD LINE: THE NECRO-ARRANGEMENT" (lines 84-124) and "THE WORLD BEFORE THE FALL", UNDEAD (lines 240-244), describe contractual dead houses. Goblin toll debt is not asserted to be the cosmic debt or an undead transformation.
- Undersovran and debt: doc 19, "THE DEVIL: THE UNDERSOVRAN" (lines 56-65), forbids a spawned body/boss; doc 37's "The Deep Table" (lines 759-786) does not instantiate one. Doc 37 Part 4, THE UGLY REQUISITION (lines 643-646), is a diegetic echo of doc 19, "THE UNDERTOW: THE DEBT" (lines 23-54), doc 19 "Open Questions", 1 (lines 254-259), and doc 21 "D. The Debt Discovery Arc" (lines 76-85), not a visible debt meter.
- Hidden Court and comeback safety: doc 19, "THE HIDDEN COURT" (lines 166-214) and "Open Questions", 6 (lines 276-280), reserve the ace for debt default or Third Path crisis. Doc 37 does not explicitly deploy that ace through a key. Ordinary dungeon faction wars must not be mistaken for comeback events: doc 22, "THE GREAT CITIES AND THE SIEGE TRIGGERS" (lines 182-197), gives the locked minor-city-conquest trigger. Doc 13's "COUNTERWEIGHT" is still an IO proposal (lines 98-100), not the complete locked comeback specification.
- Signer provenance: doc 19, "THE RELIQUARY WARDENS", SUPERSEDED note (lines 156-164), already changes the Signer into the Pale Queen's role. Doc 37's THE WARDEN'S DOUBLE LEDGER (lines 407-412) refers to that mask consistently. Old Signer passages in docs 20-21 were not counted as new doc 37 contradictions.

## Source file key

All paths are relative to docs/planning/. Numeric citations above identify these exact files and their named sections.

- 04: 04-combat-system.md
- 06: 06-loot-and-resources.md
- 07: 07-leveling-progression.md
- 12: 12-moral-axis-factions.md
- 13: 13-territory-conquest.md
- 19: 19-fall-of-the-veil-throne.md
- 20: 20-quests-factions-gdd-part1.md
- 21: 21-quests-factions-gdd-part2.md
- 22: 22-quests-factions-gdd-part3.md
- 31: 31-vertical-slice-scope.md
- 34: 34-enemy-ai-and-bestiary.md
- 35: 35-slice-systems.md
- 37: 37-popup-quests.md

## Verification

- Branch: dev. Tracked worktree and staged diffs are empty.
- This audit created only docs/planning/37-B-crossdoc-consistency.md, incrementally. No existing file was modified. No commit or push was performed.
- Validation passed: ASCII-only text, contiguous B1-B15 identifiers, and one resolution line per finding.
- Final status also contains untracked sibling audits 37-A-internal-consistency.md and 37-C-feasibility-slice-fit.md. They were not created or changed by this worker. Therefore the repository is not literally clean except for this file; all tracked files remain clean.

FINDINGS SUMMARY: 15 findings; HIGH contradiction: 1; MEDIUM unexplored: 12; LOW polish: 2.

