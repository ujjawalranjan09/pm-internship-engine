import logging
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)

StartupHandler = Callable[[], Coroutine[Any, Any, None]]
ShutdownHandler = Callable[[], Coroutine[Any, Any, None]]

_startup_handlers: list[StartupHandler] = []
_shutdown_handlers: list[ShutdownHandler] = []


def on_startup(func: StartupHandler) -> StartupHandler:
    _startup_handlers.append(func)
    return func


def on_shutdown(func: ShutdownHandler) -> ShutdownHandler:
    _shutdown_handlers.append(func)
    return func


async def startup_handler() -> None:
    for handler in _startup_handlers:
        await handler()


async def shutdown_handler() -> None:
    for handler in _shutdown_handlers:
        await handler()

# Event names
EVENT_ALLOCATION_COMPLETE = "allocation_complete"
EVENT_MATCHING_COMPLETE = "matching_complete"
EVENT_PROFILE_UPDATED = "profile_updated"

class EventBus:
    """Minimal event bus for internal notifications."""
    async def publish(self, event_name: str, data: Any) -> None:
        logger.info("Event published: %s", event_name)

event_bus = EventBus()
