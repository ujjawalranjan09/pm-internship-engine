"""
Text Processor – NLP Utilities for Matching
============================================

Provides text cleaning, tokenisation, keyword extraction, and
TF-IDF-based similarity scoring for candidate profiles and
opportunity descriptions.
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter

logger = logging.getLogger(__name__)

# Common English + Hindi-English stop words relevant to the domain
_STOP_WORDS: set[str] = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "used",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "as",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "out",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "because",
    "but",
    "and",
    "or",
    "if",
    "while",
    "about",
    "up",
    "down",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "he",
    "him",
    "his",
    "she",
    "her",
    "they",
    "them",
    "their",
    "what",
    "which",
    "who",
    "whom",
    "am",
    "also",
    "well",
    "like",
    "etc",
    "experience",
    "working",
    "work",
    "knowledge",
    "skills",
    "ability",
}

# Normalisation map for common abbreviations and variants
_NORMALISATION_MAP: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "db": "database",
    "be": "backend",
    "fe": "frontend",
    "fs": "fullstack",
    "devops": "dev ops",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "k8s": "kubernetes",
}


class TextProcessor:
    """
    Text processing utilities for the matching pipeline.

    Provides:
        - Text cleaning and normalisation
        - Tokenisation with stop-word removal
        - Keyword extraction (TF-IDF-like)
        - Text similarity (Jaccard, cosine, overlap coefficient)
    """

    def __init__(
        self,
        stop_words: set[str] | None = None,
        normalisation_map: dict[str, str] | None = None,
    ) -> None:
        self._stop_words = stop_words or _STOP_WORDS
        self._normalisation = normalisation_map or _NORMALISATION_MAP

    def clean(self, text: str) -> str:
        """
        Clean and normalise text.

        - Lowercase
        - Remove URLs, emails, phone numbers
        - Normalise whitespace
        - Apply abbreviation expansion
        """
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"\S+@\S+\.\S+", " ", text)
        text = re.sub(r"\+?\d[\d\s\-]{7,}", " ", text)
        text = re.sub(r"[^\w\s\-\+#\.]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        for abbr, expansion in self._normalisation.items():
            text = re.sub(rf"\b{re.escape(abbr)}\b", expansion, text)

        return text

    def tokenize(self, text: str, remove_stopwords: bool = True) -> list[str]:
        """
        Tokenise text into cleaned tokens.

        Optionally removes stop words and very short tokens.
        """
        cleaned = self.clean(text)
        tokens = cleaned.split()

        if remove_stopwords:
            tokens = [t for t in tokens if t not in self._stop_words and len(t) > 1]

        return tokens

    def extract_keywords(self, text: str, top_k: int = 20) -> list[tuple[str, float]]:
        """
        Extract keywords from text using a TF-like scoring.

        Returns list of (keyword, score) sorted by score descending.
        Multi-word phrases (bigrams) are also considered.
        """
        tokens = self.tokenize(text)
        if not tokens:
            return []

        # Unigram frequencies
        counter = Counter(tokens)
        total = len(tokens)

        keywords: dict[str, float] = {}
        for word, count in counter.items():
            keywords[word] = count / total

        # Bigrams
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i + 1]}"
            keywords[bigram] = keywords.get(bigram, 0) + 0.5 / total

        sorted_kw = sorted(keywords.items(), key=lambda x: -x[1])
        return sorted_kw[:top_k]

    def jaccard_similarity(self, text_a: str, text_b: str) -> float:
        """Token-level Jaccard similarity between two texts."""
        tokens_a = set(self.tokenize(text_a))
        tokens_b = set(self.tokenize(text_b))

        if not tokens_a and not tokens_b:
            return 0.0

        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b

        return len(intersection) / len(union) if union else 0.0

    def cosine_similarity(self, text_a: str, text_b: str) -> float:
        """
        Token-level cosine similarity using term frequency vectors.

        More forgiving than Jaccard for documents of different lengths.
        """
        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        freq_a = Counter(tokens_a)
        freq_b = Counter(tokens_b)

        all_tokens = set(freq_a.keys()) | set(freq_b.keys())

        dot_product = sum(freq_a.get(t, 0) * freq_b.get(t, 0) for t in all_tokens)
        norm_a = math.sqrt(sum(v**2 for v in freq_a.values()))
        norm_b = math.sqrt(sum(v**2 for v in freq_b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def overlap_coefficient(self, text_a: str, text_b: str) -> float:
        """
        Overlap coefficient: |A ∩ B| / min(|A|, |B|).

        Useful when one text is much shorter than the other
        (e.g. a skill list vs a long job description).
        """
        tokens_a = set(self.tokenize(text_a))
        tokens_b = set(self.tokenize(text_b))

        if not tokens_a or not tokens_b:
            return 0.0

        intersection = tokens_a & tokens_b
        min_size = min(len(tokens_a), len(tokens_b))

        return len(intersection) / min_size if min_size > 0 else 0.0

    def compute_similarity(
        self,
        text_a: str,
        text_b: str,
        method: str = "cosine",
    ) -> float:
        """
        Compute text similarity using the specified method.

        Methods: "jaccard", "cosine", "overlap"
        """
        methods = {
            "jaccard": self.jaccard_similarity,
            "cosine": self.cosine_similarity,
            "overlap": self.overlap_coefficient,
        }
        fn = methods.get(method)
        if fn is None:
            raise ValueError(f"Unknown similarity method: {method!r}. Choose from {list(methods)}")
        return fn(text_a, text_b)

    def build_skill_text(self, skills: list[str], education: dict | None = None) -> str:
        """
        Build a combined text representation from skills and education.

        Useful for generating a single text blob for embedding or
        keyword-based matching.
        """
        parts = list(skills)
        if education:
            if education.get("field"):
                parts.append(education["field"])
            if education.get("level"):
                parts.append(education["level"])
            if education.get("institution"):
                parts.append(education["institution"])
        return " ".join(parts)
