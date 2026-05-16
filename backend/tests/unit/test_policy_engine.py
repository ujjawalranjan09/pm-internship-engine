"""Tests for the policy engine module."""

import numpy as np
import pandas as pd

from app.ml.fairness.policy_engine import (
    PolicyConfig,
    apply_policy,
    load_policy,
)


class TestPolicyConfig:
    """Tests for PolicyConfig dataclass."""

    def test_defaults(self):
        config = PolicyConfig()
        assert config.district_target_fraction == 0.1
        assert config.category_balance_factor == 0.03
        assert config.rural_preference_factor == 0.04
        assert config.female_target_fraction == 0.33
        assert config.max_total_adjustment == 0.15

    def test_custom_values(self):
        config = PolicyConfig(
            district_target_fraction=0.2,
            rural_preference_factor=0.1,
        )
        assert config.district_target_fraction == 0.2
        assert config.rural_preference_factor == 0.1


class TestLoadPolicy:
    """Tests for load_policy function."""

    def test_load_from_dict(self):
        config_dict = {
            "district_target_fraction": 0.15,
            "rural_preference_factor": 0.08,
            "enable_female_uplift": False,
        }
        config = load_policy(config_dict)
        assert config.district_target_fraction == 0.15
        assert config.rural_preference_factor == 0.08
        assert config.enable_female_uplift is False

    def test_load_empty_dict(self):
        config = load_policy({})
        assert isinstance(config, PolicyConfig)

    def test_load_ignores_unknown_keys(self):
        config_dict = {"unknown_key": 999, "district_target_fraction": 0.2}
        config = load_policy(config_dict)
        assert config.district_target_fraction == 0.2


class TestApplyPolicy:
    """Tests for apply_policy function."""

    def test_basic_reranking(self):
        scores = np.array([0.8, 0.7, 0.6, 0.5])
        candidates = pd.DataFrame(
            {
                "candidate_id": [1, 2, 3, 4],
                "district": ["A", "B", "A", "C"],
                "category": ["general", "sc", "obc", "st"],
                "is_rural": [False, True, True, False],
                "gender": ["male", "female", "male", "female"],
                "previous_allocations": [0, 0, 0, 0],
            }
        )
        config = PolicyConfig(
            enable_district_uplift=True,
            enable_category_balancing=True,
            enable_rural_preference=True,
            enable_female_uplift=True,
            enable_repeat_penalty=False,
        )
        result = apply_policy(scores, candidates, config)
        # Scores should still be valid
        assert len(result) == 4
        assert all(0 <= s <= 1.5 for s in result)

    def test_repeat_penalty(self):
        scores = np.array([0.8, 0.7])
        candidates = pd.DataFrame(
            {
                "candidate_id": [1, 2],
                "district": ["A", "A"],
                "category": ["general", "general"],
                "is_rural": [False, False],
                "gender": ["male", "male"],
                "previous_allocations": [0, 3],
            }
        )
        config = PolicyConfig(
            enable_repeat_penalty=True,
            enable_district_uplift=False,
            enable_category_balancing=False,
            enable_rural_preference=False,
            enable_female_uplift=False,
        )
        result = apply_policy(scores, candidates, config)
        # Candidate 2 should be penalized
        assert result[1] < scores[1]

    def test_scores_stay_non_negative(self):
        scores = np.array([0.05, 0.1])
        candidates = pd.DataFrame(
            {
                "candidate_id": [1, 2],
                "district": ["A", "A"],
                "category": ["general", "general"],
                "is_rural": [False, False],
                "gender": ["male", "male"],
                "previous_allocations": [5, 5],  # Heavy penalty
            }
        )
        config = PolicyConfig(enable_repeat_penalty=True)
        result = apply_policy(scores, candidates, config)
        assert all(s >= 0 for s in result)
