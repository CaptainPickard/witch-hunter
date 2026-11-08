#!/bin/bash
# CC-C8 TRIM2 builder - real-boulder count cut, per io/missions/2026-10-12-cc-c8-trim2.md
cd /tmp/wh-worldfeat || exit 1
export HOME=/home/hermeswebui/.hermes/profiles/io/home
export PATH="$HOME/.local/bin:$PATH"
LOG=/tmp/wh-worldfeat/scratch/cc_c8_trim2_log.txt
echo "=== CC-C8 TRIM2 dispatch start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" > "$LOG"

claude -p --model opus \
  --permission-mode acceptEdits \
  --allowedTools "Read Write Edit Bash" \
  --max-turns 40 \
  "Execute the trim-2 brief at io/missions/2026-10-12-cc-c8-trim2.md exactly: revert all mossBoulderSmall rows to mossBoulder then DELETE the listed rows (6 outcrop horseshoe, 5 den shoulders), DELETE the mossBoulderSmall manifest row + bootCritical row, update block comments, python3 tools/build_v8.py, node --check CONFIG.js + assets.js, fix scratch/cc_c8_ledger_probe.js T table (drop mossBoulderSmall entry), run node scratch/cc_c8_ledger_probe.js . -84 -309 170 and paste the C8 LAYOUT line verbatim. NO commit/push. Finish with: deleted rows (x/z), kept-row vm confirmation, probe line, bundle bytes, syntax results, then STOP." \
  >> "$LOG" 2>&1
echo "=== CC-C8 TRIM2 dispatch end $(date -u +%Y-%m-%dT%H:%M:%SZ) exit=$? ===" >> "$LOG"
tail -5 "$LOG"