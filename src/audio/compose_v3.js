/**
 * @file compose_v3.js
 * @description V3「墨」物理建模声音合成与质检驱动脚本
 */

const path = require("path");
const fs = require("fs");
const {
  PhysicalString,
  applyBodyResonance,
  generateSealImpact,
  generateBrushWhoosh,
  AudioWorkstation
} = require("../core/audio/synth");
const { evaluateAudioQuality, generateSpectrogram } = require("../core/audio/qc");
const { NARRATIVE_BEATS } = require("../scenes/v3_ink");

async function composeV3Audio() {
  const duration = 10.0;
  const ws = new AudioWorkstation(duration);
  const string = new PhysicalString();

  console.log("[Compose] 开始执行 V3「墨」物理拨弦与音效合成...");

  // Beat 1: 起势 (0.0s ~ 1.2s) - 空灵高音泛音 (D5 587.33Hz)
  const tone1 = string.synthesize({
    freq: 587.33,
    duration: 2.2,
    velocity: 0.88,
    damping: 0.994,
    harmonicNode: 2,
    nailTone: 0.25
  });
  ws.mixTrack(applyBodyResonance(tone1), 0.20, -0.2, 0.95);

  // Beat 2: 破墨 (1.2s ~ 2.4s) - 墨滴触纸，明亮原音下潜 (D4 293.66Hz -> D3 146.83Hz 滑音)
  const tone2 = string.synthesize({
    freq: 293.66,
    duration: 2.2,
    velocity: 0.9,
    damping: 0.989,
    pluckPos: 0.18,
    glissando: [
      { t: 0.0, freq: 293.66 },
      { t: 0.3, freq: 293.66 },
      { t: 0.9, freq: 220.00 }
    ],
    nailTone: 0.45
  });
  ws.mixTrack(applyBodyResonance(tone2), 1.20, 0.1, 0.95);

  // Beat 3: 运笔 (2.4s ~ 3.6s) - 狂草飞白微摩擦 + 游龙滑音 (A3 220Hz -> E4 329.63Hz)
  const whoosh = generateBrushWhoosh(1.6);
  ws.mixTrack(whoosh, 2.35, -0.15, 0.7);

  const tone3 = string.synthesize({
    freq: 220.00,
    duration: 2.0,
    velocity: 0.85,
    damping: 0.986,
    pluckPos: 0.25,
    glissando: [
      { t: 0.0, freq: 220.00 },
      { t: 0.4, freq: 261.63 },
      { t: 0.8, freq: 329.63 }
    ],
    nailTone: 0.5
  });
  ws.mixTrack(applyBodyResonance(tone3), 2.50, 0.25, 0.9);

  // Beat 4: 积墨 (3.6s ~ 4.8s) - 五音和鸣 (宫商角徵羽叠置: D3 146.8Hz + F#3 185Hz + A3 220Hz)
  const chordRoot = string.synthesize({ freq: 146.83, duration: 2.5, velocity: 0.85, damping: 0.991 });
  const chordThird = string.synthesize({ freq: 185.00, duration: 2.2, velocity: 0.75, damping: 0.988 });
  const chordFifth = string.synthesize({ freq: 220.00, duration: 2.0, velocity: 0.8, damping: 0.987 });
  ws.mixTrack(applyBodyResonance(chordRoot), 3.60, 0.0, 0.95);
  ws.mixTrack(applyBodyResonance(chordThird), 3.75, -0.3, 0.75);
  ws.mixTrack(applyBodyResonance(chordFifth), 3.90, 0.3, 0.8);

  // Beat 5 & 6: 聚散与构形 (4.8s ~ 7.2s) - 远山沉稳基频 (低音深沉 D2 73.4Hz + 高八度泛音)
  const deepBass = string.synthesize({ freq: 73.42, duration: 3.2, velocity: 0.92, damping: 0.995, pluckPos: 0.12 });
  const airHarmonic = string.synthesize({ freq: 440.0, duration: 2.4, velocity: 0.7, damping: 0.993, harmonicNode: 3 });
  ws.mixTrack(applyBodyResonance(deepBass), 5.80, 0.0, 1.0);
  ws.mixTrack(applyBodyResonance(airHarmonic), 6.10, 0.35, 0.7);

  // Beat 7: 凝神 (7.2s ~ 8.2s) - 空灵留白，只有极微细琴弦余音消解

  // Beat 8: 盖印 (8.2s ~ 9.2s) - 朱砂古印雷霆落定次低频冲击
  const sealImpact = generateSealImpact(2.0);
  ws.mixTrack(sealImpact, 8.20, 0.0, 0.85);

  // Beat 9: 留白 (9.2s ~ 10.0s) - 印记长尾与终极入定

  // 母带总线处理: 严格控制在 -14.0 ± 1.0 LUFS, -1.2 dBTP
  ws.mastering(-13.8, -1.2);

  // 确保输出目录
  const outDir = path.resolve(__dirname, "../../video");
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const wavPath = path.join(outDir, "code3d-v3-score.wav");
  const specPath = path.join(outDir, "score-spectrogram.png");

  ws.exportWav(wavPath);

  // 运行 6 项客观音频质检门禁
  const qcResult = evaluateAudioQuality(wavPath, NARRATIVE_BEATS);

  // 产出声学频谱瀑布图
  generateSpectrogram(wavPath, specPath);

  return { wavPath, specPath, qcResult };
}

if (require.main === module) {
  composeV3Audio().catch(console.error);
}

module.exports = { composeV3Audio };
