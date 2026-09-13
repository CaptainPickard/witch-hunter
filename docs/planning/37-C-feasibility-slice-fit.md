# 37-C - Feasibility and Slice-Fit Audit (2026-09-13)

Status: audit findings and proposed resolutions only. No new locks.
Scope: doc 37 read in full; cross-check against docs 30, 31, 35 and the frame, world, and bestiary owners. Citations use file numbers and line ranges in this checkout. Existing files are read-only.
Severity: HIGH contradiction; MEDIUM unexplored; LOW polish.
Authority caveat: doc 31 is the explicit slice boundary, but its header still marks remaining scope/numbers PROPOSED. Only the engine and Rot-Mother inclusion carry explicit locks there. This audit does not upgrade its entire scope to a Nicko lock. Doc 35 also mixes locked rulings with broader proposed slice systems.

## C1. HIGH contradiction: the proposed quest slice is not slice 1

- Evidence: doc 37, lines 1025-1041, includes rumors, bounty contracts, digging, reactive World Ledger writes, and a dungeon round trip. Doc 31, lines 17-21 and 56-68, explicitly says combat-loop slice, not a quest/world demo, and excludes quests, factions, moral axis, World Ledger, procedural interiors, and stealth. Its tavern is one door stub, not a populated rumor hub.
- Impact: this is a new acceptance target and dependency stack, not cheap tissue content on top of the arena. Doc 35's broader save/economy proposals do not authorize reversing doc 31's OUT list.
- Recommended resolution: label doc 37's subset a separate post-combat quest integration slice; require an explicit scope ruling before adding it to doc 31.

## C2. HIGH contradiction: the slice's dungeon leads cross the locked intel gate

- Evidence: doc 37, lines 110-120, has public hearsay point at dungeons and a paid veteran identify what lives there; lines 330-339 require monster and treasure locations to be GUARDED and spoken only when speakers believe they are alone. Lines 1029-1041 include both rumor tiers and discovery without a private-listening exception. Doc 31, lines 67-68, excludes stealth.
- Impact: buying a drink cannot silently bypass the locked private-conversation rule. Not every rumor needs stealth, but a precise monster-location lead does under the current wording.
- Recommended resolution: classify each slice rumor's facts explicitly; defer guarded facts with stealth, or seek a ruling on consensual private disclosure rather than treating payment as an implicit exemption.

## C3. MEDIUM unexplored: dialogue and schedule ownership is still missing

- Evidence: doc 37, lines 112-135, requires procedural patrons, standing checks, promotion and source memory; lines 280-307 add deferral, relocation, and scheduled private meetings. Doc 30 G17, lines 219-230, explicitly leaves dialogue format, instantiation, disposition and even place-based versus scheduled NPCs unresolved. Doc 35, lines 138-145, persists NPC positions, not conversation or schedule state.
- Candidate question: can the later rumor proof use fixed tavern patrons with event-triggered lines, while scheduled private conversations remain a separate feature? Suggested owners: doc 20 for rumor eligibility and a G17 dialogue/schedules specification for runtime behavior.
- Impact: HEARSAY and VETERAN'S ACCOUNT do not inherently require daily schedules. Inheriting all of Part 3b would add them unnecessarily, along with interruption and retry state.
- Recommended resolution: define a place-based rumor MVP and explicitly defer G17 daily schedules; assign conversation state and source-memory schema before implementing either tier.

## C4. HIGH contradiction: the slice dig loop imports standing and non-slice actors

- Evidence: doc 37, lines 174-179, makes keeper detection a mini-faction standing event with shovel, map and rite services; lines 236-242 require light-reputation loss on every dig. Lines 1031-1034 retain keeper and revenant wake risk. Doc 31, lines 30-32 and 56-68, offers one human combat body, excludes moral axis/factions and stealth, and provides graveyard clutter rather than a cemetery system.
- Impact: omitting dead-speech correctly avoids the undead-graverobber gate, but does not remove keeper AI, detection, faction memory, dig interaction, inventory and reputation dependencies. A revenant also needs an explicit roster mapping, not an assumed extra enemy.
- Recommended resolution: defer digging to the quest integration slice, or separately approve a ghoul-wake interaction with no claim that it implements the full reputation-bearing Quiet Parish loop.

## C5. HIGH contradiction: the proposed proof archetypes exceed the enemy and encounter roster

