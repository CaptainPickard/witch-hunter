# Witch Hunter — wh-econ-spike1 (Sui TESTNET)

The ownership conflict and step-name conflict are resolved by spec amendments A1/A2: `WHItem` is **address-owned** (`key, store`) so it can enter a Kiosk; the Registry and TransferPolicy are shared. The result file has exactly seven `steps` (`mint`, `craft`, `serial`, `kiosk_list`, `kiosk_purchase`, `royalty`, `provenance`); CLI installation and publish belong in top-level `setup`.

## Current outcome (2026-09-30)

`/workspace/witch-hunter/sui/move/wh-items` builds and its **14 Move tests pass**. Live testnet publishing was attempted but **did not happen**: three faucet attempts left the deployer with zero MIST. `sui client publish . --json` failed gas selection (estimated budget 83,152,800 MIST). The TypeScript harness is **review-only on this VPS**, which has no Node; no e2e transaction was executed. `sui/ts/e2e_result.json` records all seven as `skipped_faucet` with null digests, not success. Package ID: **none (not published)**. A browser-based faucet attempt was blocked because no Chromium-family browser was running.

## Prerequisites and environment

- Linux/macOS with `curl`; Sui CLI for **testnet only**. Install with the official installer:

  ```sh
  curl -sSfL https://raw.githubusercontent.com/MystenLabs/suiup/main/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  suiup install sui
  suiup switch sui@testnet
  sui --version
  ```

  Installed here using official suiup `0.0.14`; exact CLI output: **`sui 1.81.0-bf0c491c17b8`**. The installer's home on this profile is `/home/hermeswebui/.hermes/profiles/io/home`; no global binary or repository secrets are required. `suiup switch sui@testnet` selects the installed testnet CLI. `sui client envs` should show testnet; use `sui client switch --env testnet` if needed.
