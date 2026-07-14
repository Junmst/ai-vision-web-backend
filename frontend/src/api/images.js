import { request } from "./client";

// 上传图片：使用 FormData，不设置 Content-Type，让浏览器自动添加 boundary
export function uploadImage(file) {
  const form = new FormData();
  form.append("file", file);
  return request("/api/images", {
    method: "POST",
    body: form,
    // 注意：这里绝对不能设置 Content-Type，否则浏览器不会自动添加 boundary
  });
}

export function listImages() {
  return request("/api/images");
}

export function deleteImage(imageId) {
  return request(`/api/images/${imageId}`, {
    method: "DELETE",
  });
}
