from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


# ── 语法知识点 ──

class GrammarTopicNode(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    common_errors: str | None = None
    sort_order: int = 0
    children: list["GrammarTopicNode"] = []


class GrammarTopicTreeResponse(BaseModel):
    topics: list[GrammarTopicNode]


# ── AI 分析 ──

class GrammarAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    mode: str = Field(default="analyze", pattern="^(analyze|correct)$")


class GrammarAnalyzeResponse(BaseModel):
    id: uuid.UUID
    mode: str
    input_text: str
    result: dict  # JSON 分析结果
