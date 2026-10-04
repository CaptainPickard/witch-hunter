"""Static (no game loop) check of the Round B bandit wiring.
python3 scratch/check_bandit_wire.py REPO_ROOT
Parses anim.js/enemy.js/assets.js with esprima, reads CharacterAnim VARIANTS
from the AST, and confirms every bandit slot clip exists in banditBody's GLB.
"""
import re
import sys
from pathlib import Path
import esprima

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse

root = Path(sys.argv[1])
js = root / 'prototype/js'
trees = {f: esprima.parseScript((js / f).read_text()) for f in ('anim.js', 'enemy.js', 'assets.js')}
for f in trees:
    print('parse ok', f)


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


decl = next(find(trees['anim.js'], lambda n: n.type == 'VariableDeclarator' and
                 getattr(n.id, 'name', None) == 'VARIANTS'))
variants = obj(decl.init)
print('VARIANTS keys', sorted(variants))
assert {'zombie', 'bandit'} <= set(variants)
assert any(n.type == 'AssignmentExpression' and getattr(n.left.property, 'name', None) == 'VARIANTS'
           for n in find(trees['anim.js'], lambda n: n.type == 'AssignmentExpression'))
expected = {'idle': 'WH_Idle_Melee', 'walk': 'WH_Walk_Melee', 'run': 'WH_Run_Melee',
            'attack': 'WH_Attack_High', 'hit': 'WH_Hit_Large_L', 'death': 'WH_Death'}
assert variants['bandit'] == {'names': expected, 'moves': {}}, variants['bandit']
print('bandit names', variants['bandit']['names'], 'moves', variants['bandit']['moves'])
enemy = (js / 'enemy.js').read_text()
assert "{ variant: this.type === 'ghoul' ? 'zombie' : 'bandit' }" in enemy
print('enemy.js passes variant zombie|bandit')
assets = (js / 'assets.js').read_text()
body = re.search(r"banditBody: '([^']+\.glb)'", assets).group(1)
tex = re.search(r"banditBody: '([^']+\.png)'", assets).group(1)
assert body.endswith('orc-male-warrior.mixamo.glb') and tex.endswith('orc-male-warrior.rigged.pixelated.png')
doc, _ = parse(root / body)
names = {a['name'] for a in doc['animations']}
missing = [c for c in expected.values() if c not in names]
assert not missing, missing
print('banditBody', body, '-> all 6 slot clips present in GLB (%d clips)' % len(names))
print('BANDIT_WIRE_STATIC_PASS')