- Evidence: doc 37, lines 612-619 and 1035-1037, proposes THE LOST CHILD and THE NIGHT HAUNTER. The latter requires a ghost or wight and destroy/rest/bargain outcomes. Doc 34, lines 3-6, explicitly locks Bandit 180, Rot Wolf 140, Grave Ghoul 220 and Rot-Mother 900; doc 31, lines 25-46, supplies a combat arena, not rescue actors or dialogue encounters.
- Impact: THE LOST CHILD can reuse those enemies as captors, but needs a captive, rescue/body outcomes and potentially another delve. THE NIGHT HAUNTER cannot ship as written with this roster. A ghoul reskin does not automatically supply ghost/wight identity or bargaining. Neither requires dead-speech by definition; a living investigator could discover the haunting's cause.
- Recommended resolution: for a separately approved quest proof, prefer THE MONASTERY MEAL as a ghoul clear-site plus a wolf VERMIN contract; retain the four locked stat blocks and explicitly cost any rescue or curse-lift extension.

## C6. MEDIUM unexplored: combat perception is not an audience-check specification

- Evidence: doc 37, lines 277-311 and 1070-1083, delegates private speech to G19 and G17. Doc 30 G19, lines 244-254, still lacks stealth/lockpicking specification. Doc 34, lines 19-30, does provide proposed sight/noise detection for combat, so claiming that no perception model exists would be wrong.
- Candidate question: does suspected presence with detection below combat aggro suppress speech, and which speaker's belief governs? What about followers, bystanders, walls, crowds, recovery after interruption and NPCs who move away? Suggested owners: a G19 stealth specification using doc 34 perception, plus G17 conversation state.
- Impact: reusing the combat threshold of 100 would let suspicious speakers disclose guarded information; testing all nearby actors without an intended-audience rule could suppress conversations forever.
- Recommended resolution: specify an audience predicate, speech propagation and interruption/retry state independently of combat aggro, sharing perception primitives where appropriate.

## C7. MEDIUM unexplored: situations have no interior representation contract

- Evidence: doc 37, lines 920-953, combines permanent destruction, replacement tenants, six situations and exterior tells; lines 979-986 suggest changed room grammar. Doc 03, lines 4-6 and 40-43, locks persistent generated layouts. Doc 30 G24, lines 301-309, still lacks room grammar, generation constraints and persistence representation; doc 37 open 19, lines 1010-1012, only assigns layer-generation work.
- Candidate question: is a situation an overlay on immutable room IDs, a pre-authored room-state swap, or a topology mutation? Who updates navigation, hazards, collision, entrance signs and reachable exits? Suggested owner: doc 03's G24 dungeon-generation specification.
- Impact: a new tenant pool and entrance banner do not define how an occupied, flooded or collapsing interior changes without erasing the player's wounds or stranding quest actors.
- Recommended resolution: define stable dungeon/layer/room IDs and allowed situation overlays, with reachability checks against permanent destruction, before authoring situation-specific content.

## C8. MEDIUM unexplored: permanent wounds have no bounded save contract

- Evidence: doc 37, lines 920-929, promises burnt rooms, cut bridges and persistent boss corpses. Doc 35, lines 138-145, names static seeds and generic system deltas, not per-room destructible records, corpse representation or a memory budget. Doc 30 G24, lines 305-308, asks seed versus full layout versus entity deltas. Doc 08 open 32, lines 807-809, already assigns the wound budget to a slice-systems pass; this is assigned but unspecified, not an entirely unowned question.
- Candidate question: which destruction is a finite authored flag and which is arbitrary geometry? How many room/object/corpse records persist per dungeon and across a full playthrough? Suggested owners: doc 35 G13 for serialization and doc 03 G24 for stable identities and bounded destructibles.
- Impact: a seed cannot reconstruct player modifications. Permanent physical debris and corpses have different storage, streaming and runtime costs from a room-state flag; no numeric budget can be inferred from these docs.
- Recommended resolution: choose a bounded sparse-delta model and publish a worst-case per-dungeon/playthrough budget plus save/load and version-migration tests; do not silently weaken the locked permanence promise.

## C9. HIGH contradiction: the new tenant rule and existing respawn rule disagree

