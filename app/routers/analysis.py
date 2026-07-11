"""AI 分析路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Image, AnalysisResult
from app.schemas import AnalysisRequest, AnalysisOut, AnalysisUpdate
from app.auth import get_current_user
from app.services.ai_service import run_analysis

router = APIRouter(prefix="/api/analysis", tags=["AI分析"])


@router.post("", response_model=AnalysisOut)
async def create_analysis(
    data: AnalysisRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 校验图片归属
    image = db.query(Image).filter(Image.id == data.image_id, Image.user_id == user.id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")

    try:
        result = await run_analysis(
            db=db,
            user=user,
            image=image,
            analysis_type=data.analysis_type,
            ai_config_id=data.ai_config_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失败：{e}")


@router.get("", response_model=list[AnalysisOut])
def list_analyses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(AnalysisResult)
        .filter(AnalysisResult.user_id == user.id)
        .order_by(AnalysisResult.created_at.desc())
        .all()
    )


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id,
        AnalysisResult.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    return record


@router.put("/{analysis_id}", response_model=AnalysisOut)
def update_analysis(
    analysis_id: int,
    data: AnalysisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id,
        AnalysisResult.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    if data.result_json is not None:
        record.result_json = data.result_json
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id,
        AnalysisResult.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
