"""讲解片配乐公共件：和弦表 + 律动 + 钢琴分解 + 大提琴断奏。每部片的 score.py 只写“提示表”。"""
import math
from bb.score import *
C = [48, 55, 60, 64]; Am = [45, 57, 60, 64]; F = [41, 57, 60, 65]; G_ = [43, 55, 59, 62]; Dm = [38, 53, 57, 62]
Bb = [46, 53, 58, 62]; Eb = [39, 55, 58, 63]; Em = [40, 55, 59, 64]; D = [38, 54, 57, 62]; A7 = [45, 55, 61, 64]
Cm = [36, 55, 60, 63]; Ab = [44, 56, 60, 63]; Fm = [41, 56, 60, 65]; E_ = [40, 56, 59, 64]


class Cues:
    def __init__(s, r3d):
        s.r = r3d; s.T = r3d.TOTAL; s.mus, s.sfx = buses(s.T); s.S = r3d.SEG
    def G(s, k, lt): return s.S[k] + lt
    def E(s, k): return [s.G(k, s.r.ev(k, i)) for i in range(len(s.r.SUBS[k]))]
    def end(s, k): return s.S[k] + s.r.dur[k] + 0.3

    def groove(s, t0, t1, bpm, chords, kick_v=0.45, hat_v=0.6, pl=True, snare_v=0.2, strings_g=0.32):
        b = 60 / bpm; i = 0; t = t0; mus = s.mus
        while t < t1 - 0.05:
            c = chords[(i // 8) % len(chords)]
            if i % 2 == 0 and kick_v: add(mus, t, kick(kick_v if (i // 2) % 2 == 0 else kick_v * 0.6))
            if hat_v: add(mus, t, hat(hat_v * (1 if i % 2 else 0.5)), pan=0.3)
            if i % 4 == 2 and snare_v: add(mus, t, snare(snare_v))
            if pl: add(mus, t, pluck(c[1 + (i % 3)] + 12, 0.42), pan=0.35 * math.sin(i))
            if i % 8 == 0 and strings_g: chord_strings(t, min(t1, t + 4 * b), c, strings_g, 0.4, 0.5, 1.0)
            t += b / 2; i += 1

    def piano_arp(s, t0, t1, bpm, chords, v=0.42, strings_g=0.3):
        b = 60 / bpm; t = t0; i = 0
        while t < t1 - 0.1:
            c = chords[(i // 8) % len(chords)]
            add(s.mus, t, piano(c[1 + i % 3] + 12 * (i % 2), v, 2.0), pan=0.4 * math.sin(i * 0.7))
            if i % 8 == 0:
                add(s.mus, t, piano(c[0], v * 1.1, 3.5))
                if strings_g: chord_strings(t, min(t1, t + 4 * b), c, strings_g, 0.7, 0.7, 0.9)
            t += b / 2; i += 1

    def cello(s, t0, t1, bpm, roots, v=0.5):
        b = 60 / bpm; t = t0; i = 0
        while t < t1 - 0.1:
            add(s.mus, t, cello_stac(roots[(i // 8) % len(roots)] - 12 + (7 if i % 4 == 3 else 0)), g=v)
            t += b / 2; i += 1

    def pad(s, t0, t1, chords, g=0.45):
        prog(t0, t1, chords, lambda a, b_, c: chord_strings(a, b_, c, g, 0.7, 0.8, 0.9))

    def sparkle(s, t, notes, v=0.45, dt=0.09):
        for j, m in enumerate(notes): add(s.mus, t + j * dt, bell(m, v), pan=(j - len(notes) / 2) / 4)

    def ending(s, t, chords=None):
        tend = s.T - 0.3; chords = chords or [F, G_]
        prog(t, tend - 2.2, chords, lambda a, b_, c: chord_strings(a, b_, [c[0] - 12] + c + [c[-1] + 12], 0.7, 0.5, 1.0, 1.2))
        chord_strings(tend - 2.2, tend, [36, 48, 55, 60, 64, 67, 72], 0.85, 0.2, 1.6, 1.1)
        for m in [60, 64, 67, 72, 76]: add(s.mus, tend - 2.2, piano(m, 0.65, 4))
        add(s.mus, tend - 2.2, timpani(36, 0.8))

    def finish(s, here, n=None):
        import os
        n = len(s.S) if n is None else n
        voice = load_voice([os.path.join(here, f'narration/s{i}.opus') for i in range(1, n + 1)], s.S, s.mus.shape[1])
        finish(s.mus, s.sfx, voice, os.path.join(here, 'mix.wav')); print('mix.wav ok', s.T)
