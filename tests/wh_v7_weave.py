"""Witch Hunter v7 "Weave Slice" validation harness (Testerbot).
Covers AC1-AC14 of io/specs/devbot-spec-whproto7-weave.md.
Playwright sync API, headless chromium. WH_BASE_ROOT / WH_BASE_PROXY env
overrides (v2 pattern). Target: builds/v7-playable.html.
"""
from playwright.sync_api import sync_playwright
import json, math, os, re, subprocess, sys, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_ROOT = os.environ.get("WH_BASE_ROOT", "http://localhost:8791/")
BASE_PROXY = os.environ.get("WH_BASE_PROXY", "http://localhost:8792/witchhunter/")
BUILD_PATH = "builds/v7-playable.html"

RESULTS = []   # (ac_id, name, ok, detail)

def check(ac, name, ok, detail=""):
    RESULTS.append((ac, name, bool(ok), detail))
    print("AC%-3s %-42s => %s %s" % (ac, name, "PASS" if ok else "FAIL", detail))

def console_watch(page):
    errors, page_errors = [], []
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    return errors, page_errors

# ---- JS helpers -------------------------------------------------------------

JS_CONFIG = """(() => {
  var C = window.CONFIG || window.WH_CONFIG;
  if (!C) return null;
  function pick(o, path){ var v=o, parts=path.split('.'); for (var i=0;i<parts.length;i++){ if(v==null) return undefined; v=v[parts[i]]; } return v; }
  return {
    focusMax: pick(C,'player.focusMax'), focusRegen: pick(C,'player.focusRegenPerSec'),
    tax: pick(C,'player.castFocusTaxMult'),
    fbCost: pick(C,'spell.firebolt.focusCost'), fbDmg: pick(C,'spell.firebolt.damage'),
    fbSpeed: pick(C,'spell.firebolt.speed'), fbWind: pick(C,'spell.firebolt.castWindup'),
    fbCd: pick(C,'spell.firebolt.castCooldown'), fbRange: pick(C,'spell.firebolt.maxRange'),
    beltSlots: pick(C,'belt.slots'), consSlots: pick(C,'belt.consumableSlots'),
    toggleS: pick(C,'loadout.toggleSeconds'),
    armedWin: pick(C,'armed.windowSeconds'), armedMult: pick(C,'armed.damageMult'),
    crossMult: pick(C,'armed.crossDamageMult'),
    potionHeal: pick(C,'consumable.healthPotion.heal'), potionCharges: pick(C,'consumable.healthPotion.charges')
  };
})()"""

JS_HOOKS = """(() => {
  var H = window.WH_DEBUG; if (!H || typeof H !== 'object') return null;
  var names = ['getFocus','setFocus','getBelt','selectBeltSlot','getActiveLoadout',
    'toggleLoadout','getOffhand','getCastState','getArmedState','getFirebolts',
    'useConsumable','getConsumables','getCombo','teleportPlayer','setCameraYaw',
    'getLockTarget','getPlayer','getPlayerPosition'];
  var missing = names.filter(function(n){ return typeof H[n] !== 'function'; });
  return { missing: missing, ok: missing.length === 0 };
})()"""



# ---- helpers over WH_DEBUG --------------------------------------------------

def js_state(page):
    return page.evaluate("""(() => {
  var H = window.WH_DEBUG;
  var P = H.getPlayer();
  return {
    focus: H.getFocus(), belt: H.getBelt(), loadout: H.getActiveLoadout(),
    offhand: H.getOffhand(), cast: H.getCastState(), armed: H.getArmedState(),
    combo: H.getCombo(), cons: H.getConsumables(),
    hp: P.hp != null ? P.hp : P.hpCurrent, hpMax: P.hpMax != null ? P.hpMax : P.maxHp,
    nfb: H.getFirebolts().filter(function(f){return f.alive;}).length
  };
})()""")

def set_focus(page, v):
    page.evaluate("window.WH_DEBUG.setFocus(%s)" % v)

def damage_player(page, amt):
    page.evaluate("window.WH_DEBUG.getPlayer().takeDamage(%s)" % amt)

def press_r(page):
    page.keyboard.press("r")
    page.wait_for_timeout(300)


# ---- IO D2-WEAVE helpers (probed 2026-09-30) --------------------------------
def get_attack_stage(page):
    return page.evaluate(
        "(function(){try{return window.WH_DEBUG.getPlayer()"
        ".getAttackStage();}catch(e){return 'x';}})()")


def wait_attack_stage(page, want, timeout_s=30.0):
    """Page-clock poll for a player attack stage (SwiftShader dilation-safe)."""
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if get_attack_stage(page) == want:
            return True
        page.wait_for_timeout(40)
    return False


def wait_stage_null(page, timeout_s=30.0):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if get_attack_stage(page) is None:
            return True
        page.wait_for_timeout(40)
    return False



def target_hp(page):
    """Hp of the entity the F-Lock actually bound (state READ). getEnemy(0)
    may not be the locked enemy (run-2 evidence: chainHits fired while
    enemy-0 hp read 0 delta). Resolve by matching getLockTarget() coords
    against the active region's enemy list; fall back to enemy 0."""
    return page.evaluate("""(() => { try {
      var H = window.WH_DEBUG;
      var lt = H.getLockTarget();
      var rm = H.getRegionManager ? H.getRegionManager() : null;
      var list = rm ? rm.getEnemies(rm.logic.activeId) : null;
      var cands = [];
      if (list && list.length) { for (var i=0;i<list.length;i++) cands.push(list[i]); }
      else { for (var j=0;j<6;j++){ var e=H.getEnemy(j); if(e&&e.ref)cands.push(e.ref); } }
      if (lt) {
        for (var k=0;k<cands.length;k++) {
          var e = cands[k];
          if (e && e.pos && Math.abs(e.pos.x - lt.x) < 0.05 &&
              Math.abs(e.pos.z - lt.z) < 0.05) return e.hp;
        }
      }
      return (cands[0] && cands[0].hp !== undefined) ? cands[0].hp : null;
    } catch(x) { return null; } })()""")


