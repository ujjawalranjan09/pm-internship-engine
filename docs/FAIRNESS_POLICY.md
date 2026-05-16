# Fairness Policy Configuration Guide

## Overview

The Fairness Policy Engine controls how the system adjusts match scores to promote equitable access to internships. It balances **merit-based matching** (the best candidate for the job) with **equity-based adjustments** (ensuring historically disadvantaged groups have fair access).

The engine runs as part of **Stage 4** of the matching pipeline, applying additive score boosts that are bounded by quality guardrails.

```
┌──────────────────────────────────────────────────────────────────┐
│                    FAIRNESS POLICY ENGINE                        │
│                                                                  │
│   Raw Score ──▶ Policy Evaluation ──▶ Boost Calculation ──▶     │
│                                         Guardrails Check ──▶    │
│                                            Adjusted Score       │
│                                                                  │
│   Inputs:                  Outputs:                              │
│   - Candidate profile      - Adjusted match score               │
│   - Opportunity context    - Fairness breakdown                  │
│   - Policy configuration   - Audit log entry                    │
│   - Historical data        - Group fairness metrics             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Configuration Format

Fairness policies are stored as JSON in the `allocation_cycles.config` field. The policy engine reads this configuration at allocation time.

### Top-Level Structure

```json
{
  "fairness_policy": {
    "version": "1.0",
    "enabled": true,
    "quality_guardrails": { ... },
    "social_category_policy": { ... },
    "geographic_policy": { ... },
    "gender_policy": { ... },
    "repeat_participation_policy": { ... },
    "district_targets": { ... }
  }
}
```

### Complete Configuration Schema

```json
{
  "fairness_policy": {
    "version": "1.0",
    "enabled": true,

    "quality_guardrails": {
      "min_raw_score_threshold": 0.6,
      "max_total_adjustment": 0.15,
      "max_score_ceiling": 1.0,
      "preserve_top_rankings": true,
      "top_n_protected": 10
    },

    "social_category_policy": {
      "enabled": true,
      "boosts": {
        "sc": 0.15,
        "st": 0.15,
        "obc": 0.09,
        "ews": 0.075,
        "general": 0.0
      },
      "representation_targets": {
        "sc": 0.15,
        "st": 0.075,
        "obc": 0.27,
        "ews": 0.10,
        "general": 0.405
      }
    },

    "geographic_policy": {
      "enabled": true,
      "rural_boost": 0.10,
      "underserved_state_boost": 0.05,
      "underserved_states": [
        "bihar", "jharkhand", "chhattisgarh", "odisha",
        "madhya pradesh", "rajasthan", "uttar pradesh"
      ],
      "aspirational_district_boost": 0.08,
      "aspirational_districts": []
    },

    "gender_policy": {
      "enabled": true,
      "female_target_ratio": 0.40,
      "female_boost": 0.05,
      "non_binary_boost": 0.05,
      "apply_boost_below_target": true
    },

    "repeat_participation_policy": {
      "enabled": true,
      "prior_completion_penalty": -0.05,
      "prior_decline_penalty": -0.03,
      "max_prior_cycles": 2,
      "new_candidate_bonus": 0.03
    },

    "district_targets": {
      "enabled": false,
      "targets": {},
      "soft_target_weight": 0.5
    }
  }
}
```

---

## Social Category Balancing

### Background

India's reservation system ensures representation for Scheduled Castes (SC), Scheduled Tribes (ST), Other Backward Classes (OBC), and Economically Weaker Sections (EWS). The fairness engine translates these constitutional mandates into algorithmic boosts.

### Configuration

```json
{
  "social_category_policy": {
    "enabled": true,
    "boosts": {
      "sc": 0.15,
      "st": 0.15,
      "obc": 0.09,
      "ews": 0.075,
      "general": 0.0
    },
    "representation_targets": {
      "sc": 0.15,
      "st": 0.075,
      "obc": 0.27,
      "ews": 0.10,
      "general": 0.405
    }
  }
}
```

### How Boosts Work

```
Boost Calculation:
  category_boost = policy.boosts[candidate.social_category]

  SC candidate:  boost = 0.150
  ST candidate:  boost = 0.150
  OBC candidate: boost = 0.090
  EWS candidate: boost = 0.075
  General:       boost = 0.000
