#!/usr/bin/env python3
"""CC-C17v2 paste: append a probed row block at the END of CONFIG.regionC.props
(existing row indices unchanged). usage: apply_rows.py <rows.json> <header-comment-file>
Each row may carry a '_c' trailing comment (stripped from the row)."""
import json, sys
CFG = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
ANCHOR = "\n    ],\n    // CC-C8 ROT MOTHER'S DOORWAY"
rows = json.load(open(sys.argv[1])); head = open(sys.argv[2]).read().rstrip('\n').split('\n')
src = open(CFG).read()
assert src.count(ANCHOR) == 1, 'anchor'
def num(v): return (("%.3f" % v).rstrip("0") if round(v, 2) != v else "%.2f" % v) if isinstance(v, float) else str(v)
lines = ['      // ' + h for h in head]
for r in rows:
    c = r.pop('_c', None)
    body = "{ asset: '%s', x: %.1f, z: %.1f, rotY: %.2f, scale: %s" % (r['asset'], r['x'], r['z'], r['rotY'], num(r['scale']))
    for k in ('wall', 'y', 'cullM'):
        if k in r: body += ', %s: %s' % (k, num(r[k]))
    body += ' },'
    lines.append('      ' + body + (('   // ' + c) if c else ''))
src = src.replace(ANCHOR, '\n' + '\n'.join(lines) + ANCHOR, 1)
open(CFG, 'w').write(src)
print('appended', len(rows), 'rows')
