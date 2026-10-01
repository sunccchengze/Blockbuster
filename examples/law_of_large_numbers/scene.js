// 大数定律 · Law of Large Numbers — deterministic f(t) renderer (Blockbuster protocol)
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
const SUPM = { '²': '2', '⁻': '−', '⁺': '+' }, SUBM = { '₁': '1', '₂': '2', 'ₙ': 'n', 'ᵢ': 'i', '₃': '3' };
function parseFont(ctx) { const m = /(\d+)px (.*)/.exec(ctx.font); return [+m[1], m[2]]; }
function measureRich(ctx, s) { const f = ctx.font, [sz, fam] = parseFont(ctx); let w = 0; for (const ch of s) { if (ch === '\u0304') continue; if (SUPM[ch] || SUBM[ch]) { ctx.font = `${Math.round(sz * 0.62)}px ${fam}`; w += ctx.measureText(SUPM[ch] || SUBM[ch]).width; ctx.font = f; } else w += ctx.measureText(ch).width; } return w; }
function fillRich(ctx, s, x, y, stroke) {
  const f = ctx.font, [sz, fam] = parseFont(ctx), al = ctx.textAlign, w = measureRich(ctx, s);
  let cx = al === 'center' ? x - w / 2 : al === 'right' ? x - w : x; ctx.textAlign = 'left'; let lastX = cx, lastW = 0;
  for (const ch of s) {
    if (ch === '\u0304') { ctx.fillRect(lastX + lastW * 0.1, y - sz * 0.62, lastW * 0.8, Math.max(1.5, sz * 0.07)); continue; }
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
const SEG = [[0.8, 10.07], [10.47, 18.57], [18.97, 32.20], [33.20, 41.71], [42.99, 47.70], [48.10, 58.96]];
const SUBS = [
  ['抛一枚均匀硬币，正面朝上的概率是二分之一。', '可抛十次，出现七次正面也不奇怪。', '那么，概率到底体现在哪里？'],
  ['答案是：多抛。', '记录正面出现的频率，随着次数增加，', '它的波动越来越小，逐渐稳定在 0.5 附近。'],
  ['这就是大数定律。', '设随机变量独立同分布，期望为 μ。', '对任意正数 ε，样本均值与 μ 相差超过 ε 的概率，', '随着 n 趋于无穷而趋于零。'],
  ['由切比雪夫不等式，', '这个概率不超过方差除以 n 乘 ε 的平方。', 'n 越大，上界越小。'],
  ['换成骰子也一样：', '掷得越多，点数的平均值越接近 3.5。'],
  ['注意，大数定律不是说前面的偏差会被补偿，', '而是被海量数据稀释。', '频率稳定于概率，', '这正是保险定价和蒙特卡洛模拟的基础。'],
];
const subTimes = [];
SEG.forEach(([a, b], i) => { const L = SUBS[i].map(s => s.length); const T = L.reduce((x, y) => x + y); let t = a; SUBS[i].forEach((s, k) => { const d = (b - a) * L[k] / T; subTimes.push([t, t + d, s]); t += d; }); });

// ---------- data (seeded) ----------
const NMAX = 10000;
const FIRST10 = [1, 0, 1, 1, 0, 1, 1, 1, 0, 1]; // 7 heads
function trajectory(seed, fixed) { const r = mulberry32(seed); const f = new Float32Array(NMAX + 1); let h = 0; for (let n = 1; n <= NMAX; n++) { const x = fixed && n <= 10 ? fixed[n - 1] : (r() < 0.5 ? 1 : 0); h += x; f[n] = h / n; } return f; }
const MAIN = trajectory(7, FIRST10);
const OTHERS = Array.from({ length: 40 }, (_, i) => trajectory(1000 + i * 17));
const EPS = 0.05;
// empirical P(|f-0.5|>=eps) over 400 runs at checkpoints
const CHECK = []; for (let k = 0; k <= 40; k++) CHECK.push(Math.round(Math.pow(10, 1 + 3 * k / 40)));
const EMP = (() => { const cnt = new Array(CHECK.length).fill(0); const R = 400; for (let i = 0; i < R; i++) { const r = mulberry32(50000 + i); let h = 0, c = 0; for (let n = 1; n <= NMAX; n++) { h += r() < 0.5 ? 1 : 0; if (n === CHECK[c]) { if (Math.abs(h / n - 0.5) >= EPS) cnt[c]++; c++; while (c < CHECK.length && CHECK[c] === CHECK[c - 1]) { cnt[c] = cnt[c - 1] - (Math.abs(h / n - 0.5) >= EPS ? 0 : 0); c++; } } } } return cnt.map(x => x / R); })();
// dice
const DICE = (() => { const r = mulberry32(99); return Array.from({ length: 3000 }, () => 1 + Math.floor(r() * 6)); })();
// monte carlo points
const MC = (() => { const r = mulberry32(3141); return Array.from({ length: 4000 }, () => [r(), r()]); })();

// ---------- camera ----------
const KEYS = [
  [0, [0, 16, 36], [0, 3, 3]],
  [9.8, [3, 15, 34], [0, 3, 3]],
  [11.6, [0, 12, 44], [0, 11, -6]],
  [18.6, [-1, 12, 43], [0, 11, -6]],
  [20.4, [4, 12, 48], [12, 11, -6]],
  [42.4, [5, 12, 48], [12, 11, -6]],
  [43.6, [-6, 11, 24], [3, 3, 5]],
  [47.6, [-4, 11, 23], [3, 3, 5]],
  [48.9, [4, 12, 48], [12, 11, -6]],
  [58.4, [5, 12, 49], [12, 11, -6]],
  [60.4, [0, 14, 52], [3, 10, -6]],
];
function camAt(t) { let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++; const [t0, p0, g0] = KEYS[i], [t1, p1, g1] = KEYS[i + 1]; const x = ease((t - t0) / (t1 - t0)); return { pos: p0.map((v, k) => lerp(v, p1[k], x)), tgt: g0.map((v, k) => lerp(v, g1[k], x)) }; }
let CAM;
function setCam(t) { const { pos, tgt } = camAt(t); const f = norm(sub(tgt, pos)); const r = norm(cross(f, [0, 1, 0])); const u = cross(r, f); CAM = { pos, f, r, u, focal: (H / 2) / Math.tan(22 * Math.PI / 180) }; }
function P(p) { const d = sub(p, CAM.pos); const z = dot(d, CAM.f); return [W / 2 + CAM.focal * dot(d, CAM.r) / z, H / 2 - CAM.focal * dot(d, CAM.u) / z, z]; }
const scl = (p, r) => CAM.focal * r / P(p)[2];
function poly(ctx, pts) { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); }

// ---------- environment ----------
function background(ctx) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#1d2128'); g.addColorStop(1, '#0b0c0f'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // wall grid
  ctx.strokeStyle = 'rgba(255,255,255,0.03)'; ctx.lineWidth = 1;
  for (let x = -60; x <= 60; x += 6) { const a = P([x, 0, -12]), b = P([x, 50, -12]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  // wooden table top
  const c = [[-40, 0, -10], [40, 0, -10], [40, 0, 30], [-40, 0, 30]].map(P); poly(ctx, c);
  const tg = ctx.createLinearGradient(0, c[0][1], 0, H); tg.addColorStop(0, '#3b2a1e'); tg.addColorStop(1, '#1a120c'); ctx.fillStyle = tg; ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.18)'; ctx.lineWidth = 1.2;
  for (let z = -10; z <= 30; z += 1.3) { const a = P([-40, 0.001, z]), b = P([40, 0.001, z + 0.4]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  const lp = P([0, 0, 4]); const rg = ctx.createRadialGradient(lp[0], lp[1], 10, lp[0], lp[1], Math.max(50, scl([0, 0, 4], 28))); rg.addColorStop(0, 'rgba(255,230,190,0.16)'); rg.addColorStop(1, 'rgba(255,230,190,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
}

// ---------- coin ----------
function coin(ctx, c, ang, head, r = 1.3, alpha = 1) {
  // disc normal rotates around x-axis: n = (0, cos a, sin a)
  const n = [0, Math.cos(ang), Math.sin(ang)], e1 = [1, 0, 0], e2 = norm(cross(n, e1));
  const th = 0.12, rim = [], top = [], bot = [];
  for (let i = 0; i < 36; i++) { const a = i / 36 * 6.283; const v = [e1[0] * Math.cos(a) + e2[0] * Math.sin(a), e1[1] * Math.cos(a) + e2[1] * Math.sin(a), e1[2] * Math.cos(a) + e2[2] * Math.sin(a)];
    top.push(P([c[0] + v[0] * r + n[0] * th, c[1] + v[1] * r + n[1] * th, c[2] + v[2] * r + n[2] * th])); bot.push(P([c[0] + v[0] * r - n[0] * th, c[1] + v[1] * r - n[1] * th, c[2] + v[2] * r - n[2] * th])); }
  ctx.globalAlpha = alpha;
  const view = norm(sub(CAM.pos, c)); const facing = dot(n, view); const face = facing > 0 ? top : bot; const back = facing > 0 ? bot : top;
  poly(ctx, back); ctx.fillStyle = '#6e5316'; ctx.fill();
  // rim fill via hull of both
  ctx.fillStyle = '#8a6a1c'; for (let i = 0; i < 36; i++) { const j = (i + 1) % 36; ctx.beginPath(); ctx.moveTo(top[i][0], top[i][1]); ctx.lineTo(top[j][0], top[j][1]); ctx.lineTo(bot[j][0], bot[j][1]); ctx.lineTo(bot[i][0], bot[i][1]); ctx.closePath(); ctx.fill(); }
  poly(ctx, face); const s = P(c); const rad = scl(c, r);
  const g = ctx.createLinearGradient(s[0] - rad, s[1] - rad, s[0] + rad, s[1] + rad); g.addColorStop(0, '#fff1b0'); g.addColorStop(0.45, '#e2b23c'); g.addColorStop(1, '#9c7420'); ctx.fillStyle = g; ctx.fill();
  ctx.strokeStyle = 'rgba(90,60,10,0.8)'; ctx.lineWidth = 1; ctx.stroke();
  const showHead = facing > 0 ? head : !head; const sq = Math.abs(facing);
  if (sq > 0.25 && rad > 6) { ctx.save(); ctx.translate(s[0], s[1]); ctx.scale(1, Math.max(0.25, Math.abs(dot(n, CAM.u)) * 0 + sq)); ctx.fillStyle = showHead ? '#7a4a00' : '#5a4a2a'; ctx.font = `${Math.round(rad * 1.0)}px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(showHead ? '正' : '反', 0, 0); ctx.restore(); }
  ctx.globalAlpha = 1;
}
const TOSS0 = 1.4, TOSSD = 0.82;
function coinScene(ctx, t) {
  const A = 1 - clamp((t - 11) / 1.2); if (A <= 0) return;
  let heads = 0, n = 0; const landed = [];
  for (let k = 0; k < 10; k++) {
    const t0 = TOSS0 + k * TOSSD, t1 = t0 + 0.75, slot = [-10.8 + k * 2.4, 1.15, 9];
    if (t >= t1) { landed.push([slot, FIRST10[k]]); n++; heads += FIRST10[k]; }
    else if (t >= t0) { const p = (t - t0) / 0.75; const start = [0, 1.5, 3]; const c = [lerp(start[0], slot[0], p), lerp(start[1], slot[1], p) + 9 * p * (1 - p) * 1.6, lerp(start[2], slot[2], p)];
      const final = FIRST10[k] ? Math.PI / 2 : -Math.PI / 2; const ang = final + (1 - p) * 6.283 * 3; coin(ctx, c, ang, true, 1.1, A); }
  }
  // shadows + landed coins (flat: normal up => ang = pi/2 shows 'top'=head)
  landed.forEach(([s, h]) => { const sh = P([s[0], 0.01, s[2] - 0.3]); ctx.globalAlpha = 0.4 * A; ctx.fillStyle = '#000'; ctx.beginPath(); ctx.ellipse(sh[0], sh[1], scl(s, 1.15), scl(s, 0.45), 0, 0, 6.283); ctx.fill(); ctx.globalAlpha = 1; coin(ctx, s, h ? Math.PI / 2 : -Math.PI / 2, true, 1.1, A); });
  // counter
  if (t > TOSS0) { ctx.globalAlpha = A; ctx.fillStyle = 'rgba(10,12,16,0.75)'; rr(ctx, W / 2 - 190, 36, 380, 70, 12); ctx.fill(); ctx.globalAlpha = A;
    txt(ctx, `正面 ${heads} / ${n} 次`, W / 2 - 160, 71, 30, '#ffe08a', true); txt(ctx, n ? `频率 ${(heads / n).toFixed(2)}` : '频率 —', W / 2 + 40, 71, 30, '#fff', true); }
  if (t > 7.0) { ctx.globalAlpha = A * clamp((t - 7.0) / 0.6) * (1 - clamp((t - 10.2) / 0.5)); txt(ctx, 'P(正) = 1/2 ，但 7/10 ≠ 1/2 ?', W / 2, 140, 28, '#8fd0ff', true, 'center'); }
  ctx.globalAlpha = 1;
}

// ---------- chart board (in 3D) ----------
const BX0 = -14, BX1 = 14, BY0 = 3, BY1 = 20, BZ = -6;
const cp = (n, f) => P([BX0 + 1.8 + (BX1 - BX0 - 3) * Math.log10(n) / 4, BY0 + 1.5 + (BY1 - BY0 - 3) * f, BZ]);
function board(ctx, t, A) {
  const c = [[BX0, BY0, BZ], [BX1, BY0, BZ], [BX1, BY1, BZ], [BX0, BY1, BZ]].map(P);
  ctx.globalAlpha = A; poly(ctx, c); ctx.fillStyle = 'rgba(14,20,28,0.92)'; ctx.fill(); ctx.strokeStyle = 'rgba(160,200,255,0.35)'; ctx.lineWidth = 2; ctx.stroke();
  // legs
  ctx.strokeStyle = 'rgba(80,80,90,0.9)'; ctx.lineWidth = 4; [[BX0 + 3, BX0 + 3], [BX1 - 3, BX1 - 3]].forEach(([x]) => { const a = P([x, 0, BZ]), b = P([x, BY0, BZ]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); });
  // grid & axes
  const fs = Math.max(10, scl([0, 10, BZ], 0.62));
  ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(255,255,255,0.10)';
  for (let e = 0; e <= 4; e++) { const a = cp(Math.pow(10, e), 0), b = cp(Math.pow(10, e), 1); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); txt(ctx, ['1', '10', '100', '1000', '10000'][e], a[0], a[1] + fs, fs, '#9aa4b0', false, 'center'); }
  for (const f of [0, 0.25, 0.5, 0.75, 1]) { const a = cp(1, f), b = cp(NMAX, f); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); txt(ctx, f.toFixed(2), a[0] - 6, a[1], fs, '#9aa4b0', false, 'right'); }
  ctx.globalAlpha = A; txt(ctx, '正面频率', cp(1, 1)[0] - 10, cp(1, 1)[1] - fs * 1.4, fs * 1.1, '#cfd8e3', true, 'left');
  txt(ctx, '抛掷次数 n（对数刻度）', cp(NMAX, 0)[0], cp(NMAX, 0)[1] + fs * 2.3, fs, '#cfd8e3', false, 'right');
  // p = 0.5 line
  const a = cp(1, 0.5), b = cp(NMAX, 0.5); ctx.setLineDash([8, 6]); ctx.strokeStyle = 'rgba(255,224,102,0.8)'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); ctx.setLineDash([]);
  txt(ctx, 'p = 0.5', b[0] + 6, b[1], fs, '#ffe066', true);
  ctx.globalAlpha = 1;
}
function drawTraj(ctx, f, nUpTo, col, lw, A) {
  if (nUpTo < 1) return; ctx.globalAlpha = A; ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.beginPath();
  let first = true; const steps = 360;
  for (let k = 0; k <= steps; k++) { const n = Math.max(1, Math.round(Math.pow(10, 4 * k / steps))); if (n > nUpTo) break; const p = cp(n, f[n]); first ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]); first = false; }
  const p = cp(nUpTo, f[Math.floor(nUpTo)]); ctx.lineTo(p[0], p[1]); ctx.stroke(); ctx.globalAlpha = 1; return p;
}
function chartScene(ctx, t) {
  const A = clamp((t - 10.6) / 1.0) * (1 - win(t, 43.1, 48.4, 0.8));
  if (A <= 0.01) return;
  board(ctx, t, A);
  // epsilon band
  const bA = A * clamp((t - 24.5) / 0.8);
  if (bA > 0) { const q = [cp(1, 0.5 + EPS), cp(NMAX, 0.5 + EPS), cp(NMAX, 0.5 - EPS), cp(1, 0.5 - EPS)]; ctx.globalAlpha = 0.22 * bA; poly(ctx, q); ctx.fillStyle = '#4fd18b'; ctx.fill(); ctx.globalAlpha = bA; txt(ctx, 'μ ± ε  (ε = 0.05)', q[1][0] - 4, q[1][1] - 12, Math.max(11, scl([0, 10, BZ], 0.55)), '#7ff0b0', true, 'right'); ctx.globalAlpha = 1; }
  // other trajectories
  const oA = A * clamp((t - 19.6) / 1.4);
  if (oA > 0) OTHERS.forEach((f, i) => drawTraj(ctx, f, NMAX * Math.min(1, Math.pow(clamp((t - 19.6 - i * 0.02) / 2.2), 1)) + 1, `hsla(${(i * 37) % 360},70%,65%,1)`, 1, oA * 0.35));
  // main trajectory progressive
  const p = clamp((t - 11.4) / 6.8); const nNow = Math.min(NMAX, Math.max(1, Math.pow(10, 4 * ease(p) * 0.999 + 0.0)));
  const end = drawTraj(ctx, MAIN, nNow, '#ffd24a', 3, A);
  if (end && t < 19.5) { ctx.globalAlpha = A; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(end[0], end[1], 5, 0, 6.283); ctx.fill();
    const n = Math.floor(nNow); ctx.fillStyle = 'rgba(10,12,16,0.8)'; rr(ctx, end[0] + 12, end[1] - 50, 190, 44, 8); ctx.fill(); txt(ctx, `n = ${n}   f = ${MAIN[n].toFixed(3)}`, end[0] + 22, end[1] - 28, 18, '#fff', true); ctx.globalAlpha = 1; }
  // scan line: fraction outside band (seg 3 end)
  const sA = A * win(t, 27.5, 33.2, 0.5);
  if (sA > 0) { const n = Math.round(Math.pow(10, 1 + 3 * ease((t - 27.6) / 5.2))); const a = cp(n, 0), b = cp(n, 1); ctx.globalAlpha = sA; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    let out = 0; OTHERS.forEach(f => { const q = cp(n, f[n]); const o = Math.abs(f[n] - 0.5) >= EPS; if (o) out++; ctx.fillStyle = o ? '#ff6b6b' : '#7ff0b0'; ctx.beginPath(); ctx.arc(q[0], q[1], 3.5, 0, 6.283); ctx.fill(); });
    ctx.fillStyle = 'rgba(10,12,16,0.8)'; rr(ctx, b[0] - 110, b[1] - 58, 220, 48, 8); ctx.fill(); txt(ctx, `n=${n}  带外 ${out}/40`, b[0], b[1] - 34, 18, out ? '#ff9a9a' : '#7ff0b0', true, 'center'); ctx.globalAlpha = 1; }
  // seg 6: gambler's fallacy annotation on board
  const gA = A * win(t, 48.6, 54.2, 0.6);
  if (gA > 0) { const q = cp(10, MAIN[10]); ctx.globalAlpha = gA; ctx.strokeStyle = '#ff9a6b'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(q[0], q[1], 12, 0, 6.283); ctx.stroke();
    ctx.fillStyle = 'rgba(10,12,16,0.85)'; rr(ctx, q[0] - 20, q[1] - 70, 190, 44, 8); ctx.fill(); txt(ctx, '前 10 次：7 正（多 2 个）', q[0] - 10, q[1] - 48, 16, '#ffb08a', true); ctx.globalAlpha = 1; }
}

// ---------- formula panels ----------
function lawPanel(ctx, t) {
  const A = win(t, 19.4, 33.2, 0.7); if (A <= 0) return; panel(ctx, A, 'rgba(120,190,255,0.5)');
  const px = 720; txt(ctx, '（弱）大数定律', px, 110, 26, '#8fd0ff', true);
  ctx.globalAlpha = A * clamp((t - 20.5) / 0.7);
  txt(ctx, 'X₁, X₂, …, Xₙ 独立同分布，E(Xᵢ) = μ', px, 170, 24, '#fff');
  let x = px; x += txt(ctx, 'X\u0304ₙ = ', x, 240, 30, '#fff'); x += frac(ctx, x, 240, '1', 'n', 30) + 6; txt(ctx, '(X₁ + … + Xₙ)', x, 240, 28, '#fff');
  ctx.globalAlpha = A * clamp((t - 23.8) / 0.7); txt(ctx, '对任意 ε > 0：', px, 320, 24, '#ffd27a');
  ctx.globalAlpha = A * clamp((t - 26.0) / 0.7);
  txt(ctx, 'lim', px + 10, 385, 32, '#fff'); txt(ctx, 'n→∞', px + 6, 415, 16, '#fff'); txt(ctx, 'P( |X\u0304ₙ − μ| ≥ ε ) = 0', px + 72, 385, 32, '#ffe066', true);
  ctx.globalAlpha = A * clamp((t - 28.0) / 0.7); txt(ctx, '硬币：Xᵢ ∈ {0,1}，μ = 0.5，X\u0304ₙ 就是正面频率', px, 480, 20, '#9aa4b0');
  txt(ctx, '右侧扫描线：带外轨迹随 n 增大而消失', px, 520, 20, '#9aa4b0'); ctx.globalAlpha = 1;
}
function chebPanel(ctx, t) {
  const A = win(t, 33.5, 42.8, 0.7); if (A <= 0) return; panel(ctx, A, 'rgba(255,200,120,0.5)');
  const px = 720; txt(ctx, '切比雪夫不等式给出上界', px, 110, 26, '#ffc57a', true);
  ctx.globalAlpha = A * clamp((t - 34.2) / 0.7);
  let x = px; x += txt(ctx, 'P( |X\u0304ₙ − μ| ≥ ε ) ≤ ', x, 180, 28, '#fff'); frac(ctx, x, 180, 'σ²', 'nε²', 30, '#ffe066');
  ctx.globalAlpha = A * clamp((t - 36.0) / 0.7); txt(ctx, '硬币：σ² = 0.25，ε = 0.05 ⇒ 上界 = 100 / n', px, 245, 20, '#9aa4b0');
  // mini log-log chart: bound vs empirical
  const gx = px + 50, gy = 285, gw = 430, gh = 200; const cA = A * clamp((t - 36.5) / 0.6); ctx.globalAlpha = cA;
  ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx, gy + gh); ctx.lineTo(gx + gw, gy + gh); ctx.stroke();
  txt(ctx, '1', gx - 14, gy + 6, 14, '#aab'); txt(ctx, '0', gx - 14, gy + gh, 14, '#aab'); txt(ctx, 'n: 10 → 10000（对数）', gx + gw, gy + gh + 20, 14, '#aab', false, 'right');
  const X = k => gx + gw * k / 40, Y = v => gy + gh - gh * clamp(v);
  const prog = clamp((t - 36.8) / 4.0); const kmax = Math.floor(40 * prog);
  ctx.strokeStyle = '#ffb45a'; ctx.lineWidth = 3; ctx.beginPath(); for (let k = 0; k <= kmax; k++) { const v = Math.min(1, 100 / CHECK[k]); k ? ctx.lineTo(X(k), Y(v)) : ctx.moveTo(X(k), Y(v)); } ctx.stroke();
  for (let k = 0; k <= kmax; k += 2) { ctx.fillStyle = 'rgba(127,240,176,0.85)'; const v = EMP[k]; ctx.fillRect(X(k) - 4, Y(v), 8, gy + gh - Y(v)); }
  ctx.fillStyle = '#ffb45a'; ctx.fillRect(gx + gw - 170, gy + 6, 16, 4); txt(ctx, '上界 σ²/(nε²)', gx + gw - 148, gy + 8, 14, '#ffd2a0');
  ctx.fillStyle = '#7ff0b0'; ctx.fillRect(gx + gw - 170, gy + 28, 16, 10); txt(ctx, '实测概率（400 次实验）', gx + gw - 148, gy + 33, 14, '#b8f5d0');
  ctx.globalAlpha = 1;
}

// ---------- dice ----------
const PIPS = { 1: [[0, 0]], 2: [[-1, -1], [1, 1]], 3: [[-1, -1], [0, 0], [1, 1]], 4: [[-1, -1], [1, -1], [-1, 1], [1, 1]], 5: [[-1, -1], [1, -1], [0, 0], [-1, 1], [1, 1]], 6: [[-1, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [1, 1]] };
function rotM(ax, ay, az) { const [ca, sa, cb, sb, cc, sc] = [Math.cos(ax), Math.sin(ax), Math.cos(ay), Math.sin(ay), Math.cos(az), Math.sin(az)];
  const Rx = [[1, 0, 0], [0, ca, -sa], [0, sa, ca]], Ry = [[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]], Rz = [[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]];
  const mm = (A, B) => A.map(r => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); return mm(Ry, mm(Rx, Rz)); }
const mv = (M, v) => [M[0][0] * v[0] + M[0][1] * v[1] + M[0][2] * v[2], M[1][0] * v[0] + M[1][1] * v[1] + M[1][2] * v[2], M[2][0] * v[0] + M[2][1] * v[1] + M[2][2] * v[2]];
// faces: normal, value (top face after "rest" orientation = +y)
const FACES = [[[0, 1, 0], 0], [[0, -1, 0], 1], [[1, 0, 0], 2], [[-1, 0, 0], 3], [[0, 0, 1], 4], [[0, 0, -1], 5]];
// rest orientations to show value v on top (+y): rotation mapping face normal to +y
const REST = { 1: [0, 0, 0], 6: [Math.PI, 0, 0], 3: [0, 0, Math.PI / 2], 4: [0, 0, -Math.PI / 2], 2: [-Math.PI / 2, 0, 0], 5: [Math.PI / 2, 0, 0] };
const FACEVAL = [1, 6, 3, 4, 2, 5]; // value painted on FACES[i]
function die(ctx, c, M, s = 1.2) {
  const view = CAM.pos; const faces = [];
  FACES.forEach(([nrm, i]) => { const n = mv(M, nrm); const ctr = [c[0] + n[0] * s, c[1] + n[1] * s, c[2] + n[2] * s]; if (dot(n, sub(view, ctr)) <= 0) return;
    const a = Math.abs(nrm[0]) ? [0, 1, 0] : [1, 0, 0]; const b = cross(nrm, a); const ua = mv(M, a), ub = mv(M, b);
    const corner = (x, y) => P([ctr[0] + (ua[0] * x + ub[0] * y) * s, ctr[1] + (ua[1] * x + ub[1] * y) * s, ctr[2] + (ua[2] * x + ub[2] * y) * s]);
    faces.push({ n, ctr, ua, ub, i, pts: [corner(-1, -1), corner(1, -1), corner(1, 1), corner(-1, 1)], corner, d: P(ctr)[2] }); });
  faces.sort((a, b) => b.d - a.d).forEach(f => { poly(ctx, f.pts); const lit = 0.55 + 0.45 * Math.max(0, dot(f.n, norm([0.3, 1, 0.5]))); ctx.fillStyle = `rgb(${245 * lit | 0},${242 * lit | 0},${236 * lit | 0})`; ctx.fill(); ctx.strokeStyle = 'rgba(0,0,0,0.3)'; ctx.lineWidth = 1; ctx.stroke();
    const v = FACEVAL[f.i]; PIPS[v].forEach(([x, y]) => { const p = f.corner(x * 0.5, y * 0.5); ctx.fillStyle = v === 1 ? '#c0282d' : '#1b1b1f'; ctx.beginPath(); ctx.arc(p[0], p[1], Math.max(1.5, scl(f.ctr, 0.17)), 0, 6.283); ctx.fill(); }); });
}
function diceScene(ctx, t) {
  const A = win(t, 43.0, 48.2, 0.6); if (A <= 0) return;
  // two dice tumbling, each roll 0.55s
  ctx.globalAlpha = A;
  for (let d = 0; d < 2; d++) {
    const per = 0.62, lt = t - 43.0 - d * 0.3; const k = Math.max(0, Math.floor(lt / per)); const ph = lt / per - k; const val = DICE[(k * 2 + d) % DICE.length];
    const bx = -3 + d * 4.2, bz = 5 + d * 1.5; const hgt = ph < 0.7 ? 4 * Math.sin(Math.PI * ph / 0.7) : 0;
    const R = REST[val]; const spin = ph < 0.7 ? (0.7 - ph) * 9 : 0; const M = rotM(R[0] + spin * 1.3, R[1] + spin * 0.9 + d, R[2] + spin * 0.7);
    const sh = P([bx, 0.01, bz]); ctx.globalAlpha = A * 0.35; ctx.fillStyle = '#000'; ctx.beginPath(); ctx.ellipse(sh[0], sh[1], scl([bx, 0, bz], 1.6), scl([bx, 0, bz], 0.6), 0, 0, 6.283); ctx.fill(); ctx.globalAlpha = A;
    die(ctx, [bx, 1.2 + hgt, bz], M);
  }
  // histogram panel
  panel(ctx, A, 'rgba(255,140,140,0.5)', 740, 90, 500, 440);
  const n = Math.max(6, Math.round(Math.pow(10, lerp(0.78, Math.log10(3000), ease((t - 43.3) / 4.0)))));
  const cnt = [0, 0, 0, 0, 0, 0]; let sum = 0; for (let i = 0; i < n; i++) { cnt[DICE[i] - 1]++; sum += DICE[i]; }
  txt(ctx, '掷骰子：点数分布与平均值', 770, 130, 24, '#ff9f9f', true);
  const gx = 790, gy = 170, gw = 400, gh = 220; ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(gx, gy + gh); ctx.lineTo(gx + gw, gy + gh); ctx.stroke();
  const yv = v => gy + gh - gh * v / 0.4; ctx.setLineDash([6, 5]); ctx.strokeStyle = 'rgba(255,224,102,0.7)'; ctx.beginPath(); ctx.moveTo(gx, yv(1 / 6)); ctx.lineTo(gx + gw, yv(1 / 6)); ctx.stroke(); ctx.setLineDash([]); txt(ctx, '1/6', gx + gw + 6, yv(1 / 6), 14, '#ffe066');
  cnt.forEach((c, i) => { const bw = gw / 6 * 0.7, x = gx + gw / 6 * (i + 0.15); const v = c / n; ctx.fillStyle = '#ff7b7b'; ctx.fillRect(x, yv(v), bw, gy + gh - yv(v)); txt(ctx, `${i + 1}`, x + bw / 2, gy + gh + 16, 16, '#ccd', true, 'center'); });
  txt(ctx, `n = ${n}`, 790, 450, 26, '#fff', true); txt(ctx, `平均点数 = ${(sum / n).toFixed(3)}`, 940, 450, 26, '#ffe066', true); txt(ctx, 'μ = (1+2+…+6)/6 = 3.5', 790, 495, 20, '#9aa4b0');
  ctx.globalAlpha = 1;
}

// ---------- seg 6 panel: dilution + monte carlo ----------
function dilutionPanel(ctx, t) {
  const A = win(t, 48.5, 58.6, 0.7); if (A <= 0) return; panel(ctx, A, 'rgba(255,170,120,0.5)');
  const px = 720; txt(ctx, '偏差被“稀释”，而非“补偿”', px, 110, 26, '#ffb08a', true);
  const rows = [[10, '0.7', '+2', '0.2'], [100, '0.52', '+2', '0.02'], [10000, '0.5002', '+2', '0.0002']];
  ctx.globalAlpha = A * clamp((t - 49.2) / 0.6); txt(ctx, 'n', px, 160, 18, '#9aa4b0', true); txt(ctx, '多出的正面', px + 100, 160, 18, '#9aa4b0', true); txt(ctx, '频率偏差 = 2/n', px + 260, 160, 18, '#9aa4b0', true);
  rows.forEach((r, i) => { ctx.globalAlpha = A * clamp((t - 49.6 - i * 0.9) / 0.5); const y = 200 + i * 40; txt(ctx, `${r[0]}`, px, y, 22, '#fff', true); txt(ctx, r[2], px + 100, y, 22, '#fff'); txt(ctx, r[3], px + 260, y, 22, '#ffe066', true); });
  // monte carlo pi
  const mA = A * clamp((t - 53.4) / 0.6); if (mA <= 0) { ctx.globalAlpha = 1; return; } ctx.globalAlpha = mA;
  txt(ctx, '蒙特卡洛：随机撒点估计 π', px, 350, 22, '#8fd0ff', true);
  const sx = px, sy = 375, sz = 170; ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.strokeRect(sx, sy, sz, sz); ctx.beginPath(); ctx.arc(sx, sy + sz, sz, -Math.PI / 2, 0); ctx.stroke();
  const n = Math.max(1, Math.round(Math.pow(10, lerp(1, Math.log10(4000), ease((t - 53.5) / 4.6))))); let inside = 0;
  for (let i = 0; i < n; i++) { const [u, v] = MC[i]; const inn = u * u + v * v <= 1; if (inn) inside++; ctx.fillStyle = inn ? 'rgba(127,240,176,0.9)' : 'rgba(255,120,120,0.9)'; ctx.fillRect(sx + u * sz - 1, sy + sz - v * sz - 1, 2, 2); }
  txt(ctx, `n = ${n}`, sx + sz + 30, sy + 50, 22, '#fff', true); txt(ctx, `π ≈ 4 × ${inside}/${n}`, sx + sz + 30, sy + 90, 20, '#ccd'); txt(ctx, `= ${(4 * inside / n).toFixed(4)}`, sx + sz + 30, sy + 125, 26, '#ffe066', true);
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
  setCam(t); background(ctx);
  chartScene(ctx, t); coinScene(ctx, t); diceScene(ctx, t);
  lawPanel(ctx, t); chebPanel(ctx, t); dilutionPanel(ctx, t);
  const tA = win(t, 0.2, 3.4, 0.6); if (tA > 0) { ctx.globalAlpha = tA; txt(ctx, '大数定律', 48, 60, 42, '#fff', true); txt(ctx, 'The Law of Large Numbers', 50, 102, 20, '#9fb3c8'); ctx.globalAlpha = 1; }
  const eA = clamp((t - 58.9) / 0.6);
  if (eA > 0) { ctx.globalAlpha = eA * 0.65; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = eA; txt(ctx, '样本越多，频率越稳定于概率', W / 2, H / 2 - 30, 44, '#fff', true, 'center'); txt(ctx, 'lim P( |X\u0304ₙ − μ| ≥ ε ) = 0', W / 2, H / 2 + 34, 30, '#ffe066', false, 'center'); ctx.globalAlpha = 1; }
  if (t < 58.9) subtitle(ctx, t);
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.45)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}
module.exports = { render };

if (require.main === module) {
  process.chdir(__dirname);
  const mode = process.argv[2] || 'video'; const cv = createCanvas(W, H), ctx = cv.getContext('2d');
  if (mode === 'still') { const fs = require('fs'); for (const t of process.argv.slice(3).map(Number)) { render(ctx, t); fs.writeFileSync(`still_${t}.png`, cv.toBuffer('image/png')); } return; }
  const ff = spawn(ffmpegBin(), ['-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', `${FPS}`, '-i', '-', '-i', 'mix.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'law_of_large_numbers.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  (async () => { const N = Math.round(DUR * FPS);
    for (let f = 0; f < N; f++) { render(ctx, f / FPS); const a = ctx.getImageData(0, 0, W, H).data; render(ctx, f / FPS + 0.25 / FPS); const b = ctx.getImageData(0, 0, W, H).data;
      const out = Buffer.alloc(a.length); for (let i = 0; i < a.length; i++) out[i] = (a[i] + b[i] + 1) >> 1; if (!ff.stdin.write(out)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); })();
}
