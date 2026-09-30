# Craft rules — the six lessons, as enforceable rules

These are the differences between "a rendered demo" and "a film". Each has a QA gate.

## 1 · Art direction & material texture (biggest lever)
- COMMIT one style. Write its palette (hex), material params, post params, font pairing, motion adjectives.
- The style MUST include a **material texture** the eye reads as handmade: paper fibre, brush stroke,
  cel grain, scanline, halftone, impasto. Clean vector/PBR alone = sterile = "AI default".
- DO NOT ship: chrome torus + grid + particles on near-black with cyan accents, unless explicitly requested.
- *Gate:* look at 3 stills; if you can't name the style in one word, it isn't committed.

## 2 · Animation principles & story
- Every moving thing gets: anticipation, then action, then follow-through/secondary motion.
  (A drop hovers & squashes before falling; droplets arc after impact; a stamp overshoots then settles.)
- Squash & stretch proportional to velocity. Ease everything (springs / smoothstep); no linear moves.
- **Every cut is motivated by action** (a slam, a splash, a blink) — never a timed jump.
- Give the piece a protagonist and 3–5 beats. Objects can be protagonists if they act.
- *Gate:* storyboard row per beat names the principle used; a beat with "none" gets rewritten.

## 3 · Motion blur & cadence (the cinema switch)
- ≤30 fps (24 preferred) WITH temporal supersampling over a 180° shutter (expose `dt/2`).
  Sub-samples at `t + (k+0.5)/N * dt/2`, averaged. N=3 default, N=2 if budget-tight.
- Fast camera moves without blur read as CG stutter. If you can't afford blur, slow the move.
- *Gate:* two consecutive fast-move frames, viewed side by side, must show smear not teleport.

## 4 · Sound is half the picture
- One clock: sound anchors and visual hits share exact timestamps (define them as constants in BOTH
  the score script and the scene).
- Structure > loop: a score needs an opening gesture, a build, a climax at the main anchor, a tail.
  Add Foley for physical events (drop, splash, thud) — Foley sells reality more than melody does.
- A simple reverb (2–3 feedback delays) makes synthetic instruments sit in a room.
- *Gate:* mute test — if the picture's hits don't line up with audible events, fix timestamps.

## 5 · Iteration & direction (not one-shot)
- Two passes minimum: pass 1 = build, pass 2 = revision. Never present pass 1 as final.
- Contact sheet BEFORE full render, every time. Include every cut ±0.1 s and the first/last frame.
- Also review a sheet pulled from the **encoded MP4** (encoding can surprise you).
- Offer the user 2–3 options with previews before committing to a full build when the brief is fuzzy.
- *Gate:* no full render without a clean sheet; log what the sheet caught in the final report.

## 6 · Hybrid pipeline (right tool per shot)
Code-render is best at: typography, charts/UI, graphic motion, stylized worlds, exact repeatability.
Bring in other tools ONLY for shots code draws badly:
- photoreal plate / face / fabric → generated image or video model as a plate or green-screen layer;
- restyle a code render into footage → video-to-video (e.g. Aleph-style) as a finishing pass;
- true hard-surface/organic 3D → drive Blender from code.
Keep the deterministic contract: any external asset is a **fixed file**, sampled by `seek(t)`, never re-randomized.
- *Gate:* every non-code asset is listed in the brief with its source and licence note.

---

## Numeric guard-rails (learned the hard way)

| Thing | Safe | Ruins the film |
|---|---|---|
| Bloom threshold / strength | ≥1.5 / ≤0.25 | 1.0 / 0.6 → milky veil, metal goes black |
| Additive element opacity | start at ½ of "looks right" | full → veiling glare |
| Flash peak / σ | ≤0.10 / ≤0.005 | 0.30 / 0.012 → grey wash over 4–5 frames |
| Metal roughness / envMapIntensity | 0.18–0.25 / ≥2.0 | 0.12 / 1.5 → black chrome |
| Grain | 0.02–0.04 | >0.06 → dirty |
| Vignette | 0.15–0.25 | >0.5 → tunnel |
| Ink/pigment noise | smooth value noise, fine | `floor()`-cell hash → digital camo |

## Shader-compile paranoia
A subject that silently vanishes is usually a **compile error**, and what you see instead is whatever
fallback mesh is behind it. Always capture page console during QA stills and fail loud on any
`THREE.WebGLProgram: Shader Error`. (This exact bug shipped a grey blob once.)
