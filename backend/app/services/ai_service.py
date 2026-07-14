"""AI 调度层：根据用户配置选择 Provider 并执行分析"""
import base64
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.models import User, Image, AIConfig, AnalysisResult
from app.config import settings
from app.services.cloud_provider import CloudProvider


async def run_analysis(
    db: Session,
    user: User,
    image: Image,
    analysis_type: str = "all",
    ai_config_id: Optional[int] = None,
) -> AnalysisResult:
    """执行一次 AI 分析并存入数据库"""

    # 1. 读取图片转 base64
    with open(image.file_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    # 2. 获取 AI 配置
    provider = None
    base_url = ""
    api_key = ""
    model_name = ""

    if ai_config_id:
        config = db.query(AIConfig).filter(
            AIConfig.id == ai_config_id,
            AIConfig.user_id == user.id,
        ).first()
    else:
        config = db.query(AIConfig).filter(
            AIConfig.user_id == user.id,
            AIConfig.is_default == 1,
        ).first()

    if config:
        provider = config.provider
        base_url = config.base_url
        api_key = config.api_key_encrypted
        model_name = config.model_name
    else:
        # 回退到系统默认配置
        provider = "cloud"
        base_url = settings.DEFAULT_AI_BASE_URL
        api_key = settings.DEFAULT_AI_API_KEY
        model_name = settings.DEFAULT_AI_MODEL

    if not base_url or not api_key:
        raise ValueError("未配置 AI 服务，请先在「AI 配置」页面添加 API Key")

    # 3. 调用 AI
    start = time.time()

    if provider == "cloud":
        ai = CloudProvider(base_url=base_url, api_key=api_key, model=model_name)
    else:
        # 本地模型 V3 再接入
        raise NotImplementedError(f"暂不支持的 provider 类型：{provider}")

    result = await ai.analyze(image_base64=image_base64, analysis_type=analysis_type)
    elapsed = round(time.time() - start, 2)

    # 4. 存入数据库
    record = AnalysisResult(
        user_id=user.id,
        image_id=image.id,
        provider=provider,
        model_name=model_name,
        analysis_type=analysis_type,
        result_json=result.to_json(),
        latency=elapsed,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
