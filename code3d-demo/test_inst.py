import sys, wave
import numpy as np
sys.path.insert(0, 'skills/blockbuster/scripts')
import guqin as G
SR=G.SR
parts=[]
def add(s, gap=0.25):
    parts.append(s); parts.append(np.zeros(int(gap*SR)))
# 1 古琴：绰（上滑）+ 吟
add(G.note(220.0, 2.2, 'guqin', amp=0.5, slide_to=220.0*2**(-2/12), slide_start=0.10, slide_dur=0.30, vibrato=1, seed=11))
# 2 古琴：注（下滑）长音 + 猱
add(G.note(329.63, 2.4, 'guqin', amp=0.5, slide_to=329.63*2**(3/12), slide_start=0.06, slide_dur=0.26, vibrato=2, seed=12))
# 3 古筝：甲拨单音
add(G.note(392.0, 1.8, 'guzheng', amp=0.5, seed=13))
# 4 古筝：刮奏
add(G.guozhi(523.25, 1046.5, 9, 1.4, 'guzheng', 0.4, seed=14), 0.4)
# 5 琵琶
add(G.note(440.0, 1.4, 'pipa', amp=0.45, seed=15))
x=np.concatenate(parts)
x=x/np.max(np.abs(x))*0.9
pcm=(x*32767).astype('<i2')
with wave.open('out/inst-test.wav','wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote out/inst-test.wav', len(x)/SR, 's')