```

### Representation Targets

These are **soft targets** used for reporting and analytics, not hard constraints. After each allocation cycle, the system computes:

```
actual_representation[cat] = count(allocated[cat]) / total_allocated

gap[cat] = target[cat] - actual_representation[cat]

if gap > 0:
    → category is underrepresented
    → consider increasing boost in next cycle
if gap < 0:
    → category is overrepresented
    → consider decreasing boost
```

### Example

```
Allocation cycle results:
  Total allocated: 1,000 candidates

  Category    Actual    Target    Gap       Status
  ────────    ──────    ──────    ───       ──────
  SC          120       150       -30       Under-represented ↑
  ST          60        75        -15       Under-represented ↑
  OBC         280       270       +10       On target ✅
  EWS         95        100       -5        Slightly under ↑
  General     445       405       +40       Over-represented ↓
```

---

## Geographic Policy

### Rural Candidate Boost

Candidates from rural areas receive an additive score boost to counteract urban-centric opportunity distribution.

```json
{
  "geographic_policy": {
    "rural_boost": 0.10
  }
}
```

**Eligibility**: `candidate.is_rural = true`

### Underserved State Boost

Candidates from states with historically lower access to quality internships receive an additional boost.

```json
{
  "geographic_policy": {
    "underserved_state_boost": 0.05,
    "underserved_states": [
      "bihar", "jharkhand", "chhattisgarh", "odisha",
      "madhya pradesh", "rajasthan", "uttar pradesh"
    ]
  }
}
```

### Aspirational Districts

For districts identified by NITI Aayog as aspirational (lagging on development indices):

```json
{
  "geographic_policy": {
    "aspirational_district_boost": 0.08,
    "aspirational_districts": [
      "muzzaffarpur", "begusarai", "kishanganj",
      "raichur", "kalaburagi", "bellary",
      "koraput", "malakangiri", "rayagada"
    ]
  }
}
```

### Combined Geographic Boost Example

```
Candidate: Sunita Devi
  - State: Bihar (underserved)
  - District: Muzzaffarpur (aspirational)
  - Rural: Yes

Geographic boost calculation:
  rural_boost               = 0.10
  underserved_state_boost   = 0.05
  aspirational_district_boost = 0.08
  ─────────────────────────────────
  total geographic boost    = 0.23  → capped at max_total_adjustment (0.15)
```

---

## Female Participation Targets

### Configuration

```json
{
  "gender_policy": {
    "enabled": true,
    "female_target_ratio": 0.40,
    "female_boost": 0.05,
    "non_binary_boost": 0.05,
    "apply_boost_below_target": true
  }
}
```

### How It Works

The boost is applied **conditionally** — only when the current cycle's female allocation ratio is below the target:

```
if current_female_ratio < female_target_ratio:
    apply female_boost to all female candidates
else:
    no boost (target already met)
```

This prevents over-correction once the target is achieved.

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `female_target_ratio` | 0.40 | Target percentage of female allocations |
| `female_boost` | 0.05 | Score boost for female candidates |
| `non_binary_boost` | 0.05 | Score boost for non-binary candidates |
| `apply_boost_below_target` | true | Only apply boost when target not yet met |

---

## Repeat Participation Penalties

### Purpose

Ensure new candidates have fair access by slightly penalizing candidates who have already completed internships through the system.

### Configuration

```json
{
  "repeat_participation_policy": {
    "enabled": true,
    "prior_completion_penalty": -0.05,
    "prior_decline_penalty": -0.03,
    "max_prior_cycles": 2,
    "new_candidate_bonus": 0.03
  }
}
```

### Penalty Logic

```
historical_adjustment = 0.0

if candidate has prior allocation:
    if prior allocation status = "completed":
        historical_adjustment += prior_completion_penalty  (-0.05)
    elif prior allocation status = "declined":
        historical_adjustment += prior_decline_penalty     (-0.03)

    if count(prior_cycles) >= max_prior_cycles:
        historical_adjustment += -0.10  (strong penalty for repeat participants)

elif candidate is new (no prior cycles):
    historical_adjustment += new_candidate_bonus  (+0.03)
else:
    historical_adjustment = 0.0  (neutral)
```

### Example

```
Candidate A: First-time applicant
  → historical_adjustment = +0.03 (new candidate bonus)

