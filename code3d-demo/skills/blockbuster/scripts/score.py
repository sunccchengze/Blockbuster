#!/usr/bin/env python3
"""
score.py — structured score + Foley on physically-modelled Chinese plucked strings.
NO music models, NO samples. ONE CLOCK with the picture.

    python3 score.py out/score.wav --dur=10 --anchors=drop=1.0,impact=1.9,stamp=8.0 \
        --arrange=ink --instrument=mix --emit-anchors=out/anchors.json

The anchors you pass MUST equal the constants in scene.html. With --emit-anchors the script
writes anchors.json so the scene can fetch it instead of hard-coding (single source of truth).

Instruments come from guqin.py (block Karplus-Strong + slides/vibrato/friction/body formants).
Arrangements add humanisation: ±12 ms timing jitter, velocity jitter, unequal note lengths —
perfect grid = plastic.
"""
import argparse, json, wave
import numpy as np
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guqin as G

SR = G.SR
ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--dur', type=float, default=10.0)
ap.add_argument('--anchors', default='')
ap.add_argument('--arrange', default='generic', choices=['ink', 'generic'])
ap.add_argument('--instrument', default='mix', choices=['guqin', 'guzheng', 'pipa', 'mix'])
ap.add_argument('--mood', default='calm', choices=['calm', 'drive'])
ap.add_argument('--root', type=float, default=130.81)
ap.add_argument('--seed', type=int, default=20260930)
ap.add_argument('--emit-anchors', default='')
A = ap.parse_args()

anch = {}
for kv in A.anchors.split(','):
    if '=' in kv:
        k, v = kv.split('='); anch[k] = float(v)
if A.emit_anchors:
    os.makedirs(os.path.dirname(os.path.abspath(A.emit_anchors)) or '.', exist_ok=True)
    json.dump({'dur': A.dur, 'fps_note': 'share these with scene.html', **anch},
              open(A.emit_anchors, 'w'), indent=2)

rng = np.random.default_rng(A.seed)
N = int(A.dur * SR)
L, R = np.zeros(N), np.zeros(N)
B = [L, R]

def put(sig, t, pan=0.0, human=True):
    if human:
        t += rng.uniform(-0.012, 0.012)          # 微时序：人不会在网格上
    i = int(round(t * SR))
    if i >= N or i < 0: return
    n = min(len(sig), N - i)
    v = rng.uniform(0.88, 1.12) if human else 1.0
    B[0][i:i+n] += sig[:n] * v * (1 - max(0.0, pan))
    B[1][i:i+n] += sig[:n] * v * (1 - max(0.0, -pan))

# ── 打击 / Foley ────────────────────────────────────────────
def drum(f0=95, d=0.5, amp=0.4):
    t = np.arange(int(d*SR))/SR
    f = f0*0.62 + (f0-f0*0.62)*np.exp(-t/0.045)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.16)
            + rng.standard_normal(len(t))*np.exp(-t/0.020)*0.35)*amp
def tick(amp=0.12, f=2100):
    d = 0.05; n = rng.standard_normal(int(d*SR)); n = np.diff(n, prepend=0.0)
    return (n*0.8 + np.sin(2*np.pi*f*np.arange(len(n))/SR)*0.4)*np.exp(-np.arange(len(n))/SR/0.010)*amp
def plop(amp=0.3):
    d = 0.16; t = np.arange(int(d*SR))/SR
    f = 950-650*(t/d)**0.7
    o = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.045)
    c = rng.standard_normal(int(0.004*SR))*0.4
    o[:len(c)] += c
    return o*amp
def splash(amp=0.32):
    d = 0.55; t = np.arange(int(d*SR))/SR
    n = rng.standard_normal(len(t)); n = np.cumsum(n)*0.03 + n*0.7
    o = n*np.exp(-t/0.10)
    for k in range(6):
        i = int((0.05+0.055*k+rng.uniform(0, 0.02))*SR); Ln = int(0.05*SR)
        if i+Ln < len(o):
            f = 700-380*(np.arange(Ln)/SR/0.05)
            o[i:i+Ln] += np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-np.arange(Ln)/SR/0.02)*0.16
    return o*amp
def thud(amp=0.8):
    d = 0.9; t = np.arange(int(d*SR))/SR
    f = 78-34*np.exp(-t/0.06)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.26)
            + rng.standard_normal(len(t))*np.exp(-t/0.012)*0.5
            + rng.standard_normal(len(t))*np.exp(-t/0.05)*0.12)*amp
def shimmer(amp=0.09, d=1.6):
    t = np.arange(int(d*SR))/SR
    return sum(np.sin(2*np.pi*f*t)*np.exp(-t/0.5) for f in (1567.98, 2093.0, 2637.02))/3*amp

def pl(f, dur=1.8, amp=0.2, **kw):
    """route to the chosen instrument (mix = guqin lead + guzheng colour)"""
    inst = kw.pop('inst', None) or (A.instrument if A.instrument != 'mix' else 'guqin')
    return G.note(f, dur=dur, inst=inst, amp=amp, seed=int(f*131) & 0xFFFF, **kw)

