# Intake — the questions that block production

Ask these BEFORE any code. Batch them into one message; offer 2–4 options each where sensible.
If the user already specified something, don't re-ask it.

## Blocking (creative axes — never silently default)

1. **Purpose & audience** — promo / explainer / MV / title sequence / art film? Where will it play
   (feed, stage, site hero)? Feeds want early hook + vertical; stage wants slow and wide.
2. **Subject & story** — what is the ONE thing happening? Demand 3–5 beats in plain sentences.
   If they can't give beats, propose them and confirm. *A film needs a protagonist; an object can be one
   (a drop of ink, a seed, a coin) but it must ACT (hesitate, fall, splash, settle).*
3. **Art direction** — offer committed presets from `styles.md` (ink-paper / cel-80s / watercolour /
   pixel / neon-noir) with a one-line visual each. Ask them to pick or name a reference.
   Explicitly warn against "generic dark tech" unless requested.
4. **Length & aspect** — default 10–15 s, 16:9. Vertical 9:16 changes composition rules (safe zones).
5. **Text & language** — on-screen copy verbatim; language; font mood (serif/calligraphic/mono/grotesk).
   Confirm CJK needs a CJK font present in the render env.
6. **Sound** — score mood + 2–4 **anchors** (timestamps of the narrative hits: drop, impact, reveal, stamp).
   Offer: synthesized score (default, `scripts/score.py`), user-supplied track, or TTS narration + word timestamps.

## Non-blocking (sensible defaults, state them)

- fps / shutter: **24 fps, 180° shutter** (film cadence). 30 fps only for feed-native.
- Resolution: 1280×720 on CPU/software GL; 1080p only if the user accepts ~2.2× render time.
- Motion blur sub-samples: 3 (drop to 2 if per-frame budget exceeded).
- Delivery: H.264 MP4 + AAC, `+faststart`.
- HUD / meta overlay: **off** for films, on only for pipeline demos (ask).

## Budget honesty (say it out loud before committing)
Give an estimate: `frames = dur × fps`, `renders = frames × sub-samples`,
`wall ≈ renders × per-frame`, with per-frame measured from a 3-still test run.
If the estimate exceeds what the user wants to wait for, reduce dur / fps / resolution —
**never** reduce motion blur or QA gates to save time.
