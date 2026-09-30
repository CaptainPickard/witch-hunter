module wh_items::items;

use std::string::String;
use sui::event;

const ENotDeployer: u64 = 0;
const EInvalidFamily: u64 = 1;

public struct ITEMS has drop {}

public struct MintCap has key, store { id: UID, registry: ID }

/// Shared serial authority: independent, monotonic counters for the five families.
public struct Registry has key {
    id: UID,
    counters: vector<u64>,
}

/// Owned, consumable crafting ingredient. An ingredient may itself record a prior item ID.
public struct Material has key, store {
    id: UID,
    family: u8,
    source: vector<ID>,
}

/// Address-owned (never shared); the fields are set only at mint and have no setters.
public struct WHItem has key, store {
    id: UID,
    family: u8,
    base_item: String,
    rarity_bands: u8,
    affix_id: u8,
    affix_stats: u64,
    serial: u64,
    crafter_addr: address,
    lineage: vector<ID>,
    created_epoch: u64,
    name: String,
    display_meta: String,
}

public struct Salvaged has copy, drop { item: ID, serial: u64, family: u8 }
public struct SalvageYield has copy, drop { item: ID, material: ID }

fun init(_: ITEMS, ctx: &mut TxContext) {
    let registry = Registry { id: object::new(ctx), counters: vector[0, 0, 0, 0, 0] };
    let cap = MintCap { id: object::new(ctx), registry: object::id(&registry) };
    transfer::share_object(registry);
    transfer::transfer(cap, ctx.sender());
}

/// 0 weapon, 1 armor, 2 potion, 3 charm, 4 decor.
public fun valid_family(family: u8): bool { family < 5 }
public fun decor_family(): u8 { 4 }
public fun family(item: &WHItem): u8 { item.family }
public fun serial(item: &WHItem): u64 { item.serial }
public fun lineage(item: &WHItem): &vector<ID> { &item.lineage }
public fun name(item: &WHItem): &String { &item.name }
public fun affix_id(item: &WHItem): u8 { item.affix_id }
public fun rarity_bands(item: &WHItem): u8 { item.rarity_bands }
public fun material_family(mat: &Material): u8 { mat.family }
public fun material_source(mat: &Material): &vector<ID> { &mat.source }

public(package) fun new_registry(ctx: &mut TxContext): Registry {
    Registry { id: object::new(ctx), counters: vector[0, 0, 0, 0, 0] }
}

#[test_only]
public(package) fun destroy_registry(registry: Registry) {
    let Registry { id, counters: _ } = registry;
    id.delete();
}

public(package) fun next_serial(registry: &mut Registry, family: u8): u64 {
    assert!(valid_family(family), EInvalidFamily);
    let counter = &mut registry.counters[family as u64];
    *counter = *counter + 1;
    *counter
}

/// Demo material issuance is capability gated; no paid random rolls.
entry fun mint_material(cap: &MintCap, registry: &Registry, family: u8, ctx: &mut TxContext) {
    assert!(cap.registry == object::id(registry), ENotDeployer);
    assert!(valid_family(family), EInvalidFamily);
    transfer::transfer(new_material(family, vector[], ctx), ctx.sender());
}

public(package) fun new_material(family: u8, source: vector<ID>, ctx: &mut TxContext): Material {
    assert!(valid_family(family), EInvalidFamily);
    Material { id: object::new(ctx), family, source }
}

/// Deliberately returns the material's provenance before consuming the object.
public(package) fun consume_material(mat: Material): (ID, vector<ID>) {
    let Material { id, family: _, source } = mat;
    let material_id = id.to_inner();
    id.delete();
    (material_id, source)
}

public(package) fun new_item(
    family: u8, base_item: String, rarity_bands: u8, affix_id: u8,
    serial: u64, lineage: vector<ID>, ctx: &mut TxContext,
): WHItem {
    WHItem {
        id: object::new(ctx), family, base_item, rarity_bands, affix_id,
        affix_stats: if (affix_id == 0) 0 else (affix_id as u64) * 10,
        serial, crafter_addr: ctx.sender(), lineage, created_epoch: ctx.epoch(),
        name: base_item,
        display_meta: b"https://witch-hunter.example/items/{id}".to_string(),
    }
}

/// Permanent burn (no material refund). Emits a provenance event.
entry fun burn(item: WHItem) { burn_internal(item) }

/// Salvage destroys the owned item and yields one material that points back to it.
entry fun burn_salvage(item: WHItem, ctx: &mut TxContext) {
    transfer::transfer(salvage_internal(item, ctx), ctx.sender());
}

public(package) fun salvage_internal(item: WHItem, ctx: &mut TxContext): Material {
    let family = item.family;
    let source = object::id(&item);
    burn_internal(item);
    let material = new_material(family, vector[source], ctx);
    event::emit(SalvageYield { item: source, material: object::id(&material) });
    material
}

public(package) fun burn_internal(item: WHItem) {
    let WHItem { id, family, base_item: _, rarity_bands: _, affix_id: _,
        affix_stats: _, serial, crafter_addr: _, lineage: _, created_epoch: _,
        name: _, display_meta: _ } = item;
    event::emit(Salvaged { item: id.to_inner(), serial, family });
    id.delete();
}