def ensure_alive(page):
    """SETUP: revive/top-up the player between combat ACs. Real ds1 enemies
    deal damage during the ~10min suite; a dead/low player refuses strikes
    (state gate) and zeroes every baseline. Writes are setup acts; all
    assertions below read post-act state."""
    page.evaluate("""(() => { var P = window.WH_DEBUG.getPlayer();
      var maxhp = P.hpMax || P.maxHp || 100;
      if (P.state !== 'alive' || P.hp <= 0) {
        if (typeof P.respawnAt === 'function') { P.respawnAt(-6, -2); }
        else { P.state = 'alive'; P.hp = maxhp; }
      }
      P.hp = Math.max(P.hp, maxhp * 0.8); })()""")

def beef_target(page, hpv=3000):
    """SETUP write only (mirrors the AC10 hp-write fixture pattern): keep the
    locked enemy alive through N strikes so arming is reachable. Assertions
    below read damage/timers, never this write."""
    page.evaluate("""(() => { var e = window.WH_DEBUG.getEnemy(0);
      if (e && e.ref) { e.ref.hp = %s; e.ref.hpMax = %s; } })()""" % (hpv, hpv))


def real_chain(page, presses=3):
    """Organic chain: real LMB press 1, then buffered presses during the
    recover window (the combo-open path), page-clock polled."""
    page.mouse.click(640, 400)
    n = 1
    t0 = time.time()
    while n < presses and time.time() - t0 < 150:
        if wait_attack_stage(page, "recover"):
            page.mouse.click(640, 400)
            n += 1
    wait_stage_null(page)

def guard_break_player(page):
    # v6 guard break: stagger via repeated blocked hits is not reachable
    # headless; use the player's guardBreak entry point if exposed.
    page.evaluate("""(() => {
      var P = window.WH_DEBUG.getPlayer();
      if (typeof P.guardBreak === 'function') { P.guardBreak(); return 'fn'; }
      if (typeof P.breakGuard === 'function') { P.breakGuard(); return 'fn2'; }
      if (typeof P.enterGuardBreak === 'function') { P.enterGuardBreak(); return 'fn3'; }
      P.stagger = (P.stagger||0); P.stagger += 3; return 'stagger-poke';
    })()""")

# ---- suite ------------------------------------------------------------------

