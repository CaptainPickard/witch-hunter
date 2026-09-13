# 37-A - Internal Consistency Audit (2026-09-13)

Scope: contradictions, overlapping systems, numbering, and internal references in doc 37 only. Doc 08 supplies tracker context, not cross-document findings. Existing files remain read-only.

Initial repository check: branch dev; git status --short was empty.

## Rulings and early systems

### A1 - HIGH contradiction - PUBLIC heirlessness still requires stealth

Citation: Session rulings, ruling 6 (lines 34-41); Part 3b, THE PRIVATE-CONVERSATION RULE (lines 277-287), FOLLOWER LIABILITY and TIE-IN (lines 308-317); The intel tier table, PUBLIC (lines 324-329).

The old rule says a player seeking the heirless-noble fact must remain unseen. The locked tier table explicitly makes that fact ambient, with no audience check or risk. The mechanics notes do not limit follower liability to GUARDED facts.

Resolution: Apply audience checks and follower liability only to GUARDED facts, and explicitly exempt PUBLIC heirlessness in the earlier examples.

### A2 - HIGH contradiction - Sleep-only capture includes an awake road trigger

Citation: Session rulings, ruling 7 (lines 42-49); Part 3c, The trigger (lines 440-449).

The trigger says kidnappers do not attack on the road and take the player ASLEEP, but lists "crossing the bridge at dusk" as a capture opportunity. Crossing supplies neither the required sleep state nor an off-road setting. The separate no-currency-loss and no-XP-loss capture rules agree with ruling 7.

Resolution: Replace the crossing example with sleeping near the bridge, or seek an explicit ruling before permitting awake road captures.

### A3 - HIGH contradiction - Guaranteed killer identity conflicts with fallible testimony

Citation: Part 3, The loop, THE VENDETTA GRAVE (lines 207-210); Open Questions, question 4 (lines 1052-1057).

The vendetta guarantees that the named killer is true because the dead cannot lie. The resolved truth rule explicitly includes "their killer" among truthful testimony that may be mistaken. A sincere accusation is not a guaranteed correct target under that rule.

Resolution: State whether bound vendetta identity is an explicit exception to fallible testimony, and reconcile the two passages without silently changing the ruling.

### A4 - MEDIUM unexplored - Rumor purchases bypass the intel access rule

Citation: Part 1, THE VETERAN'S ACCOUNT and THE LEDGER PAGE (lines 112-120); Part 3b, The intel tier table (lines 321-339); Part 5, Key tiers, THE AUCTION HOUSE (lines 892-895).

The tier table says it decides WHERE facts can be learned and makes monster and treasure locations private-conversation-only. Accurate purchased dungeon accounts, mapped dossiers, and auctioned intel supply alternative channels without a stated exemption or audience-check policy. This is an unresolved interface between systems, not proof that every rumor contains a guarded location.

Resolution: Define how paid intel and dossiers obey GUARDED access rules, and limit public rumors to information that does not reveal guarded facts.

## Descent, faction, and replayability systems

### A5 - MEDIUM unexplored - The single door has four incompatible-looking unlock descriptions

Citation: Session rulings, ruling 10 (lines 59-61); Part 5, Session rulings, ruling 10 (lines 710-714); The gate rule (lines 724-757); Faction keys opening paragraph (lines 790-793).

One door contains four strata, but the ladder calls them GATE I-IV, assigns four lock tiers, says the door opens on the layer matching level, and then permanently unlocks the gate after one pick. It never says whether opening at level 10 exposes all strata, preserves deeper thresholds, or selects an entry layer. Faction keys add another way past the door without defining which depth checks survive.

Resolution: Describe one physical door with explicit per-stratum access rules, including permanent unlocking and faction-key precedence, and rename ladder entries to strata.

### A6 - MEDIUM unexplored - CONTESTED has two competing entry conditions

Citation: Session rulings, ruling 14 (lines 77-88); Part 5, Key tiers, TIER RULES (lines 903-910); The Situation system, 15B (lines 931-944).

CONTESTED is explicitly "the tier-3 key state" but also one of six timer-rolled situations. Tier-3 keys require sworn standing and war-seeded availability. No rule says whether a random CONTESTED roll bypasses those gates, requires them, or merely advertises inaccessible tier-3 content.

Resolution: Define one transition authority for CONTESTED and distinguish the outside situation signal from permission to enter a tier-3 faction battle.

### A7 - MEDIUM unexplored - Persistent faction claims compete with tenant replacement

Citation: Part 5, Faction keys, CLAIM RULE (lines 831-836); Key tiers, THE WAR BELOW (lines 868-873); The Cleared-Wound Rule and the Situation system, 15A-15B (lines 920-944).

A keyed layer keeps its faction content until a different faction key is used. Vacuum tenants replace cleared inhabitants, OCCUPIED records who holds the dungeon now, and war corridors change hands between visits. The document does not separate a persistent claim from current occupants or define which system can displace faction content.

Resolution: Separate claim ownership from physical occupation and specify how clears, situation changes, and battle outcomes affect each state without requiring a new key.

### A8 - HIGH contradiction - Old-pool respawns survive the no-old-self rule

Citation: Session rulings, ruling 15 (lines 89-102); Part 5, 15A THE CLEARED-WOUND RULE (lines 920-929); What I would add, THE LAYER BOSS RULE and SCAVENGER SPOILS (lines 987-995).

The locked vacuum rule says the dungeon "does not respawn its old self" and replaces cleared inhabitants with new tenants. The later working notes still apply inhabitants-respawn-on-rest and preserve the base layer's respawn economy without qualification. Both rules govern cleared spaces but imply different inhabitants and refresh clocks.

Resolution: Mark the old respawn notes superseded or define a bounded respawn rule for the current tenant that cannot restore the destroyed original population.

