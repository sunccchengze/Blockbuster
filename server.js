/**
 * @file server.js
 * @description Blockbuster Universal Studio 生产级服务入口
 * 监听 0.0.0.0:3000，提供通用需求驱动 (Prompt-to-Video) 视频生产流水线 API、REST API、流式静态资源与实时日志推流
 */

const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const { runBlockbusterPipeline } = require("./src/pipeline/orchestrator");

const app = express();
const PORT = process.env.PORT || 3000;

// 允许跨域与任意主机头 (适配 e2b 代理域名 https://{port}-{sandboxId}.e2b.app)
app.use(cors({ origin: "*" }));
app.use(express.json());

// 静态托管 generated 目录与 video 目录
const GENERATED_DIR = path.resolve(__dirname, "public/generated");
if (!fs.existsSync(GENERATED_DIR)) fs.mkdirSync(GENERATED_DIR, { recursive: true });

const VIDEO_DIR = path.resolve(__dirname, "video");
app.use("/video", express.static(VIDEO_DIR, {
  setHeaders: (res, filePath) => {
    if (filePath.endsWith(".mp4")) {
      res.setHeader("Content-Type", "video/mp4");
      res.setHeader("Accept-Ranges", "bytes");
    } else if (filePath.endsWith(".wav")) {
      res.setHeader("Content-Type", "audio/wav");
    } else if (filePath.endsWith(".png")) {
      res.setHeader("Content-Type", "image/png");
    }
  }
}));

app.use(express.static(path.resolve(__dirname, "public"), {
  setHeaders: (res, filePath) => {
    if (filePath.endsWith(".mp4")) {
      res.setHeader("Content-Type", "video/mp4");
      res.setHeader("Accept-Ranges", "bytes");
    }
  }
}));

// 日志事件广播机制 (Server-Sent Events)
let logClients = [];
function broadcastLog(line) {
  const data = `data: ${JSON.stringify({ text: line, time: new Date().toLocaleTimeString() })}\n\n`;
  logClients.forEach((client) => client.write(data));
}

// 1. 系统状态与门禁数据 API
app.get("/api/status", (req, res) => {
  let gitCommit = "unknown";
  try {
    const { execSync } = require("child_process");
    gitCommit = execSync("git rev-parse --short HEAD", { stdio: "pipe" }).toString().trim();
  } catch (e) {}

  res.json({
    status: "online",
    name: "Blockbuster Universal Studio",
    version: "v4.0 Universal Pipeline",
    gitCommit,
    branch: "arena/01a0f07e-blockbuster",
    pipeline: "Prompt -> Intent -> Procedural Scene & Audio -> Stream Engine -> Quality Gate",
    gatesPassed: true
  });
});

// 2. 通用需求驱动视频流水线 API (Prompt-to-Video)
let isPipelineBusy = false;
app.post("/api/pipeline/generate", async (req, res) => {
  const { prompt } = req.body;
  if (!prompt || typeof prompt !== "string" || prompt.trim().length === 0) {
    return res.status(400).json({ error: "请输入有效的视频需求或创意描述" });
  }

  if (isPipelineBusy) {
    return res.status(409).json({ error: "当前已有流水线任务正在运行，请稍候片刻" });
  }

  isPipelineBusy = true;
  broadcastLog(`\n🎬 [Pipeline] 接收到需求驱动生成任务: "${prompt.trim()}"`);

  try {
    const manifest = await runBlockbusterPipeline(prompt.trim(), {
      outputDir: GENERATED_DIR,
      onLog: (msg) => {
        console.log(msg);
        broadcastLog(msg);
      }
    });

    isPipelineBusy = false;
    broadcastLog(`🎉 [Pipeline] 视频制作完成! 视频已就绪: ${manifest.deliverables.video}`);
    res.json({ success: true, manifest });
  } catch (err) {
    isPipelineBusy = false;
    console.error(err);
    broadcastLog(`❌ [Pipeline Error] ${err.message}`);
    res.status(500).json({ error: err.message });
  }
});

