// 统一解析后端返回的 result_json，避免页面重复写 try/catch
export function parseResult(resultJson) {
  if (!resultJson) {
    return { description: "", tags: [], scene: "", prompt: "" };
  }
  try {
    const parsed = JSON.parse(resultJson);
    return {
      description: parsed.description || "",
      tags: Array.isArray(parsed.tags) ? parsed.tags : [],
      scene: parsed.scene || "",
      prompt: parsed.prompt || "",
    };
  } catch {
    return {
      description: String(resultJson),
      tags: [],
      scene: "",
      prompt: "",
    };
  }
}
