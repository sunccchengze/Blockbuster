# 浓差电池与能斯特方程 · 60 秒 3D 教学动画

按 [Blockbuster](https://github.com/sunccchengze/Blockbuster/tree/arena%2F01a0f07e-blockbuster) 的“代码驱动、确定性渲染”协议制作：每一帧由纯函数 `render(ctx, t)` 求值，带种子 PRNG，内存 RGBA 帧直推 FFmpeg，不落盘中间图片。

## 成片
- `concentration_cell_nernst.mp4` — 1280×720 · 24 fps · 60.4 s · H.264 + AAC 立体声
- 中文普通话配音 + 中文字幕，写实实验室风格，面向大学物理化学水平
- 音频：积分响度约 −14.4 LUFS，真峰值 −1.7 dBTP

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
| `scene.js` | 3D 场景渲染器（自写透视投影、玻璃/液体/电极/粒子/公式面板/字幕），`node scene.js still 12 47` 可导出指定时刻静帧 |
| `music.js` | 确定性配乐合成：电钢琴分解和弦（Cmaj7–Am7–Fmaj7–G6，84 BPM）+ 轻弦乐垫 + 换场铃声 + 混响 |
| `narration/s1–s6.wav` | 已裁静音并 1.19× 变速的旁白分段 |
| `build.sh` | 一键重建：配乐 → 旁白混音（侧链闪避）→ 渲染封装 → 接触单 |
| `LESSONS.md` | 本次制作经验总结 |
| `HANDOFF.md` | 交接清单 |

## 重建
```bash
# 需要同级目录下有 Blockbuster 仓库（提供 @napi-rs/canvas 与 ffmpeg 静态二进制）
./build.sh      # 约 2.5 分钟
```

## 配乐（v2 重制）
- `score.py` — 分场景配乐：弦乐群/钢琴/定音鼓/鼓组/钟琴 + 与画面同步的音效，混响 + 人声闪避（引擎：`~/scorelib.py`）
- 替换音轨：`python3 score.py && bash ~/remux.sh <视频>.mp4 mix.wav`（画面不重渲染，响度对齐 −14 LUFS）
- 旧的 music.js 已删除；build.sh 中的配乐步骤已被 score.py 取代
