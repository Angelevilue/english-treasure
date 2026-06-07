"""
SM-2 间隔重复算法实现

SM-2 Algorithm (SuperMemo 2):
- 每次复习后根据用户评分 (0-5) 更新 ease_factor 和 interval
- quality: 0=完全忘记, 1-2=回忆困难, 3=犹豫正确, 4=正确稍慢, 5=完美
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def sm2_step(
    ease_factor: float,
    interval: int,
    repetitions: int,
    quality: int,
) -> tuple[float, int, int]:
    """
    执行一次 SM-2 间隔重复计算。

    Args:
        ease_factor: 当前难度系数 (≥1.3)
        interval: 当前间隔天数
        repetitions: 连续正确次数
        quality: 本次评分 0-5

    Returns:
        (new_ease_factor, new_interval, new_repetitions)
    """
    if quality < 3:
        # 遗忘：重置
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)

        repetitions += 1

    # 更新 ease_factor
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3

    return ease_factor, interval, repetitions


def next_review_datetime(interval_days: int) -> datetime:
    """根据间隔天数计算下次复习时间。"""
    return datetime.now(timezone.utc) + timedelta(days=interval_days)
