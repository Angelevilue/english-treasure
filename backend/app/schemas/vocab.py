from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.word import WordStatus


# ── 词库 ──

class WordBankItem(BaseModel):
    id: uuid.UUID
    name: str
    stage: str
    word_count: int
    description: str | None = None


class WordBankListResponse(BaseModel):
    items: list[WordBankItem]


# ── 单词 ──

class WordItem(BaseModel):
    id: uuid.UUID
    word: str
    phonetic: str | None = None
    audio_url: str | None = None
    definition: str
    example_sentence: str | None = None
    example_translation: str | None = None
    part_of_speech: str | None = None
    difficulty: int


class WordListResponse(BaseModel):
    items: list[WordItem]
    total: int


# ── 闪卡 ──

class FlashcardItem(BaseModel):
    word_id: uuid.UUID
    word: str
    phonetic: str | None = None
    audio_url: str | None = None
    definition: str
    example_sentence: str | None = None
    example_translation: str | None = None
    status: WordStatus = WordStatus.NEW


class FlashcardReviewRequest(BaseModel):
    word_id: uuid.UUID
    quality: int = Field(ge=0, le=5, description="0=完全忘记, 5=完美记忆")


class FlashcardResponse(BaseModel):
    items: list[FlashcardItem]
    new_count: int
    review_count: int


# ── 学习进度 ──

class WordProgressItem(BaseModel):
    word_id: uuid.UUID
    word: str
    status: WordStatus
    ease_factor: float
    interval: int
    repetitions: int
    correct_count: int
    incorrect_count: int
    next_review_at: datetime | None = None
