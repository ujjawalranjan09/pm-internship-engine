# AI-Based Smart Allocation Engine for PM Internship Scheme

A production-ready architecture for matching student applicants to internship opportunities under the PM Internship Scheme.

## Architecture

### Tech Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS v4, shadcn/ui
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0, Pydantic v2
- **Database**: PostgreSQL 16 with pgvector
- **Cache**: Redis
- **Search**: OpenSearch
- **Workflow**: Temporal
- **ML**: LightGBM/XGBoost, sentence-transformers
- **Optimization**: Google OR-Tools
- **Monitoring**: MLflow, OpenTelemetry

### Core Modules
1. **Applicant Management** - Registration, profiles, resume parsing
2. **Opportunity Management** - Internship CRUD, capacity management
3. **Eligibility & Rules Engine** - Hard filters, policy compliance
4. **Matchmaking Engine** - Multi-stage ranking with explainability
5. **Fairness & Policy Engine** - Representation-aware re-ranking
6. **Allocation Engine** - Constrained optimization via OR-Tools
7. **Admin & Oversight** - Policy control, audit trails, overrides
8. **Notification Service** - Email, SMS, in-app notifications

### Matching Pipeline
1. Rule-based filtering → 2. Hybrid retrieval → 3. Feature-based ranking → 4. Fairness-aware re-ranking → 5. Global constrained optimization

## Quick Start

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## License
Government of India - PM Internship Scheme
