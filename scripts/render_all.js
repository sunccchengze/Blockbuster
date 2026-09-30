/**
 * @file render_all.js
 * @description 批量流式渲染 V1, V2, V3 视频并生成后质检接触单
 */

const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");
const { renderVideo } = require("../src/core/engine");
const V1Scene = require("../src/scenes/v1_route");
const V2Scene = require("../src/scenes/v2_metallic");
const { V3Scene, NARRATIVE_BEATS } = require("../src/scenes/v3_ink");
const { composeV3Audio } = require("../src/audio/compose_v3");

async function main() {
  const videoDir = path.resolve(__dirname, "../video");
  if (!fs.existsSync(videoDir)) {
    fs.mkdirSync(videoDir, { recursive: true });
  }

  console.log("==================== 开始执行 BLOCKBUSTER 渲染流水线 ====================");

  // 1. 渲染 V1 (路线验证版)
  const v1Out = path.join(videoDir, "code3d-v1.mp4");
  console.log("\n>>> [1/4] 渲染 V1 路线验证版 (12.00s 3D 线框坐标系)...");
  const v1Scene = new V1Scene();
  await renderVideo(v1Scene, v1Out, null, {
    duration: 12.0,
    fps: 24,
    width: 1280,
    height: 720,
    shutterAngle: 0,
    subframes: 1
  });

  // 2. 渲染 V2 (质感进阶版)
  const v2Out = path.join(videoDir, "code3d-v2.mp4");
  console.log("\n>>> [2/4] 渲染 V2 质感进阶版 (10.00s 金属 PBR + Bloom)...");
  const v2Scene = new V2Scene();
  await renderVideo(v2Scene, v2Out, null, {
    duration: 10.0,
    fps: 24,
    width: 1280,
    height: 720,
    shutterAngle: 90,
    subframes: 2
  });

  // 3. 合成 v3.1 物理建模配乐与声学质检
  console.log("\n>>> [3/4] 合成 v3.1 物理建模配乐并执行 6 项门禁...");
  const audioResult = await composeV3Audio();

  // 4. 渲染 V3 旗舰成片「墨」（水墨宣纸 + 180° 快门 + 物理配乐音画封装）
  const v3Out = path.join(videoDir, "code3d-v3.mp4");
  console.log("\n>>> [4/4] 渲染 V3 旗舰成片「墨」 (10.00s 24fps 180°快门)...");
  const v3Scene = new V3Scene();
  await renderVideo(v3Scene, v3Out, audioResult.wavPath, {
    duration: 10.0,
    fps: 24,
    width: 1280,
    height: 720,
    shutterAngle: 180,
    subframes: 4
  });

  // 5. 编码后真实质检：从刚压制出的 code3d-v3.mp4 中精准抽帧生成 9 宫格 Contact Sheet
  console.log("\n>>> [质检] 从已编码的 code3d-v3.mp4 中提取 9 叙事 Beat 真实帧并拼贴印相单...");
  const contactSheetPath = path.join(videoDir, "contact-sheet-v3.png");
  await generateContactSheet(v3Out, contactSheetPath, NARRATIVE_BEATS);

  console.log("\n==================== BLOCKBUSTER 渲染与质检全部圆满完成 ====================");
}

/**
 * 从编码后的 MP4 抽帧并拼贴 3x3 九宫格 Contact Sheet
 */
async function generateContactSheet(mp4Path, outputPath, beats) {
  const tmpDir = path.join(path.dirname(outputPath), "_tmp_frames");
  if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir, { recursive: true });

  const frameFiles = [];
  beats.forEach((beat, idx) => {
    // 抽每个 beat 的中心时间点
    const midT = (beat.start + beat.end) / 2.0;
    const fPath = path.join(tmpDir, `beat_${idx + 1}.png`);
    // 调用 FFmpeg 精准抽帧
    const cmd = `ffmpeg -y -ss ${midT.toFixed(3)} -i "${mp4Path}" -vframes 1 -q:v 2 "${fPath}"`;
    execSync(cmd, { stdio: "pipe" });
    frameFiles.push(fPath);
  });

  // 使用 @napi-rs/canvas 拼贴九宫格并标注时间戳和 Beat 标题
  const { createCanvas, loadImage } = require("@napi-rs/canvas");
  const tileW = 640;
  const tileH = 360;
  const sheetW = tileW * 3;
  const sheetH = tileH * 3 + 120; // 留出顶部标题空间

  const canvas = createCanvas(sheetW, sheetH);
  const ctx = canvas.getContext("2d");

  // 工业黑底
  ctx.fillStyle = "#0a0c10";
  ctx.fillRect(0, 0, sheetW, sheetH);

  // 顶部 Header
  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 32px sans-serif";
  ctx.fillText("BLOCKBUSTER // POST-ENCODING QUALITY CONTROL: 9 NARRATIVE BEATS", 40, 52);

  ctx.fillStyle = "#8899aa";
  ctx.font = "20px monospace";
  ctx.fillText("SOURCE: video/code3d-v3.mp4 | 1280x720 24fps 180° Shutter | H.264+AAC", 40, 88);

  // 绘制 9 宫格
  for (let i = 0; i < frameFiles.length; i++) {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = col * tileW;
    const y = 120 + row * tileH;

    const img = await loadImage(frameFiles[i]);
    ctx.drawImage(img, x, y, tileW, tileH);

    // 格子边框
    ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, tileW, tileH);

    // 叙事 Beat 标签
    const beat = beats[i];
    ctx.fillStyle = "rgba(10, 12, 16, 0.75)";
    ctx.fillRect(x + 15, y + tileH - 45, tileW - 30, 32);

    ctx.fillStyle = "#ffcc00";
    ctx.font = "bold 16px monospace";
    ctx.fillText(`BEAT ${beat.id}: ${beat.name} [${beat.start.toFixed(1)}s ~ ${beat.end.toFixed(1)}s]`, x + 25, y + tileH - 24);
  }

  const buf = canvas.toBuffer("image/png");
  fs.writeFileSync(outputPath, buf);
  console.log(`[质检] 九宫格接触印相单已输出至: ${outputPath} (${(buf.length / 1024 / 1024).toFixed(2)} MB)`);

  // 清理临时小图
  frameFiles.forEach((f) => fs.unlinkSync(f));
  fs.rmdirSync(tmpDir);
}

if (require.main === module) {
  main().catch(console.error);
}
