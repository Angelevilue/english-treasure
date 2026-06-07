from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AccentType(str, enum.Enum):
    AMERICAN = "american"
    BRITISH = "british"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"


class SpeakMaterial(Base):
    """跟读素材"""

    __tablename__ = "speak_materials"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50))  # 教材对话/名人演讲/影视台词/...
    accent: Mapped[AccentType] = mapped_column(Enum(AccentType, values_callable=lambda x: [e.value for e in x]), default=AccentType.AMERICAN)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, values_callable=lambda x: [e.value for e in x]), default=DifficultyLevel.INTERMEDIATE
    )
    audio_url: Mapped[str] = mapped_column(String(512))
    cover_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    sentences: Mapped[list["SpeakSentence"]] = relationship(
        back_populates="material", lazy="selectin", order_by="SpeakSentence.sort_order"
    )


class SpeakSentence(Base):
    """素材单句"""

    __tablename__ = "speak_sentences"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("speak_materials.id", ondelete="CASCADE")
    )
    text: Mapped[str] = mapped_column(Text)
    translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    material: Mapped["SpeakMaterial"] = relationship(back_populates="sentences")


class SpeakRecord(Base):
    """用户跟读记录"""

    __tablename__ = "speak_records"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    material_id: Mapped[uuid.UUID | None] = mapped_column(
        String(36), ForeignKey("speak_materials.id", ondelete="SET NULL"), nullable=True
    )
    sentence_id: Mapped[uuid.UUID | None] = mapped_column(
        String(36), ForeignKey("speak_sentences.id", ondelete="SET NULL"), nullable=True
    )

    # 录音
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 评分结果
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 总分
    accuracy_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 音准
    fluency_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 流利度
    completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 完整度

    # 音素诊断（JSON）
    phoneme_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
