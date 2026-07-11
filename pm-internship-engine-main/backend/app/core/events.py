"""Event bus and event constants for the application."""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Event names
EVENT_ALLOCATION_COMPLETE = "allocation.complete"
EVENT_MATCHING_COMPLETE = "matching.complete"
EVENT_PROFILE_UPDATED = "profile.updated"


class EventBus:
    """Simple async event bus for decoupled event handling."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[Any], Coroutine[Any, Any, None]]]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        """Subscribe a handler to an event."""
        self._subscribers[event].append(handler)
        logger.debug("Subscribed handler to event: %s", event)

    def unsubscribe(self, event: str, handler: Callable[[Any], Coroutine[Any, Any, None]]) -> None:
        """Unsubscribe a handler from an event."""
        if event in self._subscribers:
            self._subscribers[event].remove(handler)
            logger.debug("Unsubscribed handler from event: %s", event)

    async def publish(self, event: str, data: Any) -> None:
        """Publish an event to all subscribers."""
        if event not in self._subscribers:
            return

        logger.debug("Publishing event %s to %d subscribers", event, len(self._subscribers[event]))
        tasks = [handler(data) for handler in self._subscribers[event]]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Global event bus instance
event_bus = EventBus()


# Startup/shutdown handlers (for backward compatibility)
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