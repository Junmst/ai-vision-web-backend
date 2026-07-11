"""云端 OpenAI 兼容 API Provider"""
import httpx
from app.services import BaseProvider, AIResult

# ========== 提示：不同平台的 base_url 格式 ==========
# 硅基流动:   https://api.siliconflow.cn/v1/chat/completions
# 智谱 GLM:   https://open.bigmodel.cn/api/paas/v4/chat/completions
# 通义千问:   https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
# DeepSeek:   https://api.deepseek.com/v1/chat/completions
# 聚合平台大同小异，关键是 /v1/chat/completions 这个路径
# ================================================


class CloudProvider(BaseProvider):
    """OpenAI 兼容格式的云端 API"""

    def __init__(self, base_url: str, api_key: str, model: str):
        # 自动补全 /chat/completions 路径（有些平台给的是带路径的，有些只给域名）
        url = base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            if url.endswith("/v1"):
                url += "/chat/completions"
            else:
                url += "/v1/chat/completions"
        self.url = url
        self.api_key = api_key
        self.model = model

    async def analyze(self, image_base64: str, analysis_type: str = "all") -> AIResult:
        prompt = self.build_system_prompt(analysis_type)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        # 提取模型文本回复
        content = data["choices"][0]["message"]["content"]
        return self.parse_json_response(content, analysis_type)
