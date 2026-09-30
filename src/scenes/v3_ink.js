/**
 * @file v3_ink.js
 * @description V3 旗舰成片「墨」场景定义：
 * 1. 10.00s, 1280x720, 24fps, 180° 快门运动模糊；
 * 2. 宣纸纤维肌理 + 焦浓重淡清五色墨晕 + 枯笔飞白 + 朱砂古印；
 * 3. 严格绑定 9 个视听叙事 Beat。
 */

const { createPRNG, Easing, mapRange } = require("../core/timeline");

// 9 个叙事 Beat 的时序定义
const NARRATIVE_BEATS = [
  { id: 1, name: "起势 (Void & First Drop)", start: 0.0, end: 1.2 },
  { id: 2, name: "破墨 (Splash & Burst)", start: 1.2, end: 2.4 },
  { id: 3, name: "运笔 (Brush & Dry Bristles)", start: 2.4, end: 3.6 },
  { id: 4, name: "积墨 (Layered Tones)", start: 3.6, end: 4.8 },
  { id: 5, name: "聚散 (Particle Dispersion)", start: 4.8, end: 6.0 },
  { id: 6, name: "构形 (Form & Mountain)", start: 6.0, end: 7.2 },
  { id: 7, name: "凝神 (Focus & Calm)", start: 7.2, end: 8.2 },
  { id: 8, name: "盖印 (Seal Impact)", start: 8.2, end: 9.2 },
  { id: 9, name: "留白 (Resonance & Stillness)", start: 9.2, end: 10.0 }
];

class V3Scene {
  constructor() {
    this.width = 1280;
    this.height = 720;
    this.fps = 24;
    this.duration = 10.0;
    this.shutterAngle = 180; // 严格 180° 快门
    this.subframes = 4;      // 4 子步时间高斯曝光积分

    // 预生成确定性宣纸纤维噪声样本
    this.paperPRNG = createPRNG(42);
    this.fiberSeeds = [];
    for (let i = 0; i < 400; i++) {
      this.fiberSeeds.push({
        x: this.paperPRNG() * this.width,
        y: this.paperPRNG() * this.height,
        len: 4 + this.paperPRNG() * 14,
        angle: this.paperPRNG() * Math.PI * 2,
        alpha: 0.02 + this.paperPRNG() * 0.05
      });
    }

    // 预生成墨点飞白粒子簇
    this.inkPRNG = createPRNG(888);
    this.particles = [];
    for (let i = 0; i < 180; i++) {
      this.particles.push({
        angle: this.inkPRNG() * Math.PI * 2,
        speed: 80 + this.inkPRNG() * 260,
        radius: 1.5 + this.inkPRNG() * 4.5,
        decay: 0.6 + this.inkPRNG() * 0.8,
        offset: this.inkPRNG() * 0.4
      });
    }
  }

  /**
   * 绘制传统古法宣纸基底与纤维暗纹
   */
  drawXuanPaper(ctx, width, height) {
    // 柔和微暖米黄色宣纸底色
    const grad = ctx.createRadialGradient(
      width / 2, height / 2, 80,
      width / 2, height / 2, 650
    );
    grad.addColorStop(0, "#f8f5ee");
    grad.addColorStop(0.7, "#efe8d8");
    grad.addColorStop(1, "#dfd4c0");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    // 绘制天然植物草木纤维肌理
    ctx.strokeStyle = "#8b7e66";
    ctx.lineWidth = 1;
    for (let i = 0; i < this.fiberSeeds.length; i++) {
      const f = this.fiberSeeds[i];
      ctx.globalAlpha = f.alpha;
      ctx.beginPath();
      ctx.moveTo(f.x, f.y);
      ctx.lineTo(
        f.x + Math.cos(f.angle) * f.len,
        f.y + Math.sin(f.angle) * f.len
      );
      ctx.stroke();
    }
    ctx.globalAlpha = 1.0;
  }

