# Devbot Implementation Spec — wh-econ-spike1 (Sui testnet crafting-economy spike)

Spec ID: wh-econ-spike1
Date: 2026-09-30
Author: IO
Status: ACTIVE
Gate: Testerbot validation spec FIRST (reads this), then Devbot implements, Testerbot validates, IO commits.
Project: Witch Hunter on-chain crafting economy (concept brief: Obsidian vault commit f2c53b6).

## Context (Nicko-locked, do not amend)

Locked decisions: all items tradeable incl. power; crafting-is-the-game; paid=deterministic, random rolls earned-only; camp decor first-class; items immutable on mint; provenance+serials on-chain; skill-influenced timing shifts probability bands, never guarantees; single-player + async market.

## Objective

A WORKING Sui testnet spike proving the full item loop end-to-end: material mint → craft (provably-fair `sui::random` roll with skill-timing band input) → serial+provenance on item → Kiosk list → purchase → royalty to the policy publisher. Deliverable is code + a live testnet demonstration; this spike informs the full economy spec (wh-econ1) that follows.

## Repo layout

- repo root: /workspace/witch-hunter, branch dev, starting HEAD 2fa6b15, tree clean.
- spike dir: sui/ (NEW — all spike code lives here; do NOT touch prototype/, tests/, docs/, art-direction/, io/ other than adding the validation-spec file you are told to add in the implementation notes)
- Move package: sui/move/wh-items/ (Move.toml + sources + tests)
- TS harness: sui/ts/ (package.json; @mysten/sui + @mysten/dapp-kit or raw sdk + @mysten/zkbuild-crypto NOT NEEDED)
- docs: sui/README.md (how to run the harness end-to-end, env setup required, exact commands, expected outputs)
- The spike runs against Sui TESTNET only. No mainnet package publish, no funds moves, no third-party marketplace listing.

## Deliverables

