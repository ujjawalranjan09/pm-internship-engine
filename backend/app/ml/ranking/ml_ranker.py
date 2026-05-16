"""
ML Ranker – LightGBM Learned Ranking (Stage B)
================================================

Trains and applies a LightGBM ranker (LambdaRank objective) for
candidate-opportunity matching. The model learns to optimise NDCG
directly, producing scores that are better calibrated than the
heuristic baseline.

Supports:
    - Training from labelled (query, candidate, relevance) data
    - Prediction with feature importance explanation
    - Model persistence via joblib
    - MLflow experiment tracking integration
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    import lightgbm as lgb
except ImportError:
    lgb = None  # type: ignore[assignment]
    logger.warning("lightgbm not installed – MLRanker will fall back to heuristic-only mode")


@dataclass
class TrainingConfig:
    """Hyperparameters for LightGBM ranker training."""
    objective: str = "lambdarank"
    metric: str = "ndcg"
    ndcg_eval_at: List[int] = field(default_factory=lambda: [5, 10, 20])
    num_leaves: int = 63
    max_depth: int = -1
    learning_rate: float = 0.05
    n_estimators: int = 500
    min_child_samples: int = 20
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    reg_alpha: float = 0.1
    reg_lambda: float = 0.1
    early_stopping_rounds: int = 30
    verbose: int = -1
    random_state: int = 42


@dataclass
class RankerPrediction:
    """Result of ranking with the ML model."""
    candidate_id: str
    opportunity_id: str
    score: float
    feature_contributions: Dict[str, float] = field(default_factory=dict)
    rank: int = 0


class MLRanker:
    """
    LightGBM-based learning-to-rank model.

    Wraps LightGBM's LambdaRank objective to learn a ranking function
    from historical match data. Falls back gracefully when lightgbm
    is not installed or no trained model is available.
    """

    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        model_path: Optional[str] = None,
    ) -> None:
        self.config = config or TrainingConfig()
        self._model: Optional[Any] = None
        self._feature_names: Optional[List[str]] = None
        self._model_path = model_path

        if model_path and os.path.exists(model_path):
            self.load(model_path)

    @property
    def is_trained(self) -> bool:
        """Whether a trained model is available."""
        return self._model is not None

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        query_groups: np.ndarray,
        feature_names: Optional[List[str]] = None,
        eval_X: Optional[np.ndarray] = None,
        eval_y: Optional[np.ndarray] = None,
        eval_query_groups: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Train the LightGBM ranker.

        Args:
            X: Feature matrix (n_samples, n_features).
            y: Relevance labels (n_samples,) – higher = more relevant.
            query_groups: Number of candidates per query (opportunity).
                e.g. [50, 50, 50] means 3 opportunities, each with 50 candidates.
            feature_names: Names for each feature column.
            eval_X: Evaluation feature matrix (optional).
            eval_y: Evaluation labels (optional).
            eval_query_groups: Evaluation query groups (optional).

        Returns:
            Training metrics dict.
        """
        if lgb is None:
            raise ImportError("lightgbm is required for training. pip install lightgbm")

        self._feature_names = feature_names

        params = {
            "objective": self.config.objective,
            "metric": self.config.metric,
            "ndcg_eval_at": self.config.ndcg_eval_at,
            "num_leaves": self.config.num_leaves,
            "max_depth": self.config.max_depth,
            "learning_rate": self.config.learning_rate,
            "min_child_samples": self.config.min_child_samples,
            "subsample": self.config.subsample,
            "colsample_bytree": self.config.colsample_bytree,
            "reg_alpha": self.config.reg_alpha,
            "reg_lambda": self.config.reg_lambda,
            "verbose": self.config.verbose,
            "seed": self.config.random_state,
        }

        train_data = lgb.Dataset(
            X, label=y, group=query_groups.tolist(),
            feature_name=feature_names or "auto",
        )

        valid_sets = [train_data]
        valid_names = ["train"]

        if eval_X is not None and eval_y is not None and eval_query_groups is not None:
            eval_data = lgb.Dataset(
                eval_X, label=eval_y, group=eval_query_groups.tolist(),
                feature_name=feature_names or "auto",
                reference=train_data,
            )
            valid_sets.append(eval_data)
            valid_names.append("eval")

        callbacks = [lgb.log_evaluation(period=50)]
        if self.config.early_stopping_rounds > 0 and len(valid_sets) > 1:
            callbacks.append(lgb.early_stopping(self.config.early_stopping_rounds))

        logger.info("Training LightGBM ranker: %d samples, %d features", X.shape[0], X.shape[1])
        start = time.time()

        self._model = lgb.train(
            params,
            train_data,
            num_boost_round=self.config.n_estimators,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=callbacks,
        )

        elapsed = time.time() - start
        metrics = {
            "training_time_seconds": elapsed,
            "best_iteration": self._model.best_iteration if hasattr(self._model, "best_iteration") else self.config.n_estimators,
            "num_samples": int(X.shape[0]),
            "num_features": int(X.shape[1]),
        }

        # Feature importance
        importance = self._model.feature_importance(importance_type="gain")
        names = feature_names or [f"f{i}" for i in range(X.shape[1])]
        metrics["feature_importance"] = dict(zip(names, importance.tolist()))

        logger.info("Training complete in %.1fs. Best iteration: %s", elapsed, metrics["best_iteration"])
        return metrics

    def predict(
        self,
        X: np.ndarray,
        candidate_ids: List[str],
        opportunity_id: str,
        top_k: Optional[int] = None,
    ) -> List[RankerPrediction]:
        """
        Score and rank candidates for an opportunity.

        Args:
            X: Feature matrix (n_candidates, n_features).
            candidate_ids: Candidate IDs corresponding to rows of X.
            opportunity_id: The opportunity being ranked for.
            top_k: Return only top-k results.

        Returns:
            List of RankerPrediction sorted by score descending.
        """
        if self._model is None:
            raise RuntimeError("No trained model. Call train() or load() first.")

        raw_scores = self._model.predict(X)

        # Normalise scores to [0, 1] via min-max
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s > min_s:
            scores = (raw_scores - min_s) / (max_s - min_s)
        else:
            scores = np.full_like(raw_scores, 0.5)

        predictions = []
        for i, (cid, score) in enumerate(zip(candidate_ids, scores)):
            contributions = {}
            if self._feature_names:
                # Approximate per-feature contribution using feature importance × value
                importance = self._model.feature_importance(importance_type="gain")
                total_imp = importance.sum()
                if total_imp > 0:
                    for fname, imp, val in zip(self._feature_names, importance, X[i]):
                        contributions[fname] = float(imp / total_imp * val)

            predictions.append(RankerPrediction(
                candidate_id=cid,
                opportunity_id=opportunity_id,
                score=float(score),
                feature_contributions=contributions,
            ))

        predictions.sort(key=lambda p: -p.score)
        for i, pred in enumerate(predictions):
            pred.rank = i + 1

        if top_k is not None:
            predictions = predictions[:top_k]

        return predictions

    def get_feature_importance(self, importance_type: str = "gain") -> Dict[str, float]:
        """Return feature importance as a dict."""
        if self._model is None:
            return {}

        imp = self._model.feature_importance(importance_type=importance_type)
        names = self._feature_names or [f"f{i}" for i in range(len(imp))]
        return dict(zip(names, imp.tolist()))

    def save(self, path: Optional[str] = None) -> str:
        """Save the model to disk."""
        save_path = path or self._model_path
        if not save_path:
            raise ValueError("No save path specified")

        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        if lgb is not None and self._model is not None:
            self._model.save_model(save_path)

        # Save metadata alongside
        meta_path = save_path + ".meta.json"
        meta = {
            "feature_names": self._feature_names,
            "config": {
                "objective": self.config.objective,
                "num_leaves": self.config.num_leaves,
                "learning_rate": self.config.learning_rate,
                "n_estimators": self.config.n_estimators,
            },
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        logger.info("Model saved to %s", save_path)
        return save_path

    def load(self, path: str) -> None:
        """Load a trained model from disk."""
        if lgb is None:
            raise ImportError("lightgbm is required to load models")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        self._model = lgb.Booster(model_file=path)
        self._model_path = path

        # Load metadata if available
        meta_path = path + ".meta.json"
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            self._feature_names = meta.get("feature_names")

        logger.info("Model loaded from %s", path)
