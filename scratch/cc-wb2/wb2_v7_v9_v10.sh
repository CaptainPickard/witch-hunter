#!/bin/bash
# V-7/V-9/V-10 shell one-shots (cc-wb2 valspec; read-only git only).
cd /tmp/wh-worldfeat || exit 1

echo "=== V-7 build + markers ==="
python3 tools/build_v8.py > /tmp/wb2_v7_build.log 2>&1
V7_EXIT=$?
echo "build exit: $V7_EXIT"
tail -3 /tmp/wb2_v7_build.log
MARKERS=$(grep -o 'CC-WB2' prototype/builds/v8-playable.html | wc -l)
echo "CC-WB2 markers: $MARKERS (law >= 6)"
SIZE=$(stat -c%s prototype/builds/v8-playable.html)
echo "artifact bytes: $SIZE"
TITLE=$(grep -o '<title>[^<]*</title>' prototype/builds/v8-playable.html | head -1)
echo "title stamp: $TITLE"
echo "$MARKERS" | grep -qE '^[0-9]+$' && awk -v m="$MARKERS" 'BEGIN{exit !(m>=6)}' && echo "V7-MARKERS-PASS" || echo "V7-MARKERS-FAIL"
[ "$V7_EXIT" = "0" ] && echo "V7-EXIT-PASS" || echo "V7-BUILD-FAIL"

echo
echo "=== V-9 ledger grep ==="
for tok in pact creditor Undersovran debt; do
  C1=$(grep -ci "$tok" prototype/js/wareffort.js || true)
  C2=$(sed -n '/window.WH_CONFIG.warEffort/,/^};/p' prototype/js/CONFIG.js | grep -ci "$tok" || true)
  C3=$(grep -ci "$tok" prototype/builds/v8-playable.html || true)
  echo "token '$tok': wareffort.js=$C1 CONFIG.warEffort=$C2 built=$C3"
  if [ "$C1" != "0" ] || [ "$C2" != "0" ]; then echo "V9-FAIL($tok board-facing source)"; else echo "V9-OK($tok sources)"; fi
done
# built-artifact scan is diagnostics-only (game content may mention iron for the war etc)
echo "V9 built-artifact hits are reported for observation (board-facing law binds SOURCES; built hits from other modules are inspected not auto-failed)"
grep -ioE 'pact|creditor|undersovran|debt' prototype/builds/v8-playable.html | sort | uniq -c || true

echo
echo "=== V-10 NO-GIT audit ==="
HEADNOW=$(git rev-parse HEAD)
echo "HEAD now: $HEADNOW"
echo "HEAD V-0 : a4d3736d845895bcd0a1ccd7bfd6e04e364fe650"
[ "$HEADNOW" = "a4d3736d845895bcd0a1ccd7bfd6e04e364fe650" ] && echo "V10-HEAD-UNCHANGED" || echo "V10-HEAD-CHANGED"
LAST=$(git log -1 --format=%H)
[ "$LAST" = "a4d3736d845895bcd0a1ccd7bfd6e04e364fe650" ] && echo "V10-NO-NEW-COMMITS" || echo "V10-NEW-COMMIT($LAST)"
STAGED=$(git diff --cached --name-only | wc -l)
[ "$STAGED" = "0" ] && echo "V10-NOTHING-STAGED" || echo "V10-STAGED($STAGED)"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "branch: $BRANCH (expected feat/world-visuals)"
[ "$BRANCH" = "feat/world-visuals" ] && echo "V10-BRANCH-UNCHANGED" || echo "V10-BRANCH-CHANGED"
echo "status porcelain:"
git status --porcelain | head
