# Continue the Witch Hunter 3D viewer debugging. The repo is
# /workspace/witch-hunter (github CaptainPickard/witch-hunter, branch dev).
#
# CONTEXT: A 46-asset 3D production run completed (10 race bodies 15k tris, 9
# weapons 2k, 8 armor 3k/5k, 15 church kit 2k, 4 graveyard 2k). All GLBs live in
# art-direction/3d/assets/<category>/<name>.glb and <name>-pixelated.glb. They
# are viewable/equippable in art-direction/3d/arsenal-viewer.html, a
# self-contained three.js r147 page (all GLBs inline as base64 data URIs), also
# served by the Hermes WebUI at the /art-3d-viewer route, linked from the hub
# at /art-hub. Source of truth: art-direction/3d/asset-manifest.md and
# art-direction/3d-spike/SPIKE-LOG.md.
#
# THE PROBLEM (user screenshot AISelect_20260913_134813_Chrome-1.jpg):
# When Nicko views a race body in the arsenal viewer (human-hunter-male
# selected, nothing equipped), the figure renders WRONG:
#   - black silhouette with white salt-and-pepper speckle texture
#   - small detached black shards floating near the arms and feet
#   - legs appear fused, head reads as a blob
#   - overall geometry looks mangled vs the concept
#
# WHAT IS ALREADY KNOWN (verified, do not re-derive):
# 1. The GLB data itself is structurally fine. Python-side renders
#    (trimesh/matplotlib orthographic preview, art-direction/3d/ortho_preview.py)
#    of the SAME pixelated glb show a correct upright hunter: head, A-pose
#    arms, cloak, two legs. Texture atlas is a valid (if dark) 256px atlas:
#    70% dark pixels, mean RGB ~35, no alpha/metallic tricks, metallicFactor 0.
# 2. So the defect is in the BROWSER RENDER path (three.js r147 + GLTFLoader +
#    the page's pixelFilter/material/lights), not in the asset data.
# 3. Likely suspects, in order:
#    a. fast_simplification decimation may have produced tiny disconnected
#       triangle islands ("floating shards"). Check with trimesh
#       face-adjacency graph connectivity (use networkx or a manual union-find;
#       networkx is NOT installed - either pip install networkx or write a
#       small union-find). The user screenshot shows detached shards, and
#       decimation to exactly 2k/15k can orphan triangles.
#    b. The texture is 70% near-black. With NearestFilter + no mipmaps
#       (pixelFilter sets generateMipmaps=false when nearest), a dark noisy
#       atlas reads as salt-and-pepper at distance. The user-visible
#       "corruption" may partly be this, by design but too harsh.
#    c. The page's material is whatever GLTFLoader produces (MeshStandardMaterial
#       with the baked texture). Lights: ambient 0x8a97a4 at 1.3, directional
#       0xc8d8e8 at 2.2, directional rim 0x8aa4b4 at 1.6, point 0x9ab8c8 at 2.2.
#       A dark albedo (mean ~35/255) under these lights still renders near-black.
#    d. The deployed WebUI route /art-3d-viewer may serve a STALE viewer build
#       (the file was rebuilt several times; check what the route actually
#       serves vs the on-disk art-direction/3d/arsenal-viewer.html, and check
#       whether the running WebUI process picked up the latest hub + route).
#
# YOUR TASKS, in order:
# 1. DIAGNOSE the shards: load each race glb (all 10 under
#    art-direction/3d/assets/races/), count disconnected components in the
#    decimated mesh (pip install networkx first if needed). Report: how many
#    tiny components (<10 faces), how many tiny components far from the body
#    (distance > 1.0 from origin). If tiny islands exist, fix = in the build
#    pipeline (art-direction/3d/ retexture.py + the batch build scripts) OR a
#    post-pass script: keep only the largest connected component (bodies are
#    single-mesh; weapons/kit can be multi-part - only drop components that are
#    BOTH tiny AND far from the main body bbox). Apply the fix to all 10 race
#    glbs + re-run the pixel pass for any changed mesh.
# 2. DIAGNOSE the salt-and-pepper: render the male body in an actual headless
#    browser with playwright (installed, chromium headless shell available via
#    python3 -m playwright) against the viewer page itself:
#      - serve /workspace/witch-hunter over a local http port
#      - load arsenal-viewer.html, select human-hunter-male
#      - screenshot at the default camera AND after setting
#        camera.position.set(0,1.3,3.2) + controls.target.set(0,1.0,0)
#      - also screenshot with the RAW texture toggle on
#    Compare: does the noise disappear with LinearFilter+Mipmaps (raw mode)?
#    If yes, the pixelated path needs fixing: most likely fix is keeping
#    mipmaps ON with NearestMipmapLinearFilter for minFilter (crisp mag,
#    smooth min) instead of full Nearest both. Update pixelFilter in
#    art-direction/3d/arsenal-viewer.html (and the template
#    art-direction/3d/arsenal-viewer.template.html) accordingly, then rebuild
#    with python3 art-direction/3d/build_viewer.py.
# 3. VERIFY the deployed route matches disk: the WebUI route /art-3d-viewer
#    (in /workspace/hermes-webui/api/routes.py, search "art-3d-viewer") serves
#    the file LIVE from the workspace, so no rebuild needed there - but check
#    the served bytes match the on-disk file (size + a hash of the first 4KB).
#    If the route 404s or the running server hasn't picked up routes.py
#    changes, write /home/hermeswebui/.hermes/webui_restart_request (a host
#    guardian cron picks it up; NEVER run docker from inside the webui
#    container) and wait ~60s, then re-verify with curl http://localhost:8787.
# 4. VISION-QA the final result with vision_analyze on a fresh playwright
#    screenshot: figure should read as an upright cloaked hunter, no floating
#    shards, texture readable. Compare against the original screenshot
#    /home/hermeswebui/.hermes/webui/attachments/9749288e2741/AISelect_20260913_134813_Chrome-1.jpg
# 5. Commit + push everything to dev (viewer template + built html + any fixed
#    glbs), and append a row to art-direction/3d-spike/SPIKE-LOG.md describing
#    the defect, root cause, and fix.
#
# CONSTRAINTS:
# - Do NOT modify docs/planning/ except appending to SPIKE-LOG.md. dev branch only.
# - The WebUI server runs as root in this container; file modes must be 644 and
#   dirs 755 under art-direction/ or the route 403s.
# - python3 has trimesh/fast_simplification/scipy/matplotlib/PIL/playwright
#   installed. networkx may need a pip install.
# - Never run docker/compose from inside this container. Use the restart request
#   file mechanism described above for WebUI restarts.
# - The three.js bundle inside the viewer is r147 minified; edit only the page's
#   own <script> block (functions pixelFilter, equipTo, setBody, anchors), never
#   the bundle.
# - If Meshy re-submission is ever needed: driver is
#   art-direction/3d/meshy_driver.py, key is inside it, budget 10 credits max
#   this session (month resets on the 13th; today the Pro allowance is nearly
#   spent).
#
# FINAL DELIVERABLE: fixed viewer + fixed meshes pushed to dev, before/after
# screenshots compared, SPIKE-LOG row appended, and a summary of root cause(s)
# and what changed.