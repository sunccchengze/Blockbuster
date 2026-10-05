// 波尔共振仪 · Bohr Resonance — deterministic f(t) renderer (Blockbuster protocol)
const path = require('path');
const { canvas, fontFile, ffmpegBin } = require(path.join(__dirname, '../../tools/node_env.js'));
const { createCanvas, GlobalFonts } = canvas();
const { spawn } = require('child_process');
GlobalFonts.registerFromPath(fontFile(false), 'CJK');
GlobalFonts.registerFromPath(fontFile(true), 'CJKB');
const W = 1280, H = 720, FPS = 24, DUR = 60.4;
const FONT = '"CJK"', FONTB = '"CJKB"';

// ---------- math ----------
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, x) => a + (b - a) * x;
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const win = (t, a, b, f = 0.5) => clamp((t - a) / f) * clamp((b - t) / f);
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = a => { const l = Math.hypot(...a); return [a[0] / l, a[1] / l, a[2] / l]; };

// ---------- rich text (sub/superscripts + combining bar, missing in Noto CJK) ----------
const SUPM = { '²': '2', '⁻': '−', '⁺': '+' }, SUBM = { '₁': '1', '₂': '2', 'ₙ': 'n', 'ᵢ': 'i', '₃': '3', '₀': '0' };
function parseFont(ctx) { const m = /(\d+)px (.*)/.exec(ctx.font); return [+m[1], m[2]]; }
function measureRich(ctx, s) { const f = ctx.font, [sz, fam] = parseFont(ctx); let w = 0; for (const ch of s) { if (ch === '\u0304' || ch === '\u0307' || ch === '\u0308') continue; if (SUPM[ch] || SUBM[ch]) { ctx.font = `${Math.round(sz * 0.62)}px ${fam}`; w += ctx.measureText(SUPM[ch] || SUBM[ch]).width; ctx.font = f; } else w += ctx.measureText(ch).width; } return w; }
function fillRich(ctx, s, x, y, stroke) {
  const f = ctx.font, [sz, fam] = parseFont(ctx), al = ctx.textAlign, w = measureRich(ctx, s);
  let cx = al === 'center' ? x - w / 2 : al === 'right' ? x - w : x; ctx.textAlign = 'left'; let lastX = cx, lastW = 0;
  for (const ch of s) {
    if (ch === '\u0304') { ctx.fillRect(lastX + lastW * 0.1, y - sz * 0.62, lastW * 0.8, Math.max(1.5, sz * 0.07)); continue; }
    if (ch === '\u0307' || ch === '\u0308') { const r = Math.max(1.2, sz * 0.06), cxm = lastX + lastW / 2, yy = y - sz * 0.62; if (ch === '\u0307') { ctx.beginPath(); ctx.arc(cxm, yy, r, 0, 6.283); ctx.fill(); } else { ctx.beginPath(); ctx.arc(cxm - sz * 0.12, yy, r, 0, 6.283); ctx.arc(cxm + sz * 0.12, yy, r, 0, 6.283); ctx.fill(); } continue; }
    let t = ch, dy = 0, small = false;
    if (SUPM[ch]) { t = SUPM[ch]; dy = -sz * 0.32; small = true; } else if (SUBM[ch]) { t = SUBM[ch]; dy = sz * 0.25; small = true; }
    if (small) ctx.font = `${Math.round(sz * 0.62)}px ${fam}`;
    if (stroke) ctx.strokeText(t, cx, y + dy); ctx.fillText(t, cx, y + dy);
    lastX = cx; lastW = ctx.measureText(t).width; cx += lastW; ctx.font = f;
  }
  ctx.textAlign = al; return w;
}
function txt(ctx, s, x, y, size, col, b, align = 'left') { ctx.font = `${size}px ${b ? FONTB : FONT}`; ctx.fillStyle = col; ctx.textAlign = align; ctx.textBaseline = 'middle'; return fillRich(ctx, s, x, y); }
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function frac(ctx, x, y, num, den, size, col = '#fff') { ctx.font = `${size}px ${FONT}`; ctx.fillStyle = col; const w = Math.max(measureRich(ctx, num), measureRich(ctx, den)) + 10; ctx.textAlign = 'center'; fillRich(ctx, num, x + w / 2, y - size * 0.58); fillRich(ctx, den, x + w / 2, y + size * 0.62); ctx.fillRect(x, y - 1, w, 2); ctx.textAlign = 'left'; return w; }
function panel(ctx, A, col, x = 690, y = 70, w = 550, h = 500) { ctx.globalAlpha = A; ctx.fillStyle = 'rgba(12,16,22,0.84)'; rr(ctx, x, y, w, h, 16); ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 1.5; ctx.stroke(); }

