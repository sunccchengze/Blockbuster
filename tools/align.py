"""旁白逐字对齐：用 faster-whisper 求每个字的时间，映射回原稿，输出每句字幕的起止时间。

用法（Python）：
    from tools.align import align
    times, dur = align("narration/s1.flac", ["第一句", "第二句", ...])   # → [(start, end), ...]
句子必须是旁白原稿按顺序切出的片段（标点可省略）；返回 (句子时间列表, 音频时长)，单位为秒，相对音频开头。

依赖：pip install faster-whisper（首次运行会下载模型到 ~/.cache，用完可删）。
注意：直接传文件路径给 faster-whisper 会在部分环境触发 av.open TypeError，所以这里先用 ffmpeg 解码成 16 kHz numpy 数组。
"""
import re, subprocess, difflib, functools, sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bb.media import ffmpeg

KEEP = re.compile(r'[\u4e00-\u9fffA-Za-z0-9]')
CN_NUM = str.maketrans('', '')


def _norm(s):
    return [c.lower() for c in s if KEEP.match(c)]


@functools.lru_cache(1)
def _model(name='small'):
    from faster_whisper import WhisperModel
    return WhisperModel(name, device='cpu', compute_type='int8')


def load16k(path):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def char_times(path, script, model='small'):
    """返回原稿每个有效字符的 (start, end)；识别不到的字符用相邻字符插值。"""
    audio = load16k(path)
    segs, _ = _model(model).transcribe(audio, language='zh', word_timestamps=True,
                                       initial_prompt="以下是普通话的句子。", vad_filter=False, beam_size=5)
    rec, rt = [], []
    for s in segs:
        for w in s.words:
            cs = _norm(w.word)
            if not cs: continue
            d = (w.end - w.start) / len(cs)
            for j, c in enumerate(cs): rec.append(c); rt.append((w.start + j * d, w.start + (j + 1) * d))
    ref = _norm(script)
    out = [None] * len(ref)
    sm = difflib.SequenceMatcher(None, ref, rec, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1): out[i1 + k] = rt[j1 + k]
        elif tag == 'replace' and j2 > j1:            # 数字读法等不一致：按比例摊时间
            a, b = rt[j1][0], rt[j2 - 1][1]
            for k in range(i2 - i1): out[i1 + k] = (a + (b - a) * k / (i2 - i1), a + (b - a) * (k + 1) / (i2 - i1))
    # 插值补洞
    known = [i for i, v in enumerate(out) if v]
    dur = len(audio) / 16000
    for i, v in enumerate(out):
        if v: continue
        L = max([k for k in known if k < i], default=None); R = min([k for k in known if k > i], default=None)
        a = out[L][1] if L is not None else 0.0; b = out[R][0] if R is not None else dur
        nL = i - (L if L is not None else -1); nT = (R if R is not None else len(out)) - (L if L is not None else -1)
        t = a + (b - a) * nL / nT; out[i] = (t, t)
    return ref, out, dur


def align(path, sentences, model='small'):
    script = ''.join(sentences)
    ref, ct, dur = char_times(path, script, model)
    res, p = [], 0
    for s in sentences:
        n = len(_norm(s))
        if n == 0: res.append((ct[p][0] if p < len(ct) else dur,) * 2); continue
        res.append((round(ct[p][0], 2), round(ct[p + n - 1][1], 2))); p += n
    return res, dur


if __name__ == '__main__':
    import json
    path, *sents = sys.argv[1:]
    print(json.dumps(align(path, sents), ensure_ascii=False))
