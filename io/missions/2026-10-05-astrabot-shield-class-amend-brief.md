# ASTRABOT MISSION BRIEF - Order D-amend: shield weight-class block slowdown (mechanics, small)
2026-10-05, from IO. Nicko's rule (10-05, stated while Order D runs):
- "when blocking the player speed should be slowed [by shield class]: small
  shields like bucklers only slow 25%, medium shields 50%, heavy tower shields
  block 75%."
Supersedes the fixed CONFIG.block.moveMult = 0.5 in the D brief's DO-NOT-CHANGE
law for the MOVE path ONLY (parry window/absorb/arc/guard-break/riposte stay).

Dispatch this AFTER Order D lands (same-worktree sequential law).

You are Astrabot, Claude Code print-mode agent, worktree /tmp/wh-worldfeat
(branch feat/world-visuals). Commit + push once. Short report appended to
scratch/astrabot_orderD_shield_block_report.md (AMENDMENT section).

## CHANGES
1. Per-item block movement: CONFIG.items[*].block.moveMult (optional).
   - roundShield: 0.5 (medium - unchanged feel today)
   - buckler: 0.75, towerShield: 0.25 - ADD THESE TWO ENTRIES as dormant items
     (kind 'shield', hands both, NO mesh/mount entry yet: equipping refusal
     toast 'No visual - asset pending' if ever equipped via debug; they exist
     for stage 2 drops).
   - Items without the key fall back to CONFIG.block.moveMult (0.5 legacy).
2. player.js block slow path (~1369): speed multiplies by the LEFT-hand shield
   item's block.moveMult (fallback CFG.block.moveMult). ONE lookup, no new
   state.
3. Report note: weight-class table + where future shield absorb/stamina class
   stats could hang off the same data shape (do NOT implement).

## AC (Nicko)
| AC | Test |
|---|---|
| DA1 | Blocking with roundShield slows to 50% of walk exactly as today |
| DA2 | Debug-equipping buckler (WH_DEBUG) blocks at 75% speed; towerShield 25% |
| DA3 | No other block numbers moved (parry timing, absorb, arc) |

Final chat message: commit sha, table of the three classes, what to playtest.