#!/usr/bin/env python3
"""
Seed realistic test data for the PM Internship Allocation Engine.
Generates candidates, opportunities, matches, and allocation cycles.
"""

import asyncio
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
settings = get_settings()
from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.opportunity import Opportunity
from app.models.match import Match
from app.models.allocation_cycle import AllocationCycle

# ── Realistic data pools ──────────────────────────────────────────

SKILLS_TAXONOMY = {
    "IT": ["Python", "Java", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS", "Git", "TypeScript", "MongoDB", "Linux"],
    "Data Science": ["Python", "R", "Machine Learning", "Deep Learning", "TensorFlow", "Pandas", "NumPy", "SQL", "Tableau", "Power BI"],
    "Finance": ["Financial Analysis", "Excel", "Accounting", "Tally", "GST", "Taxation", "Audit", "SAP", "Bloomberg Terminal"],
    "Healthcare": ["Patient Care", "Medical Records", "Clinical Research", "Pharmacology", "First Aid", "Health Informatics"],
    "Manufacturing": ["AutoCAD", "SolidWorks", "Lean Manufacturing", "Six Sigma", "Quality Control", "CNC Programming"],
    "Marketing": ["Digital Marketing", "SEO", "Social Media", "Content Writing", "Google Analytics", "Brand Management", "Canva"],
    "Education": ["Teaching", "Curriculum Design", "EdTech", "Public Speaking", "Content Development", "LMS"],
    "Agriculture": ["Crop Management", "Organic Farming", "Soil Analysis", "AgriTech", "Supply Chain", "Irrigation"],
}

DEGREES = [
    ("B.Tech", "Computer Science"), ("B.Tech", "Electronics"), ("B.Tech", "Mechanical"),
    ("B.Tech", "Civil"), ("B.Tech", "Electrical"), ("B.Sc", "Physics"), ("B.Sc", "Mathematics"),
    ("B.Sc", "Computer Science"), ("B.Com", "General"), ("B.Com", "Honours"),
    ("BBA", "General"), ("BCA", "General"), ("M.Tech", "Computer Science"),
    ("MBA", "Finance"), ("MBA", "Marketing"), ("MBA", "HR"), ("MCA", "General"),
    ("M.Sc", "Data Science"), ("M.Sc", "Mathematics"), ("MA", "Economics"),
]

STATES_DISTRICTS = {
    "Uttar Pradesh": ["Lucknow", "Varanasi", "Agra", "Noida", "Prayagraj", "Gorakhpur", "Kanpur"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
}

ASPIRATIONAL_DISTRICTS = [
    "Gorakhpur", "Gaya", "Muzaffarpur", "Darbhanga", "Sambalpur",
    "Berhampur", "Ajmer", "Ujjain", "Asansol", "Belagavi",
]

SECTORS = list(SKILLS_TAXONOMY.keys())

CATEGORIES = ["General", "OBC", "SC", "ST"]
CATEGORY_WEIGHTS = [0.40, 0.30, 0.20, 0.10]

COMPANIES = [
    "TechVision India", "Digital Bharat Solutions", "GreenEnergy Corp",
    "FinServe Analytics", "HealthBridge India", "AgriTech Innovations",
    "ManufacturePro India", "EduLearn Platform", "DataMinds AI",
    "SmartCity Solutions", "Bharat Pharmaceuticals", "RetailMax India",
    "CloudScale Systems", "CyberShield India", "AutoDrive Technologies",
    "BioResearch Labs", "MediaWorks Digital", "InfraBuild Construction",
    "LogiChain Supply", "NanoTech Materials",
]


def generate_candidates(n: int = 100) -> list[dict]:
    """Generate n realistic candidate profiles."""
    candidates = []
    states = list(STATES_DISTRICTS.keys())

    for i in range(n):
        state = random.choice(states)
        district = random.choice(STATES_DISTRICTS[state])
        degree, specialization = random.choice(DEGREES)
        sector = random.choice(SECTORS)
        skills = random.sample(SKILLS_TAXONOMY[sector], min(random.randint(2, 5), len(SKILLS_TAXONOMY[sector])))
        # Add some cross-sector skills
        other_sector = random.choice(SECTORS)
        skills += random.sample(SKILLS_TAXONOMY[other_sector], min(2, len(SKILLS_TAXONOMY[other_sector])))
        skills = list(set(skills))

        candidates.append({
            "id": i + 1,
            "full_name": f"Candidate_{i+1:03d}",
            "email": f"candidate{i+1}@test.in",
            "phone": f"98{random.randint(10000000, 99999999)}",
            "education_degree": degree,
            "education_specialization": specialization,
            "education_college": f"{state} Institute of Technology",
            "education_year": random.randint(2022, 2026),
            "education_cgpa": round(random.uniform(6.0, 9.8), 2),
            "skills": skills,
            "state": state,
            "district": district,
            "social_category": random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0],
            "is_rural": random.random() < 0.45,
            "is_aspirational_district": district in ASPIRATIONAL_DISTRICTS,
            "gender": random.choice(["Male", "Female", "Other"]),
            "prior_internships": random.choices([0, 1, 2, 3], weights=[0.6, 0.25, 0.10, 0.05])[0],
            "profile_completion_score": round(random.uniform(0.5, 1.0), 2),
            "sector_interests": [sector, other_sector],
            "mobility_preferences": random.choice(["local", "state", "national"]),
            "resume_url": f"s3://resumes/candidate_{i+1}.pdf",
        })

    return candidates


def generate_opportunities(n: int = 50) -> list[dict]:
    """Generate n realistic internship opportunities."""
    opportunities = []
    states = list(STATES_DISTRICTS.keys())

    for i in range(n):
        sector = random.choice(SECTORS)
        state = random.choice(states)
        district = random.choice(STATES_DISTRICTS[state])
        company = random.choice(COMPANIES)
        skills = random.sample(SKILLS_TAXONOMY[sector], min(random.randint(2, 4), len(SKILLS_TAXONOMY[sector])))
        work_mode = random.choice(["onsite", "remote", "hybrid"])

        opportunities.append({
            "id": i + 1,
            "title": f"{sector} Intern - {company}",
            "description": f"Exciting {sector} internship opportunity at {company}. "
                          f"Gain hands-on experience in {', '.join(skills[:3])}. "
                          f"Work with industry experts on real-world projects.",
            "employer_id": random.randint(1, 20),
            "company_name": company,
            "sector": sector,
            "required_skills": skills,
            "state": state,
            "district": district,
            "location": f"{district}, {state}",
            "work_mode": work_mode,
            "capacity": random.choice([5, 10, 15, 20, 25, 30, 50]),
            "stipend": random.choice([5000, 8000, 10000, 12000, 15000, 20000, 25000]),
            "duration_months": random.choice([3, 6, 12]),
            "eligibility_criteria": {
                "min_cgpa": round(random.uniform(6.0, 8.0), 1),
                "min_year": random.choice([2023, 2024, 2025]),
                "required_degree": random.choice(["B.Tech", "B.Sc", "B.Com", "Any"]),
            },
            "is_active": True,
        })

    return opportunities


def generate_matches(candidates: list[dict], opportunities: list[dict], n: int = 500) -> list[dict]:
    """Generate candidate-opportunity match scores."""
    matches = []

    for i in range(n):
        cand = random.choice(candidates)
        opp = random.choice(opportunities)

        # Compute a realistic score
        skill_overlap = len(set(cand["skills"]) & set(opp["required_skills"]))
        max_skills = max(len(cand["skills"]), len(opp["required_skills"]))
        skill_score = skill_overlap / max_skills if max_skills > 0 else 0

        location_score = 1.0 if cand["state"] == opp["state"] else 0.3
        sector_score = 1.0 if opp["sector"] in cand.get("sector_interests", []) else 0.2

        base_score = 0.30 * skill_score + 0.15 * location_score + 0.10 * sector_score + 0.45 * random.uniform(0.3, 1.0)
        base_score = round(min(base_score, 1.0), 4)

        matches.append({
            "candidate_id": cand["id"],
            "opportunity_id": opp["id"],
            "score": base_score,
            "score_breakdown": {
                "skill_match": round(skill_score, 4),
                "location_fit": round(location_score, 4),
                "sector_alignment": round(sector_score, 4),
                "profile_readiness": round(random.uniform(0.5, 1.0), 4),
            },
            "explanation": f"Candidate has {skill_overlap} matching skills for {opp['title']}. "
                          f"{'Located in same state.' if location_score > 0.5 else 'Different state.'}",
            "rank": 0,  # Will be computed during allocation
            "status": "pending",
        })

    return matches


async def seed():
    """Main seeding function."""
    print("[seed] Starting database seeding...")

    DATABASE_URL = settings.DATABASE_URL

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Generate data
    candidates = generate_candidates(100)
    opportunities = generate_opportunities(50)
    matches = generate_matches(candidates, opportunities, 500)

    async with session_factory() as session:
        # Create admin user (matching demo login button)
        admin = User(
            email="admin@gov.in",
            password_hash=hash_password("password123"),
            role="admin",
            is_active=True,
        )
        session.add(admin)

        # Create employer users (for opportunity FK)
        for i in range(1, 21):
            emp = User(
                email=f"employer{i}@gov.in",
                password_hash=hash_password("password123"),
                role="employer",
                is_active=True,
            )
            session.add(emp)

        # Create candidate users and profiles
        for c in candidates:
            user = User(
                email=c["email"],
                password_hash=hash_password("password123"),
                role="candidate",
                is_active=True,
            )
            session.add(user)
            await session.flush()

            profile = CandidateProfile(
                user_id=user.id,
                full_name=c["full_name"],
                phone=c["phone"],
                education={
                    "degree": c["education_degree"],
                    "specialization": c["education_specialization"],
                    "college": c["education_college"],
                    "year": c["education_year"],
                    "cgpa": c["education_cgpa"],
                },
                skills=c["skills"],
                location=c["district"],
                district=c["district"],
                state=c["state"],
                social_category=c["social_category"],
                is_rural=c["is_rural"],
                resume_url=c["resume_url"],
                profile_completion_score=c["profile_completion_score"],
                mobility_preferences={"type": c["mobility_preferences"]},
            )
            session.add(profile)

        # Create demo employer user (matching login button)
        demo_emp = User(
            email="employer@gov.in",
            password_hash=hash_password("password123"),
            role="employer",
            is_active=True,
        )
        session.add(demo_emp)
        await session.flush()

        # Create demo candidate user (matching login button)
        demo_cand = User(
            email="candidate@gov.in",
            password_hash=hash_password("password123"),
            role="candidate",
            is_active=True,
        )
        session.add(demo_cand)
        await session.flush()

        demo_profile = CandidateProfile(
            user_id=demo_cand.id,
            full_name="Demo Candidate",
            phone="9800000000",
            education={
                "degree": "B.Tech",
                "specialization": "Computer Science",
                "college": "Delhi Institute of Technology",
                "year": 2024,
                "cgpa": 8.5,
            },
            skills=["Python", "React", "SQL", "Docker"],
            location="New Delhi",
            district="New Delhi",
            state="Delhi",
            social_category="General",
            is_rural=False,
            resume_url="s3://resumes/demo_candidate.pdf",
            profile_completion_score=1.0,
            mobility_preferences={"type": "national"},
        )
        session.add(demo_profile)

        # Create opportunities
        for o in opportunities:
            opp = Opportunity(
                employer_id=o["employer_id"],
                title=o["title"],
                description=o["description"],
                sector=o["sector"],
                required_skills=o["required_skills"],
                location=o["location"],
                state=o["state"],
                district=o["district"],
                work_mode=o["work_mode"],
                capacity=o["capacity"],
                stipend=o["stipend"],
                duration_months=o["duration_months"],
                eligibility_criteria=o["eligibility_criteria"],
                is_active=o["is_active"],
            )
            session.add(opp)

        # Create allocation cycles
        for name, status, days_ago in [
            ("Summer 2025 - Cycle 1", "completed", 90),
            ("Winter 2025 - Cycle 2", "running", 10),
            ("Spring 2026 - Cycle 3", "draft", 0),
        ]:
            cycle = AllocationCycle(
                name=name,
                status=status,
                config={
                    "weights": {
                        "skill_match": 0.30,
                        "qualification_fit": 0.15,
                        "sector_interest": 0.10,
                        "location_preference": 0.10,
                        "profile_readiness": 0.10,
                        "employer_preference": 0.10,
                        "historical_adjustment": 0.05,
                        "semantic_similarity": 0.10,
                    },
                    "fairness_enabled": True,
                    "aspirational_bonus": 0.05,
                },
                started_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
                completed_at=(
                    datetime.now(timezone.utc) - timedelta(days=days_ago - 2)
                    if status == "completed" else None
                ),
            )
            session.add(cycle)

        await session.commit()

    print(f"✅ Seeded {len(candidates)} candidates")
    print(f"✅ Seeded {len(opportunities)} opportunities")
    print(f"✅ Seeded {len(matches)} matches")
    print(f"✅ Seeded 3 allocation cycles")
    print(f"✅ Seeded 1 admin user (admin@gov.in / password123)")
    print(f"✅ Seeded 20 employer users (employer1..20@gov.in / password123)")
    print(f"✅ Seeded demo employer (employer@gov.in / password123)")
    print(f"✅ Seeded demo candidate (candidate@gov.in / password123)")
    print("🎉 Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
