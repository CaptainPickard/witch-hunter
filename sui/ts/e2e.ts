// TESTNET ONLY. Review-only on the VPS (Node is unavailable there).
// Never write mnemonic/keypair material to disk or to the result JSON.
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { fromBase58 } from '@mysten/bcs';
import { SuiClient, getFullnodeUrl } from '@mysten/sui/client';
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { Transaction } from '@mysten/sui/transactions';

const dir = dirname(fileURLToPath(import.meta.url));
const output = resolve(dir, 'e2e_result.json');
const pkgDir = resolve(dir, '../move/wh-items');
const rpc = new SuiClient({ url: getFullnodeUrl('testnet') });
const names = ['mint', 'craft', 'serial', 'kiosk_list', 'kiosk_purchase', 'royalty', 'provenance'] as const;
type Step = typeof names[number];
type Result = { setup: Record<string, unknown>; steps: Record<Step, {
  ok: boolean; status: 'ok' | 'skipped_faucet' | 'failed'; digest: string | null; sui_digest?: string; detail?: string;
}> };
const initial = Object.fromEntries(names.map(name => [name, { ok: false, status: 'skipped_faucet', digest: null }])) as Result['steps'];
const result: Result = {
  setup: { network: 'testnet', cli_version: null, install_method: 'official suiup',
    package_id: null, publish_digest: null, publish_sui_digest: null,
    faucet_url: process.env.SUI_TESTNET_FAUCET_URL ?? null, faucet_attempts: [], craft_retries: [],
    runner: 'TypeScript SDK; never run on the VPS without Node' },
  steps: initial,
};
function flush() { writeFileSync(output, JSON.stringify(result, null, 2) + '\n', { mode: 0o600 }); }
function mark(name: Step, digest: string, detail?: string) {
  // Native Sui digests are base58; the validation contract uses their 32-byte hex encoding.
  const bytes = fromBase58(digest);
  if (bytes.length !== 32) throw new Error(`Unexpected Sui digest length for ${name}`);
  result.steps[name] = { ok: true, status: 'ok', digest: Buffer.from(bytes).toString('hex'), sui_digest: digest, detail };
  flush();
}
function requireSuccess(response: { digest: string; effects?: { status?: { status: string; error?: string } } }) {
  if (response.effects?.status?.status !== 'success') {
    throw new Error(`Transaction ${response.digest} failed: ${response.effects?.status?.error ?? 'missing success effects'}`);
  }
  return response.digest;
}
function created(response: { objectChanges?: Array<{ type: string; objectType?: string; objectId?: string }> }, type: string, required = true) {
  const ids = (response.objectChanges ?? []).filter(o => o.type === 'created' && o.objectType?.endsWith(type)).map(o => o.objectId);
  if ((required && !ids.length) || ids.some(id => !id)) throw new Error(`Missing created ${type} object`);
  return ids as string[];
}
async function runTx(signer: Ed25519Keypair, tx: Transaction) {
  const response = await rpc.signAndExecuteTransaction({ signer, transaction: tx,
    options: { showEffects: true, showObjectChanges: true, showEvents: true } });
  requireSuccess(response);
  await rpc.waitForTransaction({ digest: response.digest });
  return response;
}
async function fund(address: string, faucetUrl: string) {
  const existing = await rpc.getCoins({ owner: address });
  if (existing.data.some(c => BigInt(c.balance) >= 500_000_000n)) {
    result.setup.faucet_status = 'pre_funded';
    flush();
    return true;
  }
  for (let attempt = 1; attempt <= 3; attempt++) {
    const log = result.setup.faucet_attempts as Array<Record<string, unknown>>;
    try {
      const response = await fetch(faucetUrl, { method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ FixedAmountRequest: { recipient: address } }), signal: AbortSignal.timeout(15000) });
      log.push({ attempt, http_status: response.status, ok: response.ok });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      for (let poll = 0; poll < 8; poll++) {
        await new Promise(done => setTimeout(done, 2500));
        const coins = await rpc.getCoins({ owner: address });
        if (coins.data.some(c => BigInt(c.balance) > 0n)) return true;
      }
    } catch (error) { log.push({ attempt, error: String(error) }); }
    flush();
  }
  return false;
}
function pseudoTimingBand(address: string): number {
  // Demo timing input is deterministic and non-secret; randomness stays on-chain.
  return 50 + Array.from(address.slice(2), char => char.charCodeAt(0))
    .reduce((acc, n) => (acc + n) % 51, 0);
}
async function kiosk(wallet: Ed25519Keypair) {
  const tx = new Transaction();
  const [kioskObject, ownerCap] = tx.moveCall({ target: '0x2::kiosk::new' });
  tx.moveCall({ target: '0x2::transfer::public_share_object', typeArguments: ['0x2::kiosk::Kiosk'], arguments: [kioskObject] });
  tx.transferObjects([ownerCap], wallet.toSuiAddress());
  const response = await runTx(wallet, tx);
  return { id: created(response, '::kiosk::Kiosk')[0], cap: created(response, '::kiosk::KioskOwnerCap')[0] };
}

