#[test_only]
module wh_items::economy_tests;

use sui::coin;
use sui::kiosk;
use sui::sui::SUI;
use sui::test_scenario;
use sui::transfer_policy;
use sui::tx_context;
use wh_items::craft;
use wh_items::items::{Self, Registry, WHItem};
use wh_items::market::{Self, DecorLockRule, RoyaltyConfig, RoyaltyRule};

fun two(family: u8, ctx: &mut TxContext): vector<items::Material> {
    vector[items::new_material(family, vector[], ctx), items::new_material(family, vector[], ctx)]
}

fun mint(registry: &mut Registry, family: u8, band: u8, roll: u8, ctx: &mut TxContext): WHItem {
    let (result, survivors) = craft::resolve(registry, b"Ash Blade".to_string(), two(family, ctx), band, roll, ctx);
    survivors.destroy_empty();
    result.destroy_some()
}

fun clean_policy(policy: transfer_policy::TransferPolicy<WHItem>, cap: transfer_policy::TransferPolicyCap<WHItem>, ctx: &mut TxContext): u64 {
    let mut policy = policy;
    transfer_policy::remove_rule<WHItem, RoyaltyRule, RoyaltyConfig>(&mut policy, &cap);
    transfer_policy::remove_rule<WHItem, DecorLockRule, bool>(&mut policy, &cap);
    coin::burn_for_testing(transfer_policy::destroy_and_withdraw(policy, cap, ctx))
}

#[test]
fun test_craft_success_band() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let item = mint(&mut registry, 0, 70, 42, &mut ctx);
    assert!(items::affix_id(&item) == 1 && items::rarity_bands(&item) == 2, 0);
    items::burn_internal(item); items::destroy_registry(registry);
}

#[test]
fun test_craft_failure_band_sink() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let (result, mut survivors) = craft::resolve(&mut registry, b"Ash".to_string(), two(0, &mut ctx), 50, 0, &mut ctx);
    assert!(!result.is_some() && survivors.length() == 1, 0);
    result.destroy_none();
    let (_, _) = items::consume_material(survivors.pop_back());
    survivors.destroy_empty();
    assert!(items::next_serial(&mut registry, 0) == 1, 1);
    items::destroy_registry(registry);
}

#[test]
fun test_timing_band_monotonicity() {
    let mut band = 0;
    let mut last_failure = 20;
    let mut last_affix = 40;
    while (band <= 100) {
        let (failure, affix) = craft::thresholds(band);
        assert!(failure <= last_failure && affix >= last_affix && affix < 100, 0);
        last_failure = failure; last_affix = affix;
        band = band + 1;
    };
}

#[test]
fun test_serial_monotonic_per_family() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let a = mint(&mut registry, 0, 50, 50, &mut ctx);
    let b = mint(&mut registry, 0, 50, 50, &mut ctx);
    let c = mint(&mut registry, 1, 50, 50, &mut ctx);
    assert!(items::serial(&a) == 1 && items::serial(&b) == 2 && items::serial(&c) == 1, 0);
    items::burn_internal(a); items::burn_internal(b); items::burn_internal(c);
    items::destroy_registry(registry);
}

#[test]
fun test_royalty_rule_present() {
    let mut ctx = tx_context::dummy();
    let (mut policy, cap) = transfer_policy::new_for_testing<WHItem>(&mut ctx);
    market::configure(&mut policy, &cap);
    assert!(market::has_royalty(&policy) && market::has_decor_lock(&policy), 0);
    assert!(market::royalty_bps() == 500 && market::royalty_due(10000) == 500, 1);
    let mut request = transfer_policy::new_request<WHItem>(object::id_from_address(@0x123), 10000, object::id_from_address(@0x456));
    let royalty = coin::mint_for_testing<SUI>(500, &mut ctx);
    market::pay_royalty(&mut policy, &mut request, royalty);
    market::receipt_decor(&mut request);
    let (_, paid, _) = transfer_policy::confirm_request(&policy, request);
    assert!(paid == 10000, 2);
    assert!(clean_policy(policy, cap, &mut ctx) == 500, 3);
}

#[test]
fun test_kiosk_list_purchase_round_trip() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let item = mint(&mut registry, 0, 30, 55, &mut ctx);
    let id = object::id(&item);
    let (mut policy, policy_cap) = transfer_policy::new_for_testing<WHItem>(&mut ctx);
    market::configure(&mut policy, &policy_cap);
    let (mut seller, seller_cap) = kiosk::new(&mut ctx);
    let (mut buyer, buyer_cap) = kiosk::new(&mut ctx);
    market::list_internal(&mut seller, &seller_cap, &policy, item, 10000, false);
    assert!(kiosk::is_listed(&seller, id), 0);
    let payment = coin::mint_for_testing<SUI>(10000, &mut ctx);
    let fee = coin::mint_for_testing<SUI>(500, &mut ctx);
    market::purchase_internal(&mut seller, id, payment, fee, &mut buyer, &buyer_cap, &mut policy);
    assert!(kiosk::has_item(&buyer, id) && kiosk::profits_amount(&seller) == 10000, 1);
    let purchased = kiosk::take<WHItem>(&mut buyer, &buyer_cap, id);
    items::burn_internal(purchased);
    assert!(coin::burn_for_testing(kiosk::close_and_withdraw(seller, seller_cap, &mut ctx)) == 10000, 2);
    coin::destroy_zero(kiosk::close_and_withdraw(buyer, buyer_cap, &mut ctx));
    assert!(clean_policy(policy, policy_cap, &mut ctx) == 500, 3);
    items::destroy_registry(registry);
}

