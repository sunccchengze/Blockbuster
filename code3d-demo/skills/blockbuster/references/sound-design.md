# Sound design — making synthesized score sound like instruments, not plastic

The agent cannot listen, so this file does two jobs: (a) encode the physics that makes plucked
Chinese strings convincing, and (b) list the **plastic tells** and the objective gate that catches each.

## Why additive harmonics sound plastic (and the fix in `guqin.py`)

| Plastic tell | Physics it violates | Fix |
|---|---|---|
| constant brightness | high string modes decay much faster than the fundamental | block Karplus-Strong: the loop's averaging lowpass makes decay frequency-dependent |
| perfectly even harmonics | pluck position creates spectral comb nulls | excitation = noise − delay(noise, pos·N) |
| dead pitch | guqin/guzheng left hand slides (绰/注) and vibrato (吟/猱) | time-varying period length (resample the KS buffer); delayed-onset sinusoidal modulation |
| no body | soundboard resonances colour every note | FFT-domain formant peaks per instrument (`BODY`) |
| clean attack | flesh vs nail vs pick transients differ hugely | `excite='flesh'|'nail'|'pick'` |
| silent slides | finger friction on string | band-passed noise scaled by slide velocity |
| perfect grid | humans don't play on the grid | ±12 ms timing jitter + velocity jitter in `score.py` |

## Instrument presets
- **guqin** 琴 — mellow, flesh pluck, long slides, deep vibrato (猱). Use for solemn/contemplative.
- **guzheng** 筝 — brighter, nail attack, longer ring, `guozhi()` glissando sweeps as reveals/transitions.
- **pipa** 琵琶 — percussive, sharp pick, shorter decay. Use for drive/action.
- `--instrument=mix` = guqin lead + guzheng colour (the ink film's choice).

## Arrangement rules
- Structure over loop: opening gesture → build → climax at the main anchor → tail cadence.
- Foley sells reality more than melody: drop plop, splash+droplets, stamp thud, woodblock ticks.
- Space: 3-tap feedback delay with per-channel ms differences = a room, not a dry synth.
- Leave 留白: silence before the final anchor makes the hit land.
- DC/rumble: FFT high-pass at 25 Hz; normalize to **−1.2 dBTP**.

## Objective gates (`audio_qa.py`) — run before every delivery
- L1 levels: peak ≤ −1 dBTP, RMS −24..−10 dBFS, crest 8–20 dB, |DC| < 0.002
- L2 no clipping · L3 every anchor has an onset within ±60 ms (**one-clock proof**)
- **L4 anti-plastic:** spectral centroid must fall ≥15% over 400 ms after attack (static harmonics ≈ 0%)
- **L5 anti-plastic:** ≥1 held note must show f0 movement (slide/vibrato present)
- L6 clean head/tail (no EOF click)
Exit non-zero on any FAIL. Do not ship a failing score; retune, don't waive.

## When NOT to synthesize
If the brief names a real recording, a vocalist, or an ensemble — license/record it. Synthesis is for
score beds, Foley, and stylized worlds; it is not a substitute for a named performance.
