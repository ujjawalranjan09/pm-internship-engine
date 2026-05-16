"""
Model registry for versioning and managing ML models.
File-based storage for prototype; can be extended to MLflow.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_REGISTRY_PATH = "model_registry"


@dataclass
class ModelVersion:
    """Metadata for a registered model version."""
    name: str
    version: str
    stage: str = "development"  # development, staging, production, archived
    metrics: dict[str, float] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    path: str = ""
    description: str = ""
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelVersion:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ModelRegistry:
    """
    File-based model registry for versioning ML models.

    Stores model artifacts and metadata in a structured directory.
    """

    def __init__(self, registry_path: str = DEFAULT_REGISTRY_PATH):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self._index_file = self.registry_path / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load the model index from disk."""
        if self._index_file.exists():
            with open(self._index_file) as f:
                self._index: dict[str, list[dict]] = json.load(f)
        else:
            self._index = {}
            self._save_index()

    def _save_index(self) -> None:
        """Persist the model index to disk."""
        with open(self._index_file, "w") as f:
            json.dump(self._index, f, indent=2)

    def register_model(
        self,
        name: str,
        model: Any,
        metrics: dict[str, float] | None = None,
        params: dict[str, Any] | None = None,
        description: str = "",
        tags: dict[str, str] | None = None,
    ) -> ModelVersion:
        """
        Register a new model version.

        Args:
            name: Model name (e.g., 'ranker', 'embedder')
            model: The model object (must be picklable)
            metrics: Evaluation metrics (ndcg, map, etc.)
            params: Model hyperparameters
            description: Human-readable description
            tags: Key-value tags

        Returns:
            ModelVersion with assigned version number
        """
        if name not in self._index:
            self._index[name] = []

        # Auto-increment version
        existing_versions = [v["version"] for v in self._index[name]]
        if existing_versions:
            max_ver = max(int(v.split(".")[-1]) for v in existing_versions if v.startswith("v"))
            version = f"v{max_ver + 1}"
        else:
            version = "v1"

        # Create model directory
        model_dir = self.registry_path / name / version
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save model artifact
        model_path = model_dir / "model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # Create version metadata
        mv = ModelVersion(
            name=name,
            version=version,
            metrics=metrics or {},
            params=params or {},
            path=str(model_path),
            description=description,
            tags=tags or {},
        )

        # Save version metadata
        meta_path = model_dir / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(mv.to_dict(), f, indent=2)

        # Update index
        self._index[name].append(mv.to_dict())
        self._save_index()

        logger.info("Registered model %s %s at %s", name, version, model_path)
        return mv

    def load_model(self, name: str, version: str | None = None) -> Any:
        """
        Load a model by name and optional version.

        Args:
            name: Model name
            version: Specific version (loads latest if None)

        Returns:
            The deserialized model object
        """
        if name not in self._index or not self._index[name]:
            raise ValueError(f"No models registered for '{name}'")

        if version is None:
            # Load latest
            entry = self._index[name][-1]
        else:
            matches = [v for v in self._index[name] if v["version"] == version]
            if not matches:
                raise ValueError(f"Version {version} not found for model '{name}'")
            entry = matches[0]

        model_path = entry["path"]
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        logger.info("Loaded model %s %s", name, entry["version"])
        return model

    def get_best_model(self, name: str, metric: str = "ndcg_at_10") -> ModelVersion | None:
        """Get the model version with the best score on a given metric."""
        if name not in self._index or not self._index[name]:
            return None

        versions = self._index[name]
        best = max(
            versions,
            key=lambda v: v.get("metrics", {}).get(metric, 0.0),
        )
        return ModelVersion.from_dict(best)

    def compare_versions(self, name: str, v1: str, v2: str) -> dict[str, Any]:
        """Compare two model versions on metrics."""
        versions = {v["version"]: v for v in self._index.get(name, [])}
        if v1 not in versions or v2 not in versions:
            raise ValueError(f"Version not found: {v1} or {v2}")

        m1 = versions[v1].get("metrics", {})
        m2 = versions[v2].get("metrics", {})

        all_keys = set(m1.keys()) | set(m2.keys())
        comparison = {}
        for key in sorted(all_keys):
            val1 = m1.get(key, 0.0)
            val2 = m2.get(key, 0.0)
            comparison[key] = {
                v1: val1,
                v2: val2,
                "diff": val2 - val1,
                "improved": val2 > val1,
            }

        return comparison

    def promote_model(self, name: str, version: str, stage: str) -> ModelVersion:
        """
        Promote a model to a new stage (staging, production, archived).

        If promoting to production, demote current production model to staging.
        """
        if name not in self._index:
            raise ValueError(f"Model '{name}' not found")

        # Demote current production model if promoting to production
        if stage == "production":
            for entry in self._index[name]:
                if entry["stage"] == "production":
                    entry["stage"] = "staging"
                    logger.info("Demoted %s %s to staging", name, entry["version"])

        # Promote target
        for entry in self._index[name]:
            if entry["version"] == version:
                entry["stage"] = stage
                self._save_index()

                # Update metadata file
                meta_path = Path(entry["path"]).parent / "metadata.json"
                mv = ModelVersion.from_dict(entry)
                with open(meta_path, "w") as f:
                    json.dump(mv.to_dict(), f, indent=2)

                logger.info("Promoted %s %s to %s", name, version, stage)
                return mv

        raise ValueError(f"Version {version} not found for model '{name}'")

    def list_models(self) -> dict[str, list[str]]:
        """List all registered models and their versions."""
        return {
            name: [v["version"] for v in versions]
            for name, versions in self._index.items()
        }

    def list_versions(self, name: str) -> list[ModelVersion]:
        """List all versions of a model."""
        return [ModelVersion.from_dict(v) for v in self._index.get(name, [])]
