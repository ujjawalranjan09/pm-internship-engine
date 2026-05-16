# System Architecture

## Overview

The PM Internship Smart Allocation Engine is a multi-layered system that matches candidates to internship opportunities using a 5-stage pipeline with fairness-aware optimization. The system is designed for scale, transparency, and equitable outcomes.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LAYER 7: PRESENTATION                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Next.js 15   │  │  Admin Panel │  │  Candidate   │                  │
│  │  Dashboard    │  │  Analytics   │  │  Portal      │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                  │                          │
└─────────┼─────────────────┼──────────────────┼──────────────────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        LAYER 6: API GATEWAY                            │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                     FastAPI Application                       │      │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │      │
│  │  │  Auth   │ │Candidates│ │Opportuni│ │Matching │            │      │
│  │  │ /auth/* │ │/candidate│ │/opportu*│ │/matchin*│            │      │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │      │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                        │      │
│  │  │Allocatn │ │  Admin  │ │Notifica*│  JWT Auth + RBAC       │      │
│  │  │/allocat*│ │ /admin/*│ │/notific*│  Rate Limiting          │      │
│  │  └─────────┘ └─────────┘ └─────────┘  CORS                   │      │
│  └──────────────────────────────────────────────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      LAYER 5: BUSINESS LOGIC                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Matching Service │  │ Allocation Svc   │  │ Fairness Service │      │
│  │                   │  │                   │  │                   │      │
│  │  5-Stage Pipeline │  │  OR-Tools Solver  │  │  Equity Policies  │      │
│  │  Filter→Retrieve  │  │  Constraint Opt.  │  │  Category Boosts  │      │
│  │  →Rank→Fair→Opt  │  │  Cycle Management │  │  Rural Boosts     │      │
│  └────────┬─────────┘  └────────┬──────────┘  └────────┬──────────┘      │
│           │                     │                       │               │
│  ┌────────┴─────────┐  ┌───────┴──────────┐  ┌────────┴──────────┐      │
│  │ Eligibility Svc   │  │ Notification Svc │  │  Search Service   │      │
│  │  Rule Engine      │  │  Email/SMS/InApp │  │  OpenSearch Query  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 4: ML / INTELLIGENCE                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Feature Extractor │  │ Heuristic Scorer │  │ Embedding Gen    │      │
│  │                   │  │                   │  │                   │      │
│  │ 13 Features       │  │ 8 Weighted        │  │ SentenceTransform │      │
│  │ Numpy Vectors     │  │ Components        │  │ all-MiniLM-L6-v2  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Text Processor    │  │ Skill Taxonomy   │  │ Vector Store     │      │
│  │ NLP Preprocessing │  │ Skill Normalizer │  │ pgvector / OpenSrch│     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 3: DATA ACCESS (ORM)                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │              SQLAlchemy 2.0 (Async) + Alembic                │      │
│  │                                                              │      │
│  │  Models: User │ CandidateProfile │ Opportunity │ Match       │      │
│  │          Allocation │ AllocationCycle │ Notification │ AuditLog│     │
│  │                                                              │      │
│  │  Schemas: Pydantic v2 (Request/Response validation)          │      │
│  └──────────────────────────────────────────────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 2: DATA STORAGE                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  PostgreSQL   │  │    Redis     │  │  OpenSearch  │                  │
│  │               │  │              │  │              │                  │
│  │  Primary DB   │  │  Cache Layer │  │  Full-Text   │                  │
│  │  + pgvector   │  │  Sessions    │  │  Search      │                  │
│  │  Migrations   │  │  Task Queue  │  │  Analytics   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: INFRASTRUCTURE                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │    Docker     │  │  AWS (ECS)   │  │  Terraform   │                  │
│  │  Compose Dev  │  │  RDS/ECR/ALB │  │  IaC Modules │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐                                    │
│  │  GitHub       │  │  CloudWatch  │                                    │
│  │  Actions CI   │  │  Monitoring  │                                    │
│  └──────────────┘  └──────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
                    ┌─────────┐
                    │  Client │
                    │ (Browser)│
                    └────┬────┘
                         │ HTTP/REST
                         ▼
                    ┌─────────┐
                    │ FastAPI │
                    │  Router │
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       ┌─────────┐ ┌──────────┐ ┌─────────┐
       │  Auth   │ │ Business │ │  Admin  │
       │  Deps   │ │  Logic   │ │  Guard  │
       └────┬────┘ └────┬─────┘ └────┬────┘
            │           │            │
            ▼           ▼            ▼
       ┌─────────┐ ┌──────────┐ ┌─────────┐
       │  JWT    │ │ Services │ │  Audit  │
       │ Decoder │ │ Layer    │ │  Logger │
       └────┬────┘ └────┬─────┘ └────┬────┘
            │           │            │
            └───────────┼────────────┘
                        ▼
              ┌─────────────────┐
              │  SQLAlchemy     │
              │  Async Session  │
              └────┬────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌─────────┐ ┌───────┐ ┌─────────┐
   │PostgreSQL│ │ Redis │ │OpenSrch │
   └─────────┘ └───────┘ └─────────┘
```

---

## Matching Pipeline Data Flow

```
Candidate Profile                Opportunity Listings
       │                                │
       ▼                                ▼
┌──────────────────────────────────────────────┐
│  STAGE 1: RULE-BASED FILTERING              │
│  ┌────────────────────────────────────────┐  │
│  │  EligibilityService.is_eligible()      │  │
│  │  • Education level check               │  │
│  │  • Location restriction check          │  │
│  │  • Social category check               │  │
│  │  • Profile completion threshold        │  │
│  └────────────────────────────────────────┘  │
│  Output: Filtered opportunity set            │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  STAGE 2: HYBRID RETRIEVAL                   │
│  ┌────────────────────────────────────────┐  │
│  │  Keyword Search (OpenSearch)           │  │
│  │  + Semantic Search (Embeddings)        │  │
│  │  • SentenceTransformer embeddings      │  │
│  │  • pgvector cosine similarity          │  │
│  │  • BM25 keyword matching               │  │
│  └────────────────────────────────────────┘  │
│  Output: Candidate-opportunity pairs         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  STAGE 3: FEATURE-BASED RANKING              │
│  ┌────────────────────────────────────────┐  │
│  │  HeuristicScorer.score()               │  │
│  │  8 weighted components:                │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │ skill_similarity      w=0.30     │  │  │
│  │  │ location_preference   w=0.20     │  │  │
│  │  │ education_fit         w=0.15     │  │  │
│  │  │ sector_interest       w=0.15     │  │  │
│  │  │ social_equity         w=0.10     │  │  │
│  │  │ profile_completeness  w=0.10     │  │  │
│  │  └──────────────────────────────────┘  │  │
│  │  score = Σ(wi × fi) → sigmoid norm    │  │
│  └────────────────────────────────────────┘  │
│  Output: Scored matches with breakdown       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  STAGE 4: FAIRNESS-AWARE RE-RANKING          │
│  ┌────────────────────────────────────────┐  │
│  │  FairnessService.rerank()              │  │
│  │  • SC/ST category boost: +0.15         │  │
│  │  • OBC category boost:    +0.09        │  │
│  │  • EWS category boost:    +0.075       │  │
│  │  • Rural candidate boost: +0.10        │  │
│  │  • Underserved state:     +0.05        │  │
│  │  adjusted_score = min(raw + boost, 1.0)│  │
│  └────────────────────────────────────────┘  │
│  Output: Fairness-adjusted ranked matches    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  STAGE 5: GLOBAL CONSTRAINED OPTIMIZATION    │
│  ┌────────────────────────────────────────┐  │
│  │  AllocationService.run_allocation()    │  │
│  │  • OR-Tools CP-SAT solver              │  │
│  │  • Maximize total match score          │  │
│  │  • Subject to:                         │  │
│  │    - Each candidate gets ≤ 1 slot      │  │
│  │    - Each opportunity ≤ capacity       │  │
│  │    - Min category representation       │  │
│  │    - Geographic diversity constraints  │  │
│  └────────────────────────────────────────┘  │
│  Output: Final allocations + waitlist        │
└──────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose | Version |
|-------|-----------|---------|---------|
| **Frontend** | Next.js (App Router) | SSR/CSR web application | 15.1+ |
| | React | UI component library | 19.0+ |
| | Tailwind CSS | Utility-first styling | 4.0+ |
| | Zustand | Client state management | 5.0+ |
| | TanStack Query | Server state management | 5.62+ |
| | AG Grid | Data tables | 32.3+ |
| | Recharts | Charts & visualization | 2.14+ |
| | MapLibre GL | Map rendering | 4.7+ |
| **Backend** | FastAPI | Async REST API framework | 0.115+ |
| | SQLAlchemy 2.0 | Async ORM | 2.0.35+ |
| | Alembic | Database migrations | 1.13+ |
| | Pydantic v2 | Data validation & serialization | 2.0+ |
| | python-jose | JWT token handling | 3.3+ |
| | Celery | Background task queue | 5.4+ |
| **ML/Intelligence** | sentence-transformers | Text embeddings | 3.2+ |
| | scikit-learn | Feature engineering | 1.5+ |
| | LightGBM | Gradient boosting (future) | 4.5+ |
| | OR-Tools | Constraint optimization | 9.10+ |
| | pgvector | Vector similarity search | 0.3+ |
| **Data** | PostgreSQL 16 | Primary relational database | 16+ |
| | Redis 7 | Caching, sessions, queues | 7+ |
| | OpenSearch 2.x | Full-text search, analytics | 2.x |
| **Infrastructure** | Docker / Compose | Containerization | 24+ |
| | AWS ECS Fargate | Container orchestration | - |
| | AWS RDS (PostgreSQL) | Managed database | - |
| | AWS ElastiCache (Redis) | Managed cache | - |
| | Terraform | Infrastructure as Code | 1.x |
| | GitHub Actions | CI/CD pipelines | - |
| **Monitoring** | Sentry | Error tracking | - |
| | OpenTelemetry | Distributed tracing | - |
| | CloudWatch | Logs & metrics | - |

---

## Module Responsibility Matrix

| Module | Path | Responsibility |
|--------|------|----------------|
| **auth** | `api/v1/auth.py` | User registration, login, JWT token management |
| **candidates** | `api/v1/candidates.py` | Candidate profile CRUD, profile completion tracking |
| **opportunities** | `api/v1/opportunities.py` | Internship opportunity CRUD, search, soft-delete |
| **matching** | `api/v1/matching.py` | Recommendation retrieval, batch matching trigger |
| **allocation** | `api/v1/allocation.py` | Allocation cycle management, results, overrides |
| **admin** | `api/v1/admin.py` | Analytics dashboards, policy config, audit logs |
| **notifications** | `api/v1/notifications.py` | User notification listing, read status management |
| **MatchingService** | `services/matching_service.py` | 5-stage pipeline orchestration |
| **EligibilityService** | `services/eligibility_service.py` | Hard eligibility rule evaluation |
| **FairnessService** | `services/fairness_service.py` | Equity-aware re-ranking and metrics |
| **AllocationService** | `services/allocation_service.py` | OR-Tools constraint optimization |
| **SearchService** | `services/search_service.py` | OpenSearch query builder |
| **NotificationService** | `services/notification_service.py` | Multi-channel notification dispatch |
| **HeuristicScorer** | `ml/ranking/heuristic_scorer.py` | Weighted feature scoring with sigmoid normalization |
| **FeatureExtractor** | `ml/feature_engineering/feature_extractor.py` | 13-feature vector extraction |
| **EmbeddingGenerator** | `ml/embeddings/embedding_generator.py` | SentenceTransformer embedding generation |
| **VectorStore** | `ml/embeddings/vector_store.py` | pgvector similarity search |
| **SkillTaxonomy** | `ml/feature_engineering/skill_taxonomy.py` | Skill normalization and hierarchy |
| **TextProcessor** | `ml/feature_engineering/text_processor.py` | NLP text preprocessing |

---

## Security Architecture

```
Request Flow:
  Client → CORS Check → Rate Limiter → JWT Validation → RBAC Check → Handler

Authentication:
  • JWT access tokens (30 min expiry)
  • JWT refresh tokens (7 day expiry)
  • HS256 signing algorithm
  • Password hashing via bcrypt (passlib)

Authorization Roles:
  • candidate  → Own profile, recommendations, notifications
  • employer   → Create/manage own opportunities
  • admin      → Full access, allocation runs, policy config, analytics
```