// ---------- timeline ----------
const SEG = [[0.8, 9.41], [9.8, 21.38], [21.78, 31.43], [31.83, 41.38], [41.78, 50.09], [50.49, 58.92]];
const SUBS = [
  ['这是波尔共振仪：', '铜质摆轮连着蜗卷弹簧，下方是电磁阻尼线圈，', '电机通过连杆驱动弹簧。'],
  ['先关掉电机，把摆轮转一个角度后释放。', '它在弹簧回复力矩作用下来回摆动，振幅逐渐衰减。', '增大线圈电流，阻尼变大，衰减更快。'],
  ['再打开电机。经过一段过渡，', '摆轮以电机的频率稳定振动，这就是受迫振动。', '它的振幅和相位差，都取决于驱动频率。'],
  ['当驱动频率接近固有频率，振幅急剧增大，', '这就是共振。', '此时摆轮落后驱动约九十度，', '用闪光灯定格，就能读出相位差。'],
  ['运动方程是：', '转动惯量乘角加速度，加上阻尼力矩和弹性力矩，', '等于周期性的驱动力矩。'],
  ['阻尼越小，共振峰越高越尖；', '相位差在共振点附近，从零迅速变到一百八十度。'],
];
const subTimes = [];
SEG.forEach(([a, b], i) => { const L = SUBS[i].map(s => s.length); const T = L.reduce((x, y) => x + y); let t = a; SUBS[i].forEach((s, k) => { const d = (b - a) * L[k] / T; subTimes.push([t, t + d, s]); t += d; }); });

// ---------- physics (precomputed, deterministic) ----------
const D2R = Math.PI / 180, W0 = 2 * Math.PI / 1.6, THD = 12 * D2R, TH0 = 120 * D2R;
const T_REL1 = 9.8, T_GRAB2 = 15.8, T_REL2 = 16.6, T_MOTOR = 21.8, T_SWEEP0 = 31.9, T_SWEEP1 = 33.4;
const beta = t => t < T_GRAB2 ? 0.25 : t < T_MOTOR ? 0.9 : 0.2;
const omegaD = t => t < T_SWEEP0 ? 0.8 * W0 : t < T_SWEEP1 ? W0 * lerp(0.8, 1.0, ease((t - T_SWEEP0) / (T_SWEEP1 - T_SWEEP0))) : W0;
const SR = 480, NS = Math.round(DUR * SR) + 2;
const TH = new Float64Array(NS), PH = new Float64Array(NS);
(() => {
  let th = 0, w = 0, ph = 0; const h = 1 / SR / 4;
  for (let i = 0; i < NS; i++) {
    const t = i / SR;
    if (t < T_REL1) { th = t < 8.4 ? 0 : TH0 * ease((t - 8.4) / 1.2); w = 0; }
    else if (t >= T_GRAB2 && t < T_REL2) { th = lerp(th, TH0, 0.02); w = 0; }
    else {
      for (let k = 0; k < 4; k++) {
        const tt = t + k * h, b = beta(tt), om = tt >= T_MOTOR ? omegaD(tt) : 0;
        const thd = tt >= T_MOTOR ? THD * Math.sin(ph) : 0;
        const acc = (x, v) => -2 * b * v - W0 * W0 * (x - thd);
        // RK4 (drive frozen over substep)
        const k1x = w, k1v = acc(th, w), k2x = w + h / 2 * k1v, k2v = acc(th + h / 2 * k1x, w + h / 2 * k1v);
        const k3x = w + h / 2 * k2v, k3v = acc(th + h / 2 * k2x, w + h / 2 * k2v), k4x = w + h * k3v, k4v = acc(th + h * k3x, w + h * k3v);
        th += h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x); w += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v); ph += om * h;
      }
    }
    TH[i] = th; PH[i] = ph;
  }
})();
const sample = (A, t) => { const x = clamp(t, 0, DUR) * SR, i = Math.floor(x), f = x - i; return lerp(A[i], A[Math.min(NS - 1, i + 1)], f); };
const theta = t => sample(TH, t);
const thetaD = t => t >= T_MOTOR ? THD * Math.sin(sample(PH, t)) : 0;
const phaseDeg = t => Math.atan2(2 * 0.2 * omegaD(t), W0 * W0 - omegaD(t) ** 2) / D2R;

// ---------- camera ----------
const KEYS = [
  [0, [-9, 17, 40], [1, 12, 0]],
  [9.2, [-3, 14, 35], [1, 12, 0]],
  [10.6, [2, 13, 40], [11, 12, 0]],
  [31.8, [3, 13, 40], [11, 12, 0]],
  [33.2, [1, 13, 36], [10, 12, 0]],
  [41.4, [2, 13, 37], [10, 12, 0]],
  [42.6, [2, 13, 40], [11, 12, 0]],
  [58.4, [4, 13, 41], [11, 12, 0]],
  [60.4, [0, 14, 46], [3, 12, 0]],
];
function camAt(t) { let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++; const [t0, p0, g0] = KEYS[i], [t1, p1, g1] = KEYS[i + 1]; const x = ease((t - t0) / (t1 - t0)); return { pos: p0.map((v, k) => lerp(v, p1[k], x)), tgt: g0.map((v, k) => lerp(v, g1[k], x)) }; }
let CAM;
function setCam(t) { const { pos, tgt } = camAt(t); const f = norm(sub(tgt, pos)); const r = norm(cross(f, [0, 1, 0])); const u = cross(r, f); CAM = { pos, f, r, u, focal: (H / 2) / Math.tan(22 * Math.PI / 180) }; }
function P(p) { const d = sub(p, CAM.pos); const z = dot(d, CAM.f); return [W / 2 + CAM.focal * dot(d, CAM.r) / z, H / 2 - CAM.focal * dot(d, CAM.u) / z, z]; }
const scl = (p, r) => CAM.focal * r / P(p)[2];
function poly(ctx, pts) { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); }


