#!/usr/bin/env python3
"""Host-side serving verification: merged equip+radiance content."""
import subprocess

def host_exec(cmd):
    out = subprocess.run(['python3', '/tmp/dhost.py', cmd],
                         capture_output=True, text=True).stdout
    return out.strip()

checks = [
    ("/tmp/wh-worldfeat-clean/prototype/js/player.js", "leftHand", "player leftHand"),
    ("/tmp/wh-worldfeat-clean/prototype/js/player.js", "stowToShield", "player stow"),
    ("/tmp/wh-worldfeat-clean/prototype/js/CONFIG.js", "radiance", "config radiance"),
    ("/tmp/wh-worldfeat-clean/prototype/js/spells.js", "RadianceEffect", "spells effect"),
    ("/tmp/wh-worldfeat-clean/prototype/js/game.js", "radiances", "game effect list"),
    ("/tmp/wh-worldfeat-clean/prototype/js/assets.js", "roundShield", "manifest shield"),
]
bad = 0
for path, needle, label in checks:
    out = host_exec("grep -c %s %s" % (needle, path))
    ok = out and out.strip('\n\r').splitlines()[-1].isdigit() and int(out.strip().splitlines()[-1]) > 0
    print(('PASS' if ok else 'FAIL'), label, '=', out.strip().replace('\u0001', '').replace('\x00', '')[-3:])
    bad += 0 if ok else 1
print('FAILS:', bad)