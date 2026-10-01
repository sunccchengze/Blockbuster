# 波尔共振实验 · 60 秒 3D 教学动画

画面是 `scene.js`，配乐是 `score.py`。摆轮运动由 RK4 数值积分求解 θ'' + 2βθ' + ω₀²θ = ω₀²θd(t)（T₀ = 1.6 s）。画面、曲线、读数来自同一组仿真数据。

- 成片：`bohr_resonance.mp4`（1280×720 · 24fps · 60.4s）。不在 git 里。Release 标签 [`films-2026-09-30`](https://github.com/sunccchengze/Blockbuster/releases/tag/films-2026-09-30) 已建，但附件还没传上去；原片在历史提交 `08b26af` 的 `.zip` 里。交付时记录约 −14.6 LUFS / −1.7 dBTP。这次整理没有重渲，也没有试听。
- 旁白：`narration/s1.flac`–`s6.flac`（voice-01）
- 重建：`bash examples/bohr_resonance/build.sh`

| 时间 | 内容 |
|---|---|
| 0.8–9.4 | 仪器结构：摆轮、蜗卷弹簧、电磁阻尼线圈、电机+相位盘、摇杆连杆、角度盘 |
| 9.8–21.4 | 阻尼振动：扭转 120° 释放；小阻尼 / 大阻尼 θ(t) 与指数包络对比 |
| 21.8–31.4 | 受迫振动：ω = 0.8ω₀，过渡后稳态，振幅约 31° |
| 31.8–41.4 | 共振：ω → ω₀，振幅增至约 90°+，闪光灯定格，相位差 90° |
| 41.8–50.1 | 运动方程 Jθ̈ + bθ̇ + kθ = M₀cosωt，稳态振幅与 tanφ |
| 50.5–58.9 | 三种阻尼的幅频、相频曲线 |

只换音轨：`python3 examples/bohr_resonance/score.py`，再 `python3 -m bb remux`。不要调用已删除的 `music.js`。
