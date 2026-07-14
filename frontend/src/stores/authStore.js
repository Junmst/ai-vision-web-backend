const TOKEN_KEY = "ai_vision_access_token";

// 使用 localStorage 持久化 token，保证刷新后仍可请求受保护接口
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