  /**
   * 纯函数主渲染管线
   */
  render(ctx, t, frameIndex, subIndex, subCount, width, height) {
    // 1. 铺设宣纸肌理
    this.drawXuanPaper(ctx, width, height);

    // 2. 依据当前时间求值各个叙事 Beat

    // ================= Beat 1: 起势 (0.0s - 1.2s) 墨滴下坠 =================
    if (t < 1.4) {
      const dropProgress = Math.min(1.0, t / 1.15);
      const easeY = Easing.easeInCubic(dropProgress);
      const dropY = -40 + easeY * (height / 2 + 40);
      const dropSize = 8 + easeY * 6;

      ctx.fillStyle = "#121214";
      ctx.beginPath();
      // 墨滴拉伸水滴形态
      ctx.ellipse(width / 2, dropY, dropSize * 0.7, dropSize * 1.3, 0, 0, Math.PI * 2);
      ctx.fill();

      // 微弱下落气流尾迹
      if (dropProgress > 0.3) {
        ctx.strokeStyle = "rgba(18, 18, 20, 0.15)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(width / 2, dropY - 20);
        ctx.lineTo(width / 2, dropY - 60);
        ctx.stroke();
      }
    }

    // ================= Beat 2: 破墨 (1.2s - 2.8s) 墨滴触纸与多重水晕扩散 =================
    if (t >= 1.18 && t < 3.2) {
      const burstT = t - 1.2;
      const burstProgress = Math.max(0, Math.min(1.0, burstT / 1.2));
      const p = Easing.easeOutExpo(burstProgress);

      const cx = width / 2;
      const cy = height / 2;

      // 焦墨核心 (Core)
      const coreR = 26 + p * 35;
      ctx.fillStyle = "#101114";
      ctx.beginPath();
      ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
      ctx.fill();

      // 五色外层渗透水晕 (Capillary Diffusion Rings)
      const ringCount = 5;
      for (let r = 0; r < ringCount; r++) {
        const ringAlpha = (1.0 - burstProgress) * (0.28 - r * 0.05);
        if (ringAlpha <= 0) continue;
        const ringR = coreR + (r + 1) * (18 + p * 42);

        ctx.fillStyle = `rgba(35, 38, 44, ${ringAlpha})`;
        ctx.beginPath();
        // 分形边缘毛边
        for (let a = 0; a <= Math.PI * 2 + 0.1; a += 0.1) {
          const wobble = Math.sin(a * 7 + r * 3) * (4 + p * 8) + Math.cos(a * 13) * 3;
          const px = cx + Math.cos(a) * (ringR + wobble);
          const py = cy + Math.sin(a) * (ringR + wobble);
          if (a === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.fill();
      }

      // 炸裂飞溅粒子 (Droplet Splatters)
      for (let i = 0; i < this.particles.length; i++) {
        const pt = this.particles[i];
        const dist = pt.speed * burstProgress;
        const alpha = Math.max(0, 1.0 - burstProgress * pt.decay);
        if (alpha > 0) {
          const px = cx + Math.cos(pt.angle) * dist;
          const py = cy + Math.sin(pt.angle) * dist * 0.7; // 椭圆飞溅透视
          ctx.fillStyle = `rgba(18, 19, 22, ${alpha})`;
          ctx.beginPath();
          ctx.arc(px, py, pt.radius * (1 - burstProgress * 0.4), 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    // ================= Beat 3: 运笔 (2.4s - 4.2s) 狂草苍劲笔锋与枯笔飞白 =================
    if (t >= 2.4 && t < 5.2) {
      const strokeT = t - 2.4;
      const strokeProgress = Math.min(1.0, strokeT / 1.4);

      // 三次贝塞尔曲线笔锋轨迹 (从左下划至右上，盘旋游龙)
      const p0 = { x: 180, y: height * 0.75 };
      const p1 = { x: width * 0.35, y: height * 0.15 };
      const p2 = { x: width * 0.65, y: height * 0.85 };
      const p3 = { x: width - 200, y: height * 0.3 };

      const steps = Math.floor(strokeProgress * 150);
      for (let s = 1; s < steps; s++) {
        const u0 = (s - 1) / 150;
        const u1 = s / 150;

        const getPt = (u) => {
          const inv = 1 - u;
          return {
            x: inv * inv * inv * p0.x + 3 * inv * inv * u * p1.x + 3 * inv * u * u * p2.x + u * u * u * p3.x,
            y: inv * inv * inv * p0.y + 3 * inv * inv * u * p1.y + 3 * inv * u * u * p2.y + u * u * u * p3.y
          };
        };

        const ptA = getPt(u0);
        const ptB = getPt(u1);

        // 笔锋粗细起伏变化（顿挫与提笔）
        const pressure = Math.sin(u1 * Math.PI) * 28 + 6;

        // 浓墨主体笔触
        ctx.strokeStyle = "#16171a";
        ctx.lineWidth = pressure;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(ptA.x, ptA.y);
        ctx.lineTo(ptB.x, ptB.y);
        ctx.stroke();

        // 枯笔飞白分叉 (Flying White Bristles)
        if (s % 4 === 0) {
          ctx.strokeStyle = "rgba(45, 48, 55, 0.45)";
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(ptA.x + pressure * 0.5, ptA.y - pressure * 0.3);
          ctx.lineTo(ptB.x + pressure * 0.6, ptB.y - pressure * 0.4);
          ctx.stroke();
        }
      }
    }

    // ================= Beat 4 & 5: 积墨与聚散 (3.6s - 6.4s) 多层水墨层叠漫润与微粒升华 =================
    if (t >= 3.6 && t < 7.2) {
      const blendT = t - 3.6;
      const blendP = Math.min(1.0, blendT / 2.4);

      // 背景深淡山形墨韵
      ctx.fillStyle = `rgba(50, 55, 65, ${0.12 * Math.sin(blendP * Math.PI)})`;
      ctx.beginPath();
      ctx.moveTo(100, height);
      ctx.bezierCurveTo(width * 0.3, height * 0.4, width * 0.5, height * 0.6, width * 0.85, height);
      ctx.fill();

      // 水汽墨气上升微粒
      const particleAlpha = Math.sin(blendP * Math.PI) * 0.5;
      if (particleAlpha > 0) {
        ctx.fillStyle = `rgba(20, 22, 26, ${particleAlpha})`;
        for (let k = 0; k < 60; k++) {
          const px = 200 + (k * 17) % (width - 400);
          const py = (height * 0.8) - ((blendT * 90 + k * 23) % 400);
          ctx.beginPath();
          ctx.arc(px + Math.sin(blendT * 2 + k) * 12, py, 2.0, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    // ================= Beat 6 & 7: 构形与凝神 (6.0s - 8.4s) 苍茫远山与极度空灵留白 =================
    if (t >= 6.0) {
      const mountT = Math.min(1.0, (t - 6.0) / 1.5);
      const easeMount = Easing.easeOutQuad(mountT);

      // 第一重远山（淡墨）
      ctx.fillStyle = `rgba(40, 44, 52, ${0.35 * easeMount})`;
      ctx.beginPath();
      ctx.moveTo(80, height * 0.78);
      ctx.quadraticCurveTo(width * 0.35, height * 0.42, width * 0.68, height * 0.72);
      ctx.quadraticCurveTo(width * 0.85, height * 0.58, width - 80, height * 0.75);
      ctx.lineTo(width - 80, height);
      ctx.lineTo(80, height);
      ctx.fill();

      // 第二重近景山脊（焦浓墨，苍劲勾线）
      ctx.strokeStyle = `rgba(15, 16, 18, ${0.85 * easeMount})`;
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(150, height * 0.75);
      ctx.bezierCurveTo(width * 0.28, height * 0.62, width * 0.45, height * 0.78, width * 0.65, height * 0.68);
      ctx.stroke();

      // 书法题字：“墨” 意象中锋结构
      if (t >= 6.5) {
        const textAlpha = Math.min(1.0, (t - 6.5) / 0.8);
        ctx.fillStyle = `rgba(18, 19, 22, ${textAlpha})`;
        ctx.font = "900 84px serif";
        ctx.textAlign = "center";
        ctx.fillText("墨", width / 2, height * 0.44);

        ctx.font = "300 20px monospace";
        ctx.letterSpacing = "6px";
        ctx.fillStyle = `rgba(80, 85, 95, ${textAlpha * 0.8})`;
        ctx.fillText("CODE AS VIDEO // PURE DETERMINISTIC EVALUATION", width / 2, height * 0.52);
      }
    }

    // ================= Beat 8 & 9: 盖印与留白 (8.2s - 10.0s) 朱砂古印雷霆落定 =================
    if (t >= 8.15) {
      const sealT = t - 8.2;
      const sealX = width / 2 + 120;
      const sealY = height * 0.42;

      if (sealT >= 0) {
        // 盖落动量：强烈的冲击回弹
        const impactP = Math.min(1.0, sealT / 0.2);
        const scale = sealT < 0.2 ? 1.4 - 0.4 * Easing.easeOutBack(impactP, 2.5) : 1.0;
        const sealSize = 54 * scale;

        // 朱砂印泥色 (#b22822 / 纯正辰砂红)
        ctx.save();
        ctx.translate(sealX, sealY);
        ctx.rotate(-0.03); // 古印微倾角

        // 印章外框
        ctx.fillStyle = "#af261e";
        ctx.fillRect(-sealSize / 2, -sealSize / 2, sealSize, sealSize);

        // 内部白文/朱文金石刻印
        ctx.strokeStyle = "#efe8d8";
        ctx.lineWidth = 2.5 * scale;
        ctx.strokeRect(-sealSize * 0.42, -sealSize * 0.42, sealSize * 0.84, sealSize * 0.84);

        // 印文汉印线条模拟
        ctx.beginPath();
        ctx.moveTo(-sealSize * 0.2, -sealSize * 0.3);
        ctx.lineTo(-sealSize * 0.2, sealSize * 0.3);
        ctx.moveTo(sealSize * 0.1, -sealSize * 0.25);
        ctx.lineTo(sealSize * 0.1, sealSize * 0.25);
        ctx.stroke();

        ctx.restore();

        // 盖落瞬间的印泥震波光晕
        if (sealT < 0.45) {
          const shockR = 30 + (sealT / 0.45) * 60;
          const shockAlpha = (1.0 - sealT / 0.45) * 0.4;
          ctx.strokeStyle = `rgba(175, 38, 30, ${shockAlpha})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(sealX, sealY, shockR, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
    }

    // ================= 电影级上下宽画幅遮幅 (Letterbox 2.35:1) =================
    const letterboxH = 50;
    ctx.fillStyle = "#0c0d10";
    ctx.fillRect(0, 0, width, letterboxH);
    ctx.fillRect(0, height - letterboxH, width, letterboxH);

    // 遮幅暗金微标
    ctx.fillStyle = "rgba(220, 200, 160, 0.5)";
    ctx.font = "12px monospace";
    ctx.textAlign = "left";
    ctx.fillText("BLOCKBUSTER // CODE3D-DEMO「墨」· 24FPS 180° SHUTTER", 50, 32);

    ctx.textAlign = "right";
    ctx.fillText(`T = ${t.toFixed(3)}s / 10.000s`, width - 50, 32);
  }
}

module.exports = {
  V3Scene,
  NARRATIVE_BEATS
};
