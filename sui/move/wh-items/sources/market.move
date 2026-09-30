#[allow(lint(share_owned))]
module wh_items::market;

use std::string::String;
use sui::coin::{Self, Coin};
use sui::display;
use sui::kiosk::{Self, Kiosk, KioskOwnerCap};
use sui::package;
use sui::sui::SUI;
use sui::transfer_policy::{Self, TransferPolicy, TransferPolicyCap, TransferRequest};
use wh_items::items::{Self, WHItem};

const EPayment: u64 = 0;
const EDecor: u64 = 1;
const ROYALTY_BPS: u64 = 500; // 5% of listing price; paid in addition to seller price.
const DENOMINATOR: u64 = 10000;

public struct MARKET has drop {}
public struct RoyaltyRule has drop {}
public struct DecorLockRule has drop {}
public struct RoyaltyConfig has store, drop { bps: u64 }

/// Five on-chain per-family metadata objects, in addition to Display<WHItem>.
public struct FamilyDisplay has key, store {
    id: UID, family: u8, name: String, description: String,
    image_url: String, attributes: String,
}

fun init(witness: MARKET, ctx: &mut TxContext) {
    let publisher = package::claim(witness, ctx);
    let (mut policy, cap) = transfer_policy::new<WHItem>(&publisher, ctx);
    configure(&mut policy, &cap);
    transfer::public_share_object(policy);
    transfer::public_transfer(cap, ctx.sender());
    let mut display = display::new<WHItem>(&publisher, ctx);
    display::add(&mut display, b"name".to_string(), b"{name}".to_string());
    display::add(&mut display, b"description".to_string(), b"Family {family} serial {serial}".to_string());
    display::add(&mut display, b"image_url".to_string(), b"{display_meta}".to_string());
    display::add(&mut display, b"attributes".to_string(), b"{affix_stats}".to_string());
    display::update_version(&mut display);
    transfer::public_transfer(display, ctx.sender());
    let mut family = 0;
    while (family < 5) {
        transfer::share_object(new_family_display(family, ctx));
        family = family + 1;
    };
    package::burn_publisher(publisher);
}

public(package) fun new_family_display(family: u8, ctx: &mut TxContext): FamilyDisplay {
    assert!(items::valid_family(family), EDecor);
    FamilyDisplay {
        id: object::new(ctx), family,
        name: if (family == 0) b"Weapon".to_string() else if (family == 1) b"Armor".to_string()
            else if (family == 2) b"Potion".to_string() else if (family == 3) b"Charm".to_string()
            else b"Decor".to_string(),
        description: b"Witch Hunter crafted item".to_string(),
        image_url: b"https://witch-hunter.example/images/{id}".to_string(),
        attributes: b"family,rarity_bands,affix_id,affix_stats,serial".to_string(),
    }
}

public(package) fun display_family(display: &FamilyDisplay): u8 { display.family }

#[test_only]
public(package) fun destroy_family_display(display: FamilyDisplay) {
    let FamilyDisplay { id, family: _, name: _, description: _, image_url: _, attributes: _ } = display;
    id.delete();
}

public(package) fun configure(policy: &mut TransferPolicy<WHItem>, cap: &TransferPolicyCap<WHItem>) {
    transfer_policy::add_rule(RoyaltyRule {}, policy, cap, RoyaltyConfig { bps: ROYALTY_BPS });
    transfer_policy::add_rule(DecorLockRule {}, policy, cap, true);
}

public fun royalty_bps(): u64 { ROYALTY_BPS }
public fun royalty_due(price: u64): u64 { ((price as u128) * (ROYALTY_BPS as u128) / (DENOMINATOR as u128)) as u64 }
public fun has_royalty(policy: &TransferPolicy<WHItem>): bool {
    transfer_policy::has_rule<WHItem, RoyaltyRule>(policy)
}
public fun has_decor_lock(policy: &TransferPolicy<WHItem>): bool {
    transfer_policy::has_rule<WHItem, DecorLockRule>(policy)
}

/// Helper enforces lock for decor before listing; optional lock for valuable other items.
entry fun list_item(
    kiosk_ref: &mut Kiosk, cap: &KioskOwnerCap, policy: &TransferPolicy<WHItem>,
    item: WHItem, price: u64, lock_high_value: bool,
) {
    list_internal(kiosk_ref, cap, policy, item, price, lock_high_value)
}

public(package) fun list_internal(
    kiosk_ref: &mut Kiosk, cap: &KioskOwnerCap, policy: &TransferPolicy<WHItem>,
    item: WHItem, price: u64, lock_high_value: bool,
) {
    assert!(has_royalty(policy) && has_decor_lock(policy), EPayment);
    let id = object::id(&item);
    if (items::family(&item) == items::decor_family() || lock_high_value) {
        kiosk::lock(kiosk_ref, cap, policy, item);
    } else {
        kiosk::place(kiosk_ref, cap, item);
    };
    kiosk::list<WHItem>(kiosk_ref, cap, id, price);
}

/// Royalty is an additional buyer payment to TransferPolicy; seller gets full listing price.
/// Decor remains locked in buyer's kiosk; buyer must own its KioskOwnerCap.
entry fun purchase(
    seller: &mut Kiosk, id: ID, payment: Coin<SUI>, royalty: Coin<SUI>,
    buyer: &mut Kiosk, buyer_cap: &KioskOwnerCap,
    policy: &mut TransferPolicy<WHItem>,
) {
    purchase_internal(seller, id, payment, royalty, buyer, buyer_cap, policy)
}

public(package) fun purchase_internal(
    seller: &mut Kiosk, id: ID, payment: Coin<SUI>, royalty: Coin<SUI>,
    buyer: &mut Kiosk, buyer_cap: &KioskOwnerCap,
    policy: &mut TransferPolicy<WHItem>,
) {
    let (item, mut request) = kiosk::purchase<WHItem>(seller, id, payment);
    pay_royalty(policy, &mut request, royalty);
    if (items::family(&item) == items::decor_family()) {
        kiosk::lock(buyer, buyer_cap, policy, item);
    } else {
        kiosk::place(buyer, buyer_cap, item);
    };
    transfer_policy::add_receipt(DecorLockRule {}, &mut request);
    let (_, _, _) = transfer_policy::confirm_request(policy, request);
}

public(package) fun receipt_decor(request: &mut TransferRequest<WHItem>) {
    transfer_policy::add_receipt(DecorLockRule {}, request);
}

public(package) fun pay_royalty(
    policy: &mut TransferPolicy<WHItem>, request: &mut TransferRequest<WHItem>,
    royalty: Coin<SUI>,
) {
    let cfg = transfer_policy::get_rule<WHItem, RoyaltyRule, RoyaltyConfig>(RoyaltyRule {}, policy);
    assert!(cfg.bps == ROYALTY_BPS && coin::value(&royalty) == royalty_due(transfer_policy::paid(request)), EPayment);
    transfer_policy::add_to_balance(RoyaltyRule {}, policy, royalty);
    transfer_policy::add_receipt(RoyaltyRule {}, request);
}
