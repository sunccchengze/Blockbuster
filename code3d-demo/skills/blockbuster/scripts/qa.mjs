#!/usr/bin/env node
/**
 * qa.mjs — pull frames from the ENCODED mp4 and tile a contact sheet.
 *   node qa.mjs video/final.mp4 --times=0.5,2.0,4.0,6.0,8.0,9.5 --cols=3 --out=video/sheet.png
 * Always QA the encoded file, not just the live page: encoding can surprise you.
 */
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import ffmpegPath from 'ffmpeg-static';

const arg = (k, d) => { const m = process.argv.find(a => a.startsWith(`--${k}=`)); return m ? m.slice(k.length + 3) : d; };
const src = process.argv[2];
if (!src || !fs.existsSync(src)) { console.error('usage: node qa.mjs <mp4> --times=... [--cols=4] [--out=sheet.png]'); process.exit(1); }
const times = arg('times', '0.5,2,4,6,8,9.5').split(',').map(Number);
const cols = Number(arg('cols', Math.min(4, times.length)));
const rows = Math.ceil(times.length / cols);
const out = arg('out', 'qa-sheet.png');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'qa-'));
const files = [];
times.forEach((t, i) => {
  const f = path.join(tmp, `f${String(i).padStart(2, '0')}.png`);
  const r = spawnSync(ffmpegPath, ['-y', '-loglevel', 'error', '-ss', String(t), '-i', src, '-frames:v', '1', f]);
  if (r.status !== 0 || !fs.existsSync(f)) { console.error(`frame @${t}s failed`); process.exit(1); }
  files.push(f);
});
const layout = [];
for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
  const i = r * cols + c; if (i >= files.length) break;
  layout.push(i === 0 ? '0_0' : (c === 0 ? `0_h${r}` : `w${i - 1}_${r === 0 ? 0 : 'h' + r}`));
}
// simpler & robust: use tile filter on a concat of inputs via xstack is fiddly; use tile on image2 sequence
const seq = path.join(tmp, 's%02d.png');
files.forEach((f, i) => fs.copyFileSync(f, path.join(tmp, `s${String(i).padStart(2, '0')}.png`)));
const r2 = spawnSync(ffmpegPath, ['-y', '-loglevel', 'error', '-i', seq,
  '-filter_complex', `scale=480:270,tile=${cols}x${rows}:margin=6:padding=6:color=0x0a0d14`, out]);
if (r2.status !== 0) { console.error(r2.stderr.toString()); process.exit(1); }
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`[qa] ${times.length} frames @ [${times.join(', ')}]s → ${out}  (look at it before you ship)`);
