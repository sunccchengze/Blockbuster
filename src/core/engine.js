/**
 * @file engine.js
 * @description 通用离线确定性流式渲染引擎：
 * 1. 严格基于 seek(t) 纯函数求值；
 * 2. 180° 快门（曝光窗口 1/(2*fps)）多子帧加权累加运动模糊；
 * 3. 内存直接 Pipe 推流 FFmpeg stdin，零磁盘中间小碎图生成；
 * 4. 支持同步音轨封装（AAC 256k）。
 */

const { createCanvas } = require("@napi-rs/canvas");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

/**
 * 离线流式渲染导出函数
 * @param {Object} options
 * @param {Object} scene 场景对象，必须暴露 render(ctx, t, frameIndex)
 * @param {string} outputPath 输出 mp4 路径
 * @param {string} [audioPath] 可选配乐路径 (.wav / .aac)
 * @param {Object} [config] 渲染与快门配置
 */
async function renderVideo(scene, outputPath, audioPath = null, config = {}) {
  const width = config.width || scene.width || 1280;
  const height = config.height || scene.height || 720;
  const fps = config.fps || scene.fps || 24;
  const duration = config.duration || scene.duration || 10.0;
  const shutterAngle = config.shutterAngle !== undefined ? config.shutterAngle : (scene.shutterAngle !== undefined ? scene.shutterAngle : 180);
  const subframeSamples = config.subframes || scene.subframes || (shutterAngle > 0 ? 8 : 1);

  const totalFrames = Math.round(duration * fps);
  const dt = 1.0 / fps;
  const shutterDuration = (shutterAngle / 360.0) * dt;

  // 确保输出目录存在
  const outDir = path.dirname(outputPath);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  // 准备 FFmpeg 启动参数
  const ffmpegArgs = [
    "-y",
    "-f", "rawvideo",
    "-pix_fmt", "rgba",
    "-s", `${width}x${height}`,
    "-r", `${fps}`,
    "-i", "-"
  ];

  if (audioPath && fs.existsSync(audioPath)) {
    ffmpegArgs.push("-i", audioPath, "-c:a", "aac", "-b:a", "256k", "-shortest");
  }

  ffmpegArgs.push(
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    "-preset", "medium",
    outputPath
  );

  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const ffmpeg = spawn("ffmpeg", ffmpegArgs);

    let stderrData = "";
    ffmpeg.stderr.on("data", (chunk) => {
      stderrData += chunk.toString();
    });

    ffmpeg.on("error", (err) => {
      reject(new Error(`FFmpeg spawn error: ${err.message}`));
    });

    ffmpeg.on("close", (code) => {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
      if (code === 0) {
        console.log(`[Engine] 渲染完成: ${outputPath} (${totalFrames} 帧, 耗时 ${elapsed}s, 平均 ${(totalFrames / elapsed).toFixed(1)} fps)`);
        resolve({ outputPath, totalFrames, elapsed });
      } else {
        reject(new Error(`FFmpeg exited with code ${code}.\nSTDERR:\n${stderrData}`));
      }
    });

    // 内存画布与多采样累加缓冲
    const subCanvas = createCanvas(width, height);
    const subCtx = subCanvas.getContext("2d");

    // 像素累加缓冲 (Float64Array 确保多重曝光累加精度)
    const pixelCount = width * height;
    const accumR = new Float64Array(pixelCount);
    const accumG = new Float64Array(pixelCount);
    const accumB = new Float64Array(pixelCount);
    const accumA = new Float64Array(pixelCount);

    // 输出的单帧 RGBA 缓冲区
    const outputBuffer = Buffer.alloc(pixelCount * 4);

    // 预计算子采样权重（采用高斯衰减/帐篷核模拟真实快门叶片光学特性）
    const weights = new Float64Array(subframeSamples);
    let totalWeight = 0;
    for (let s = 0; s < subframeSamples; s++) {
      if (subframeSamples === 1) {
        weights[0] = 1.0;
        totalWeight = 1.0;
      } else {
        // 归一化位置 [-1, 1]
        const u = ((s + 0.5) / subframeSamples) * 2.0 - 1.0;
        // 高斯核权重
        const w = Math.exp(-0.5 * u * u * 3.0);
        weights[s] = w;
        totalWeight += w;
      }
    }
    for (let s = 0; s < subframeSamples; s++) {
      weights[s] /= totalWeight;
    }

    // 逐帧渲染并推流
    (async () => {
      try {
        for (let frame = 0; frame < totalFrames; frame++) {
          const tFrame = frame * dt;

          if (subframeSamples <= 1) {
            // 单次求值无快门模糊
            scene.render(subCtx, tFrame, frame, 0, 1, width, height);
            const imgData = subCtx.getImageData(0, 0, width, height);
            const raw = Buffer.from(imgData.data.buffer, imgData.data.byteOffset, imgData.data.byteLength);
            
            // 写入 stdin
            if (!ffmpeg.stdin.write(raw)) {
              await new Promise((res) => ffmpeg.stdin.once("drain", res));
            }
          } else {
            // 180° 快门多子帧时间超采样积分
            accumR.fill(0);
            accumG.fill(0);
            accumB.fill(0);
            accumA.fill(0);

            for (let s = 0; s < subframeSamples; s++) {
              const subT = tFrame + ((s + 0.5) / subframeSamples) * shutterDuration;
              scene.render(subCtx, subT, frame, s, subframeSamples, width, height);
              const imgData = subCtx.getImageData(0, 0, width, height);
              const data = imgData.data;
              const w = weights[s];

              for (let i = 0; i < pixelCount; i++) {
                const idx = i << 2;
                accumR[i] += data[idx] * w;
                accumG[i] += data[idx + 1] * w;
                accumB[i] += data[idx + 2] * w;
                accumA[i] += data[idx + 3] * w;
              }
            }

            // 打包进输出 Buffer
            for (let i = 0; i < pixelCount; i++) {
              const idx = i << 2;
              outputBuffer[idx] = Math.min(255, Math.max(0, Math.round(accumR[i])));
              outputBuffer[idx + 1] = Math.min(255, Math.max(0, Math.round(accumG[i])));
              outputBuffer[idx + 2] = Math.min(255, Math.max(0, Math.round(accumB[i])));
              outputBuffer[idx + 3] = Math.min(255, Math.max(0, Math.round(accumA[i])));
            }

            // 写入 stdin
            if (!ffmpeg.stdin.write(outputBuffer)) {
              await new Promise((res) => ffmpeg.stdin.once("drain", res));
            }
          }
        }

        // 推流完毕
        ffmpeg.stdin.end();
      } catch (err) {
        ffmpeg.kill("SIGKILL");
        reject(err);
      }
    })();
  });
}

module.exports = {
  renderVideo
};