- A **testnet-only, funded** mnemonic in `SUI_TESTNET_MNEMONIC`; never paste it into a script, README, git-tracked file, or a command-line argument. The second wallet is generated ephemerally and funded from this wallet with testnet SUI.
- A working legacy JSON faucet endpoint in `SUI_TESTNET_FAUCET_URL` (accepting `POST {"FixedAmountRequest":{"recipient":"..."}}`); **the historical `https://faucet.testnet.sui.io/gas` currently returns HTTP 404**. Alternatively fund the derived address manually at [the official browser faucet](https://faucet.sui.io/) before running. The harness checks for existing gas first, so it does not depend on that API when pre-funded. The CLI currently redirects to the web faucet. Three failed API attempts are recorded before the run is marked `skipped_faucet`.
- For executing the review-only harness elsewhere: Node >=20 and npm. **Node/npm are not installed or used on this VPS.**

  ```sh
  export SUI_TESTNET_MNEMONIC='<obtain securely from your testnet wallet, do not save here>'
  export SUI_TESTNET_FAUCET_URL='<working testnet-only JSON faucet URL>'
  ```

  The angle-bracket strings above are placeholders, not credentials. To learn the wallet address, derive it off-box using the same mnemonic; fund it on testnet with the browser faucet or a compatible API. Do not use mainnet keys or mainnet funds.

## Build, test and run

From the repo root `/workspace/witch-hunter`:

```sh
cd sui/move/wh-items
sui move build --warnings-are-errors
sui move test --warnings-are-errors
```

Expected output: successful build; `Test result: OK. Total tests: 14; passed: 14; failed: 0`. Sui 1.81 prints **`Total number of linter warnings suppressed: 1`** for the narrowly scoped `share_owned` suppression in `market.move` (sharing the framework-owned TransferPolicy freshly returned by `transfer_policy::new` in publish init). This is a real compiler output line and may fail an automated “zero *warning* strings” check even though `--warnings-are-errors` exits zero. No other compiler warnings were observed.

On a **Node-enabled machine**, from the repo root (with the above environment variables set and Sui CLI on PATH):

```sh
cd sui/ts
npm ci
npm run check
npm run e2e
```

The harness compiles `../move/wh-items`, publishes it **immutably** by consuming the publish result in `0x2::package::make_immutable` in the same programmable transaction, mints two weapon materials, attempts a deterministic UI timing-band input with an on-chain `sui::random` roll (up to five genuine craft attempts, minting new inputs after failed rolls), reads serial and lineage from the item, creates seller and buyer Kiosks, lists the item, purchases into the buyer Kiosk, and reads the 5% royalty from TransferPolicy. No third-party marketplace is contacted. The e2e runtime has not been exercised on this host; the SDK path is review-only until run on a Node-enabled machine. `package-lock.json` was generated from npm registry integrity metadata without running Node on this VPS; regenerate/check it with `npm install --package-lock-only` on the Node-enabled machine if npm rejects it.

Expected: `sui/ts/e2e_result.json` contains:

```json
{
  "setup": {
    "network": "testnet",
    "cli_version": "sui 1.81.0-bf0c491c17b8",
    "install_method": "official suiup",
    "package_id": "0x... or null if unfunded",
    "publish_digest": "64-hex or null if unfunded",
    "faucet_attempts": []
  },
  "steps": {
    "mint": { "ok": false, "status": "skipped_faucet", "digest": null },
    "craft": { "ok": false, "status": "skipped_faucet", "digest": null },
    "serial": { "ok": false, "status": "skipped_faucet", "digest": null },
    "kiosk_list": { "ok": false, "status": "skipped_faucet", "digest": null },
    "kiosk_purchase": { "ok": false, "status": "skipped_faucet", "digest": null },
    "royalty": { "ok": false, "status": "skipped_faucet", "digest": null },
    "provenance": { "ok": false, "status": "skipped_faucet", "digest": null }
  }
}
```

When funded, each completed step has `ok: true`, `status: "ok"`, and a **real** 64-character lowercase hex representation of the transaction's 32-byte Sui base58 digest; `sui_digest` retains the native base58 value. Some assertions share a transaction digest (e.g. craft/serial/provenance and purchase/royalty). Publish digest and package ID are in top-level `setup`, not extra step names. If the faucet fails after three attempts, **all seven** have `ok: false`, `status: "skipped_faucet"`, `digest: null`; no fake IDs/digests. A non-faucet transaction error is recorded as `status: "failed"` rather than silently relabeled skipped. The current result is the unfunded case, not evidence of a testnet publish.

## Implementation notes

- `items.move`: address-owned WHItem, owned Material, shared per-family serial Registry created at package initialization, deployer MintCap, immutable-at-mint item fields, burn and salvage events; salvage destroys an item and returns one provenance-linked material (no coin refund).
- `craft.move`: private entry with shared Registry and Sui Random singleton; failure threshold `20 - floor(timing_band/10)`; affix probability rises with timing band and never reaches certainty. On failure exactly one of at least two materials is consumed; the rest return to the crafter. Successful recipes consume all material IDs and preserve ancestor IDs in lineage. Randomness call is the final PTB move call; do not compose calls after it. The test-only deterministic roll helper is isolated from the entry point.
- `market.move`: five per-family metadata display objects plus standard `Display<WHItem>` template with `name`, `description`, `image_url`, `attributes`; shared TransferPolicy with custom `RoyaltyRule` at **500 basis points = 5%** and `DecorLockRule`. Decor and optionally high-value items enter a Kiosk via `lock`; purchased Decor remains locked in the buyer's Kiosk. Buyer supplies the exact price and a separate 5% royalty coin; policy balance accrues the royalty. No UpgradeCap is retained.
- `tests/economy_tests.move`: 14 passing unit tests, including simulated e2e using identical roll math and a kiosk purchase/royalty round-trip. TS/runtime checks are **not** asserted as passed.
- CLI: installed with official suiup installer (`suiup 0.0.14`), `suiup install sui`, `suiup switch sui@testnet`; `sui 1.81.0-bf0c491c17b8`. Published package ID **null** because faucet funding failed; no upgrade cap published/retained.

## What this spike proves / does not prove

**Proves locally:** Move compiles and its 14 tests validate roll math, material sink, serials, lineage, burn/salvage, Display metadata, Kiosk list/purchase, locked decor, and the policy's 5% royalty distribution in simulation. The code is scoped to `sui/**` and does not touch the parallel prototype/planning work.

**Does not prove yet:** live testnet execution, real marketplace liquidity, TS SDK compatibility at runtime, battle balance, any mainnet safety guarantees, anti-bot policy, production URLs/images, or sustainable token economics. A successful green live report requires a funded testnet account and executing `npm run e2e` off this VPS; the present `skipped_faucet` result must not be reported as a live success.
