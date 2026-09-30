#!/usr/bin/env python3
"""
audio.py — 用代码合成 12 秒音轨，不依赖任何音乐模型。

120 BPM → beat = 0.5s。鼓点落在 t = 0.5, 1.0, 1.5 ...
scene.html 里的闪白用 `beat = t % 0.5` 同一个公式算，
所以音画同步不是后期对齐出来的，是同源生成的。

和声进行：Am | F | C | G  （每 3 秒一段，对上分镜的四个 beat）

    python3 audio.py out/audio.wav
"""
import sys
import wave
import numpy as np

SR = 48000
DUR = 12.0
BPM = 120.0
BEAT = 60.0 / BPM          # 0.5s
STEP = BEAT / 4            # 16 分音符 = 0.125s

rng = np.random.default_rng(20260922)   # 播种：与画面同一个种子，确定性


def axis(dur):
    return np.arange(int(dur * SR)) / SR


def place(buf, sig, t):
    """把 sig 叠进 buf 的 t 秒处"""
    i = int(round(t * SR))
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n]


def dec(dur, tau):
    return np.exp(-axis(dur) / tau)


def harm(f, dur, k, roll=1.0):
    """加法合成：前 k 次谐波，幅度按 1/n^roll 衰减。省掉滤波器，全向量化。"""
    t = axis(dur)
    out = np.zeros_like(t)
    for n in range(1, k + 1):
        out += np.sin(2 * np.pi * f * n * t) / (n ** roll)
    return out


def saw(f, dur, k=10):
    t = axis(dur)
    out = np.zeros_like(t)
    for n in range(1, k + 1):
        out += np.sin(2 * np.pi * f * n * t + n * 0.7) / n
    return out * 0.5


# ── 音色 ──────────────────────────────────────────────────────
def kick(amp=1.0):
    d = 0.34
    t = axis(d)
    f = 46 + 88 * np.exp(-t / 0.028)              # 音高下扫
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.105)
    click = rng.standard_normal(int(0.006 * SR)) * np.exp(-axis(0.006) / 0.0016) * 0.35
    out = np.zeros(int(d * SR))
    out[:len(body)] += body
    out[:len(click)] += click
    return out * amp


def hat(amp=0.16, d=0.055):
    n = rng.standard_normal(int(d * SR))
    n = np.diff(n, prepend=0.0)                   # 一阶差分 ≈ 高通
    return n * np.exp(-axis(d) / 0.013) * amp


def sub(f, d, amp=0.55):
    t = axis(d)
    a = np.minimum(t / 0.02, 1.0) * np.minimum((d - t) / 0.18, 1.0)
    return (np.sin(2 * np.pi * f * t) * 0.8 + np.sin(4 * np.pi * f * t) * 0.2) * a * amp


def pluck(f, d=0.30, amp=0.20):
    t = axis(d)
    sig = saw(f, d, k=9) * np.exp(-t / 0.075)
    return sig * amp


def pad(fs, d, amp=0.10):
    t = axis(d)
    out = np.zeros_like(t)
    for f in fs:
        for det in (-0.14, 0.0, +0.14):           # 三条失谐，做宽度
            out += saw(f + det, d, k=7)
    a = np.minimum(t / 0.85, 1.0) * np.minimum((d - t) / 0.9, 1.0)   # 慢起慢收
    return out / (len(fs) * 3) * a * amp


def crash(amp=0.34, d=1.9):
    n = rng.standard_normal(int(d * SR))
    n = np.diff(n, prepend=0.0)
    n = np.cumsum(n) * 0.02 + n                   # 掺一点低频体重
    return n * np.exp(-axis(d) / 0.42) * amp


def riser(d, amp=0.20):
    t = axis(d)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0.0)
    swell = (t / d) ** 2.6
    tone = np.sin(2 * np.pi * np.cumsum(180 + 900 * (t / d) ** 2) / SR)
    return (n * 0.55 + tone * 0.45) * swell * amp * np.minimum((d - t) / 0.05, 1.0)


def impact(amp=0.75):
    d = 1.1
    t = axis(d)
    f = 34 + 130 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.30)
    boom = rng.standard_normal(len(t)) * np.exp(-t / 0.16) * 0.30
    return (body + boom) * amp


# ── 编排 ──────────────────────────────────────────────────────
L = np.zeros(int(DUR * SR))
R = np.zeros(int(DUR * SR))

