/**
 * @file director.js
 * @description 通用 AI 导演中枢：需求解构、类型判定与程序化分镜策划器
 */

const GENRES = {
  SCI_FI: {
    id: "sci_fi",
    name: "未来科幻 / 量子科技",
    keywords: ["量子", "芯片", "超导", "人工智能", "AI", "未来", "科幻", "赛博", "矩阵", "网络", "计算", "激光"],
    palette: {
      bg: "#040810",
      primary: "#00f0ff",
      secondary: "#7928ca",
      accent: "#00ff88",
      text: "#ffffff",
      glow: "rgba(0, 240, 255, 0.6)"
    },
    audioStyle: "cyber_synth",
    cameraStyle: "hyper_dynamic"
  },
  COSMOS: {
    id: "cosmos",
    name: "深空宇宙 / 天体物理",
    keywords: ["宇宙", "星空", "黑洞", "超新星", "引力", "星球", "星系", "天体", "太空", "大爆炸", "深空"],
    palette: {
      bg: "#020208",
      primary: "#ff007f",
      secondary: "#4a00e0",
      accent: "#ffaa00",
      text: "#ffffff",
      glow: "rgba(255, 0, 127, 0.5)"
    },
    audioStyle: "cosmic_ambient",
    cameraStyle: "orbital_flythrough"
  },
  PRODUCT_3D: {
    id: "product_3d",
    name: "工业三维 / 极简硬件",
    keywords: ["硬件", "手机", "手表", "工业", "金属", "产品", "极简", "设计", "渲染", "发布会", "轻薄", "质感"],
    palette: {
      bg: "#0a0a0c",
      primary: "#ffffff",
      secondary: "#8e8e93",
      accent: "#0071e3",
      text: "#f5f5f7",
      glow: "rgba(255, 255, 255, 0.4)"
    },
    audioStyle: "modern_clean",
    cameraStyle: "product_pedestal"
  },
  DATA_VIZ: {
    id: "data_viz",
    name: "数据智能 / 金融孪生",
    keywords: ["数据", "金融", "大屏", "算法", "流形", "拓扑", "算力", "图表", "可视化", "区块链", "交易"],
    palette: {
      bg: "#050b14",
      primary: "#00d2ff",
      secondary: "#00f5a0",
      accent: "#f7b731",
      text: "#f1f2f6",
      glow: "rgba(0, 210, 255, 0.5)"
    },
    audioStyle: "algorithmic_pulse",
    cameraStyle: "isometric_sweep"
  },
  ORGANIC_ART: {
    id: "organic_art",
    name: "东方美学 / 意象写意",
    keywords: ["水墨", "墨", "东方", "古风", "山水", "书法", "宣纸", "意境", "诗意", "写意", "朱砂"],
    palette: {
      bg: "#efe8d8",
      primary: "#141518",
      secondary: "#4a4c52",
      accent: "#c02c23",
      text: "#121214",
      glow: "rgba(20, 21, 24, 0.3)"
    },
    audioStyle: "physical_pluck",
    cameraStyle: "zen_contemplative"
  }
};

/**
 * 意图解析器：从自然语言需求中提取流派、基调与视觉线索
 */
function analyzeIntent(prompt) {
  const p = prompt.toLowerCase();
  let bestMatch = GENRES.SCI_FI;
  let maxHits = 0;

  for (const key of Object.keys(GENRES)) {
    const genre = GENRES[key];
    let hits = 0;
    for (const kw of genre.keywords) {
      if (p.includes(kw.toLowerCase())) {
        hits++;
      }
    }
    if (hits > maxHits) {
      maxHits = hits;
      bestMatch = genre;
    }
  }

  // 提取关键词作为主题标头
  const words = prompt.replace(/[，。！？、\s]+/g, " ").trim().split(" ").filter(w => w.length > 1);
  const title = words.slice(0, 3).join(" ") || "BLOCKBUSTER EXPEDITION";

  return {
    prompt,
    title,
    genre: bestMatch,
    duration: 8.0,
    fps: 24,
    width: 1280,
    height: 720
  };
}

