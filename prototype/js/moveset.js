// Witch Hunter v5 sword moveset: keyframed weapon-pivot poses for player sword combos.
window.WH_MOVESET = {
  idle: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
  m1: {
    name: 'slash-l2r',
    windup:  { pos: [0.55, 1.35, 0.1],   rot: [-0.4, 0.8, 0.9] },
    strike:  { pos: [0.25, 0.95, -0.45], rot: [0.1, -0.6, -0.9] },
    recover: { pos: [0.42, 0.9, -0.18],  rot: [0.35, -0.5, 0.25] },
    bodyLean: 0.18, crouch: 0.03, lunge: 0.25
  },
  m2: {
    name: 'slash-r2l',
    windup:  { pos: [-0.1, 1.35, 0.15], rot: [-0.4, -0.8, 0.9] },
    strike:  { pos: [0.5, 0.95, -0.4],  rot: [0.1, 0.6, -0.9] },
    recover: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
    bodyLean: 0.18, crouch: 0.03, lunge: 0.25
  },
  m3: {
    name: 'overhead',
    windup:  { pos: [0.1, 1.7, 0.05],  rot: [-1.2, 0, 0.15] },
    strike:  { pos: [0.3, 0.35, -0.3], rot: [0.9, 0, 0.1] },
    recover: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
    bodyLean: 0.25, crouch: 0.09, lunge: 0.3
  },
  m4: {
    name: 'thrust',
    windup:  { pos: [0.35, 1.1, 0.35], rot: [0, 0.15, 0.05] },
    strike:  { pos: [0.15, 1.05, -0.7], rot: [0, 0, 0] },
    recover: { pos: [0.7, 1.0, -0.3], rot: [2.2, -0.7, 0.6] },
    bodyLean: 0.12, crouch: 0.02, lunge: 0.4
  },
  claw: {
    name: 'claw',
    windup:  { pos: [0.3, 1.2, 0.2],  rot: [-0.3, 0.4, 0.4] },
    strike:  { pos: [0.35, 1.0, -0.4], rot: [0.2, 0, 0] },
    recover: { pos: [0.3, 1.2, 0.2],   rot: [0.2, 0.4, 0.4] },
    bodyLean: 0.15, crouch: 0.03, lunge: 0.2
  }
};
window.WH_MOVESET.chainCap = 3;
window.WH_MOVESET.interpPose = function (a, b, t) {
  var T = Math.max(0, Math.min(1, t));
  var out = { pos: [0, 0, 0], rot: [0, 0, 0] };
  for (var i = 0; i < 3; i++) {
    out.pos[i] = a.pos[i] + (b.pos[i] - a.pos[i]) * T;
    out.rot[i] = a.rot[i] + (b.rot[i] - a.rot[i]) * T;
  }
  return out;
};