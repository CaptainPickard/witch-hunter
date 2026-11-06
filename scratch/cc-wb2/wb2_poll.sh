#!/bin/bash
# V-0 landing poll (cc-wb2): wait in-process for Devbot's changes, then
# verify. >=15 min polling budget inside the one-shot per the dispatch law.
cd /tmp/wh-worldfeat || exit 1

CONFIG_WANT="9da84bd62ff3460a1e388cd57538b2dddbe8ab5ef7d45b26d53ad17d4020b9b2"
WARE_WANT="6f5d03af6e11266741b7cd2b69926765e5e08f66ee6a17038ea023ef1e12da99"
GAME_WANT="afe066a1697bf15d563914a15b9bccd1bfe300901d8f75a0f54e7131ffe733fd"
IDX_WANT="9fbae01d1583cd98bc9fb7ac08ea7deedb73623ba1af67afbd54b00d088b230b"
HEAD_WANT="a4d3736d845895bcd0a1ccd7bfd6e04e364fe650"

POLL_BUDGET=${1:-960}       # default 16 minutes (>= the 15-min law)
INTERVAL=${2:-30}           # 30 s between probes
START=$(date +%s)

while true; do
  NOW=$(date +%s)
  ELAPSED=$((NOW - START))
  C=$(sha256sum prototype/js/CONFIG.js | cut -d' ' -f1)
  W=$(sha256sum prototype/js/wareffort.js | cut -d' ' -f1)
  MARKERS=$(grep -o 'CC-WB2' prototype/builds/v8-playable.html 2>/dev/null | wc -l)
  if [ "$C" != "$CONFIG_WANT" ] || [ "$W" != "$WARE_WANT" ]; then
    echo "LANDED after ${ELAPSED}s: CONFIG=$C wareffort=$W markers=$MARKERS"
    break
  fi
  if [ "$MARKERS" -ge 6 ] 2>/dev/null; then
    echo "LANDED (markers $MARKERS) after ${ELAPSED}s: CONFIG=$C wareffort=$W"
    break
  fi
  if [ "$ELAPSED" -ge "$POLL_BUDGET" ]; then
    echo "POLLOUT after ${ELAPSED}s: NOT LANDED. CONFIG=$C (want $CONFIG_WANT) wareffort=$W (want $WARE_WANT) markers=$MARKERS"
    exit 3
  fi
  echo "poll ${ELAPSED}s: not landed (CONFIG unchanged, markers=$MARKERS); sleeping ${INTERVAL}s"
  sleep "$INTERVAL"
done

# Landed: full pre-validation sha table + zero-touch probe
sha256sum prototype/js/CONFIG.js prototype/js/wareffort.js prototype/js/game.js prototype/index.html prototype/builds/v8-playable.html
echo "--- zero-touch probe on landing ---"
G=$(sha256sum prototype/js/game.js | cut -d' ' -f1)
I=$(sha256sum prototype/index.html | cut -d' ' -f1)
H=$(git rev-parse HEAD)
[ "$G" = "$GAME_WANT" ] && echo "ZERO-TOUCH game.js OK" || echo "ZERO-TOUCH-VIOLATION game.js=$G"
[ "$I" = "$IDX_WANT" ] && echo "ZERO-TOUCH index.html OK" || echo "ZERO-TOUCH-VIOLATION index.html=$I"
[ "$H" = "$HEAD_WANT" ] && echo "HEAD unchanged OK" || echo "HEAD-CHANGED=$H"
echo "git status:"
git status --porcelain | head
