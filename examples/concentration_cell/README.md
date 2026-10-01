# 浓差电池与能斯特方程 · 60 秒 3D 教学动画

每一帧由 `scene.js` 的 `render(ctx, t)` 求值，带种子 PRNG，内存 RGBA 直推 ffmpeg。这不是仓库里已废弃的模板流水线。

## 成片

- `concentration_cell_nernst.mp4`：1280×720 · 24 fps · 60.4 s。不在 git 里。Release 标签 [`films-2026-09-30`](https://github.com/sunccchengze/Blockbuster/releases/tag/films-2026-09-30) 已建，但附件还没传上去；原片在历史提交 `08b26af` 的 `.zip` 里。
- 中文普通话配音（voice-01）+ 字幕，写实实验室，面向大学物理化学。
- 交付时测过的响度约 −14.4 LUFS，真峰值 −1.7 dBTP。这次整理没有重渲，也没有试听。

## 内容分镜（时间码来自实测旁白时长）

| 时间 | 段落 | 画面 |
|---|---|---|
| 0.8–9.2 s | 引入 | 两只烧杯（0.01 / 1 mol/L CuSO₄）、铜电极、盐桥、电压表 0.059 V；溶液颜色与 Cu²⁺ 数量随浓度 |
| 9.6–21.1 s | 电极反应 | 推近稀侧：Cu → Cu²⁺ + 2e⁻（负极/氧化）；推近浓侧：Cu²⁺ + 2e⁻ → Cu（正极/还原），电极镀铜 |
| 21.5–32.9 s | 电路与盐桥 | 电子经外电路稀→浓；NO₃⁻ 向稀侧、K⁺ 向浓侧；总反应 Cu²⁺(浓) → Cu²⁺(稀) |
| 33.3–42.9 s | 能斯特方程 | E = E° − (RT/nF) ln Q → 25 ℃ 换算为 (0.0592 V/n) lg Q → E° = 0, n = 2 → E = (0.0592/2) lg(c浓/c稀) |
| 43.3–48.9 s | 代入 | 0.0296 V × lg(1/0.01) ≈ 0.059 V，与电压表一致 |
| 49.3–60.4 s | 放电至平衡 | 浓度趋同、E–t 曲线实时绘制、电压→0；片尾“浓度差，就是驱动力” |

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