- Evidence: doc 37, lines 920-929, says the dungeon does not respawn its old self and grows a new tenant. Doc 35, lines 151-153, says dungeon inhabitants respawn on rest except bosses. Doc 37, lines 987-995, still imports that older respawn economy. Doc 35, lines 128-145, commits dungeon-clear state only on exit and restores unsaved enemy kills, bosses included, on reload.
- Impact: resting after a clear can either restore the defeated residents or preserve a vacuum awaiting new tenants. A boss corpse cannot be treated as both permanently committed on kill and reverted on an unsaved reload. These are rule-precedence questions, not spawn weights.
- Recommended resolution: rule explicitly on partial kills versus completed clears, rest versus long-timer recolonization, and live wounds versus exit-committed saves; preserve doc 35's locked exit trigger unless Nicko changes it.

## C10. MEDIUM unexplored: faction keys lack a per-dungeon state schema

- Evidence: doc 37, lines 790-836 and 903-910, changes layers by court family, proposes persistent claims, and gates key tiers on prior clears and war state. Doc 35, lines 138-145, has no keyed-layer record. Doc 08, lines 749-758 and 776-783, already tracks layer scope, claim consequences and corridor persistence, but does not supply a schema.
- Candidate question: is a key stored per gate, per stratum or per room? Does a new key replace or suspend previous claims, loot, quests and faction-clear history? How do claim, situation, key tier and permanent wounds compose? Suggested owners: doc 35 G13 for serialized records, doc 03 G24 for composition, doc 13 for claim authority.
- Impact: repeated re-keying can duplicate rewards or resurrect cleared occupants unless key family/tier, unlocks, faction-clear history, claim owner, situation epoch and loot state have stable identities and precedence. Changing content need not regenerate the underlying layout.
- Recommended resolution: define one versioned dungeon-state record and an atomic re-key transition, including occupied-floor safety and reward deduplication, before pricing keys.

## C11. MEDIUM unexplored: bounty boards have locations but no persistent lifecycle

- Evidence: doc 37, lines 139-159, lists tavern boards, chapels, guild posts and requisition stones, with generated contracts and player bounties. Doc 20, lines 78-93, handles patron death and expiry; doc 35, lines 138-145, lists quest flags and NPC/vendor state, not physical board identity or posting state.
- Candidate question: are postings shared world contracts or independently generated per board? What survives hold conquest, a destroyed chapel, patron death, accepting a posting and save/load? Does a paper remain, vanish or display its resolved state? Suggested owners: doc 03 for physical anchors, doc 20 G26 for contract lifecycle, doc 35 G13 for persistence.
- Impact: the same hunt could pay twice at different boards, or remain advertised after its site changes. An abstract menu and a persistent in-world object are not the same implementation.
- Recommended resolution: give each board and contract a stable ID, define posted/accepted/resolved/expired presentation, and persist a single reward-authority record across every posting surface.

## C12. HIGH contradiction: frame expressibility is being used as proof of free implementation

- Evidence: doc 37, lines 577-582 and 691-694, claims all archetypes need no new systems beyond rumors and Quiet Parish. Its own Part 3c, lines 440-458 and 473-563, requires capture, gear escrow, debt installments, gambling and flood escape. Doc 20, lines 46-79, defines frame fields, not executable objective operators; the actual eight-template list is doc 21, lines 115-117. Doc 30 G26, lines 323-332, explicitly leaves generator authoring data unowned.
- Finding: no additional top-level frame type is demonstrably mandatory. All 26 can be described with the existing labels, often as compositions. That does not prove that a single existing frame can execute them. A chain runner and objective/consequence primitives are missing from the claimed implementation boundary.
- Recommended resolution: retain the eight labels provisionally, assign the following mapping and chain/verb schema to docs 20/21 G26, and replace the no-new-systems claim with an explicit dependency list.

### C12 evidence matrix: all 26 archetypes

Candidate mappings, not locked authoring decisions. Rows 1-25 cite doc 37, lines 586-689; row 26 cites Part 3c, lines 432-573. The template vocabulary is doc 21, lines 115-117. A plus sign means composition, not a proposed ninth frame.

