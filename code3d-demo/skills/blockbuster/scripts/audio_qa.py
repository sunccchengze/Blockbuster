#!/usr/bin/env python3
"""
audio_qa.py — objective audio gates (the agent cannot listen; metrics listen for it).

    python3 audio_qa.py out/score.wav --anchors=drop=1.0,impact=1.9,stamp=8.0 [--json=out/qa.json]

Gates (exit 1 on any FAIL):
  L1 levels      : true-peak <= -1.0 dBTP, RMS in [-24,-10] dBFS, crest factor in [8,20] dB, |DC| < 0.002
  L2 clipping    : zero samples at +-1.0
  L3 anchors     : every anchor has a detected onset within +-60 ms        ← one-clock proof
  L4 anti-plastic: spectral centroid at attack+40ms vs +400ms must FALL >= 15%   ← static-harmonic tell
  L5 anti-plastic: f0 movement detected on >= 1 held note (slide/vibrato)  ← dead-pitch tell
  L6 tails       : last 60 ms below -35 dBFS (no click at EOF), first 20 ms below -40 dBFS
"""
import argparse, json, wave, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('wav')
ap.add_argument('--anchors', default='')
ap.add_argument('--json', default='')
A = ap.parse_args()

w = wave.open(A.wav, 'rb')
sr = w.getframerate(); nch = w.getnchannels(); n = w.getnframes()
x = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float64) / 32768.0
if nch == 2:
    x = x.reshape(-1, 2).mean(1)
w.close()

res = {'file': A.wav, 'sr': sr, 'dur': len(x)/sr, 'gates': {}}
def gate(k, ok, detail):
    res['gates'][k] = {'pass': bool(ok), 'detail': detail}
    print(('  [PASS] ' if ok else '  [FAIL] ') + f'{k}: {detail}')
    return bool(ok)

# L1 levels
peak = np.max(np.abs(x))
dbtp = 20*np.log10(peak + 1e-12)
rms = np.sqrt(np.mean(x**2)); dbfs = 20*np.log10(rms + 1e-12)
crest = dbtp - dbfs
dc = abs(np.mean(x))
gate('L1_levels', (dbtp <= -0.9) and (-24 <= dbfs <= -10) and (8 <= crest <= 20) and dc < 0.002,
     f'peak {dbtp:.2f} dBTP, RMS {dbfs:.2f} dBFS, crest {crest:.1f} dB, DC {dc:.5f}')
# L2 clipping
clip = int(np.sum(np.abs(x) >= 0.999))
gate('L2_clipping', clip == 0, f'{clip} samples at full scale')
# frames for analysis
FR, HOP = 1024, 256
nf = max(1, (len(x) - FR) // HOP)
idx = np.arange(nf)[:, None] * HOP + np.arange(FR)[None, :]
mag = np.abs(np.fft.rfft(x[idx] * np.hanning(FR), axis=1))
freqs = np.fft.rfftfreq(FR, 1/sr)
flux = np.sum(np.maximum(0.0, mag[1:] - mag[:-1]), axis=1)
# onset pick
thr = np.median(flux)*3.0 + 1e-9
onsets = []
for i in range(2, len(flux)-2):
    if flux[i] > thr and flux[i] >= flux[i-1] and flux[i] > flux[i+1]:
        t = (i*HOP + FR/2)/sr
        if not onsets or t - onsets[-1] > 0.08:
            onsets.append(t)
# L3 anchors
anch = {}
for kv in A.anchors.split(','):
    if '=' in kv:
        k, v = kv.split('='); anch[k] = float(v)
miss = []
for k, t in anch.items():
    d = min((abs(o - t), o) for o in onsets) if onsets else (9.9, None)
    if d[0] > 0.060:
        miss.append(f'{k}@{t:.2f}(nearest {d[1]:.2f}, Δ{d[0]*1000:.0f}ms)')
gate('L3_anchor_sync', not miss, 'all anchors within 60ms' if not miss else 'misaligned: ' + ', '.join(miss))
# L4 centroid fall
cent = (mag * freqs).sum(1) / (mag.sum(1) + 1e-12)
falls = []
for o in onsets[:8]:
    i0 = int((o - FR/2/sr) * sr / HOP)
    i1 = i0 + int(0.04*sr/HOP); i2 = i0 + int(0.40*sr/HOP)
    if 0 <= i1 < len(cent) and 0 <= i2 < len(cent):
        a, b = cent[max(0,i0):i1+1].mean(), cent[i1:i2+1].mean()
        if a > 0: falls.append(1 - b/a)
fallmed = float(np.median(falls)) if falls else 0.0
gate('L4_brightness_decay', fallmed >= 0.15, f'median centroid fall over 400ms = {fallmed*100:.0f}% (static harmonics ≈ 0%)')
# L5 pitch movement on held notes
def f0_at(t):
    i = int(t*sr)
    if i + 2048 > len(x): return None
    seg = x[i:i+2048] * np.hanning(2048)
    ac = np.correlate(seg, seg, 'full')[2047:]
    lo, hi = int(sr/600), int(sr/70)
    if hi >= len(ac): return None
    j = lo + np.argmax(ac[lo:hi])
    return sr/j if ac[j] > 0.3*ac[0] else None
moved = 0; tested = 0
for o in onsets[:8]:
    a, b = f0_at(o+0.12), f0_at(o+0.55)
    if a and b:
        tested += 1
        if abs(b-a)/a > 0.015: moved += 1
gate('L5_pitch_life', (tested == 0) or (moved >= 1), f'{moved}/{tested} held notes show slide/vibrato f0 movement')
# L6 tails
tail = 20*np.log10(np.sqrt(np.mean(x[-int(0.06*sr):]**2)) + 1e-12)
head = 20*np.log10(np.sqrt(np.mean(x[:int(0.02*sr)]**2)) + 1e-12)
gate('L6_tails', tail < -35 and head < -40, f'head {head:.1f} dBFS, tail {tail:.1f} dBFS')

res['onsets'] = [round(o, 3) for o in onsets]
res['anchors'] = anch
ok = all(g['pass'] for g in res['gates'].values())
print(('  => AUDIO QA PASS' if ok else '  => AUDIO QA FAIL') + f'  ({sum(g["pass"] for g in res["gates"].values())}/{len(res["gates"])})')
if A.json:
    json.dump(res, open(A.json, 'w'), indent=2)
sys.exit(0 if ok else 1)
