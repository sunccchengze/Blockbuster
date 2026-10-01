// Concentration cell & Nernst equation — deterministic f(t) renderer (Blockbuster protocol)
const path = require('path');
const { canvas, fontFile, ffmpegBin } = require(path.join(__dirname, '../../tools/node_env.js'));
const { createCanvas, GlobalFonts } = canvas();
const { spawn } = require('child_process');
GlobalFonts.registerFromPath(fontFile(false), 'CJK');
GlobalFonts.registerFromPath(fontFile(true), 'CJKB');
const W = 1280, H = 720, FPS = 24, DUR = 62.0;
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


const SUPM={'²':'2','⁺':'+','⁻':'−','°':'°'}, SUBM={'₃':'3','₄':'4','₂':'2'};
function measureRich(ctx,s){const f=ctx.font;const m=/(\d+)px (.*)/.exec(f);const sz=+m[1];let w=0;for(const ch of s){if(SUPM[ch]&&ch!=='°'||SUBM[ch]){ctx.font=`${Math.round(sz*0.62)}px ${m[2]}`;w+=ctx.measureText(SUPM[ch]||SUBM[ch]).width;ctx.font=f;}else w+=ctx.measureText(ch).width;}return w;}
function fillRich(ctx,s,x,y,stroke){const f=ctx.font;const m=/(\d+)px (.*)/.exec(f);const sz=+m[1];const al=ctx.textAlign;const w=measureRich(ctx,s);let cx=al==='center'?x-w/2:al==='right'?x-w:x;ctx.textAlign='left';
for(const ch of s){let t=ch,dy=0,small=false;if(SUPM[ch]&&ch!=='°'){t=SUPM[ch];dy=-sz*0.32;small=true;}else if(SUBM[ch]){t=SUBM[ch];dy=sz*0.25;small=true;}
if(small)ctx.font=`${Math.round(sz*0.62)}px ${m[2]}`;if(stroke)ctx.strokeText(t,cx,y+dy);ctx.fillText(t,cx,y+dy);cx+=ctx.measureText(t).width;ctx.font=f;}
ctx.textAlign=al;return w;}

// ---------- timeline (from measured narration) ----------
const SEG = [[0.8, 9.2], [9.6, 21.05], [21.45, 32.87], [33.27, 42.91], [43.31, 50.33], [50.73, 61.9]];
const SUBS = [
  ['两个烧杯，同样的铜电极和硫酸铜溶液，', '只是浓度不同。', '仅凭浓度差就能产生电压，', '这就是浓差电池。'],
  ['在稀溶液一侧，铜失去电子，变成铜离子进入溶液，', '这是负极，发生氧化。', '在浓溶液一侧，铜离子得到电子，析出为铜，', '这是正极，发生还原。'],
  ['电子经外电路从稀侧流向浓侧，', '盐桥中的离子迁移，维持电荷平衡。', '总反应的本质，', '就是把铜离子从浓溶液搬运到稀溶液。'],
  ['电压多大？看能斯特方程。', '浓差电池两极相同，E标准为零，', 'E 就等于 RT 除以 2F，', '乘以浓度比的自然对数。'],
  ['浓度比一百比一，', '理想溶液理论值约零点零五九伏。', '这是动画模拟，不是实测。'],
  ['放电时两侧浓度逐渐接近，电压降低；', '浓度相等，电池达到平衡。', '记住，浓度比决定电压，', '浓度差关联可释放的电量。'],
];
const subTimes = [];
SEG.forEach(([a, b], i) => { const L = SUBS[i].map(s => s.length); const T = L.reduce((x, y) => x + y); let t = a; SUBS[i].forEach((s, k) => { const d = (b - a) * L[k] / T; subTimes.push([t, t + d, s]); t += d; }); });

// concentrations
const DISCH = [51.0, 58.0];
function conc(t) { const p = ease((t - DISCH[0]) / (DISCH[1] - DISCH[0])); return [lerp(0.01, 0.505, p), lerp(1.0, 0.505, p)]; }
// Ideal-solution animation model only: concentration ratio approximates the activity ratio.
function emf(t) { const [a, b] = conc(t); return 0.05916 / 2 * Math.log10(b / a); }

