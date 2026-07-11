"""
Embeddings Module
=================

Generates and manages dense vector embeddings for candidates and
opportunities using sentence-transformers. Stores vectors in a
simple in-memory / file-backed vector store for similarity search.
"""

from .embedding_generator import EmbeddingGenerator
from .vector_store import VectorStore

__all__ = ["EmbeddingGenerator", "VectorStore"]