#[test]
fun test_provenance_lineage_growth() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let a = items::new_material(0, vector[], &mut ctx);
    let b = items::new_material(0, vector[], &mut ctx);
    let a_id = object::id(&a);
    let b_id = object::id(&b);
    let (result, survivors) = craft::resolve(&mut registry, b"Blade".to_string(), vector[a, b], 60, 55, &mut ctx);
    survivors.destroy_empty();
    let item = result.destroy_some();
    assert!(items::lineage(&item).contains(&a_id) && items::lineage(&item).contains(&b_id), 0);
    let parent = object::id(&item);
    let second = items::new_material(0, vector[parent], &mut ctx);
    let sibling = items::new_material(0, vector[], &mut ctx);
    let (next, remains) = craft::resolve(&mut registry, b"Reforged".to_string(), vector[second, sibling], 60, 55, &mut ctx);
    remains.destroy_empty();
    let child = next.destroy_some();
    assert!(items::lineage(&child).contains(&parent) && items::lineage(&child).length() == 3, 1);
    items::burn_internal(item); items::burn_internal(child); items::destroy_registry(registry);
}

#[test]
fun test_salvage_yields_material_with_item_lineage() {
    let mut ctx = tx_context::dummy();
    let item = items::new_item(2, b"Potion".to_string(), 1, 0, 1, vector[], &mut ctx);
    let old = object::id(&item);
    let material = items::salvage_internal(item, &mut ctx);
    assert!(items::material_family(&material) == 2, 1);
    assert!(items::material_source(&material).length() == 1, 2);
    assert!(*items::material_source(&material).borrow(0) == old, 3);
    let (_, _) = items::consume_material(material);
}

#[test]
fun test_simulated_e2e_roll_math() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    assert!(craft::outcome(80, 0) == 0, 0);
    assert!(craft::outcome(80, 25) == 2, 1);
    assert!(craft::outcome(80, 99) == 1, 2);
    let item = mint(&mut registry, 2, 80, 25, &mut ctx);
    assert!(items::serial(&item) == 1 && items::lineage(&item).length() == 2, 3);
    items::burn_internal(item); items::destroy_registry(registry);
}

#[test]
fun test_burn_salvage_emits_event() {
    let mut scenario = test_scenario::begin(@0x1);
    let mut registry = items::new_registry(test_scenario::ctx(&mut scenario));
    let item = mint(&mut registry, 0, 0, 90, test_scenario::ctx(&mut scenario));
    items::burn_internal(item);
    items::destroy_registry(registry);
    let effects = test_scenario::next_tx(&mut scenario, @0x1);
    assert!(test_scenario::num_user_events(&effects) == 1, 0);
    let _ = test_scenario::end(scenario);
}

#[test]
fun test_display_per_family() {
    let mut ctx = tx_context::dummy();
    let mut family = 0;
    while (family < 5) {
        let display = market::new_family_display(family, &mut ctx);
        assert!(market::display_family(&display) == family, 0);
        market::destroy_family_display(display);
        family = family + 1;
    };
}

#[test, expected_failure(abort_code = wh_items::craft::ETiming)]
fun test_timing_band_bounds_rejected() { let (_, _) = craft::thresholds(101); }

#[test, expected_failure(abort_code = wh_items::craft::EIngredients)]
fun test_ingredients_bounds_rejected() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let (result, survivors) = craft::resolve(&mut registry, b"x".to_string(), vector[], 30, 50, &mut ctx);
    result.destroy_none(); survivors.destroy_empty();
    items::destroy_registry(registry);
}

#[test, expected_failure(abort_code = sui::kiosk::EItemLocked)]
fun test_decor_lock_rule_prevents_withdrawal() {
    let mut ctx = tx_context::dummy();
    let mut registry = items::new_registry(&mut ctx);
    let item = mint(&mut registry, 4, 0, 90, &mut ctx);
    let id = object::id(&item);
    let (mut policy, cap) = transfer_policy::new_for_testing<WHItem>(&mut ctx);
    market::configure(&mut policy, &cap);
    let (mut seller, seller_cap) = kiosk::new(&mut ctx);
    market::list_internal(&mut seller, &seller_cap, &policy, item, 100, false);
    let withdrawn = kiosk::take<WHItem>(&mut seller, &seller_cap, id);
    items::burn_internal(withdrawn);
    coin::destroy_zero(kiosk::close_and_withdraw(seller, seller_cap, &mut ctx));
    let _ = clean_policy(policy, cap, &mut ctx);
    items::destroy_registry(registry);
}
