from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 启动时：可初始化 Redis 连接池等
    yield
    # 关闭时：清理资源


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── 注册路由 ──
    from app.api.auth import router as auth_router
    from app.api.vocab import router as vocab_router
    from app.api.grammar import router as grammar_router
    from app.api.speak import router as speak_router
    from app.api.stats import router as stats_router

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(vocab_router, prefix="/api/vocab", tags=["vocab"])
    app.include_router(grammar_router, prefix="/api/grammar", tags=["grammar"])
    app.include_router(speak_router, prefix="/api/speak", tags=["speak"])
    app.include_router(stats_router, prefix="/api/stats", tags=["stats"])

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "app": settings.APP_NAME}

    return app


app = create_app()
