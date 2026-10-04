"""Static (no game loop) check of the Round C player sword wiring.
python3 scratch/check_player_sword_wire.py REPO_ROOT
Parses anim.js/player.js/assets.js with esprima, reads VARIANTS from the AST,
confirms sword.moves IS the MOVE_NAMES identifier (not a copy), player.js passes
variant 'sword', and every sword-variant clip exists in playerBody's GLB.
"""
import re
import sys
from pathlib import Path
import esprima

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse


def find(node, pred):
    if isinstance(node, list):
        for n in node:
            yield from find(n, pred)
    elif hasattr(node, 'type'):
        if pred(node):
            yield node
        for v in vars(node).values():
            if isinstance(v, list) or hasattr(v, 'type'):
                yield from find(v, pred)


def obj(node):
    return {(p.key.name or p.key.value): obj(p.value) if p.value.type == 'ObjectExpression'
            else p.value.value for p in node.properties}


root = Path(sys.argv[1])
js = root / 'prototype/js'
trees = {f: esprima.parseScript((js / f).read_text()) for f in ('anim.js', 'player.js', 'assets.js')}
for f in trees:
    print('parse ok', f)


def declared(name):
    return next(find(trees['anim.js'], lambda n: n.type == 'VariableDeclarator' and
                     getattr(n.id, 'name', None) == name)).init


variants = declared('VARIANTS')
keys = [p.key.name for p in variants.properties]
print('VARIANTS keys', len(keys), keys)
assert keys == ['zombie', 'bandit', 'sword'], keys
sword = next(p.value for p in variants.properties if p.key.name == 'sword')
names = obj(next(p.value for p in sword.properties if p.key.name == 'names'))
moves = next(p.value for p in sword.properties if p.key.name == 'moves')
assert moves.type == 'Identifier' and moves.name == 'MOVE_NAMES', moves
move_names = obj(declared('MOVE_NAMES'))
expected = {'idle': 'WH_SwordIdle', 'walk': 'WH_SwordWalk', 'run': 'WH_SwordRun',
            'attack': 'WH_Attack1', 'hit': 'WH_Hit', 'death': 'WH_Death'}
assert names == expected, names
assert obj(declared('NAMES'))['attack'] == 'WH_Attack1'
print('sword names', names, '| moves = MOVE_NAMES', move_names)
player = (js / 'player.js').read_text()
assert player.count("{ variant: 'sword' }") == 1
print("player.js passes { variant: 'sword' }")
assets = (js / 'assets.js').read_text()
body = re.search(r"playerBody: '([^']+\.glb)'", assets).group(1)
tex = re.search(r"playerBody: '([^']+\.png)'", assets).group(1)
assert body.endswith('human-hunter-male.combat-sword.glb'), body
assert tex.endswith('human-hunter-male.rigged.pixelated.png'), tex
count = re.search(r"var CHARACTERS = \{ playerBody: (\w+)", assets).group(1)
doc, _ = parse(root / body)
clips = [a['name'] for a in doc['animations']]
assert count in ('true', str(len(clips))), (count, len(clips))
missing = [c for c in list(names.values()) + list(move_names.values()) if c not in clips]
assert not missing, missing
print('playerBody', body, '-> all sword slot + chain move clips present (%d clips; CHARACTERS=%s)'
      % (len(clips), count))
print('PLAYER_SWORD_WIRE_STATIC_PASS')
