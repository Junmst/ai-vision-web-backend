"""AI 配置 CRUD 路由"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, AIConfig
from app.schemas import AIConfigCreate, AIConfigUpdate, AIConfigOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/ai-configs", tags=["AI配置"])


@router.post("", response_model=AIConfigOut)
def create_config(
    data: AIConfigCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 如果设为默认，先把其他配置取消默认
    if data.is_default:
        db.query(AIConfig).filter(AIConfig.user_id == user.id).update({"is_default": 0})

    config_data = data.model_dump()
    config_data["api_key_encrypted"] = config_data.pop("api_key")
    config = AIConfig(user_id=user.id, **config_data)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("", response_model=List[AIConfigOut])
def list_configs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(AIConfig).filter(AIConfig.user_id == user.id).order_by(AIConfig.created_at.desc()).all()


@router.get("/{config_id}", response_model=AIConfigOut)
def get_config(
    config_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    config = db.query(AIConfig).filter(AIConfig.id == config_id, AIConfig.user_id == user.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.put("/{config_id}", response_model=AIConfigOut)
def update_config(
    config_id: int,
    data: AIConfigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    config = db.query(AIConfig).filter(AIConfig.id == config_id, AIConfig.user_id == user.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    update_data = data.model_dump(exclude_unset=True)

    if "api_key" in update_data:
        update_data["api_key_encrypted"] = update_data.pop("api_key")

    if update_data.get("is_default"):
        db.query(AIConfig).filter(AIConfig.user_id == user.id).update({"is_default": 0})

    for key, value in update_data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{config_id}")
def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    config = db.query(AIConfig).filter(AIConfig.id == config_id, AIConfig.user_id == user.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    db.delete(config)
    db.commit()
    return {"message": "删除成功"}
