# 浓差电池与能斯特方程 · 约 62 秒 3D 教学动画

每一帧由 `scene.js` 的 `render(ctx, t)` 求值，带种子 PRNG，内存 RGBA 直推 ffmpeg。这不是仓库里已废弃的模板流水线。

## 成片

- `concentration_cell_nernst.mp4`：1280×720 · 24 fps · 约 62 s，成片与源码一同保存在本目录并入库。
- 写实实验室场景，面向大学物理化学。电压表与公式中的 0.059 V 明确标注为“理想溶液理论值（动画模拟，非实测）”；不把它说成真实开路电压，也不引用未经核实的 CuSO₄ 活度系数。重制后响度检测为 −14.2 LUFS，峰值 −1.7 dBFS。
- 新版更正片尾结论：“浓度比决定电压；浓度差关联可释放的电量。”旁白 s1–s4 保留原男声；修订的 s5–s6 使用用户第一次试听选择的音色。

## 内容分镜（时间码来自实测旁白时长）

| 时间 | 段落 | 画面 |
|---|---|---|
| 0.8–9.2 s | 引入 | 两只烧杯（0.01 / 1 mol/L CuSO₄）、铜电极、盐桥；电压表读数作为理想溶液理论模拟值展示，不是实验测量 |
| 9.6–21.1 s | 电极反应 | 推近稀侧：Cu → Cu²⁺ + 2e⁻（负极/氧化）；推近浓侧：Cu²⁺ + 2e⁻ → Cu（正极/还原），电极镀铜 |
| 21.5–32.9 s | 电路与盐桥 | 电子经外电路稀→浓；NO₃⁻ 向稀侧、K⁺ 向浓侧；总反应 Cu²⁺(浓) → Cu²⁺(稀) |
| 33.3–42.9 s | 能斯特方程 | E = E° − (RT/nF) ln Q → 25 ℃ 换算为 (0.0592 V/n) lg Q → E° = 0, n = 2 → E = (0.0592/2) lg(c浓/c稀) |
| 43.3–50.3 s | 代入 | 浓度比一百比一；0.0296 V × lg(1/0.01) ≈ 0.059 V，标明这是理想溶液近似的动画理论值，非实测 |
| 50.7–61.9 s | 放电至平衡 | 理想模型中浓度比趋近一、E–t 曲线下降至零；片尾更正为“浓度比决定电压；浓度差关联可释放的电量” |

## 文件

| 文件 | 作用 |
|---|---|
| `scene.js` | 3D 场景。`node scene.js still 12 47` 导出静帧 |
| `score.py` | 分场景配乐和音效，混入 `narration/*.flac`，写出 `mix.wav` |
| `narration/s1.flac`–`s6.flac` | 旁白 |
| `build.sh` | 混音 → 渲染封装 → `python3 -m bb remux` 对齐 −14 LUFS |
| `LESSONS.md` | 制作时的经验。开头说明了哪些路径已经过时 |

`music.js` 已删除。不要再跑它。

## 重建

在仓库根目录安装好 Python 依赖和 `npm install` 之后：

```bash
bash examples/concentration_cell/build.sh
```

只换音轨：

```bash
python3 examples/concentration_cell/score.py
python3 -m bb remux 成片.mp4 examples/concentration_cell/mix.wav
```