def run_suite(page, base_url, origin):
    errors, page_errors = console_watch(page)
    url = base_url + BUILD_PATH
    page.goto(url, wait_until="load", timeout=30000)
    page.wait_for_timeout(6000)

    title = page.title()
    dbg = page.evaluate(JS_HOOKS)
    cfg = page.evaluate(JS_CONFIG)

    # --- AC13: clean load, title, WH_DEBUG present -------------------------
    ac13 = title.find("v7") >= 0 and dbg is not None and dbg["ok"] \
        and not errors and not page_errors
    check(13, "clean load + hooks [%s]" % origin, ac13,
          "title=%r missing=%s consoleErr=%d" % (title, dbg and dbg["missing"], len(errors)))
    if dbg is None or not dbg["ok"]:
        # nothing after this is meaningful
        check(13, "ABORT: hooks missing", False, str(dbg))
        return False

    H = "window.WH_DEBUG"

    # --- AC1: CONFIG tunables ----------------------------------------------
    exp = {"focusMax": 100, "tax": 1.25, "fbCost": 8, "fbDmg": 12, "fbSpeed": 40,
           "fbWind": 0.25, "fbCd": 0.3, "fbRange": 30, "beltSlots": 5,
           "consSlots": 2, "toggleS": 0.8, "armedWin": 3.5, "armedMult": 1.5,
           "crossMult": 2.0, "potionHeal": 40, "potionCharges": 3}
    bad = {k: (cfg.get(k), v) for k, v in exp.items() if cfg.get(k) != v} if cfg else {"cfg": (None, "missing")}
    check(1, "CONFIG tunables", not bad, str(bad))
    if cfg is None:
        return False

    # --- AC12: hook round-trips --------------------------------------------
    set_focus(page, 55)
    rt_focus = page.evaluate("%s.getFocus()" % H)
    page.evaluate("%s.selectBeltSlot(2)" % H)
    rt_belt = page.evaluate("%s.getBelt()" % H)
    rt_loadout = page.evaluate("%s.getActiveLoadout()" % H)
    rt_off = page.evaluate("%s.getOffhand()" % H)
    rt_state = page.evaluate("!!%s.getCastState() && !!%s.getArmedState() && "
                             "Array.isArray(%s.getFirebolts()) && !!%s.getCombo()"
                             % (H, H, H, H))
    ok12 = abs(rt_focus - 55) < 0.01 and rt_belt is not None and rt_state \
        and rt_loadout in (1, 2) and rt_off in ("spell", "shield")
    check(12, "debug hook round-trips", ok12,
          "focus=%s belt=%s loadout=%s offhand=%s" % (rt_focus, rt_belt, rt_loadout, rt_off))

    # --- AC11: HUD elements -------------------------------------------------
    hud = page.evaluate("""(() => {
      var q = function(s){ return document.querySelector(s); };
      var all = document.body.innerText;
      var focusBar = q('#wh-focus-bar') || q('#focus-bar') || q('[class*="focus"]');
      var beltRow = q('#wh-belt') || q('#belt-row') || q('[class*="belt"]') || q('[id*="belt"]');
      var pips = (q('[class*="loadout-pip"], [id*="loadout"]') != null);
      return { focusBar: !!focusBar, label: all.indexOf('Focus') >= 0,
               beltRow: !!beltRow, pips: pips, text: all.indexOf('R') >= 0 && all.indexOf('T') >= 0 };
    })()""")
    ok11 = hud["focusBar"] and hud["label"] and hud["beltRow"] and hud["pips"]
    check(11, "HUD focus bar + belt row + pips", ok11, str(hud))

    # --- AC2: belt selection via Digit1-5 + empty-slot refusal --------------
    # (IO D2-WEAVE fixes, probed 2026-09-30: (a) flash element is #wh-block-
    # flash, an ID - [class*="flash"] can never match it; verdict = className
    # gains a flash kind + opacity>0 inside a page-clock window. (b) belt has
    # ONE spell in this slice, so "glow color changes" is untestable; spec
    # intent (devbot-spec-weave L48-50, L69) = glow color == selected spell's
    # schoolColor - assert equality in THREE. Color MANAGED linear space via
    # page-side THREE.Color compare. (c) key waits are page-clock.)
    page.evaluate("%s.setFocus(100)" % H)
    page.evaluate("%s.selectBeltSlot(1)" % H)
    page.wait_for_timeout(500)
    belt_before = page.evaluate("%s.getBelt()" % H)
    # select slot 0 (firebolt) via REAL key first so glow reflects a spell
    page.keyboard.press("1")
    page.wait_for_timeout(400)
    glow0 = page.evaluate("""(() => {
      var H = window.WH_DEBUG, P = H.getPlayer();
      var g = P.offhandGlow || P.offhandMesh || P.offhand;
      if (g && g.material && g.material.color) {
        return [g.material.color.r, g.material.color.g, g.material.color.b,
                g.material.color.getHexString ? g.material.color.getHexString() : null];
      }
      return null;
    })()""")
    empty_idx = None
    for i in range(5):
        if belt_before[i] is None:
            empty_idx = i
            break
    flashes0 = page.evaluate(
        "document.getElementById('wh-block-flash').className")
    ok_sel, detail2 = True, ""
    sel_slots = []
    for i in range(5):
        page.keyboard.press(str(i + 1))       # Digit1..Digit5 real key path
        page.wait_for_timeout(300)
        b = page.evaluate("%s.getBelt()" % H)
        sel = page.evaluate(
            "%s.getPlayer().selectedBeltSlot" % H)
        sel_slots.append(sel)
        if b is None:
            ok_sel, detail2 = False, "getBelt null at slot %d" % (i + 1)
            break
    # D2-WEAVE-W2: only slot 0 holds a spell in this slice; presses on 2-5
    # (empty) are REFUSED by design (flash + selection unchanged at 0).
    # slots [0,0,0,0,0] with flash on press >= 2 = correct refusal behavior.
    refused_after_first = all(s == 0 for s in sel_slots[1:])
    sel_ok = ok_sel and sel_slots[0] == 0 and refused_after_first
    # glow equality: select the firebolt slot and compare to schoolColor
    fb_slot = 0 if (belt_before and belt_before[0] == "firebolt") else None
    glow_ok = False
    if fb_slot is not None:
        page.keyboard.press(str(fb_slot + 1))
        page.wait_for_timeout(400)
        glow1 = page.evaluate("""(() => {
          var H = window.WH_DEBUG, P = H.getPlayer();
          var g = P.offhandGlow || P.offhandMesh || P.offhand;
          if (g && g.material && g.material.color) {
            return [g.material.color.r, g.material.color.g, g.material.color.b];
          }
          return null;
        })()""")
        glow_ok = bool(glow1) and page.evaluate("""(() => {
          var C = window.CONFIG || window.WH_CONFIG;
          var id = window.WH_DEBUG.getPlayer().getSelectedSpellId ?
            window.WH_DEBUG.getPlayer().getSelectedSpellId() : null;
          var SC = id && C.spell && C.spell[id];
          if (!SC) return false;
          var want = new THREE.Color(SC.schoolColor);
          var g = window.WH_DEBUG.getPlayer().offhandGlow;
          if (!g || !g.material || !g.material.color) return false;
          return Math.abs(g.material.color.r - want.r) < 1e-4 &&
                 Math.abs(g.material.color.g - want.g) < 1e-4 &&
                 Math.abs(g.material.color.b - want.b) < 1e-4;
        })()""")
    # empty-slot refusal flash via REAL key, page-clock poll
    flash_refused = False
    flash_detail = ""
    if empty_idx is not None:
        page.keyboard.press(str(empty_idx + 1))
        t0 = time.time()
        while time.time() - t0 < 6.0:
            f = page.evaluate("""(() => { var el =
              document.getElementById('wh-block-flash');
              if (!el) return null;
              return {cls: el.className,
                      op: parseFloat(getComputedStyle(el).opacity)};})()""")
            if f and f["op"] > 0.01 and f["cls"]:
                flash_refused = True
                flash_detail = "cls=%s op=%.2f" % (f["cls"], f["op"])
                break
            page.wait_for_timeout(120)
        if not flash_refused:
            flash_detail = "no flash in 6s page-window"
    ok2 = sel_ok and glow_ok and (empty_idx is None or flash_refused)
    check(2, "belt Digit1-5 + empty refusal + glow", ok2,
          "sel=%s slots=%s glowOk=%s flash=%s %s" %
          (sel_ok, sel_slots, glow_ok, flash_refused, flash_detail))

    # --- AC3: cast tax + Firebolt hit ---------------------------------------
    # (IO D2-WEAVE: select slot 0 (firebolt), page-clock poll for the bolt
    # instead of a fixed 0.3s wall wait - windup is 0.25s SIM which dilates
    # 2-5x under SwiftShader. Probed 2026-09-30: full cast->hit works live.)
    page.evaluate("%s.teleportPlayer(-6, -2)" % H)
    page.evaluate("%s.setCameraYaw(0)" % H)
    page.wait_for_timeout(400)
    page.keyboard.press("f")                    # lock on bandit
    page.wait_for_timeout(500)
    tgt = page.evaluate("%s.getLockTarget()" % H)
    page.evaluate("%s.setFocus(100)" % H)
    # D2-WEAVE-W2: loadout must be I + offhand spell here (AC6 left it at 2
    # in run 1 -> RMB routed to block, cast never started).
    page.evaluate("""(() => { var H = window.WH_DEBUG;
      if (H.getActiveLoadout() === 2) { H.toggleLoadout(); } })()""")
    t_tog = time.time()
    while time.time() - t_tog < 20.0:
        csf = page.evaluate("%s.getCastState()" % H)
        if csf and not csf.get("toggling") and \
                page.evaluate("%s.getActiveLoadout()" % H) == 1:
            break
        page.wait_for_timeout(150)
    page.keyboard.press("1")                    # select firebolt slot 0
    t_rg = time.time()
    while time.time() - t_rg < 20.0:            # regrip is 0.3s sim
        rg = page.evaluate(
            "(window.WH_DEBUG.getCastState()||{}).regrip")
        if rg is not None and rg == 0:
            break
        page.wait_for_timeout(150)
    f0 = page.evaluate("%s.getFocus()" % H)
    hp0 = page.evaluate("(window.WH_DEBUG.getLockTarget()||{}).hp")
    page.mouse.click(640, 400, button="right")  # RMB cast path
    fb_mid = 0
    t0 = time.time()
    while time.time() - t0 < 14.0:              # page-clock: spawn within win
        fb_mid = page.evaluate(
            "%s.getFirebolts().filter(function(f){return f.alive;}).length" % H)
        if fb_mid >= 1:
            break
        page.wait_for_timeout(150)
    page.wait_for_timeout(2500)                 # flight + hit (page-clock)
    f1 = page.evaluate("%s.getFocus()" % H)
    hp1 = page.evaluate("(window.WH_DEBUG.getLockTarget()||{}).hp")
    tax_spent = (f0 - f1) if (f0 is not None and f1 is not None) else -1
    exp_tax = cfg["fbCost"] * cfg["tax"]
    dmg_drop = (hp0 - hp1) if (hp0 is not None and hp1 is not None) else -1
    ok3 = tgt is not None and fb_mid >= 1 and abs(tax_spent - exp_tax) < 1.0 \
        and abs(dmg_drop - cfg["fbDmg"]) < 3.0
    check(3, "cast tax + Firebolt hit", ok3,
          "tgt=%s fb=%d spent=%.2f exp=%.2f dmg=%.1f" % (bool(tgt), fb_mid, tax_spent, exp_tax, dmg_drop))

    # --- AC4: cast does not reset chain -------------------------------------
    page.evaluate("%s.setFocus(100)" % H)
    page.evaluate("""(() => { var H = window.WH_DEBUG, P = H.getPlayer();
      P.comboIndex = 2; P.comboQueued = true; })()""")
    page.mouse.click(640, 400, button="right")
    page.wait_for_timeout(900)
    combo = page.evaluate("%s.getCombo()" % H)
    ok4 = combo and combo["index"] == 2 and combo["queued"] == True
    check(4, "cast preserves combo chain", ok4, str(combo))
    page.evaluate("""(() => { var P = window.WH_DEBUG.getPlayer();
      P.comboIndex = 0; P.comboQueued = false; })()""")

    # --- AC5: fizzle on damage during windup --------------------------------
    page.evaluate("%s.setFocus(100)" % H)
    page.evaluate("%s.teleportPlayer(-6, -2)" % H)
    page.wait_for_timeout(400)
    # D2-WEAVE-W2b: AC4 leaves castCooldown running; a refused RMB never
    # starts a windup. Poll canCast() first.
    t_cc = time.time()
    while time.time() - t_cc < 20.0:
        can = page.evaluate(
            "window.WH_DEBUG.getPlayer().canCast ? "
            "window.WH_DEBUG.getPlayer().canCast() : null")
        if can:
            break
        page.wait_for_timeout(150)
    # D2-WEAVE-W4 (run-3 evidence: focus 91.6 = regen resumed when the python
    # poll crossed the 0.25s sim windup under dilation). Reflex probe: page-
    # side watch flips damage INSIDE the windup window the frame it starts;
    # python only reads the outcome. takeDamage is the sanctioned damage-act.
    page.evaluate("""(() => {
      window.__IO_FIZZLE = {fired: false, done: false, log: []};
      var P0 = window.WH_DEBUG.getPlayer();
      // W6c instrument: wrap takeDamage/fizzle to log the REAL order
      // (run-6 evidence: fired=True yet focus dropped => the fizzle did
      // not fire on this damage; name the state at the event).
      var origTake = P0.takeDamage;
      P0.takeDamage = function (a) {
        window.__IO_FIZZLE.log.push(
          {ev: 'take', castWindup: this.castWindup, focus: this.focus,
           state: this.state, iframes: this.iframes});
        return origTake.apply(this, arguments);
      };
      var origFz = P0.cancelCastFizzle;
      P0.cancelCastFizzle = function () {
        var r = origFz.apply(this, arguments);
        window.__IO_FIZZLE.log.push(
          {ev: 'fz', ret: r, focus: this.focus});
        return r;
      };
      function tick(){
        if (window.__IO_FIZZLE.done) return;
        var cs = window.WH_DEBUG.getCastState();
        // W6b: fire only with >= half the windup REMAINING.
        if (cs && cs.windup >= 0.12 && !window.__IO_FIZZLE.done) {
          window.__IO_FIZZLE.fired = true;
          window.__IO_FIZZLE.done = true;
          window.__IO_FIZZLE.log.push({ev: 'reflex', windupRead: cs.windup});
          var p2 = window.WH_DEBUG.getPlayer();
          p2.takeDamage(5);      // damage-act DURING windup mid-window
          return;
        }
        if (cs && cs.windup > 0 && cs.windup < 0.12) {
          window.__IO_FIZZLE.done = true;
          return;
        }
        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    })()""")
    page.mouse.click(640, 400, button="right")
    page.wait_for_timeout(3000)
    fz = page.evaluate("window.__IO_FIZZLE")
    f2 = page.evaluate("%s.getFocus()" % H)
    nfb = page.evaluate("%s.getFirebolts().filter(function(f){return f.alive;}).length" % H)
    nfb_all = page.evaluate("%s.getFirebolts().length" % H)
    # D2-WEAVE-W7 (run-7 instrument SOLVED the 91.6/92.4 focus mystery):
    # AC4's cast A can complete INSIDE AC5's canCast poll (load-delayed
    # windup), spending its 10 focus mid-poll; B is then correctly
    # fizzled (instrument log: fz ret=True at windup 0.2, focus 90 -> 90).
    # The 100-flat bar was authored against an isolated cast. Correct
    # bars: B contributed NO spend (focus at reflex time == final focus,
    # modulo regen), B's fizzle confirmed (log fz ret=True), no live bolt.
    f_at_reflex = None
    if isinstance(fz, dict):
        for e in fz.get("log") or []:
            if e.get("ev") == "take":
                f_at_reflex = e.get("focus")
                break
    fizzle_ok = isinstance(fz, dict) and \
        any(e.get("ev") == "fz" and e.get("ret") for e in fz.get("log") or [])
    ok5 = (fz and fz["fired"] and fizzle_ok and f_at_reflex is not None
           and f2 >= f_at_reflex - 0.5 and nfb == 0)
    check(5, "fizzle on windup damage", ok5,
          "fired=%s fizzleConfirmed=%s focusAtReflex=%s focusFinal=%.1f "
          "fbAlive=%d fbAll=%d" %
          (fz and fz["fired"], fizzle_ok, f_at_reflex, f2, nfb, nfb_all))

    # --- AC6: Q toggle rules ------------------------------------------------
    # (IO D2-WEAVE: toggle busy window is 0.8s SIM = 2-4s wall under
    # SwiftShader; fixed waits read pre-completion loadout. Page-clock poll
    # for the toggling flag to clear; probed clean live 2026-09-30.)
    page.evaluate("%s.setFocus(100)" % H)
    # arm a fake armedTimer first so we can see it survive
    page.evaluate("""(() => { var P = window.WH_DEBUG.getPlayer();
      if (typeof P.armedTimer !== 'undefined') { P.armedTimer = 3.0; }
      window.__v7HadArmed = typeof P.armedTimer !== 'undefined'; })()""")
    lo0 = page.evaluate("%s.getActiveLoadout()" % H)
    page.keyboard.press("q")
    t0 = time.time()
    while time.time() - t0 < 20.0:              # page-clock: busy window
        cs = page.evaluate("%s.getCastState()" % H)
        if cs and not cs.get("toggling") and \
                page.evaluate("%s.getActiveLoadout()" % H) != lo0:
            break
        page.wait_for_timeout(150)
    cs = page.evaluate("%s.getCastState()" % H)
    page.mouse.click(640, 400, button="right")  # already-completed toggle: cast may run
    page.wait_for_timeout(500)
    f3 = page.evaluate("%s.getFocus()" % H)
    busy_refused = abs(f3 - 100) < 0.5
    # re-arm and re-toggle to probe the BUSY refusal at the right moment
    page.evaluate("""(() => { var P = window.WH_DEBUG.getPlayer();
      if (typeof P.armedTimer !== 'undefined') { P.armedTimer = 3.0; } })()""")
    page.evaluate("%s.setFocus(100)" % H)
    page.keyboard.press("q")
    tt = time.time()
    seen_busy = False
    while time.time() - tt < 20.0:
        csb = page.evaluate("%s.getCastState()" % H)
        if csb and csb.get("toggling"):
            seen_busy = True
            page.mouse.click(640, 400, button="right")
            page.wait_for_timeout(500)
            f4 = page.evaluate("%s.getFocus()" % H)
            if abs(f4 - 100) < 0.5:
                break
            seen_busy = False
        page.wait_for_timeout(150)
    busy_refused = busy_refused and seen_busy
    page.wait_for_timeout(1000)                 # settle to completed toggle
    lo1 = page.evaluate("%s.getActiveLoadout()" % H)
    off1 = page.evaluate("%s.getOffhand()" % H)
    armed_surv = page.evaluate("""(() => {
      var P = window.WH_DEBUG.getPlayer(), a = window.WH_DEBUG.getArmedState();
      return (a && a.timer > 0) || (typeof P.armedTimer !== 'undefined' && P.armedTimer > 0) || !window.__v7HadArmed;
    })()""")
    combo_reset = page.evaluate("%s.getCombo()" % H)
    pip = page.evaluate("""(() => {
      var act = document.querySelector('[class*="loadout-pip"][class*="active"], [class*="pip"][class*="active"]');
      return !!act || document.body.innerText.indexOf('II') >= 0;
    })()""")
    ok6 = (lo0 != lo1) and (off1 == ("shield" if lo1 == 2 else "spell")) \
        and armed_surv and combo_reset["index"] == 0 and busy_refused and pip
    check(6, "Q toggle busy/reset/armed/pip", ok6,
          "lo %s->%s off=%s armed=%s combo=%s busy=%s pip=%s"
          % (lo0, lo1, off1, armed_surv, combo_reset, busy_refused, pip))

    # --- AC7: armed finisher on 3-hit chain ---------------------------------
    # (IO D2-WEAVE: original used comboIndex POKE (chainHits stays 0 -> no
    # arm) + fixed wall waits + a 70hp target that DIES at strike 2 (dead
    # enemies are skipped by the sweep loop, so no landing can register).
    # Probed live 2026-09-30: real buffered 3-chain arms at exactly landing 3
    # (chainHits 1->2->3, armedTimer=3.0); consume hit = 34 * 1.5 exactly.)
    page.evaluate("""(() => { var H = window.WH_DEBUG;
      if (H.getActiveLoadout() === 2) { H.toggleLoadout(); } })()""")
    page.wait_for_timeout(1500)                 # loadout I settled
    page.evaluate("%s.teleportPlayer(-6, -2)" % H)
    page.evaluate("%s.setCameraYaw(0)" % H)
    ensure_alive(page)
    # D2-WEAVE-W6c (run-5: base=68 = TWO strikes in the bracket): AC6's
    # busy-refusal RMB click was BUFFERED (P0-5 input buffer) and fired as
    # a real attack inside AC7's baseline bracket. SETUP: clear the
    # buffered/combo state before measuring (mirrors AC4's poke pattern).
    page.evaluate("""(() => { var P = window.WH_DEBUG.getPlayer();
      P.comboQueued = false; P.comboIndex = 0;
      // W6d (run-5 root cause: AC6's fake armedTimer=3.0 poke + REAL toggle
      // banked crossArmed=true; AC7's baseline click consumed it at 2.0x
      // => base=68, ratio 0.75 false-fail). SETUP: clear leftover armed
      // state before measuring baselines.
      P.armedTimer = 0; P.crossArmed = false; })()""")
    page.wait_for_timeout(500)
    page.keyboard.press("f")                    # lock a LIVE enemy
    t_lk = time.time()
    while time.time() - t_lk < 10.0:
        if page.evaluate("%s.isLocked()" % H):
            break
        page.wait_for_timeout(150)
    hpA = target_hp(page)                       # lock-sanity read only
    # D2-WEAVE-W6 (run-4 evidence hpA=46 = earlier ACs' real firebolt/strike
    # damage): BOTH baseline reads must live INSIDE one beef frame; a
    # pre-beef hpA mixed into the delta reads negative and masks a healthy
    # strike. Baseline = one strike, beefed-frame bracketing.
    beef_target(page, 3000)                     # SETUP: target survives chain
    hpP = target_hp(page)
    page.mouse.click(640, 400)                  # baseline plain strike
    wait_stage_null(page)                       # page-clock settle
    hpB0 = target_hp(page)
    base_dmg = (hpP - hpB0) if None not in (hpP, hpB0) else 0
    if base_dmg <= 0:
        check(7, "3-hit chain arms finisher", False,
              "baseline strike dealt 0 (target dead/unreachable?) hpA=%s" % hpA)
    else:
        real_chain(page, 3)                     # ORGANIC 3-hit chain
        armed0 = page.evaluate("%s.getArmedState()" % H)
        timer0 = (armed0 or {}).get("timer", 0)
        ok_arm = timer0 > 0
        check(7, "3-hit chain arms finisher", ok_arm, "timer=%.2f" % timer0)
        # next attack consumes at 1.5x
        beef_target(page, 3000)
        hpD = target_hp(page)
        page.mouse.click(640, 400)
        wait_stage_null(page)
        armed1 = page.evaluate("%s.getArmedState()" % H)
        hpE = target_hp(page)
        fin_dmg = (hpD - hpE) if (hpD is not None and hpE is not None) else 0
        ratio = (fin_dmg / base_dmg) if base_dmg > 0 and fin_dmg > 0 else 0
        consumed = (armed1 or {}).get("timer", 1) == 0 and \
            not (armed1 or {}).get("cross", False)
        ok7 = ok_arm and consumed and (1.3 <= ratio <= 1.7)
        check(7, "armed consumed at ~1.5x", ok7,
              "base=%.1f fin=%.1f ratio=%.2f consumed=%s" %
              (base_dmg, fin_dmg, ratio, consumed))
        # timer expiry alone disarms
        ok_exp = False
        if ok_arm:
            page.evaluate("""(() => { var H=window.WH_DEBUG, P=H.getPlayer();
              if (typeof P.armedTimer !== 'undefined') { P.armedTimer = 0.3; } })()""")
            page.wait_for_timeout(6000)   # 0.3s sim >= 1.5-3s wall dilated
            armed2 = page.evaluate("%s.getArmedState()" % H)
            ok_exp = (armed2 or {}).get("timer", 1) == 0
        check(7, "armed timer expiry disarms", ok_exp or not ok_arm, "")

    # --- AC8: cross-finisher via toggle -------------------------------------
    # (IO D2-WEAVE: same poke/dead-target artifacts as AC7. Real chain while
    # LOCKED, REAL Q toggle while armed -> crossArmed, strike in loadout II
    # = 2.0x. Probed live 2026-09-30: 34 * 2.0 = 68 exact, consumed.)
    page.evaluate("%s.teleportPlayer(-6, -2)" % H)
    page.evaluate("%s.setCameraYaw(0)" % H)
    ensure_alive(page)
    # D2-WEAVE-W6c: same buffered-input clear as AC7 (AC6's busy-refusal
    # RMB is buffered by P0-5 and would fire as the cross strike itself).
    page.evaluate("""(() => { var P = window.WH_DEBUG.getPlayer();
      P.comboQueued = false; P.comboIndex = 0;
      P.armedTimer = 0; P.crossArmed = false; })()""")
    page.wait_for_timeout(500)
    page.keyboard.press("f")
    t_lk8 = time.time()
    while time.time() - t_lk8 < 10.0:
        if page.evaluate("%s.isLocked()" % H):
            break
        page.wait_for_timeout(150)
    locked8 = page.evaluate("%s.isLocked()" % H)
    if locked8:
        beef_target(page, 3000)
        real_chain(page, 3)
        armed3 = page.evaluate("%s.getArmedState()" % H)
        page.keyboard.press("q")                # toggle while armed -> cross
        t0 = time.time()
        while time.time() - t0 < 20.0:          # page-clock toggle window
            cs8 = page.evaluate("%s.getCastState()" % H)
            if cs8 and not cs8.get("toggling"):
                break
            page.wait_for_timeout(150)
        armed3b = page.evaluate("%s.getArmedState()" % H)
        cross_set = (armed3b or {}).get("cross") == True
        page.wait_for_timeout(300)
        # D2-WEAVE-W6 (run-4 evidence: cross=True reached the strike, then
        # xratio=0 + crossCleared=False=True): the locked bandit MELEES the
        # player across the ~multi-sim-second window; player death CLEARS
        # armed/cross (player.js death block) which masquerades as
        # "consumed". Fixture: revive + re-beef INSIDE the window, and gate
        # the verdict on the player being alive at strike time.
        ensure_alive(page)
        beef_target(page, 3000)
        hpF = target_hp(page)
        alive_at_strike = page.evaluate(
            "window.WH_DEBUG.getPlayer().state")
        page.mouse.click(640, 400)
        wait_stage_null(page)
        armed4 = page.evaluate("%s.getArmedState()" % H)
        hpG = target_hp(page)
        cross_dmg = (hpF - hpG) if (hpF is not None and hpG is not None) else 0
        xratio = (cross_dmg / base_dmg) if base_dmg > 0 and cross_dmg > 0 else 0
        consumed_x = (armed4 or {}).get("cross") == False and \
            alive_at_strike == "alive"
        ok8 = (cross_set and alive_at_strike == "alive" and consumed_x
               and (1.6 <= xratio <= 2.4))
        check(8, "cross-finisher ~2.0x consumed", ok8,
              "cross=%s xratio=%.2f consumed=%s alive=%s (armedAtToggle=%s)" %
              (cross_set, xratio, consumed_x, alive_at_strike,
               (armed3 or {}).get("timer")))
    else:
        check(8, "cross-finisher ~2.0x consumed", False,
              "pre-run: no lock target for chain")

    # --- AC9: guard break clears armed --------------------------------------
    page.evaluate("""(() => { var H=window.WH_DEBUG, P=H.getPlayer();
      if (typeof P.armedTimer !== 'undefined') { P.armedTimer = 3.0; }
      if (P.crossArmed !== undefined) { P.crossArmed = true; } })()""")
    guard_break_player(page)
    page.wait_for_timeout(400)
    armed5 = page.evaluate("%s.getArmedState()" % H)
    ok9 = (armed5 or {}).get("timer", 1) == 0 and not (armed5 or {}).get("cross", False)
    check(9, "guard break clears armed", ok9, str(armed5))

    # --- AC10: R potion / T empty slot --------------------------------------
    # D2-WEAVE-W2: run at a SAFE spot (no enemy in strike range) so the fixed
    # inter-step waits cannot be punctured by melee while assertions run.
    page.evaluate("window.WH_DEBUG.teleportPlayer(0, 40)")
    page.evaluate("window.WH_DEBUG.breakLockOn && window.WH_DEBUG.breakLockOn()")
    page.wait_for_timeout(600)
    hp_before = page.evaluate("window.WH_DEBUG.getPlayer().hp")
    maxhp = page.evaluate("window.WH_DEBUG.getPlayer().hpMax || window.WH_DEBUG.getPlayer().maxHp || 100")
    page.evaluate("window.WH_DEBUG.getPlayer().hp = %s" % max(1, maxhp - 50))
    cons0 = page.evaluate("%s.getConsumables()" % H)
    press_r(page)
    hp_after = page.evaluate("window.WH_DEBUG.getPlayer().hp")
    cons1 = page.evaluate("%s.getConsumables()" % H)
    healed = hp_after - max(1, maxhp - 50)
    heal_ok = abs(healed - cfg["potionHeal"]) < 3.0 and hp_after <= maxhp + 0.01
    charge_ok = cons0 is not None and cons1 is not None and json_len_delta(cons0, cons1) != 0
    # refuse at full hp (settle the write, page-clock)
    page.evaluate("window.WH_DEBUG.getPlayer().hp = %s" % maxhp)
    t_f = time.time()
    while time.time() - t_f < 5.0:
        cur = page.evaluate("window.WH_DEBUG.getPlayer().hp")
        if cur is not None and cur >= maxhp - 0.01:
            break
        page.wait_for_timeout(100)
    cons_pre = page.evaluate("%s.getConsumables()" % H)
    press_r(page)
    hp_full = page.evaluate("window.WH_DEBUG.getPlayer().hp")
    cons_post = page.evaluate("%s.getConsumables()" % H)
    # refusal = hp stays max AND no charge burned
    refused_full = hp_full >= maxhp - 0.01 and \
        json_len_delta(cons_pre or [], cons_post or []) == 0
    # T empty slot refuses (poll until hp stable = no heal fired)
    page.evaluate("window.WH_DEBUG.getPlayer().hp = %s" % max(1, maxhp - 50))
    hp_t0 = page.evaluate("window.WH_DEBUG.getPlayer().hp")
    page.keyboard.press("t")
    t_t2 = time.time()
    hp_t1 = hp_t0
    while time.time() - t_t2 < 5.0:
        hp_t1 = page.evaluate("window.WH_DEBUG.getPlayer().hp")
        if hp_t1 is not None and hp_t0 is not None and hp_t1 > hp_t0 + 0.01:
            break    # a heal DID fire
        page.wait_for_timeout(150)
    t_refused = (hp_t1 is not None and hp_t0 is not None
                 and hp_t1 <= hp_t0 + 0.01)
    ok10 = heal_ok and refused_full and t_refused
    check(10, "R potion heal/refuse + T empty", ok10,
          "heal=%.1f fullRefuse=%s tRefuse=%s cons=%s->%s" % (healed, refused_full, t_refused, cons0, cons1 or []))

    # --- final: zero console errors across the whole run --------------------
    ok_err = not errors and not page_errors
    check(13, "zero console errors [%s]" % origin, ok_err,
          "console=%s page=%s" % (errors[:2], page_errors[:2]))
    return ok_err

