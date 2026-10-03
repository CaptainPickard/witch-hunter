# Astrabot Mission Brief - HUD bars to top-left (2026-10-03)

Nicko change order (verbatim): "Lets put the health, stamina, and magic bars
at the top left corner of the screen."

Baseline: feat/world-visuals @ ed9f0e7 in worktree /tmp/wh-worldfeat. All
previous work confirmed working. NO harness runs - his playtest is the bar.
esprima syntax checks only. ONE commit to feat/world-visuals IN THE WORKTREE,
then append "## Astrabot findings" and amend (message starts "feat: hud bars
top-left"). NO pushes. No touching: /workspace/witch-hunter, servers,
io/specs, docs/planning, art GLB binaries, player mount code (sword round 2
is a SEPARATE mission running after this one - do not touch player.js).

## IO facts you need (pre-read done)
- Bars live in prototype/index.html inside #wh-hud (lines ~12-17): .bar-outer
  elements #wh-hp-bar-outer (fill #wh-hp-bar), #wh-stam-bar-outer
  (fill #wh-stam-bar), focus bar per moveset HUD block. Styling in
  prototype/style.css (.bar-outer, .bar-fill.hp/.stam classes ~line 169+).
- IMPORTANT COLLISION: the pink asset-failure note (#wh-asset-fail-note,
  created by assets.js flushAssetFailureNote) is already absolute-positioned
  top:6px left:8px z-index:40 inside #wh-hud. If bars move to top-left it
  will overlap. RELOCATE the note in the same pass: move it below the bars
  (e.g. top: calc(<bars block height>px + 8px), left:8px) by changing the
  inline cssText in assets.js flushAssetFailureNote - same file it is
  created in, tiny change.
- Keep z-order: bars must not overlap the boot overlay (z 30) or the
  failure note (z 40). #wh-hud children are game HUD - fine to raise.

## Implementation shape
- CSS-only placement where possible: reposition the bar stack region to
  top-left (top:8px, left:8px, vertical stack hp -> stam -> focus). If the
  current layout is a horizontal row anchored elsewhere (check .hud / #wh-hud
  css), rotate the layout to a column via flex direction, width ~220-260px,
  small gap. Title text/labels (HP/Stam/Focus) keep current styling but may
  shrink if needed; keep pixel-look (no smooth gradients introduced).
- HP, stamina AND the magic/focus bar ALL move together - all three in the
  column, same order they appear now.
- Mobile: #wh-hud already serves the small screen; verify the same stack
  works at ~640px wide (pure CSS, no media-query build-out needed unless
  truncation forces it).
- Do not rename ids (game.js hud refs must keep working: wh-hp-bar,
  wh-stam-bar etc).
- Acceptance (Nicko plays): three bars stacked in the top-left corner,
  readable, not overlapping the pink asset note or boot overlay, HUD
  updates (damage drain, stamina regen, focus spend) all still visible.

## Guardrails
- index.html + style.css + assets.js (note relocation only). NO js logic
  changes. No CONFIG knobs for this one (pure placement).
- Keep diff tight (~80 lines). Player copy law: never "free"; no agent names.