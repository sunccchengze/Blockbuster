/**
 * @file orchestrator.js
 * @description 通用自动化视频生产流水线编排器 (Universal Blockbuster Pipeline)
 * 输入任意自然语言需求 -> 意图解析与分镜策划 -> 程序化视觉生成 -> 定制物理声学合成 -> 确定性流式渲染 -> 抽帧质检输出
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const { createCanvas, loadImage } = require("@napi-rs/canvas");

const { analyzeIntent, planStoryboard } = require("./director");
const { generateProceduralAudio } = require("./audio_generator");
const { createProceduralScene } = require("./scene_generator");
const { renderVideo } = require("../core/engine");

/**
 * 从生成的 MP4 中抽帧并合成九宫格质检接触单
 */
async function generateContactSheet(videoPath, beats, outputPath) {
  const tmpDir = path.join(path.dirname(outputPath), ".tmp_frames_" + Date.now());
  if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir, { recursive: true });

  const framePaths = [];
  const beatCount = Math.min(9, beats.length);

  try {
    for (let i = 0; i < beatCount; i++) {
      const beat = beats[i];
      const midT = ((beat.start + beat.end) / 2).toFixed(2);
      const outFrame = path.join(tmpDir, `frame_${i}.png`);
      execSync(`ffmpeg -y -ss ${midT} -i "${videoPath}" -vframes 1 -q:v 2 "${outFrame}" 2>/dev/null`);
      if (fs.existsSync(outFrame)) {
        framePaths.push({ beat, path: outFrame, time: midT });
      }
    }

    const sheetW = 1920;
    const sheetH = 1200;
    const canvas = createCanvas(sheetW, sheetH);
    const ctx = canvas.getContext("2d");

    // 展台底色
    ctx.fillStyle = "#121214";
    ctx.fillRect(0, 0, sheetW, sheetH);

    // 顶栏 Header
    ctx.fillStyle = "#f5f5f7";
    ctx.font = '600 32px -apple-system, "SF Pro Display", sans-serif';
    ctx.fillText("BLOCKBUSTER PIPELINE // AUTOMATED QUALITY CONTROL CONTACT SHEET", 48, 64);
    ctx.fillStyle = "#86868b";
    ctx.font = '16px -apple-system, "SF Pro Text", monospace';
    ctx.fillText(`SOURCE: ${path.basename(videoPath)} · SAMPLED AT BEAT MIDPOINTS · DETERMINISTIC ZERO-LOSS`, 48, 96);

    const cols = 3;
    const rows = 2;
    const cellW = 580;
    const cellH = 326;
    const startX = 48;
    const startY = 130;
    const gapX = 36;
    const gapY = 80;

    for (let i = 0; i < Math.min(6, framePaths.length); i++) {
      const item = framePaths[i];
      const r = Math.floor(i / cols);
      const c = i % cols;
      const x = startX + c * (cellW + gapX);
      const y = startY + r * (cellH + gapY);

      const img = await loadImage(item.path);
      ctx.drawImage(img, x, y, cellW, cellH);

      // 边框
      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, cellW, cellH);

      // 标头
      ctx.fillStyle = "#00f0ff";
      ctx.font = "600 14px monospace";
      ctx.fillText(`BEAT 0${i + 1}: ${item.beat.name} [T=${item.time}s]`, x, y + cellH + 24);
      ctx.fillStyle = "#86868b";
      ctx.font = "12px sans-serif";
      ctx.fillText(item.beat.action, x, y + cellH + 42);
    }

    const buf = canvas.toBuffer("image/png");
    fs.writeFileSync(outputPath, buf);
  } finally {
    try {
      execSync(`rm -rf "${tmpDir}"`);
    } catch (e) {}
  }
}

/**
 * 运行通用流水线
 */
async function runBlockbusterPipeline(prompt, options = {}) {
  const log = options.onLog || console.log;
  const outputDir = options.outputDir || path.resolve(__dirname, "../../output");
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const timestamp = Date.now();
  const slug = "blockbuster_" + timestamp;
  const videoPath = path.join(outputDir, `${slug}.mp4`);
  const audioPath = path.join(outputDir, `${slug}_score.wav`);
  const sheetPath = path.join(outputDir, `${slug}_contact_sheet.png`);
  const manifestPath = path.join(outputDir, `${slug}_manifest.json`);

  log(`[Pipeline] >>> 接收到需求指令: "${prompt}"`);

  // Stage 1: 意图解构与类型学标定
  log(`[Pipeline] [1/5] 正在执行意图解构与影视类型学标定...`);
  const intent = analyzeIntent(prompt);
  log(`[Pipeline] 类型判定: [${intent.genre.name}] | 主题: "${intent.title}" | 调色盘主色: ${intent.genre.palette.primary}`);

  // Stage 2: 分镜与叙事节拍自动化编剧
  log(`[Pipeline] [2/5] 正在自动化编剧 6 段宏观叙事节拍与镜头运镜清单...`);
  const storyboard = planStoryboard(intent);
  storyboard.beats.forEach((b) => {
    log(`  - [Beat 0${b.id}] ${b.start.toFixed(1)}s ~ ${b.end.toFixed(1)}s | ${b.name} (${b.subtitle})`);
  });

  // Stage 3: 程序化定制物理声学合成与母带校验
  log(`[Pipeline] [3/5] 正在实时计算物理声学音轨与多轨事件并执行 6 项门禁检验...`);
  const audioResult = await generateProceduralAudio(storyboard, audioPath);
  log(`[Pipeline] 音频合成完成: ${audioResult.duration}s, 48kHz 立体声, 响度与峰值门禁已验证`);

  // Stage 4: 编译程序化视觉场景并执行 180° 快门流式渲染
  log(`[Pipeline] [4/5] 正在编译确定性三维视觉逻辑，并直推 FFmpeg 进行 180° 快门流式合成...`);
  const renderFrame = createProceduralScene(storyboard);
  const scene = {
    width: intent.width,
    height: intent.height,
    fps: intent.fps,
    duration: intent.duration,
    shutterAngle: 180,
    subframes: 2, // 工业标准 2x 子样高质量抗锯齿与快门运动模糊
    render: (ctx, t) => renderFrame(t, ctx)
  };

  const renderStats = await renderVideo(scene, videoPath, audioPath, {
    fps: intent.fps,
    width: intent.width,
    height: intent.height,
    duration: intent.duration
  });
  log(`[Pipeline] 视频渲染完成! 产物大小: ${(fs.statSync(videoPath).size / 1024 / 1024).toFixed(2)} MB`);

  // Stage 5: 真实抽帧接触单与双轨质检验证
  log(`[Pipeline] [5/5] 正在从真实产出的 MP4 中抽取 6 节拍关键帧，生成 1920×1200 质检接触单...`);
  await generateContactSheet(videoPath, storyboard.beats, sheetPath);
  log(`[Pipeline] 质检接触单已生成: ${sheetPath}`);

  // 汇总全量交付清单
  const manifest = {
    prompt,
    timestamp,
    slug,
    meta: intent,
    storyboard,
    deliverables: {
      video: videoPath,
      videoFile: videoPath,
      audio: audioPath,
      audioFile: audioPath,
      contactSheet: sheetPath,
      contactSheetFile: sheetPath
    },
    audioQC: audioResult.qc,
    renderStats
  };

  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  log(`[Pipeline] ✅ 流水线全流程执行完毕！交付物清单已生成: ${manifestPath}`);

  return manifest;
}

module.exports = {
  runBlockbusterPipeline
};
