# 30 - Remote UE5 Pipeline: IO on the VPS, Editor on Nicko's PC

Status: PROPOSED pipeline, chartered 2026-09-13 (Nicko request). This is
the operating manual for IO/Devbot building UE5 assets and scenes from
the VPS while the editor runs on Nicko's PC. Nothing here requires
opening router ports; the whole thing rides the existing Tailscale mesh
plus GitHub.

## The shape of the problem

- IO (Hermes, all worker profiles) lives on the VPS container. No GPU,
  no UE5, no Docker-in-container. IO must never run UE5 locally.
- UE5 needs Nicko's PC (GPU, Windows). Nicko should not have to
  hand-drive the editor for every asset; he plays director/OTRO.
- The bridge must let IO: (a) ship assets to the PC, (b) execute
  Python inside the running editor, (c) see results (screenshots,
  logs), (d) commit everything back through git.

## Architecture (three planes)

```
VPS (IO/Devbot)                     Nicko PC (Windows, UE5)
+------------------------+          +----------------------------------+
| asset gen (Meshy API)  |          | UE5 editor (open, project loaded)|
| pixel re-texture (PIL) |          |  - Python Editor Script Plugin   |
| git: witch-hunter repo |<-GitHub->|  - Remote Control API plugin     |
| MCP client (native)    |          |  - Remote Control HTTP :30010    |
+-----------+------------+          |  - tailscale up                  |
            |  Tailscale HTTP :30010|  - (opt) OpenSSH server          |
            +---------------------->+  - git pull of repo              |
                                     +----------------------------------+
```

1. DATA PLANE = GitHub. All 3D assets (GLB), textures, and docs commit
   to the witch-hunter repo on dev, exactly as today. The PC pulls.
2. CONTROL PLANE = Tailscale + UE Remote Control API. The editor runs
   an HTTP server on port 30010. Over Tailscale, the VPS reaches it at
   http://<pc-tailscale-name>:30010. In-editor Python executes
   remotely: import assets, spawn actors, place kit pieces, set
   lighting, capture screenshots.
3. VERIFICATION PLANE = screenshots back to IO. Two options, pick per
   setup: (a) PC pushes captured shots to a renders/ branch of the
   repo, IO reviews on the VPS; (b) OpenSSH on the PC and IO scp/sftp
   pulls the shots directly over Tailscale.

## Software: what exists (researched 2026-09-13)

- FIRST-PARTY: Unreal 5.8 ships native MCP support in the editor
  (dev.epicgames.com, "Unreal MCP in Unreal Editor"). If the project
  lands on 5.8+, evaluate it before third-party tools.
- THIRD-PARTY MCP servers (all drive the editor via Epic's own
  Python/Remote Control plugins, no custom C++ to compile):
  - FFZackFair92/unreal-engine-mcp: fullest lifecycle (create project,
    import, level/Blueprint building, PIE, packaging). Explicit
    remote-machine support: UE_MCP_TRANSPORT=remotecontrol with
    UE_MCP_HOST pointing at the PC's Tailscale IP. Local-layer ops
    (launch editor, UBT, RunUAT) want a helper on the PC.
  - EpicLolia/UnrealPythonMCP: run_python_code / run_python_file over
    Python Remote Execution (UDP multicast + TCP). Multicast does not
    cross subnets; needs a Tailscale-friendly mode or local runner.
  - groscy/unreal-mcp: UE_CONNECT_MODE=direct (unicast) path works
    against stock PythonScriptPlugin with no UE-side changes.
- COMMON REQUIREMENT (all of them): editor running, Python Editor
  Script Plugin enabled, Remote Execution enabled, and for the HTTP
  path the Remote Control API plugin with DefaultRemoteControl.ini
  configured (bAutoStartWebServer, bEnableRemotePythonExecution,
  port 30010).

## Decision: recommended configuration

RECOMMENDED: FFZackFair92/unreal-engine-mcp running on the VPS under
IO's native MCP client (config.yaml), transport = remotecontrol, host =
Nicko PC's Tailscale address. Rationale: no stdio distance problem, no
multicast problems, HTTP survives the mesh, and it covers the most
lifecycle without PC-side daemons. If UE version ends up 5.8+, audit
Epic's first-party MCP as a possible replacement.