/**
 * 分镜与叙事节拍自动化编剧器 (Storyboard Planner)
 */
function planStoryboard(intent) {
  const { genre, title, duration } = intent;
  const beats = [];

  // 标准 6 节拍通用影视动力学结构
  // 1. 起势 (Genesis / Origin)
  beats.push({
    id: 1,
    name: "起势 · 奇点创生",
    subtitle: "Genesis / Singularity",
    start: 0.0,
    end: 1.4,
    camera: "slow_zoom_in",
    action: "虚空中微粒汇聚，引力核心点亮，空间结构开始舒展",
    visuals: {
      type: "particles_converge",
      focusText: title.toUpperCase(),
      density: 200,
      zoom: [0.8, 1.2]
    },
    audio: {
      cue: "ambient_riser",
      note: "C2",
      duration: 1.4
    }
  });

  // 2. 升维 (Unfolding / Dimensional Shift)
  beats.push({
    id: 2,
    name: "升维 · 结构铺展",
    subtitle: "Dimensional Unfolding",
    start: 1.4,
    end: 2.8,
    camera: "spiral_orbit",
    action: "核心引力场爆发，复杂的几何晶格与能量脉络向外高速延伸",
    visuals: {
      type: "geometry_burst",
      wireframe: true,
      rings: 5,
      rotationSpeed: 1.8
    },
    audio: {
      cue: "sub_drop",
      note: "G2",
      duration: 1.4
    }
  });

  // 3. 奔涌 (Acceleration & Pulse)
  beats.push({
    id: 3,
    name: "奔涌 · 算力狂飙",
    subtitle: "Kinetic Velocity",
    start: 2.8,
    end: 4.4,
    camera: "kinetic_tracking",
    action: "多层光流管道以极速穿梭，景深动态虚化，强烈的运动矢量模糊",
    visuals: {
      type: "tunnel_flow",
      streamCount: 48,
      speed: 3.5,
      chromaticAberration: true
    },
    audio: {
      cue: "rhythmic_pulse",
      note: "C3_arpeggio",
      duration: 1.6
    }
  });

  // 4. 高潮 (Climax / Grand Structure)
  beats.push({
    id: 4,
    name: "破界 · 宏观聚变",
    subtitle: "Macro Fusion",
    start: 4.4,
    end: 6.0,
    camera: "wide_revelation",
    action: "镜头猛烈拉远，宏观三维图腾完整现世，光芒耀眼，能量环谐振",
    visuals: {
      type: "hero_emblem",
      scale: 1.5,
      glowIntensity: 2.0,
      shockwave: true
    },
    audio: {
      cue: "braam_impact",
      note: "C1_heavy",
      duration: 1.6
    }
  });

  // 5. 定格 (Hero Title & Brand Slogan)
  beats.push({
    id: 5,
    name: "铭刻 · 图腾定格",
    subtitle: "Emblem Inscription",
    start: 6.0,
    end: 7.2,
    camera: "subtle_dolly",
    action: "视觉焦点收束为极简高级的品牌图腾与排版，次级光带环绕脉冲",
    visuals: {
      type: "typography_reveal",
      mainTitle: title,
      subTitle: "CODE-DRIVEN DETERMINISTIC CINEMA",
      seal: true
    },
    audio: {
      cue: "crystal_chime",
      note: "G3_sustain",
      duration: 1.2
    }
  });

  // 6. 余韵 (Fade & Harmonic Tail)
  beats.push({
    id: 6,
    name: "归寂 · 虚空回甘",
    subtitle: "Harmonic Reverberation",
    start: 7.2,
    end: duration,
    camera: "infinite_stillness",
    action: "空间能量平稳下沉，唯余深邃辉光与微粒子缓慢漂浮，余音不绝",
    visuals: {
      type: "fade_to_serenity",
      vignette: true
    },
    audio: {
      cue: "sub_decay",
      note: "C2_decay",
      duration: 0.8
    }
  });

  return {
    meta: intent,
    beats
  };
}

module.exports = {
  GENRES,
  analyzeIntent,
  planStoryboard
};
