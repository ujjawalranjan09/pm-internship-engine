"""
Model Registry – Versioned Model Management
=============================================

Manages model versions, metadata, and lifecycle for the ML ranking
models. Provides versioning, A/B comparison, rollback, and
integration with MLflow for experiment tracking.

Models are stored as:
    models/<model_name>/<version>/
        model.bin          – Serialized model weights
        metadata.json      – Training config, metrics, feature names
        metrics.json       – Evaluation metrics on holdout set
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ModelVersion:
    """Metadata for a single model version."""

    model_name: str
    version: str
    created_at: str
    status: str = "registered"  # registered, staging, production, archived
    training_config: dict[str, Any] = field(default_factory=dict)
    training_metrics: dict[str, Any] = field(default_factory=dict)
    evaluation_metrics: dict[str, Any] = field(default_factory=dict)
    feature_names: list[str] = field(default_factory=list)
    description: str = ""
    tags: list[str] = field(default_factory=list)
    artifact_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "version": self.version,
            "created_at": self.created_at,
            "status": self.status,
            "training_config": self.training_config,
            "training_metrics": self.training_metrics,
            "evaluation_metrics": self.evaluation_metrics,
            "feature_names": self.feature_names,
            "description": self.description,
            "tags": self.tags,
            "artifact_path": self.artifact_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelVersion:
        return cls(**data)


class ModelRegistry:
    """
    Registry for managing ML model versions.

    Stores model artifacts and metadata in a local directory structure.
    Supports promotion (staging → production), rollback, and comparison.

    Usage:
        registry = ModelRegistry("models/")
        registry.register("ranker", "v1.0", model_path, metrics)
        production_model = registry.get_production("ranker")
    """

    def __init__(self, base_path: str = "models") -> None:
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._registry_file = self._base_path / "registry.json"
        self._models: dict[str, dict[str, ModelVersion]] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load registry state from disk."""
        if self._registry_file.exists():
            try:
                with open(self._registry_file) as f:
                    data = json.load(f)
                for name, versions in data.items():
                    self._models[name] = {v: ModelVersion.from_dict(meta) for v, meta in versions.items()}
                logger.info(
                    "Loaded model registry: %d models, %d total versions",
                    len(self._models),
                    sum(len(v) for v in self._models.values()),
                )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to load registry: %s", e)
                self._models = {}

    def _save_registry(self) -> None:
        """Persist registry state to disk."""
        data = {name: {v: meta.to_dict() for v, meta in versions.items()} for name, versions in self._models.items()}
        with open(self._registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def register(
        self,
        model_name: str,
        version: str,
        model_path: str,
        training_config: dict[str, Any] | None = None,
        training_metrics: dict[str, Any] | None = None,
        evaluation_metrics: dict[str, Any] | None = None,
        feature_names: list[str] | None = None,
        description: str = "",
        tags: list[str] | None = None,
    ) -> ModelVersion:
        """
        Register a new model version.

        Copies the model artifact into the registry directory structure
        and records metadata.

        Args:
            model_name: Name of the model (e.g. "ranker", "reranker").
            version: Version string (e.g. "v1.0", "2024-01-15").
            model_path: Path to the model artifact file.
            training_config: Training hyperparameters.
            training_metrics: Metrics from training (loss, etc.).
            evaluation_metrics: Metrics from evaluation (NDCG, MAP, etc.).
            feature_names: Ordered list of feature names.
            description: Human-readable description.
            tags: Tags for filtering (e.g. ["production", "v2"]).

        Returns:
            ModelVersion with the registered metadata.
        """
        # Create artifact directory
        artifact_dir = self._base_path / model_name / version
        artifact_dir.mkdir(parents=True, exist_ok=True)

        # Copy model artifact
        artifact_dest = artifact_dir / "model.bin"
        if os.path.exists(model_path):
            shutil.copy2(model_path, artifact_dest)
        else:
            logger.warning("Model file not found at %s, registering metadata only", model_path)

        # Save metadata
        metadata = ModelVersion(
            model_name=model_name,
            version=version,
            created_at=datetime.now(UTC).isoformat(),
            status="registered",
            training_config=training_config or {},
            training_metrics=training_metrics or {},
            evaluation_metrics=evaluation_metrics or {},
            feature_names=feature_names or [],
            description=description,
            tags=tags or [],
            artifact_path=str(artifact_dest),
        )

        # Save metadata file
        meta_path = artifact_dir / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        # Update registry
        if model_name not in self._models:
            self._models[model_name] = {}
        self._models[model_name][version] = metadata
        self._save_registry()

        logger.info("Registered model %s/%s at %s", model_name, version, artifact_dest)
        return metadata

    def get(self, model_name: str, version: str) -> ModelVersion | None:
        """Get metadata for a specific model version."""
        return self._models.get(model_name, {}).get(version)

    def get_latest(self, model_name: str) -> ModelVersion | None:
        """Get the latest registered version of a model."""
        versions = self._models.get(model_name, {})
        if not versions:
            return None
        # Sort by created_at descending
        sorted_versions = sorted(
            versions.values(),
            key=lambda v: v.created_at,
            reverse=True,
        )
        return sorted_versions[0]

    def get_production(self, model_name: str) -> ModelVersion | None:
        """Get the current production version of a model."""
        versions = self._models.get(model_name, {})
        for v in versions.values():
            if v.status == "production":
                return v
        return None

    def get_staging(self, model_name: str) -> ModelVersion | None:
        """Get the current staging version of a model."""
        versions = self._models.get(model_name, {})
        for v in versions.values():
            if v.status == "staging":
                return v
        return None

    def list_versions(self, model_name: str) -> list[ModelVersion]:
        """List all versions of a model, newest first."""
        versions = self._models.get(model_name, {})
        return sorted(
            versions.values(),
            key=lambda v: v.created_at,
            reverse=True,
        )

    def list_models(self) -> list[str]:
        """List all registered model names."""
        return list(self._models.keys())

    def promote(self, model_name: str, version: str, target_status: str) -> bool:
        """
        Promote a model version to a new status.

        Common transitions:
            registered → staging
            staging → production
            production → archived

        When promoting to production, the current production model
        is automatically moved to archived.
        """
        mv = self.get(model_name, version)
        if mv is None:
            logger.error("Model %s/%s not found", model_name, version)
            return False

        # Archive current production model if promoting to production
        if target_status == "production":
            current_prod = self.get_production(model_name)
            if current_prod and current_prod.version != version:
                current_prod.status = "archived"
                logger.info(
                    "Archived previous production model %s/%s",
                    model_name,
                    current_prod.version,
                )

        old_status = mv.status
        mv.status = target_status
        self._save_registry()

        logger.info(
            "Promoted %s/%s: %s → %s",
            model_name,
            version,
            old_status,
            target_status,
        )
        return True

    def rollback(self, model_name: str) -> ModelVersion | None:
        """
        Rollback to the previous production model.

        Finds the most recent archived version and promotes it to
        production.
        """
        versions = self._models.get(model_name, {})
        archived = sorted(
            [v for v in versions.values() if v.status == "archived"],
            key=lambda v: v.created_at,
            reverse=True,
        )

        if not archived:
            logger.error("No archived version available for rollback of %s", model_name)
            return None

        target = archived[0]
        self.promote(model_name, target.version, "production")
        logger.info("Rolled back %s to version %s", model_name, target.version)
        return target

    def compare(
        self,
        model_name: str,
        version_a: str,
        version_b: str,
    ) -> dict[str, Any]:
        """
        Compare two model versions.

        Returns a dict with metric differences and the better version
        for each metric.
        """
        mv_a = self.get(model_name, version_a)
        mv_b = self.get(model_name, version_b)

        if not mv_a or not mv_b:
            return {"error": "One or both versions not found"}

        comparison = {
            "model_name": model_name,
            "version_a": version_a,
            "version_b": version_b,
            "metrics_comparison": {},
            "config_diff": {},
        }

        # Compare evaluation metrics
        all_metrics = set(mv_a.evaluation_metrics.keys()) | set(mv_b.evaluation_metrics.keys())
        for metric in all_metrics:
            val_a = mv_a.evaluation_metrics.get(metric)
            val_b = mv_b.evaluation_metrics.get(metric)

            if val_a is not None and val_b is not None:
                diff = val_b - val_a
                better = version_b if diff > 0 else version_a if diff < 0 else "tie"
                comparison["metrics_comparison"][metric] = {
                    "version_a": val_a,
                    "version_b": val_b,
                    "difference": diff,
                    "better": better,
                }

        return comparison

    def delete(self, model_name: str, version: str) -> bool:
        """Delete a model version and its artifacts."""
        mv = self.get(model_name, version)
        if mv is None:
            return False

        if mv.status == "production":
            logger.error("Cannot delete production model. Promote another version first.")
            return False

        # Remove artifact directory
        artifact_dir = self._base_path / model_name / version
        if artifact_dir.exists():
            shutil.rmtree(artifact_dir)

        # Remove from registry
        del self._models[model_name][version]
        if not self._models[model_name]:
            del self._models[model_name]

        self._save_registry()
        logger.info("Deleted model %s/%s", model_name, version)
        return True
