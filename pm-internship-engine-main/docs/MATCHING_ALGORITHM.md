# Matching Algorithm — 5-Stage Pipeline

## Overview

The PM Internship Smart Allocation Engine uses a **5-stage matching pipeline** to pair candidates with internship opportunities. Each stage progressively narrows and refines candidates, moving from coarse eligibility checks to fine-grained optimization. The pipeline is designed for **transparency** (every score is explainable), **fairness** (equitable access for underrepresented groups), and **scale** (handles 100K+ candidates × 10K+ opportunities).

```
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│   STAGE 1  │────▶│   STAGE 2  │────▶│   STAGE 3  │────▶│   STAGE 4  │────▶│   STAGE 5  │
│  Rule-Based│     │  Hybrid    │     │  Feature   │     │ Fairness   │     │ Constrained│
│  Filtering │     │  Retrieval │     │  Scoring   │     │ Re-Ranking │     │ Optimizer  │
│            │     │            │     │            │     │            │     │            │
│  Eligible? │     │  Relevant? │     │  How good? │     │  Fair?     │     │  Optimal?  │
│  Yes/No    │     │  Top-N     │     │  0.0–1.0   │     │  Adjusted  │     │  Assigned  │
└────────────┘     └────────────┘     └────────────┘     └────────────┘     └────────────┘
  100%  ──────▶  ~60%  ──────▶  ~60%  ──────▶  ~60%  ──────▶  Final
candidates       candidates      scored         re-ranked       allocations
```

---

## Stage 1: Rule-Based Filtering

### Purpose

Eliminate candidates who cannot legally or logistically participate in an opportunity. This is a **binary gate** — a candidate either passes or fails. No scoring occurs here.

### Hard Constraints Evaluated

| Constraint | Field | Rule |
|------------|-------|------|
| **Minimum Education** | `eligibility_criteria.min_education` | Candidate's degree level ≥ required level |
| **State Restriction** | `eligibility_criteria.allowed_states` | Candidate's state must be in allowed list |
| **State Exclusion** | `eligibility_criteria.excluded_states` | Candidate's state must not be excluded |
| **District Restriction** | `eligibility_criteria.allowed_districts` | Candidate's district must be in allowed list |
| **Social Category** | `eligibility_criteria.required_social_categories` | Candidate's category must match (if specified) |
| **Rural Only** | `eligibility_criteria.rural_only` | Only rural candidates eligible (if true) |
| **Profile Completion** | `eligibility_criteria.min_profile_completion` | Completion score ≥ threshold (default 0.0) |

### Education Hierarchy

```
Level 6: PhD
Level 5: Masters (M.Tech, M.Sc, MBA, MCA)
Level 4: Bachelors (B.Tech, B.Sc, B.Com, B.A)
Level 3: Diploma
Level 2: 12th
Level 1: 10th
```

A candidate at level N is eligible for any opportunity requiring level ≤ N.

### Example

```
Candidate: Priya Sharma
  - Education: B.Tech (level 4)
  - State: Bihar
  - Category: SC
  - Rural: Yes
  - Profile completion: 0.85

Opportunity: Software Intern at TCS, Bangalore
  - min_education: bachelors (level 4)  ✅ Priya qualifies
  - allowed_states: null                 ✅ No restriction
  - required_social_categories: null     ✅ Open to all
  - min_profile_completion: 0.7          ✅ 0.85 ≥ 0.7

Result: ELIGIBLE → proceeds to Stage 2
```

```
Candidate: Rahul Verma
  - Education: 12th (level 2)
  - State: Maharashtra

Opportunity: Data Analyst Intern at Infosys
  - min_education: bachelors (level 4)  ❌ Rahul is level 2

Result: FILTERED OUT → candidate does not proceed
```

### Implementation

```python
# From EligibilityService.is_eligible()
def is_eligible(self, candidate, opportunity) -> bool:
    criteria = opportunity.eligibility_criteria or {}
    if not self._check_education(candidate, criteria):    return False
    if not self._check_location_eligibility(candidate, criteria): return False
    if not self._check_category_eligibility(candidate, criteria): return False
    if candidate.profile_completion_score < criteria.get("min_profile_completion", 0.0):
        return False
    return True
```

---

## Stage 2: Hybrid Retrieval

### Purpose

From the eligible set, retrieve the most **semantically and lexically relevant** opportunity-candidate pairs. This stage uses a hybrid of keyword search (BM25 via OpenSearch) and semantic search (dense embeddings via pgvector).

### Retrieval Methods

#### 2a. Keyword Search (BM25)

