module wh_items::craft;

use std::string::String;
use sui::random::{Self, Random};
use wh_items::items::{Self, Material, Registry, WHItem};

const ETiming: u64 = 0;
const EIngredients: u64 = 1;
const EMismatch: u64 = 2;

/// Fixed curve: timing 0..100 -> quality bucket 0..10 (integer division).
/// Failure threshold is 20-bucket percent; affix probability is 40+2*bucket
/// percent. The remaining band mints a plain item. No band guarantees an
/// affix; even best timing retains an explicit 10% failure band.
public(package) fun thresholds(timing_band: u8): (u8, u8) {
    assert!(timing_band <= 100, ETiming);
    let bucket = timing_band / 10;
    (20 - bucket, 40 + 2 * bucket)
}

/// 0 failure, 1 plain, 2 affixed. Tests and live craft share this function.
public(package) fun outcome(timing_band: u8, roll: u8): u8 {
    assert!(roll < 100, ETiming);
    let (failure, affix) = thresholds(timing_band);
    if (roll < failure) 0 else if (roll < failure + affix) 2 else 1
}

/// Private entry, terminal in the client's PTB: no commands after randomness.
/// All ingredients are owned before the roll; no user-controlled callbacks.
/// RandomGenerator never leaves this private scope or enters a public API.
entry fun craft(
    registry: &mut Registry, randomness: &Random, recipe: String,
    mats: vector<Material>, timing_band: u8, ctx: &mut TxContext,
) {
    let mut generator = random::new_generator(randomness, ctx);
    let roll = random::generate_u8_in_range(&mut generator, 0, 99);
    let (result, mut survivors) = resolve(registry, recipe, mats, timing_band, roll, ctx);
    if (result.is_some()) {
        transfer::public_transfer(result.destroy_some(), ctx.sender());
    } else {
        result.destroy_none();
    };
    while (!survivors.is_empty()) transfer::public_transfer(survivors.pop_back(), ctx.sender());
    survivors.destroy_empty();
}

/// Isolated roll math path; package-visible only for deterministic unit tests.
public(package) fun resolve(
    registry: &mut Registry, recipe: String, mut mats: vector<Material>,
    timing_band: u8, roll: u8, ctx: &mut TxContext,
): (Option<WHItem>, vector<Material>) {
    assert!(mats.length() >= 2, EIngredients);
    let family = items::material_family(&mats[0]);
    let mut i = 0;
    while (i < mats.length()) {
        assert!(items::material_family(&mats[i]) == family, EMismatch);
        i = i + 1;
    };
    let result = outcome(timing_band, roll);
    if (result == 0) {
        // Strict subset sink: consume exactly one, return all other materials.
        let mat = mats.pop_back();
        let (_, _) = items::consume_material(mat);
        (option::none(), mats)
    } else {
        let mut lineage = vector[];
        while (!mats.is_empty()) {
            let (id, source) = items::consume_material(mats.pop_back());
            lineage.push_back(id);
            source.do!(|ancestor| lineage.push_back(ancestor));
        };
        mats.destroy_empty();
        let serial = items::next_serial(registry, family);
        (option::some(items::new_item(family, recipe, result, if (result == 2) 1 else 0, serial, lineage, ctx)), vector[])
    }
}
