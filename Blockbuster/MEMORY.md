# MEMORY — Blockbuster 工作记忆（2026-09-30 重构）

## 重构记录
- 删除旧的"通用 prompt→video"流水线（src/、scripts/、server.js、public/、DEVLOG、HANDOFF）和 video/ 里的演示片。
  - 删除原因：按关键词套模板，所有主题共用同一个粒子场景，没有内容，质检只看技术参数，用户评价是"粗糙无可用"。
  - 旧版里保留下来的原则：确定性渲染（纯函数 f(t)）、带种子的随机数、从成片抽帧拼接触单检查。
- 新增 `bb/` Python 工具包，来源是两个已被用户认可的作品：马斯克 3D 传记（r3d.py），以及得到用户"很满意"评价的配乐系统（scorelib.py）。
- 新增 `bb qc` 内容质检：第一次跑马斯克成片就查出 14 处文字重叠/出画和 1 处峰值超标，都已修复。
  - 引擎因此新增两项能力：标签自动收进画面、标签碰撞时自动避让。

## 用户偏好（节选，完整版见 SKILL.md 第 0 节）
voice-01 普通话；希腊字母读英文名；必须有 3D 和逐句字幕；配乐跟画面走、有弦乐和音效、不要嗡鸣、不要刺耳转场；时效性题材先搜索；工作区保持精简；有歧义先问。

## 样例状态
| 样例 | 成片位置（工作区，不入 git） | 重建 |
|---|---|---|
| musk | ~/musk/musk_3min.mp4 | `bash examples/musk/build.sh` |
| concentration_cell / law_of_large_numbers / bohr_resonance / pinn | ~/<name>/<name>.mp4 | 画面：在 ~/<name> 下 `node scene.js video`（需要 npm install）；音轨：`python3 score.py && python3 -m bb remux <mp4> mix.wav` |
- 旁白 FLAC 放在各工作区目录的 `narration/` 里，不入 git。

## 待办 / 可改进
- 把 4 个旧 node 场景逐步迁移到 bb.render3d，统一成一套引擎。
- assets 继续扩充：人物剪影、建筑、实验器材、图表组件等。
- qc 可以加"声画事件对齐"检查：把 film.py 的事件点和 score.py 的重音时间做比对。
