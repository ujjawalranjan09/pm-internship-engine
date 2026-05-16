from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    admin,
    allocation,
    auth,
    candidates,
    matching,
    notifications,
    opportunities,
)
from app.core.config import settings
from app.core.database import Base, engine
from app.core.events import shutdown_handler, startup_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    await startup_handler()
    yield
    await shutdown_handler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])
app.include_router(opportunities.router, prefix="/api/v1/opportunities", tags=["opportunities"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["matching"])
app.include_router(allocation.router, prefix="/api/v1/allocation", tags=["allocation"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {"status": "healthy", "version": settings.VERSION}
