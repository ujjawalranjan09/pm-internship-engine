# Development Guide

## Prerequisites

| Tool | Version | Installation |
|------|---------|-------------|
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 22+ | [nodejs.org](https://nodejs.org/) |
| Docker | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.20+ | Included with Docker Desktop |
| Git | 2.40+ | [git-scm.com](https://git-scm.com/) |

### Optional Tools

| Tool | Purpose |
|------|---------|
| `ruff` | Python linter and formatter |
| `mypy` | Python type checker |
| `pgcli` | PostgreSQL CLI with auto-complete |
| `httpie` | Human-friendly HTTP client |

---

## Local Setup (Step by Step)

### 1. Clone the Repository

```bash
git clone https://github.com/pm-internship/engine.git
cd engine
```

### 2. Environment Configuration

```bash
cp .env.development .env
```

Edit `.env` if needed. The defaults work for local development with Docker.

### 3. One-Command Setup

```bash
./scripts/setup.sh
```

This script will:
- Check prerequisites
- Create Python virtual environment
- Install all dependencies
- Start Docker services
- Run database migrations
- Seed test data
- Start the application

### 4. Manual Setup (if preferred)

```bash
# Python environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..

# Start infrastructure
cd infrastructure/docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d \
    postgres redis opensearch temporal
cd ../..

# Run migrations
cd backend && alembic upgrade head && cd ..

# Seed data
python scripts/seed-data.py

# Start services
cd infrastructure/docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend frontend
```

---

## Project Structure

```
pm-internship-engine/
├── backend/                          # FastAPI backend application
│   ├── app/
│   │   ├── api/                      # API layer
│   │   │   ├── deps.py               # Dependency injection
│   │   │   └── v1/                   # API v1 endpoints
│   │   │       ├── router.py         # Route aggregation
│   │   │       ├── auth.py           # Authentication endpoints
│   │   │       ├── candidates.py     # Candidate CRUD
│   │   │       ├── opportunities.py  # Opportunity CRUD
│   │   │       ├── matching.py       # Matching endpoints
│   │   │       ├── allocation.py     # Allocation endpoints
│   │   │       ├── admin.py          # Admin/analytics endpoints
│   │   │       └── notifications.py  # Notification endpoints
│   │   ├── core/                     # Core configuration
│   │   │   ├── config.py             # Settings management
│   │   │   ├── database.py           # Database engine setup
│   │   │   ├── security.py           # JWT and password handling
│   │   │   ├── exceptions.py         # Custom exception classes
│   │   │   └── events.py             # Event bus system
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── base.py               # Base model with timestamps
│   │   │   ├── user.py               # User model
│   │   │   ├── candidate.py          # Candidate profile model
│   │   │   ├── opportunity.py        # Opportunity model
│   │   │   ├── match.py              # Match scoring model
│   │   │   ├── allocation.py         # Allocation model
│   │   │   ├── allocation_cycle.py   # Allocation cycle model
│   │   │   ├── notification.py       # Notification model
│   │   │   ├── audit_log.py          # Audit log model
│   │   │   └── waitlist.py           # Waitlist model
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   │   ├── user.py               # User schemas
│   │   │   ├── candidate.py          # Candidate schemas
│   │   │   ├── opportunity.py        # Opportunity schemas
│   │   │   ├── match.py              # Match schemas
│   │   │   ├── allocation.py         # Allocation schemas
│   │   │   └── common.py             # Shared schemas (pagination)
│   │   ├── services/                 # Business logic services
│   │   │   ├── matching_service.py   # 5-stage matching pipeline
│   │   │   ├── eligibility_service.py # Hard eligibility rules
│   │   │   ├── fairness_service.py   # Fairness-aware re-ranking
│   │   │   ├── allocation_service.py # OR-Tools optimization
│   │   │   ├── search_service.py     # OpenSearch integration
│   │   │   └── notification_service.py # Notification dispatch
│   │   ├── modules/                  # Domain modules (future expansion)
│   │   │   ├── allocation_module/
│   │   │   ├── analytics_module/
│   │   │   ├── audit_module/
│   │   │   ├── candidate_module/
│   │   │   ├── fairness_module/
│   │   │   ├── identity_module/
│   │   │   ├── matching_module/
│   │   │   ├── notification_module/
│   │   │   ├── opportunity_module/
│   │   │   └── rules_module/
│   │   ├── ml/                       # Machine learning components
│   │   │   ├── embeddings/           # Vector embeddings
│   │   │   │   ├── embedding_generator.py
│   │   │   │   └── vector_store.py
│   │   │   ├── feature_engineering/  # Feature extraction
│   │   │   │   ├── feature_extractor.py
│   │   │   │   ├── skill_taxonomy.py
│   │   │   │   └── text_processor.py
│   │   │   ├── ranking/              # Scoring algorithms
│   │   │   │   └── heuristic_scorer.py
│   │   │   ├── matching/             # Matching algorithms (future)
│   │   │   └── fairness/             # Fairness algorithms (future)
│   │   └── main.py                   # FastAPI application entry point
│   ├── alembic/                      # Database migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini                   # Alembic configuration
│   ├── requirements.txt              # Python dependencies
│   ├── requirements-dev.txt          # Development dependencies
│   └── pyproject.toml                # Python project configuration
├── frontend/                         # Next.js frontend application
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── globals.css           # Global styles
│   │   │   ├── providers.tsx         # Context providers
│   │   │   └── auth/                 # Auth pages
│   │   │       ├── layout.tsx
│   │   │       ├── login/page.tsx
│   │   │       └── register/page.tsx
│   │   ├── components/
│   │   │   ├── ui/                   # Reusable UI components
│   │   │   └── shared/               # Shared layout components
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── services/                 # API client services
│   │   ├── stores/                   # Zustand state stores
│   │   ├── types/                    # TypeScript type definitions
│   │   └── lib/                      # Utility functions
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── postcss.config.js
├── infrastructure/                   # Infrastructure configuration
│   ├── docker/                       # Docker configurations
│   │   ├── docker-compose.yml        # Production compose
│   │   ├── docker-compose.dev.yml    # Development overrides
│   │   ├── Dockerfile.backend        # Backend Dockerfile
│   │   ├── Dockerfile.frontend       # Frontend Dockerfile
│   │   └── .dockerignore
│   └── terraform/                    # Terraform IaC
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── modules/
│           ├── vpc/
│           ├── ecs/
│           ├── rds/
│           ├── redis/
│           └── opensearch/
├── scripts/                          # Utility scripts
│   ├── setup.sh                      # One-command setup
│   ├── seed-data.py                  # Test data generator
│   ├── health-check.sh              # Service health checks
│   └── backup.sh                     # Database backup
├── docs/                             # Documentation
├── .github/workflows/                # CI/CD pipelines
│   ├── ci.yml
│   ├── deploy-staging.yml
│   └── deploy-production.yml
├── Makefile                          # Build commands
├── .env.example                      # Environment template
├── .env.development                  # Development defaults
├── .env.production                   # Production defaults
├── .editorconfig                     # Editor configuration
├── .gitignore
└── README.md
```

---

## Running Tests

### Backend Tests

```bash
# Activate virtual environment
source backend/.venv/bin/activate

# Run all tests
cd backend && python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
python -m pytest tests/test_matching.py -v

# Run tests matching pattern
python -m pytest tests/ -k "test_eligibility" -v

# Run with parallel execution
python -m pytest tests/ -n auto
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

### Integration Tests

```bash
# Start test infrastructure
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis

# Run integration tests
cd backend && python -m pytest tests/integration/ -v --tb=short
```

### End-to-End Tests

```bash
cd frontend
npm run test:e2e
```

---

## Code Style Guide

### Python (Backend)

We use **Ruff** for linting and formatting, and **mypy** for type checking.

```bash
# Lint
cd backend && ruff check .

# Format
ruff format .

# Type check
mypy app/ --config-file pyproject.toml
```

**Key conventions:**
- Use type hints for all function signatures
- Use `async/await` for all database operations
- Use Pydantic v2 for all data validation
- Docstrings: Google style
- Max line length: 100 characters
- Import order: stdlib → third-party → local (enforced by ruff)

**Example:**
```python
"""Candidate service for profile management."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import CandidateProfile
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CandidateService:
    """Handles candidate profile operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: int) -> Optional[CandidateProfile]:
        """Retrieve candidate profile by user ID.

        Args:
            user_id: The user's ID.

        Returns:
            Candidate profile or None if not found.
        """
        result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
```

### TypeScript (Frontend)

We use **ESLint** and **TypeScript strict mode**.

```bash
cd frontend

# Lint
npm run lint

# Type check
npx tsc --noEmit
```

**Key conventions:**
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use Zustand for client state
- Use TanStack Query for server state
- Component files: `kebab-case.tsx`
- Type files: `kebab-case.ts`
- Use `interface` for object shapes, `type` for unions/intersections

---

## Git Workflow

### Branch Strategy

```
main          ← Production releases
  └── develop ← Integration branch
       ├── feature/add-ml-ranking
       ├── feature/candidate-dashboard
       ├── fix/allocation-timeout
       └── chore/update-dependencies
```

### Branch Naming

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New features | `feature/add-ml-ranking` |
| `fix/` | Bug fixes | `fix/allocation-timeout` |
| `chore/` | Maintenance | `chore/update-deps` |
| `docs/` | Documentation | `docs/api-reference` |
| `refactor/` | Code refactoring | `refactor/simplify-scoring` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `ci`

**Examples:**
```
feat(matching): add semantic search stage to pipeline
fix(allocation): handle zero-capacity opportunities gracefully
docs(api): add allocation endpoint documentation
test(fairness): add unit tests for category boost calculation
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with conventional commits
3. Write/update tests
4. Update documentation if needed
5. Push branch and create PR
6. Ensure CI passes
7. Request code review
8. Address review comments
9. Squash merge to `develop`

---

## Debugging Tips

### Backend Debugging

**Enable SQL query logging:**
```bash
# In .env
DB_ECHO=true
SQL_ECHO=true
```

**Debug with breakpoints:**
```python
# Add to code
import pdb; pdb.set_trace()
# Or use IDE debugger with uvicorn --reload
```

**View application logs:**
```bash
# Docker logs
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend

# Or direct uvicorn
cd backend && uvicorn app.main:app --reload --log-level debug
```

**Check database state:**
```bash
# Via Docker
docker exec -it pm-postgres psql -U pm_admin -d pm_internship

# Useful queries
SELECT count(*) FROM candidate_profiles;
SELECT count(*) FROM matches WHERE status = 'pending';
SELECT * FROM allocation_cycles ORDER BY created_at DESC LIMIT 5;
```

**Check Redis cache:**
```bash
docker exec -it pm-redis redis-cli
> KEYS *
> GET candidate:1:recommendations
```

### Frontend Debugging

**Browser DevTools:**
- Network tab: Check API calls and responses
- React DevTools: Inspect component tree and state
- Console: Check for errors and warnings

**Debug API calls:**
```typescript
// In browser console
localStorage.setItem('debug', 'api:*')
```

### Matching Pipeline Debugging

**Test individual scoring components:**
```python
from app.services.matching_service import MatchingService

service = MatchingService(db)

# Test skill similarity
candidate = await get_candidate(1)
opportunity = await get_opportunity(5)
score = service._skill_similarity(candidate, opportunity)
print(f"Skill similarity: {score}")

# Test full pipeline
matches = await service.get_recommendations(candidate_id=1, top_k=5)
for m in matches:
    print(f"Opp {m.opportunity_id}: {m.score:.3f} - {m.explanation}")
```

---

## Adding New Modules

### 1. Create Module Structure

```bash
mkdir -p backend/app/modules/my_module
touch backend/app/modules/my_module/__init__.py
```

### 2. Add Models

```python
# backend/app/models/my_entity.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class MyEntity(BaseModel):
    __tablename__ = "my_entities"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
```

### 3. Create Schemas

```python
# backend/app/schemas/my_entity.py
from pydantic import BaseModel, Field

class MyEntityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None

class MyEntityResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}
```

### 4. Add API Endpoints

```python
# backend/app/api/v1/my_entities.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_session, get_current_user
from app.models.user import User

router = APIRouter(prefix="/my-entities", tags=["My Entities"])

@router.get("/")
async def list_entities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    # Implementation
    pass
```

### 5. Register Router

```python
# backend/app/api/v1/router.py
from app.api.v1.my_entities import router as my_entities_router
v1_router.include_router(my_entities_router)
```

### 6. Create Migration

```bash
cd backend
alembic revision --autogenerate -m "add my_entities table"
alembic upgrade head
```

### 7. Write Tests

```python
# backend/tests/test_my_entities.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_entity(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/my-entities/",
        json={"name": "Test Entity", "description": "A test"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Entity"
```