// ---------- camera ----------
const KEYS = [ // t, pos, target
  [0, [-6, 40, 62], [0, 8, 0]],
  [4, [-3, 26, 46], [0, 9, 0]],
  [9.0, [6, 24, 44], [0, 10, 0]],
  [10.6, [-12, 14, 20], [-9, 9, 0]],
  [15.0, [-10, 13, 19], [-9, 8.5, 0]],
  [16.4, [8, 14, 20], [9, 9, 0]],
  [20.6, [10, 13, 19], [9, 8.5, 0]],
  [22.4, [0, 30, 44], [0, 13, 0]],
  [32.6, [-4, 29, 44], [0, 13, 0]],
  [34.4, [-2, 26, 50], [12, 11, 0]],
  [48.9, [2, 25, 48], [12, 11, 0]],
  [57.0, [0, 27, 50], [12, 11, 0]],
  [62.0, [0, 34, 60], [0, 12, 0]],
];
function camAt(t) {
  let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++;
  const [t0, p0, g0] = KEYS[i], [t1, p1, g1] = KEYS[i + 1];
  const x = ease((t - t0) / (t1 - t0));
  return { pos: p0.map((v, k) => lerp(v, p1[k], x)), tgt: g0.map((v, k) => lerp(v, g1[k], x)) };
}
let CAM;
function setCam(t) {
  const { pos, tgt } = camAt(t); const f = norm(sub(tgt, pos)); const r = norm(cross(f, [0, 1, 0])); const u = cross(r, f);
  CAM = { pos, f, r, u, focal: (H / 2) / Math.tan(22 * Math.PI / 180) };
}
function P(p) { const d = sub(p, CAM.pos); const z = dot(d, CAM.f); return [W / 2 + CAM.focal * dot(d, CAM.r) / z, H / 2 - CAM.focal * dot(d, CAM.u) / z, z]; }
const scl = (p, r) => CAM.focal * r / P(p)[2];

