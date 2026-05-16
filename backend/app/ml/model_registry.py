"""Central registry for ML models loaded at runtime."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Thread-safe in-memory model registry."""

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def register(self, name: str, model: Any, metadata: dict[str, Any] | None = None) -> None:
        self._models[name] = model
        self._metadata[name] = metadata or {}
        logger.info("Registered model '%s'", name)

    def get(self, name: str) -> Any:
        if name not in self._models:
            raise KeyError(f"Model '{name}' not found in registry")
        return self._models[name]

    def list_models(self) -> list[str]:
        return list(self._models.keys())

    def unregister(self, name: str) -> None:
        self._models.pop(name, None)
        self._metadata.pop(name, None)

    def get_metadata(self, name: str) -> dict[str, Any]:
        return self._metadata.get(name, {})


registry = ModelRegistry()
