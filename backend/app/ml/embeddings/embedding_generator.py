"""
Embedding Generator – Dense Vector Representations
====================================================

Uses sentence-transformers to generate dense embeddings for
candidate profiles and opportunity descriptions. These embeddings
power the semantic similarity stage of the matching pipeline.

Model: defaults to all-MiniLM-L6-v2 (384-dim, fast, good quality).
Can be swapped via config for larger models when quality matters more
than latency.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates dense vector embeddings using sentence-transformers.

    The model is loaded lazily on first use to avoid import-time
    overhead. Supports batch encoding for efficiency.

    Usage:
        gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        vectors = gen.encode(["python developer", "data scientist"])
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        batch_size: int = 64,
        show_progress: bool = False,
        normalize: bool = True,
    ) -> None:
        """
        Initialise the embedding generator.

        Args:
            model_name: HuggingFace model name or local path.
            device: torch device ("cpu", "cuda", "mps"). Auto-detected if None.
            batch_size: Number of texts per forward pass.
            show_progress: Show tqdm progress bar during encode.
            normalize: L2-normalize output vectors.
        """
        self._model_name = model_name
        self._device = device
        self._batch_size = batch_size
        self._show_progress = show_progress
        self._normalize = normalize
        self._model = None
        self._dimension: int | None = None

    def _load_model(self):
        """Lazy-load the sentence-transformer model."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for embedding generation. "
                "Install it with: pip install sentence-transformers"
            ) from None

        logger.info("Loading sentence-transformer model: %s", self._model_name)
        self._model = SentenceTransformer(
            self._model_name,
            device=self._device,
        )
        # Probe dimensionality
        probe = self._model.encode(["test"], show_progress_bar=False)
        self._dimension = probe.shape[1]
        logger.info("Model loaded. Embedding dimension: %d", self._dimension)

    @property
    def dimension(self) -> int:
        """Return the embedding dimensionality."""
        self._load_model()
        return self._dimension  # type: ignore[return-value]

    def encode(
        self,
        texts: list[str],
        batch_size: int | None = None,
    ) -> np.ndarray:
        """
        Encode a list of texts into dense embeddings.

        Args:
            texts: List of strings to encode.
            batch_size: Override default batch size.

        Returns:
            numpy array of shape (len(texts), dimension).
        """
        self._load_model()

        if not texts:
            return np.zeros((0, self._dimension), dtype=np.float32)

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size or self._batch_size,
            show_progress_bar=self._show_progress,
            normalize_embeddings=self._normalize,
            convert_to_numpy=True,
        )

        return embeddings.astype(np.float32)

    def encode_candidates(
        self,
        candidates: list[dict],
        text_fields: list[str] | None = None,
    ) -> np.ndarray:
        """
        Encode candidate profiles into embeddings.

        Concatenates specified fields (default: skills + education)
        into a single text, then encodes.
        """
        fields = text_fields or ["skills", "education"]
        texts = []
        for cand in candidates:
            parts = []
            for field_name in fields:
                value = cand.get(field_name)
                if isinstance(value, list):
                    parts.append(" ".join(str(v) for v in value))
                elif isinstance(value, dict):
                    parts.append(" ".join(str(v) for v in value.values()))
                elif value:
                    parts.append(str(value))
            texts.append(" ".join(parts))

        return self.encode(texts)

    def encode_opportunities(
        self,
        opportunities: list[dict],
        text_fields: list[str] | None = None,
    ) -> np.ndarray:
        """
        Encode opportunity listings into embeddings.

        Concatenates specified fields (default: title + description +
        required_skills + sector) into a single text, then encodes.
        """
        fields = text_fields or ["title", "description", "required_skills", "sector"]
        texts = []
        for opp in opportunities:
            parts = []
            for field_name in fields:
                value = opp.get(field_name)
                if isinstance(value, list):
                    parts.append(" ".join(str(v) for v in value))
                elif isinstance(value, dict):
                    parts.append(" ".join(str(v) for v in value.values()))
                elif value:
                    parts.append(str(value))
            texts.append(" ".join(parts))

        return self.encode(texts)

    def similarity_matrix(
        self,
        embeddings_a: np.ndarray,
        embeddings_b: np.ndarray,
    ) -> np.ndarray:
        """
        Compute pairwise cosine similarity between two sets of embeddings.

        Returns matrix of shape (len(a), len(b)) with values in [-1, 1].
        If embeddings are L2-normalised, this is just the dot product.
        """
        if embeddings_a.size == 0 or embeddings_b.size == 0:
            return np.zeros((embeddings_a.shape[0], embeddings_b.shape[0]), dtype=np.float32)

        # If already normalised, dot product = cosine similarity
        return (embeddings_a @ embeddings_b.T).astype(np.float32)
