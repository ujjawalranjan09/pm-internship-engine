"""
Vector Store – In-Memory Similarity Search
============================================

A lightweight, file-backed vector store for storing and retrieving
dense embeddings by ID. Supports approximate nearest-neighbour
search via brute-force (sufficient for < 100k vectors).

For production scale, swap with FAISS, Annoy, or a managed vector DB.
"""

from __future__ import annotations

import json
import logging
import os

import numpy as np

logger = logging.getLogger(__name__)


class VectorStore:
    """
    In-memory vector store with optional file persistence.

    Each vector is keyed by an (entity_type, entity_id) pair so that
    candidates and opportunities can share the same store.

    Usage:
        store = VectorStore(dimension=384)
        store.add("candidate", 42, embedding_array)
        results = store.search(query_embedding, top_k=10)
    """

    def __init__(
        self,
        dimension: int = 384,
        persist_path: str | None = None,
    ) -> None:
        self._dimension = dimension
        self._persist_path = persist_path

        # Storage: list of (entity_type, entity_id) aligned with rows of _matrix
        self._keys: list[tuple[str, int]] = []
        self._matrix: np.ndarray | None = None

        if persist_path and os.path.exists(persist_path):
            self._load()

    @property
    def size(self) -> int:
        """Number of vectors currently stored."""
        return len(self._keys)

    @property
    def dimension(self) -> int:
        return self._dimension

    def add(
        self,
        entity_type: str,
        entity_id: int,
        embedding: np.ndarray,
    ) -> None:
        """
        Add or update a vector in the store.

        Args:
            entity_type: "candidate" or "opportunity".
            entity_id: Database ID of the entity.
            embedding: 1-D numpy array of shape (dimension,).
        """
        if embedding.shape != (self._dimension,):
            raise ValueError(f"Expected embedding of shape ({self._dimension},), got {embedding.shape}")

        key = (entity_type, entity_id)

        # Check if already exists → update in place
        try:
            idx = self._keys.index(key)
            self._matrix[idx] = embedding  # type: ignore[index]
            return
        except ValueError:
            pass

        self._keys.append(key)
        row = embedding.reshape(1, -1).astype(np.float32)

        if self._matrix is None:
            self._matrix = row
        else:
            self._matrix = np.vstack([self._matrix, row])

    def add_batch(
        self,
        entity_type: str,
        entity_ids: list[int],
        embeddings: np.ndarray,
    ) -> None:
        """
        Add multiple vectors at once.

        Args:
            entity_type: Common type for all entities.
            entity_ids: List of database IDs.
            embeddings: 2-D array of shape (n, dimension).
        """
        if embeddings.shape[0] != len(entity_ids):
            raise ValueError("Number of embeddings must match number of IDs")
        if embeddings.shape[1] != self._dimension:
            raise ValueError(f"Expected dimension {self._dimension}, got {embeddings.shape[1]}")

        for eid, emb in zip(entity_ids, embeddings, strict=False):
            self.add(entity_type, eid, emb)

    def get(self, entity_type: str, entity_id: int) -> np.ndarray | None:
        """Retrieve a single vector by key, or None if not found."""
        key = (entity_type, entity_id)
        try:
            idx = self._keys.index(key)
            return self._matrix[idx]  # type: ignore[index]
        except (ValueError, IndexError):
            return None

    def search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        entity_type: str | None = None,
        min_score: float = 0.0,
    ) -> list[tuple[str, int, float]]:
        """
        Find the top-k most similar vectors.

        Args:
            query: 1-D query embedding.
            top_k: Number of results to return.
            entity_type: Filter results to this type (None = all).
            min_score: Minimum cosine similarity threshold.

        Returns:
            List of (entity_type, entity_id, similarity_score) sorted
            by score descending.
        """
        if self._matrix is None or self.size == 0:
            return []

        if query.shape != (self._dimension,):
            raise ValueError(f"Query shape {query.shape} doesn't match dimension {self._dimension}")

        # Cosine similarity (vectors are assumed L2-normalised)
        scores = (self._matrix @ query.reshape(-1, 1)).flatten()

        # Apply entity type filter
        indices = np.arange(len(self._keys))
        if entity_type is not None:
            mask = np.array([k[0] == entity_type for k in self._keys])
            indices = indices[mask]
            scores = scores[mask]

        # Filter by min_score
        above_threshold = scores >= min_score
        indices = indices[above_threshold]
        scores = scores[above_threshold]

        # Top-k
        if len(scores) > top_k:
            top_indices = np.argpartition(scores, -top_k)[-top_k:]
            top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]
            indices = indices[top_indices]
            scores = scores[top_indices]
        else:
            order = np.argsort(scores)[::-1]
            indices = indices[order]
            scores = scores[order]

        results = []
        for idx, score in zip(indices, scores, strict=False):
            entity_type_val, entity_id = self._keys[idx]
            results.append((entity_type_val, entity_id, float(score)))

        return results

    def remove(self, entity_type: str, entity_id: int) -> bool:
        """Remove a vector from the store. Returns True if found."""
        key = (entity_type, entity_id)
        try:
            idx = self._keys.index(key)
            self._keys.pop(idx)
            if self._matrix is not None:
                self._matrix = np.delete(self._matrix, idx, axis=0)
                if self._matrix.shape[0] == 0:
                    self._matrix = None
            return True
        except ValueError:
            return False

    def clear(self) -> None:
        """Remove all vectors."""
        self._keys.clear()
        self._matrix = None

    def save(self, path: str | None = None) -> None:
        """Persist the store to disk."""
        save_path = path or self._persist_path
        if not save_path:
            raise ValueError("No persist_path configured")

        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        data = {
            "dimension": self._dimension,
            "keys": self._keys,
            "matrix": self._matrix.tolist() if self._matrix is not None else [],
        }
        with open(save_path, "w") as f:
            json.dump(data, f)
        logger.info("Vector store saved to %s (%d vectors)", save_path, self.size)

    def _load(self) -> None:
        """Load store from disk."""
        if not self._persist_path:
            return

        try:
            with open(self._persist_path) as f:
                data = json.load(f)

            self._dimension = data["dimension"]
            self._keys = [tuple(k) for k in data["keys"]]
            matrix_data = data.get("matrix", [])
            self._matrix = np.array(matrix_data, dtype=np.float32) if matrix_data else None
            logger.info(
                "Vector store loaded from %s (%d vectors)",
                self._persist_path,
                self.size,
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to load vector store from %s: %s", self._persist_path, e)
