#!/usr/bin/env node
/**
 * render.mjs — 逐帧 seek(t) → 截图 → ffmpeg
 *
 *   node render.mjs --frames=0:12 --fps=30 --out=out/silent.mp4
 *   node render.mjs --stills=0.5,3.2,6.2,9.2 --out=qa
 *   node render.mjs --probe            # 只自检契约，不出图
 *
 * 渲染不是实时的：第 400 帧可能在第 399 帧几秒后才截。
 * 所以 scene.html 里每个像素都必须只是 t 的纯函数。
 */
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { fileURLToPath } from 'node:url';
import ffmpegPath from 'ffmpeg-static';

const ROOT = path.dirname(fileURLToPath(import.meta.url));

/* ── 参数 ─────────────────────────────────────────────────── */
const arg = (k, d) => {
  const m = process.argv.find(a => a.startsWith(`--${k}=`));
  return m ? m.slice(k.length + 3) : d;
};
const has = k => process.argv.includes(`--${k}`);

const FPS   = Number(arg('fps', 30));
const W     = Number(arg('w', 1280));
const H     = Number(arg('h', 720));
const OUT   = arg('out', 'out/silent.mp4');
const SCENE = arg('scene', 'scene.html');
const PORT  = Number(arg('port', 8137));

/* ── 静态服务器（ES module 需要 http://，file:// 会被 CORS 挡） ── */
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'text/javascript; charset=utf-8',
  '.mjs':  'text/javascript; charset=utf-8',
  '.json': 'application/json',
  '.css':  'text/css; charset=utf-8',
  '.png':  'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
};
function serve() {
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
      const fp = path.join(ROOT, rel);
      if (!fp.startsWith(ROOT) || !fs.existsSync(fp) || fs.statSync(fp).isDirectory()) {
        res.writeHead(404); return res.end('not found: ' + rel);
      }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
      fs.createReadStream(fp).pipe(res);
    });
    srv.listen(PORT, '127.0.0.1', () => resolve(srv));
  });
}

/* ── 浏览器 ───────────────────────────────────────────────── */
async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await page.goto(`http://127.0.0.1:${PORT}/${SCENE}`, { waitUntil: 'load' });
  await page.waitForFunction(() => typeof window.seek === 'function', null, { timeout: 30000 });
  await page.evaluate(() => window.ready());     // 等字体 + init
  if (errs.length) throw new Error('scene 报错:\n  ' + errs.join('\n  '));
  return page;
}

const launchArgs = [
  '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
  '--disable-gpu-sandbox', '--no-sandbox', '--hide-scrollbars',
  '--force-color-profile=srgb', '--mute-audio',
];

const t0 = Date.now();
const srv = await serve();
const browser = await chromium.launch({ args: launchArgs });
const page = await openPage(browser);
const contract = await page.evaluate(() => window.__contract);
console.log(`[契约] ${JSON.stringify(contract)}`);

if (has('probe')) {
  console.log(`[probe] 就绪，用时 ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await browser.close(); srv.close(); process.exit(0);
}

/* ── 模式 A：抽静帧（QA 用） ─────────────────────────────── */
if (has('stills') || arg('stills', '')) {
  const times = arg('stills', '').split(',').map(Number).filter(n => !isNaN(n));
  fs.mkdirSync(path.resolve(ROOT, OUT), { recursive: true });
  for (let idx = 0; idx < times.length; idx++) {
    const t = times[idx];
    await page.evaluate(tt => window.seek(tt), t);
    const fp = path.resolve(ROOT, OUT, `still-${String(idx).padStart(2, '0')}-t${t.toFixed(3).replace('.', '_')}s.png`);
    await page.screenshot({ path: fp, type: 'png' });
    console.log(`[still] t=${t.toFixed(3)}s → ${path.relative(ROOT, fp)}`);
  }
  await browser.close(); srv.close();
  console.log(`完成，用时 ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  process.exit(0);
}

/* ── 模式 B：逐帧渲染，直接 pipe 给 ffmpeg ───────────────── */
const [fromS, toS] = arg('frames', `0:${contract.DURATION}`).split(':').map(Number);
const i0 = Math.round(fromS * FPS);
const i1 = Math.round(toS * FPS);
const N = i1 - i0;
console.log(`[渲染] frame ${i0}..${i1} (共 ${N} 帧) @ ${FPS}fps, ${W}×${H}`);

fs.mkdirSync(path.dirname(path.resolve(ROOT, OUT)), { recursive: true });
const ff = spawn(ffmpegPath, [
  '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
  '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
  path.resolve(ROOT, OUT),
], { stdio: ['pipe', 'inherit', 'inherit'] });

let done = 0;
const mark = Date.now();
for (let i = i0; i < i1; i++) {
  const t = i / FPS;
  await page.evaluate(tt => window.seek(tt), t);
  const png = await page.screenshot({ type: 'png' });
  if (!ff.stdin.write(png)) await once(ff.stdin, 'drain');
  done++;
  if (done % 30 === 0 || done === N) {
    const el = (Date.now() - mark) / 1000;
    const per = el / done;
    console.log(`  ${String(done).padStart(4)}/${N} 帧  ·  ${per.toFixed(2)}s/帧  ·  预计剩余 ${((N - done) * per).toFixed(0)}s`);
  }
}
ff.stdin.end();
const [code] = await once(ff, 'close');
await browser.close(); srv.close();
if (code !== 0) { console.error(`ffmpeg 退出码 ${code}`); process.exit(1); }

const el = (Date.now() - t0) / 1000;
console.log(`[完成] ${OUT}  ·  ${N} 帧  ·  总用时 ${el.toFixed(1)}s  ·  平均 ${(el / N).toFixed(2)}s/帧`);
