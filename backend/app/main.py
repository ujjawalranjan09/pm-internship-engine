from typing import Any
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.events import startup_event, shutdown_event
from app.api.v1 import router as api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    await startup_event()
    yield
    await shutdown_event()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

event_handlers: dict[str, Any] = {}
webhook_handlers: dict[str, Any] = {}

async def _on_allocation_complete(data: dict[str, Any]) -> None:
    pass

async def _on_candidate_registered(data: dict[str, Any]) -> None:
    pass

async def health_check() -> dict[str, Any]:
    return {"status": "ok", "version": settings.VERSION}

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
