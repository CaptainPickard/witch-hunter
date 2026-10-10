#!/bin/bash
# IO finalize sequence for EPR1 gate step 2 (Testerbot valspec):
# 1) freeze E2 floor against the PURE origin/dev worktree server (8794)
# 2) full pre-build smoke of wh_erparity_validation.py against the same clean base
cd /workspace/witch-hunter/scratch/erparity
rm -f floor/weave_floor.log floor/v2_floor.log floor/v3_floor.log floor/mousebind_floor.log
python3 freeze_floor.py > /tmp/floor_freeze_final.log 2>&1
WH_BASE_ROOT=http://127.0.0.1:8794/ python3 wh_erparity_validation.py > /tmp/erparity_smoke_final.log 2>&1
echo "FINALIZE DONE rc=$?"