---
name: blockbuster
description: Turn a one-line video request into a finished, cinematic code-rendered MP4. Use whenever the user asks for a video, film, promo, explainer, MV, title sequence, or "make me a clip" — especially when they want it to look premium / 有质感 rather than like a raw AI demo. Runs a director protocol: intake interview → committed art direction → brief → storyboard → deterministic build → contact-sheet QA gates → render → scored MP4.
---

# blockbuster — 从一句话到一条"交付级"片子

You are the **director**, not a renderer. The model's job is to make decisions a director makes
(art direction, beats, pacing, sound anchors, cuts) and then execute them deterministically.
Quality comes from those decisions, NOT from asking harder for "a nice video".

> Core doctrine: **"质感" is directed, not rendered.**
> A generic brief produces a generic demo no matter how good the renderer is.

## The protocol (do not skip phases, do not reorder)

### Phase 0 — Intake (ASK, don't guess)
Read `references/intake.md` and ask the user the blocking questions **before writing any code**.
Never silently default a creative axis (style / subject / length / music). If the user says
"you decide", propose **2–3 committed options with a one-line visual description each** and let them pick.

### Phase 1 — Commit an art direction
Pick ONE style preset from `references/styles.md` (or invent one with the same rigor) and write its
recipe into the brief: palette hexes, material/post parameters, font pairing, motion adjectives,
and the **material texture** that gives it 质感 (paper fibre / brush stroke / cel grain / scanlines…).
A style without a material texture will look like plastic. Reject any "dark tech default" unless
the user explicitly asks for it.

### Phase 2 — Brief
Fill `references/brief-template.md` (7 blocks). Save as `brief.md`. This is the contract for everything after.

### Phase 3 — Storyboard
Write `STORYBOARD.md`: one row per beat with time range, what happens, the **animation principle** used
(anticipation / squash-stretch / follow-through / motivated cut), camera move, and the sound anchor it syncs to.
Rules in `references/craft-rules.md` are mandatory here.

### Phase 4 — Build (deterministic contract)
Implement `scene.html` exposing exactly:
```js
window.DURATION = <seconds>;
await window.seek(t);        // every pixel is a pure function of t
```
Forbidden: `Date.now()`, `performance.now()`, `requestAnimationFrame` loops, CSS transitions,
`setTimeout`, unseeded `Math.random()`. See `references/pipeline.md`.
If any shot needs media code can't draw well (faces, fabric, photoreal plates), follow the
**hybrid rules** in `references/pipeline.md` and bring in a generated plate / image / video model for that shot only.

### Phase 4b — Sound design (one clock)
Read `references/sound-design.md`. Define the anchors ONCE and emit them:
```bash
python3 scripts/score.py out/score.wav --dur=<DUR> --anchors=<k=t,...> --arrange=<…> --emit-anchors=out/anchors.json
```
`scene.html` must **fetch `anchors.json`** in `ready()` instead of hard-coding timestamps —
that is the mechanical enforcement of "one clock". Choose instrument preset per mood
(guqin solemn / guzheng bright / pipa drive / mix). Never ship additive-harmonic plucks:
they are the #1 "plastic" tell; the engine in `scripts/guqin.py` is physical modelling for a reason.

### Phase 5 — QA gates (this is where quality is actually won)
1. `node scripts/render.mjs --scene=scene.html --stills=<one per beat + every cut ±0.1s> --out=qa`
2. Tile them into a contact sheet and **look at it**. Check against `references/craft-rules.md` §QA gates:
   no camera passing through subjects, no washed-out flash frames, text legible over subject,
   first/last frame intentional, no shader-compile fallbacks (a missing subject = compile error, verify console).
3. **Audio gates:** `python3 scripts/audio_qa.py out/score.wav --anchors=<same> ` must be 6/6 PASS.
   L4/L5 are the anti-plastic gates (brightness decay, pitch life). Retune, never waive.
4. Fix → re-still / re-score → only then render. **Never render full before both sheets are clean.**

### Phase 6 — Render + mix + deliver
```bash
node scripts/render.mjs --scene=scene.html --fps=<fps> --frames=0:<DUR> --out=out/silent.mp4
ffmpeg -i out/silent.mp4 -i out/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
       -shortest -movflags +faststart video/<title>.mp4        # + loudnorm per references/delivery.md
node scripts/qa.mjs video/<title>.mp4 --times=<…> --out=video/<title>-sheet.png
```
Then run the full QC checklist in `references/delivery.md` (loudness/peak, sheet, sidecars, licences).
Copy the MP4 out of `out/` — **`out/` is a build-artefact dir and is excluded from workspace snapshots**;
deliverables left there effectively do not exist for the user.

### Phase 7 — Report honestly
State: duration/res/fps, render wall-time and per-frame cost, what the visual AND audio gates caught,
measured loudness/true-peak, and what the piece still can't do (this pipeline's ceiling). No hype.

## Hard rules (summary — full list in references/craft-rules.md + sound-design.md)
- One clock: anchors defined once, emitted to `anchors.json`, fetched by the scene; sound and hits share them.
- Motion blur or don't move fast: temporal supersampling, 180° shutter, ≤30fps (24 preferred).
- Bloom is the #1 way to ruin a film: threshold ≥1.5, strength ≤0.25, halve additive elements first.
- Flash frames crisp (σ ≤0.005, peak ≤0.10), never a milky veil.
- Text over subject needs its own backing (panel / paper wash).
- Every cut motivated by action.
- **No additive-harmonic plucks** (plastic); physical-modelling engine only; audio_qa 6/6 before delivery.
- Loudness/true-peak matched to the briefed target (delivery.md).
- Review contact sheets from the **encoded MP4**, not just the live page.

## Environment
`scripts/check_env.py` verifies Node/Chromium/ffmpeg/fonts and prints install commands.
Expect: no GPU → SwiftShader software WebGL; budget ~0.5–2 s/frame at 720p.
Dependencies are NOT persisted between sessions — reinstall before re-rendering.

## Package map
```
SKILL.md                    this protocol
references/intake.md        the interview: every blocking question, with defaults
references/styles.md        5 committed presets (incl. ink-on-rice-paper recipe) + guard-rails
references/craft-rules.md   camera/light/text/cut rules + visual QA gates
references/sound-design.md  physical-instrument synthesis, plastic tells, audio gates
references/pipeline.md      render contract, cost table, hybrid rules, re-mux hygiene
references/brief-template.md the 7-block contract (incl. sound + loudness target)
references/delivery.md      loudness/codecs/naming/QC checklist/sidecars
scripts/render.mjs          frame-accurate capture + encode (stills & frames modes)
scripts/qa.mjs              contact sheet from the ENCODED mp4
scripts/guqin.py            physical plucked-string engine (K-S, slides, formants, friction)
scripts/score.py            arrangement + foley + room; emits anchors.json
scripts/audio_qa.py         6 objective audio gates, exit code for CI
scripts/check_env.py        toolchain check with exact fix commands
```
