from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudyStage(str, enum.Enum):
    ELEMENTARY = "elementary"        # 小学
    MIDDLE_SCHOOL = "middle_school"  # 初中
    HIGH_SCHOOL = "high_school"      # 高中
    COLLEGE = "college"              # 大学
    POSTGRADUATE = "postgraduate"    # 研究生
    OVERSEAS = "overseas"            # 海思 (雅思/托福/GRE)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    wechat_openid: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True
    )
    hashed_password: Mapped[str | None] = mapped_column(String(128), nullable=True)
    nickname: Mapped[str] = mapped_column(String(50), default="英语学习者")
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关系
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, lazy="selectin"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    study_stage: Mapped[StudyStage] = mapped_column(
        Enum(StudyStage, values_callable=lambda x: [e.value for e in x]), default=StudyStage.COLLEGE
    )
    daily_goal_words: Mapped[int] = mapped_column(default=20)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关系
    user: Mapped["User"] = relationship(back_populates="profile")
