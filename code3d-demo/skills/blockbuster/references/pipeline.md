# Pipeline — the deterministic contract, render loop, cost model, hybrid rules

## The contract
`scene.html` must expose:
```js
window.DURATION = <sec>;              // total length
window.FPS      = <fps>;
await window.ready();                 // fonts + assets + init; resolves once
await window.seek(t);                 // pose everything for t and present one frame
window.__contract = {...};            // self-description for the renderer/QA
```
Every pixel must be a pure function of `t`. Forbidden: `Date.now()`, `performance.now()`,
rAF loops, CSS transitions/timers, unseeded `Math.random()`. Seeded PRNG (mulberry32) for anything stochastic.
Fonts: build CanvasTextures only after `document.fonts.ready` + explicit `fonts.load(...)`, else CJK → tofu.
Assets over `file://` break ES modules/CORS → the renderer serves the project over a local HTTP server.

## Motion blur (temporal supersampling, 180° shutter)
```js
const SHUT = (1/FPS) * 0.5;
for (let k=0;k<N;k++){                 // N=3 default
  setState(t + (k+0.5)/N * SHUT);
  render(scene → rtSub);
  accumulate(rtSub → rtAcc, weight 1/(k+1));   // ping-pong mix blit
}
composite(rtAcc → canvas);
```
Keep the scene in a **linear HalfFloat RT** with `renderer.toneMapping = NoToneMapping`; do exposure,
tonemap/curve, grade, vignette, grain in the composite so bloom (if any) acts on HDR.

## Post chain (pick per style)
- ink/paper: NO bloom; S-curve preserving whites; paper multiply; stain vignette; grain.
- emissive/neon: bright-pass (thresh ≥1.2) → ¼-res H/V blur ×2 → add; then CA, grade, vignette, grain.
- Grain MUST be seeded per frame: `hash(gl_FragCoord.xy + uFrame*137)`.

## Render loop
`scripts/render.mjs`:
- serves project over HTTP; launches headless Chromium with SwiftShader flags;
- `--stills=a,b,c` for QA stills; `--frames=A:B --fps=N --out=...` pipes PNGs straight into ffmpeg
  (`-f image2pipe -c:v libx264 -crf 17 -pix_fmt yuv420p`); prints per-frame cost every 30 frames.
- Captures page console; **fails loud on any shader-compile error** (silent vanish = compile bug).

## Cost model (measured on 2-core CPU, no GPU, SwiftShader)
| config | per-frame | 10 s piece |
|---|---|---|
| 720p, PBR metal, bloom, MSAA4, no blur | 0.79 s | 284 s (360f@30) |
| 720p, ink (cheap shading), no bloom, MSAA2, blur ×3 | ~1.7 s | ~410 s (240f@24) |
| 1080p | ≈2.2× the 720p number | plan accordingly |
Tokens buy planning/code only; **frames cost your wall-clock and electricity**, not tokens.

## Hybrid rules (right tool per shot)
Code-render by default. Bring external media only where code is the wrong tool:
photoreal plate/face/fabric → generated image/video model as a fixed file; restyle-to-footage → video-to-video
finishing pass; hard-surface/organic 3D → drive Blender from code. Every external asset = fixed file sampled by
`seek(t)`; list source + licence in the brief. (v3 uses generated paper + ink-mountain plates this way.)

## Sound — one clock, physical instruments
Anchors are defined once and flow both ways:
```bash
python3 scripts/score.py out/score.wav --dur=10 --anchors=drop=1.0,impact=1.9,stamp=8.0 \
       --arrange=ink --instrument=mix --emit-anchors=out/anchors.json
python3 scripts/audio_qa.py out/score.wav --anchors=drop=1.0,impact=1.9,stamp=8.0   # must be 6/6
```
`scene.html` fetches `anchors.json` in `ready()`; never duplicate timestamps in the scene.
The engine (`guqin.py`) is block Karplus-Strong with pluck-position comb, slides/吟猱, body formants and
friction — additive harmonics are banned (L4/L5 catch them). Presets: guqin/guzheng/pipa/mix.

## Assemble & deliver
```bash
ffmpeg -i out/silent.mp4 -i out/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
       -shortest -movflags +faststart video/final.mp4        # add loudnorm= per delivery.md if LUFS target
node scripts/qa.mjs video/final.mp4 --times=... --out=video/sheet.png     # sheet from the ENCODED file
```
**Deliverables must not live in `out/`** (build-artefact dir, excluded from workspace snapshots).
Copy to `video/` (or similar) or the user will not see them. If only the score changes, re-mux from the
existing MP4 (`-map 0:v -c:v copy`) — do not pay for a re-render. Keep `video/<title>-silent.mp4` around.

## Re-render hygiene
Dependencies (node_modules, Chromium, system libs) are NOT persisted between sessions.
Run `python3 scripts/check_env.py` first; it prints exact install commands.
