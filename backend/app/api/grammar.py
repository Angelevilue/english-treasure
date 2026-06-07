from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_dep
from app.chains.grammar_chain import analyze_grammar, correct_grammar
from app.core.database import get_db
from app.models.grammar import GrammarAnalysisRecord, GrammarTopic
from app.models.user import User
from app.schemas.grammar import (
    GrammarAnalyzeRequest,
    GrammarAnalyzeResponse,
    GrammarTopicNode,
    GrammarTopicTreeResponse,
)

router = APIRouter()


# ── 语法知识库（树形结构） ──

@router.get("/topics", response_model=GrammarTopicTreeResponse)
async def get_grammar_topics(db: AsyncSession = Depends(get_db)):
    """获取所有语法知识点（树形嵌套结构）。"""
    stmt = select(GrammarTopic).order_by(GrammarTopic.sort_order)
    result = await db.execute(stmt)
    all_topics = result.scalars().all()

    # 构建树：parent_id → children
    topic_map = {
        t.id: GrammarTopicNode(
            id=t.id,
            title=t.title,
            content=t.content,
            common_errors=t.common_errors,
            sort_order=t.sort_order,
            children=[],
        )
        for t in all_topics
    }

    roots: list[GrammarTopicNode] = []
    for t in all_topics:
        node = topic_map[t.id]
        if t.parent_id and t.parent_id in topic_map:
            topic_map[t.parent_id].children.append(node)
        else:
            roots.append(node)

    return GrammarTopicTreeResponse(topics=roots)


@router.get("/topics/{topic_id}", response_model=GrammarTopicNode)
async def get_topic(topic_id: str, db: AsyncSession = Depends(get_db)):
    topic = await db.get(GrammarTopic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return GrammarTopicNode(
        id=topic.id,
        title=topic.title,
        content=topic.content,
        common_errors=topic.common_errors,
        sort_order=topic.sort_order,
        children=[],
    )


# ── AI 语法分析 / 批改 ──

@router.post("/analyze", response_model=GrammarAnalyzeResponse)
async def analyze_text(
    body: GrammarAnalyzeRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """AI 语法成分分析或错误批改。"""
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="请输入要分析的文本")

    # 调用 LangChain 链
    if body.mode == "correct":
        result = await correct_grammar(body.text)
    else:
        result = await analyze_grammar(body.text)

    # 保存记录
    record = GrammarAnalysisRecord(
        user_id=user.id,
        input_text=body.text,
        analysis_result=str(result),
        mode=body.mode,
    )
    db.add(record)
    await db.flush()

    return GrammarAnalyzeResponse(
        id=record.id,
        mode=body.mode,
        input_text=body.text,
        result=result,
    )


# ── 分析历史 ──

@router.get("/history")
async def get_analysis_history(
    limit: int = 20,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(GrammarAnalysisRecord)
        .where(GrammarAnalysisRecord.user_id == user.id)
        .order_by(GrammarAnalysisRecord.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {"id": r.id, "input_text": r.input_text[:100], "mode": r.mode, "created_at": r.created_at.isoformat()}
        for r in records
    ]
