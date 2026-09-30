# Delivery — specs, naming, QC

## Loudness & peaks (pick by target, state it in the brief)
| Target | Integrated loudness | True peak |
|---|---|---|
| Feed / social (default) | −14 LUFS | −1 dBTP |
| Web hero / product | −16 LUFS | −1 dBTP |
| Broadcast-safe | −23 LUFS (EBU R128) | −1 dBTP |
| Festival / cinema hand-off | −24 LKFS ±2 | −2 dBTP |
`score.py` normalizes to −1.2 dBTP; do final loudness at mux time with
`ffmpeg -af loudnorm=I=<target>:TP=-1:LRA=11` when a LUFS target is specified (measure first with
`ffmpeg -af ebur128 -f null -` and use two-pass loudnorm for accuracy).

## Container & codecs
- Delivery: H.264 High + AAC-LC 192k, MP4, `+faststart`, yuv420p (player-safe).
- Master: keep the silent PNG-sequence or ProRes/FFV1 intermediate + WAV stems; never re-encode the master.
- fps/res/shutter exactly as briefed (24fps/180° default). Vertical builds: 1080×1920, keep action in centre 60%.

## Naming & sidecars (everything the next person needs)
```
video/<title>-<ver>.mp4          delivery
video/<title>-<ver>-sheet.png    contact sheet from the ENCODED file
video/<title>-spectrogram.png    score spectrogram (audio evidence)
brief.md  STORYBOARD.md  out/anchors.json  out/audio-qa.json
```
`anchors.json` (from `score.py --emit-anchors`) is the single source of truth for sound/visual sync;
`scene.html` should fetch it rather than hard-code timestamps.

## QC checklist before handing over (all mandatory)
- [ ] contact sheet from encoded MP4 reviewed (cuts ±0.1 s, first/last frame)
- [ ] `audio_qa.py` 6/6 PASS, json archived
- [ ] loudness measured & matches target; true peak ≤ target
- [ ] duration = briefed ±1 frame; A/V sync spot-checked at 2 anchors by eye+meter
- [ ] text legible at 25% scale (feed thumbnail test) and in the darkest frame
- [ ] no shader-fallback frames (QA stills console clean)
- [ ] deliverable copied OUT of `out/` (snapshot-excluded dir)
- [ ] licence note for every external asset (incl. generated plates)

## Poster & extras (offer, don't assume)
Poster frame at the strongest composition (`ffmpeg -ss <t> -frames:v 1`); loop-safe variant (first=last
frame, no tail fade) if the target loops; caption/SRT if narration exists; 3 s preview cut for feeds.