| ID | Archetype | Candidate existing frame(s) | Extra execution dependency |
|---|---|---|---|
| 1 | The Dead Man's Ledger | relic-hunt | Dead-speech, competing buyers |
| 2 | Grave-Lease Salvage | relic-hunt | Collapse timer, per-artifact authentication |
| 3 | The Silent Ferryman | escort | Moving patron, interception |
| 4 | The Cartographer's Last Map | relic-hunt | Discovery chain, persistent map reward |
| 5 | Purge the Den | clear-site | Hidden faction patron |
| 6 | The Hanged Man's Debt | curse-lift + supply | Grave relocation, timed ghost consequence |
| 7 | The Quiet Commission | relic-hunt | Rival claimant and reputation writes |
| 8 | The Lost Child | clear-site + escort | Captive alive/dead state, deeper-chain branch |
| 9 | The Night Haunter | curse-lift | Haunter actor, investigation and bargaining |
| 10 | The Monastery Meal | clear-site | Optional evidence and suppression branch |
| 11 | The Accused | parish-work + escort | Execution deadline, innocence evidence |
| 12 | The Bleeding Field | clear-site + supply | Persistent burn or sample objective |
| 13 | The Salt Scare | parish-work | Investigation and selected culprit truth |
| 14 | Relic Recovery | relic-hunt | Competing recipient selection |
| 15 | The Ugly Requisition | supply | Debt-conditioned requirements |
| 16 | The Blood Tithe | supply | Partial collection and warning outcomes |
| 17 | The Desecration | parish-work | Ritual placement and witnessed-bounty writes |
| 18 | The Unmaking | relic-hunt | Theft, ownership and detection |
| 19 | The Pale Pilgrim | escort | Night clock and betrayal pursuit |
| 20 | Grave-Goods Retrieval | relic-hunt | Distributed targets and restitution |
| 21 | The Leaning Cross | parish-work + clear-site | Crypt discovery/unlock handoff |
| 22 | The Drowned Bell | curse-lift | Bell interaction and alternate world effects |
| 23 | The Quiet Parish | relic-hunt + parish-work | Multi-witness dead-speech chain |
| 24 | Refugee Roads | escort + defense | War-spawned NPCs, alternate trafficking branch |
| 25 | The Dead Man's Justice | hunt | Bound target, assassination and succession writes |
| 26 | The Warren Under the Bridge | hunt + supply + escort + relic-hunt + clear-site | Capture, debt jobs, escape, gear escrow, four-ending chain |

Supply here can carry an information-delivery objective, but that operator still needs specification. Parish-work must not become an unlimited catch-all that hides missing objective types. Row 26's four endings do not alone violate doc 20: its wording permits 2-3+ endings (lines 69-74).

## C13. MEDIUM unexplored: rumor truth and live quest targets can race dungeon changes

- Evidence: doc 37, lines 124-135, distinguishes true, stale and planted rumors and improves a verified source's standing. Lines 931-947 allow situations to change on long timers and announce those changes. Doc 20, lines 81-93, handles expiry consequences but does not define site-version invalidation. Doc 08, lines 801-806, tracks transition timing and tenant tables, not active-contract arbitration.
- Candidate question: if a truthful veteran names a ghoul nest and a new faction occupies it before arrival, is the source punished? Does the accepted hunt migrate, expire, or freeze the encounter? What happens to a captive or proof item in a collapsed room? Suggested owners: doc 20 G25/G26 for facts and contracts, doc 03 G24 for site transitions, doc 35 G13 for atomic saves.
- Impact: four independent clocks can produce unreachable objectives or false source grudges without a fact timestamp, provenance and explicit resolution policy. Freezing every accepted quest would also suppress the promised living-world changes.
- Recommended resolution: version site facts and specify one deterministic fails-forward policy for each quest objective when its target or situation changes.

## C14. MEDIUM unexplored: proof-as-reagent has no consumption or attribution rules

- Evidence: doc 37, lines 147-156, makes trophies crafting reagents and gives every contract alternative resolutions; open 3, lines 1050-1051, only names generic versus specific proof. Doc 35, lines 81-94, separates materials from a zero-weight quest pocket. Its regular enemies respawn on rest (lines 151-153).
- Candidate question: can a jaw harvested before accepting a hunt satisfy it, can one trophy serve multiple boards, and what completes a spared or bargained outcome? Does crafting the only proof fail the contract, or can another piece substitute? Suggested owners: doc 20 for objective attribution, doc 06 for item identity, doc 35 G12/G14 for storage and turn-in.
- Impact: classifying reusable reagents as quest-pocket items can erase their weight cost; accepting any generic respawn drop can bypass the named target or repeatedly pay one contract.
- Recommended resolution: specify proof provenance, inventory class, consume-on-turn-in behavior, alternative-outcome evidence and single-payment guards together.

## C15. MEDIUM unexplored: capture needs transactional saves and a guaranteed release path