OpenSearch performs full-text search across opportunity titles, descriptions, and required skills. This catches **exact matches** — when a candidate's skills literally appear in the opportunity text.

```json
// OpenSearch query structure
{
  "bool": {
    "should": [
      { "match": { "title": "python machine learning" } },
      { "match": { "description": "data science internship" } },
      { "match": { "required_skills": "python sql pandas" } }
    ]
  }
}
```

#### 2b. Semantic Search (Embeddings)

SentenceTransformer embeddings (`all-MiniLM-L6-v2`) are generated for candidate profiles and opportunity descriptions. Cosine similarity is computed via pgvector to find **semantically similar** pairs even when keywords differ.

```
Candidate text: "B.Tech CSE student with experience in Python, 
                 machine learning, and data visualization"
                    ↓
           SentenceTransformer
                    ↓
         [0.023, -0.145, 0.089, ...]  (384-dim vector)
                    ↓
          pgvector cosine similarity
                    ↓
Opportunity: "Data Science Intern - Work on predictive models 
              using Python and scikit-learn"
```

#### 2c. Hybrid Fusion

Results from both methods are merged using **Reciprocal Rank Fusion (RRF)**:

```
RRF_score(d) = Σ  1
              k + rank_i(d)

where:
  k = 60 (standard RRF constant)
  rank_i(d) = rank of document d in result set i
```

The top-N pairs (default N=200 per candidate) proceed to scoring.

### Why Hybrid?

| Method | Strengths | Weaknesses |
|--------|-----------|------------|
| BM25 | Exact keyword match, fast | Misses synonyms, paraphrases |
| Semantic | Catches meaning similarity | May miss exact terms |
| **Hybrid** | **Best of both** | Slightly more compute |

### Implementation Note

For the initial deployment, Stage 2 uses a simplified approach: all eligible pairs are scored directly (the full hybrid retrieval with OpenSearch + pgvector is activated at scale). The `_filter_stage` in `MatchingService` handles this.

---

## Stage 3: Feature-Based Scoring

### Purpose

Assign a **composite score** (0.0–1.0) to each candidate-opportunity pair based on 8 weighted features. This is the core ranking signal.

### Scoring Formula

```
score(c, o) = Σ  w_i × f_i(c, o)
             i=1..8

where:
  w_i = weight of feature i
  f_i(c, o) = feature function evaluating candidate c against opportunity o
```

The result is passed through a **sigmoid normalization** to keep values in [0, 1]:

```
σ(x) = 1 / (1 + e^(-k(x - x₀)))

where k=10, x₀=0.5 (steepness and midpoint)
```

### Feature Components

```
┌─────────────────────────────────────────────────────────────┐
│                    SCORING BREAKDOWN                         │
│                                                             │
│  ┌──────────────────────┬────────┬─────────────────────────┐│
│  │ Component            │ Weight │ What It Measures         ││
│  ├──────────────────────┼────────┼─────────────────────────┤│
│  │ Skill Match          │  0.30  │ Required skill overlap   ││
│  │ Qualification Fit    │  0.15  │ Education alignment      ││
│  │ Sector Interest      │  0.10  │ Sector-skill relevance   ││
│  │ Location Preference  │  0.10  │ Geographic compatibility ││
│  │ Profile Readiness    │  0.10  │ Profile completeness     ││
│  │ Employer Preference  │  0.10  │ Employer-specific match  ││
│  │ Historical Adjust    │  0.05  │ Past cycle learnings     ││
│  │ Semantic Similarity  │  0.10  │ Embedding cosine sim     ││
│  ├──────────────────────┼────────┼─────────────────────────┤│
│  │ TOTAL                │  1.00  │                         ││
│  └──────────────────────┴────────┴─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Skill Match (weight: 0.30)

Measures the overlap between candidate skills and opportunity required skills.

```
f_skill(c, o) = |skills(c) ∩ skills(o)| / |skills(o)|
```

**Example:**
```
Candidate skills:    {"python", "sql", "pandas", "machine learning"}
Required skills:     {"python", "sql", "data analysis"}
Intersection:        {"python", "sql"}  →  2 matches
Score:               2/3 = 0.667
```

If no required skills are specified, returns 0.5 (neutral). If candidate has no skills, returns 0.0.

### 3.2 Qualification Fit (weight: 0.15)

Evaluates education level and field-of-study alignment.

```
f_qual(c, o) = level_score + field_bonus

where:
  level_score = 1.0  if candidate_level ≥ required_level
                0.7  if candidate_level = required_level - 1
                0.2  otherwise
  
  field_bonus = 0.2  if field_of_study matches (capped at 1.0 total)
