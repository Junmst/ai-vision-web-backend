import { request } from "./client";

export function createAnalysis(payload) {
  return request("/api/analysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function listAnalysis() {
  return request("/api/analysis");
}

export function updateAnalysis(analysisId, payload) {
  return request(`/api/analysis/${analysisId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function deleteAnalysis(analysisId) {
  return request(`/api/analysis/${analysisId}`, {
    method: "DELETE",
  });
}
