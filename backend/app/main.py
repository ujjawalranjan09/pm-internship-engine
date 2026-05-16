"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown lifecycle."""
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    from app.api.v1 import (
        admin,
        allocation,
        auth,
        candidates,
        matching,
        notifications,
        opportunities,
    )

    prefix = settings.API_V1_PREFIX
    app.include_router(auth.router, prefix=prefix)
    app.include_router(candidates.router, prefix=prefix)
    app.include_router(opportunities.router, prefix=prefix)
    app.include_router(matching.router, prefix=prefix)
    app.include_router(allocation.router, prefix=prefix)
    app.include_router(notifications.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)

    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