```

**Example:**
```
Candidate: B.Tech Computer Science (level 4)
Opportunity requires: Bachelors in Engineering (level 4)
→ level_score = 1.0, field_bonus = 0.2 → f_qual = 1.0 (capped)
```

### 3.3 Sector Interest (weight: 0.10)

Maps candidate skills to sector-specific skill sets and computes overlap.

```
Sector-Skill Map:
  Technology   → python, java, javascript, sql, ml, data science, web, cloud, devops
  Finance      → accounting, finance, excel, sql, data analysis, banking
  Healthcare   → biology, chemistry, healthcare, medical, nursing, pharmacy
  Education    → teaching, training, curriculum, education
  Manufacturing → mechanical, electrical, production, quality, manufacturing
  Agriculture  → agriculture, farming, horticulture, agronomy
  Marketing    → marketing, digital marketing, seo, social media, content writing

f_sector(c, o) = min(matching_skills / (|sector_skills| × 0.3), 1.0)
```

### 3.4 Location Preference (weight: 0.10)

Scores geographic compatibility considering mobility preferences.

```
f_location(c, o) = {
    1.0   if same district
    0.8   if same state
    0.7   if willing_to_relocate AND different location
    0.9   if opportunity is remote
    0.5   otherwise (base score)
}
```

Remote work opportunities get a floor of 0.9 since they're universally accessible.

### 3.5 Profile Readiness (weight: 0.10)

Directly uses the candidate's profile completion score.

```
f_profile(c) = c.profile_completion_score

Ranges from 0.0 (empty profile) to 1.0 (fully complete)
Factors: bio, education, skills, resume upload, preferences
```

### 3.6 Employer Preference (weight: 0.10)

Captures employer-specific preferences or candidate-employer affinity.

```
f_employer(c, o) = employer_preference_score

Factors:
  - Employer's preferred universities (if specified)
  - Employer's preferred skill specializations
  - Past employer-candidate interactions (if any)
  - Default: 0.5 (neutral)
```

### 3.7 Historical Adjustment (weight: 0.05)

Learns from past allocation cycles to improve future matching.

```
f_history(c, o) = {
    0.3   if candidate was previously allocated and declined
    0.7   if candidate was previously allocated and completed successfully
    0.5   if no history (neutral)
}
```

This factor penalizes repeat participants slightly to give new candidates fair access.

### 3.8 Semantic Similarity (weight: 0.10)

Cosine similarity between candidate and opportunity embeddings.

```
f_semantic(c, o) = cos(emb(c), emb(o))

                  emb(c) · emb(o)
               = ─────────────────
                 ||emb(c)|| × ||emb(o)||

where emb() = SentenceTransformer('all-MiniLM-L6-v2') embedding
      dimension = 384
```

### Full Scoring Example

```
Candidate: Ananya Patel (B.Tech, Python/SQL/ML, Mumbai, General)
Opportunity: Data Science Intern at Flipkart, Bangalore

  f_skill:           {python,ml} ∩ {python,sql,ml} = 2/3    → 0.667  × 0.30 = 0.200
  f_qualification:   B.Tech ≥ Bachelors, field match         → 1.000  × 0.15 = 0.150
  f_sector:          tech skills overlap                     → 0.800  × 0.10 = 0.080
  f_location:        Mumbai ≠ Bangalore, willing to relocate → 0.700  × 0.10 = 0.070
  f_profile:         completion = 0.92                       → 0.920  × 0.10 = 0.092
  f_employer:        no specific preference                  → 0.500  × 0.10 = 0.050
  f_history:         no prior allocation                     → 0.500  × 0.05 = 0.025
  f_semantic:        cosine sim = 0.78                       → 0.780  × 0.10 = 0.078
                                                                     ─────────────
                                                              Total:     0.745
```

---

## Stage 4: Fairness-Aware Re-Ranking

### Purpose

Adjust scores to ensure historically disadvantaged groups receive equitable access to opportunities. This stage applies **additive boosts** that are bounded by quality guardrails.

### Adjustment Formula

```
adjusted_score(c, o) = min(raw_score(c, o) + fairness_boost(c, o), 1.0)

where:
  fairness_boost(c, o) = category_boost(c) + rural_boost(c) + location_boost(c)
```

### Boost Components

#### Social Category Boost

```
category_boost(c) = {
    SOCIAL_CATEGORY_BOOST          if c.category ∈ {SC, ST}
    SOCIAL_CATEGORY_BOOST × 0.60   if c.category = OBC
    SOCIAL_CATEGORY_BOOST × 0.50   if c.category = EWS
    0.0                             if c.category = General
}