// ---------- geometry ----------
const BK = [{ x: -9, name: 'L' }, { x: 9, name: 'R' }];
const BR = 5, BH = 12, LIQ = 9;
function circ(cx, y, cz, r, n = 48) { const a = []; for (let i = 0; i < n; i++) { const th = i / n * Math.PI * 2; a.push(P([cx + r * Math.cos(th), y, cz + r * Math.sin(th)])); } return a; }
function poly(ctx, pts) { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); }
function hull(pts) { // monotone chain convex hull on 2D
  const a = pts.map(p => [p[0], p[1]]).sort((p, q) => p[0] - q[0] || p[1] - q[1]);
  const cr = (o, a2, b) => (a2[0] - o[0]) * (b[1] - o[1]) - (a2[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const p of a) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (let i = a.length - 1; i >= 0; i--) { const p = a[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
function cylinder(ctx, cx, cz, r, y0, y1, fill) { poly(ctx, hull(circ(cx, y0, cz, r, 40).concat(circ(cx, y1, cz, r, 40)))); ctx.fillStyle = fill; ctx.fill(); }
function hullBounds(pts) { let a = 1e9, b = -1e9; pts.forEach(p => { a = Math.min(a, p[0]); b = Math.max(b, p[0]); }); return [a, b]; }

// liquid colour by concentration (Cu2+ absorbance)
function liqColor(c, a = 0.78) { const k = clamp(Math.log10(c / 0.005) / Math.log10(200)); const r = lerp(185, 20, k), g = lerp(225, 95, k), b = lerp(245, 200, k); return `rgba(${r | 0},${g | 0},${b | 0},${a})`; }

// ---------- particles ----------
const rnd = mulberry32(20260930);
const IONS = [0, 1].map(() => Array.from({ length: 46 }, () => ({ r: Math.sqrt(rnd()) * 4.1, th: rnd() * 6.283, y: 0.8 + rnd() * 7.4, ph: rnd() * 100, sp: 0.3 + rnd() * 0.5 })));
function ionPos(b, ion, t) {
  let r = ion.r + 0.35 * Math.sin(t * ion.sp + ion.ph), th = ion.th + 0.12 * t * ion.sp * (ion.ph > 50 ? 1 : -1);
  let x = r * Math.cos(th), z = r * Math.sin(th); if (Math.abs(x) < 0.9) x = 0.9 * Math.sign(x || 1) + x * 0.2; // keep off electrode
  return [BK[b].x + x, ion.y + 0.4 * Math.sin(t * ion.sp * 1.3 + ion.ph * 2), z];
}
function sphere(ctx, s, rad, col, label, alpha = 1) {
  if (s[2] <= 0) return; ctx.globalAlpha = alpha;
  const g = ctx.createRadialGradient(s[0] - rad * 0.35, s[1] - rad * 0.35, rad * 0.1, s[0], s[1], rad);
  g.addColorStop(0, '#ffffff'); g.addColorStop(0.25, col); g.addColorStop(1, 'rgba(0,0,0,0.85)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s[0], s[1], rad, 0, 6.283); ctx.fill();
  if (label && rad > 7) { ctx.fillStyle = '#fff'; ctx.font = `${Math.round(rad * 0.8)}px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; fillRich(ctx,label, s[0], s[1]); }
  ctx.globalAlpha = 1;
}

// wire path: left electrode top -> voltmeter -> right electrode top
const VM = [0, 25, -1];
const WIRE = [[-9, 17.5, 0], [-9, 22, 0], [-7, 25, -1], [-2.6, 25, -1], [2.6, 25, -1], [7, 25, -1], [9, 22, 0], [9, 17.5, 0]];
function along(path, u) { const L = []; let tot = 0; for (let i = 1; i < path.length; i++) { const l = Math.hypot(...sub(path[i], path[i - 1])); L.push(l); tot += l; } let d = ((u % 1) + 1) % 1 * tot; for (let i = 0; i < L.length; i++) { if (d <= L[i]) { const x = d / L[i]; return path[i].map((v, k) => lerp(v, path[i + 1][k], x)); } d -= L[i]; } return path[path.length - 1]; }
// salt bridge U tube
const BRIDGE = [[-7.2, 4, 1.5], [-7.2, 12, 1.5], [-6.6, 15, 1.5], [-4.5, 16.2, 1.5], [4.5, 16.2, 1.5], [6.6, 15, 1.5], [7.2, 12, 1.5], [7.2, 4, 1.5]];

// ---------- drawing ----------
function background(ctx) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#20242a'); g.addColorStop(0.55, '#15181c'); g.addColorStop(1, '#0b0c0e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // bench top
  const c = [[-60, 0, -30], [60, 0, -30], [60, 0, 40], [-60, 0, 40]].map(P);
  poly(ctx, c); const bg = ctx.createLinearGradient(0, c[0][1], 0, H); bg.addColorStop(0, '#2b2e33'); bg.addColorStop(1, '#101114'); ctx.fillStyle = bg; ctx.fill();
  // back wall tiles
  ctx.strokeStyle = 'rgba(255,255,255,0.035)'; ctx.lineWidth = 1;
  for (let x = -60; x <= 60; x += 6) { const a = P([x, 0, -30]), b = P([x, 60, -30]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  for (let y = 6; y <= 60; y += 6) { const a = P([-60, y, -30]), b = P([60, y, -30]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  // warm key light pool
  const lp = P([0, 0, 0]); const rg = ctx.createRadialGradient(lp[0], lp[1], 10, lp[0], lp[1], scl([0, 0, 0], 30));
  rg.addColorStop(0, 'rgba(255,240,215,0.10)'); rg.addColorStop(1, 'rgba(255,240,215,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
}
function shadow(ctx, x) { const c = circ(x, 0.01, 0.6, BR * 1.25, 32); poly(ctx, c); ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fill(); }

function electrode(ctx, x, t, plating) {
  const w = 1.6, d = 0.18, y0 = 1.2, y1 = 17.5;
  const faces = [
    [[x - w, y0, d], [x + w, y0, d], [x + w, y1, d], [x - w, y1, d]],
    [[x + w, y0, d], [x + w, y0, -d], [x + w, y1, -d], [x + w, y1, d]],
    [[x - w, y0, -d], [x - w, y0, d], [x - w, y1, d], [x - w, y1, -d]],
    [[x - w, y1, d], [x + w, y1, d], [x + w, y1, -d], [x - w, y1, -d]],
  ];
  faces.forEach((f, i) => {
    const p = f.map(P); poly(ctx, p);
    const g = ctx.createLinearGradient(p[0][0], p[0][1], p[2][0], p[2][1]);
    const sh = [1, 0.6, 0.7, 1.15][i];
    g.addColorStop(0, `rgb(${120 * sh | 0},${58 * sh | 0},${30 * sh | 0})`); g.addColorStop(0.45, `rgb(${Math.min(255, 235 * sh) | 0},${150 * sh | 0},${95 * sh | 0})`); g.addColorStop(1, `rgb(${150 * sh | 0},${72 * sh | 0},${40 * sh | 0})`);
    ctx.fillStyle = g; ctx.fill();
  });
  // specular streak moving with camera
  const a = P([x - w * 0.3, y0 + 1, d]), b = P([x - w * 0.1, y1 - 1, d]); ctx.strokeStyle = 'rgba(255,230,200,0.25)'; ctx.lineWidth = Math.max(1, scl([x, 8, 0], 0.25)); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
  if (plating > 0) { const pr = mulberry32(7); const n = Math.floor(60 * plating); for (let i = 0; i < n; i++) { const s = P([x - w + pr() * 2 * w, y0 + 0.3 + pr() * 7.2, d + 0.05]); ctx.fillStyle = `rgba(${200 + pr() * 55 | 0},${110 + pr() * 40 | 0},60,0.95)`; ctx.beginPath(); ctx.arc(s[0], s[1], scl([x, 5, 0], 0.12 + pr() * 0.12), 0, 6.283); ctx.fill(); } }
}

function beakerBack(ctx, x, c) {
  // back glass wall
  cylinder(ctx, x, 0, BR, 0, BH, 'rgba(200,220,235,0.06)');
  // liquid body
  cylinder(ctx, x, 0, BR * 0.97, 0.15, LIQ, liqColor(c, 0.55));
  // liquid surface
  poly(ctx, circ(x, LIQ, 0, BR * 0.97)); ctx.fillStyle = liqColor(c, 0.65); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.25)'; ctx.lineWidth = 1; ctx.stroke();
}
function beakerFront(ctx, x) {
  const top = circ(x, BH, 0, BR, 48), bot = circ(x, 0, 0, BR, 48);
  const [a, b] = hullBounds(top.concat(bot));
  cylinder(ctx, x, 0, BR, 0, BH, 'rgba(210,230,245,0.05)');
  // vertical highlights
  const g = ctx.createLinearGradient(a, 0, b, 0);
  g.addColorStop(0, 'rgba(255,255,255,0.28)'); g.addColorStop(0.08, 'rgba(255,255,255,0.02)'); g.addColorStop(0.18, 'rgba(255,255,255,0.18)'); g.addColorStop(0.24, 'rgba(255,255,255,0.0)'); g.addColorStop(0.9, 'rgba(255,255,255,0.03)'); g.addColorStop(1, 'rgba(255,255,255,0.22)');
  poly(ctx, hull(top.concat(bot))); ctx.fillStyle = g; ctx.fill();
  ctx.strokeStyle = 'rgba(230,240,250,0.55)'; ctx.lineWidth = 1.4; poly(ctx, top); ctx.stroke();
  ctx.strokeStyle = 'rgba(230,240,250,0.18)'; poly(ctx, bot); ctx.stroke();
  // graduations
  ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 1;
  for (let y = 2; y <= 10; y += 2) { const p0 = P([x - 1.2, y, BR]), p1 = P([x + 0.2, y, BR]); ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke(); }
}
function tube(ctx, path, r, stroke, lw) { const p = path.map(P); ctx.beginPath(); p.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = lw || scl(path[Math.floor(path.length/2)], r * 2); ctx.stroke(); }

function voltmeter(ctx, t, E, show) {
  const x0 = -3.2, x1 = 3.2, y0 = 22.6, y1 = 27.4, z = -1;
  const front = [[x0, y0, z + 0.8], [x1, y0, z + 0.8], [x1, y1, z + 0.8], [x0, y1, z + 0.8]].map(P);
  const topf = [[x0, y1, z + 0.8], [x1, y1, z + 0.8], [x1, y1, z - 1.2], [x0, y1, z - 1.2]].map(P);
  poly(ctx, topf); ctx.fillStyle = '#3a3f46'; ctx.fill();
  poly(ctx, front); const g = ctx.createLinearGradient(0, front[3][1], 0, front[0][1]); g.addColorStop(0, '#e9b73a'); g.addColorStop(1, '#b3861c'); ctx.fillStyle = g; ctx.fill();
  const lcd = [[x0 + 0.5, y0 + 1.6, z + 0.82], [x1 - 0.5, y0 + 1.6, z + 0.82], [x1 - 0.5, y1 - 0.5, z + 0.82], [x0 + 0.5, y1 - 0.5, z + 0.82]].map(P);
  poly(ctx, lcd); ctx.fillStyle = '#9fb59a'; ctx.fill(); ctx.strokeStyle = '#222'; ctx.lineWidth = 1; ctx.stroke();
  const cx = (lcd[0][0] + lcd[2][0]) / 2, cy = (lcd[0][1] + lcd[2][1]) / 2, hh = Math.abs(lcd[0][1] - lcd[2][1]);
  ctx.fillStyle = '#1b2419'; ctx.font = `${Math.round(hh * 0.5)}px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(show ? E.toFixed(3) + ' V' : '0.000 V', cx, cy);
  const lb = P([0, y0 + 0.75, z + 0.82]); ctx.fillStyle = '#2a1f05'; ctx.font = `${Math.round(hh * 0.28)}px ${FONTB}`; ctx.fillText('V', lb[0], lb[1]);
}

function label3(ctx, p, lines, alpha, color = '#fff', size = 22, dx = 0) {
  if (alpha <= 0.01) return; const s = P(p); ctx.globalAlpha = alpha; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const x = s[0] + dx; let w = 0; ctx.font = `${size}px ${FONTB}`; lines.forEach(l => w = Math.max(w, measureRich(ctx,l)));
  const h = lines.length * size * 1.35 + 12; ctx.fillStyle = 'rgba(10,12,16,0.72)'; rr(ctx, x - w / 2 - 12, s[1] - h / 2, w + 24, h, 8); ctx.fill();
  ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
  lines.forEach((l, i) => { ctx.fillStyle = i === 0 ? color : '#e8ecf0'; fillRich(ctx,l, x, s[1] - h / 2 + 6 + size * 1.35 * (i + 0.5)); });
  ctx.globalAlpha = 1;
}
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }

// ---- equation panel (2D overlay, math typeset manually) ----
function frac(ctx, x, y, num, den, size) { ctx.font = `${size}px ${FONT}`; const w = Math.max(ctx.measureText(num).width, ctx.measureText(den).width) + 10; ctx.textAlign = 'center'; ctx.fillText(num, x + w / 2, y - size * 0.55); ctx.fillText(den, x + w / 2, y + size * 0.6); ctx.fillRect(x, y - 1, w, 2); ctx.textAlign = 'left'; return w; }
function txt(ctx, s, x, y, size, col, b) { ctx.font = `${size}px ${b ? FONTB : FONT}`; ctx.fillStyle = col; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; return fillRich(ctx,s, x, y); }
function eqPanel(ctx, t) {
  const A = win(t, 33.4, 50.4, 0.7); if (A <= 0) return;
  const px = 690, py = 70, pw = 550, ph = 500;
  ctx.globalAlpha = A; ctx.fillStyle = 'rgba(12,16,22,0.82)'; rr(ctx, px, py, pw, ph, 16); ctx.fill(); ctx.strokeStyle = 'rgba(120,190,255,0.5)'; ctx.lineWidth = 1.5; ctx.stroke();
  txt(ctx, '能斯特方程  Nernst Equation', px + 28, py + 38, 24, '#8fd0ff', true);
  const s = 30; let y = py + 100, x = px + 36;
  const a1 = clamp((t - 34.0) / 0.8); ctx.globalAlpha = A * a1;
  x += txt(ctx, 'E = E° − ', x, y, s, '#fff'); ctx.fillStyle = '#fff'; x += frac(ctx, x, y, 'RT', 'nF', s) + 8; txt(ctx, 'ln Q', x, y, s, '#fff');
  const a1b = clamp((t - 35.3) / 0.8); ctx.globalAlpha = A * a1b; y += 56; x = px + 36;
  txt(ctx, '25 ℃ 时 2.303RT/F = 0.0592 V，ln 换为 lg：', x, y, 20, '#9aa4b0');
  y += 52; x = px + 36;
  x += txt(ctx, 'E = E° − ', x, y, s, '#fff'); ctx.fillStyle = '#fff'; x += frac(ctx, x, y, '0.0592 V', 'n', s) + 8; txt(ctx, 'lg Q', x, y, s, '#fff');
  const a2 = clamp((t - 37.0) / 0.8); ctx.globalAlpha = A * a2; y += 66; x = px + 36;
  txt(ctx, '两极同为 Cu | Cu²⁺  ⇒  E° = 0，n = 2', x, y, 22, '#ffd27a');
  const a3 = clamp((t - 38.6) / 0.8); ctx.globalAlpha = A * a3; y += 72; x = px + 36;
  x += txt(ctx, 'E = ', x, y, s, '#fff'); ctx.fillStyle = '#fff'; x += frac(ctx, x, y, '0.0592 V', '2', s) + 8; x += txt(ctx, 'lg ', x, y, s, '#fff'); ctx.fillStyle = '#7fe0a8'; frac(ctx, x, y, 'c浓', 'c稀', s);
  const a4 = clamp((t - 43.6) / 0.8); ctx.globalAlpha = A * a4; y += 76; x = px + 36;
  x += txt(ctx, '= 0.0296 V × lg(1 / 0.01)', x, y, 28, '#fff');
  const a5 = clamp((t - 45.8) / 0.6); ctx.globalAlpha = A * a5;
  txt(ctx, ' ≈ 0.059 V', x, y, 30, '#ffe066', true);
  ctx.globalAlpha = A;
  txt(ctx, '理想溶液近似 · 动画模拟值，非实测', px + 36, py + 468, 18, '#d8e4ef');
  ctx.globalAlpha = 1;
}
// ---- discharge graph panel ----
function graphPanel(ctx, t) {
  const A = win(t, 50.8, 60.4, 0.7); if (A <= 0) return;
  const px = 690, py = 110, pw = 540, ph = 440; ctx.globalAlpha = A;
  ctx.fillStyle = 'rgba(12,16,22,0.82)'; rr(ctx, px, py, pw, ph, 16); ctx.fill(); ctx.strokeStyle = 'rgba(255,200,120,0.5)'; ctx.lineWidth = 1.5; ctx.stroke();
  txt(ctx, '理想模型模拟：浓度趋同，E → 0', px + 28, py + 38, 24, '#ffc57a', true);
  const gx = px + 70, gy = py + 90, gw = pw - 110, gh = 220;
  ctx.strokeStyle = '#8894a0'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx, gy + gh); ctx.lineTo(gx + gw, gy + gh); ctx.stroke();
  txt(ctx, 'E / V', gx - 50, gy - 6, 18, '#aab'); txt(ctx, '时间', gx + gw - 40, gy + gh + 22, 18, '#aab');
  txt(ctx, '0.059', gx - 58, gy + 12, 16, '#aab'); txt(ctx, '0', gx - 20, gy + gh, 16, '#aab');
  const ymap = E => gy + gh - E / 0.0592 * (gh - 12);
  ctx.strokeStyle = '#ffe066'; ctx.lineWidth = 3; ctx.beginPath(); let last;
  for (let k = 0; k <= 200; k++) { const tt = lerp(50.8, 60.2, k / 200); if (tt > t) break; const xx = gx + gw * k / 200, yy = ymap(emf(tt)); k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); last = [xx, yy]; }
  ctx.stroke(); if (last) { ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(last[0], last[1], 5, 0, 6.283); ctx.fill(); }
  const [cl, cr] = conc(t);
  txt(ctx, `c稀 = ${cl.toFixed(3)} mol/L`, px + 36, py + 360, 24, '#bfe6ff'); txt(ctx, `c浓 = ${cr.toFixed(3)} mol/L`, px + 290, py + 360, 24, '#6fa8ff');
  txt(ctx, `E = ${emf(t).toFixed(3)} V`, px + 36, py + 405, 28, '#ffe066', true);
  ctx.globalAlpha = 1;
}

function subtitle(ctx, t) {
  for (const [a, b, s] of subTimes) {
    if (t >= a - 0.05 && t < b + 0.05) {
      const A = clamp((t - a + 0.05) / 0.15) * clamp((b + 0.05 - t) / 0.15);
      ctx.globalAlpha = A; ctx.font = `34px ${FONTB}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      const w = ctx.measureText(s).width; ctx.fillStyle = 'rgba(0,0,0,0.55)'; rr(ctx, W / 2 - w / 2 - 20, H - 78, w + 40, 52, 10); ctx.fill();
      ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(0,0,0,0.8)'; ctx.fillStyle = '#fff'; fillRich(ctx,s, W / 2, H - 52, true); ctx.globalAlpha = 1;
    }
  }
}

// ---------- frame ----------
function render(ctx, t) {
  setCam(t);
  background(ctx);
  const [cl, cr] = conc(t), E = emf(t), flow = E / 0.0592;
  const nL = Math.round(lerp(6, 23, (cl - 0.01) / 0.495)), nR = Math.round(lerp(40, 23, (1 - cr) / 0.495));
  shadow(ctx, -9); shadow(ctx, 9);
  // wires (behind)
  const wireA = clamp((t - 1.5) / 1.5);
  ctx.globalAlpha = wireA; tube(ctx, WIRE.slice(0, 4), 0.18, '#2fbf5a'); tube(ctx, WIRE.slice(4), 0.18, '#d0302a'); tube(ctx, WIRE.slice(3, 5), 0.18, '#444'); ctx.globalAlpha = 1;
  voltmeter(ctx, t, E, t > 3.0);
  const plating = clamp((t - 15) / 6) * 0.6 + clamp((t - 21) / 30) * 0.4;
  for (let b = 0; b < 2; b++) {
    const x = BK[b].x, c = b ? cr : cl, n = b ? nR : nL;
    beakerBack(ctx, x, c);
    const ions = IONS[b].slice(0, n).map(io => ionPos(b, io, t)).map(p => ({ p, s: P(p) }));
    const behind = ions.filter(o => o.p[2] < 0), front = ions.filter(o => o.p[2] >= 0);
    const ionR = p => scl(p, 0.42);
    behind.sort((a, c2) => c2.s[2] - a.s[2]).forEach(o => sphere(ctx, o.s, ionR(o.p), '#2f7dff', 'Cu²⁺', 0.9));
    electrode(ctx, x, t, b ? plating : 0);
    front.sort((a, c2) => c2.s[2] - a.s[2]).forEach(o => sphere(ctx, o.s, ionR(o.p), '#2f7dff', 'Cu²⁺', 0.95));
  }
  // electrode reaction events (segment 2 onward, strongest while zoomed)
  const evA = clamp((t - 9.8) / 0.6) * (0.35 + 0.65 * win(t, 9.8, 21.2, 0.6)) * flow;
  if (evA > 0.01) {
    for (let k = 0; k < 8; k++) {
      const per = 1.6, ph = ((t - 9.8) / per + k / 8) % 1, zz = ((k * 37) % 7 - 3) * 0.22;
      const yy = 2 + ((k * 53) % 11) * 0.55;
      // left: Cu leaves plate as Cu2+ (oxidation)
      const pL = [-9 + (k % 2 ? 1 : -1) * (0.3 + ph * 2.6), yy, 0.3 + zz];
      sphere(ctx, P(pL), scl(pL, 0.42), ph < 0.15 ? '#d9823f' : '#2f7dff', ph < 0.15 ? 'Cu' : 'Cu²⁺', evA * clamp(ph * 8) * clamp((1 - ph) * 5));
      // electrons climbing left plate
      for (let e = 0; e < 2; e++) { const pe = [-9 + (e ? 0.5 : -0.5), yy + ph * (17.5 - yy), 0.25]; sphere(ctx, P(pe), scl(pe, 0.2), '#ffd83a', 'e⁻', evA * clamp(ph * 6) * clamp((1 - ph) * 6)); }
      // right: Cu2+ approaches plate and deposits (reduction)
      const pR = [9 + (k % 2 ? 1 : -1) * (0.3 + (1 - ph) * 2.6), yy, 0.3 + zz];
      sphere(ctx, P(pR), scl(pR, 0.42), ph > 0.85 ? '#d9823f' : '#2f7dff', ph > 0.85 ? 'Cu' : 'Cu²⁺', evA * clamp(ph * 5) * clamp((1 - ph) * 8 + 0.2));
      for (let e = 0; e < 2; e++) { const pe = [9 + (e ? 0.5 : -0.5), 17.5 - ph * (17.5 - yy), 0.25]; sphere(ctx, P(pe), scl(pe, 0.2), '#ffd83a', 'e⁻', evA * clamp(ph * 6) * clamp((1 - ph) * 6)); }
    }
  }
  // salt bridge
  const brA = clamp((t - 2.0) / 1.5);
  ctx.globalAlpha = brA; tube(ctx, BRIDGE, 0.75, 'rgba(210,235,255,0.22)'); tube(ctx, BRIDGE, 0.5, 'rgba(240,248,255,0.10)'); ctx.globalAlpha = 1;
  const sbA = clamp((t - 21.6) / 0.8) * flow;
  if (sbA > 0.01) for (let k = 0; k < 10; k++) {
    const ua = (k / 10 + t * 0.05 * flow) % 1, uc = (k / 10 + 0.05 + t * 0.05 * flow) % 1;
    const pa = along(BRIDGE, 1 - ua), pc = along(BRIDGE, uc);
    sphere(ctx, P(pa), scl(pa, 0.36), '#35c46a', 'NO₃⁻', sbA); sphere(ctx, P(pc), scl(pc, 0.3), '#ff8a3d', 'K⁺', sbA);
  }
  // electrons in wire
  const ewA = clamp((t - 9.8) / 0.8) * flow;
  if (ewA > 0.01) for (let k = 0; k < 18; k++) { const u = (k / 18 + t * 0.07 * flow) % 1; const p = along(WIRE, u); if (Math.abs(p[0]) < 3.3 && p[1] > 24) continue; const s = P(p); const r = scl(p, 0.3);
    ctx.globalAlpha = ewA * 0.45; const g = ctx.createRadialGradient(s[0], s[1], 0, s[0], s[1], r * 3); g.addColorStop(0, 'rgba(255,220,80,0.9)'); g.addColorStop(1, 'rgba(255,220,80,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s[0], s[1], r * 3, 0, 6.283); ctx.fill(); ctx.globalAlpha = 1;
    sphere(ctx, s, r, '#ffd83a', 'e⁻', ewA); }
  for (let b = 0; b < 2; b++) beakerFront(ctx, BK[b].x);
  // arrow label for electron flow
  // 3D labels
  label3(ctx, [-9, -1.8, 5], [`c稀 = ${cl.toFixed(cl < 0.1 ? 2 : 3)} mol/L CuSO₄`], win(t, 2.5, 9.6), '#bfe6ff', 20);
  label3(ctx, [9, -1.8, 5], [`c浓 = ${cr.toFixed(cr > 0.99 ? 1 : 3)} mol/L CuSO₄`], win(t, 3.0, 9.6), '#6fa8ff', 20);
  label3(ctx, [-9, 14.5, 3], ['负极（阳极）· 氧化', 'Cu → Cu²⁺ + 2e⁻'], win(t, 11.0, 16.0) + win(t, 22.6, 33.0) * 0.9, '#ff9a8a', 22);
  label3(ctx, [9, 14.5, 3], ['正极（阴极）· 还原', 'Cu²⁺ + 2e⁻ → Cu'], win(t, 16.8, 21.3) + win(t, 22.6, 33.0) * 0.9, '#8affc1', 22);
  label3(ctx, [0, 18.4, 1.5], ['盐桥 KNO₃：NO₃⁻ → 稀侧，K⁺ → 浓侧'], win(t, 25.2, 33.0), '#9ff0b8', 20);
  label3(ctx, [0, 29.8, -1], ['e⁻：稀侧 → 外电路 → 浓侧'], win(t, 22.6, 27.5), '#ffe066', 20);
  label3(ctx, [0, 30.2, -1], ['总反应：Cu²⁺(浓) → Cu²⁺(稀)'], win(t, 28.3, 33.0), '#ffe066', 24);
  eqPanel(ctx, t); graphPanel(ctx, t);
  // title
  const tA = win(t, 0.2, 3.2, 0.6);
  if (tA > 0) { ctx.globalAlpha = tA; txt(ctx, '浓差电池与能斯特方程', 48, 60, 40, '#fff', true); txt(ctx, 'Concentration Cell · Nernst Equation', 50, 102, 20, '#9fb3c8'); ctx.globalAlpha = 1; }
  const noteA = clamp((t - 2.8) / 0.6) * clamp((60.6 - t) / 0.6);
  if (noteA > 0) { ctx.globalAlpha = noteA; ctx.fillStyle = 'rgba(0,0,0,0.7)'; rr(ctx, 40, 122, 510, 38, 8); ctx.fill(); txt(ctx, '理想溶液理论值（动画模拟，非实测）', 54, 141, 18, '#ffe066', true); ctx.globalAlpha = 1; }
  const eA = clamp((t - 58.2) / 0.8);
  if (eA > 0) { ctx.globalAlpha = eA * 0.6; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = eA; ctx.textAlign = 'center'; txt; ctx.font = `46px ${FONTB}`; ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.fillText('浓度比决定电压；浓度差关联可释放的电量', W / 2, H / 2 - 30); ctx.font = `28px ${FONT}`; ctx.fillStyle = '#ffe066'; ctx.fillText('理想溶液近似：E = (0.0592 V / n) · lg(c浓 / c稀)', W / 2, H / 2 + 30); ctx.globalAlpha = 1; }
  if (t < 58.2) subtitle(ctx, t);
  // letterbox vignette
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.45)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}

module.exports = { render, W, H, FPS, DUR };

if (require.main === module) {
  process.chdir(__dirname); const mode = process.argv[2] || 'video';
  const cv = createCanvas(W, H), ctx = cv.getContext('2d');
  if (mode === 'still') { const fs = require('fs'); for (const t of process.argv.slice(3).map(Number)) { render(ctx, t); fs.writeFileSync(`still_${t}.png`, cv.toBuffer('image/png')); } return; }
  const ff = spawn(ffmpegBin(), ['-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', `${FPS}`, '-i', '-', '-i', 'mix.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'concentration_cell_nernst.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  (async () => {
    const N = Math.round(DUR * FPS);
    for (let f = 0; f < N; f++) {
      // 2-sample 180° shutter integration
      render(ctx, f / FPS); const a = ctx.getImageData(0, 0, W, H).data;
      render(ctx, f / FPS + 0.5 / FPS / 2); const b = ctx.getImageData(0, 0, W, H).data;
      const out = Buffer.alloc(a.length); for (let i = 0; i < a.length; i++) out[i] = (a[i] + b[i] + 1) >> 1;
      if (!ff.stdin.write(out)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 240 === 0) console.log('frame', f, '/', N);
    }
    ff.stdin.end();
  })();
}
