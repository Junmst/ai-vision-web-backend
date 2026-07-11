"""图片上传与管理路由"""
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Image
from app.schemas import ImageOut
from app.config import settings
from app.auth import get_current_user

router = APIRouter(prefix="/api/images", tags=["图片"])


@router.post("", response_model=ImageOut)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 校验类型
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WEBP 格式")

    # 保存文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    saved_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, saved_name)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    img = Image(
        user_id=user.id,
        filename=file.filename or saved_name,
        file_path=save_path,
        file_size=len(content),
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.get("", response_model=list[ImageOut])
def list_images(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Image).filter(Image.user_id == user.id).order_by(Image.created_at.desc()).all()


@router.get("/{image_id}", response_model=ImageOut)
def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    img = db.query(Image).filter(Image.id == image_id, Image.user_id == user.id).first()
    if not img:
        raise HTTPException(status_code=404, detail="图片不存在")
    return img


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    img = db.query(Image).filter(Image.id == image_id, Image.user_id == user.id).first()
    if not img:
        raise HTTPException(status_code=404, detail="图片不存在")
    # 删文件
    if os.path.exists(img.file_path):
        os.remove(img.file_path)
    db.delete(img)
    db.commit()
    return {"message": "删除成功"}
