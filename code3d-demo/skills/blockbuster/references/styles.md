# Style presets — committed directions with recipes

A preset = palette + material/post params + fonts + motion adjectives + **material texture**.
Reference implementation of preset A: `scene-v3.html` in this repo (the ink film).

---

## A · ink-paper 水墨宣纸 *(the v3 recipe — proven)*
- **Idea:** one drop of ink falls on rice paper and wakes into mountains. Bold, calm, lots of 留白.
- **Palette:** paper `#ece5d6`, ink `#17181a`, wash greys, single accent vermilion `#b03a2e`.
- **Material texture:** generated rice-paper fibre scan as background AND multiplied over the composite
  (uv tile ~2.3×1.3, mix 0.24) so ink sits *in* the paper; generated ink-wash mountain plate on a
  `MultiplyBlending` plane (needs `premultipliedAlpha:true`) for parallax depth.
- **Ink shader:** concentration `c` from light bands (±0.18) × dry-brush value-noise × granulation
  value-noise × edge pigment-pooling; map `c` → `mix(0.105, 0.012, c)` linear; alpha opaque in body,
  feathered only at silhouette, punched by dry-brush near edges. NO cel outline hull (it greys the ink).
- **Post:** NO bloom. Light S-curve preserving paper white, warm tint, paper-edge stain vignette 0.17, grain 0.03.
- **Fonts:** Noto Serif CJK SC (titles 700–900), mono for meta. Vermilion seal stamp + vertical 题跋 line.
- **Motion adjectives:** calm push, breath/留白 before the final stamp, stamp = motivated cut + thud.

## B · cel-80s 赛璐璐
- Flat 3-band toon ramp + inverted-hull ink outline (outline IS the style here, unlike ink);
  hard rim light; slight film grain + gate weave; palette: sunset magenta/teal/cream.
- Fonts: bold grotesk + chrome-bevel title card. Motion: snappy, held poses, whip pans WITH blur.

## C · watercolour-brush 水彩笔触
- p5.brush-style instanced strokes (or a stroke-shader) painting shapes on cold-press paper;
  pigment pools at edges (darken by curvature), blooms outward on wet hits.
- Palette: transparent jewel tones on white. Fonts: humanist serif. Motion: strokes draw on, never pop.

## D · pixel-rpg 像素
- Render at 320×180, nearest-neighbour upscale; dithered gradients; 12-fps stepped motion inside a
  24-fps container (blur OFF deliberately — stepping is the style); chiptune arps via `score.py`.

## E · neon-noir 霓虹
- Near-black + two neon accents; strong bloom is ALLOWED here (threshold 1.2, strength 0.35) because
  the style is emissive; anamorphic streak (horizontal-only blur tap); rain/scanline overlay; grain 0.05.
- Fonts: mono + wide-tracked caps. Motion: slow drift, sudden snap-cuts on bass hits.

---

### Inventing a new preset
Answer in the brief: (1) one-word style, (2) what the surface is made of (the texture),
(3) 3 palette hexes + 1 accent, (4) light model (flat / banded / PBR), (5) post chain,
(6) font pairing, (7) 3 motion adjectives. If (2) is empty, the preset will look like plastic — go back.