Candidate B: Previously completed 1 internship
  → historical_adjustment = -0.05 (completion penalty)

Candidate C: Previously completed 3 internships (≥ max_prior_cycles)
  → historical_adjustment = -0.05 + -0.10 = -0.15 (strong penalty)
```

---

## Quality Guardrails

### Purpose

Prevent fairness adjustments from degrading match quality below acceptable thresholds.

### Configuration

```json
{
  "quality_guardrails": {
    "min_raw_score_threshold": 0.6,
    "max_total_adjustment": 0.15,
    "max_score_ceiling": 1.0,
    "preserve_top_rankings": true,
    "top_n_protected": 10
  }
}
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_raw_score_threshold` | 0.6 | Only apply boosts to matches with raw score ≥ this value |
| `max_total_adjustment` | 0.15 | Maximum total fairness boost per match |
| `max_score_ceiling` | 1.0 | Final score cannot exceed this value |
| `preserve_top_rankings` | true | Protect top-N candidates from re-ranking |
| `top_n_protected` | 10 | Number of top-ranked candidates to protect |

### Guardrail Application

```
Step 1: Check minimum threshold
  if raw_score < min_raw_score_threshold (0.6):
      → NO boost applied (match quality too low)

Step 2: Calculate total boost
  total_boost = category_boost + rural_boost + location_boost + ...
  
Step 3: Cap total adjustment
  if total_boost > max_total_adjustment (0.15):
      total_boost = max_total_adjustment

Step 4: Apply ceiling
  final_score = min(raw_score + total_boost, max_score_ceiling)

Step 5: Protect top rankings (optional)
  if preserve_top_rankings AND candidate is in top N by raw_score:
      → boost reduced or skipped to preserve merit-based ordering
```

### Guardrail Visualization

```
Score Scale:  0.0 ──────────────────────────────── 1.0
              │                                      │
              │  No boost zone  │  Boost zone        │
              │  (below 0.6)    │  (0.6+)            │
              │                 │                    │
              ├─────────────────┼────────────────────┤
              0.0              0.6                   1.0
                               ▲
                    min_raw_score_threshold

Boost Cap:    ┌─────────────────┐
              │ Max +0.15 boost │
              └─────────────────┘
```

---

## District Representation Targets

### Purpose

Ensure opportunities are distributed across districts proportionally to their candidate population, preventing concentration in urban centers.

### Configuration

```json
{
  "district_targets": {
    "enabled": true,
    "soft_target_weight": 0.5,
    "targets": {
      "mumbai": 0.08,
      "delhi": 0.07,
      "bangalore": 0.06,
      "hyderabad": 0.05,
      "pune": 0.04,
      "patna": 0.03,
      "lucknow": 0.03,
      "jaipur": 0.03,
      "_rural_other": 0.25,
      "_urban_other": 0.36
    }
  }
}
```

### How It Works

District targets are **soft constraints** in the OR-Tools optimization:

```
For each district d with target t_d:
  if actual_allocation[d] < t_d × total_allocations:
      → increase score for candidates from district d (soft preference)
  else:
      → no adjustment
