"""数据模型（SQLAlchemy ORM）"""
import os
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    images = relationship("Image", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("AnalysisResult", back_populates="owner", cascade="all, delete-orphan")
    ai_configs = relationship("AIConfig", back_populates="owner", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="images")
    analyses = relationship("AnalysisResult", back_populates="image", cascade="all, delete-orphan")

    @property
    def url(self) -> str:
        """供前端渲染图片的公开静态资源路径。"""
        return f"/uploads/{os.path.basename(self.file_path)}"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    provider = Column(String(32), default="cloud")         # cloud / local
    model_name = Column(String(128), default="")
    analysis_type = Column(String(64), default="all")      # all / describe / tags / scene / prompt
    result_json = Column(Text, default="{}")                # 结构化 JSON 结果
    latency = Column(Float, default=0.0)                    # 耗时（秒）
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="analyses")
    image = relationship("Image", back_populates="analyses")


class AIConfig(Base):
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    config_name = Column(String(128), default="默认配置")
    provider = Column(String(32), default="cloud")
    base_url = Column(String(512), default="")
    api_key_encrypted = Column(String(512), default="")
    model_name = Column(String(128), default="")
    is_default = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="ai_configs")
