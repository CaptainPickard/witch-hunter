# Witch Hunter Sprite Pipeline Tools

The scripted stages of the art production pipeline (25-art-pipeline.md),
as used in the gravedigger-undead pilot (art-direction/sprites/gravedigger/).

## Scripts

- alpha_extract.py - S5a: chroma-key alpha extraction (corner-sampled
  background color, tolerance matte, bbox crop).
- defringe.py - S5b: median-filter defringe + alpha hardening; removes
  background halos after keying.
- atlas_pack.py - S5c: normalize frames to 512px canvas (feet anchored)
  and pack a horizontal atlas sheet.
- qa_gate.py - S6: scripted QA (adjacent-frame flicker diff, silhouette
  coverage at 25 percent, accent hue census). Vision QA (gemma4:31b via
  ollama cloud) runs alongside this for register conformance; see
  docs/planning/24-art-bible.md section 7.

## Pipeline order

1. S1-S4 are generation stages (image model + art bible prompt grammar,
   docs/planning/24-art-bible.md section 4). Human gate after turnaround.
2. S5: alpha_extract.py -> defringe.py -> atlas_pack.py
3. S6: qa_gate.py + vision QA -> human gate
4. S7: atlas -> engine (Unreal flipbook billboard, or the JS prototype
   pattern in art-direction/sprites/gravedigger/pilot-billboard.html).

## Production notes (from the pilot)

- rembg was attempted for S5a but its model download killed the host;
  chroma-key + defringe is the proven fallback. Revisit rembg with the
  model pre-cached.
- Identity drift across separately generated directional views is real;
  named characters need per-character adapter training (LoRA), see
  25-art-pipeline.md section 5.
- Idle animation frames must derive image-to-image from ONE source view.
