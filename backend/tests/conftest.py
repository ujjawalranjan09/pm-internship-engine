"""Shared test fixtures and configuration."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base


# Use SQLite for tests (no PostgreSQL dependency)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for tests."""
    async with TestSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
def sample_candidate_data() -> dict:
    """Sample candidate profile data for tests."""
    return {
        "full_name": "Priya Sharma",
        "phone": "9876543210",
        "education": {"degree": "bachelors", "institution": "IIT Delhi", "year_of_passing": 2024, "field_of_study": "Computer Science"},
        "skills": ["python", "machine learning", "data analysis", "sql"],
        "location": "New Delhi",
        "district": "South Delhi",
        "state": "Delhi",
        "social_category": "general",
        "is_rural": False,
        "mobility_preferences": {"willing_to_relocate": True, "remote_work_ok": True},
    }


@pytest.fixture
def sample_opportunity_data() -> dict:
    """Sample opportunity data for tests."""
    return {
        "title": "Data Science Intern",
        "description": "Work on ML models for predictive analytics in the agriculture sector.",
        "sector": "technology",
        "required_skills": ["python", "machine learning", "data analysis"],
        "location": "Bangalore",
        "state": "Karnataka",
        "district": "Bangalore Urban",
        "work_mode": "hybrid",
        "capacity": 5,
        "stipend": 25000.0,
        "duration_months": 6,
        "eligibility_criteria": {
            "min_education": "bachelors",
            "field_of_study": "Computer Science",
        },
    }