async function main() {
  flush();
  const mnemonic = process.env.SUI_TESTNET_MNEMONIC;
  const faucetUrl = process.env.SUI_TESTNET_FAUCET_URL;
  if (!mnemonic || !faucetUrl) throw new Error('Set SUI_TESTNET_MNEMONIC and SUI_TESTNET_FAUCET_URL');
  result.setup.cli_version = execFileSync('sui', ['--version'], { encoding: 'utf8' }).trim();
  flush();
  const owner = Ed25519Keypair.deriveKeypair(mnemonic);
  const buyer = new Ed25519Keypair();
  const address = owner.toSuiAddress();
  result.setup.owner_address = address;
  result.setup.buyer_address = buyer.toSuiAddress();
  result.setup.cli_version = execFileSync('sui', ['--version'], { encoding: 'utf8' }).trim();
  flush();
  if (!(await fund(address, faucetUrl))) {
    result.setup.status = 'skipped_faucet';
    result.setup.reason = 'Three documented faucet attempts did not fund the owner; no package was published';
    flush();
    return;
  }
  const built = JSON.parse(execFileSync('sui', ['move', 'build', '--dump-bytecode-as-base64', '--path', pkgDir], { encoding: 'utf8' })) as {
    modules: string[]; dependencies: string[];
  };
  const publish = new Transaction();
  const [upgradeCap] = publish.publish({ modules: built.modules, dependencies: built.dependencies });
  // Consuming UpgradeCap in the SAME publish PTB makes this package immutable.
  publish.moveCall({ target: '0x2::package::make_immutable', arguments: [upgradeCap] });
  const published = await runTx(owner, publish);
  const pkg = (published.objectChanges ?? []).find(c => c.type === 'published');
  if (!pkg || !('packageId' in pkg) || typeof pkg.packageId !== 'string') throw new Error('Missing published package ID');
  const packageId = pkg.packageId;
  result.setup.package_id = packageId;
  result.setup.publish_sui_digest = published.digest;
  result.setup.publish_digest = Buffer.from(fromBase58(published.digest)).toString('hex');
  const registry = created(published, '::items::Registry')[0];
  const mintCap = created(published, '::items::MintCap')[0];
  const policy = created(published, '::transfer_policy::TransferPolicy<'+packageId+'::items::WHItem>')[0];
  flush();

  const mintTx = new Transaction();
  for (let i = 0; i < 2; i++) mintTx.moveCall({ target: `${packageId}::items::mint_material`,
    arguments: [mintTx.object(mintCap), mintTx.object(registry), mintTx.pure.u8(0)] });
  const minted = await runTx(owner, mintTx);
  let materials = created(minted, '::items::Material');
  if (materials.length !== 2) throw new Error('Expected two materials');
  mark('mint', minted.digest, `Material IDs: ${materials.join(', ')}`);

  let crafted: Awaited<ReturnType<typeof runTx>> | undefined;
  let item: string | undefined;
  for (let attempt = 1; attempt <= 5; attempt++) {
    const craftTx = new Transaction();
    const vec = craftTx.makeMoveVec({ type: `${packageId}::items::Material`, elements: materials.map(id => craftTx.object(id)) });
    // The sui::random call is terminal in this PTB. Never append commands afterwards.
    craftTx.moveCall({ target: `${packageId}::craft::craft`, arguments: [craftTx.object(registry),
      craftTx.object('0x8'), craftTx.pure.string('Ash Blade'), vec, craftTx.pure.u8(pseudoTimingBand(address))] });
    crafted = await runTx(owner, craftTx);
    item = created(crafted, '::items::WHItem', false)[0];
    if (item) break;
    if (attempt === 5) throw new Error('Five genuine random craft outcomes failed; no item minted');
    const retryMint = new Transaction();
    for (let i = 0; i < 2; i++) retryMint.moveCall({ target: `${packageId}::items::mint_material`,
      arguments: [retryMint.object(mintCap), retryMint.object(registry), retryMint.pure.u8(0)] });
    const retry = await runTx(owner, retryMint);
    materials = created(retry, '::items::Material');
    if (materials.length !== 2) throw new Error('Retry did not mint two materials');
    (result.setup.craft_retries as Array<string>).push(crafted.digest);
    flush();
  }
  if (!crafted || !item) throw new Error('No successful craft transaction');
  mark('craft', crafted.digest, `Item ${item}`);

  const chainItem = await rpc.getObject({ id: item, options: { showContent: true } });
  const fields = chainItem.data?.content?.dataType === 'moveObject' ? chainItem.data.content.fields as Record<string, unknown> : null;
  if (!fields || BigInt(String(fields.serial)) < 1n) throw new Error('Missing positive on-chain serial');
  mark('serial', crafted.digest, `serial=${fields.serial}`);
  const lineage = fields.lineage as string[];
  if (!Array.isArray(lineage) || !materials.every(id => lineage.some(v => v.toLowerCase() === id.toLowerCase()))) {
    throw new Error('On-chain lineage does not contain both material IDs');
  }
  mark('provenance', crafted.digest, `Lineage contains ${materials.length} material IDs`);

  // Transfer testnet gas to second wallet before purchasing, not an external marketplace.
  const giveGas = new Transaction();
  const [buyerGas] = giveGas.splitCoins(giveGas.gas, [giveGas.pure.u64(200_000_000)]);
  giveGas.transferObjects([buyerGas], buyer.toSuiAddress());
  await runTx(owner, giveGas);
  const sellerKiosk = await kiosk(owner);
  const buyerKiosk = await kiosk(buyer);
  const price = 10_000_000n;
  const list = new Transaction();
  list.moveCall({ target: `${packageId}::market::list_item`, arguments: [list.object(sellerKiosk.id),
    list.object(sellerKiosk.cap), list.object(policy), list.object(item), list.pure.u64(price), list.pure.bool(false)] });
  const listed = await runTx(owner, list);
  mark('kiosk_list', listed.digest, `Kiosk ${sellerKiosk.id}, price ${price} MIST`);

  const buy = new Transaction();
  const fee = price * 500n / 10_000n;
  const [payment, royalty] = buy.splitCoins(buy.gas, [buy.pure.u64(price), buy.pure.u64(fee)]);
  buy.moveCall({ target: `${packageId}::market::purchase`, arguments: [buy.object(sellerKiosk.id),
    buy.pure.id(item), payment, royalty, buy.object(buyerKiosk.id), buy.object(buyerKiosk.cap), buy.object(policy)] });
  const bought = await runTx(buyer, buy);
  const buyerItem = await rpc.getObject({ id: item, options: { showOwner: true } });
  const ownerType = buyerItem.data?.owner;
  if (!ownerType || typeof ownerType !== 'object' || !('ObjectOwner' in ownerType) || ownerType.ObjectOwner !== buyerKiosk.id) {
    throw new Error('Purchased item was not placed in buyer Kiosk');
  }
  mark('kiosk_purchase', bought.digest, `Buyer Kiosk ${buyerKiosk.id}`);
  const policyObject = await rpc.getObject({ id: policy, options: { showContent: true } });
  const policyFields = policyObject.data?.content?.dataType === 'moveObject' ? policyObject.data.content.fields as Record<string, unknown> : null;
  const rawBalance = policyFields?.balance;
  const balanceValue = typeof rawBalance === 'object' && rawBalance !== null
    ? (rawBalance as Record<string, unknown>).value : rawBalance;
  if (balanceValue === undefined || BigInt(String(balanceValue)) < fee) {
    throw new Error('5% royalty was not credited to TransferPolicy');
  }
  mark('royalty', bought.digest, `5% (${fee} MIST) credited to policy ${policy}`);
  result.setup.status = 'ok';
  flush();
}
main().catch(error => {
  result.setup.status = 'failed';
  result.setup.error = String(error);
  // Preserve actual earlier successes; distinguish failure from faucet skip in downstream steps.
  for (const name of names) if (!result.steps[name].ok && result.steps[name].status === 'skipped_faucet') {
    result.steps[name] = { ok: false, status: 'failed', digest: null, detail: 'Flow stopped before this step' };
  }
  flush();
  process.stderr.write(`${String(error)}\n`);
  process.exitCode = 1;
});
