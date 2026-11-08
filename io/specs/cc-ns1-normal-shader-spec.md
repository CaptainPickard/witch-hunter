# CC-NS1 — Normal-Shader Spec for Kit GLBs (doc 61 P1-6 core half)

Status: IO spec of record, pre-Devbot. 2026-11-08 (wake 44), Autopilot.
Devbot = worktree child at /tmp/wh-worldfeat on feat/world-visuals. Children
NEVER commit or push. IO is the sole git gatekeeper
(identity CaptainPickard <pickard.nicko@gmail.com>).
Art anchors (law 1, vision-analyzed by IO this wake): concept-06-siege-council
+ day-06-council (faceted voxel-brush shading on steel/stone) + concept-04-tavern
(faceted wood grain, iron glints; "darks are not true black but saturated with
cool tones") + scene-01-bard-skeleton (smooth tarnished pewter metal law for
weapons). Shading law derived: smooth per-vertex normals + faceted-suggestive
textures, NOT hard flat-shading — the facets live in the texels, the smoothing
in the geometry.

## 1. Goal

Every GLB the game loads from art-direction/3d/assets/** (except the 2
untextured ok-fence-corner pieces) carries a NORMAL attribute, computed by the
repo's own weld+smooth law (art-direction/3d/add_normals.py algorithm), so
prepTemplate's computeVertexNormals() rebuild stops changing lighting between
the authored GLB and the boot-time geometry. This is the CORE half of doc 61
P1-6 "Consistent shading and texture style across asset families". Texture
re-generation (re-bake / re-download lanes [INF-L]) stays OUT of scope no
matter what the art provider does: those are visual-bake ops requiring
Nicko-visible A/B verdicts, not shader-consistency ops.

## 2. Frozen baseline (measured 2026-11-08 07:33Z, HEAD 9c0fd6c)

io/specs/cc-ns1-normal-census.json (committed this round) = authority. 80 GLB
files without NORMAL, indexed comp 5125 everywhere, POSITION float32 (5126)
with min/max everywhere, single-prim single-material (or no-material) every-
where. By family: church-kit 29, weapons 18, armor 16, graveyard 7,
biome_library 8 (6 in-family + raw/ + refs/), old_king 2,
plus biome_library raw/ and refs/ counts as given. 75 files are
mat+tex+tc (POSITION,TEXCOORD_0); 5 are nomat/textureless
(biome_library wh-bush-snare raw+refs+live, old_king ok-fence-corner
v2+v3 pixelated — POSITION only). The live runtime paths use the -pixelated
variants; the base/races variants are pipeline outputs and get the same fix
so the pipeline stays consistent (both variants of every kit asset are live
game assets once the pipeline re-runs them).

## 3. Hard constraints

1. ZERO engine-file edits. prototype/js/** (assets.js, game.js, region-
   manager.js, enemy.js, wh-ground.js), prototype/index.html, prototype/style.css,
   CONFIG.js: untouched. prepTemplate's computeVertexNormals() fallback stays.
2. NO visual re-bake: textures (the image buffer in each GLB), materials,
   UVs, texel content, geometry POSITIONS, and triangle topology byte-preserved
   except for the appended NORMAL buffer and the glTF JSON index/attribute edits
   (same edit shape add_normals.py already does for races).
3. Weld law verbatim from add_normals.py: weld tolerance 1e-4 (cKDTree
   query_pairs + union-find), per-vertex area-weighted normals from welded
   faces, normalize, un-weld back to original vertex order, float32 NORMAL
   accessor appended (VEC3, 5126, min/max written), attribute order
   POSITION, NORMAL, TEXCOORD_0 (TANGENT/COLOR_0 after if the file had them).
4. Scope = the 80 census files ONLY: art-direction/3d/assets/{church-kit,
   graveyard,crypt?,weapons,armor,biome_library,old_king}... (the census file
   is the exact list). No NEW files added, no files renamed, nothing deleted.
5. Determinism: same input file + same script version -> identical output
   bytes (hash twice, both equal). The script accepts a --verify mode:
   re-running on an already-normal'd file must DETECT NORMAL present and
   skip WITHOUT writing (no double-append, no re-encode).
6. Textures intact: for every processed GLB, sha256 of the image-buffer
   bytes (imageBufferViews window from the census, re-derived post-edit)
   must equal the census value even after byteOffset shifts from the JSON
   size change. Geometry positions unchanged: POSITION accessor byte count,
   count, and min/max must equal the census row.
7. Workdir /tmp/wh-worldfeat; scratch lives in scratch/ (census script +
   probe outputs there); scratch/ is NOT committed.
8. Node v22.22.3 IS on the box; `node --check` any touched .js — this round
   touches none, but if any js got touched by accident the round FAILS scope.
9. NO harness/browser runs (PRIMA: no HEADLESS BROWSER). Static + GLB
   forensics only. Nicko's playtest is the acceptance bar for the visuals;
   this round's hard gate is byte/attribute forensics + a real WebGL load in
   the 8793 serve AFTER IO flips (serving-health duty, not child work).
10. Report-first: write scratch/cc-ns1-impl-notes.md BEFORE touching GLBs,
    process in batches, overwrite the notes after each batch (per-batch
    rows: file, verts, welded verts, faces, ok).

## 4. Deliverables

- D1 art-direction/3d/add_normals_v2.py: the family-batch normalizer.
  Same weld+compute law as add_normals.py but: walks a directory TREE
  (default art-direction/3d/assets), processes EVERY file in the census
  (the 80), skips NORMAL-present files idempotently (--verify reports
  skipped vs processed); handles both mat+tex+tc and nomat/textureless
  files identically (normals are attribute-level, material-independent);
  preserves file mode 0644; writes the JSON batch log to the arg-out path
  (default scratch/ dir; NOT committed). Reuses (copy of) weld_vertices +
  the accessor-append logic from add_normals.py; the OLD add_normals.py
  file stays untouched for provenance.
- D2 the 80 GLBs re-written in place with NORMAL appended (per the law).
- D3 io/specs/cc-ns1-postbuild-census.json: same census script re-run;
  expected totalNoNormal = 0; every file's hasNORMAL=true; posCount/min/
  max/idxCompType unchanged; per-file texture-window sha256 equal to census
  (re-derive the window from the NEW bufferViews). Include the
  before/after glb byteSize and the NORMAL accessor byteLength per file in
  this artifact.
- D4 scratch/cc-ns1-impl-notes.md: per-batch table + anomalies + final
  totals (80 processed, 0 skipped pre-normal, verify-mode = 0 processed on
  re-run + 0 byte diffs).

## 5. Validation shape (Testerbot valspec, ordered BEFORE build)

V-1 census replay: re-run the census script logic at baseline HEAD on a
    pristine copy -> same 80-file set + identical sha256 values (crown
    proof = census file's own sha256 of each row re-computed).
V-2 post-build census: totalNoNormal=0; per-file NORMAL accessor present;
    VEC3/5126; count == POSITION count; min/max present; bounds ~[-1,1].
V-3 texture integrity: per-file image-buffer sha256 equals the census
    (window re-derived), 80/80.
V-4 geometry integrity: POSITION count/min/max equal per file, 80/80;
    index compType 5125 unchanged for all.
V-5 determinism: script on a copy = same output bytes for every file (or
    a 12-file sample if runtime forbids full re-run; the SAMPLE files are
    1 per family + the 3 smallest).
V-6 idempotence: --verify on processed tree reports 0 processed.
V-7 scope floor: git status --porcelain shows ONLY (a) 80 GLBs modified,
    (b) one NEW file art-direction/3d/add_normals_v2.py, (c) io/specs/
    cc-ns1-* files (+valspec/verdict). Nothing in prototype/js, CONFIG.js,
    index.html, style.css, docs/planning, tools/.
V-8 engine-file zero-diff proof: git diff --name-only vs 9c0fd6c excludes
    prototype/**, CONFIG.js, index.html/style.css.
V-9 loader-compat static check: no Draco/extension headers added (the glTF
    JSON asset/extensions keys must not grow); generator stays trimesh (or
    the JSON-rewriter's own generator string is preserved — state which
    per file class).
V-10 spot render-shape check (static): one file per family gets a
    normal-magnitude histogram (all ~1.0) + a "no zero-length normals"
    proof. No browser needed.
V-11 build health: tools/build_v8.py runs clean; bundle writes
    prototype/builds/v8-playable.html; bundle's inlined js files byte-match
    the prototype/js sources (build_v8 inlines whole files) — proves no
    latent js change rode in. Bundle committed BY IO AFTER the verdict (IO
    commit step), the valspec pins the commit-order (build from code-HEAD,
    then bundle commit).

## 6. Spec-vs-canon precedence

Doc 61 P1-6's texture-style bullet (choose one texture style, re-download
originals [INF-L]) stays OPEN and is EXPLICITLY not this round. If the
builder finds a real conflict with doc 61, STOP and file an amendment
request in its notes (the gate treats that as a healthy stop).
