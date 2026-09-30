# code3d — 用「写代码」的方式做一条 3D 视频

一条 12 秒的自我说明片：内容就是它自己的生成方式。
**没有任何视频/图像生成模型参与**——模型写渲染代码，浏览器逐帧截图，ffmpeg 编码。
这正是 2026-09 那波 "Claude Opus 5.5 自制视频" 的底层逻辑，这里把它完整跑通并实测。

成片：[`video/code3d-v2.mp4`](video/code3d-v2.mp4)（精修版）· 12.00s · 1280×720 · 30fps · H.264 + AAC
对照：[`video/code3d-v1.mp4`](video/code3d-v1.mp4)（初版，无后期链）· `video/code3d-final.mp4` = v2 的副本

---

## V2 精修版：自己写的一条后期链

V1 是"raw 渲染"，V2 补上了 raw 和"交付级"之间的那道差距。**不引入 three/examples 的任何后处理模块**，
全部手写 shader，五个 pass：

```
scene → rtScene (HalfFloat, MSAA×4, 线性 HDR)
      → bright pass (阈值 1.6, 半分辨率)
      → blur H/V ×2 (四分之一分辨率 ping-pong)   = 泛光
      → composite: 泛光叠加 → 曝光 → ACES → 分离色调 → S 曲线
                   → 径向色差 → 暗角 → sRGB → 按帧播种的胶片颗粒
```

关键决定：
- **色调映射移到后期**。`renderer.toneMapping = NoToneMapping`，场景以线性 HDR 进 RT，
  ACES 在 composite 里做——这样泛光作用在 HDR 值上，高光才" bloomy "而不是糊。
- **颗粒按帧播种**（`hash(gl_FragCoord.xy + uFrame*137)`），保持确定性契约不被破坏。
- 色差/暗角/颗粒只作用在 3D 层，HUD 保持锐利——反而是优点。

### 调参教训（泛光是最容易毁掉一片子的东西）

第一版 v2 直接过曝：加性元素（辉光 sprite、加性轨道环、尘埃点、网格）全被泛光放大，
深黑底被洗成奶蓝雾，金属反而发黑。收敛顺序：

1. 泛光阈值 1.0 → **1.6**（只让真高光 bloom），强度 0.62 → **0.12**
2. 所有加性元素 opacity 砍半再砍半（辉光 0.34→0.16，加性环 0.55→0.28，尘埃 0.85→0.45）
3. 金属 roughness 0.14 → **0.20**、envMapIntensity 1.7 → **2.2**：更宽的反射才能让镀铬"读到"环境
4. 环境贴图加**软箱长条**：金属上的长高光是"摄影棚感"的来源
5. 爆点闪白 0.30 → **0.08**、衰减 σ 0.012 → **0.0035**：闪要"脆"（1–2 帧），不要"糊"（一层灰纱）

V2 还加了：kicker 小标 + 标题下划线从左往右画的动效、三条轨道环、加性尘埃、地面光池（接触感）、
相机轻微 roll。

### V2 成本

单帧 0.79s（V1 是 0.55s），360 帧 **284s**。后期五个 pass 在软件渲染下只加了 ~0.24s/帧——
**精修的边际成本很低**，这和普通"渲染越精越贵"的直觉不同，因为后期都在低分辨率 target 上跑。

---

## 四段式流水线（对照 PDoomVideo / LaunchVideo 那套）

| 阶段 | 本仓库对应 | 产物 |
|---|---|---|
| **Plan** | [`STORYBOARD.md`](STORYBOARD.md) | 分镜、配色、运镜映射、验收清单 |
| **Build** | [`scene.html`](scene.html) | three.js r186 场景，核心是一个 `renderAt(t)` 纯函数 |
| **Render** | [`render.mjs`](render.mjs) | 无头 Chromium 逐帧 `seek(t)` → 截图 → pipe 给 ffmpeg |
| **Join** | ffmpeg | 帧序列 + [`audio.py`](audio.py) 合成的音轨 → MP4 |

## 确定性契约（这条路线能成立的唯一原因）

渲染**不是实时的**：第 400 帧可能在第 399 帧几秒后才截。所以画面里任何东西都不能依赖真实时钟。
`scene.html` 暴露的契约：