// ---------- scene geometry ----------
const C = [0, 12.5, 0.6], R = 5;
const rot = (a, r, z = C[2], cx = C[0], cy = C[1]) => [cx + r * Math.cos(a), cy + r * Math.sin(a), z];
function background(ctx) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#20242a'); g.addColorStop(0.6, '#15181c'); g.addColorStop(1, '#0b0c0e'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const c = [[-60, 0, -20], [60, 0, -20], [60, 0, 40], [-60, 0, 40]].map(P); poly(ctx, c);
  const bg = ctx.createLinearGradient(0, c[0][1], 0, H); bg.addColorStop(0, '#2c2f34'); bg.addColorStop(1, '#101114'); ctx.fillStyle = bg; ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.035)'; ctx.lineWidth = 1;
  for (let x = -60; x <= 60; x += 6) { const a = P([x, 0, -20]), b = P([x, 60, -20]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  const lp = P([1, 0, 2]); const rg = ctx.createRadialGradient(lp[0], lp[1], 10, lp[0], lp[1], scl([1, 0, 2], 26)); rg.addColorStop(0, 'rgba(255,240,215,0.12)'); rg.addColorStop(1, 'rgba(255,240,215,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
}
function box(ctx, x0, x1, y0, y1, z0, z1, col) {
  const f = [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]].map(P), top = [[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]].map(P);
  const side = CAM.pos[0] > x1 ? [[x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1]].map(P) : [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]].map(P);
  poly(ctx, top); ctx.fillStyle = shade(col, 1.25); ctx.fill(); poly(ctx, side); ctx.fillStyle = shade(col, 0.7); ctx.fill();
  poly(ctx, f); const g = ctx.createLinearGradient(f[3][0], f[3][1], f[1][0], f[1][1]); g.addColorStop(0, shade(col, 1.1)); g.addColorStop(1, shade(col, 0.85)); ctx.fillStyle = g; ctx.fill();
}
function shade(hex, k) { const n = parseInt(hex.slice(1), 16); const r = Math.min(255, ((n >> 16) & 255) * k) | 0, g = Math.min(255, ((n >> 8) & 255) * k) | 0, b = Math.min(255, (n & 255) * k) | 0; return `rgb(${r},${g},${b})`; }
function ring(ctx, cx, cy, z, r0, r1, a0, a1, fill) { const n = 90; ctx.beginPath(); for (let i = 0; i <= n; i++) { const p = P(rot(lerp(a0, a1, i / n), r1, z, cx, cy)); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); } for (let i = n; i >= 0; i--) { const p = P(rot(lerp(a0, a1, i / n), r0, z, cx, cy)); ctx.lineTo(p[0], p[1]); } ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); }
function disk(ctx, cx, cy, z, r, fill) { const pts = []; for (let i = 0; i < 64; i++) pts.push(P(rot(i / 64 * 6.283, r, z, cx, cy))); poly(ctx, pts); ctx.fillStyle = fill; ctx.fill(); return pts; }