def json_len_delta(a, b):
    try:
        sa, sb = json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True)
        return 0 if sa == sb else 1
    except Exception:
        return 1

import json  # noqa: E402  (used in json_len_delta)

# ---- AC14: regression suites -------------------------------------------------

def start_proxy_server(port=8792):
    """IO D2-WEAVE: serve the repo root ALSO at /witchhunter/ prefix on 8792
    (the historical reverse-proxy origin). Self-hosted fallback so AC14
    exercises the prefix-tolerant path without external infra."""
    import threading
    from http.server import ThreadingHTTPServer
    # inline handler: reuse the PROTO_SUBPATH remap semantics of server.py,
    # plus '/witchhunter/...' prefix tolerance.
    ROOT = os.path.abspath(os.path.join(HERE, ".."))
    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)
        def translate_path(self, path):
            path = path.split("?", 1)[0].split("#", 1)[0]
            path = re.sub(r"^/witchhunter/", "/", path)
            parts = [p for p in path.split("/") if p not in ("", ".")]
            if not parts or parts == ["index.html"]:
                parts = ["prototype", "index.html"]
            elif parts[0] in ("js", "vendor", "builds", "style.css", "index.html",
                              "server.py", "README.md"):
                parts = ["prototype"] + parts
            return os.path.join(ROOT, *parts)
        def guess_type(self, path):
            base = super().guess_type(path)
            if path.endswith(".glb"):
                return "model/gltf-binary"
            if path.endswith(".js") and base in ("text/plain",
                                                 "application/octet-stream", None):
                return "text/javascript"
            return base
        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()
        def log_message(self, *a):
            pass
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", port), H)
        th = threading.Thread(target=srv.serve_forever, daemon=True)
        th.start()
        return srv
    except OSError:
        return None  # already served by an external proxy

