#!/usr/bin/env python3
"""Fix assets.js fusion: machinery bled into loadAttempt's promise body.
Re-cut so: machinery funcs (module scope) -> loadAttempt (full) -> loadOne."""
import re

p = '/workspace/witch-hunter/prototype/js/assets.js'
src = open(p).read()

# The fused region: from the start of the machinery (embeddedDataUris map at
# module scope is FINE) to loadOne's body. Find the actual seams.
m_begin = src.index("  // The manager modifier is synchronous")
m_attempt = src.index("  // One load attempt, racing the per-attempt timeout.")
m_loadone = src.index("  function loadOne(name, url, isPixelated) {")
m_preload = src.index("  // Preload every manifest entry.")

# Segment analysis:
# [m_begin .. m_attempt): machinery header + loadAttempt-proto pieces fused
seg = src[m_begin:m_preload]
print("--- fused segment inspection ---")
# locate the fused promise fragment inside seg (loader.load inside machinery)
fused_load = seg.index("      loader.load(url, function (gltf) {")
trunc_at = seg.index("      \n", fused_load)
print(seg[fused_load:trunc_at] [:200])

open('/tmp/assets_fused_segment.txt','w').write(seg)
print("segment saved to /tmp/assets_fused_segment.txt for inspection")
print("seg length:", len(seg), "loadAttempt starts at", m_attempt - m_begin, "loadOne at", m_loadone - m_begin)