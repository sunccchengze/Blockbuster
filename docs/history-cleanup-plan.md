# 历史瘦身方案（仅供审批，不执行）

> 状态：方案草稿。没有运行 `git filter-repo`、没有强推、没有改写提交，也没有删除远端引用。

## 拟清理的历史路径

只移除用户已确认作废的旧演示媒体和两个归档压缩包：

```text
.zip
浓差电池.zip
code3d-demo/video/*.mp4
code3d-demo/video/*.wav
video/*.mp4
video/*.wav
```

预期在独立的临时镜像克隆中使用类似命令（待明确批准后才执行）：

```bash
git filter-repo --invert-paths \
  --path .zip \
  --path '浓差电池.zip' \
  --path-glob 'code3d-demo/video/*.mp4' \
  --path-glob 'code3d-demo/video/*.wav' \
  --path-glob 'video/*.mp4' \
  --path-glob 'video/*.wav'
```

不会删除 `code3d-demo/video/` 下的 PNG 接触单/频谱图，也不会删除其他源码、README、旁白或构建脚本。

## 体积估算

按当前可达历史树对 blob 去重后的实测值：

| 类别 | 唯一 blob 大小 |
|---|---:|
| 历史工作区 `.zip` | 84,053,538 bytes |
| `浓差电池.zip` | 33,425,190 bytes |
| `code3d-demo/video/` 中旧 MP4/WAV | 34,666,994 bytes |
| 根目录 `video/` 中旧 MP4/WAV | 5,791,324 bytes |
| **拟清理合计（去重后）** | **157,937,046 bytes（约 150.6 MiB）** |

`code3d-demo/video/code3d-final.mp4` 与 `code3d-v3.mp4` 在历史中指向同一 blob，估算中只计一次。路径/对象复查未发现这些目标 blob 在拟保留路径中复用；真正过滤后仍应扫描所有 refs 确认残留。当前可达历史的唯一 blob 原始大小约 226,070,109 bytes；这个数字不是 pack 文件大小。

本次 A 将新增五个必须保留的成片，共 66,017,784 bytes（约 63.0 MiB）。因此，考虑新增成片后，粗略净减少约 91,919,262 bytes（约 87.7 MiB）原始 blob 数据。实际克隆/pack 缩小量会受 delta 压缩、GC 和远端引用影响；没有用临时重写来测量，因此不是承诺值。当前工作副本在多次调查 fetch 后的 pack 体积不代表一次干净克隆，不能拿来当精确基准。

五部新版成片位于 `examples/` 下，不匹配以上清理路径，必须在任何获批的重写后逐个核对路径、大小和校验值，确保完整保留。

## 影响与执行前检查

- 所有受影响提交及其后代都会获得新的 commit SHA；旧 SHA、commit 链接、签名、PR 比较页和依赖旧历史的本地分支都会受影响。
- 要让 GitHub 的 `main` 使用清理后的历史，需要强制更新远端分支。协作者必须重新克隆或按迁移说明重置，普通 pull/fast-forward 不再适用；fork 和已有克隆不会自动变小。
- 标签和 Release 所指向的提交也可能被重写。`films-2026-09-30` 的空 Release/标签须先由用户单独决定保留、删除或重定位；此方案不替用户决定。
- 现存远端分支 `arena/01a0f07e-blockbuster` 相对 `main` 有 3 个未合并提交，都是更新现已删除的 `HANDOFF.md` 的文档提交。不能把它描述为“无未合并提交”；应先由用户决定保留还是删除该分支，再制定各 ref 的更新方式。
- GitHub PR 管理的隐藏 `refs/pull/*` 不等同于普通分支，不能假设它们会随普通分支推送而被改写或清除。
- 用户尚未批准历史改写。本方案只列路径和影响，不执行过滤、强推或标签/分支删除。