def run_regressions(proxy_srv=None):
    oks = {}
    for name, fn in (("v2", "wh_v2_verify.py"), ("v3", "wh_v3_anim_probes.py")):
        path = os.path.join(HERE, fn)
        if not os.path.exists(path):
            check(14, "%s present" % name, False, "missing %s" % path)
            oks[name] = False
            continue
        env = dict(os.environ)
        env.pop("WH_BASE_ROOT", None)
        env.pop("WH_BASE_PROXY", None)
        env["WH_V7_SKIP_REGRESS"] = "1"
        try:
            # retry policy per D2 flake protocol: one rerun on failure
            r = subprocess.run([sys.executable, path], timeout=420,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               env=env)
            out = r.stdout.decode("utf-8", "replace")
            if r.returncode != 0:
                import time as _t
                _t.sleep(5)
                r = subprocess.run([sys.executable, path], timeout=420,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, env=env)
                out = r.stdout.decode("utf-8", "replace")
                out += " | RETRY-EXIT=%d" % r.returncode
            oks[name] = r.returncode == 0
            # detail = the FAIL lines of the sub-suite (evidence, not tail
            # noise) + final verdict line
            fail_lines = [ln for ln in out.split("\n")
                          if "=> FAIL" in ln or "VERIFY:" in ln]
            check(14, "%s regression exit=%d" % (name, r.returncode),
                  r.returncode == 0,
                  " | ".join(fail_lines)[-400:])
        except Exception as e:
            check(14, "%s regression" % name, False, str(e)[:120])
            oks[name] = False
    return all(oks.values())

