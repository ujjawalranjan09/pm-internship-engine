"""Custom exception classes and FastAPI exception handlers."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):  # noqa: N818
    """Base application exception."""

    def __init__(self, detail: str, status_code: int = 400) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404)


class DuplicateException(AppException):
    """Duplicate resource conflict."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail=detail, status_code=409)


class ForbiddenException(AppException):
    """Insufficient permissions."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail=detail, status_code=403)


class ValidationException(AppException):
    """Validation error."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(detail=detail, status_code=422)


class AllocationException(AppException):
    """Allocation process error."""

    def __init__(self, detail: str = "Allocation failed") -> None:
        super().__init__(detail=detail, status_code=500)


class MatchingException(AppException):
    """Matching process error."""

    def __init__(self, detail: str = "Matching failed") -> None:
        super().__init__(detail=detail, status_code=500)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException on %s %s: %s", request.method, request.url.path, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "type": "InternalServerError"},
        )
