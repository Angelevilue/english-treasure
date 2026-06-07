"""用户系统 API 测试"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 注册
    resp = await client.post(
        "/api/auth/register/phone",
        json={
            "phone": "13800138000",
            "password": "test123456",
            "nickname": "测试用户",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # 获取个人信息
    resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    me = resp.json()
    assert me["phone"] == "13800138000"
    assert me["nickname"] == "测试用户"
    assert me["profile"] is not None
    assert me["profile"]["study_stage"] == "college"  # 默认大学


@pytest.mark.asyncio
async def test_duplicate_register(client: AsyncClient):
    await client.post(
        "/api/auth/register/phone",
        json={"phone": "13900139000", "password": "test123456"},
    )
    resp = await client.post(
        "/api/auth/register/phone",
        json={"phone": "13900139000", "password": "test123456"},
    )
    assert resp.status_code == 400
    assert "已注册" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/register/phone",
        json={"phone": "13700137000", "password": "correct"},
    )
    resp = await client.post(
        "/api/auth/login/phone",
        json={"phone": "13700137000", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_switch_study_stage(client: AsyncClient):
    # 注册
    resp = await client.post(
        "/api/auth/register/phone",
        json={"phone": "13600136000", "password": "test123456"},
    )
    token = resp.json()["access_token"]

    # 切换至小学
    resp = await client.put(
        "/api/auth/me/stage?stage=elementary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["profile"]["study_stage"] == "elementary"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401  # HTTPBearer 返回 401
