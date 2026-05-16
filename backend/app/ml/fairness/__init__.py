"""
Fairness Module
===============

Ensures equitable allocation across social categories, geographies,
and demographic groups. Includes metrics, policy enforcement, and
guardrails to prevent overcorrection.

Submodules:
    - fairness_metrics: Distribution and equity metrics
    - policy_engine: Configurable fairness policies
    - guardrails: Quality-fairness tradeoff monitoring
"""

from .fairness_metrics import FairnessMetrics
from .guardrails import FairnessGuardrails
from .policy_engine import PolicyEngine

__all__ = ["FairnessMetrics", "PolicyEngine", "FairnessGuardrails"]