# ---- main ---------------------------------------------------------------------

if __name__ == "__main__":
    regress_only = os.environ.get("WH_V7_REGRESS_ONLY") == "1"
    proxy_srv = None
    ok_regress = True
    if os.environ.get("WH_V7_SKIP_REGRESS") != "1":
        # IO D2-WEAVE: ensure the /witchhunter/ proxy origin exists (AC14);
        # self-host fallback when no external proxy is up.
        import urllib.request
        up = False
        try:
            with urllib.request.urlopen(BASE_PROXY, timeout=2.0) as r:
                up = r.status == 200
        except Exception:
            up = False
        if not up:
            proxy_srv = start_proxy_server(8792)
            if proxy_srv is None and not up:
                print("[diag] proxy origin %s not up and fallback bind "
                      "failed; AC14 will run root-only" % BASE_PROXY)
        ok_regress = run_regressions(proxy_srv)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        ok_main = True
        if not regress_only:
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            try:
                ok_main = run_suite(page, BASE_ROOT, "root")
            except Exception as e:
                check(13, "harness exception", False, str(e)[:200])
                ok_main = False
            page.close()
        browser.close()

    npass = sum(1 for r in RESULTS if r[2])
    print("---")
    for ac, name, ok, det in RESULTS:
        if not ok:
            print("FAIL AC%s %s :: %s" % (ac, name, det))
    print("V7 WEAVE: %s (%d/%d checks pass, regress=%s)"
          % ("PASS" if (ok_main and ok_regress) else "FAIL",
             npass, len(RESULTS), ok_regress))
    sys.exit(0 if (ok_main and ok_regress) else 1)