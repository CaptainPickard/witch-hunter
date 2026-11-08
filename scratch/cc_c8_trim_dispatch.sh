#!/bin/bash
# CC-C8 TRIM builder - tri-budget fix per io/missions/2026-10-12-cc-c8-trim.md
cd /tmp/wh-worldfeat || exit 1
export HOME=/home/hermeswebui/.hermes/profiles/io/home
export PATH="$HOME/.local/bin:$PATH"
LOG=/tmp/wh-worldfeat/scratch/cc_c8_trim_log.txt
echo "=== CC-C8 TRIM dispatch start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" > "$LOG"

claude -p --model opus \
  --permission-mode acceptEdits \
  --allowedTools "Read Write Edit Bash" \
  --max-turns 40 \
  "Execute the trim brief at io/missions/2026-10-12-cc-c8-trim.md in the repo root (your cwd) exactly: mossBoulder swaps to mossBoulderSmall where specified, one cemeteryGate removed + 2 bramble re-dress, manifest row + boot-load row, count comments updated, python3 tools/build_v8.py, node --check on the 2 edited files. Then run node scratch/cc_c8_ledger_probe.js . -84 -309 170 and paste the 'C8 LAYOUT' line. Budget: commit-by is NOT on you (NO commit/push - IO commits). Finish with: rows changed (old->new asset per row), new outcrop + den tri totals, the probe line verbatim, bundle bytes, node --check results, then STOP." \
  >> "$LOG" 2>&1
echo "=== CC-C8 TRIM dispatch end $(date -u +%Y-%m-%dT%H:%M:%SZ) exit=$? ===" >> "$LOG"
tail -5 "$LOG"