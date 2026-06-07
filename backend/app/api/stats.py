from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_dep
from app.core.database import get_db
from app.models.user import User
from app.models.word import UserWordProgress, WordStatus
from app.models.speak import SpeakRecord

router = APIRouter()


@router.get("/overview")
async def get_stats_overview(
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """获取用户学习统计总览"""

    # 累计词汇（学习过的单词数）
    vocab_stmt = select(func.count()).select_from(UserWordProgress).where(
        UserWordProgress.user_id == user.id,
    )
    total_vocab = (await db.execute(vocab_stmt)).scalar() or 0

    # 已掌握词汇
    mastered_stmt = select(func.count()).select_from(UserWordProgress).where(
        UserWordProgress.user_id == user.id,
        UserWordProgress.status == WordStatus.MASTERED,
    )
    mastered = (await db.execute(mastered_stmt)).scalar() or 0

    # 跟读句数
    speak_stmt = select(func.count()).select_from(SpeakRecord).where(
        SpeakRecord.user_id == user.id,
    )
    speak_count = (await db.execute(speak_stmt)).scalar() or 0

    # 连续打卡天数（基于 UserWordProgress.updated_at）
    streak = 0
    streak_stmt = select(
        func.distinct(func.date(UserWordProgress.updated_at))
    ).where(
        UserWordProgress.user_id == user.id,
    ).order_by(
        func.date(UserWordProgress.updated_at).desc()
    ).limit(60)
    streak_result = await db.execute(streak_stmt)
    dates = [row[0] for row in streak_result.all() if row[0]]

    if dates:
        from datetime import date
        today = date.today()
        streak = 0
        for i in range(len(dates)):
            expected = today.isoformat() if i == 0 else (today - __import__('datetime').timedelta(days=i)).isoformat()
            if expected in dates:
                streak += 1
            elif i == 0:
                # 今天没学，检查昨天
                yesterday = (today - __import__('datetime').timedelta(days=1)).isoformat()
                if yesterday in dates:
                    streak = 1
                    continue
                break
            else:
                break

    return {
        "total_vocab": total_vocab,
        "mastered_vocab": mastered,
        "speak_count": speak_count,
        "streak_days": streak,
        "study_stage": user.profile.study_stage.value if user.profile else "college",
        "daily_goal": user.profile.daily_goal_words if user.profile else 20,
    }
