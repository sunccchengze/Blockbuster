# BLOCKBUSTER DIRECTOR SKILL SPECIFICATION (v3.1)

> **核心法则**：这里没有一段像素是“生成”出来的。模型产出的是**程序**，不是视频。
> 全领域覆盖，样样精通，做到极致。

---

## 概述与定位

`blockbuster` 是专为 Coding Agent（如 Claude Code、Codex）设计的**全领域电影级代码渲染视频导演协议**。
它将视频制作彻底软件工程化：输入一句话或商业需求，Agent 通过严谨的导演问询与协议标准，现场写出确定性数学场景代码、现场合成声学/物理配乐、通过内存管道驱动 FFmpeg 压制，并通过双模客观门禁完成交付。

---

## 全领域支持矩阵 (All-Domain Engines)

| 领域分类 | 典型应用场景 | 推荐图形技术栈 | 动画与动力学策略 | 声效与配乐策略 |
|---|---|---|---|---|
| **Domain A: 商业科技排版** | 产品发布、SaaS 演示、概念宣发 | HTML5 Canvas / SVG 矢量 / 瑞士排版 | 欠阻尼物理弹簧（Spring Dynamics）、微观位移 | 现代科技低音 (Sub Drop) + UI Click + 扫频 Whoosh |
| **Domain B: 电影三维视效** | 赛博空间、穿梭漫游、机械装配 | Three.js Math / PBR / 着色器 | 样条平滑摄像机轨道、多光源反射、Bloom 辉光 | 电影级撞击 (Cinematic Hit) + Riser 紧张张力 |
| **Domain C: 科学数据可视** | 算法推演、金融数据、拓扑几何 | 参数化数学函数、SDF 距离场 | 连续拓扑变形、动态折线增长、自适应计数器 | 极简脉冲晶体音 (Bip/Click) + 纯净微弦振 |
| **Domain D: 艺术有机质感** | 东方水墨、水彩晕染、手绘定格 | 分形噪声 / 自定义 Shader / 纤维滤镜 | 180° 快门曝光超采样、定格颤线（Line Boil） | 扩展 Karplus-Strong 物理建模弦乐（古琴/琵琶滑音） |
| **Domain E: 音乐节拍叙事** | 节奏混剪、MV 叙事、高燃卡点 | 混合图层 / 快速蒙太奇 / 动态遮罩 | 毫秒级重音强切、张力起伏节奏 | 声画共享统一时间戳清单，重音绝对锁定 |

---

## 七阶段工业导演协议 (The 7-Stage Protocol)

### Phase 1: 需求意图与领域澄清 (Director Interview)
当用户提出视频制作需求时，Agent **必须首先通过问询树确认 5 项核心诉求**，禁止盲目开始写代码：
1. **领域与类型**：确立属于 Domain A~E 中的哪一种或混合流派；
2. **画幅与分辨率**：默认 16:9 (1280×720 或 1920×1080) / 竖屏 9:16 (1080×1920) / 宽银幕 2.35:1；
3. **时长与节奏**：严格锁定总秒数 $T$（如 10.0s）与帧率（电影级 24fps 或丝滑 60fps）；
4. **视觉影调与基调色**：主色调、对比度、光影氛围与材质风格；
5. **声效架构**：是物理真实乐器、现代合成器电子还是极简音效点缀。

### Phase 2: 视听统一步骤分镜清单 (BeatSheet Manifest)
在编写渲染代码前，必须先输出格式化的 JSON / Markdown 分镜表，将视觉动作与音频事件严格绑定：
```json
[
  {
    "beat": 1,
    "name": "起势",
    "start": 0.0,
    "end": 1.2,
    "visual": "宣纸微暖光晕，孤墨自天际垂直坠落",
    "camera": "固定俯仰中景",
    "audio": { "type": "harmonic", "freq": 587.33, "velocity": 0.88, "event": "D5 泛音" }
  },
  {
    "beat": 2,
    "name": "破墨",
    "start": 1.2,
    "end": 2.4,
    "visual": "墨滴触纸，焦墨核心炸裂，分形水晕向外渗透",
    "camera": "微观贴地推进",
    "audio": { "type": "strike_slide", "freq": 293.66, "target": 146.83, "event": "原音下潜滑音" }
  }
]
```

