#!/usr/bin/env node
/**
 * @file generate.js
 * @description 命令行一键运行通用 Blockbuster 视频生产流水线
 * 用法：node scripts/generate.js --prompt "制作一个量子计算芯片的科幻发布会视频"
 */

const { runBlockbusterPipeline } = require("../src/pipeline/orchestrator");

async function main() {
  const args = process.argv.slice(2);
  let prompt = "制作一个黑金风格的量子计算超导芯片发布会视频，微观粒子到宏观芯片定格";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--prompt" || args[i] === "-p") {
      prompt = args[i + 1] || prompt;
      i++;
    }
  }

  console.log("==================================================================");
  console.log("🎬 BLOCKBUSTER UNIVERSAL PIPELINE (通用端到端视频生产流水线)");
  console.log(`💬 输入需求: "${prompt}"`);
  console.log("==================================================================\n");

  const startTime = Date.now();
  try {
    const manifest = await runBlockbusterPipeline(prompt, {
      onLog: (msg) => console.log(msg)
    });

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log("\n==================================================================");
    console.log(`🎉 视频流水线全链路执行成功! (总耗时: ${elapsed}s)`);
    console.log(`🎬 视频文件: ${manifest.deliverables.videoFile}`);
    console.log(`🎵 定制配乐: ${manifest.deliverables.audioFile}`);
    console.log(`🎞 抽帧印相: ${manifest.deliverables.contactSheetFile}`);
    console.log(`📊 叙事节拍: 共 ${manifest.storyboard.beats.length} 个镜头`);
    console.log("==================================================================");
  } catch (err) {
    console.error("❌ 流水线执行失败:", err);
    process.exit(1);
  }
}

main();
