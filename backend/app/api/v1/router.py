"""Aggregate v1 API router."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.matching import router as matching_router
from app.api.v1.allocation import router as allocation_router
from app.api.v1.admin import router as admin_router
from app.api.v1.notifications import router as notifications_router

v1_router = APIRouter()

v1_router.include_router(auth_router)
v1_router.include_router(candidates_router)
v1_router.include_router(opportunities_router)
v1_router.include_router(matching_router)
v1_router.include_router(allocation_router)
v1_router.include_router(admin_router)
v1_router.include_router(notifications_router)
