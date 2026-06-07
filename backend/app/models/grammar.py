from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GrammarTopic(Base):
    """语法知识点（树状结构）"""

    __tablename__ = "grammar_topics"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        String(36), ForeignKey("grammar_topics.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)  # 知识点讲解（Markdown）
    common_errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # 树形自引用
    children: Mapped[list["GrammarTopic"]] = relationship(
        "GrammarTopic",
        backref="parent",
        remote_side="GrammarTopic.id",
        lazy="selectin",
    )


class GrammarAnalysisRecord(Base):
    """AI 语法分析历史记录"""

    __tablename__ = "grammar_analysis_records"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    input_text: Mapped[str] = mapped_column(Text)
    analysis_result: Mapped[str] = mapped_column(Text)  # JSON 格式的分析结果
    mode: Mapped[str] = mapped_column(String(20), default="analyze")  # analyze / correct
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