```

The `soft_target_weight` (0.0–1.0) controls how strongly these targets influence the optimization. At 0.0, targets are ignored; at 1.0, they're treated as near-hard constraints.

---

## Example Configurations

### Conservative (Merit-First)

Minimal fairness adjustments, focused on quality:

```json
{
  "fairness_policy": {
    "version": "1.0",
    "enabled": true,
    "quality_guardrails": {
      "min_raw_score_threshold": 0.7,
      "max_total_adjustment": 0.08,
      "max_score_ceiling": 1.0,
      "preserve_top_rankings": true,
      "top_n_protected": 20
    },
    "social_category_policy": {
      "enabled": true,
      "boosts": { "sc": 0.08, "st": 0.08, "obc": 0.05, "ews": 0.04, "general": 0.0 }
    },
    "geographic_policy": {
      "enabled": true,
      "rural_boost": 0.05,
      "underserved_state_boost": 0.03
    },
    "gender_policy": { "enabled": false },
    "repeat_participation_policy": { "enabled": false }
  }
}
```

### Balanced (Default)

Standard fairness with quality guardrails:

```json
{
  "fairness_policy": {
    "version": "1.0",
    "enabled": true,
    "quality_guardrails": {
      "min_raw_score_threshold": 0.6,
      "max_total_adjustment": 0.15,
      "max_score_ceiling": 1.0,
      "preserve_top_rankings": true,
      "top_n_protected": 10
    },
    "social_category_policy": {
      "enabled": true,
      "boosts": { "sc": 0.15, "st": 0.15, "obc": 0.09, "ews": 0.075, "general": 0.0 }
    },
    "geographic_policy": {
      "enabled": true,
      "rural_boost": 0.10,
      "underserved_state_boost": 0.05
    },
    "gender_policy": {
      "enabled": true,
      "female_target_ratio": 0.40,
      "female_boost": 0.05
    },
    "repeat_participation_policy": {
      "enabled": true,
      "prior_completion_penalty": -0.05,
      "new_candidate_bonus": 0.03
    }
  }
}
```

### Equity-First (Maximum Inclusion)

Aggressive fairness adjustments for maximum representation:

```json
{
  "fairness_policy": {
    "version": "1.0",
    "enabled": true,
    "quality_guardrails": {
      "min_raw_score_threshold": 0.5,
      "max_total_adjustment": 0.25,
      "max_score_ceiling": 1.0,
      "preserve_top_rankings": false,
      "top_n_protected": 0
    },
    "social_category_policy": {
      "enabled": true,
      "boosts": { "sc": 0.25, "st": 0.25, "obc": 0.15, "ews": 0.12, "general": 0.0 }
    },
    "geographic_policy": {
      "enabled": true,
      "rural_boost": 0.15,
      "underserved_state_boost": 0.10,
      "aspirational_district_boost": 0.12
    },
    "gender_policy": {
      "enabled": true,
      "female_target_ratio": 0.50,
      "female_boost": 0.10,
      "non_binary_boost": 0.10
    },
    "repeat_participation_policy": {
      "enabled": true,
      "prior_completion_penalty": -0.10,
      "prior_decline_penalty": -0.05,
      "max_prior_cycles": 1,
      "new_candidate_bonus": 0.05
    },
    "district_targets": {
      "enabled": true,
      "soft_target_weight": 0.7
    }
  }
}
```

### Rural Focus

Prioritizing rural and semi-urban candidates:

```json
{
  "fairness_policy": {
    "version": "1.0",
    "enabled": true,
    "quality_guardrails": {
      "min_raw_score_threshold": 0.55,
      "max_total_adjustment": 0.20
    },
    "social_category_policy": {
      "enabled": true,
      "boosts": { "sc": 0.12, "st": 0.15, "obc": 0.08, "ews": 0.06, "general": 0.0 }
    },
    "geographic_policy": {
      "enabled": true,
      "rural_boost": 0.15,
      "underserved_state_boost": 0.10,
      "aspirational_district_boost": 0.12
    },
    "gender_policy": {
      "enabled": true,
      "female_target_ratio": 0.35,
      "female_boost": 0.08
    },
    "repeat_participation_policy": { "enabled": false }
  }
}
```

---

## Monitoring & Auditing

### Fairness Metrics (Post-Allocation)

After each allocation cycle, the system computes:

```python
{
    "total": 1000,
    "category_distribution": {
        "sc": 145, "st": 72, "obc": 268, "ews": 98, "general": 417
    },
    "category_percentages": {
        "sc": 14.5, "st": 7.2, "obc": 26.8, "ews": 9.8, "general": 41.7
    },
    "rural_count": 320,
    "rural_percentage": 32.0,
    "female_count": 380,
    "female_percentage": 38.0
}
```

### Audit Log Entries

Every fairness adjustment is logged:

```json
{
  "event": "fairness_adjustment",
  "candidate_id": 1234,
  "opportunity_id": 567,
  "raw_score": 0.72,
  "fairness_boost": 0.15,
  "boost_breakdown": {
    "social_category": 0.15,
    "rural": 0.10,
    "underserved_state": 0.05
  },
  "capped_total": 0.15,
  "final_score": 0.87,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Dashboard Metrics

The admin dashboard displays:
- **Category distribution** vs targets (bar chart)
- **Geographic heat map** of allocations
- **Gender ratio** trend across cycles
- **Score distribution** before/after fairness adjustments
- **Guardrail trigger rate** (how often caps are hit)
