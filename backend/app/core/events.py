from typing import Any, Coroutine
from collections.abc import Callable
import logging

logger = logging.getLogger(__name__)

EventHandler = Callable[..., Coroutine[Any, Any, Any]]

_startup_handlers: list[EventHandler] = []
_shutdown_handlers: list[EventHandler] = []


def on_startup(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    _startup_handlers.append(func)
    return func


def on_shutdown(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    _shutdown_handlers.append(func)
    return func


async def startup_event() -> None:
    for handler in _startup_handlers:
        await handler()


async def shutdown_event() -> None:
    for handler in _shutdown_handlers:
        await handler()