Default SOCIAL_CATEGORY_BOOST = 0.15
```

```
┌─────────────────────────────────────────┐
│  Category Boost Values (default config) │
│                                         │
│  SC/ST  ████████████████  +0.150        │
│  OBC    █████████         +0.090        │
│  EWS    ████████          +0.075        │
│  General                   +0.000       │
└─────────────────────────────────────────┘
```

#### Rural Candidate Boost

```
rural_boost(c) = RURAL_BOOST    if c.is_rural = True
                 0.0            otherwise

Default RURAL_BOOST = 0.10
```

#### Underserved State Boost

```
location_boost(c) = 0.05    if c.state ∈ {Bihar, Jharkhand, Chhattisgarh,
                                            Odisha, Madhya Pradesh, Rajasthan,
                                            Uttar Pradesh}
                    0.0     otherwise
```

### Quality Guardrails

To prevent fairness adjustments from degrading match quality:

1. **Minimum threshold**: Only matches with `raw_score ≥ 0.6` are eligible for fairness boosts
2. **Maximum adjustment**: Total fairness boost is capped at `0.15` per match
3. **Score ceiling**: Final score is capped at `1.0`

```
┌──────────────────────────────────────────────────────────┐
│  FAIRNESS GUARDRAILS                                     │
│                                                          │
│  Raw Score    Fairness Boost    Final Score    Eligible?  │
│  ─────────    ──────────────    ───────────    ─────────  │
│  0.85         +0.15             1.00           ✅ Yes     │
│  0.70         +0.10             0.80           ✅ Yes     │
│  0.55         +0.15             0.70           ❌ No*     │
│  0.40         +0.15             0.55           ❌ No*     │
│                                                          │
│  * Below 0.6 minimum threshold — no boost applied        │
└──────────────────────────────────────────────────────────┘
```

### Re-Ranking Example

```
Candidate: Deepak Kumar (SC, Rural, Bihar)
Opportunity: Government Data Analyst Intern

Before fairness:
  raw_score = 0.72

Fairness boost:
  category_boost = 0.150  (SC)
  rural_boost    = 0.100  (rural)
  location_boost = 0.050  (Bihar = underserved)
  total_boost    = 0.300  → capped at 0.15

After fairness:
  adjusted_score = min(0.72 + 0.15, 1.0) = 0.87

This candidate may now rank higher than a candidate with raw_score 0.80
but no fairness adjustments, promoting equitable access.
```

---

## Stage 5: Constrained Optimization (OR-Tools)

### Purpose

Find the **globally optimal** allocation of candidates to opportunities, respecting capacity limits and fairness constraints. This is a **bipartite matching** problem solved with linear programming.

### Problem Formulation

```
Maximize:    Σ  score(c_i, o_j) × x_ij
           (i,j)∈M

Subject to:
  Σ_j x_ij ≤ 1          ∀ candidate i     (each candidate gets ≤ 1 slot)
  Σ_i x_ij ≤ cap_j      ∀ opportunity j    (respect capacity)
  x_ij ∈ {0, 1}         ∀ (i,j) ∈ M        (binary decision)

where:
  M = set of valid (candidate, opportunity) match pairs
  cap_j = opportunity j's available slots
  x_ij = 1 if candidate i is allocated to opportunity j
```

### Solver

The system uses **OR-Tools CP-SAT** solver (via `pywraplp`):

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")

# Decision variables
x = {}
for match in matches:
    x[match.id] = solver.IntVar(0, 1, f"x_{match.id}")

# Constraint 1: Each candidate allocated at most once
for candidate_id, match_ids in candidate_matches.items():
    solver.Add(sum(x[mid] for mid in match_ids) <= 1)

# Constraint 2: Opportunity capacity
for opp_id, match_ids in opp_matches.items():
    solver.Add(sum(x[mid] for mid in match_ids) <= capacity)

# Objective: maximize total score
objective = solver.Objective()
for match in matches:
    objective.SetCoefficient(x[match.id], match.score)
objective.SetMaximization()

status = solver.Solve()
```

### Allocation Flow

