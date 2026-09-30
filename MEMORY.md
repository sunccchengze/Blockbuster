# BLOCKBUSTER SYSTEM MEMORY (核心工作记忆)

> **最高纲领**：未来一切工作必须做到极致。模型产出的是程序，不是视频。全领域覆盖，样样精通。

---

## 1. 核心定位与设计哲学

1. **非视频生成模型，而是现场写出确定性渲染器的 Agent 导演中枢**：
   - 每一帧画面由纯函数 $f(t)$ 求值决定，严禁对物理时钟（`Date.now()`、`rAF`）产生隐式依赖。
   - 随机性必须采用带种子的伪随机数生成器（Seeded PRNG，如 Mulberry32），保证跨平台比特级绝对可复现。
2. **全领域覆盖，样样精通**：
   - 本项目绝不仅是水墨风。涵盖 **商业科技排版（Tech/UI）**、**电影级三维视效（Cinematic 3D/PBR）**、**科学数据可视化（Science/Data）**、**艺术风格化（Artistic Stylized）** 与 **音乐节拍叙事（Music MV）** 全领域。
   - 「墨」（水墨宣纸、180° 快门、微观纤维 Shader、物理拨弦）是整个体系的**极限压力测试基准（Stress Benchmark）**，用于淬炼出全域通用的导演协议。
3. **声画物理一体化**：
   - 配乐由纯离散数学物理建模（Karplus-Strong 扩展模型 + 动态音效 + 母带限制器）实时计算生成，严禁外挂塑料电子音。
   - 声画共享统一时间戳清单（Universal Timeline Manifest），毫秒级锁定重音对齐。
4. **客观自动化门禁**：
   - 拒绝主观玄学。视频必须通过“编码后真实 MP4 抽帧接触单（Contact Sheet）”，音频必须通过“六项客观声学门禁 + 频谱瀑布图”。

---

## 2. 宿主与执行环境约束

1. **网络与依赖约束**：
   - 宿主容器外网访问部分受限（Debian 官方源与部分 CDN 连接重置）。
   - 依赖全面基于 `registry.npmjs.org` 的自包含预编译包：
     - `@ffmpeg-installer/ffmpeg` + `@ffprobe-installer/ffprobe`（已安装至 `/usr/local/bin`）；
     - `@napi-rs/canvas`（基于 Google Skia 引擎，C++ 极速 2D/路径/字体/着色像素操作）；
     - `three`（三维数学、矩阵几何与投影算法）。
2. **渲染推流架构**：
   - 严禁产生大量临时图片文件落盘！
   - 一律采用 **Memory IPC Buffer Stream 直推 FFmpeg stdin**（`ffmpeg -f rawvideo -pix_fmt rgba -s WxH -r FPS -i - -c:v libx264 -pix_fmt yuv420p -crf 18`）。
3. **版本控制约束**：
   - 固定工作分支：`arena/01a0f07e-blockbuster`。
   - 任何 push 操作必须严格推送到 `origin arena/01a0f07e-blockbuster`。
   - **每一次 push 后必须自动更新 `HANDOFF.md`！**

---

## 3. 六项客观音频门禁标准 (The 6 Objective Audio Gates)

| 门禁项 | 英文标识 | 判定阈值 | 意义与物理成因 |
|---|---|---|---|
| 1. 积分响度 | Integrated Loudness | $-14.0 \pm 1.0\text{ LUFS}$ | 符合 YouTube / 国际流媒体工业交付母带响度，不爆头、不过虚 |
| 2. 真实峰值 | True Peak | $\le -1.0\text{ dBTP}$ | 留足采样间插值净空（Headroom），消除解码重采样失真 |
| 3. 动态范围 | Loudness Range (LRA) | $8.0 \sim 18.0\text{ LU}$ | 保证动态呼吸感与冲击力，杜绝过度挤压变成砖墙 |
| 4. 直流与瞬态 | DC Offset & Pop Check | 直流 $< -60\text{ dBFS}$，首尾无爆破 | 消除声卡直流偏置，首尾样点零交叉过渡 |
| 5. 频谱分布 | Spectral Balance | 次低频截断，无异常谐振尖刺 | 消除 <20Hz 无效能耗，高频呈物理自然滚降 |
| 6. 声画同步 | Audio-Visual Sync Drift | $\le \pm 1\text{ 帧} (\approx 41.6\text{ms})$ | 叙事 Beat 与音频瞬态 Transient 毫秒级锁定 |

---

## 4. 七阶段导演协议 (The 7-Stage Director Protocol)

1. **Phase 1: 需求意图与领域澄清 (Clarification)**：自动识别领域（Tech / 3D / Science / Artistic / MV），问清情绪色调、节奏与交付规格。
2. **Phase 2: 视听统一步骤分镜 (BeatSheet Manifest)**：定义带有时间戳、视觉描述、运镜曲线与音频事件的共享清单。
3. **Phase 3: 确定性场景纯函数实现 (Deterministic Implementation)**：编写 `seek(t)`，实现图层、着色器与动力学。
4. **Phase 4: 180° 自适应快门时间积分 (Motion Blur Accumulator)**：以 $\tau = \frac{1}{2 \times \text{fps}}$ 进行子帧加权混合。
5. **Phase 5: 物理建模配乐与音效合成 (Procedural Sound Design)**：离散数学直接生成 24-bit/48kHz WAV 并通过母带压限。
6. **Phase 6: 流式推流与实时编码 (Stream Encoding Pipeline)**：内存 Pipe 零中间文件直接压缩生成 MP4。
7. **Phase 7: 双模客观自动化质检 (Dual-Modal QC Gates)**：从编码后的 MP4 抽帧生成 Contact Sheet，并进行 6 项音频门禁检测。