FALLBACKS: if MCP tooling proves flaky, the same control plane works
with plain curl against the Remote Control HTTP API (ExecutePythonCommandEx),
or the gravedigger-simple path: IO prepares Python import/build scripts
in the repo, PC pulls and runs them in-editor with two clicks
(Tools > Execute Python Script). Automated where possible, scripted-
manual as floor.

## Nicko PC setup checklist (one-time)

1. Install UE5 (version TBD, 5.8+ preferred), Tailscale, git.
2. Clone CaptainPickard/witch-hunter (dev) to a fixed path.
3. In the project: enable Python Editor Script Plugin + Remote Control
   API; enable Enable Remote Execution (Python settings).
4. Config/DefaultRemoteControl.ini per the MCP server's SECURITY.md:
   web server autostart on :30010, bEnableRemotePythonExecution=True,
   CustomAllowedRemoteFunctionCalls gated to PythonScriptLibrary,
   bAllowAnyRemoteFunctionCall=False, console-command gate OFF.
5. Bind the web server to the Tailscale interface (or 0.0.0.0 and let
   Windows Firewall restrict to the Tailscale subnet).
6. Optional but recommended: Windows OpenSSH server for the process
   layer (launching editor remotely, RunUAT cooks) and direct file
   pulls of screenshots.
7. Keep the editor open when an IO work session is expected. (The
   Remote Control API only talks to a RUNNING editor.)

## The asset -> scene -> review loop (how IO works)

1. IO generates/finishes an asset on the VPS exactly as in the spike
   (concept frame -> Meshy -> pixel re-texture pass), commits the GLB
   to dev, pushes.
2. IO calls the UE MCP: run_python_file with a repo script
   (ue/import_asset.py) that pulls latest, runs an AssetImportTask for
   the new GLBs into /Game/Assets/<kit>, applies the pixel material
   function, reports asset paths back.
3. IO calls run_python_file (ue/build_scene.py) with a scene manifest
   (JSON in the repo: piece, transform, lighting state) to place kit
   instances, set the mood lighting, fog state.
4. IO captures verification: editor Python HighResShot to
   <project>/Saved/Renders/<name>.png, PC pushes to renders/ branch
   (or IO scp-pulls). IO reviews the shot with vision QA against the
   concept frames, the same QA loop as the 2D pipeline.
5. IO commits scene manifests + renders back; Nicko reviews in his
   editor at his leisure and plays director by comment.

## Security notes

- Remote Control listens and executes Python = arbitrary code on the
  PC. Restrict to the Tailscale interface, keep the function-call
  gates ON (allow-list), console-command gate OFF, and treat the PC as
  reachable-by-IO only. This matches the existing threat model
  (VPS and Nicko endpoints share a Tailscale mesh).
- The Meshy key and GitHub token stay on the VPS; the PC never needs
  them (it pulls via existing git auth).

## Phased adoption

- PHASE 0 (manual proof, ~1 evening): Nicko opens UE5 on his PC with a
  blank project, enables the two plugins, confirms http://localhost:
  30010/remote/info answers locally. IO curls the same URL over
  Tailscale. That single curl IS the pipeline working end to end.
- PHASE 1 (import automation): IO ships the gravedigger + helmet +
  gravestone GLBs from the spike through the MCP import script; shot
  comes back; compare against the Three.js demos.
- PHASE 2 (register in-engine): build the shared pixel Material
  Function + post-process volume (low-res render, point sample,
  ordered dither, grain) and lock the mood-lighting blueprint. This
  closes doc 29's "register survival" criterion in the real engine.
- PHASE 3 (scene building): kit-based graveyard scene from a manifest,
  doc 28 camera registers, night + Pale Tide fog state, readability
  floor numbers measured (doc 24 bake-in).
- PHASE 4 (loop hardening): auto-pull on push (PC-side git hook or
  scheduled task), render queue, per-shot vision QA reports into doc
  29's memo automatically.

## Open items

- UE version decision (drives first-party MCP vs community MCP).
- PC hardware check vs UE5 requirements (GPU/VRAM/RAM).
- Who owns Windows-side upkeep (Nicko, ~zero-touch after setup).
- Decide repo layout for the UE project (separate repo recommended:
  witch-hunter-ue, LFS for binaries; planning docs stay here).