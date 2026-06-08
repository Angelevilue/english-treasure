from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_dep
from app.core.database import get_db
from app.models.user import User
from app.models.word import (
    UserWordProgress,
    Word,
    WordBank,
    WordStatus,
)
from app.schemas.vocab import (
    FlashcardItem,
    FlashcardResponse,
    FlashcardReviewRequest,
    QuizAnswer,
    QuizQuestion,
    QuizResponse,
    QuizResultResponse,
    QuizSubmitRequest,
    WordBankItem,
    WordBankListResponse,
    WordItem,
    WordListResponse,
)
from app.services.sm2 import next_review_datetime, sm2_step

router = APIRouter()


# ── 词库列表 ──

@router.get("/banks", response_model=WordBankListResponse)
async def list_word_banks(
    stage: str | None = Query(None, description="按学段筛选"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(WordBank)
    if stage:
        stmt = stmt.where(WordBank.stage == stage)
    stmt = stmt.order_by(WordBank.name)

    result = await db.execute(stmt)
    banks = result.scalars().all()
    items = [
        WordBankItem(
            id=b.id,
            name=b.name,
            stage=b.stage.value,
            word_count=b.word_count,
            description=b.description,
        )
        for b in banks
    ]
    return WordBankListResponse(items=items)


# ── 词库单词列表 ──

@router.get("/banks/{bank_id}/words", response_model=WordListResponse)
async def list_words(
    bank_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    bank = await db.get(WordBank, bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="词库不存在")

    count_stmt = select(func.count()).select_from(Word).where(Word.word_bank_id == bank_id)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Word)
        .where(Word.word_bank_id == bank_id)
        .order_by(Word.created_at)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    words = result.scalars().all()

    items = [
        WordItem(
            id=w.id,
            word=w.word,
            phonetic=w.phonetic,
            audio_url=w.audio_url,
            definition=w.definition,
            example_sentence=w.example_sentence,
            example_translation=w.example_translation,
            part_of_speech=w.part_of_speech,
            difficulty=w.difficulty,
        )
        for w in words
    ]
    return WordListResponse(items=items, total=total)


# ── 今日闪卡任务 ──

@router.get("/flashcards", response_model=FlashcardResponse)
async def get_flashcards(
    bank_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    force_new: bool = Query(False, description="强制加载新词，忽略已有进度"),
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的今日复习/新学任务。"""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    # 1. 到期复习的单词
    review_stmt = (
        select(UserWordProgress)
        .where(
            UserWordProgress.user_id == user.id,
            UserWordProgress.next_review_at <= now,
            UserWordProgress.status != WordStatus.MASTERED,
        )
        .order_by(UserWordProgress.next_review_at.asc())
        .limit(limit)
    )
    review_result = await db.execute(review_stmt)
    review_progress = review_result.scalars().all()

    review_ids = {p.word_id for p in review_progress}
    remaining = limit - len(review_progress)

    items: list[FlashcardItem] = []

    # 加载复习单词
    if review_progress:
        word_ids = [p.word_id for p in review_progress]
        word_stmt = select(Word).where(Word.id.in_(word_ids))
        word_result = await db.execute(word_stmt)
        words_by_id = {w.id: w for w in word_result.scalars().all()}

        for p in review_progress:
            w = words_by_id.get(p.word_id)
            if w:
                items.append(
                    FlashcardItem(
                        word_id=w.id,
                        word=w.word,
                        phonetic=w.phonetic,
                        audio_url=w.audio_url,
                        definition=w.definition,
                        example_sentence=w.example_sentence,
                        example_translation=w.example_translation,
                        status=p.status,
                    )
                )

    # 2. 新单词（还未学习过的）
    if remaining > 0:
        new_stmt = (
            select(Word)
            .outerjoin(
                UserWordProgress,
                (UserWordProgress.word_id == Word.id)
                & (UserWordProgress.user_id == user.id),
            )
            .where(UserWordProgress.id.is_(None))
        )
        if bank_id:
            new_stmt = new_stmt.where(Word.word_bank_id == bank_id)
        new_stmt = new_stmt.order_by(Word.difficulty, Word.created_at).limit(remaining)

        new_result = await db.execute(new_stmt)
        new_words = new_result.scalars().all()

        for w in new_words:
            items.append(
                FlashcardItem(
                    word_id=w.id,
                    word=w.word,
                    phonetic=w.phonetic,
                    audio_url=w.audio_url,
                    definition=w.definition,
                    example_sentence=w.example_sentence,
                    example_translation=w.example_translation,
                    status=WordStatus.NEW,
                )
            )

    # 3. force_new: 当没有复习词时，返回新词（忽略已有进度）
    if force_new and not items:
        fresh_stmt = (
            select(Word)
            .order_by(func.random())
            .limit(limit)
        )
        if bank_id:
            fresh_stmt = fresh_stmt.where(Word.word_bank_id == bank_id)
        fresh_result = await db.execute(fresh_stmt)
        fresh_words = fresh_result.scalars().all()
        for w in fresh_words:
            items.append(
                FlashcardItem(
                    word_id=w.id,
                    word=w.word,
                    phonetic=w.phonetic,
                    audio_url=w.audio_url,
                    definition=w.definition,
                    example_sentence=w.example_sentence,
                    example_translation=w.example_translation,
                    status=WordStatus.NEW,
                )
            )

    return FlashcardResponse(
        items=items,
        new_count=len(items) - len(review_progress),
        review_count=len(review_progress),
    )


# ── 闪卡评分（提交复习结果） ──

@router.post("/flashcards/review")
async def review_flashcard(
    body: FlashcardReviewRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    # 查找或创建进度记录
    stmt = select(UserWordProgress).where(
        UserWordProgress.user_id == user.id,
        UserWordProgress.word_id == body.word_id,
    )
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = UserWordProgress(
            user_id=user.id,
            word_id=body.word_id,
            status=WordStatus.NEW,
        )
        db.add(progress)
        await db.flush()

    # SM-2 计算
    new_ef, new_interval, new_reps = sm2_step(
        ease_factor=progress.ease_factor,
        interval=progress.interval,
        repetitions=progress.repetitions,
        quality=body.quality,
    )

    progress.ease_factor = new_ef
    progress.interval = new_interval
    progress.repetitions = new_reps
    progress.next_review_at = next_review_datetime(new_interval)
    progress.last_review_at = next_review_datetime(0)  # now

    if body.quality >= 3:
        progress.correct_count += 1
    else:
        progress.incorrect_count += 1

    # 更新状态
    if new_reps >= 2 and body.quality >= 4:
        progress.status = WordStatus.MASTERED
    elif progress.status == WordStatus.NEW:
        progress.status = WordStatus.LEARNING
    else:
        progress.status = WordStatus.REVIEW

    await db.flush()

    return {
        "word_id": str(body.word_id),
        "ease_factor": new_ef,
        "interval": new_interval,
        "repetitions": new_reps,
        "status": progress.status.value,
        "next_review_at": progress.next_review_at.isoformat() if progress.next_review_at else None,
    }


# ── 选择模式 Quiz ──

import random


@router.get("/quiz", response_model=QuizResponse)
async def generate_quiz(
    bank_id: str | None = Query(None, description="词库 ID，不传则跨词库随机"),
    mode: str = Query("en2cn", pattern="^(en2cn|cn2en)$"),
    count: int = Query(10, ge=4, le=20),
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """生成一组选择题。mode: en2cn=英选中, cn2en=中选英"""
    # 获取候选单词
    word_stmt = select(Word)
    if bank_id:
        word_stmt = word_stmt.where(Word.word_bank_id == bank_id)
    result = await db.execute(word_stmt)
    all_words = result.scalars().all()

    if len(all_words) < 4:
        raise HTTPException(status_code=400, detail="词库单词不足 4 个，无法出题")

    # 随机选 count 个作为题目
    quiz_words = random.sample(all_words, min(count, len(all_words)))

    questions = []
    for w in quiz_words:
        # 选 3 个干扰项（排除当前词）
        others = [ow for ow in all_words if ow.id != w.id]
        distractors = random.sample(others, min(3, len(others)))

        if mode == "en2cn":
            question_text = w.word
            correct = w.definition
            options = [correct] + [d.definition for d in distractors]
        else:
            question_text = w.definition
            correct = w.word
            options = [correct] + [d.word for d in distractors]

        random.shuffle(options)
        correct_index = options.index(correct)

        questions.append(QuizQuestion(
            word_id=w.id,
            question=question_text,
            options=options,
            correct_index=correct_index,
            correct_answer=correct,
        ))

    return QuizResponse(questions=questions, mode=mode, total=len(questions))


@router.post("/quiz/submit", response_model=QuizResultResponse)
async def submit_quiz(
    body: QuizSubmitRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """提交选择题作答结果，更新 SM-2 进度"""
    total = len(body.answers)
    if total == 0:
        raise HTTPException(status_code=400, detail="作答列表为空")

    correct_count = 0
    wrong_words: list[str] = []

    for answer in body.answers:
        # 查找进度
        stmt = select(UserWordProgress).where(
            UserWordProgress.user_id == user.id,
            UserWordProgress.word_id == answer.word_id,
        )
        result = await db.execute(stmt)
        progress = result.scalar_one_or_none()

        if not progress:
            progress = UserWordProgress(
                user_id=user.id,
                word_id=answer.word_id,
                status=WordStatus.NEW,
            )
            db.add(progress)
            await db.flush()

        quality = 5 if answer.correct else 1
        new_ef, new_interval, new_reps = sm2_step(
            ease_factor=progress.ease_factor,
            interval=progress.interval,
            repetitions=progress.repetitions,
            quality=quality,
        )

        progress.ease_factor = new_ef
        progress.interval = new_interval
        progress.repetitions = new_reps
        progress.next_review_at = next_review_datetime(new_interval)
        progress.last_review_at = next_review_datetime(0)

        if answer.correct:
            correct_count += 1
            progress.correct_count += 1
        else:
            progress.incorrect_count += 1
            # 记录错词
            word = await db.get(Word, answer.word_id)
            if word:
                wrong_words.append(word.word)

        if progress.status == WordStatus.NEW:
            progress.status = WordStatus.LEARNING
        else:
            progress.status = WordStatus.REVIEW

    await db.flush()

    accuracy = correct_count / total if total > 0 else 0
    return QuizResultResponse(
        total=total,
        correct=correct_count,
        incorrect=total - correct_count,
        accuracy=round(accuracy * 100, 1),
        wrong_words=wrong_words,
    )
