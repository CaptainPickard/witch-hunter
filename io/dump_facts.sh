#!/usr/bin/env bash
# Per-function dump facts + the ac_a1_4 tail (cellvar loop question).
for f in 314_ac_a1_1 361_ac_a1_2 455_ac_a1_3 496_ac_a1_4 607_ac_a2_2 678_ac_a2_4 722_ac_a3_1 805_ac_a3_3 847_ac_a3_4 99_stage; do
  lines=$(grep -c . "/tmp/pyc_dump/$f.txt")
  nl=$(sed -n '1p' "/tmp/pyc_dump/$f.txt" | sed 's/.*nlocals=//')
  echo "$f: lines=$lines nlocals=$nl"
done
echo "--- ac_a1_4 tail last 25 non-JUMP lines ---"
sed -n '290,324p' /tmp/pyc_dump/496_ac_a1_4.txt