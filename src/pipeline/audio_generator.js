/**
 * @file audio_generator.js
 * @description 程序化定制声学合成器：根据分镜与流派自动合成物理声效与母带音轨
 * 严格接入 AudioWorkstation 闭环母带限制器，确保 6 项客观门禁全部一次性通过
 */

const {
  AudioWorkstation,
  PhysicalString,
  generateSealImpact,
  generateBrushWhoosh,
  SAMPLE_RATE
} = require("../core/audio/synth");
const { evaluateAudioQuality } = require("../core/audio/qc");

/**
 * 电影级重音 Braam / 电子次重低音合成
 */
function synthBraam(sampleRate, duration, rootFreq = 55.0) {
  const totalSamples = Math.round(sampleRate * duration);
  const out = new Float64Array(totalSamples);

  for (let i = 0; i < totalSamples; i++) {
    const t = i / sampleRate;
    const freq = rootFreq * (1 + 1.2 * Math.exp(-t * 3.5));
    const phase = 2 * Math.PI * freq * t;
    const saw = 2 * ((phase / (2 * Math.PI)) % 1) - 1;
    const sub = Math.sin(2 * Math.PI * (freq * 0.5) * t);
    const env = Math.min(1.0, t * 25) * Math.exp(-t * 1.8);
    out[i] = (saw * 0.4 + sub * 0.6) * env;
  }
  return out;
}

/**
 * 冲音升频器 (Riser / Whoosh)
 */
function synthRiser(sampleRate, duration, startFreq = 80, endFreq = 600) {
  const totalSamples = Math.round(sampleRate * duration);
  const out = new Float64Array(totalSamples);

  for (let i = 0; i < totalSamples; i++) {
    const p = i / totalSamples;
    const freq = startFreq + (endFreq - startFreq) * Math.pow(p, 2.5);
    const phase = 2 * Math.PI * freq * (i / sampleRate);
    const noise = Math.random() * 2 - 1;
    const env = Math.pow(p, 1.8);
    out[i] = (Math.sin(phase) * 0.7 + noise * 0.3) * env * 0.45;
  }
  return out;
}

/**
 * 根据分镜自动化合成高保真立体声音频并执行母带处理
 */
async function generateProceduralAudio(storyboard, outputPath) {
  const duration = storyboard.meta.duration || 8.0;
  const daw = new AudioWorkstation(duration, SAMPLE_RATE);
  const beats = storyboard.beats;
  const genreId = storyboard.meta.genre.id;
  const physString = new PhysicalString(SAMPLE_RATE);

  // 1. 注入全篇低底噪温暖氛围底床 (保证 LRA 在 8 ~ 14 LU 舒适区间)
  const bedSamples = Math.round(duration * SAMPLE_RATE);
  const bed = new Float64Array(bedSamples);
  for (let i = 0; i < bedSamples; i++) {
    const t = i / SAMPLE_RATE;
    const drone = Math.sin(2 * Math.PI * 110 * t) * 0.04 + Math.sin(2 * Math.PI * 164.8 * t) * 0.03;
    bed[i] = drone;
  }
  daw.mixTrack(bed, 0, 0.0, 0.5);

  // 2. 遍历节拍点，注入多轨事件
  for (const beat of beats) {
    const cue = beat.audio.cue;

    if (cue === "ambient_riser") {
      const riser = synthRiser(SAMPLE_RATE, beat.audio.duration, 70, 480);
      daw.mixTrack(riser, beat.start, 0.0, 0.75);
      const whoosh = generateBrushWhoosh(beat.audio.duration, 0.45);
      daw.mixTrack(whoosh, beat.start, 0.1, 0.6);
    } else if (cue === "sub_drop") {
      const dropDur = beat.audio.duration;
      const sub = synthBraam(SAMPLE_RATE, dropDur, 65);
      daw.mixTrack(sub, beat.start, 0.0, 0.85);
    } else if (cue === "rhythmic_pulse") {
      // 快速物理拨弦琶音脉冲
      const freqs = genreId === "organic_art" ? [196, 220, 261, 329] : [130.8, 164.8, 196.0, 246.9];
      const stepInterval = 0.16;
      for (let step = 0; step < 8; step++) {
        const f = freqs[step % freqs.length];
        const pluck = physString.synthesize({
          freq: f,
          duration: 0.5,
          velocity: 0.75,
          damping: 0.991
        });
        const pan = Math.sin(step) * 0.5;
        daw.mixTrack(pluck, beat.start + step * stepInterval, pan, 0.65);
      }
    } else if (cue === "braam_impact") {
      const braam = synthBraam(SAMPLE_RATE, beat.audio.duration, 45);
      const seal = generateSealImpact();
      daw.mixTrack(braam, beat.start, 0.0, 0.9);
      daw.mixTrack(seal, beat.start, 0.0, 0.8);
    } else if (cue === "crystal_chime") {
      const chimeFreq = genreId === "organic_art" ? 392.0 : 523.25;
      const chime = physString.synthesize({
        freq: chimeFreq,
        duration: 1.5,
        velocity: 0.85,
        damping: 0.996
      });
      daw.mixTrack(chime, beat.start, 0.0, 0.8);
    }
  }

  // 2. 母带压限与响度标准化 (-14 LUFS, -1.2 dBTP)
  daw.mastering(-14.0, -1.2);

  // 3. 导出 WAV
  daw.exportWav(outputPath);

  // 4. 执行 6 项门禁质检
  const qc = evaluateAudioQuality(outputPath);
  return {
    path: outputPath,
    duration,
    qc
  };
}

module.exports = {
  generateProceduralAudio
};
