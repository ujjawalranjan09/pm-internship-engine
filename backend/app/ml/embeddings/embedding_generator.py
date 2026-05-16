"""Sentence-transformer embedding generation with caching."""

import hashlib
import logging
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingGenerator:
    """Wraps a SentenceTransformer model and provides caching."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name: str = model_name or settings.EMBEDDING_MODEL
        self.model: SentenceTransformer | None = None
        self._cache: dict[str, list[float]] = {}

    def _load_model(self) -> None:
        if self.model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            self.model = SentenceTransformer(self.model_name)

    def _cache_key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def embed(self, text: str) -> list[float]:
        """Return a vector embedding for *text*, using cache when possible."""
        key = self._cache_key(text)
        if key in self._cache:
            return self._cache[key]
        self._load_model()
        assert self.model is not None
        vector: np.ndarray[Any, Any] = self.model.encode(text, convert_to_numpy=True)
        result = vector.tolist()
        self._cache[key] = result
        return result

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch-embed a list of texts."""
        self._load_model()
        assert self.model is not None
        vectors: np.ndarray[Any, Any] = self.model.encode(texts, convert_to_numpy=True, batch_size=64)
        return [v.tolist() for v in vectors]

    def clear_cache(self) -> None:
        self._cache.clear()


_generator: EmbeddingGenerator | None = None


def get_embedding_generator() -> EmbeddingGenerator:
    global _generator
    if _generator is None:
        _generator = EmbeddingGenerator()
    return _generator