```js
window.DURATION = 12;          // 秒
await window.seek(t);          // 把场景摆到 t，渲染一帧；每个像素都只是 t 的函数
```

被禁用的：`Date.now()`、`performance.now()`、`requestAnimationFrame` 循环、CSS transition、`setTimeout`、未播种的 `Math.random()`。
粒子位置用 `mulberry32(20260922)` 播种；手持漂移用固定频率正弦叠加（确定，但画面不死板）。

## 一个时钟：音画同源

[`audio.py`](audio.py) 用 numpy 加法合成整条音轨（底鼓/踩镲/sub/pad/琶音/riser/impact，和声 Am→F→C→G），**不依赖任何音乐模型**。
120 BPM → beat = 0.5s。画面的闪白用 `beat = t % 0.5` 同一个公式算。
所以音画同步不是后期对齐出来的，是**同源生成**的。

## 实测成本（这台机器：2 核 CPU / 2GB / 无 GPU）

| 项目 | 实测 |
|---|---|
| 环境搭建 | `apt` 系统库 + Chromium 114MB + `ffmpeg-static`（一次性） |
| WebGL | SwiftShader **软件渲染**（`/dev/dri` 不存在，无 GPU） |
| 单帧 | ~0.55s（1280×720，PBR 金属 + 1100 实例化粒子） |
| 360 帧渲染 | **197.8s** |
| 音轨合成 | ~2s |
| 编码 + 合流 | <1s |

对照文章里的说法：token 只覆盖"规划和写代码"，**帧的绘制跑在你自己机器上，成本是墙钟时间和电**。
这里 0 个 token 用在渲染上——和那批病毒视频的成本结构完全一致。

## 复现

```bash
npm i playwright ffmpeg-static three
npx playwright install chromium && npx playwright install-deps chromium   # 需要 sudo
python3 audio.py out/audio.wav
node render.mjs --scene=scene-v2.html --stills=0.8,3.8,6.8,9.0,10.0 --out=qa   # 先抽静帧自检
node render.mjs --scene=scene-v2.html --frames=0:12 --fps=30 --out=out/silent-v2.mp4
ffmpeg -i out/silent.mp4 -i out/audio.wav -c:v copy -c:a aac -shortest out/code3d-final.mp4
mkdir -p video && cp out/code3d-final.mp4 video/   # 注意：out/ 属于构建产物目录，不在工作区快照里
```

## 踩到的坑（比成品更有价值的部分）

1. **`file://` 下 ES module 会被 CORS 挡** → `render.mjs` 内置了一个静态 HTTP 服务器。
2. **字体必须等 `document.fonts.ready` 再建 CanvasTexture**，否则中文首帧变豆腐块。
   （这就是为什么契约里有个 `window.ready()` 门。）
3. **运镜穿过主体**：第一版结尾机位从背后直冲正面，从环面结和内核中间穿了过去，
   t≈10s 出现一整块淡青色多边形。靠抽帧 contact sheet 发现，改成右侧绕行解决。
   → 这就是那批工作流里"逐镜头出静帧自检"步骤存在的理由。
4. **ffmpeg-static 没有 `drawtext` 滤镜**，contact sheet 的标注只能放弃或换方案。

## 这条路线的边界（诚实版）

- 强项：矢量排版/文字零幻觉、可局部修改（改变量不重抽卡）、音画同时钟、产物可版本管理。
- 弱项：真实人脸/布料/实拍摄影机运动做不了；本质是"高级动态幻灯片"。
  要实拍感得混合视频模型（绿幕人物 + 代码场景，或 Runway Aleph 重风格化）。
- 交付成本：要 MP4 就永远背着 Node + Chromium + ffmpeg 这套构建依赖——**模型产出的是渲染器，不是渲染结果**。

---

# V3 「墨」— 究极改善版（对着六个差距逐条补）

成片：[`video/code3d-v3.mp4`](video/code3d-v3.mp4) · 10.00s · 1280×720 · **24fps · 180° 快门运动模糊** · H.264+AAC
源：[`scene-v3.html`](scene-v3.html) · 配乐 `skills/blockbuster/scripts/score.py --arrange=ink`（[`audio3.py`](audio3.py) 现为其薄封装）· 质检图 `video/contact-sheet-v3.png` + `video/score-spectrogram.png`

