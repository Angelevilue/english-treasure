from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_dep
from app.core.database import get_db
from app.models.speak import (
    DifficultyLevel,
    SpeakMaterial,
    SpeakRecord,
    SpeakSentence,
)
from app.models.user import User
from app.schemas.speak import (
    SpeakEvaluateRequest,
    SpeakEvaluateResponse,
    SpeakMaterialDetail,
    SpeakMaterialItem,
    SpeakMaterialListResponse,
    SpeakSentenceItem,
)
from app.services.iflytek import evaluator

router = APIRouter()


# ── 素材列表 ──

@router.get("/materials", response_model=SpeakMaterialListResponse)
async def list_materials(
    category: str | None = Query(None),
    difficulty: DifficultyLevel | None = None,
    accent: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SpeakMaterial)
    if category:
        stmt = stmt.where(SpeakMaterial.category == category)
    if difficulty:
        stmt = stmt.where(SpeakMaterial.difficulty == difficulty)
    if accent:
        stmt = stmt.where(SpeakMaterial.accent == accent)
    stmt = stmt.order_by(SpeakMaterial.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    materials = result.scalars().all()

    items = [
        SpeakMaterialItem(
            id=m.id,
            title=m.title,
            description=m.description,
            category=m.category,
            accent=m.accent.value,
            difficulty=m.difficulty.value,
            audio_url=m.audio_url,
            cover_url=m.cover_url,
            sentence_count=len(m.sentences) if m.sentences else 0,
        )
        for m in materials
    ]

    count_stmt = select(func.count()).select_from(SpeakMaterial)
    total = (await db.execute(count_stmt)).scalar() or 0

    return SpeakMaterialListResponse(items=items, total=total)


# ── 素材详情（含逐句） ──

@router.get("/materials/{material_id}", response_model=SpeakMaterialDetail)
async def get_material(material_id: str, db: AsyncSession = Depends(get_db)):
    material = await db.get(SpeakMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    return SpeakMaterialDetail(
        id=material.id,
        title=material.title,
        description=material.description,
        category=material.category,
        accent=material.accent.value,
        difficulty=material.difficulty.value,
        audio_url=material.audio_url,
        cover_url=material.cover_url,
        sentences=[
            SpeakSentenceItem(
                id=s.id,
                text=s.text,
                translation=s.translation,
                audio_url=s.audio_url,
                sort_order=s.sort_order,
            )
            for s in (material.sentences or [])
        ],
    )


# ── 跟读评测 ──

@router.post("/evaluate", response_model=SpeakEvaluateResponse)
async def evaluate_speaking(
    body: SpeakEvaluateRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """提交录音，获取讯飞语音评测结果。"""
    # 查找句子
    sentence = await db.get(SpeakSentence, body.sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="句子不存在")

    # 调用讯飞评测
    eval_result = await evaluator.evaluate_sentence(
        audio_base64=body.audio_base64,
        text=sentence.text,
    )

    # 保存记录
    record = SpeakRecord(
        user_id=user.id,
        material_id=sentence.material_id,
        sentence_id=sentence.id,
        overall_score=eval_result.get("overall_score"),
        accuracy_score=eval_result.get("accuracy_score"),
        fluency_score=eval_result.get("fluency_score"),
        completeness_score=eval_result.get("completeness_score"),
        phoneme_detail=str(eval_result.get("words", eval_result.get("raw", {}))),
    )
    db.add(record)
    await db.flush()

    return SpeakEvaluateResponse(
        record_id=record.id,
        overall_score=eval_result.get("overall_score"),
        accuracy_score=eval_result.get("accuracy_score"),
        fluency_score=eval_result.get("fluency_score"),
        completeness_score=eval_result.get("completeness_score"),
        phoneme_detail=eval_result,
    )


# ── 跟读历史 ──

@router.get("/records")
async def get_speak_records(
    limit: int = 20,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SpeakRecord)
        .where(SpeakRecord.user_id == user.id)
        .order_by(SpeakRecord.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "overall_score": r.overall_score,
            "accuracy_score": r.accuracy_score,
            "fluency_score": r.fluency_score,
            "completeness_score": r.completeness_score,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
