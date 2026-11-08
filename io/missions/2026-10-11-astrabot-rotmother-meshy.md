# ASTRABOT DISPATCH · Rot Mother Meshy generation + intake bake (CC-C7 asset lane)

You are Astrabot (Claude Code print mode, cwd /tmp/wh-worldfeat, identity
CaptainPickard <pickard.nicko@gmail.com>). Asset lane brief from IO; Nicko
ordered 2026-10-11: "get astrabot to make a menacing female creature in
meshy for this" (the Rot Mother, doc 62 §5.2 / L3 lair). NO harness runs;
Blender/Python QA renders only; Nicko playtests the eventual game build.

## 0. STATE

- Worktree /tmp/wh-worldfeat @ c79b582 (C6C fires), branch
  feat/world-visuals, clean tree. DO NOT touch prototype/js/* — this is an
  ASSET-only brief.
- Meshy creds: API key at
  /home/hermeswebui/.hermes/profiles/io/secrets/meshy_key (Bearer).
  Endpoints: POST/GET https://api.meshy.ai/openapi/v2/text-to-3d (v2
  supports text prompts directly; v1 image-to-3d also available).
- CREDIT LAWS (binding, from the skill evidence bank):
  - 15 credits/asset flat. Serial cadence: submit ONE task → poll to
    SUCCEEDED → download → next submit (burst 400 rule).
  - 400 with empty body after a burst = rate window; back off minutes,
    retry cold. 402 = credits exhausted → STOP, report.
  - Polycount is advisory; ship the raw mesh as-is, record the count, do
    not decimate to force numbers (post-processing discipline: geometry
    edits are a declared, QA'd decision only).
  - thumbnail_url lives at task top-level, NOT in model_urls (model_urls
    = glb/fbx/usdz/obj/mtl/stl).
- Pipeline precedents to follow (read before writing scripts):
  - art-direction/3d/regen_pipeline_v3.py (v3 bake: mesh as-is, normals
    injected, 512px NEAREST + 5-bit pixelate; NOTE its exporter writes a
    20-byte short GLB header - the wolf round patched it post-export,
    check for that on every export and fix in place).
  - glb_attribute gate recipe (scratch/verify_wolf_rig.py + the intake
    probe from the wolf session): verify POSITION/NORMAL/TEXCOORD_0,
    counts equal, before declaring a bake good.
  - The wolf intake session (io/missions/2026-10-08-wolf-rig.md context
    and git log 69fbab4/fc01956/1a4e13c) shows the verify-gate house
    style - keep gate numbers in the report.

## 1. WHAT TO GENERATE

Generate via text-to-3d (v2): ONE creature asset, the Rot Mother:

Prompt sketch (craft to the ref-craft grammar of the skill: single
subject, connected geometry, no floating shards - adapt, do not copy
blindly; Meshy text-to-3d takes an art-style hint field):
- A bloated humanoid female swamp creature - "The Rot Mother": hunched,
  gaunt-armed, hugely distended belly, long spindly fingers, elongated
  neck, small sunken head, moss and fungus growths across the back and
  shoulders, tattered rot-green skin. Menacing, tragic, ancient. EXACTLY
  ONE character, standing in a neutral A-pose-like stance, facing forward.
- CONNECTED GEOMETRY ONLY: every part joined; NO detached fragments, no
  floating spores/particles; NO weapons; NO base/ground plane in the
  mesh (model only); NO cloth strips thin enough to shatter.
- The Meshy text prompts fail hard on multi-object + detached-bits: use
  the skill's fix language ('ONE continuous...', 'fusing directly into...',
  'no shards, no fragments, nothing detached').

TARGET: ONE raw GLB. Budget: at most THREE generation attempts
(~45 credits; the ref-failure law: fix the PROMPT between attempts, never
resubmit an un-modified prompt). If attempt 3 still fails QA, STOP,
report the failure modes + the evidence bank's verdict, and let IO/Nicko
decide (design change or accept defects).

## 2. INTAKE BAKE (after a PASS generation)

- Save raw: art-direction/3d/assets/races_regen/rotmother.glb (raw,
  byte-preserved; NEVER modified after download).
- Bake with the v3 pipeline (python, adapt the module's functions):
  art-direction/3d/assets/races/rotmother.glb (raw tex + normals) +
  art-direction/3d/assets/races/rotmother-pixelated.glb (512px 5-bit).
  If geometry-only (no UVs/materials - the grey-clay tell), apply the
  Round G fallback (flat 5-bit colour from a rot-green average + the
  standard metal/roughness) AND DISCLOSE it loudly in the report + name
  the retexture cost path.
- VERIFY GATE (numbered): vertex/tri counts, attribute presence
  (POSITION/NORMAL/TEXCOORD_0), counts equal, texture bytes round-trip,
  both files Blender-importable (fix the -20 header bug if v3 emits it;
  run the header self-check from the wolf round first).
- QA renders (headless Blender or the pure-software raster):
  THREE full-size angles (front/3-4/side). VISION QA (call the parent by
  writing a verdict file; the runner IO will vision-read it): form-only
  verdicts + kill-checks: floating fragments / melted blobs / holes
  bleeding background / wrong identity. The menacing-female read matters
  - report it plainly.
- Two commits: (1) raw + bake + gate numbers; (2) QA renders +
  verdict files. Author CaptainPickard; push origin feat/world-visuals
  after each. Commit subjects carry 'asset(rotmother)'.
- DO NOT wire the model into any game file (no CONFIG/enemy/manifest
  edits) - CC-C7 behavior order consumes it separately after Nicko sees
  the renders.

## 3. REPORT (final message)

Meshy task ids + consumed credits; prompt versions used per attempt; QA
verdicts per attempt (what failed and why); final asset file list +
sizes; the verify-gate numbers; render paths (full-size, 3 angles);
commit SHAs + push confirmations; watch-items for Nicko; ANY credit
errors (402/400) with the standing rule applied.