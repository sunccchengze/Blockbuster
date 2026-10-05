"""bb.score — 分场景配乐引擎：弦乐群/钢琴/大提琴断奏/拨弦/钟琴/定音鼓/鼓组 + 同步音效 + 混响 + 人声闪避。

写法：buses(T) → 按场景提示表 add()/chord_strings()/prog() → finish(mus, sfx, voice, "mix.wav")。
禁忌：持续嗡鸣/单音垫底、刺耳的转场音效；音乐必须随画面事件变化。
"""
import numpy as np, wave, math, re
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000
rng = np.random.default_rng(3)
def buses(T):
    global mus, sfx
    N = int(T * SR); mus, sfx = np.zeros((2, N), np.float32), np.zeros((2, N), np.float32); return mus, sfx
def mf(m): return 440 * 2 ** ((m - 69) / 12)
def add(bus, t0, sig, pan=0.0, g=1.0):
    N = bus.shape[1]
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0: return
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    sig = sig[:N - i0] * g; l, r = math.cos((pan + 1) * pi4), math.sin((pan + 1) * pi4)
    bus[0, i0:i0 + len(sig)] += sig * l; bus[1, i0:i0 + len(sig)] += sig * r
pi4 = math.pi / 4
def env_adsr(n, a, r):
    e = np.ones(n, np.float32); na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[n - nr:] *= np.linspace(1, 0, nr); return e
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x).astype(np.float32)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x).astype(np.float32)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x).astype(np.float32)

# ---------- instruments ----------
def strings(m, dur, a=0.7, r=1.0, bright=1.0, trem=0.0):
    n = int((dur + r) * SR); t = np.arange(n) / SR; f = mf(m); out = np.zeros(n, np.float32)
    for det in (-0.08, 0.0, 0.07):          # 三把琴略微走音 = 弦乐群感
        ph0 = rng.uniform(0, 6.28); vib = 1 + 0.004 * np.sin(2 * np.pi * (5.2 + det * 3) * t + ph0)
        phase = 2 * np.pi * f * 2 ** (det / 12) * np.cumsum(vib) / SR
        for h in range(1, 11):
            if f * h > 9000: break
            out += (np.sin(h * phase + h * ph0) / h ** (1.6 - 0.4 * bright)).astype(np.float32)
    e = env_adsr(n, a, r)
    if trem: e *= (0.6 + 0.4 * np.sin(2 * np.pi * trem * t) ** 2).astype(np.float32)
    return out * e * 0.12
def cello_stac(m, dur=0.22):
    n = int(dur * SR * 1.6); t = np.arange(n) / SR; f = mf(m); out = np.zeros(n, np.float32)
    for h in range(1, 9): out += np.sin(2 * np.pi * f * h * t) / h ** 1.3
    return out * np.exp(-t * 9).astype(np.float32) * np.minimum(1, t * 200) * 0.25
