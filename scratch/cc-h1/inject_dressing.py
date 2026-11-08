"""Append the CC-H1 dressing rows after the curtain wall in regionG.props.

Rows: war-table dais, 4 braziers, banner parapets, barracks tents, chapel
arch + buttresses, yard boulders/rubble, gate lanternPost (x 6.5 per spec
sec 2's own correction). Anchors on the last wall row line (unique).
"""
src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
anchor = ("      { asset: 'whWallB', x: -4.4, z: -696.08, rotY: 3.11, scale: 4.63, "
          "sy: 11.55, sz: 2.40, y: -0.2, wall: 12 },\n")
assert src.count(anchor) == 1, 'anchor not unique: %d' % src.count(anchor)
dressing = anchor + """      // -- CC-H1 THE WAR-TABLE HUB (the hold's identity, 82 m up the lane from
      //    the gate): ONE stoneSteps dais plinth at (0, -780). No table-shaped
      //    asset in the manifest - the gap is RECORDED in the build note (doc 66
      //    sec 8): the dais + banners carry the tableau v1.
      { asset: 'stoneSteps', x: 0, z: -780, rotY: 0, scale: 1.4 },
      // -- 4x banditCampfire braziers at the hub square (8.0 m from the hub,
      //    11.3 m mutual): lightSockets.banditCampfire (hf 0.55, intensity 3.2)
      //    = the amber accent. AMENDMENT B: the warm FAMILY is FIVE sockets -
      //    these 4 + the gate lanternPost below (intensity 9.0), one family.
      { asset: 'banditCampfire', x: -5.66, z: -776.34, rotY: 0, scale: 1.8 },
      { asset: 'banditCampfire', x: 5.66, z: -776.34, rotY: 0, scale: 1.8 },
      { asset: 'banditCampfire', x: -5.66, z: -787.66, rotY: 0, scale: 1.8 },
      { asset: 'banditCampfire', x: 5.66, z: -787.66, rotY: 0, scale: 1.8 },
      // -- banner dressing on the gate approach: 6x okFenceStonewall low
      //    parapet walls flanking the lane (x -13.5/-6.5/6.5/13.5 at
      //    z -702/-704/-706, alternating sides; both seat columns clear of
      //    the 4.5 m window).
      { asset: 'okFenceStonewall', x: -13.5, z: -702, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: -6.5, z: -704, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: 6.5, z: -702, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: 13.5, z: -704, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: -13.5, z: -706, rotY: 6.24, scale: 1.2 },
      { asset: 'okFenceStonewall', x: 13.5, z: -706, rotY: 6.24, scale: 1.2 },
      // -- CC-H1 barracks corner: 3x whTent (>= 4 m mutual, >= 30 m off the lane)
      { asset: 'whTent', x: 38, z: -796, rotY: 1.2, scale: 1.0 },
      { asset: 'whTent', x: 44, z: -802, rotY: 1.8, scale: 1.0 },
      { asset: 'whTent', x: 32, z: -804, rotY: 0.9, scale: 1.0 },
      // -- CC-H1 chapel corner: archway facing the yard + 2 buttresses flanking
      { asset: 'churchArchway', x: -40, z: -800, rotY: 3.14, scale: 2.2 },
      { asset: 'churchCornerButtress', x: -49, z: -804, rotY: 3.5, scale: 2.0 },
      { asset: 'churchCornerButtress', x: -49, z: -796, rotY: 2.8, scale: 2.0 },
      // -- CC-H1 yard dressing: 4 mossBoulders + 2 rubble piles scattered wide
      { asset: 'mossBoulder', x: 20, z: -830, rotY: 1.94, scale: 1.5 },
      { asset: 'mossBoulder', x: -22, z: -826, rotY: 0.73, scale: 2.2 },
      { asset: 'mossBoulder', x: 52, z: -842, rotY: 4.82, scale: 1.7 },
      { asset: 'mossBoulder', x: -58, z: -838, rotY: 2.43, scale: 1.9 },
      { asset: 'rubblePile', x: 12, z: -724, rotY: 3.30, scale: 1.1 },
      { asset: 'rubblePile', x: -16, z: -736, rotY: 5.10, scale: 1.1 },
      // -- CC-H1 gate lanternPost at (6.5, -706): THE spec's own correction
      //    (x 2.5 sat INSIDE the 4.5 m window; 6.5 keeps the lane clear).
      //    lightSockets.lanternPost: hf 0.76, intensity 9.0.
      { asset: 'lanternPost', x: 6.5, z: -706, rotY: 4.72, scale: 2.535 }
    ],
"""
src = src.replace(anchor, dressing, 1)
open('/tmp/wh-worldfeat/prototype/js/CONFIG.js', 'w').write(src)
print('dressing rows injected')
