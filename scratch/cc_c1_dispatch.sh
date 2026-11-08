#!/bin/bash
# CC-C1 builder dispatch - heightfield spike, per io/missions/2026-10-07-cc-c1-heightfield-spike.md
cd /tmp/wh-worldfeat || exit 1
export HOME=/home/hermeswebui/.hermes/profiles/io/home
export PATH="$HOME/.local/bin:$PATH"
LOG=/tmp/wh-worldfeat/scratch/cc_c1_builder_log.txt
echo "=== CC-C1 dispatch start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" > "$LOG"

claude -p --model opus \
  --permission-mode acceptEdits \
  --allowedTools "Read Write Edit Bash" \
  --max-turns 80 \
  "Read the change-order brief at io/missions/2026-10-07-cc-c1-heightfield-spike.md in the repo root (your cwd) and execute it in full, in order. Hard laws first: SCRATCH-ONLY - the ONLY files you may create/edit are scratch/region-c-spike/* and appending to scratch/cc_c1_builder_log.txt; every prototype/js file, index.html, style.css, docs/, io/ is READ-ONLY. Do NOT run tools/build_v8.py. Do NOT git commit, do NOT git push - IO commits the spike record after review; leave only working-tree artifacts. NO harness, NO headless browser, NO playwright runs of the game or of your demo - Nicko plays the demo himself; your verification is node --check plus code reading. Vendor three.js only: reference three.classic.js from ../../prototype/vendor/ (relative to the demo dir; nothing newer exists on this box). Summary of the mission: standalone demo page scratch/region-c-spike/index.html + region-c-spike.js implementing (1) deterministic seed-1337 fBm value-noise terrain 560x560, height ~0..5, flat spawn pocket r~25 at origin, PlaneGeometry with S in {100,140,180} toggle via keys 1/2/3; (2) WASD stand-in actor with slope max-step guard and orbit camera never underground; (3) all THREE height samplers A analytic fBm / B grid bilinear / C downward raycast, compared over >=1000 random points: max/mean|diff vs raycast| and per-call microseconds, verdict row naming the CC-C4 strategy; (4) on-screen panel: S density, renderer.info triangles, rolling fps from a ~60s scripted waypoint walk run once at load, build ms; (5) SPIKE-LOG.md with all numbers, slope percentiles in degrees, climbFactor used, recommendation paragraph (production S, sampler, climbFactor, warnings). Final reply exactly per the brief's FINAL REPLY FORMAT: files created with sizes, node --check result, git status output, measurement table, sampler comparison + verdict, slope percentiles, recommendation paragraph, and anything unfinished." \
  >> "$LOG" 2>&1
echo "=== CC-C1 dispatch end $(date -u +%Y-%m-%dT%H:%M:%SZ) exit=$? ===" >> "$LOG"
echo "DISPATCH WRAPPED, log tail:" >> "$LOG"
tail -4 "$LOG" >> "$LOG"