def piano(m, v=1.0, dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = mf(m); out = np.zeros(n, np.float32)
    for h in range(1, 8):
        fh = f * h * (1 + 0.0004 * h * h); out += np.sin(2 * np.pi * fh * t) * np.exp(-t * (1.2 + h * 0.9)) / h ** 1.1
    return out * np.minimum(1, t * 400) * 0.3 * v
def pluck(m, v=1.0, dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR; f = mf(m)
    return ((np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 5) * 0.22 * v).astype(np.float32)
def bell(m, v=1.0, dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR; f = mf(m)
    return ((np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.8) * 0.18 * v).astype(np.float32)
def timpani(m=38, v=1.0):
    n = int(2.2 * SR); t = np.arange(n) / SR; f = mf(m) * (1 + 0.15 * np.exp(-t * 30))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) + 0.3 * lp(rng.normal(size=n), 400) * np.exp(-t * 18)
    return (s * 0.7 * v).astype(np.float32)
def kick(v=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR; f = 45 + 90 * np.exp(-t * 25)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.8 * v).astype(np.float32)
def hat(v=1.0):
    n = int(0.08 * SR); return hp(rng.normal(size=n), 7000) * np.exp(-np.arange(n) / SR * 60).astype(np.float32) * 0.12 * v
def snare(v=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    return (bp(rng.normal(size=n), 1500, 6000) * np.exp(-t * 16) * 0.35 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20) * 0.3).astype(np.float32) * v

# ---------- sfx ----------
def rumble(dur, a=1.0, r=1.5, fc=180):
    n = int((dur + r) * SR); x = lp(rng.normal(size=n), fc, 3); x /= np.abs(x).max() + 1e-9
    crackle = bp(rng.normal(size=n), 800, 3000) * (rng.random(n) < 0.004) * 3
    return (x * 0.9 + lp(crackle, 4000) * 0.3) * env_adsr(n, a, r)
def whoosh(dur=1.0, lo=300, hi=3000, v=1.0):
    n = int(dur * SR); x = rng.normal(size=n).astype(np.float32); out = np.zeros(n, np.float32); k = 8
    for i in range(k):
        seg = slice(i * n // k, (i + 1) * n // k); fc = lo * (hi / lo) ** (math.sin(math.pi * (i + 0.5) / k))
        out[seg] = bp(x, fc * 0.7, min(fc * 1.4, 18000))[seg]
    return out * np.sin(np.linspace(0, math.pi, n)) ** 2 * 0.35 * v
def riser(dur, v=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.normal(size=n).astype(np.float32); out = np.zeros(n, np.float32); k = 12
    for i in range(k):
        seg = slice(i * n // k, (i + 1) * n // k); fc = 300 * (8000 / 300) ** (i / k); out[seg] = bp(x, fc * 0.6, fc * 1.3)[seg]
    tone = np.sin(2 * np.pi * np.cumsum(200 * 4 ** (t / dur)) / SR) * 0.3
    return (out + tone) * (t / dur) ** 2 * 0.4 * v
def boom(v=1.0):
    n = int(2.5 * SR); t = np.arange(n) / SR
    return (lp(rng.normal(size=n), 250, 3) * 3 * np.exp(-t * 2.5) + np.sin(2 * np.pi * np.cumsum(60 * np.exp(-t * 3) + 30) / SR) * np.exp(-t * 3)).astype(np.float32) * 0.6 * v
def ping(f=2400, v=1.0):
    n = int(0.9 * SR); t = np.arange(n) / SR; s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
    s = s + 0.4 * np.concatenate([np.zeros(int(0.18 * SR)), s[:n - int(0.18 * SR)]])
    return (s * 0.12 * v).astype(np.float32)
def clink(v=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR; f = rng.uniform(2800, 3600)
    return ((np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 2.3 * t)) * np.exp(-t * 18) * 0.1 * v).astype(np.float32)
def blip(f, v=1.0):
    n = int(0.09 * SR); t = np.arange(n) / SR; return (np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 30) * 0.05 * v).astype(np.float32)
def alarm(dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = np.where((t * 2.5) % 1 < 0.5, 880, 660)
    return lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 2500) * 0.04 * env_adsr(n, 0.1, 0.3)
def city(dur):
    n = int(dur * SR); x = lp(rng.normal(size=n), 700, 2) * 0.5; x += bp(rng.normal(size=n), 2000, 5000) * 0.05
    return x * env_adsr(n, 1.0, 1.0) * 0.5
def heartbeat(v=1.0):
    a = kick(0.8 * v)[:int(0.3 * SR)]; out = np.zeros(int(0.7 * SR), np.float32); out[:len(a)] += a; b = int(0.22 * SR); out[b:b + len(a)] += a * 0.6; return lp(out, 150)

def chord_strings(t0, t1, notes, g=1.0, a=0.8, r=1.2, bright=1.0, trem=0):
    for j, m in enumerate(notes): add(mus, t0, strings(m, t1 - t0, a, r, bright, trem), pan=(j / max(1, len(notes) - 1) - 0.5) * 0.8, g=g)
def prog(t0, t1, chords, fn):
    step = (t1 - t0) / len(chords)
    for i, c in enumerate(chords): fn(t0 + i * step, t0 + (i + 1) * step, c)


# 和弦
Am = [45, 57, 60, 64]; F = [41, 57, 60, 65]; C = [48, 55, 60, 64]; Gm_ = [43, 55, 59, 62]; Em = [40, 55, 59, 64]
Dm = [38, 53, 57, 62]; Bb = [46, 53, 58, 62]; A7 = [45, 55, 61, 64]; Gm = [43, 55, 58, 62]; D = [38, 54, 57, 62]
Cmaj7 = [48, 55, 59, 64]; Am7 = [45, 55, 60, 64]; Fmaj7 = [41, 57, 60, 64]; G6 = [43, 55, 59, 64]; Dm7 = [38, 57, 60, 65]; Em7 = [40, 55, 59, 62]
def reverb(x, dec=2.2, wet=0.28):
    n = int(dec * SR); t = np.arange(n) / SR
    out = np.zeros_like(x)
    for c in range(2):
        ir = (rng.normal(size=n) * np.exp(-t * 6.9 / dec)).astype(np.float32); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
        out[c] = x[c] + wet * fftconvolve(x[c], ir)[:x.shape[1]].astype(np.float32)
    return out

def read_audio(p):
    import os, subprocess
    from .media import ffmpeg
    root, ext = os.path.splitext(p)
    if ext == '.wav' and not os.path.isfile(p):
        alt = root + '.flac'
        if os.path.isfile(alt): p = alt
    ff = ffmpeg()
    raw = subprocess.run([ff, '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-'], capture_output=True, check=True).stdout
    info = subprocess.run([ff, '-i', p], capture_output=True, text=True).stderr
    sr = int(re.search(r'(\d+) Hz', info).group(1))
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768, sr
def load_voice(paths, delays, N):
    v = np.zeros(N, np.float32)
    for p, d in zip(paths, delays):
        a, sr = read_audio(p)
        if sr != SR: a = np.interp(np.arange(0, len(a), sr / SR), np.arange(len(a)), a).astype(np.float32)
        i0 = int(d * SR); n = min(len(a), N - i0); v[i0:i0 + n] += a[:n]
    return v
def finish(mus, sfx, voice, out, music_gain=0.42, voice_gain=1.0):
    mus = reverb(mus, 2.4, 0.35); sfx = reverb(sfx, 1.2, 0.12)
    envv = lp(np.abs(voice), 4, 1); envv = np.clip(envv / (np.percentile(envv, 95) + 1e-9), 0, 1)
    m = mus * (1 - 0.45 * envv) + sfx * (1 - 0.25 * envv); m /= np.abs(m).max() + 1e-9; m *= 0.9
    mix = m * music_gain + voice[None, :] * voice_gain
    mix /= np.abs(mix).max() + 1e-9; mix *= 0.95
    w = wave.open(out, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype(np.int16).tobytes()); w.close()

# ---------- 额外音效 ----------
def bubbles(dur, rate=12, v=1.0):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    for _ in range(int(dur * rate)):
        i0 = int(rng.uniform(0, dur - 0.1) * SR); m = int(0.06 * SR); t = np.arange(m) / SR; f0 = rng.uniform(600, 1600)
        out[i0:i0 + m] += np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * t / 0.06)) / SR) * np.exp(-t * 60) * 0.08
    return out * env_adsr(n, 0.3, 0.5) * v
def zap(v=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (bp(rng.normal(size=n), 3000, 9000) * 0.3 + np.sin(2 * np.pi * np.cumsum(2400 - 1600 * t / 0.12) / SR) * 0.15) * np.exp(-t * 35) * 0.5 * v
def tick(v=1.0, f=3200):
    n = int(0.03 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 200) * 0.2 * v).astype(np.float32)
def chalk(dur=0.8, v=1.0):
    n = int(dur * SR); x = bp(rng.normal(size=n), 2500, 7000); g = (np.sin(np.arange(n) / SR * 2 * np.pi * 9) > 0).astype(np.float32)
    return x * lp(g, 40) * env_adsr(n, 0.05, 0.1) * 0.08 * v
def beep(f=1760, dur=0.12, v=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * env_adsr(n, 0.005, 0.03) * 0.08 * v).astype(np.float32)
def rattle(dur=0.5, v=1.0):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    for k in range(7):
        i0 = int(dur * SR * (1 - (1 - k / 7) ** 1.7)); c = clink(0.5)[: int(0.05 * SR)]; c = lp(c * 3, 2500)
        out[i0:i0 + len(c)] += c[: n - i0] * (1 - k / 9)
    return out * v
def thud(v=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 12) + 50) / SR) * np.exp(-t * 14) * 0.5 + lp(rng.normal(size=n), 800) * np.exp(-t * 40) * 0.2).astype(np.float32) * v
def creak(dur, v=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = 120 + 60 * t / dur
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t))
    return lp(s.astype(np.float32), 1500) * env_adsr(n, 0.1, 0.2) * 0.05 * v
def glitch(dur, v=1.0):
    n = int(dur * SR); out = np.zeros(n, np.float32); k = 0
    while k < n:
        L = int(rng.uniform(0.02, 0.08) * SR); f = rng.choice([200, 400, 1600, 3200]); t = np.arange(min(L, n - k)) / SR
        out[k:k + len(t)] = np.sign(np.sin(2 * np.pi * f * t)) * rng.uniform(0, 0.08); k += L + int(rng.uniform(0, 0.06) * SR)
    return lp(out, 6000) * v
def shutter(v=1.0):
    return (tick(1.0, 5000) * 2 + np.concatenate([np.zeros(int(0.04 * SR), np.float32), hp(rng.normal(size=int(0.05 * SR)), 3000) * 0.06])[: int(0.03 * SR)].sum() * 0 + np.pad(hp(rng.normal(size=int(0.06 * SR)), 2500) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70) * 0.15, (0, 0))[: int(0.03 * SR)]) * v