```
                    ┌─────────────────┐
                    │  Match Pool     │
                    │  (scored pairs) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  OR-Tools SCIP  │
                    │  Solver         │
                    │                 │
                    │  maximize Σ sx  │
                    │  s.t. ≤1/cand   │
                    │       ≤cap/opp  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │  ALLOCATED   │ │ WAITLIST │ │  NOT MATCHED │
     │              │ │          │ │              │
     │  x_ij = 1    │ │ Top non- │ │  Below score │
     │  Confirmed   │ │ allocated│ │  threshold   │
     │  assignment  │ │ backups  │ │  or infeasible│
     └──────────────┘ └──────────┘ └──────────────┘
```

### Waitlist Generation

After the optimal solution, unallocated high-scoring matches become waitlist entries:

```
for each match not in optimal solution:
    if candidate is NOT already allocated
    AND opportunity has remaining capacity:
        → add to waitlist at position (rank by score descending)
```

### Example

```
Scenario: 3 candidates, 2 opportunities (capacity 1 each)

Matches:
  (Priya,    TCS Intern)    score = 0.85
  (Priya,    Infosys Intern) score = 0.72
  (Rahul,    TCS Intern)    score = 0.78
  (Rahul,    Infosys Intern) score = 0.81
  (Ananya,   TCS Intern)    score = 0.70
  (Ananya,   Infosys Intern) score = 0.68

OR-Tools Solution:
  Priya   → TCS Intern      (0.85)  ← highest for this opp
  Rahul   → Infosys Intern  (0.81)  ← highest for this opp
  Ananya  → Waitlisted      (next best: 0.70 at TCS)

Total objective value = 0.85 + 0.81 = 1.66 (maximized)
```

---

## Pipeline Integration

### Data Flow Through All 5 Stages

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FULL PIPELINE FLOW                             │
│                                                                      │
│  Input: N candidates × M opportunities                               │
│                                                                      │
│  Stage 1: Rule Filter                                                │
│    Input:  N × M = 1,000,000 pairs (1000 cands × 1000 opps)        │
│    Output: ~600,000 eligible pairs (60% pass rate)                   │
│    Time:   O(N×M) — simple predicate checks                          │
│                                                                      │
│  Stage 2: Hybrid Retrieval                                           │
│    Input:  600,000 pairs                                             │
│    Output: ~200,000 relevant pairs (top 200 per candidate)          │
│    Time:   O(N×log M) — vector similarity + BM25                     │
│                                                                      │
│  Stage 3: Feature Scoring                                            │
│    Input:  200,000 pairs                                             │
│    Output: 200,000 scored pairs (each with 8-component breakdown)    │
│    Time:   O(P) — feature computation per pair                       │
│                                                                      │
│  Stage 4: Fairness Re-Ranking                                        │
│    Input:  200,000 scored pairs                                      │
│    Output: 200,000 adjusted pairs (re-sorted)                        │
│    Time:   O(P×log P) — boost computation + re-sort                  │
│                                                                      │
│  Stage 5: Constrained Optimization                                   │
│    Input:  Top matches per candidate (above threshold)               │
│    Output: Final allocations + waitlist                              │
│    Time:   O(V×E) — LP solver (polynomial in practice)              │
│                                                                      │
│  Final: Each candidate gets 0 or 1 allocation                        │
│         Each opportunity ≤ capacity filled                           │
│         Waitlist ranked by score for backfills                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Configuration

All weights and thresholds are configurable via environment variables:

```env
# Scoring weights
MATCH_WEIGHTS={"skill_similarity":0.30,"location_preference":0.10,
               "education_fit":0.15,"sector_interest":0.10,
               "social_equity":0.10,"profile_completeness":0.10}

# Fairness parameters
FAIRNESS_ENABLED=true
FAIRNESS_SOCIAL_CATEGORY_BOOST=0.15
FAIRNESS_RURAL_BOOST=0.10
FAIRNESS_GENDER_PARITY_TARGET=0.40

# Pipeline parameters
MATCH_TOP_K=50
MATCH_MIN_SCORE=0.1
```

---

## Transparency & Explainability

Every match includes a **score breakdown** and **human-readable explanation**:

```json
{
  "score": 0.745,
  "score_breakdown": {
    "skill_similarity": 0.667,
    "education_fit": 1.000,
    "sector_interest": 0.800,
    "location_preference": 0.700,
    "profile_completeness": 0.920,
    "employer_preference": 0.500,
    "historical_adjustment": 0.500,
    "semantic_similarity": 0.780,
    "fairness_boost": 0.0,
    "original_score": 0.745
  },
  "explanation": "Strengths: Education Fit: 100%, Profile Completeness: 92%, Sector Interest: 80%. Areas for improvement: Employer Preference: 50%, Historical Adjustment: 50%."
}
```

This enables administrators to understand why any specific match was made and audit the system for bias or errors.
