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

## 4. 七阶段工业化生产全流程 (The 7-Stage Production Protocol)

1. **Stage 1: 题材意图解构与类型学标定**  
   根据需求快速判定流派分类（Tech UI / Cinematic 3D / Science Data / Stylized / Music MV），设定总时长、纵横比、目标帧率与色彩空间。
2. **Stage 2: 宏观情绪弧与时间码节拍单 (Narrative Manifest)**  
   严谨划分起承转合结构，输出包含起始时间、动作焦点、声学瞬态预设的原子节拍清单。
3. **Stage 3: 确定性离散数学与物理建模**  
   选用 Mulberry32 伪随机种子、二阶阻尼弹簧动力学与连续 Bézier 缓动曲线，杜绝物理时钟隐式依赖。
4. **Stage 4: 极速线框/占位预览 (V1 Quick Wireframe)**  
   以 60+ fps 极速渲染低开销几何体与时间码标记，验证镜头运镜与节奏张力。
5. **Stage 5: 物理真实感与微观 Shader 渲染 (V2 & V3 Master)**  
   加入 PBR 金属微表面、双向反射、180° 快门（4x 子样多重曝光）、宣纸纤维噪声与毛细渗透算法。
6. **Stage 6: 纯代码合成物理建模音轨 (v3.1 Procedural Score)**  
   Karplus-Strong 离散物理琴弦仿真、木质琴箱共鸣腔、金石碰撞声，严格通过 6 项客观门禁并输出声学瀑布图。
7. **Stage 7: 双轨质检与最终交付闭环**  
   从最终封装完毕的 MP4 中真实抽帧合成 1920×1200 九宫格接触单，并交付生产级全功能演播厅前端。

---

## 5. Web UI 与设计系统 (Apple Design System Integration)

- **设计系统规范**：严格遵循 `VoltAgent/awesome-design-md/design-md/apple` (DESIGN.md)
  - **核心准则**：摄影优先、UI 镀铬隐退（Receding Chrome）、无花哨渐变；
  - **色彩基准**：
    - 主强调色：`#0066cc` (Action Blue)，悬停态 `#0071e3`；
    - 深色表面文本链接：`#2997ff` (Sky Link Blue)；
    - 浅色底正文文本：`#1d1d1f` (Near-Black Ink，绝不使用死黑 `#000000`)；
    - 浅灰交替底色：`#f5f5f7` (Parchment)；
    - 展台瓷面底色：`#272729` (Tile 1) / `#2a2a2c` (Tile 2) / `#000000` (Cinema Stage)；
    - 全系统杜绝引入第二种强调色。
  - **排印系统**：
    - 主标题：56px / 600 / -0.28px；
    - 二级标题：40px / 600 / 0px；
    - 正文：17px / 400 / -0.374px（行高 1.47）；
    - 严格避免使用 500 字重，全站仅在 400 与 600 间建立鲜明对比；
    - 目录链接：14px / 400 / 行高 2.41。
  - **按钮语法**：
    - 胶囊药丸：`border-radius: 9999px`，内边距 `11px 22px`；
    - 点按反馈：`transform: scale(0.95)` 真实物理微缩；
    - 次级按钮：1px Action Blue 边框的 Ghost Pill。
  - **单阴影绝对约束**：
    - 全站唯一合法的投影仅赋予沉浸式黑展台上的产品屏幕：`rgba(0, 0, 0, 0.22) 3px 5px 30px 0`；
    - 卡片、按钮、正文一律零 drop-shadow，以 1px hairline border 或底色对比界定空间。

---

## 6. 通用需求驱动流水线架构 (Universal Prompt-to-Video Pipeline)

1. **可持续流水线核心原则**：
   - 彻底破除“单片执念”：不仅是单一水墨 Demo，而是任意需求输入即可自主完成制作的可复用工业流水线；
   - 模块化架构：
     - `src/pipeline/director.js`：自然语言意图解构与类型学判定，生成 6 阶段动态分镜清单；
     - `src/pipeline/scene_generator.js`：根据分镜动态编译纯函数渲染逻辑 $f(t)$；
     - `src/pipeline/audio_generator.js`：定制离散物理弦乐与电影级冲击音效，确保 6 项客观门禁全部通过；
     - `src/pipeline/orchestrator.js`：编排全链路，输出 1920×1200 真实抽帧接触单与全量 manifest。
2. **多形态驱动接入**：
   - 命令行：`npm run generate -- --prompt "..."`；
   - Web 演播厅：`POST /api/pipeline/generate`，SSE 实时日志推流与动态回放；
   - 编程式 API：`runBlockbusterPipeline(prompt)`。

