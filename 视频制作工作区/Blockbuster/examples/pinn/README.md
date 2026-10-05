# PINN（物理信息神经网络）· 60 秒讲解动画

画面是 `scene.js`，配乐是 `score.py`。

画面里的训练曲线是真实训练结果。`train.py` 用 PyTorch 训练（全连接 1→32→32→32→1，tanh，Adam lr=1e-3）。例子是阻尼振子 u″ + μu′ + ku = 0（μ=4, k=400, u(0)=1, u′(0)=0），只给 t∈[0,0.36] 的 10 个观测点，40 个配点，λ=1e-4。快照在 `train_data.json`。渲染只读 JSON，重建视频不需要 PyTorch。

| 模型 | 全区间 RMSE |
|---|---|
| 普通神经网络（仅数据，6000 步） | 0.57 |
| PINN（数据 + 残差，20000 步） | 0.004 |
| 反问题 PINN：μ 可训练 | μ 估计 4.20（真值 4） |

- 成片：`pinn_explained.mp4`（1280×720 · 24fps · 60.4s）。不在 git 里。Release 标签 [`films-2026-09-30`](https://github.com/sunccchengze/Blockbuster/releases/tag/films-2026-09-30) 已建，但附件还没传上去；原片在历史提交 `08b26af` 的 `.zip` 里。这次整理没有重渲，也没有试听。
- 旁白：`narration/s1.flac`–`s6.flac`（voice-01）
- 重建：`bash examples/pinn/build.sh`
- 重新训练：`python3 train.py`（需要 torch，大约 1.5 分钟；这次整理没有重跑）

只换音轨：`python3 examples/pinn/score.py`，再 `python3 -m bb remux`。不要调用已删除的 `music.js`。
