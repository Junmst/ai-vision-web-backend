"""AI 服务抽象层"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import json
import re


@dataclass
class AIResult:
    """AI 分析统一返回结构"""
    description: str = ""       # 图片描述
    tags: list[str] = None      # 关键词标签
    scene: str = ""             # 场景识别
    prompt: str = ""            # Prompt 反推
    raw_response: str = ""      # 原始响应（调试用）

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_json(self) -> str:
        return json.dumps({
            "description": self.description,
            "tags": self.tags,
            "scene": self.scene,
            "prompt": self.prompt,
        }, ensure_ascii=False)


class BaseProvider(ABC):
    """AI Provider 抽象基类，所有平台接入都继承这个"""

    @abstractmethod
    async def analyze(
        self,
        image_base64: str,
        analysis_type: str = "all",
    ) -> AIResult:
        """分析图片，返回统一结构"""
        ...

    @staticmethod
    def build_system_prompt(analysis_type: str) -> str:
        """根据分析类型构造 Prompt"""
        prompts = {
            "all": (
                "你是一个专业的图像分析助手。请仔细分析这张图片，严格按照以下 JSON 格式返回结果（只返回 JSON，不要其他内容）：\n"
                '{\n'
                '  "description": "图片的详细中文描述",\n'
                '  "tags": ["标签1", "标签2", "标签3"],\n'
                '  "scene": "场景类型和氛围描述",\n'
                '  "prompt": "如果用AI生成类似图片，可能使用的prompt"\n'
                '}'
            ),
            "describe": "请用中文详细描述这张图片的内容，包括主体、背景、色彩、构图等。",
            "tags": (
                "请提取这张图片的关键词标签。"
                "严格只返回一个 JSON 数组，格式如：[\"标签1\",\"标签2\",\"标签3\"]，不要其他内容。"
            ),
            "scene": "请识别这张图片的场景类型、环境氛围和光线特点，用中文简要描述。",
            "prompt": "请反推这张图片如果是 AI 生成可能使用的 prompt，用中文详细描述。",
        }
        return prompts.get(analysis_type, prompts["all"])

    @staticmethod
    def parse_json_response(text: str, analysis_type: str) -> AIResult:
        """从模型返回的文本中提取结构化结果"""
        result = AIResult(raw_response=text)

        # 尝试从返回文本中提取 JSON 块
        text_stripped = text.strip()
        # 去掉可能的 markdown 代码块标记
        if text_stripped.startswith("```"):
            text_stripped = re.sub(r"^```(?:json)?\s*", "", text_stripped)
            text_stripped = re.sub(r"\s*```$", "", text_stripped)

        try:
            data = json.loads(text_stripped)
            if isinstance(data, dict):
                result.description = data.get("description", "")
                result.tags = data.get("tags", [])
                result.scene = data.get("scene", "")
                result.prompt = data.get("prompt", "")
            elif isinstance(data, list):
                # 纯标签列表
                result.tags = [str(t) for t in data]
        except json.JSONDecodeError:
            # 解析失败就用原始文本作描述
            result.description = text.strip()

        return result
