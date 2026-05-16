"""In-memory event bus for prototype pub/sub messaging."""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    """Simple async in-memory publish/subscribe event bus."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., Coroutine]]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[..., Coroutine]) -> None:
        """Register an async handler for an event type."""
        self._subscribers[event_type].append(handler)
        logger.debug("Subscribed %s to event '%s'", handler.__name__, event_type)

    def unsubscribe(self, event_type: str, handler: Callable[..., Coroutine]) -> None:
        """Remove a handler from an event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event_type: str, data: Any = None) -> None:
        """Publish an event to all registered handlers."""
        handlers = self._subscribers.get(event_type, [])
        if not handlers:
            logger.debug("No handlers for event '%s'", event_type)
            return
        tasks = [asyncio.create_task(h(data)) for h in handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for handler, result in zip(handlers, results, strict=False):
            if isinstance(result, Exception):
                logger.error(
                    "Handler %s failed for event '%s': %s",
                    handler.__name__,
                    event_type,
                    result,
                )


event_bus = EventBus()

# Event type constants
EVENT_ALLOCATION_COMPLETE = "allocation_complete"
EVENT_CANDIDATE_REGISTERED = "candidate_registered"
EVENT_MATCHING_COMPLETE = "matching_complete"
EVENT_NOTIFICATION_SENT = "notification_sent"
EVENT_PROFILE_UPDATED = "profile_updated"