### Phase 3: 确定性场景纯函数实现 (Deterministic Implementation)
* **绝对纯函数约束**：场景必须暴露统一接口 `render(ctx, t, frameIndex, subIndex, subCount, width, height)`。
* **时钟铁律**：严禁调用 `Date.now()`、`performance.now()`、`Math.random()` 或 CSS/WAAPI 异步动画！
* **伪随机数**：一律使用种子 PRNG（如 `createPRNG(seed)` Mulberry32 算法），保证跨平台比特级绝对一致。
* **动力学**：拒绝死板的线性过渡，运动采用带有质量与阻尼的二阶真实物理弹簧（Spring Dynamics）或三次贝塞尔缓动。

### Phase 4: 180° 自适应快门时间积分 (Motion Blur Accumulator)
* 电影感的核心在于快门曝光时间积分。
* 电影标准 180° 快门意味着曝光时间窗口为 $\tau = \frac{1}{2 \times \text{fps}}$（24fps 下为 $\frac{1}{48}\text{s}$）。
* 渲染引擎必须在 $[t, t + \tau]$ 窗口内以高斯/帐篷加权核采样多子步（Subframes $\ge 4$）并累加混合，从光学物理本质上消除频闪和锯齿。

### Phase 5: 物理建模配乐与程序化音效 (Procedural Sound Design)
* 彻底摈弃塑料电子音与外部未知素材，全由代码实时计算生成。
* **物理弦乐**：采用扩展 Karplus-Strong 算法，支持指甲/指肉激励脉冲、分数延时微调、弦内频响损耗衰减、泛音节点激振与平滑滑音（吟猱绰注）。
* **母带处理链**：DC 偏置高通滤除（<18Hz） + 软压限软饱和（Soft Clipper） + 统一增益对准 -14.0 LUFS。
* 导出为 48,000Hz、16-bit / 24-bit 无损 WAV 音轨。

### Phase 6: 内存管道直推流式编码 (Zero-Disk Stream Encoding)
* 严禁将成百上千帧落盘为临时小 PNG 图片！
* 采用 Skia Canvas 内存 RGBA 缓冲区，通过 Node.js IPC Stream 直接推入 FFmpeg 标准输入：
  ```bash
  ffmpeg -y -f rawvideo -pix_fmt rgba -s 1280x720 -r 24 -i - -i audio.wav -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -c:a aac -b:a 256k output.mp4
  ```

### Phase 7: 双模客观自动化质检门禁 (Dual-Modal QC Gates)
交付前必须运行双模自动化质检，未全部达标者严禁交付：
1. **画面门禁（Contact Sheet）**：必须从**最终编码生成的 MP4 文件中**精准抽取各叙事 Beat 的物理帧，拼贴为 9 宫格印相单，验证色度抽样与节拍无损。
2. **音频门禁（6 项客观声学指标）**：
   * **Gate 1: 积分响度 (Integrated LUFS)**：必须处于 $-14.0 \pm 1.0\text{ LUFS}$；
   * **Gate 2: 真实峰值 (True Peak)**：必须 $\le -1.0\text{ dBTP}$，留足重采样净空；
   * **Gate 3: 动态范围 (LRA)**：Short-term 动态范围处于 $4.0 \sim 18.0\text{ LU}$；
   * **Gate 4: 直流与削波 (DC Offset)**：直流偏置 $< -60\text{ dBFS}$，首尾无爆破；
   * **Gate 5: 频谱分布 (Spectral Balance)**：次低频受控，高频呈物理自然滚降；
   * **Gate 6: 声画同步 (Sync Drift)**：视觉 Beat 与音频 Transient 偏移 $\le \pm 41.6\text{ ms}$（$\pm 1$ 帧）。
   * 输出声学频谱瀑布图（`score-spectrogram.png`）作为质检凭证。
