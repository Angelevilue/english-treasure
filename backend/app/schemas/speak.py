from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


# ── 素材 ──

class SpeakSentenceItem(BaseModel):
    id: uuid.UUID
    text: str
    translation: str | None = None
    audio_url: str | None = None
    sort_order: int = 0


class SpeakMaterialItem(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    category: str
    accent: str
    difficulty: str
    audio_url: str
    cover_url: str | None = None
    sentence_count: int = 0


class SpeakMaterialDetail(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    category: str
    accent: str
    difficulty: str
    audio_url: str
    cover_url: str | None = None
    sentences: list[SpeakSentenceItem]


class SpeakMaterialListResponse(BaseModel):
    items: list[SpeakMaterialItem]
    total: int


# ── 跟读评分 ──

class SpeakEvaluateRequest(BaseModel):
    sentence_id: uuid.UUID
    audio_base64: str = Field(description="录音 base64 编码")


class SpeakEvaluateResponse(BaseModel):
    record_id: uuid.UUID
    overall_score: float | None = None
    accuracy_score: float | None = None
    fluency_score: float | None = None
    completeness_score: float | None = None
    phoneme_detail: dict | None = None
