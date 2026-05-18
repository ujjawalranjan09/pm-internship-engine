# AI-Based Smart Allocation Engine for PM Internship Scheme

## 🚀 Professional Grade Internship Allocation System

This repository contains a high-performance, production-ready AI engine designed for the **PM Internship Scheme**. It solves the complex problem of matching thousands of student applicants with diverse internship opportunities while ensuring fairness, policy compliance, and global optimization.

### Key Professional Features
- **Type-Safe Full-Stack**: Fully optimized TypeScript (Frontend) and MyPy-checked Python (Backend) for maximum reliability.
- **Fairness-First Matching**: Multi-stage ranking pipeline with representation-aware re-ranking to meet social equity goals.
- **Constrained Optimization**: Uses Google OR-Tools to solve global allocation as a mathematical optimization problem.
- **Portable Architecture**: Engineered with a flexible data layer compatible with PostgreSQL/pgvector for production and SQLite for lightning-fast testing.
- **Explainable AI**: Provides automated justifications for match results to candidates and administrators.

## 🏗️ Architecture

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
The system utilizes a 5-stage pipeline to refine millions of possible matches into a single optimal allocation:
1.  **Eligibility Filtering**: Hard rules and policy compliance.
2.  **Hybrid Retrieval**: Keyword + semantic vector search (OpenSearch).
3.  **Feature Ranking**: ML-based scoring (XGBoost/LightGBM).
4.  **Fairness Re-ranking**: Adjusting scores for social and geographic representation.
5.  **Global Optimization**: Final assignment solving for max utility under capacity constraints.

## 🛠️ Development & Deployment

### Backend Setup
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
# Run tests
pytest
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
# Run type checks
npm run build
# Start dev server
npm run dev
```

## License
Government of India - PM Internship Scheme