1. sui/move/wh-items: Move package with
   a. WHItem: address-owned object type (`key, store`), transferred to the crafter on mint (AMENDMENT A1 2026-09-30: original "shared-owned WHItem" was a spec error — a shared object cannot be placed into an owner's Kiosk; per Devbot amendment request sui/README.md. Fields unchanged): family (weapon/armor/potion/charm/decor), base_item, rarity_bands, affix_id, affix_stats, serial (u64), crafter_addr, lineage (crafted-from ids), created_epoch, name, display_meta pointer
   a2. Registry + TransferPolicy are shared objects created at publish (AMENDMENT A1: shared at registry/policy layer only, items stay address-owned)
   b. Material object types (family-tagged), consumable in craft
   c. craft module: entry fun for craft(recipe: String, mats: vector<Material>, timing_band: u8) — timing band 0-100 input from client; maps to band multipliers on affix probability (documented constant curve), never guarantees, still rolls via sui::random. PTB composition-attack protection documented in-module (private entry + no post-random commands in PTB patterns per docs.sui.io/guides/developer/accuracy/randomness-onchain)
   d. serial allocation via a shared Registry object (monotonic per family)
 Registry created at publish with TreasuryCap-like authority retained by deployer.
   e. Kiosk listing helper: place item into owner kiosk, set price in SUI, TransferPolicy with RoyaltyRule (5% default) + lock rule for Family::Decor items. Lockable for high-value items.
   f. Display object per family with name/description/image_url/attributes keys
   g. craft-failure path: probability bands include failure band → materials partially consumed (sink), no item.
   h. Move unit tests (sui move test) covering: craft success band, failure band, timing-band multipliers monotonicity, serial monotonicity, royalty rule present, kiosk list+purchase round trip, provenance chain growth.
2. sui/ts: TypeScript harness (no browser) that drives the loop:
   a. Env: SUI_TESTNET_MNEMONIC (or keypair file) + SUI_TESTNET_FAUCET_URL. Harness generates wallet, funds via testnet faucet, publishes package to testnet, mints materials, crafts (with timing band from a deterministic pseudo-timing function), lists in kiosk, purchases from second wallet, asserts royalty distribution, then prints a machine-readable JSON summary
   e2e_result.json with per-step booleans + tx digests.
   b. e2e_result.json step names must be exactly: mint, craft, serial, kiosk_list, kiosk_purchase, royalty, provenance (AMENDMENT A2 2026-09-30: the seven step keys in both specs are the contract of record; any dispatch text using different labels (cli_install etc.) is superseded — CLI install and package publish are recorded in top-level `setup` metadata, not as steps.)
   3. sui/README.md: prereqs (suiup install steps, Sui CLI version), env setup, faucet funding, run commands, expected outputs, and a "what this spike proves/does not prove" section.
4. sui/ts/package.json + lockfile committed; node modules NOT committed.

## Tooling provisioning (spike includes it)

- If sui CLI is absent: install via official suiup (curl -sSf https://raw.githubusercontent.com/MystenLabs/suiup/main/install.sh | sh), then `suiup install sui` and add ~/.local/bin to PATH. Note in implementation notes the version installed (record exact `sui --version`).

## Constraints

- TESTNET ONLY. Faucet-funded addresses. No real funds. No mainnet publish.
- Do NOT modify prototype/, tests/, docs/, tools/, art-direction/. All spike work isolatable in sui/ + io/specs (validation spec only).
- Node is NOT available on the VPS. TS harness is written and syntax-checked via Playwright (validate via tests/util/playwright-validate.mjs or the established Playwright headless pattern), NOT run with node here; the spec VALIDATION must not require running the TS harness in this environment — instead: (a) sui move build + sui move test must pass locally, ( Move unit tests must include a "simulated e2e" test that exercises the same roll math in Move, proving the roll math; the TS harness remains a mainnet-readiness artifact validated by code review only at this stage.
- Keep the Move package small: no token economics, no auction house, no auction module, no DAO, just items+craft+kiosk+royalty.

## Move code quality bar

- No `public` functions with Random/RandomGenerator args (compiler-enforced anyway), craft as private entry with timing_band: u8 param, per docs.sui.io randomness-onchain guidance.
- No upgrades planned; publish as immutable, versioned package; do not use upgrade caps in the spike.
- Include a `burn/salvage` entry (burns item object, emits event) as the deflationary sink demo (no coin return in spike).

## Acceptance criteria

AC-1: `sui move build` succeeds in sui/move/wh-items with zero warnings-as-errors enabled strictness equivalent.
AC-2: `sui move test` all-green, >=10 dedicated tests, incl. the 8 listed behaviors.
AC-3: sui/README.md documents the exact e2e flow with exact commands and expected e2e_result.json shape.
AC-4: e2e_result.json step names exactly the 7 steps, machine-checkable booleans per step + digests.
AC-5: royalty rule at 5% default, in Move as RoyaltyRule, unit test proves rule present + distribution flow in kiosk purchase simulation.
AC-6: serial numbers monotonic per family, tested.
AC-7: craft-failure band exists and materials partially consumed (sink demo), tested.
AC-8: timing band multipliers monotonic (higher band → weakly better odds), tested.
AC-9: provenance chain: item lineage records input material ids; tested.
AC-10: tree hygiene: only sui/** plus io/specs/testerbot-spec-wh-econ-spike1.md (Testerbot's file) plus this spec file exist as changes vs. starting HEAD 2fa6b15; prototype/, tests/, docs/, tools/, art-direction/ untouched (git diff --stat proves it).
AC-11: no node run required this environment: TS harness validated by review + syntax check only; Move-side simulated e2e test proves roll math (per Constraints).
AC-12: sui/ records the installed Sui CLI version in implementation notes; no upgrade caps included; package published immutable.

## Implementation notes (Devbot returns these)

- Exact `sui --version` installed and install method.
- Package ID after testnet publish.
- Per-step e2e_result.json content (booleans + digests).
- Any suiup/faucet issues encountered and workarounds.
- Confirmation that nothing outside sui/ + io/specs changed.

## Validation-spec note (Testerbot reads this section)

Freeze baseline: `git -c core.fsmonitor=false -c core.untrackedCache=false status --porcelain` empty at HEAD 2fa6b15 (measured 2026-09-30). Validation scope: AC-1..AC-12 as above; secrets-grep on sui/ with positive control OUTSIDE the repo; verdict JSON per-AC with file:line evidence; suite floor = the 10+ Move tests enumerated at implementation start. Watch-item: this VPS has no node; do not fail the build for TS-runtime-inability, review-only per AC-11. Watch-item: faucet availability is flaky from VPS IPs; if the testnet faucet is unreachable after 3 documented retries, mark mint/craft steps as `skipped_faucet` in e2e_result.json rather than failing the environment — the Move test suite remains the hard gate.