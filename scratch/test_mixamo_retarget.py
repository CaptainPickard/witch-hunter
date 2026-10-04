"""Regression tests; run after the two batch outputs exist.
python3 -m unittest discover -s scratch -p test_mixamo_retarget.py -v
"""
import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest
from glb_append_clips import parse, save as write_glb, accessor_bytes
from verify_retarget import verify

ROOT = Path(__file__).resolve().parents[1]
RIGS = ROOT / 'art-direction/3d/assets/races_regen/rigged'
BODIES = {'bandit': 'orc-male-warrior', 'ghoul': 'undead-ghoul-male'}
# Bandit .mixamo.glb is baked from the skin-weight-fixed orc (Round B capefix).
MESH_FIX = {'bandit': ROOT / 'scratch/mixamo-fbx/capefix/orc-male-warrior.rigged.glb'}
BAKE_LOG = {'bandit': 'bandit-capefix-bake.json', 'ghoul': 'ghoul-bake.json'}


class RetargetRegression(unittest.TestCase):
    def test_accessor_stride_and_offset(self):
        g = {'accessors': [{'bufferView': 0, 'byteOffset': 4, 'componentType': 5126,
                            'type': 'VEC3', 'count': 2}],
             'bufferViews': [{'byteOffset': 4, 'byteLength': 32, 'byteStride': 16}]}
        binary = b'HEAD' + b'PAD!' + struct.pack('<3f', 1,2,3) + b'PAD!' + struct.pack('<3f', 4,5,6)
        self.assertEqual(accessor_bytes(g, binary, 0), struct.pack('<6f',1,2,3,4,5,6))

    def check_mutation(self, mutate):
        old, new = RIGS/'orc-male-warrior.rigged.glb', RIGS/'orc-male-warrior.mixamo.glb'
        g,b = parse(new)
        b = bytearray(b)
        mutate(g,b)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'mutant.glb'
            write_glb(path,g,b)
            result = verify(old,path,json.loads((ROOT/'scratch/mixamo_bandit.json').read_text()),
                            mesh_fix=MESH_FIX['bandit'])
        self.assertFalse(result['pass'])
        return result

    def test_both_deliveries(self):
        for body,stem in BODIES.items():
            with self.subTest(body=body):
                manifest = json.loads((ROOT/f'scratch/mixamo_{body}.json').read_text())
                bake = json.loads((ROOT/f'scratch/mixamo-fbx/reports/{BAKE_LOG[body]}').read_text())
                r=verify(RIGS/f'{stem}.rigged.glb',RIGS/f'{stem}.mixamo.glb',manifest,bake,
                         MESH_FIX.get(body))
                self.assertTrue(r['pass'],r['failed_assertions'])
                self.assertEqual(len(r['originals']),6)
                self.assertEqual(len(r['new_clips']),7)

    def test_player_sword_delivery(self):
        # Round C: combat-sword.glb = this branch's combat-chain.glb + 12 sword clips.
        # Round D appends 3 WH_SS_* attack clips (same manifest on dev and feat).
        old, new = RIGS/'human-hunter-male.combat-chain.glb', RIGS/'human-hunter-male.combat-sword.glb'
        manifest = json.loads((ROOT/'scratch/mixamo_player.json').read_text())
        manifest.update(json.loads(next(ROOT.glob('scratch/roundD-clips-*.json')).read_text()))
        count = len(parse(old)[0]['animations'])
        r = verify(old, new, manifest, original_count=count, held_poses=('WH_ShieldCrouchIdle',))
        self.assertTrue(r['pass'], r['failed_assertions'])
        self.assertEqual(len(r['new_clips']), 15)
        self.assertFalse(verify(old, new, manifest, original_count=count)['pass'])

    def test_reject_old_animation_byte_change(self):
        def mutate(g,b):
            acc=g['accessors'][g['animations'][0]['samplers'][0]['output']]
            view=g['bufferViews'][acc['bufferView']]
            offset=view.get('byteOffset',0)+acc.get('byteOffset',0)
            b[offset] ^= 1
        r=self.check_mutation(mutate)
        self.assertFalse(r['assertions']['binary_prefix_identical'])
        self.assertFalse(r['originals']['WH_Attack1']['source_data_identical'])

    def test_reject_missing_new_channel(self):
        self.check_mutation(lambda g,b: g['animations'][-1]['channels'].pop())

    def test_capefix_requires_mesh_fix_mode(self):
        manifest=json.loads((ROOT/'scratch/mixamo_bandit.json').read_text())
        r=verify(RIGS/'orc-male-warrior.rigged.glb',RIGS/'orc-male-warrior.mixamo.glb',manifest)
        self.assertEqual(r['failed_assertions'],['original_json_meshes'])

    def test_reject_mesh_change_beyond_skin_attrs(self):
        def mutate(g,b):
            g['meshes'][0]['primitives'][0]['attributes']['NORMAL']=0
        r=self.check_mutation(mutate)
        self.assertFalse(r['assertions']['original_json_meshes'])

    def test_reject_missing_old_clip(self):
        self.check_mutation(lambda g,b: g['animations'].pop(0))

    def test_reject_nan_new_rotation(self):
        def mutate(g,b):
            anim=g['animations'][-1]
            c=next(c for c in anim['channels'] if c['target']['path']=='rotation')
            acc=g['accessors'][anim['samplers'][c['sampler']]['output']]
            view=g['bufferViews'][acc['bufferView']]
            struct.pack_into('<f',b,view.get('byteOffset',0)+acc.get('byteOffset',0),float('nan'))
        self.check_mutation(mutate)

    def test_reject_nonzero_start_time(self):
        def mutate(g,b):
            acc=g['accessors'][g['animations'][-1]['samplers'][0]['input']]
            view=g['bufferViews'][acc['bufferView']]
            struct.pack_into('<f',b,view.get('byteOffset',0)+acc.get('byteOffset',0),.025)
        self.check_mutation(mutate)

    def test_reject_truncated_glb(self):
        data=(RIGS/'orc-male-warrior.mixamo.glb').read_bytes()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'truncated.glb'
            path.write_bytes(data[:-8])
            with self.assertRaises(AssertionError):
                parse(path)


if __name__ == '__main__':
    unittest.main()