## Numbering, catalog identity, and internal references

### A9 - MEDIUM unexplored - The owning document stops its question sequence at 23

Citation: Part 5, Open Questions (lines 1008-1023); final Open Questions (lines 1043-1098).

The two lists contain 1-18 and 19-23, with no duplicates, but omit 24-32. Thus the faction-key, key-tier, and replayability systems have no corresponding local question entries. Tracker context confirms that these nine questions already exist; the defect reported here is their absence from doc 37, not a separate tracker audit.

Resolution: Restore questions 24-32 with their existing assignments and present one navigable 1-32 sequence.

### A10 - LOW polish - Catalog counts mix listed and separately described archetypes

Citation: Session rulings, ruling 8 (lines 50-55); Part 3c heading (line 432); Part 4 numbered catalog and Count line (lines 586-694); Slice scoping, OUT OF SLICE (lines 1035-1038).

Part 4 lists 25 entries, then claims 26. Part 3c explicitly supplies archetype 26, so the document-wide count is defensible, but the catalog omits its listing. Slice scoping still calls it a 24-archetype catalog. The toll seed is an entry into the Warren chain, not evidence of a separate additional archetype.

Resolution: Add a catalog entry 26 pointing to Part 3c and change the slice count to 26 without counting the toll seed again.

### A11 - LOW polish - The goblin bounty points to salvage instead of the bounty system

Citation: Part 3b, The overheard quest-seed catalog, THE GOBLIN TOLL (lines 413-419); Part 4, entry 2 GRAVE-LEASE SALVAGE (lines 590-592); Part 2, CONTRACT TIERS (lines 143-146).

"Monster-bounty quest (catalog 2, VERMIN tier)" points to Warden crypt salvage. VERMIN is defined in Part 2, not catalog entry 2.

Resolution: Replace "catalog 2" with "Part 2, CONTRACT TIERS" and link the expanded chain to Part 3c.

### A12 - LOW polish - The toll's catalog identity is ambiguous

Citation: Part 3c, Working for the king, THE NEW COLLECTOR (lines 478-481), and The four endings, THE CLEARED LEDGER (lines 547-549); Part 3b, THE GOBLIN TOLL (lines 413-419); Part 4, entry 11 THE ACCUSED (lines 624-627).

"Catalog seed 11" means the eleventh bullet in the unnumbered overheard seed list, not numbered catalog entry 11. The later "toll line in the catalog" never specifies which catalog. This invites treating the seed, collector state, and Warren chain as separate catalog records.

Resolution: Reference "Part 3b, THE GOBLIN TOLL" by name and identify collector service as a state of archetype 26.

### A13 - MEDIUM unexplored - Catalog scope excludes a system its own archetype requires

Citation: Part 4 opening (lines 577-582); Session rulings, ruling 8 (lines 50-55); Part 3c, The trigger and capture rule (lines 440-459).

The catalog says no new systems are required beyond the rumor engine and Quiet Parish. Its declared archetype 26 requires a hidden faction grudge, sleep ambush, recoverable gear hoard, and the game's first non-death defeat state. Those dependencies are not merely a rumor or grave conversation.

Resolution: Update the catalog dependency statement to include the Warren capture and faction-grudge systems, while retaining the frame-grammar claim.

### A14 - LOW polish - The vendetta's refusal ending is cut off

Citation: Part 3, The loop, THE VENDETTA GRAVE resolution texture (lines 221-227).

The refusal branch ends at "the revenant" without closing its parenthesis. The next line starts "can complete it quietly", leaving the revenant as the apparent subject and obscuring one of the three promised player endings.

Resolution: Complete the refusal consequence and restore "the player" as the subject of the quiet and loud completion branches.

## Checks with no separate finding

- Read doc 37 through its final line and doc 08 through its final tracker entry. Doc 08 records questions 24-32 for the later passes; no findings audit other documents.
- Main session rulings are exactly 1-15, without gaps or duplicates. Part 5 restates rulings 9-12 in a clearly scoped subsection. Those repetitions are not numbering defects.
- Ruling 3 and Quiet Parish CONSENT TEXTURE agree: digging always costs light reputation; consent changes what the dead give. Keeper standing is a separate stated consequence, not a second light-reputation charge.
- Ruling 7 and Part 3c agree that capture replaces the ambush death penalty, restores access to recoverable gear, and loses no currency or XP. The sleep-trigger mismatch is A2, not a death-penalty mismatch.
- Ruling 11, Part 5's faction-key overlay, and TIER RULES all preserve the regional equipment tier band. No listed key explicitly grants an out-of-band item. Key tiers and depth strata are separate axes, not extra equipment tiers.
- The overheard seed list contains 12 seeds. Its toll seed expands into archetype 26 rather than establishing a twenty-seventh archetype.
- The SALT SCARE reference reaches catalog 13. References to Part 3b, Part 3c, Part 5, open question 15, and the mislabeled door's open question 2 reach their stated subjects.

## Verification

Only this audit file was written by this task, incrementally. Findings A1-A14 have continuous numbering, exact section citations, and one resolution line each. Automated checks confirm ASCII-only text.

Git verification found no tracked changes: both git diff --stat and git diff --cached --stat were empty. The initial status was clean. The final check also found sibling audit files created during this task, so exclusive untracked-file status cannot honestly be confirmed:

- docs/planning/37-A-internal-consistency.md
- docs/planning/37-B-crossdoc-consistency.md
- docs/planning/37-C-feasibility-slice-fit.md

No commits or pushes were made. No sibling files were read or modified.

FINDINGS SUMMARY: HIGH contradiction: 4; MEDIUM unexplored: 6; LOW polish: 4; TOTAL: 14.
