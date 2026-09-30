# brief.md template — the contract between direction and execution

Fill every block. Empty block = go back to intake. Save as `brief.md` at project root.

```md
# BRIEF — <working title>

## 1 · Logline
<one sentence: who/what does what, and why we care>

## 2 · Delivery
length: <s>   aspect: <16:9|9:16|1:1>   fps: <24|30>   shutter: 180°   res: <1280x720|1920x1080>
codec: h264+aac mp4 (+faststart)   target: <feed|stage|hero|festival>

## 3 · Art direction (committed)
preset: <ink-paper|cel-80s|watercolour|pixel|neon-noir|custom:>
palette: bg #___  primary #___  secondary #___  accent #___
material texture: <paper fibre / brush stroke / cel grain / scanline / …>  ← mandatory
light model: <flat|banded|PBR>   post: <chain from pipeline.md>
fonts: title <…>  body <…>  meta <…>
motion adjectives: <3 words, e.g. "calm, breathing, decisive">

## 4 · Beats (storyboard source of truth)
| # | t0–t1 | action | animation principle | camera | sound anchor |
|---|---|---|---|---|---|
| 1 | 0.0–1.0 | drop swells, hesitates | anticipation + squash | slow push | — |
| … | | | | | |

## 5 · Text on screen
| t0–t1 | copy (verbatim) | lang | placement | backing |
|---|---|---|---|---|
(Backing = panel/paper-wash so it survives over subject. CJK? confirm font present.)

## 6 · Sound
source: <scripts/score.py | user track | TTS+word-ts>
instrument preset: <guqin|guzheng|pipa|mix>   mood: <calm|drive>   scale root: <Hz>
anchors: drop=@<t>  impact=@<t>  reveal=@<t>  stamp=@<t>
   ← run score.py --emit-anchors=out/anchors.json ONCE; scene.html fetches it (single source of truth)
foley: <list physical events>
loudness target: <-14 LUFS feed | -16 web | -23 broadcast>   true peak: -1 dBTP
audio gates: audio_qa.py 6/6 (incl. L4 brightness-decay, L5 pitch-life anti-plastic)

## 7 · Hybrid assets & budget
external assets: <file — source — licence>   (none is a valid answer)
render estimate: <frames> × <sub-samples> × <per-frame s> ≈ <wall>
qa gates: stills at <list> + encoded-MP4 sheet
```
