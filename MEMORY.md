# BLOCKBUSTER SYSTEM MEMORY (核心工作记忆)

> **最高纲领**：未来一切工作必须做到极致。模型产出的是程序，不是视频。全领域覆盖，样样精通。

---

## 1. 核心定位与设计哲学

1. **非视频生成模型，而是现场写出确定性渲染器的 Agent 导演中枢**：
   - 每一帧画面由纯函数 $f(t)$ 求值决定，严禁对物理时钟（`Date.now()`、`rAF`）产生隐式依赖。
   - 随机性必须采用带种子的伪随机数生成器（Seeded PRNG，如 Mulberry32），保证跨平台比特级绝对可复现。
2. **可持续的通用视频生成流水线 (Universal Pipeline)**：
   - 彻底破除“单一固定 Demo”局限。用户输入任意需求，流水线自主完成意图解析、分镜编剧、程序化视觉编译、定制物理声学合成与真实抽帧质检。
   - 涵盖商业科技（Tech UI）、电影三维（Cinematic 3D/PBR）、科学数据（Science/Data）、艺术写意（Organic Art）全领域。
3. **声画物理一体化**：
   - 配乐由纯离散数学物理建模（Karplus-Strong 扩展模型 + 动态音效 + 母带限制器）实时计算生成，严禁外挂劣质现成罐头音效。
   - 6 项 EBU R128 客观门禁自动化闭环检验。
4. **客观自动化门禁**：
   - 拒绝主观玄学。视频必须通过“编码后真实 MP4 抽帧接触单（Contact Sheet）”，音频必须通过“六项客观声学门禁 + 频谱瀑布图”。

---

## 2. 宿主与执行环境约束

1. **网络与依赖约束**：
   - 依赖全面基于自包含预编译包：
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
| 3. 动态范围 | Loudness Range (LRA) | $4.0 \sim 18.0\text{ LU}$ | 保证动态呼吸感与冲击力，杜绝过度挤压变成砖墙 |
| 4. 直流与瞬态 | DC Offset & Pop Check | 直流 $< -60\text{ dBFS}$，首尾无爆破 | 消除声卡直流偏置，首尾样点零交叉过渡 |
| 5. 频谱分布 | Spectral Balance | 次低频截断，无异常谐振尖刺 | 消除 <20Hz 无效能耗，高频呈物理自然滚降 |
| 6. 声画同步 | Audio-Visual Sync Drift | $\le \pm 1\text{ 帧} (\approx 41.6\text{ms})$ | 叙事 Beat 与音频瞬态 Transient 毫秒级锁定 |

---

## 4. 通用需求驱动流水线架构 (Universal Prompt-to-Video Pipeline)

1. **五阶段闭环架构**：
   - `src/pipeline/director.js`：接收任意自然语言 Prompt，自动识别流派与生成 6 阶段动态分镜清单；
   - `src/pipeline/scene_generator.js`：根据分镜动态编译纯函数渲染逻辑 $f(t)$；
   - `src/pipeline/audio_generator.js`：定制离散物理弦乐与电影级冲击音效，确保 6 项客观门禁全部通过；
   - `src/pipeline/orchestrator.js`：编排全链路，输出 1920×1200 真实抽帧接触单与全量 manifest；
   - `scripts/generate.js`：命令行一键调用，输出到 `output/` 目录。
2. **操作接口**：
   - CLI 命令行：`npm run generate -- --prompt "..."`；
   - 编程式 API：`runBlockbusterPipeline(prompt)`。
