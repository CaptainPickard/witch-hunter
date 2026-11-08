#!/usr/local/bin/python3
"""DAG B3: dagger actionbar/grid icon via the AB1 io_icon lane.
Reuses tools/io_icon_render.py verbatim (face_colors / render_icon /
pixelize): NON-pixelated Phase A GLB source (Round 2 QA rule), 512 render
into scratch/io_icons512/dagger.png -> NEAREST 48 + 5-bit posterize into
prototype/js/icons/dagger.png. Then run tools/io_icon_registry.py.
Usage: /usr/local/bin/python3 scratch/dagger_icon.py [yaw zoom roll]
"""
import os, sys
sys.path.insert(0, '/tmp/wh-worldfeat/tools')
import trimesh
import io_icon_render as R

YAW, ZOOM, ROLL = -25, 1.0, -40
if len(sys.argv) == 4:
    YAW, ZOOM, ROLL = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
glb = os.path.join(R.ROOT, 'art-direction/3d/assets/weapons/dagger-curved.glb')
m = trimesh.load(glb, force='mesh', process=False)
cols = R.face_colors(m, glb)
p512 = os.path.join(R.ROOT, 'scratch', 'io_icons512', 'dagger.png')
p48 = os.path.join(R.ROOT, 'prototype', 'js', 'icons', 'dagger.png')
R.render_icon(m, cols, p512, YAW, ZOOM, roll_deg=ROLL)
R.pixelize(p512, p48)
print('icon dagger ok', 'yaw', YAW, 'zoom', ZOOM, 'roll', ROLL, 'faces', len(m.faces))
