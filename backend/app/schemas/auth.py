from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.user import StudyStage


# ── 请求 ──

class PhoneRegisterRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=20)
    password: str = Field(min_length=6, max_length=128)
    nickname: str = Field(default="英语学习者", max_length=50)


class PhoneLoginRequest(BaseModel):
    phone: str
    password: str


class WechatLoginRequest(BaseModel):
    code: str  # 微信授权码，后端换取 openid


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    study_stage: StudyStage | None = None
    daily_goal_words: int | None = Field(default=None, ge=5, le=200)
    avatar_url: str | None = None


# ── 响应 ──

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    study_stage: StudyStage
    daily_goal_words: int


class UserResponse(BaseModel):
    id: uuid.UUID
    phone: str | None = None
    nickname: str
    avatar_url: str | None = None
    profile: UserProfileResponse | None = None
    created_at: datetime
