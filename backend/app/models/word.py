from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import StudyStage


class WordStatus(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    MASTERED = "mastered"


class WordBank(Base):
    __tablename__ = "word_banks"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100))
    stage: Mapped[StudyStage] = mapped_column(Enum(StudyStage, values_callable=lambda x: [e.value for e in x]))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    words: Mapped[list["Word"]] = relationship(back_populates="word_bank", lazy="selectin")


class Word(Base):
    __tablename__ = "words"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    word_bank_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("word_banks.id", ondelete="CASCADE")
    )
    word: Mapped[str] = mapped_column(String(100))
    phonetic: Mapped[str | None] = mapped_column(String(100), nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    definition: Mapped[str] = mapped_column(Text)
    example_sentence: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    part_of_speech: Mapped[str | None] = mapped_column(String(30), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    word_bank: Mapped["WordBank"] = relationship(back_populates="words")

    user_progress: Mapped[list["UserWordProgress"]] = relationship(
        back_populates="word", lazy="selectin"
    )


class UserWordProgress(Base):
    """SM-2 间隔重复学习进度"""

    __tablename__ = "user_word_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    word_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("words.id", ondelete="CASCADE")
    )

    # SM-2 参数
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[int] = mapped_column(Integer, default=0)   # 天数
    repetitions: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[WordStatus] = mapped_column(Enum(WordStatus, values_callable=lambda x: [e.value for e in x]), default=WordStatus.NEW)
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    word: Mapped["Word"] = relationship(back_populates="user_progress")