| 六个差距 | V3 怎么补 |
|---|---|
| 1 美术方向/纹理 | commit **水墨宣纸**：生成模型提供宣纸纤维 + 远山墨版（multiply 叠合），墨着色器做浓/淡/枯三阶 + 干笔 + pigment granulation + 边缘积墨 |
| 2 动画原理/故事 | 一滴墨的起承转合：预备 hesitate → 挤压拉伸下落 → 溅射跟随 → 醒成 swirl → 凝浓收笔 → **盖印作为动作动机驱动的 cut** → 落款 |
| 3 运动模糊/帧率 | 24fps + 180° 快门，时间超采样 ×3（线性 HalfFloat 累加） |
| 4 声音 | 结构化配乐：锚点与画面同钟 + Foley（滴落/溅射/盖印 thud）+ 三级延迟空间。**v3.1 换物理引擎**：初版加性谐波被用户判"塑料"，改为块 Karplus-Strong 弦模型（频率相关衰减 + 拨弦位梳状谱 + 绰注/吟猱 + 琴体共振峰 + 擦弦噪），并由 `audio_qa.py` 6 项客观门禁把关（含两条反塑料门） |
| 5 迭代/导演 | 本片的每次收敛都靠 contact sheet；流程固化进 SKILL 的 Phase 5 硬门禁 |
| 6 混合管线 | 宣纸 + 远山 = 生成模型的板材质，代码叠合；规则写进 SKILL 的 hybrid rules |

实测：1.84s/帧（墨着色比 PBR 便宜，但运动模糊 ×3 把预算吃回去），240 帧 442.5s。

**声音 v3.1（反塑料重写）**：加性谐波 = 恒定亮度 = 塑料。物理模型给出频率相关衰减、滑音弯线、
刮奏叠置（见 `video/score-spectrogram.png`）。`audio_qa.py` 实测 6/6 PASS：peak −1.21 dBTP、
RMS −20.2 dBFS、crest 19.0、锚点偏差 ≤60ms、亮度 400ms 内衰减 20%、7/8 长音有音高活性。

途中抓到的两个真 bug（都写进 craft-rules 了）：
- `hash(floor(vW*52.0))` 传 vec3 → 墨着色器从未编译成功，之前看到的"墨"其实是反壳描边的 fallback；
- `MultiplyBlending` 必须 `premultipliedAlpha:true`。

---

# SKILL：blockbuster（你的最终目标）

`skills/blockbuster/` —— 装好后，对 agent 描述需求，它会**先问清楚全部诉求**再产出。

```
skills/blockbuster/
  SKILL.md                    协议：intake → commit 美术 → brief → storyboard → 确定性 build → QA 门禁 → 渲染 → 交付
  references/intake.md        必问清单（创意轴不许默默默认）+ 预算诚实化
  references/craft-rules.md   六课变成可执行规则 + 数值护栏 + QA gates
  references/styles.md        5 个 committed 风格预设（含本片水墨配方）+ 自创预设的 7 问
  references/pipeline.md      确定性契约 / 运动模糊数学 / 后期链 / 成本模型 / hybrid 规则 / out/ 陷阱
  references/brief-template.md 七块 brief 模板
  scripts/render.mjs          逐帧捕获 + ffmpeg（stills / frames 两模式，shader 编译失败会 loud fail）
  scripts/guqin.py            物理拨弦引擎：块 K-S 弦模型 + 拨弦位梳状谱 + 绰注/吟猱 + 琴体共振峰 + 擦弦噪
  scripts/score.py            配乐编排：--anchors 与画面同钟、--arrange=ink|generic、--emit-anchors 单一时钟源
  scripts/audio_qa.py         客观音频门禁 6 项（含 L4 亮度衰减 / L5 音高活性 两条"反塑料"门）
  scripts/qa.mjs              从**编码后** mp4 抽帧拼 contact sheet
  scripts/check_env.py        环境自检 + 精确安装命令
```

安装：`cp -r skills/blockbuster ~/.claude/skills/`（或任何 agent 的 skills 目录）。
它强制的事：不许跳过 intake；不许在 contact sheet 干净之前整片渲染；交付物不许留在 `out/`。