r = A.root
SC = [r, r*9/8, r*5/4, r*3/2, r*5/3, r*2, r*2*9/8, r*2*3/2]     # 宫商角徵羽 + octaves
t0 = anch.get('drop', A.dur*0.10); t1 = anch.get('impact', A.dur*0.19); t2 = anch.get('stamp', A.dur*0.80)

room = rng.standard_normal(N)*0.006; L += room; R += rng.standard_normal(N)*0.006

if A.arrange == 'ink':
    # 开场：一声带"绰"（上滑）+ 吟的低音 = 古琴的招牌韵
    put(pl(SC[0], 2.4, 0.24, slide_to=SC[0]*2**(2/12), slide_start=0.05, slide_dur=0.30, vibrato=1), t0*0.55, -0.25)
    put(plop(0.30), t0, 0.0)
    put(pl(SC[7], 0.8, 0.06, inst='guzheng'), t0+0.02, 0.35)          # 一滴的高泛音
    put(splash(0.34), t1, 0.0); put(drum(95, 0.55, 0.42), t1, 0.0)
    # 旋律 A（疏，带滑音）
    for i, (dt, d, pan) in enumerate([(0.40, 5, -0.3), (0.95, 3, 0.2), (1.50, 2, -0.2), (2.05, 0, 0.3)]):
        sl = dict(slide_to=SC[d]*2**(-1/12), slide_start=0.5, slide_dur=0.35, vibrato=1) if i in (1, 3) else {}
        put(pl(SC[d], 1.7, 0.17, **sl), t1+dt, pan)
    for tt in (t1+0.7, t1+2.2, t1+3.7, t2-0.9):
        put(drum(88, 0.5, 0.30), tt, 0.0)
    # 揭示处：古筝刮奏（招牌）
    put(G.guozhi(SC[5], SC[5]*2, 9, 1.5, 'guzheng', 0.13, seed=A.seed+5), t1+2.55, 0.1)
    # 旋律 B（密）
    for i, (dt, d) in enumerate([(2.70, 5), (3.05, 4), (3.40, 3), (3.75, 2), (4.10, 1), (4.45, 2), (4.80, 3), (5.15, 4)]):
        if t1+dt > t2-0.5: break
        put(pl(SC[d], 1.2, 0.15, inst='guzheng'), t1+dt, 0.3 if i % 2 else -0.3)
    for i, tt in enumerate((t2-1.8, t2-1.5, t2-1.2)):
        put(tick(0.12), tt, 0.4 if i % 2 else -0.4)
    put(thud(0.85), t2, 0.0)
    put(pl(SC[0], 2.8, 0.26, vibrato=2), t2, 0.0)                     # 盖印后的长吟
    put(shimmer(0.09, 1.7), t2+0.02, 0.15)
    for i, (dt, d) in enumerate([(0.45, 5), (0.95, 3), (1.40, 0)]):
        put(pl(SC[d], 2.0, 0.13, vibrato=1 if i == 0 else 0), t2+dt, -0.3 if i % 2 else 0.3)
else:  # generic
    put(pl(SC[0], 2.2, 0.22, vibrato=1), A.dur*0.06, -0.2)
    put(drum(95, 0.5, 0.35), t1, 0.0)
    step = 0.55 if A.mood == 'calm' else 0.36
    t = t1 + 0.4
    for i, d in enumerate([5, 3, 2, 0, 2, 3, 5, 4]):
        if t > t2 - 0.6: break
        put(pl(SC[d], 1.5, 0.16, vibrato=1 if i % 3 == 2 else 0), t, -0.3 if i % 2 else 0.3)
        t += step
    for tt in np.arange(t1+0.7, t2-0.6, step*2.7):
        put(drum(88, 0.5, 0.28), tt, 0.0)
    put(thud(0.8), t2, 0.0); put(pl(SC[0], 2.6, 0.24, vibrato=2), t2, 0.0)
    put(pl(SC[3], 1.8, 0.12), t2+0.5, 0.25); put(pl(SC[0], 2.0, 0.12), t2+1.0, -0.25)

# ── 空间：三级延迟 + 微立体差 ───────────────────────────────
for ch in (0, 1):
    s = B[ch].copy()
    for dt, g in ((0.121 + ch*0.004, 0.24), (0.263, 0.12), (0.411 + ch*0.006, 0.06)):
        i = int(dt*SR); s[i:] += B[ch][:-i]*g
    B[ch] = s

st = np.stack([L, R], 1)
st = np.tanh(st*1.2)/np.tanh(1.2)
# DC / rumble 去除：FFT 高通 25Hz（平滑斜坡）
for ch in (0, 1):
    S = np.fft.rfft(st[:, ch])
    f = np.fft.rfftfreq(len(st), 1/SR)
    S *= 1/(1 + np.exp(-(f-25.0)/6.0))
    st[:, ch] = np.fft.irfft(S, len(st))
fi, fo = int(0.05*SR), int(min(0.9, A.dur*0.1)*SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]
st[-fo:] *= np.linspace(1, 0, fo)[:, None]**1.5
st = st/np.max(np.abs(st))*10**(-1.2/20)          # -1.2 dBTP 留 headroom
with wave.open(A.out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print(f'[score] {A.out} · {A.dur}s · arrange={A.arrange} inst={A.instrument} · anchors={anch} (one clock)')
