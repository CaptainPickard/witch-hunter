# Witch Hunter 3D Asset Manifest

Production run 2026-09-13. Pipeline per SPIKE-LOG: concept ref (image-gen,
vision QA gate) -> commit+host -> Meshy image-to-3d (meshy-5, quad, symmetry
auto, 15 credits each) -> UV-preserving decimation to tri target -> pixelated
register re-texture pass (256px / 48-color MEDIANCUT / 5-bit posterize).
All GLBs: raw + pixelated under art-direction/3d/assets/<category>/.
Viewer: art-direction/3d/arsenal-viewer.html (self-contained, equip slots).

TOTALS: 46 assets, all SUCCEEDED, 0 rejected by vision QA (0 regen rounds),
690 credits consumed of the 700 cap.

| asset | category | tri target | tri actual | credits | meshy task id | status | vision-QA |
|---|---|---|---|---|---|---|---|
| longsword | weapons | 2000 | 1999 | 15 | 01a09c09-70f1-73c5-9dfe-3956d00c211e | SUCCEEDED | PASS |
| greatsword | weapons | 2000 | 2000 | 15 | 01a09c09-7891-73e2-8327-e2127d1074a8 | SUCCEEDED | PASS |
| hand-axe | weapons | 2000 | 1999 | 15 | 01a09c09-80eb-7300-a84e-d770bf2aab64 | SUCCEEDED | PASS |
| war-mace | weapons | 2000 | 2000 | 15 | 01a09c09-88b4-71c7-94d4-e940c54c4d87 | SUCCEEDED | PASS |
| halberd | weapons | 2000 | 2000 | 15 | 01a09c0a-5c01-72d4-9099-3c1efa80963d | SUCCEEDED | PASS |
| dagger | weapons | 2000 | 2000 | 15 | 01a09c0a-643e-71ff-983e-a714996fc984 | SUCCEEDED | PASS |
| hunting-bow | weapons | 2000 | 2000 | 15 | 01a09c0a-6db7-76a7-96f4-2adf5afa040d | SUCCEEDED | PASS |
| round-shield | weapons | 2000 | 2000 | 15 | 01a09c0a-7683-7113-bd59-806f0a972e5c | SUCCEEDED | PASS |
| gravedigger-lantern | weapons | 2000 | 2000 | 15 | 01a09c0b-774e-747e-9632-90373025108b | SUCCEEDED | PASS |
| light-court-helm | armor | 3000 | 2999 | 15 | 01a09c0b-8007-70bd-a829-7100d12637e1 | SUCCEEDED | PASS |
| light-court-chest | armor | 5000 | 5000 | 15 | 01a09c0e-323b-74ec-89bd-e3fcab020e44 | SUCCEEDED | PASS |
| dark-court-helm | armor | 3000 | 3000 | 15 | 01a09c0f-3cda-7114-ba99-d2a8829795b7 | SUCCEEDED | PASS |
| dark-court-breastplate | armor | 5000 | 4999 | 15 | 01a09c0f-ba7e-73ac-ae09-f4b73bf8eb84 | SUCCEEDED | PASS |
| shadow-court-hood | armor | 3000 | 2999 | 15 | 01a09c10-fc65-74db-8eed-40ba02fbd998 | SUCCEEDED | PASS |
| undead-husk-armor | armor | 5000 | 5000 | 15 | 01a09c11-8cec-76a8-8d99-56302a2c9411 | SUCCEEDED | PASS |
| tower-shield | armor | 3000 | 2999 | 15 | 01a09c12-1e47-74e1-bc3d-0b658dfe3e65 | SUCCEEDED | PASS |
| buckler | armor | 3000 | 3000 | 15 | 01a09c12-b0d8-7620-82d5-e0eb3a0163b1 | SUCCEEDED | PASS |
| human-hunter-male | races | 15000 | 14999 | 15 | 01a09bbb-bbd0-717a-a5a2-499a43a0fc7d | SUCCEEDED | PASS |
| human-hunter-female | races | 15000 | 14999 | 15 | 01a09bbc-7219-70d1-9397-594987a37a8e | SUCCEEDED | PASS |
| orc-male-warrior | races | 15000 | 15000 | 15 | 01a09c15-b7df-722b-b9ac-c5cb4309f4ab | SUCCEEDED | PASS |
| orc-female | races | 15000 | 15000 | 15 | 01a09c15-c91d-7750-ab66-400a786445be | SUCCEEDED | PASS |
| undead-ghoul-male | races | 15000 | 14999 | 15 | 01a09c16-8e46-75d2-90a1-1df4bddaec03 | SUCCEEDED | PASS |
| vampire-male-noble | races | 15000 | 14999 | 15 | 01a09c16-a0f8-7772-899d-a397c487bb82 | SUCCEEDED | PASS |
| vampire-female | races | 15000 | 15000 | 15 | 01a09c17-72e9-77a2-8003-001839e143e4 | SUCCEEDED | PASS |
| elf-dawn-refuser-male | races | 15000 | 14999 | 15 | 01a09c17-854d-7120-b186-133c103df973 | SUCCEEDED | PASS |
| dwarf-male-smith | races | 15000 | 14999 | 15 | 01a09c18-4dd5-734d-8423-4577a3ed6daa | SUCCEEDED | PASS |
| dwarf-female | races | 15000 | 15000 | 15 | 01a09c18-5f9d-77f4-91b1-13ad77039609 | SUCCEEDED | PASS |
| church-wall-window | church-kit | 2000 | 2000 | 15 | 01a09c19-41d9-71ed-96b6-aaf8993f4af4 | SUCCEEDED | PASS |
| church-corner-buttress | church-kit | 2000 | 2000 | 15 | 01a09c19-537f-717e-bec8-61f31bc1ca8e | SUCCEEDED | PASS |
| church-archway | church-kit | 2000 | 2000 | 15 | 01a09c19-668c-7567-bf6c-7a708458d9e1 | SUCCEEDED | PASS |
| church-roof-beam | church-kit | 2000 | 2000 | 15 | 01a09c1a-6587-70ee-9db2-cbbf0a53e65f | SUCCEEDED | PASS |
| church-window-frame | church-kit | 2000 | 2000 | 15 | 01a09c1a-79b6-771a-8f6e-25541c620ca5 | SUCCEEDED | PASS |
| church-altar | church-kit | 2000 | 1999 | 15 | 01a09c1a-8cae-752c-bd69-bb6b647e753e | SUCCEEDED | PASS |
| church-pulpit | church-kit | 2000 | 2000 | 15 | 01a09c1a-a0b0-75a3-abe4-a382e04c8feb | SUCCEEDED | PASS |
| church-pew | church-kit | 2000 | 1999 | 15 | 01a09c1b-77d0-736c-828a-187687bdc402 | SUCCEEDED | PASS |
| church-pew-broken | church-kit | 2000 | 2000 | 15 | 01a09c1b-8971-70d0-afb0-5f4682e597bc | SUCCEEDED | PASS |
| candelabra | church-kit | 2000 | 1999 | 15 | 01a09c1d-0b6c-71f2-b4f9-179dc822a05f | SUCCEEDED | PASS |
| lantern-post | church-kit | 2000 | 2000 | 15 | 01a09c1e-fea6-71f1-968f-e1da4804e047 | SUCCEEDED | PASS |
| rubble-pile | church-kit | 2000 | 2000 | 15 | 01a09c20-1313-7386-87e4-6db63e550944 | SUCCEEDED | PASS |
| dead-tree | church-kit | 2000 | 2000 | 15 | 01a09c20-295e-75fb-9b93-88e8e5e7769d | SUCCEEDED | PASS |
| iron-fence-section | church-kit | 2000 | 1999 | 15 | 01a09c20-3b26-76f3-b20a-0aee17d8c88b | SUCCEEDED | PASS |
| iron-fence-corner | church-kit | 2000 | 2000 | 15 | 01a09c20-4da9-7396-8513-96507edbb945 | SUCCEEDED | PASS |
| gravestone-obelisk | graveyard | 2000 | 2000 | 15 | 01a09c21-3037-73e5-ad2d-56707bda49d3 | SUCCEEDED | PASS |
| stone-cross-tilted | graveyard | 2000 | 2000 | 15 | 01a09c21-4087-70f2-bf0b-2962c081201f | SUCCEEDED | PASS |
| grave-mound | graveyard | 2000 | 2000 | 15 | 01a09c21-52db-748c-a563-1675dcb4942a | SUCCEEDED | PASS |
| buried-coffin | graveyard | 2000 | 2000 | 15 | 01a09c21-62ab-7792-a033-3577b0bc9545 | SUCCEEDED | PASS |

## Assumptions logged (per run instructions)

- Lantern GLB was processed under task name "lantern" and renamed to
  gravedigger-lantern (manifest item 9); task id 01a09c0b-774e-747e-9632-90373025108b.
- Meshy rate-limited concurrent submits (~1/min after burst); handled with
  backoff, no task lost. No assets skipped, no regeneration rounds needed.
- Tri targets hit exactly via UV-preserving decimation (fast-simplification +
  nearest-neighbor UV resampling); counts 1999-15000, all within target.
- Equip anchor positions in the viewer are measured from the human-hunter-male
  mesh (head top y=1.0 local, hands x=+-0.47 y=0.02 z=0.14) and shared across
  bodies at the normalized 1.8-unit scale; per-body sockets remain a rig-stage task.

