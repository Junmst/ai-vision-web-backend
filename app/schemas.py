"""Pydantic 请求/响应模型"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ===================== 用户 =====================
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===================== 图片 =====================
class ImageOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_size: int
    url: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===================== AI 配置 =====================
class AIConfigCreate(BaseModel):
    config_name: str = "默认配置"
    provider: str = "cloud"
    base_url: str = ""
    api_key: str = ""
    model_name: str = ""
    is_default: int = 0


class AIConfigUpdate(BaseModel):
    config_name: Optional[str] = None
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_default: Optional[int] = None


class AIConfigOut(BaseModel):
    id: int
    user_id: int
    config_name: str
    provider: str
    base_url: str
    model_name: str
    is_default: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===================== 分析 =====================
class AnalysisRequest(BaseModel):
    image_id: int
    analysis_type: Literal["all", "describe", "tags", "scene", "prompt"] = "all"
    ai_config_id: Optional[int] = None  # None 则用默认配置


class AnalysisOut(BaseModel):
    id: int
    user_id: int
    image_id: int
    provider: str
    model_name: str
    analysis_type: str
    result_json: str
    latency: float
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisUpdate(BaseModel):
    result_json: Optional[str] = None