- Evidence: doc 37, lines 451-458, explicitly exempts one capture ambush from death loss and escrows gear; lines 516-543 provide proposed escapes; lines 550-563 permit leaving without gear and voluntary entry. Doc 35, lines 125-145 and 215-243, specifies death deltas and ordinary item retention, not capture state.
- Candidate question: what survives quitting after gear removal but before waking, death inside the warren, destruction of the hoard, or capture while an earlier corpse drop exists? Is at least one escape possible with minimum stats and no carried tools? Suggested owners: doc 35 G13/G15, doc 04 defeat-state transitions, doc 20 chain-state authoring.
- Impact: the locked capture exception is intentional, not itself a contradiction with normal death. The missing transition protocol can duplicate or lose inventory, apply both penalties, or trap a build unable to meet an escape check.
- Recommended resolution: specify an atomic capture/escrow/release transaction, preserve the prior corpse explicitly, and prove a no-tool release path before generalizing faction capture.

## C16. MEDIUM unexplored: overheard information has no accessible delivery contract

- Evidence: doc 37, lines 269-287 and 297-307, requires learning world facts by listening with no interface revealing them independently. Doc 30 G16, lines 208-217, has no audio-design owner; G17, lines 219-230, has no dialogue delivery format; G33, lines 390-399, leaves subtitles/accessibility/localization open. Doc 31, line 95, even permits an empty audio folder for combat slice 1.
- Candidate question: are eligible lines voiced, subtitled, replayable or logged after hearing? How do simultaneous conversations, missed words, hearing impairment and localization preserve the earned-information rule? Suggested owners: a G16 audio specification and G17 dialogue specification, with doc 35 G11 accessibility presentation.
- Impact: subtitles gated by the same earshot/audience predicate need not reveal forbidden intel. Ungated captions or an automatically populated quest panel would bypass the rule; no accessible delivery would exclude players from a core information verb.
- Recommended resolution: define perception-gated subtitle/audio delivery and replay policy without adding pre-discovery world-fact readouts.

## C17. LOW polish: stale scope and tracker references hide the later passes

- Evidence: doc 37, lines 1027-1038, still says four parts and a 24-archetype catalog despite Part 5 and the 26 count at lines 691-694. It never explicitly excludes Overheard Word, Warren capture, descent gates, faction keys or situations from its proposed subset. Open 19, lines 1010-1012, points to doc 31 G24 although the gap is in doc 30. Doc 08, lines 747-809, says opens 24-32 are tracked in doc 37, whose open lists actually contain 1-18 and 19-23. Doc 08 open 32 points to doc 35 G11 for persistence, which is G13.
- Impact: these references make assigned-but-unspecified work look missing or make later full-game systems appear implicitly slice-required. In particular, the wound budget already has a tracker assignment; it is not a wholly unowned discovery.
- Recommended resolution: synchronize the open lists and correct gap references, then add an explicit post-combat/deferred table for every later Part 3b/3c/5 subsystem without changing locked rulings.

## Coverage and slice boundary

- G16: listening delivery (C16). G17: patron/dialogue/schedule state (C3, C6). G18: daily schedules and long-timer site changes (C3, C13). G19: audience detection and dig risk (C4, C6).
- G20: follower detection is a full-game dependency (doc 37, lines 308-311), not grounds to add followers to the combat slice (doc 31, line 62). G21: excluding dead-speech correctly avoids transformation/class requirements (doc 37, lines 1031-1034). G22: none of the three proposed proof loops inherently requires mounts; do not import a mount system merely for travel.
- G23: doc 31, lines 134-150, owns an arena performance proposal, not a budget for streaming persistent interiors, scheduled towns, or three-way faction battles (doc 37, lines 854-873). Cost and profile those in the later world/quest milestone; do not count the arena test as evidence of feasibility.
- G24: interior representation, stable IDs, room reachability and state persistence remain prerequisites (C7-C10). G25/G26 remain explicit post-combat quest dependencies in doc 30, lines 313-332.
- No new ninth frame is proven necessary. No daily schedule system is inherently necessary for fixed-patron rumors. Neither observation makes doc 37's proposed quest loop fit doc 31's current combat-only boundary.

FINDINGS SUMMARY: 17 findings; HIGH contradiction: 6; MEDIUM unexplored: 10; LOW polish: 1. All 26 archetypes mapped provisionally to the eight existing templates. Recommended scope: post-combat quest integration milestone, not an implicit expansion of slice 1.
