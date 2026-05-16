"""PM Internship Smart Allocation Engine - FastAPI Application.

AI-based system for matching candidates to internship opportunities
with fairness-aware allocation using constrained optimization.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.events import EVENT_ALLOCATION_COMPLETE, EVENT_CANDIDATE_REGISTERED, event_bus
from app.core.exceptions import register_exception_handlers
from app.models.base import Base

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def _on_allocation_complete(data: dict) -> None:
    """Handle allocation completion events."""
    logger.info("Allocation completed: %s", data)


async def _on_candidate_registered(data: dict) -> None:
    """Handle new candidate registration events."""
    logger.info("Candidate registered: %s", data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Register event handlers
    event_bus.subscribe(EVENT_ALLOCATION_COMPLETE, _on_allocation_complete)
    event_bus.subscribe(EVENT_CANDIDATE_REGISTERED, _on_candidate_registered)

    yield

    # Cleanup
    logger.info("Shutting down %s", settings.APP_NAME)
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Based Smart Allocation Engine for PM Internship Scheme. "
        "Matches candidates to internship opportunities using multi-stage "
        "matching with fairness-aware constrained optimization."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# API routes
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