function basePlate(ctx) {
  box(ctx, -11, 13, 0, 0.8, -3, 3, '#3a3d42');   // foot
  box(ctx, -10, 12, 0.8, 22.5, -1.2, -0.6, '#2e3136'); // back panel
  // screws
  [[-9, 21.5], [11, 21.5], [-9, 1.8], [11, 1.8]].forEach(([x, y]) => { const s = P([x, y, -0.6]); ctx.fillStyle = '#9aa0a8'; ctx.beginPath(); ctx.arc(s[0], s[1], scl([x, y, 0], 0.25), 0, 6.283); ctx.fill(); });
  // brand plate
  const b = P([-6.5, 21.4, -0.6]); ctx.fillStyle = 'rgba(210,215,222,0.6)'; ctx.font = `${Math.round(scl([0, 21, 0], 0.62))}px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('BG-2 波尔共振仪', b[0], b[1]);
}
function scaleRing(ctx) {
  const up = Math.PI / 2, span = 165 * D2R;
  ring(ctx, C[0], C[1], -0.5, 6.1, 7.7, up - span, up + span, 'rgba(232,228,214,0.92)');
  ctx.strokeStyle = '#222'; ctx.fillStyle = '#222';
  for (let d = -160; d <= 160; d += 5) { const a = up + d * D2R, l = d % 30 === 0 ? 0.75 : d % 10 === 0 ? 0.5 : 0.3; const p0 = P(rot(a, 7.7, -0.5)), p1 = P(rot(a, 7.7 - l, -0.5)); ctx.lineWidth = d % 30 === 0 ? 1.6 : 1; ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke();
    if (d % 30 === 0) { const q = P(rot(a, 6.55, -0.5)); ctx.font = `${Math.round(scl(C, 0.48))}px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(`${Math.abs(d)}`, q[0], q[1]); } }
}
function coil(ctx, front, I) {
  const z0 = front ? 0.95 : -0.35, z1 = front ? 1.35 : 0.25;
  box(ctx, -1.5, 1.5, 6.5, 7.0, z0, z1, '#4a4d52');
  box(ctx, -1.5, -0.9, 7.0, 8.8, z0, z1, '#b56a2a'); box(ctx, 0.9, 1.5, 7.0, 8.8, z0, z1, '#b56a2a');
  if (front) { ctx.strokeStyle = 'rgba(80,40,10,0.6)'; ctx.lineWidth = 1; for (let y = 7.1; y < 8.8; y += 0.22) for (const x of [-1.5, 0.9]) { const a = P([x, y, z1]), b = P([x + 0.6, y, z1]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); } }
  if (front && I > 0.01) { const s = P([0, 7.8, 1.2]); const r = scl([0, 7.8, 1], 3.2); const g = ctx.createRadialGradient(s[0], s[1], 0, s[0], s[1], r); g.addColorStop(0, `rgba(120,190,255,${0.45 * I})`); g.addColorStop(1, 'rgba(120,190,255,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s[0], s[1], r, 0, 6.283); ctx.fill(); }
}
function wheel(ctx, th) {
  const z = C[2];
  const pts = disk(ctx, C[0], C[1], z - 0.25, R, '#6b3a1a'); // edge thickness
  const s = P(C), rad = scl(C, R);
  const face = []; for (let i = 0; i < 64; i++) face.push(P(rot(i / 64 * 6.283, R, z)));
  poly(ctx, face); const g = ctx.createLinearGradient(s[0] - rad, s[1] - rad, s[0] + rad, s[1] + rad);
  g.addColorStop(0, '#f5b98a'); g.addColorStop(0.35, '#c7743e'); g.addColorStop(0.7, '#8e4a22'); g.addColorStop(1, '#d58a55'); ctx.fillStyle = g; ctx.fill();
  // rotating brushed rings
  ctx.strokeStyle = 'rgba(255,220,190,0.12)'; ctx.lineWidth = 1; for (let r = 1.2; r < R; r += 0.35) { const q = []; for (let i = 0; i < 48; i++) q.push(P(rot(i / 48 * 6.283, r, z))); poly(ctx, q); ctx.stroke(); }
  // rim notches (rotate)
  ctx.fillStyle = '#3a1d0c'; for (let k = 0; k < 30; k++) { const a = th + k * 12 * D2R; const q = [rot(a - 0.035, R, z), rot(a + 0.035, R, z), rot(a + 0.035, R - 0.55, z), rot(a - 0.035, R - 0.55, z)].map(P); poly(ctx, q); ctx.fill(); }
  // lightening holes
  for (let k = 0; k < 3; k++) { const a = th + Math.PI / 2 + (k + 0.5) * 2.094; const c = rot(a, 2.9, z); const q = []; for (let i = 0; i < 24; i++) q.push(P([c[0] + 0.8 * Math.cos(i / 24 * 6.283), c[1] + 0.8 * Math.sin(i / 24 * 6.283), z])); poly(ctx, q); ctx.fillStyle = '#1a1c20'; ctx.fill(); }
  // hub
  disk(ctx, C[0], C[1], z + 0.05, 0.75, '#b9bec6');
  // pointer
  const a = Math.PI / 2 + th; const p0 = P(rot(a, 0.6, z + 0.2)), p1 = P(rot(a, 7.4, z + 0.2)), pb = P(rot(a + Math.PI, 1.6, z + 0.2));
  ctx.strokeStyle = '#f2f2f2'; ctx.lineWidth = Math.max(2, scl(C, 0.12)); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(pb[0], pb[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke();
  ctx.fillStyle = '#e53935'; ctx.beginPath(); ctx.arc(p1[0], p1[1], Math.max(2.5, scl(C, 0.16)), 0, 6.283); ctx.fill();
}
function spring(ctx, th, thd) {
  const z = C[2] + 0.45, turns = 4.5, r0 = 0.85, r1 = 2.9, n = 260; ctx.beginPath();
  for (let i = 0; i <= n; i++) { const u = i / n; const a = u * turns * 6.283 + lerp(th, thd, u) + Math.PI / 2; const p = P(rot(a, lerp(r0, r1, u), z)); i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }
  ctx.strokeStyle = '#d9dde3'; ctx.lineWidth = Math.max(1.5, scl(C, 0.1)); ctx.stroke(); ctx.strokeStyle = 'rgba(40,44,50,0.6)'; ctx.lineWidth = Math.max(0.6, scl(C, 0.03)); ctx.stroke();
}
const ROCK_A = -30 * D2R, ROCK_L = 8, U = [Math.cos(ROCK_A + Math.PI / 2), Math.sin(ROCK_A + Math.PI / 2)], WV = [U[1], -U[0]];
const TIP0 = [C[0] + ROCK_L * Math.cos(ROCK_A), C[1] + ROCK_L * Math.sin(ROCK_A)], MOT = [TIP0[0] - 5.5 * U[0], TIP0[1] - 5.5 * U[1]], RC = ROCK_L * THD;
function driveTrain(ctx, t, thd) {
  const ph = t >= T_MOTOR ? sample(PH, t) : 0;
  // motor housing
  box(ctx, MOT[0] - 2.2, MOT[0] + 2.2, MOT[1] - 2.2, MOT[1] + 2.2, -0.6, 0.2, '#23262b');
  // phase dial (acrylic) rotating
  const z = 0.5; disk(ctx, MOT[0], MOT[1], z, 2.6, 'rgba(200,225,240,0.22)');
  ctx.strokeStyle = 'rgba(230,240,250,0.8)'; ctx.lineWidth = 1;
  for (let d = 0; d < 360; d += 10) { const a = ph + d * D2R + Math.PI / 2; const p0 = P(rot(a, 2.6, z, MOT[0], MOT[1])), p1 = P(rot(a, d % 90 === 0 ? 2.0 : 2.3, z, MOT[0], MOT[1])); ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke(); }
  disk(ctx, MOT[0], MOT[1], z + 0.05, 0.45, '#8c9199');
  const pin = [MOT[0] + RC * (U[0] * Math.sin(ph) + WV[0] * Math.cos(ph)), MOT[1] + RC * (U[1] * Math.sin(ph) + WV[1] * Math.cos(ph))];
  // rocker
  const a = ROCK_A + thd, tip = [C[0] + ROCK_L * Math.cos(a), C[1] + ROCK_L * Math.sin(a)];
  const r0 = P(rot(a, 2.9, C[2] + 0.7)), r1 = P([tip[0], tip[1], C[2] + 0.7]);
  ctx.strokeStyle = '#b0b6bf'; ctx.lineWidth = Math.max(3, scl(C, 0.32)); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(r0[0], r0[1]); ctx.lineTo(r1[0], r1[1]); ctx.stroke();
  // connecting rod
  const q0 = P([pin[0], pin[1], 0.9]), q1 = P([tip[0], tip[1], 0.9]);
  ctx.strokeStyle = '#e0c060'; ctx.lineWidth = Math.max(2.5, scl(C, 0.22)); ctx.beginPath(); ctx.moveTo(q0[0], q0[1]); ctx.lineTo(q1[0], q1[1]); ctx.stroke();
  [q0, q1].forEach(q => { ctx.fillStyle = '#666'; ctx.beginPath(); ctx.arc(q[0], q[1], Math.max(3, scl(C, 0.22)), 0, 6.283); ctx.fill(); });
  // motor-on LED
  const led = P([MOT[0] + 1.7, MOT[1] - 1.7, 0.25]); ctx.fillStyle = t >= T_MOTOR ? '#46ff7a' : '#2a3a2e'; ctx.beginPath(); ctx.arc(led[0], led[1], Math.max(2, scl(C, 0.15)), 0, 6.283); ctx.fill();
}
function flashLamp(ctx, t, F) {
  box(ctx, -9.2, -7.4, 2.6, 4.2, 0.8, 3.6, '#2a2d32');
  const s = P([-8.3, 3.4, 3.62]); ctx.fillStyle = F > 0.05 ? '#fff' : '#555a60'; ctx.beginPath(); ctx.arc(s[0], s[1], scl([-8, 3, 3], 0.55), 0, 6.283); ctx.fill();
}
function label3(ctx, anchor, off, lines, A, color = '#ffd27a', size = 20) {
  if (A <= 0.01) return; const a = P(anchor), p = P([anchor[0] + off[0], anchor[1] + off[1], anchor[2]]);
  ctx.globalAlpha = A; ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(p[0], p[1]); ctx.stroke(); ctx.fillStyle = color; ctx.beginPath(); ctx.arc(a[0], a[1], 3.5, 0, 6.283); ctx.fill();
  ctx.font = `${size}px ${FONTB}`; let w = 0; lines.forEach(l => w = Math.max(w, measureRich(ctx, l))); const h = lines.length * size * 1.3 + 10;
  ctx.fillStyle = 'rgba(10,12,16,0.78)'; rr(ctx, p[0] - w / 2 - 10, p[1] - h / 2, w + 20, h, 7); ctx.fill(); ctx.stroke();
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; lines.forEach((l, i) => { ctx.fillStyle = i ? '#e6eaef' : color; ctx.font = `${i ? size - 4 : size}px ${FONTB}`; fillRich(ctx, l, p[0], p[1] - h / 2 + 5 + size * 1.3 * (i + 0.5)); }); ctx.globalAlpha = 1;
}

// ---------- 2D graph panels ----------
const PX = 745, PY = 70, PW = 500, PH2 = 500;
function axes(ctx, gx, gy, gw, gh, xl, yl) { ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx, gy + gh); ctx.lineTo(gx + gw, gy + gh); ctx.stroke(); txt(ctx, yl, gx - 4, gy - 14, 15, '#aab4c0', true); txt(ctx, xl, gx + gw, gy + gh + 18, 15, '#aab4c0', false, 'right'); }
function dampPanel(ctx, t) {
  const A = win(t, 10.0, 21.5, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(120,190,255,0.5)', PX, PY, PW, PH2);
  txt(ctx, '阻尼振动：θ(t)', PX + 24, PY + 36, 24, '#8fd0ff', true);
  const gx = PX + 60, gy = PY + 80, gw = PW - 90, gh = 280, T = 5.6; axes(ctx, gx, gy, gw, gh, 't / s', 'θ');
  const Y = v => gy + gh / 2 - v / TH0 * gh / 2 * 0.92; ctx.strokeStyle = 'rgba(255,255,255,0.15)'; ctx.beginPath(); ctx.moveTo(gx, Y(0)); ctx.lineTo(gx + gw, Y(0)); ctx.stroke();
  const tr = (t0, col, b, lw) => { const te = Math.min(t, t0 + T); if (te <= t0) return; ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath(); for (let tt = t0; tt <= te; tt += 1 / 60) { const x = gx + gw * (tt - t0) / T, y = Y(theta(tt)); tt === t0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); } ctx.stroke();
    ctx.setLineDash([6, 5]); ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.globalAlpha *= 0.7; [1, -1].forEach(sg => { ctx.beginPath(); for (let tt = t0; tt <= te; tt += 0.1) { const x = gx + gw * (tt - t0) / T, y = Y(sg * TH0 * Math.exp(-b * (tt - t0))); tt === t0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); } ctx.stroke(); }); ctx.setLineDash([]); ctx.globalAlpha = A; };
  tr(T_REL1, '#ffb45a', 0.25, 2.5); tr(T_REL2, '#6fb8ff', 0.9, 2.5);
  txt(ctx, '— 小阻尼（线圈电流小）', gx + 10, gy + gh + 50, 17, '#ffc98a'); if (t > T_REL2) txt(ctx, '— 大阻尼（线圈电流大）', gx + 10, gy + gh + 78, 17, '#9fd0ff');
  txt(ctx, '虚线：包络 θ₀e^(−βt)', gx + 10, gy + gh + 106, 15, '#9aa4b0'); txt(ctx, '固有周期 T₀ ≈ 1.60 s', gx + 240, gy + gh + 50, 17, '#e6eaef');
  ctx.globalAlpha = 1;
}
function forcedPanel(ctx, t) {
  const A = win(t, 21.9, 41.5, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(255,200,120,0.5)', PX, PY, PW, PH2);
  const res = t > T_SWEEP0; txt(ctx, res ? '共振：ω → ω₀' : '受迫振动', PX + 24, PY + 36, 24, res ? '#ff8a7a' : '#ffc57a', true);
  const gx = PX + 60, gy = PY + 80, gw = PW - 90, gh = 250, T = 5; axes(ctx, gx, gy, gw, gh, '最近 5 s', 'θ');
  const Y = v => gy + gh / 2 - v / (130 * D2R) * gh / 2; ctx.strokeStyle = 'rgba(255,255,255,0.15)'; ctx.beginPath(); ctx.moveTo(gx, Y(0)); ctx.lineTo(gx + gw, Y(0)); ctx.stroke();
  const t0 = Math.max(T_MOTOR, t - T);
  const line = (f, col, lw) => { ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath(); let first = true; for (let tt = t0; tt <= t; tt += 1 / 60) { const x = gx + gw * (tt - (t - T)) / T, y = Y(f(tt)); first ? ctx.moveTo(x, y) : ctx.lineTo(x, y); first = false; } ctx.stroke(); };
  line(tt => thetaD(tt) * 2, 'rgba(200,210,220,0.75)', 1.5); line(theta, '#ffb45a', 2.6);
  txt(ctx, '— 摆轮 θ', gx + 10, gy + gh + 40, 17, '#ffc98a'); txt(ctx, '— 驱动（放大 2 倍）', gx + 150, gy + gh + 40, 17, '#c8d2dc');
  // amplitude over last period
  let amp = 0; for (let tt = t - 1.7; tt <= t; tt += 1 / 120) amp = Math.max(amp, Math.abs(theta(tt)));
  txt(ctx, `ω / ω₀ = ${(omegaD(t) / W0).toFixed(2)}`, gx + 10, gy + gh + 86, 24, '#fff', true); txt(ctx, `振幅 ≈ ${Math.round(amp / D2R)}°`, gx + 230, gy + gh + 86, 24, '#ffe066', true);
  if (t > 35.6) { ctx.globalAlpha = A * clamp((t - 35.6) / 0.5); txt(ctx, `相位差 φ ≈ ${Math.round(phaseDeg(t))}°（摆轮落后驱动）`, gx + 10, gy + gh + 128, 22, '#ff9a8a', true); }
  ctx.globalAlpha = 1;
}
function eqPanel(ctx, t) {
  const A = win(t, 41.8, 50.3, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(120,190,255,0.5)', PX, PY, PW, PH2);
  txt(ctx, '运动方程与稳态解', PX + 24, PY + 36, 24, '#8fd0ff', true);
  const x0 = PX + 30; let y = PY + 100; const s = 30;
  ctx.globalAlpha = A * clamp((t - 42.4) / 0.6); txt(ctx, 'J θ\u0308 + b θ\u0307 + k θ = M₀ cos ωt', x0, y, s, '#fff');
  y += 44; ctx.globalAlpha = A * clamp((t - 44.5) / 0.6); txt(ctx, '惯性      阻尼      弹性        驱动', x0 + 8, y, 16, '#9aa4b0');
  y += 50; ctx.globalAlpha = A * clamp((t - 46.0) / 0.6); txt(ctx, '令 2β = b/J，ω₀² = k/J，稳态解：', x0, y, 20, '#ffd27a');
  y += 46; txt(ctx, 'θ = θ₂ cos(ωt − φ)', x0, y, s, '#fff');
  y += 70; ctx.globalAlpha = A * clamp((t - 47.2) / 0.6); let x = x0; x += txt(ctx, 'θ₂ = ', x, y, 28, '#fff'); frac(ctx, x, y, 'M₀ / J', '√[(ω₀² − ω²)² + 4β²ω²]', 26, '#ffe066');
  y += 84; ctx.globalAlpha = A * clamp((t - 48.3) / 0.6); x = x0; x += txt(ctx, 'tan φ = ', x, y, 28, '#fff'); frac(ctx, x, y, '2βω', 'ω₀² − ω²', 28, '#ff9a8a');
  y += 64; ctx.globalAlpha = A * clamp((t - 49.0) / 0.6); txt(ctx, 'ω = ω₀ 附近：θ₂ 最大，φ = 90°', x0, y, 20, '#9aa4b0');
  ctx.globalAlpha = 1;
}
function curvePanel(ctx, t) {
  const A = win(t, 50.5, 59.2, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(255,170,120,0.5)', PX, PY, PW, PH2);
  txt(ctx, '幅频特性与相频特性', PX + 24, PY + 36, 24, '#ffb08a', true);
  const Z = [[0.05, '#ff6b6b', '小阻尼'], [0.1, '#ffd24a', '中阻尼'], [0.2, '#6fb8ff', '大阻尼']];
  const gx = PX + 60, gw = PW - 90, g1 = PY + 80, h1 = 200, g2 = PY + 330, h2 = 130; const r0 = 0.5, r1 = 1.5;
  axes(ctx, gx, g1, gw, h1, '', 'θ₂'); axes(ctx, gx, g2, gw, h2, 'ω / ω₀', 'φ');
  const X = r => gx + gw * (r - r0) / (r1 - r0);
  ctx.setLineDash([5, 5]); ctx.strokeStyle = 'rgba(255,255,255,0.3)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(X(1), g1); ctx.lineTo(X(1), g2 + h2); ctx.stroke(); ctx.setLineDash([]);
  txt(ctx, '1', X(1), g2 + h2 + 18, 14, '#aab', false, 'center'); txt(ctx, '180°', gx - 6, g2 + 4, 13, '#aab', false, 'right'); txt(ctx, '90°', gx - 6, g2 + h2 / 2, 13, '#aab', false, 'right'); txt(ctx, '0', gx - 6, g2 + h2, 13, '#aab', false, 'right');
  const prog = ease((t - 50.9) / 5.0);
  Z.forEach(([z, col, name], i) => {
    const amp = r => 1 / Math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2), ph = r => Math.atan2(2 * z * r, 1 - r * r);
    const rEnd = lerp(r0, r1, prog); ctx.strokeStyle = col; ctx.lineWidth = 2.4;
    ctx.beginPath(); for (let r = r0; r <= rEnd; r += 0.004) { const y = g1 + h1 - h1 * Math.min(1, amp(r) / 10.5); r === r0 ? ctx.moveTo(X(r), y) : ctx.lineTo(X(r), y); } ctx.stroke();
    ctx.beginPath(); for (let r = r0; r <= rEnd; r += 0.004) { const y = g2 + h2 - h2 * ph(r) / Math.PI; r === r0 ? ctx.moveTo(X(r), y) : ctx.lineTo(X(r), y); } ctx.stroke();
    ctx.fillStyle = col; ctx.fillRect(PX + 40 + i * 150, PY + PH2 - 30, 18, 4); txt(ctx, name, PX + 64 + i * 150, PY + PH2 - 28, 16, col, true);
  });
  ctx.globalAlpha = 1;
}

function subtitle(ctx, t) {
  for (const [a, b, s] of subTimes) if (t >= a - 0.05 && t < b + 0.05) {
    const A = clamp((t - a + 0.05) / 0.15) * clamp((b + 0.05 - t) / 0.15); ctx.globalAlpha = A; ctx.font = `34px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const w = measureRich(ctx, s); ctx.fillStyle = 'rgba(0,0,0,0.55)'; rr(ctx, W / 2 - w / 2 - 20, H - 78, w + 40, 52, 10); ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(0,0,0,0.8)'; ctx.fillStyle = '#fff'; fillRich(ctx, s, W / 2, H - 52, true); ctx.globalAlpha = 1;
  }
}
function flashAt(t) { if (t < 35.8 || t > 41.3) return 0; const ph = sample(PH, t); const k = Math.floor(ph / 6.283); // last crossing time
  let tt = t; for (let i = 0; i < 40; i++) { tt -= 1 / 240; if (Math.floor(sample(PH, tt) / 6.283) < k) break; } const dt = t - tt; return dt < 0.15 ? 1 - dt / 0.15 : 0; }

function render(ctx, t) {
  setCam(t); background(ctx);
  const th = theta(t), thd = thetaD(t);
  const I = t < T_REL1 ? 0 : t < T_GRAB2 ? 0.35 : t < T_MOTOR ? 1 : 0.5;
  const F = flashAt(t);
  basePlate(ctx); scaleRing(ctx); coil(ctx, false, I); flashLamp(ctx, t, F);
  wheel(ctx, th); coil(ctx, true, I); driveTrain(ctx, t, thd); spring(ctx, th, thd);
  // grabbing hand hint
  if ((t > 8.3 && t < T_REL1) || (t > T_GRAB2 && t < T_REL2)) { const p = P(rot(Math.PI / 2 + th, 5.3, 1.2)); ctx.fillStyle = 'rgba(255,220,180,0.9)'; ctx.beginPath(); ctx.arc(p[0], p[1], 9, 0, 6.283); ctx.fill(); txt(ctx, '扭转', p[0] + 14, p[1] - 14, 16, '#ffe0b0', true); }
  // flash
  if (F > 0) { ctx.globalAlpha = 0.35 * F; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; }
  if (t > 36 && t < 41.3) { const p = P(rot(Math.PI / 2 + th, 8.4, 1)); ctx.globalAlpha = win(t, 36, 41.3, 0.4); txt(ctx, '闪光定格读数', P([-8.3, 5.2, 3])[0], P([-8.3, 5.2, 3])[1], 16, '#fff', true, 'center'); ctx.globalAlpha = 1; }
  // intro labels
  const L = (a) => win(t, a, 9.5, 0.5);
  label3(ctx, [0, 12.5 + 3.4, 0.6], [-9.5, 4.5], ['摆轮', '铜质，可绕轴转动'], L(1.2), '#ffb07a');
  label3(ctx, [1.6, 12.5 + 1.2, 1.1], [-12, -1], ['蜗卷弹簧', '提供回复力矩'], L(2.4), '#d9e2ec');
  label3(ctx, [0, 7.6, 1.3], [-9.5, -3.2], ['电磁阻尼线圈', '电流越大阻尼越大'], L(3.6), '#8fd0ff');
  label3(ctx, [MOT[0], MOT[1], 0.6], [7.5, -1], ['电机 + 相位盘', '提供周期性驱动'], L(5.0), '#7fe0a8');
  label3(ctx, [TIP0[0] - 1.5, TIP0[1] + 0.5, 0.9], [8, 4], ['摇杆 · 连杆', '扭动弹簧外端'], L(5.9), '#e0c060');
  label3(ctx, [0, 12.5 + 7, -0.5], [9, 2.5], ['角度盘', '指针读振幅'], L(6.8), '#e8e4d6');
  dampPanel(ctx, t); forcedPanel(ctx, t); eqPanel(ctx, t); curvePanel(ctx, t);
  const tA = win(t, 0.2, 3.2, 0.6); if (tA > 0) { ctx.globalAlpha = tA; txt(ctx, '波尔共振实验', 48, 60, 42, '#fff', true); txt(ctx, 'Bohr Resonance · 阻尼 / 受迫振动 / 共振', 50, 102, 20, '#9fb3c8'); ctx.globalAlpha = 1; }
  const eA = clamp((t - 58.95) / 0.6);
  if (eA > 0) { ctx.globalAlpha = eA * 0.65; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = eA; txt(ctx, '驱动频率 ≈ 固有频率 → 共振', W / 2, H / 2 - 30, 44, '#fff', true, 'center'); txt(ctx, '振幅最大，相位差 90°', W / 2, H / 2 + 32, 30, '#ffe066', false, 'center'); ctx.globalAlpha = 1; }
  if (t < 58.95) subtitle(ctx, t);
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.45)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}
module.exports = { render };

if (require.main === module) {
  process.chdir(__dirname);
  const mode = process.argv[2] || 'video'; const cv = createCanvas(W, H), ctx = cv.getContext('2d');
  if (mode === 'still') { const fs = require('fs'); for (const t of process.argv.slice(3).map(Number)) { render(ctx, t); fs.writeFileSync(`still_${t}.png`, cv.toBuffer('image/png')); } return; }
  const ff = spawn(ffmpegBin(), ['-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', `${FPS}`, '-i', '-', '-i', 'mix.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'bohr_resonance.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  (async () => { const N = Math.round(DUR * FPS);
    for (let f = 0; f < N; f++) { render(ctx, f / FPS); const a = ctx.getImageData(0, 0, W, H).data; render(ctx, f / FPS + 0.25 / FPS); const b = ctx.getImageData(0, 0, W, H).data;
      const out = Buffer.alloc(a.length); for (let i = 0; i < a.length; i++) out[i] = (a[i] + b[i] + 1) >> 1; if (!ff.stdin.write(out)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); })();
}
