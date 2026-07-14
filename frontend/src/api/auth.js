import { request } from "./client";

export function register(payload) {
  return request("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// 登录接口是 form，不是 JSON
export function login({ username, password }) {
  const body = new URLSearchParams({ username, password });
  return request("/api/auth/login", {
    method: "POST",
    body,
  });
}

export function me() {
  return request("/api/auth/me");
}
