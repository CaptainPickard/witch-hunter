# CC-C15 · Den relocation: SW quadrant, snug against the rim mountains + trail/lanterns removed

## 1. RULING (Nicko, 2026-10-20)
- Move the rot mother's den to the SOUTH-WEST quadrant of the map, snug up
  against the mountain side (the map border).
- Remove the temporary denTrail road + the 3 lanternWaymarker signs (CC-C12).
- Execution BLOCKED until the CC-C13a/C13b subagent sessions land (they edit
  CONFIG.js too; IO is the sole writer after).

## 2. SITE (offline probe /tmp/c15_site_probe.py, region C coords)
- Region C center (0, -366), playable rim 278.5, rim mountains foot r 240,
  ridge peak 34 at ~270-276, skirt flush at 280.
- Bearing 225 deg (SW): 0=north, 90=east, 180=south, 270=west.
- OUTCROP (C-side approach + doorway): r 238 -> ~( -168.4, -197.6 ) at the
  mountain FOOT (walkable; approach grade inside C's ~19 deg natural max).
- DEN disc (regionD, hidden while C active): r 256 -> ~( -181.0, -185.0 ),
  groundRadius 34 (unchanged) - its mouth faces NE back toward the map.
- Clearances: west wolf loop 147+ m, nearest props = the OLD outcrop rows
  (they MOVE with the den; nothing else within 45 m).
- Mechanics unchanged: region-defs connections[2] C<->D door, E-to-enter at
  the outcrop (interactM 3.5), walk-back mouth plane, fade dips, den-local
  lair (0, +6), flag key rotmother_cleared_C byte-equal.

## 3. EXECUTION PLAN (after children land)
1. Generate new rows: adapt scratch/cc-c8/gen_den.py -> scratch/cc-c15/
   gen_den_sw.py: OC_new/outcrop at r238/225deg, den center at r256/225deg,
   front vector U = from outcrop TOWARD the den center (NE->SW face out),
   recompute FACE rotY, stains trail mouth->den, C-side land rows, keepOut
   and tri ledger re-printed. Pure arithmetic, no game run.
2. CONFIG.js edits:
   - REMOVE: roads rows denTrail + denTrailNotch; the 3 CC-C12
     lanternWaymarker sign rows (fork/mid/doorway); the CC-C12 trail comment.
   - REMOVE: old outcrop prop rows (5 vinestone + m1 gate pair + boulders +
     brambles + egg sacs at the (-136,-219) site), old regionC.rotLair
     stains/void rows.
   - PASTE: the SW outcrop block + new regionC.rotLair rows at the new site.
   - regionD: translate the whole block - center, door.planeZ/doorX (recompute
     from the new mouth), interactAt, land rows (C side + den side), lairs
     row, ALL den props (ring 10, shoulders, furniture, nest pool, egg sacs)
     - rigid translation by the den-center delta + orientation recompute for
     the ring gap/mouth only (den internals keep local bearings).
   - regionD.door.interactAt (C side) = the new outcrop opening centre.
   - Keep: every mechanic row (fade timings, prompt text, wall collider tags,
     cullM values), keepOut/clearances respected on the new approach.
3. Probes before paste: prop-prop min gap >= 4 m (site probe + generated
   ledger), approach line clear (no tree rows within trunk + road clears),
   terrain grade along the approach <= 19 deg natural (pure arithmetic from
   the rim ridge formula; the pocket/pads are far away), wolf loops >= 40 m.
4. node --check CONFIG.js; build_v8; commit; push; 8793 flip; serve verify.

## 4. ACCEPTANCE
- A1: denTrail + lanternWaymarker CC-C12 rows GONE from CONFIG + bundle.
- A2: regionD center + lairs + lands + outcrop rows all at the new SW site;
  no stale (-136/-139/-175,-22x/-27x) coordinates left.
- A3: tri ledger unchanged in total (same props, moved not added).
- A4: probe report pasted into the brief (min gaps + grades + loop dists).
- A5: node --check clean; bundle rebuilt; both serves verified.

## 5. WATCH ITEM (separate defect, unchanged)
- Wolf legs STILL frozen on the live build (C10 yaw fix landed; facing
  confirmed fixed). Nicko to read the ?whdbg=1 chip lines at a wolf pack;
  CC-C13b extends the chip (CLIPS count + stand-in detector). The freeze is
  a live-runtime fact the offline sims cannot reproduce.