# 和声进行：每 3 秒一段，对齐分镜
CHORDS = [
    (0.0, 110.00, [220.00, 261.63, 329.63], [220.00, 261.63, 329.63, 440.00]),   # Am
    (3.0,  87.31, [174.61, 220.00, 261.63], [174.61, 220.00, 261.63, 349.23]),   # F
    (6.0, 130.81, [164.81, 196.00, 261.63], [261.63, 329.63, 392.00, 523.25]),   # C
    (9.0,  98.00, [196.00, 246.94, 293.66], [196.00, 246.94, 293.66, 392.00]),   # G
]

# 开场：0.0–0.5 一个上扬的 swell，把第一脚鼓送进来
place(L, riser(0.52, 0.16), 0.0)
place(R, riser(0.52, 0.16), 0.0)

for (t0, root, padn, arpn) in CHORDS:
    # 底鼓：每拍一脚，从 t=0.5 开始（与画面闪白同相位）
    t = t0 + BEAT if t0 == 0.0 else t0
    while t < min(t0 + 3.0, DUR) - 1e-9:
        g = 1.0 if t >= 9.0 else (0.85 if t >= 3.0 else 0.7)
        place(L, kick(g), t)
        place(R, kick(g) * 0.96, t)
        t += BEAT

    # 踩镲：8 分反拍，第二段起才进来，越往后越密
    if t0 >= 3.0:
        tt = t0 + BEAT / 2
        while tt < min(t0 + 3.0, DUR) - 1e-9:
            a = 0.10 + 0.09 * (tt / DUR)
            place(L, hat(a * 0.7), tt)
            place(R, hat(a), tt)
            tt += BEAT

    # Sub 低音：跟着和声根音
    place(L, sub(root, 3.0, 0.50), t0)
    place(R, sub(root, 3.0, 0.50), t0)

    # Pad：铺满整段
    place(L, pad(padn, 3.05, 0.115), t0)
    place(R, pad([f * 1.002 for f in padn], 3.05, 0.115), t0)

    # 琶音：第三段起用 16 分，推向 9.0 的爆点
    if t0 >= 6.0:
        tt = t0
        i = 0
        while tt < min(t0 + 3.0, DUR) - 1e-9 and t0 < 9.0:
            f = arpn[i % len(arpn)]
            a = 0.13 + 0.10 * ((tt - t0) / 3.0)
            place(L, pluck(f, 0.26, a), tt)
            place(R, pluck(f * 1.0, 0.26, a * 0.92), tt + 0.004)
            tt += STEP
            i += 1

# 7.4 → 9.0 长 riser，接 9.0 的 impact（对应分镜第 4 镜的俯冲）
place(L, riser(1.6, 0.26), 7.4)
place(R, riser(1.6, 0.26), 7.4)
place(L, impact(0.85), 9.0)
place(R, impact(0.85), 9.0)
place(L, crash(0.30, 2.2), 9.0)
place(R, crash(0.30, 2.2), 9.0)

# 尾段：G 大调和弦铺开，收在 12.0
place(L, pad([196.00, 246.94, 293.66, 392.00], 3.0, 0.135), 9.0)
place(R, pad([196.40, 247.30, 294.10, 392.60], 3.0, 0.135), 9.0)
for i, f in enumerate([392.00, 493.88, 587.33]):       # 结尾三声钟
    place(L, pluck(f, 0.9, 0.16), 10.5 + i * 0.5)
    place(R, pluck(f, 0.9, 0.16), 10.5 + i * 0.5)

# ── 混音 ──────────────────────────────────────────────────────
m = (L + R) * 0.5
side = (L - R) * 0.5

st = np.stack([L, R], axis=1)
st = np.tanh(st * 1.25) / np.tanh(1.25)          # 软削波，把各轨黏起来

# 淡入淡出
fi = int(0.04 * SR)
fo = int(0.75 * SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]
st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.6

peak = np.max(np.abs(st))
st = st / peak * (10 ** (-1.0 / 20))              # 峰值 -1.0 dBFS
pcm = (st * 32767).astype('<i2')

out = sys.argv[1] if len(sys.argv) > 1 else 'out/audio.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

rms = float(np.sqrt(np.mean(st ** 2)))
print(f'[audio] {out}  ·  {DUR}s / {SR}Hz / stereo  ·  peak {peak:.3f}  ·  RMS {20*np.log10(rms+1e-12):.1f} dBFS')
print(f'[audio] {BPM:.0f} BPM · beat={BEAT}s · 鼓点相位与 scene.html 的 t%0.5 闪白一致')
