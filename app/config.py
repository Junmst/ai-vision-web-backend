"""应用配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---------- 应用基础 ----------
    APP_NAME: str = "AI Vision Web"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ---------- 数据库 ----------
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # ---------- JWT ----------
    JWT_SECRET: str = "ai-vision-web-2024-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    # ---------- 文件上传 ----------
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    # ---------- 默认 AI 配置（你的聚合平台） ----------
    DEFAULT_AI_BASE_URL: str = ""   # 填你的聚合平台地址
    DEFAULT_AI_API_KEY: str = ""     # 填你的 API Key
    DEFAULT_AI_MODEL: str = ""       # 填模型名称

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
