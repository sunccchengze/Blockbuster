// PINN · Physics-Informed Neural Networks — deterministic f(t) renderer (Blockbuster protocol)
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
const SUPM = { '²': '2', '⁻': '−', '⁺': '+' }, SUBM = { '₁': '1', '₂': '2', 'ₙ': 'n', 'ᵢ': 'i', '₃': '3', '₀': '0', 'ⱼ': 'j' };
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
const SEG = [[0.8, 12.08], [12.48, 20.02], [20.42, 31.73], [32.13, 42.20], [42.60, 47.61], [48.01, 58.85]];
const SUBS = [
  ['物理信息神经网络（PINN），', '是把物理定律写进训练过程的神经网络。', '先看一个问题：一个阻尼振子，', '我们只测到了最开始的十个数据点。'],
  ['普通神经网络只拟合数据，', '它能穿过这些点，', '但在没有数据的地方，预测完全失控。'],
  ['PINN 的做法是：网络输入时间，输出位移；', '再用自动微分，精确求出速度和加速度，', '代入振动方程，得到方程残差。'],
  ['总损失 = 数据误差 + 方程残差，', '残差在整个区间的配点上计算。', '训练让两者同时变小。'],
  ['结果，网络在没有数据的区域，', '也学会了正确的振动规律。'],
  ['更进一步，把未知的阻尼系数也设为可训练参数，', '网络还能从数据中把它反推出来，', '这就是求解反问题。'],
];
const subTimes = [];
SEG.forEach(([a, b], i) => { const L = SUBS[i].map(s => s.length); const T = L.reduce((x, y) => x + y); let t = a; SUBS[i].forEach((s, k) => { const d = (b - a) * L[k] / T; subTimes.push([t, t + d, s]); t += d; }); });

// ---------- real training data (from train.py, PyTorch) ----------
const DATA = JSON.parse(require('fs').readFileSync(__dirname + '/train_data.json', 'utf8'));
const TT = DATA.t;
function snapAt(run, p) { const S = DATA[run].snap, n = S.length; const x = clamp(p) * (n - 1), i = Math.floor(x), f = x - i; const a = S[i], b = S[Math.min(n - 1, i + 1)]; return a.map((v, k) => lerp(v, b[k], f)); }
function stepAt(run, p) { const S = DATA[run].step, n = S.length; const x = clamp(p) * (n - 1), i = Math.floor(x), f = x - i; return Math.round(lerp(S[i], S[Math.min(n - 1, i + 1)], f)); }
function histAt(run, key, p) { const S = DATA[run][key], n = S.length; const x = clamp(p) * (n - 1), i = Math.floor(x), f = x - i; return lerp(S[i], S[Math.min(n - 1, i + 1)], f); }
const L2 = run => { const s = DATA[run].snap[DATA[run].snap.length - 1]; return Math.sqrt(s.reduce((a, v, i) => a + (v - DATA.exact[i]) ** 2, 0) / s.length); };
const ERR_NN = L2('nn'), ERR_PINN = L2('pinn'), MU_FINAL = DATA.inv.mu[DATA.inv.mu.length - 1];

// ---------- camera ----------
const KEYS = [
  [0, [-6, 6, 50], [2, 0, 0]],
  [4.0, [-1, 4, 37], [8.5, 0, 0]],
  [20.4, [0, 4, 36], [8.5, 0, 0]],
  [22.0, [1, 5, 36], [8.5, 0, 0]],
  [58.4, [0, 5, 37], [8.5, 0, 0]],
  [60.4, [0, 6, 54], [3, 0, 0]],
];
function camAt(t) { let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++; const [t0, p0, g0] = KEYS[i], [t1, p1, g1] = KEYS[i + 1]; const x = ease((t - t0) / (t1 - t0)); return { pos: p0.map((v, k) => lerp(v, p1[k], x)), tgt: g0.map((v, k) => lerp(v, g1[k], x)) }; }
let CAM;
function setCam(t) { const { pos, tgt } = camAt(t); const f = norm(sub(tgt, pos)); const r = norm(cross(f, [0, 1, 0])); const u = cross(r, f); CAM = { pos, f, r, u, focal: (H / 2) / Math.tan(22 * Math.PI / 180) }; }
function P(p) { const d = sub(p, CAM.pos); const z = dot(d, CAM.f); return [W / 2 + CAM.focal * dot(d, CAM.r) / z, H / 2 - CAM.focal * dot(d, CAM.u) / z, z]; }
const scl = (p, r) => CAM.focal * r / P(p)[2];
function poly(ctx, pts) { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); }

