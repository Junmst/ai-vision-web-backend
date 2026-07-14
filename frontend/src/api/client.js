import { clearToken, getToken } from "../stores/authStore";

export const API_BASE = "";
const DEMO_TOKEN = "demo-admin-token";
const DEMO_DB_KEY = "ai_vision_demo_db";

function normalizeError(detail, fallback) {
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  if (typeof detail === "string" && detail) {
    return detail;
  }
  return fallback;
}

function isDemoMode(token) {
  return token === DEMO_TOKEN;
}

function loadDemoDb() {
  const raw = localStorage.getItem(DEMO_DB_KEY);
  if (raw) {
    return JSON.parse(raw);
  }
  const initial = {
    images: [],
    aiConfigs: [
      {
        id: 1,
        user_id: 1,
        config_name: "演示默认配置",
        provider: "cloud",
        base_url: "https://demo.example/v1",
        auth_mode: "bearer",
        auth_header: "Authorization",
        model_name: "demo-vision-model",
        is_default: 1,
        created_at: new Date().toISOString(),
      },
    ],
    analyses: [],
    nextImageId: 1,
    nextConfigId: 2,
    nextAnalysisId: 1,
  };
  localStorage.setItem(DEMO_DB_KEY, JSON.stringify(initial));
  return initial;
}

function saveDemoDb(db) {
  localStorage.setItem(DEMO_DB_KEY, JSON.stringify(db));
}

function buildDemoResult(analysisType) {
  const base = {
    description: "演示模式：一张包含主体对象和背景元素的图片。",
    tags: ["演示", "图像", "识别"],
    scene: "演示场景（室内或室外混合语义）",
    prompt: "high detail, cinematic lighting, realistic composition",
  };
  if (analysisType === "describe") {
    base.tags = [];
    base.scene = "";
    base.prompt = "";
  }
  if (analysisType === "tags") {
    base.description = "";
    base.scene = "";
    base.prompt = "";
  }
  if (analysisType === "scene") {
    base.description = "";
    base.tags = [];
    base.prompt = "";
  }
  if (analysisType === "prompt") {
    base.description = "";
    base.tags = [];
    base.scene = "";
  }
  return JSON.stringify(base);
}

// 演示模式下在前端本地模拟最小 CRUD，便于无后端联调时验收页面流程
async function handleDemoRequest(path, options = {}) {
  const db = loadDemoDb();
  const method = (options.method || "GET").toUpperCase();

  if (path === "/api/auth/me" && method === "GET") {
    return { id: 1, username: "admin", created_at: new Date().toISOString() };
  }

  if (path === "/api/images" && method === "GET") {
    return db.images;
  }

  if (path === "/api/images" && method === "POST") {
    const file = options.body?.get("file");
    const image = {
      id: db.nextImageId++,
      user_id: 1,
      filename: file?.name || `demo-${Date.now()}.png`,
      file_size: file?.size || 0,
      url: "/uploads/demo.png",
      created_at: new Date().toISOString(),
    };
    db.images.unshift(image);
    saveDemoDb(db);
    return image;
  }

  if (path.startsWith("/api/images/") && method === "DELETE") {
    const id = Number(path.split("/").pop());
    db.images = db.images.filter((item) => item.id !== id);
    saveDemoDb(db);
    return { message: "删除成功" };
  }

  if (path === "/api/ai-configs" && method === "GET") {
    return db.aiConfigs;
  }

  if (path === "/api/ai-configs" && method === "POST") {
    const body = JSON.parse(options.body || "{}");
    if (body.is_default) {
      db.aiConfigs = db.aiConfigs.map((item) => ({ ...item, is_default: 0 }));
    }
    const config = {
      id: db.nextConfigId++,
      user_id: 1,
      config_name: body.config_name || "默认配置",
      provider: body.provider || "cloud",
      base_url: body.base_url || "",
      auth_mode: body.auth_mode || "bearer",
      auth_header: body.auth_header || "Authorization",
      model_name: body.model_name || "",
      is_default: body.is_default ? 1 : 0,
      created_at: new Date().toISOString(),
    };
    db.aiConfigs.unshift(config);
    saveDemoDb(db);
    return config;
  }

  if (path.startsWith("/api/ai-configs/") && method === "PUT") {
    const id = Number(path.split("/").pop());
    const body = JSON.parse(options.body || "{}");
    if (body.is_default) {
      db.aiConfigs = db.aiConfigs.map((item) => ({ ...item, is_default: 0 }));
    }
    db.aiConfigs = db.aiConfigs.map((item) => (item.id === id ? { ...item, ...body } : item));
    saveDemoDb(db);
    return db.aiConfigs.find((item) => item.id === id);
  }

  if (path.startsWith("/api/ai-configs/") && method === "DELETE") {
    const id = Number(path.split("/").pop());
    db.aiConfigs = db.aiConfigs.filter((item) => item.id !== id);
    saveDemoDb(db);
    return { message: "删除成功" };
  }

  if (path === "/api/analysis" && method === "GET") {
    return db.analyses;
  }

  if (path === "/api/analysis" && method === "POST") {
    const body = JSON.parse(options.body || "{}");
    const record = {
      id: db.nextAnalysisId++,
      user_id: 1,
      image_id: body.image_id,
      provider: "cloud",
      model_name: "demo-vision-model",
      analysis_type: body.analysis_type || "all",
      result_json: buildDemoResult(body.analysis_type || "all"),
      latency: 0.3,
      created_at: new Date().toISOString(),
    };
    db.analyses.unshift(record);
    saveDemoDb(db);
    return record;
  }

  if (path.startsWith("/api/analysis/") && method === "PUT") {
    const id = Number(path.split("/").pop());
    const body = JSON.parse(options.body || "{}");
    db.analyses = db.analyses.map((item) => (item.id === id ? { ...item, ...body } : item));
    saveDemoDb(db);
    return db.analyses.find((item) => item.id === id);
  }

  if (path.startsWith("/api/analysis/") && method === "DELETE") {
    const id = Number(path.split("/").pop());
    db.analyses = db.analyses.filter((item) => item.id !== id);
    saveDemoDb(db);
    return { message: "删除成功" };
  }

  return null;
}

// 统一 fetch 封装：处理 token、错误格式、JSON 解析
// 演示模式下走 localStorage 模拟，不发送真实请求
export async function request(path, options = {}) {
  const token = getToken();

  // 演示模式：优先走本地模拟，命中后直接返回，不发真实请求
  if (isDemoMode(token)) {
    const demoData = await handleDemoRequest(path, options);
    if (demoData !== null) {
      return demoData;
    }
  }

  // 真实请求：构建 headers，附加 Authorization
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  // 解析响应体（仅 JSON 格式）
  const isJson = (response.headers.get("content-type") || "").includes("application/json");
  const data = isJson ? await response.json() : null;

  // 处理 HTTP 错误
  if (!response.ok) {
    const message = normalizeError(data?.detail, `请求失败(${response.status})`);
    // 401 时自动清除 token，跳转登录页
    if (response.status === 401) {
      clearToken();
    }
    throw new Error(message);
  }

  return data;
}
