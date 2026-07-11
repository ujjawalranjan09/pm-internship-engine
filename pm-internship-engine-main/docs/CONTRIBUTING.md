# Contributing Guide

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. By participating in this project, you agree to:

- **Be respectful**: Treat all contributors with dignity. Disagreements are fine; personal attacks are not.
- **Be inclusive**: Welcome contributors of all backgrounds, skill levels, and identities.
- **Be constructive**: Provide helpful feedback. Critique code, not people.
- **Be patient**: Not everyone has the same experience level. Help others learn.
- **Report issues**: If you witness or experience unacceptable behavior, report it to the project maintainers.

Unacceptable behavior includes harassment, trolling, derogatory comments, personal attacks, and publishing others' private information without consent.

---

## Development Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Docker & Docker Compose** (for PostgreSQL, Redis, OpenSearch)
- **Git**

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-org/pm-internship-engine.git
cd pm-internship-engine

# Start infrastructure services
cd backend
docker compose up -d postgres redis opensearch

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

### Environment Variables

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pm_internship
REDIS_URL=redis://localhost:6379/0
OPENSEARCH_URL=https://localhost:9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true
```

### Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# Database connection
cd backend && python -c "from app.core.database import engine; print('DB OK')"
```

---

## Git Workflow

### Branch Naming

```
feature/<description>    — New features
fix/<description>        — Bug fixes
docs/<description>       — Documentation changes
refactor/<description>   — Code refactoring
test/<description>       — Test additions/fixes
chore/<description>      — Build, CI, dependency updates
```

Examples:
```
feature/fairness-dashboard
fix/allocation-capacity-overflow
docs/matching-algorithm-guide
refactor/extract-scorer-weights
```

### Workflow

```
main (production-ready)
  │
  ├── develop (integration branch)
  │     │
  │     ├── feature/new-scoring-component
  │     ├── fix/eligibility-edge-case
  │     └── docs/api-documentation
  │
  └── release/1.2.0 (release candidates)
```

### Step-by-Step

1. **Start from `develop`**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat(matching): add semantic similarity scoring component"
   ```

3. **Keep your branch updated**
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

4. **Push and create a Pull Request**
   ```bash
   git push origin feature/my-feature
   ```

5. **After review approval, merge via PR**

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build process, dependencies, CI |
| `perf` | Performance improvement |

**Scopes:** `matching`, `allocation`, `fairness`, `api`, `frontend`, `db`, `config`, `ci`

**Examples:**
```
feat(matching): add hybrid retrieval with pgvector
fix(allocation): handle zero-capacity opportunity edge case
docs(api): add authentication flow documentation
refactor(fairness): extract boost calculation to separate module
test(matching): add unit tests for skill similarity scoring
chore(deps): upgrade SQLAlchemy to 2.0.35
```

---

## Code Review Process

### Opening a Pull Request

1. **Fill out the PR template** completely:
   - What does this PR do?
   - How was it tested?
   - Any breaking changes?
   - Related issues

2. **Ensure CI passes** before requesting review

3. **Keep PRs focused**: One feature/fix per PR. Large changes should be split.

4. **Add screenshots/recordings** for UI changes

### Review Checklist

Reviewers should check:

**Correctness**
- [ ] Does the code do what it claims?
- [ ] Are edge cases handled?
- [ ] Are error cases handled gracefully?

**Code Quality**
- [ ] Is the code readable and well-structured?
- [ ] Are functions/methods reasonably sized?
- [ ] Are names descriptive and consistent?
- [ ] No code duplication that should be extracted?

**Testing**
- [ ] Are there adequate tests?
- [ ] Do tests cover happy path and error cases?
- [ ] Are tests deterministic (no flaky behavior)?

**Security**
- [ ] No hardcoded secrets or credentials?
- [ ] Input validation present?
- [ ] SQL injection / XSS prevention?
- [ ] Authentication/authorization correct?

**Performance**
- [ ] No N+1 queries?
- [ ] Appropriate use of indexes?
- [ ] No unnecessary data loading?

### Review Etiquette

- **Authors**: Don't take feedback personally. Reviews improve code quality.
- **Reviewers**: Be specific and constructive. Suggest solutions, not just problems.
- **Both**: Resolve all conversations before merging.

### Approval Requirements

- **Minimum 1 approval** from a code owner
- **All CI checks passing**
- **No unresolved conversations**
- **Branch up to date with `develop`**

---

## Testing Requirements

### Test Structure

```
backend/
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── unit/
│   │   ├── test_eligibility.py
│   │   ├── test_matching.py
│   │   ├── test_fairness.py
│   │   └── test_allocation.py
│   ├── integration/
│   │   ├── test_api_candidates.py
│   │   ├── test_api_matching.py
│   │   └── test_api_allocation.py
│   └── e2e/
│       └── test_full_pipeline.py
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_matching.py -v

