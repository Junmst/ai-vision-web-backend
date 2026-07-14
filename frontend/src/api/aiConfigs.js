import { request } from "./client";

export function createAIConfig(payload) {
  return request("/api/ai-configs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function listAIConfigs() {
  return request("/api/ai-configs");
}

export function updateAIConfig(configId, payload) {
  return request(`/api/ai-configs/${configId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function deleteAIConfig(configId) {
  return request(`/api/ai-configs/${configId}`, {
    method: "DELETE",
  });
}
