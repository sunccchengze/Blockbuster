# PINN（物理信息神经网络）· 60 秒讲解动画
沿用同一管线（voice-01 配音、确定性渲染、电钢琴配乐 + 侧链闪避）。

**画面里的训练曲线是真实训练结果**：`train.py` 用 PyTorch 训练（全连接 1→32→32→32→1，tanh，Adam lr=1e-3），
例子为阻尼振子 u″ + μu′ + ku = 0（μ=4, k=400, u(0)=1, u′(0)=0），只给 t∈[0,0.36] 的 10 个观测点，40 个配点，λ=1e-4。
快照保存在 `train_data.json`，渲染只读 JSON，重建视频不需要 PyTorch。

| 模型 | 全区间 RMSE |
|---|---|
| 普通神经网络（仅数据，6000 步） | 0.57 |
| PINN（数据 + 残差，20000 步） | 0.004 |
| 反问题 PINN：μ 可训练 | μ 估计 4.20（真值 4） |

- 成片：`pinn_explained.mp4`（1280×720 · 24fps · 60.4s）
- 重建：`./build.sh`；重新训练：`python3 train.py`（约 1.5 分钟，需 torch）

## 配乐（v2 重制）
- `score.py` — 分场景配乐：弦乐群/钢琴/定音鼓/鼓组/钟琴 + 与画面同步的音效，混响 + 人声闪避（引擎：`~/scorelib.py`）
- 替换音轨：`python3 score.py && bash ~/remux.sh <视频>.mp4 mix.wav`（画面不重渲染，响度对齐 −14 LUFS）
- 旧的 music.js 已删除；build.sh 中的配乐步骤已被 score.py 取代