// ---------- network geometry (3D) ----------
const LAYERS = [-14, -9, -4, 1];
const NODES = []; // {l, p}
NODES.push({ l: 0, p: [LAYERS[0], 0, 0] });
for (let l = 1; l <= 2; l++) for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) NODES.push({ l, p: [LAYERS[l], a * 3.0, b * 3.0] });
NODES.push({ l: 3, p: [LAYERS[3], 0, 0] });
const EDGES = []; for (let i = 0; i < NODES.length; i++) for (let j = 0; j < NODES.length; j++) if (NODES[j].l === NODES[i].l + 1) EDGES.push([i, j]);
// hidden layers visually 3: duplicate middle layer at LAYERS[2]? keep 2 hidden shown (label says 3×32)
const rngE = mulberry32(42); const PULSE = Array.from({ length: 40 }, () => ({ e: Math.floor(rngE() * EDGES.length), ph: rngE() }));
function yawAt(t) { return 0.3 * Math.sin(t * 0.22) + 0.05; }
function W3(p, t) { const a = yawAt(t), cx = -6.5; const x = p[0] - cx, z = p[2]; return [cx + x * Math.cos(a) + z * Math.sin(a), p[1], -x * Math.sin(a) + z * Math.cos(a)]; }

function background(ctx, t) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0d1422'); g.addColorStop(1, '#05070c'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // floor grid
  ctx.strokeStyle = 'rgba(90,150,255,0.07)'; ctx.lineWidth = 1;
  for (let x = -60; x <= 60; x += 4) { const a = P([x, -9, -30]), b = P([x, -9, 30]); if (a[2] > 0 && b[2] > 0) { ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); } }
  for (let z = -30; z <= 30; z += 4) { const a = P([-60, -9, z]), b = P([60, -9, z]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  const c = P([-6, 0, 0]); const rg = ctx.createRadialGradient(c[0], c[1], 10, c[0], c[1], 420); rg.addColorStop(0, 'rgba(60,120,255,0.10)'); rg.addColorStop(1, 'rgba(60,120,255,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
}
function node(ctx, s, r, col, A) { if (A <= 0) return; ctx.globalAlpha = A; const g = ctx.createRadialGradient(s[0] - r * 0.35, s[1] - r * 0.35, r * 0.1, s[0], s[1], r); g.addColorStop(0, '#ffffff'); g.addColorStop(0.3, col); g.addColorStop(1, 'rgba(0,0,0,0.9)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s[0], s[1], r, 0, 6.283); ctx.fill();
  const hg = ctx.createRadialGradient(s[0], s[1], r, s[0], s[1], r * 2.2); hg.addColorStop(0, col.replace('rgb', 'rgba').replace(')', ',0.25)')); hg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(s[0], s[1], r * 2.2, 0, 6.283); ctx.fill(); ctx.globalAlpha = 1; }
function tag(ctx, s, text, col, size = 20, dy = 0) { ctx.font = `${size}px ${FONTB}`; const w = measureRich(ctx, text); ctx.fillStyle = 'rgba(8,12,20,0.8)'; rr(ctx, s[0] - w / 2 - 8, s[1] + dy - size * 0.75, w + 16, size * 1.5, 6); ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 1.2; ctx.stroke(); ctx.fillStyle = col; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; fillRich(ctx, text, s[0], s[1] + dy); }
function arrow(ctx, a, b, col, lw = 2, A = 1) { ctx.globalAlpha = A; ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = lw; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); const an = Math.atan2(b[1] - a[1], b[0] - a[0]); ctx.beginPath(); ctx.moveTo(b[0], b[1]); ctx.lineTo(b[0] - 11 * Math.cos(an - 0.4), b[1] - 11 * Math.sin(an - 0.4)); ctx.lineTo(b[0] - 11 * Math.cos(an + 0.4), b[1] - 11 * Math.sin(an + 0.4)); ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1; }

function training(t) { return win(t, 12.8, 18.8, 0.3) + win(t, 34.0, 47.4, 0.3) + win(t, 49.0, 57.8, 0.3); }
function network(ctx, t) {
  const appear = i => clamp((t - 1.0 - i * 0.05) / 0.5);
  const S = NODES.map(n => P(W3(n.p, t)));
  const tr = training(t);
  // edges
  EDGES.forEach(([i, j], k) => { const A = Math.min(appear(i), appear(j)); if (A <= 0) return; ctx.globalAlpha = A * (0.12 + 0.12 * tr); ctx.strokeStyle = '#6fa8ff'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(S[i][0], S[i][1]); ctx.lineTo(S[j][0], S[j][1]); ctx.stroke(); });
  ctx.globalAlpha = 1;
  // pulses (forward during training, backward-ish colour for gradient)
  if (tr > 0.01) PULSE.forEach(p => { const [i, j] = EDGES[p.e]; const u = (p.ph + t * 1.3) % 1; const back = Math.floor(p.ph * 10) % 2; const a = back ? S[j] : S[i], b = back ? S[i] : S[j]; const x = lerp(a[0], b[0], u), y = lerp(a[1], b[1], u); ctx.globalAlpha = tr * Math.sin(u * Math.PI); ctx.fillStyle = back ? '#ff9a6b' : '#8fe3ff'; ctx.beginPath(); ctx.arc(x, y, 3, 0, 6.283); ctx.fill(); ctx.globalAlpha = 1; });
  // nodes sorted by depth
  NODES.map((n, i) => ({ n, i, s: S[i] })).sort((a, b) => b.s[2] - a.s[2]).forEach(({ n, i, s }) => {
    const r = scl(W3(n.p, t), n.l === 0 || n.l === 3 ? 1.0 : 0.62); const col = n.l === 0 ? 'rgb(120,220,255)' : n.l === 3 ? 'rgb(255,200,90)' : 'rgb(110,150,255)'; node(ctx, s, r, col, appear(i)); });
  const A0 = clamp((t - 2.0) / 0.6);
  if (A0 > 0) { ctx.globalAlpha = A0; tag(ctx, S[0], '输入 t', '#8fe3ff', 20, 50); tag(ctx, S[S.length - 1], '输出 u(t)', '#ffd27a', 20, 50);
    const mid = P(W3([(LAYERS[1] + LAYERS[2]) / 2, -6.2, 0], t)); tag(ctx, mid, '隐藏层 3×32 · tanh', '#9fb8ff', 16); ctx.globalAlpha = 1; }
  return S;
}
// autodiff branch (world positions, not rotated, to the right of output)
function autodiff(ctx, t, S) {
  const A = win(t, 22.2, 47.8, 0.6) + win(t, 48.3, 60.4, 0.6); if (A <= 0) return;
  const out = S[S.length - 1];
  const p1 = P([5.0, 4.6, 0]), p2 = P([5.0, -4.6, 0]), pr = P([10.6, 0, 0]);
  const a1 = A * clamp((t - 23.2) / 0.6), a2 = A * clamp((t - 25.0) / 0.6), a3 = A * clamp((t - 28.0) / 0.6);
  arrow(ctx, out, [p1[0] - 34, p1[1] + 10], '#7fe0a8', 2, a1); ctx.globalAlpha = a1; tag(ctx, p1, 'u′ = du/dt', '#7fe0a8', 20); ctx.globalAlpha = 1;
  arrow(ctx, out, [p2[0] - 34, p2[1] - 10], '#7fe0a8', 2, a2); ctx.globalAlpha = a2; tag(ctx, p2, 'u″ = d²u/dt²', '#7fe0a8', 20); ctx.globalAlpha = 1;
  if (a1 > 0) { ctx.globalAlpha = a1; txt(ctx, '自动微分', p1[0], out[1], 17, '#b8f5d0', true, 'center'); ctx.globalAlpha = 1; }
  arrow(ctx, [p1[0] + 40, p1[1] + 12], [pr[0] - 30, pr[1] - 22], '#ff9a8a', 2, a3); arrow(ctx, [p2[0] + 40, p2[1] - 12], [pr[0] - 30, pr[1] + 22], '#ff9a8a', 2, a3);
  ctx.globalAlpha = a3; tag(ctx, pr, 'r = u″ + μu′ + ku', '#ff9a8a', 20); txt(ctx, '方程残差', pr[0], pr[1] + 34, 16, '#ffc0b8', true, 'center'); ctx.globalAlpha = 1;
  // trainable mu (inverse problem)
  const am = win(t, 48.6, 60.4, 0.6); if (am > 0) { const pm = P([10.6, 6.8, 0]); const pulse = 0.6 + 0.4 * Math.sin(t * 5); node(ctx, pm, scl([10.6, 6.8, 0], 0.9), 'rgb(255,120,200)', am); ctx.globalAlpha = am; txt(ctx, 'μ', pm[0], pm[1], 20, '#fff', true, 'center'); tag(ctx, pm, `可训练参数 μ ≈ ${Math.max(0, histAt('inv', 'mu', clamp((t - 49.0) / 8.8))).toFixed(2)}`, '#ff9ad8', 17, -40 - pulse * 0); arrow(ctx, [pm[0], pm[1] + 18], [pr[0], pr[1] - 20], '#ff9ad8', 2, am); ctx.globalAlpha = 1; }
}

// ---------- 2D panels ----------
const PX = 795, PY = 60, PW = 460, PH2 = 520;
function chart(ctx, x, y, w, h, opt, A) {
  ctx.globalAlpha = A; const X = t => x + w * t, Y = u => y + h / 2 - u / 1.25 * h / 2;
  ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + h); ctx.moveTo(x, Y(0)); ctx.lineTo(x + w, Y(0)); ctx.stroke();
  txt(ctx, 'u', x - 6, y - 10, 15, '#aab4c0', true, 'right'); txt(ctx, 't', x + w + 4, Y(0) + 14, 15, '#aab4c0', true); txt(ctx, '0', x - 4, Y(0) + 12, 13, '#aab', false, 'right'); txt(ctx, '1', x + w, Y(0) + 14, 13, '#aab', false, 'center');
  if (opt.nodata) { ctx.fillStyle = 'rgba(255,255,255,0.04)'; ctx.fillRect(X(0.36), y, w * 0.64, h); txt(ctx, '无数据区域', X(0.68), y + 14, 14, '#8894a0', false, 'center'); }
  if (opt.colloc) { ctx.strokeStyle = `rgba(127,240,176,${0.9 * opt.colloc})`; ctx.lineWidth = 2; DATA.tc.forEach(tc => { ctx.beginPath(); ctx.moveTo(X(tc), y + h - 2); ctx.lineTo(X(tc), y + h - 12); ctx.stroke(); }); ctx.globalAlpha = A * opt.colloc; txt(ctx, '配点（算残差）', x + w, y + h + 14, 13, '#7ff0b0', false, 'right'); ctx.globalAlpha = A; }
  ctx.save(); ctx.beginPath(); ctx.rect(x, y - 4, w + 2, h + 8); ctx.clip();
  if (opt.exact) { ctx.setLineDash([6, 5]); ctx.strokeStyle = `rgba(200,210,225,${0.7 * opt.exact})`; ctx.lineWidth = 1.6; ctx.beginPath(); const n = Math.floor(TT.length * clamp(opt.exactDraw ?? 1)); for (let i = 0; i < n; i++) { const px = X(TT[i]), py = Y(DATA.exact[i]); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.stroke(); ctx.setLineDash([]); }
  (opt.curves || []).forEach(([u, col]) => { ctx.strokeStyle = col; ctx.lineWidth = 2.8; ctx.beginPath(); u.forEach((v, i) => { const px = X(TT[i]), py = Y(v); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }); ctx.stroke(); });
  ctx.restore();
  if (opt.data) DATA.td.forEach((td, i) => { const a = clamp(opt.data * 10 - i); if (a <= 0) return; ctx.globalAlpha = A * a; ctx.fillStyle = '#ff5a5a'; ctx.beginPath(); ctx.arc(X(td), Y(DATA.ud[i]), 5, 0, 6.283); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.2; ctx.stroke(); });
  ctx.globalAlpha = 1;
}
function legend(ctx, x, y, items, A) { ctx.globalAlpha = A; let cx = x; items.forEach(([col, name, dash]) => { ctx.strokeStyle = col; ctx.lineWidth = 3; if (dash) ctx.setLineDash([5, 4]); ctx.beginPath(); ctx.moveTo(cx, y); ctx.lineTo(cx + 22, y); ctx.stroke(); ctx.setLineDash([]); const w = txt(ctx, name, cx + 28, y, 15, '#dfe6ee'); cx += w + 50; }); ctx.globalAlpha = 1; }

function problemPanel(ctx, t) {
  const A = win(t, 3.6, 20.2, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(120,190,255,0.5)', PX, PY, PW, PH2);
  const nnP = clamp((t - 12.9) / 5.6); const sub = t > 12.5;
  txt(ctx, sub ? '普通神经网络：只拟合数据' : '问题：阻尼振子', PX + 24, PY + 36, 24, sub ? '#ffb45a' : '#8fd0ff', true);
  ctx.globalAlpha = A; txt(ctx, 'u″ + μu′ + ku = 0,  μ = 4, k = 400', PX + 24, PY + 78, 19, '#cfd8e3');
  const curves = sub ? [[snapAt('nn', nnP), '#ffb45a']] : [];
  chart(ctx, PX + 50, PY + 120, PW - 80, 280, { exact: clamp((t - 5.0) / 0.6), exactDraw: (t - 5.0) / 2.5, data: clamp((t - 8.6) / 2.0), nodata: t > 10.2, curves }, A);
  legend(ctx, PX + 30, PY + 440, [['#c8d2e1', '真实解（训练时未知）', true], ['#ff5a5a', '10 个观测点']], A * clamp((t - 8.6) / 0.6));
  if (sub) { ctx.globalAlpha = A; txt(ctx, `训练步数 ${stepAt('nn', nnP)}`, PX + 30, PY + 480, 18, '#ffc98a', true); if (t > 17.6) { ctx.globalAlpha = A * clamp((t - 17.6) / 0.5); txt(ctx, '无数据处：预测失控 ✗', PX + 230, PY + 480, 18, '#ff7b7b', true); } }
  ctx.globalAlpha = 1;
}
function methodPanel(ctx, t) {
  const A = win(t, 21.0, 31.9, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(127,224,168,0.5)', PX, PY, PW, PH2);
  txt(ctx, 'PINN：把方程变成约束', PX + 24, PY + 36, 24, '#7fe0a8', true);
  const rows = [[21.6, '1. 网络 NN(t; θ) 近似解 u(t)', '#fff'], [23.4, '2. 自动微分：精确求 u′、u″', '#fff'], [23.9, '（不是数值差分，无截断误差）', '#9aa4b0'], [26.8, '3. 代入方程得到残差：', '#fff'], [27.6, 'r(t) = u″ + μu′ + ku', '#ff9a8a'], [29.3, '4. r(t) ≈ 0 ⇔ 满足物理规律', '#ffe066']];
  rows.forEach(([ts, s, col], i) => { ctx.globalAlpha = A * clamp((t - ts) / 0.5); txt(ctx, s, PX + 30, PY + 100 + i * 58, i === 4 ? 28 : 21, col, i === 4 || i === 5); });
  ctx.globalAlpha = 1;
}
function lossPanel(ctx, t) {
  const A = win(t, 32.2, 47.9, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(255,200,120,0.5)', PX, PY, PW, PH2);
  const res = t > 42.5; txt(ctx, res ? '结果：PINN 预测' : '损失函数与训练', PX + 24, PY + 36, 24, res ? '#7fe0a8' : '#ffc57a', true);
  // loss formula
  ctx.globalAlpha = A * clamp((t - 32.6) / 0.6); let x = PX + 24, y = PY + 92;
  x += txt(ctx, 'L = ', x, y, 24, '#fff'); x += frac(ctx, x, y, '1', 'N', 20) + 4; x += txt(ctx, 'Σ(u(tᵢ) − uᵢ)²', x, y, 22, '#ff9a9a');
  ctx.globalAlpha = A * clamp((t - 34.0) / 0.6); x += txt(ctx, ' + λ', x, y, 22, '#fff'); x += frac(ctx, x, y, '1', 'M', 20) + 4; txt(ctx, 'Σ r(tⱼ)²', x, y, 22, '#7ff0b0');
  ctx.globalAlpha = A * clamp((t - 33.2) / 0.6); txt(ctx, '数据误差（10 点）', PX + 90, PY + 132, 15, '#ffb0b0'); ctx.globalAlpha = A * clamp((t - 34.4) / 0.6); txt(ctx, '方程残差（40 个配点）', PX + 280, PY + 132, 15, '#a8f5c8');
  const p = clamp((t - 35.4) / 11.2);
  chart(ctx, PX + 50, PY + 175, PW - 80, 230, { exact: 1, data: 1, nodata: true, colloc: clamp((t - 36.4) / 0.6), curves: t > 35.4 ? [[snapAt('pinn', p), '#7fe0a8']] : [] }, A);
  ctx.globalAlpha = A; if (t > 35.4) txt(ctx, `训练步数 ${stepAt('pinn', p)}`, PX + 30, PY + 440, 18, '#a8f5c8', true);
  if (t > 43.4) { ctx.globalAlpha = A * clamp((t - 43.4) / 0.6); txt(ctx, `全区间误差（RMSE）：普通网络 ${ERR_NN.toFixed(2)}  →  PINN ${ERR_PINN.toFixed(3)}`, PX + 30, PY + 480, 16, '#ffe066', true); }
  ctx.globalAlpha = 1;
}
function inversePanel(ctx, t) {
  const A = win(t, 48.3, 59.0, 0.6); if (A <= 0) return; panel(ctx, A, 'rgba(255,154,216,0.5)', PX, PY, PW, PH2);
  txt(ctx, '反问题：从数据反推 μ', PX + 24, PY + 36, 24, '#ff9ad8', true);
  const p = clamp((t - 49.0) / 8.8);
  chart(ctx, PX + 50, PY + 80, PW - 80, 170, { exact: 1, data: 1, nodata: true, curves: [[snapAt('inv', p), '#ff9ad8']] }, A);
  // mu history
  const gx = PX + 60, gy = PY + 300, gw = PW - 100, gh = 130; ctx.globalAlpha = A; ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx, gy + gh); ctx.lineTo(gx + gw, gy + gh); ctx.stroke();
  txt(ctx, 'μ', gx - 6, gy - 10, 16, '#aab4c0', true, 'right'); txt(ctx, '训练步数（对数）', gx + gw, gy + gh + 16, 13, '#aab4c0', false, 'right');
  const Y = m => gy + gh - gh * m / 5; ctx.setLineDash([5, 5]); ctx.strokeStyle = 'rgba(255,224,102,0.8)'; ctx.beginPath(); ctx.moveTo(gx, Y(4)); ctx.lineTo(gx + gw, Y(4)); ctx.stroke(); ctx.setLineDash([]); txt(ctx, '真值 4', gx + gw - 4, Y(4) - 12, 13, '#ffe066', true, 'right');
  const M = DATA.inv.mu, n = M.length, k = Math.floor(p * (n - 1)); ctx.strokeStyle = '#ff9ad8'; ctx.lineWidth = 2.6; ctx.beginPath(); for (let i = 0; i <= k; i++) { const px = gx + gw * i / (n - 1), py = Y(clamp(M[i], 0, 5)); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.stroke();
  txt(ctx, `μ 估计 = ${Math.max(0, histAt('inv', 'mu', p)).toFixed(2)}`, PX + 30, PY + 480, 22, '#ff9ad8', true); if (p > 0.97) { ctx.globalAlpha = A * clamp((t - 57.3) / 0.5); txt(ctx, `真值 4，误差约 ${Math.abs(MU_FINAL / 4 - 1) * 100 | 0}%`, PX + 250, PY + 480, 18, '#ffe066', true); }
  ctx.globalAlpha = 1;
}

function subtitle(ctx, t) {
  for (const [a, b, s] of subTimes) if (t >= a - 0.05 && t < b + 0.05) {
    const A = clamp((t - a + 0.05) / 0.15) * clamp((b + 0.05 - t) / 0.15); ctx.globalAlpha = A; ctx.font = `34px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const w = measureRich(ctx, s); ctx.fillStyle = 'rgba(0,0,0,0.55)'; rr(ctx, W / 2 - w / 2 - 20, H - 78, w + 40, 52, 10); ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(0,0,0,0.8)'; ctx.fillStyle = '#fff'; fillRich(ctx, s, W / 2, H - 52, true); ctx.globalAlpha = 1;
  }
}

function render(ctx, t) {
  setCam(t); background(ctx, t);
  const S = network(ctx, t); autodiff(ctx, t, S);
  problemPanel(ctx, t); methodPanel(ctx, t); lossPanel(ctx, t); inversePanel(ctx, t);
  const tA = win(t, 0.2, 3.4, 0.6); if (tA > 0) { ctx.globalAlpha = tA; txt(ctx, 'PINN · 物理信息神经网络', 48, 60, 40, '#fff', true); txt(ctx, 'Physics-Informed Neural Networks', 50, 102, 20, '#9fb3c8'); ctx.globalAlpha = 1; }
  const eA = clamp((t - 58.9) / 0.6);
  if (eA > 0) { ctx.globalAlpha = eA * 0.7; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = eA; txt(ctx, 'PINN = 神经网络 + 物理方程约束', W / 2, H / 2 - 30, 44, '#fff', true, 'center'); txt(ctx, 'L = 数据误差 + λ · 方程残差', W / 2, H / 2 + 32, 28, '#7fe0a8', false, 'center'); ctx.globalAlpha = 1; }
  if (t < 58.9) subtitle(ctx, t);
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.45)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}
module.exports = { render };

if (require.main === module) {
  process.chdir(__dirname);
  const mode = process.argv[2] || 'video'; const cv = createCanvas(W, H), ctx = cv.getContext('2d');
  if (mode === 'still') { const fs = require('fs'); for (const t of process.argv.slice(3).map(Number)) { render(ctx, t); fs.writeFileSync(`still_${t}.png`, cv.toBuffer('image/png')); } return; }
  const ff = spawn(ffmpegBin(), ['-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', `${FPS}`, '-i', '-', '-i', 'mix.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'pinn_explained.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  (async () => { const N = Math.round(DUR * FPS);
    for (let f = 0; f < N; f++) { render(ctx, f / FPS); const a = ctx.getImageData(0, 0, W, H).data; render(ctx, f / FPS + 0.25 / FPS); const b = ctx.getImageData(0, 0, W, H).data;
      const out = Buffer.alloc(a.length); for (let i = 0; i < a.length; i++) out[i] = (a[i] + b[i] + 1) >> 1; if (!ff.stdin.write(out)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); })();
}
