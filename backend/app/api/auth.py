from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserProfile, StudyStage
from app.schemas.auth import (
    PhoneLoginRequest,
    PhoneRegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
    UserProfileResponse,
)

router = APIRouter()


def _user_to_response(user: User) -> UserResponse:
    profile = None
    if user.profile:
        profile = UserProfileResponse(
            id=user.profile.id,
            study_stage=user.profile.study_stage,
            daily_goal_words=user.profile.daily_goal_words,
        )
    return UserResponse(
        id=user.id,
        phone=user.phone,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        profile=profile,
        created_at=user.created_at,
    )


# ── 手机号注册 ──

@router.post("/register/phone", response_model=TokenResponse)
async def register_phone(body: PhoneRegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == body.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该手机号已注册")

    user = User(
        phone=body.phone,
        hashed_password=hash_password(body.password),
        nickname=body.nickname,
    )
    db.add(user)
    await db.flush()

    # 创建默认 profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.flush()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


# ── 手机号登录 ──

@router.post("/login/phone", response_model=TokenResponse)
async def login_phone(body: PhoneLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


# ── 微信登录（占位，后续接入微信 SDK） ──

@router.post("/login/wechat", response_model=TokenResponse)
async def login_wechat(code: str = ..., db: AsyncSession = Depends(get_db)):
    # TODO: 用 code 换取微信 openid，查找或创建用户
    raise HTTPException(status_code=501, detail="微信登录待接入")


# ── 获取当前用户 ──

async def get_current_user(
    token: str = Depends(lambda: None),  # 由子依赖覆盖
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 Authorization header 解析 JWT 并返回当前用户。实际使用见下方依赖。"""
    ...


from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的登录凭证")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user_dep)):
    return _user_to_response(user)


# ── 更新个人信息 ──

@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url

    if user.profile:
        if body.study_stage is not None:
            user.profile.study_stage = body.study_stage
        if body.daily_goal_words is not None:
            user.profile.daily_goal_words = body.daily_goal_words

    await db.flush()
    return _user_to_response(user)


# ── 学段切换 ──

@router.put("/me/stage", response_model=UserResponse)
async def switch_stage(
    stage: StudyStage,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    if not user.profile:
        raise HTTPException(status_code=400, detail="用户档案不存在")

    user.profile.study_stage = stage
    await db.flush()
    return _user_to_response(user)
