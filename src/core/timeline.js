/**
 * @file timeline.js
 * @description 统一时钟与数学动力学核心：提供种子伪随机数、物理弹簧阻尼、贝塞尔缓动与节拍清单绑定。
 */

/**
 * 种子伪随机数生成器 (Mulberry32)
 * 保证跨平台、跨环境的像素级绝对一致
 */
function createPRNG(seed = 1337) {
  let s = Math.floor(seed) >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * 经典缓动函数集
 */
const Easing = {
  linear: (t) => Math.max(0, Math.min(1, t)),
  easeInQuad: (t) => t * t,
  easeOutQuad: (t) => t * (2 - t),
  easeInOutQuad: (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t),
  easeInCubic: (t) => t * t * t,
  easeOutCubic: (t) => --t * t * t + 1,
  easeInOutCubic: (t) =>
    t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  easeInExpo: (t) => (t === 0 ? 0 : Math.pow(2, 10 * (t - 1))),
  easeOutExpo: (t) => (t === 1 ? 1 : -Math.pow(2, -10 * t) + 1),
  easeInOutExpo: (t) => {
    if (t === 0) return 0;
    if (t === 1) return 1;
    if ((t *= 2) < 1) return 0.5 * Math.pow(2, 10 * (t - 1));
    return 0.5 * (-Math.pow(2, -10 * --t) + 2);
  },
  easeOutBack: (t, s = 1.70158) => {
    t = t - 1;
    return t * t * ((s + 1) * t + s) + 1;
  },
  easeInOutBack: (t, s = 1.70158) => {
    const k = s * 1.525;
    if ((t *= 2) < 1) return 0.5 * (t * t * ((k + 1) * t - k));
    return 0.5 * ((t -= 2) * t * ((k + 1) * t + k) + 2);
  }
};

/**
 * 带有阻尼的二阶真实物理弹簧 (Spring Dynamics)
 * 严禁使用死板的线性过渡，模拟真实质量与弹力惯性
 */
function createSpring({ stiffness = 170, damping = 26, mass = 1 } = {}) {
  return function evaluateSpring(t, duration = 1.0) {
    if (t <= 0) return 0;
    if (t >= duration) return 1;
    
    // 欠阻尼/过阻尼解析解
    const omega0 = Math.sqrt(stiffness / mass);
    const zeta = damping / (2 * Math.sqrt(stiffness * mass));

    if (zeta < 1) {
      // 欠阻尼震颤衰减
      const omegaD = omega0 * Math.sqrt(1 - zeta * zeta);
      const decay = Math.exp(-zeta * omega0 * t);
      const envelope = 1 - decay * (Math.cos(omegaD * t) + (zeta / Math.sqrt(1 - zeta * zeta)) * Math.sin(omegaD * t));
      return envelope;
    } else {
      // 临界阻尼/过阻尼
      const r1 = -omega0 * (zeta - Math.sqrt(Math.max(0, zeta * zeta - 1)));
      const r2 = -omega0 * (zeta + Math.sqrt(Math.max(0, zeta * zeta - 1)));
      return 1 - (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r2 - r1);
    }
  };
}

/**
 * 平滑范围映射
 */
function mapRange(value, inMin, inMax, outMin, outMax, clamp = true) {
  let norm = (value - inMin) / (inMax - inMin);
  if (clamp) norm = Math.max(0, Math.min(1, norm));
  return outMin + norm * (outMax - outMin);
}

module.exports = {
  createPRNG,
  Easing,
  createSpring,
  mapRange
};
