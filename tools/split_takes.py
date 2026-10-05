"""把整段录音 take*.wav 按 script.py 的段落切成 narration/s1..sN.flac（变速 + 去首尾静音）。
用法：python3 tools/split_takes.py <片目录> [语速倍率=1.0]
script.py 需定义 SEGS 与 TAKES=[(段起, 段止), ...]，录音文件名为 take{段起}.wav。
"""
import sys, os, subprocess, importlib.util
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.align import align
from bb.media import ffmpeg
d = os.path.abspath(sys.argv[1]); tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
spec = importlib.util.spec_from_file_location('script', os.path.join(d, 'script.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
os.makedirs(os.path.join(d, 'narration'), exist_ok=True)
TRIM = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05'
for a, b in m.TAKES:
    src = os.path.join(d, f'take{a}.wav')
    sents, owner = [], []
    for k in range(a, b):
        for sp, _ in m.SEGS[k]: sents.append(sp); owner.append(k)
    t, dur = align(src, sents)
    for k in range(a, b):
        idx = [i for i, o in enumerate(owner) if o == k]
        s0 = 0.0 if k == a else (t[idx[0] - 1][1] + t[idx[0]][0]) / 2
        s1 = dur if k == b - 1 else (t[idx[-1]][1] + t[idx[-1] + 1][0]) / 2
        out = os.path.join(d, f'narration/s{k + 1}.flac')
        af = f'atempo={tempo},{TRIM},areverse,{TRIM},areverse,apad=pad_dur=0.12'
        subprocess.run([ffmpeg(), '-v', 'error', '-y', '-ss', f'{s0:.3f}', '-to', f'{s1:.3f}', '-i', src, '-af', af, '-ar', '44100', '-ac', '1', out], check=True)
        print(k + 1, round(s0, 2), round(s1, 2), flush=True)