# Run tests matching a pattern
pytest -k "test_skill_similarity" -v
```

### Writing Tests

**Unit tests** — test individual functions in isolation:

```python
# tests/unit/test_matching.py
import pytest
from app.services.matching_service import MatchingService

class TestSkillSimilarity:
    def test_perfect_match(self):
        """All required skills present → score 1.0"""
        service = MatchingService.__new__(MatchingService)
        candidate_skills = {"python", "sql", "pandas"}
        required_skills = {"python", "sql"}
        # ... assert score == 1.0

    def test_no_overlap(self):
        """No matching skills → score 0.0"""
        # ...

    def test_partial_match(self):
        """Some skills match → proportional score"""
        # ...

    def test_no_required_skills(self):
        """No required skills specified → neutral 0.5"""
        # ...
```

**Integration tests** — test API endpoints with database:

```python
# tests/integration/test_api_matching.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_recommendations(client: AsyncClient, auth_headers: dict):
    """GET /api/v1/matching/recommendations returns scored matches"""
    response = await client.get(
        "/api/v1/matching/recommendations?top_k=5",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
    assert all("score" in match for match in data)
```

### Coverage Requirements

- **Minimum overall coverage**: 80%
- **New code coverage**: 90%+
- **Critical paths** (matching, allocation, fairness): 95%+

### Test Data

Use fixtures for consistent test data:

```python
# tests/conftest.py
@pytest.fixture
def sample_candidate():
    return CandidateProfile(
        full_name="Test Candidate",
        education={"degree": "b.tech", "field_of_study": "computer science"},
        skills=["python", "sql", "machine learning"],
        state="karnataka",
        district="bangalore",
        social_category="general",
        is_rural=False,
        profile_completion_score=0.85,
    )

@pytest.fixture
def sample_opportunity():
    return Opportunity(
        title="Data Science Intern",
        description="Work on ML models",
        sector="technology",
        required_skills=["python", "machine learning"],
        state="karnataka",
        district="bangalore",
        capacity=5,
        eligibility_criteria={"min_education": "bachelors"},
    )
```

---

## Documentation Standards

### Code Documentation

**All public functions** must have docstrings:

```python
def rerank(
    self,
    candidate: CandidateProfile,
    scored: list[tuple[Opportunity, float, dict[str, float]]],
) -> list[tuple[Opportunity, float, dict[str, float]]]:
    """Apply fairness-aware re-ranking to scored matches.

    Adjusts scores based on candidate's social category and rural status
    to ensure historically disadvantaged groups receive equitable access.

    Args:
        candidate: The candidate profile with demographic information.
        scored: List of (opportunity, score, breakdown) tuples sorted by score.

    Returns:
        Re-ranked list with fairness adjustments applied, sorted by
        adjusted score in descending order.

    Raises:
        ValueError: If scored list contains invalid score values.
    """
```

**Type annotations** are mandatory for all function signatures:

```python
# ✅ Good
def compute_score(candidate: CandidateProfile, opportunity: Opportunity) -> float:
    ...

# ❌ Bad
def compute_score(candidate, opportunity):
    ...
```

### API Documentation

All API endpoints must have:
- OpenAPI schema (auto-generated from FastAPI)
- Request/response examples
- Error response documentation

### Architecture Documentation

Update `docs/ARCHITECTURE.md` when:
- Adding new services or modules
- Changing the matching pipeline
- Modifying data flow patterns
- Adding new infrastructure components

### Changelog

Maintain a `CHANGELOG.md` with entries for each release:

```markdown
## [1.2.0] - 2025-02-01

### Added
- Semantic similarity scoring using pgvector embeddings
- Aspirational district boost in fairness policy
- District representation targets in allocation

### Changed
- Increased default skill_match weight from 0.25 to 0.30
- Improved OR-Tools solver performance by 40%

### Fixed
- Edge case where zero-capacity opportunities caused allocation failure
- Fairness boost exceeding max_total_adjustment for rural SC candidates
```

---

## Project Structure

```
pm-internship-engine/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API route handlers
│   │   ├── core/            # Config, database, security
│   │   ├── ml/              # ML models, embeddings, scoring
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── modules/         # Business domain modules
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   └── services/        # Business logic services
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test suite
│   ├── docker-compose.yml   # Infrastructure services
│   ├── Dockerfile           # Backend container
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client services
│   │   ├── stores/          # Zustand state stores
│   │   └── types/           # TypeScript type definitions
│   └── package.json
├── docs/                    # Project documentation
├── scripts/                 # Utility scripts
└── README.md
```

---

## Getting Help

- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check `docs/` for architecture, API, and deployment guides
- **Code**: Read existing code for patterns and conventions

## Recognition

All contributors are recognized in the project README. Significant contributions may earn maintainer status.