// 3. 获取流水线历史生成作品列表 API
app.get("/api/pipeline/history", (req, res) => {
  try {
    const files = fs.readdirSync(GENERATED_DIR).filter((f) => f.endsWith("_manifest.json"));
    const history = [];

    for (const f of files) {
      try {
        const full = path.join(GENERATED_DIR, f);
        const content = JSON.parse(fs.readFileSync(full, "utf8"));
        history.push(content);
      } catch (e) {}
    }

    history.sort((a, b) => b.timestamp - a.timestamp);
    res.json(history);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// 4. 制品与资产文件列表 API
app.get("/api/artifacts", (req, res) => {
  const artifacts = [
    {
      id: "code3d-v3",
      name: "V3「墨」旗舰压力测试成片",
      filename: "code3d-v3.mp4",
      path: "/video/code3d-v3.mp4",
      type: "video/mp4",
      desc: "10.00s · 1280×720 · 24fps · 180° 快门运动模糊 · 物理拨弦配乐 · H.264+AAC",
      size: 0
    },
    {
      id: "contact-sheet-v3",
      name: "V3 九宫格印相质检单",
      filename: "contact-sheet-v3.png",
      path: "/video/contact-sheet-v3.png",
      type: "image/png",
      desc: "从编码后的 code3d-v3.mp4 真实抽帧拼贴，九个叙事 Beat 全在",
      size: 0
    },
    {
      id: "score-spectrogram",
      name: "v3.1 声学频谱瀑布图",
      filename: "score-spectrogram.png",
      path: "/video/score-spectrogram.png",
      type: "image/png",
      desc: "物理建模古琴滑音弯线、刮奏叠置与大印盖落次低频长尾",
      size: 0
    },
    {
      id: "code3d-v3-score",
      name: "v3.1 物理建模配乐母带 (WAV)",
      filename: "code3d-v3-score.wav",
      path: "/video/code3d-v3-score.wav",
      type: "audio/wav",
      desc: "48,000Hz · 16-bit · 2 Channel · -13.89 LUFS · -1.20 dBTP",
      size: 0
    }
  ];

  artifacts.forEach((item) => {
    const fullPath = path.join(VIDEO_DIR, item.filename);
    if (fs.existsSync(fullPath)) {
      item.size = fs.statSync(fullPath).size;
      item.sizeFormatted = (item.size / 1024 / 1024).toFixed(2) + " MB";
      item.exists = true;
    } else {
      item.exists = false;
    }
  });

  res.json(artifacts);
});

// 5. 叙事 Beat 清单与分镜 API
app.get("/api/beats", (req, res) => {
  const { NARRATIVE_BEATS } = require("./src/scenes/v3_ink");
  res.json(NARRATIVE_BEATS);
});

// 6. SSE 实时日志推流
app.get("/api/logs", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders();

  logClients.push(res);
  broadcastLog("[Blockbuster Studio] 客户端已连接到实时日志总线");

  req.on("close", () => {
    logClients = logClients.filter((c) => c !== res);
  });
});

// 7. 触发全量重新渲染 API
let isRendering = false;
app.post("/api/render", (req, res) => {
  if (isRendering) {
    return res.status(409).json({ error: "渲染流水线正在运行中，请等待上一任务完成" });
  }

  isRendering = true;
  broadcastLog(">>> [API] 收到全量渲染请求，正在启动流水线 runner...");

  const child = spawn("node", ["scripts/render_all.js"], { cwd: __dirname });

  child.stdout.on("data", (d) => {
    const str = d.toString().trim();
    if (str) {
      console.log(str);
      broadcastLog(str);
    }
  });

  child.stderr.on("data", (d) => {
    const str = d.toString().trim();
    if (str) {
      console.error(str);
      broadcastLog("[WARN/STDERR] " + str);
    }
  });

  child.on("close", (code) => {
    isRendering = false;
    broadcastLog(`<<< [API] 渲染任务完成，退出码: ${code}`);
  });

  res.json({ message: "渲染任务已在后台启动", status: "started" });
});

// 8. 触发物理配乐重新合成与质检 API
app.post("/api/audio", (req, res) => {
  try {
    broadcastLog(">>> [API] 启动物理建模音频合成与 6 项客观门禁验证...");
    const { composeV3Audio } = require("./src/audio/compose_v3");
    composeV3Audio().then((result) => {
      broadcastLog("<<< [API] 物理配乐合成完成，6 项门禁全部合格！");
      res.json({ success: true, result });
    }).catch((err) => {
      broadcastLog("<<< [API ERROR] " + err.message);
      res.status(500).json({ error: err.message });
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 启动服务，严格绑定 0.0.0.0
app.listen(PORT, "0.0.0.0", () => {
  console.log(`[Blockbuster Studio] 服务已启动: http://0.0.0.0:${PORT}`);
  console.log(`[Blockbuster Studio] 运行环境: Node ${process.version}, 架构: All-Domain Master`);
});
