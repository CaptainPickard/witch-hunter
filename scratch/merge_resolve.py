#!/usr/bin/env python3
"""Merge resolver for the 10 conflict blocks (dev=whanim3+combat-integrity vs
feat=world-visuals+camera-decouple+moveset-framework+chain-clips).

IO rulings per block:
 player.js:
  B1 mount: FEAT (pose-independent + grip slide; supersedes whanim3 mount)
  B2 roll: FEAT semantics (roll cancels RECOVER only) with dev's comment
      tone; feat lines win. endCombo is GONE (feat has cancelAttack).
  B3 endCombo vs cancelAttack+getAttackPhase: FEAT (both fns).
  B4 consumeAttackSweep comment: FEAT (per-move sweep params).
  B5 chain-close: FEAT (recoverFullyElapsed path + rebuffer start).
  B6 fallback pose clock: FEAT (getAttackPhase); keep dev's D2 note.
  B7 strike se: FEAT (aph.p).
  B8 recover re: FEAT (aph.p).
  B9 lunge hook: FEAT (in update() before clamp; block 1084 = delete).
  B10 sweep-consume comment: FEAT.
 CONFIG.js: FEAT + re-add dev's whanim2/animRt comment (merge both lines).
 assets.js: UNION - dev's CSP-safe loader machinery INTO feat's
   loadAttempt/loadOne + clips>=6 not ===6 (9-clip GLB) + feat comment.
 game.js: FEAT (equipPlayerWeapon replaces inline sword mount).
anim.js: not conflicted (feat MOVE_NAMES vs dev NAMES idle..attack: auto
   merged? verify!) - MUST CHECK after resolution.
"""
import re, sys

BASE = '/workspace/witch-hunter/prototype/js/'

def resolve(path, keep='theirs', edits=None):
    """keep='theirs' -> for each conflict keep feat side; edits: list of
    (old, new) exact strings applied AFTER conflict removal."""
    src = open(path).read()
    pat = re.compile(r"<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> feat/world-visuals\n",
                     re.S)
    n = 0
    def sub(m):
        nonlocal n
        n += 1
        return m.group(2) if keep == 'theirs' else m.group(1)
    src = pat.sub(sub, src)
    if n == 0:
        print(f"NO CONFLICT MARKERS in {path} - check before writing")
    for old, new in (edits or []):
        assert old in src, f"{path}: edit anchor missing: {old[:60]!r}"
        src = src.replace(old, new, 1)
    open(path, 'w').write(src)
    print(f"resolved {path}: {n} blocks (keep={keep})")

def resolve_union_assets(path):
    src = open(path).read()
    pat = re.compile(r"<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> feat/world-visuals\n", re.S)
    blocks = list(pat.finditer(src))
    assert len(blocks) == 1, f"assets.js expected 1 conflict block, got {len(blocks)}"
    ours, theirs = blocks[0].group(1), blocks[0].group(2)
    # Union: dev's CSP-safe loader (ours) replaces feat's bare loadOne body,
    # but feat's call sites stay. Strategy: take OURS (the CSP machinery and
    # loadOne with dev's done/timer logic) then patch in feat's retry/progress
    # wrapper by REPLACING the body pieces:
    # ours ends with "var done = false;\n" and dev's loadOne continues WITHOUT
    # markers after the conflict (the rest of dev's loadOne body).
    # theirs is feat's swapBodyMap + loadAttempt head.
    # Correct structural merge:
    #   feat file keeps: swapBodyMap + loadAttempt(with CSP loader) + loadOne
    #   (feat structure). So: insert the CSP machinery (from ours) BEFORE
    #   loadAttempt, and patch loadAttempt's loader line to include mgr.
    union = theirs
    # extract machinery from ours: everything before 'var done = false;'
    machinery = ours.split('var done = false;')[0]
    # feat's loadAttempt head to patch:
    old_loader = ("    return new Promise(function (resolve) {\n"
                  "      var loader = new window.WHGLTFLoader();\n")
    assert old_loader in union, "feat loadAttempt loader line not found"
    new_loader = ("    return new Promise(function (resolve) {\n"
                  "      var mgr = new THREE.LoadingManager();\n"
                  "      var loader = new window.WHGLTFLoader(mgr);\n")
    union = union.replace(old_loader, new_loader, 1)
    # anchor machinery insertion just before loadAttempt comment
    anchor = "  // One load attempt, racing the per-attempt timeout."
    assert union.count(anchor) == 1
    union = union.replace(anchor, machinery + "\n" + anchor, 1)
    src = pat.sub(lambda m: union, src, count=1)
    # feat's clip-count warn: accept the 9-clip GLB (>=6)
    old_warn = ("expected 6 clips for ' + name + ', got ' +")
    # (warn already tolerant: it only warns. leave as-is.)
    open(path, 'w').write(src)
    print("resolved assets.js: CSP-machinery union applied")

def resolve_config(path):
    src = open(path).read()
    pat = re.compile(r"<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> feat/world-visuals\n", re.S)
    blocks = list(pat.finditer(src))
    # each block: take theirs but prepend dev's whanim2 header line set
    for b in blocks:
        theirs = b.group(2)
        if 'procedural animation feel' in theirs:
            union = ("  // v3: procedural animation feel. Since whanim2 pose values drive\n"
                     "  // only the rigid stand-in fallback (skinned bodies play animRt\n"
                     "  // clips; whanim2 stage fractions = combat FSM clock for both paths).\n"
                     "  // 10-04: stage durations + lunge are per move in CONFIG.moveset.weapons;\n"
                     "  // windup crouch / recover lean are per pose (WH_MOVESET crouch/bodyLean).\n")
            src = src.replace(b.group(0), union)
        else:
            src = src.replace(b.group(0), theirs)
    open(path, 'w').write(src)
    print(f"resolved CONFIG.js: {len(blocks)} blocks")

def resolve_game(path):
    resolve(path, keep='theirs', edits=[
        # dev's setWeapon call site replaced by feat's equipPlayerWeapon;
        # nothing of dev's survives (the socket mount path was whanim3's
        # own refactor and feat's setWeapon handles the socket via body bind)
    ])
    print("game.js done")

resolve(BASE + 'player.js', keep='theirs')
resolve_config(BASE + 'CONFIG.js')
resolve_union_assets(BASE + 'assets.js')
resolve_game(BASE + 'game.js')

# leftover-markers sanity
for f in ['player.js', 'CONFIG.js', 'assets.js', 'game.js']:
    s = open(BASE + f).read()
    assert '<<<<<<< HEAD' not in s, f + ' still has markers'
    print(f, 'marker-free')
print("ALL RESOLVED")