# 大数定律 · 60 秒 3D 教学动画

画面是 `scene.js`，配乐是 `score.py`。制作经验见 `../concentration_cell/LESSONS.md`（其中的旧路径已过时）。

- 成片：`law_of_large_numbers.mp4`（1280×720 · 24fps · 60.4s）。不在 Git 里，也不上传 Release。历史成片恢复线索见 [整理记录](../../docs/IMPORT.md)，本次未核验远端历史。交付时记录约 −14.3 LUFS / −1.8 dBTP。这次整理没有重渲，也没有试听。
- 旁白：`narration/s1.flac`–`s6.flac`（voice-01）
- 重建：`bash examples/law_of_large_numbers/build.sh`

| 时间 | 内容 |
|---|---|
| 0.8–10.1 | 3D 抛硬币 10 次，7 正：P=1/2 但 7/10≠1/2？ |
| 10.5–18.6 | 频率随 n（对数轴 1→10000）的轨迹逐渐稳定到 0.5 |
| 19.0–33.1 | 40 条轨迹收敛成漏斗、ε 带；弱大数定律公式；扫描线统计带外轨迹数 |
| 33.5–42.6 | 切比雪夫上界 σ²/(nε²) 与 400 次实验实测概率对比 |
| 43.0–47.7 | 3D 骰子 + 点数直方图，平均值→3.5 |
| 48.1–59.0 | 偏差被稀释而非补偿（2/n 表）；蒙特卡洛撒点估计 π；片尾公式 |

只换音轨：`python3 examples/law_of_large_numbers/score.py`，再 `python3 -m bb remux`。不要调用已删除的 `music.js`。
