import { apiGet, apiPost } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { PaginatedResponse } from "@/types/common";
import type { MatchRecommendation, Match } from "@/types/match";

const MOCK_RECOMMENDATIONS: MatchRecommendation[] = [
  {
    opportunityId: "o1",
    title: "Software Development Intern",
    employerName: "TechCorp India",
    sector: "Information Technology",
    location: "Bangalore",
    stipend: 15000,
    matchScore: 87,
    explanation: "Strong match based on Python and React skills.",
    topFactors: [
      { name: "Skill Match", weight: 0.35, score: 92, description: "3 of 4 required skills matched" },
      { name: "Education", weight: 0.25, score: 85, description: "B.Tech in CS meets requirements" },
      { name: "Location", weight: 0.2, score: 70, description: "Preferred location" },
      { name: "Preference", weight: 0.2, score: 90, description: "IT sector is top preference" },
    ],
    workMode: "hybrid",
    duration: 6,
    skills: ["Python", "React", "SQL"],
  },
  {
    opportunityId: "o2",
    title: "Data Analytics Intern",
    employerName: "FinServ Ltd",
    sector: "Finance & Banking",
    location: "Mumbai",
    stipend: 12000,
    matchScore: 72,
    explanation: "Good match with SQL and analytical skills.",
    topFactors: [
      { name: "Skill Match", weight: 0.35, score: 65, description: "2 of 3 required skills matched" },
      { name: "Education", weight: 0.25, score: 80, description: "Quantitative background fits" },
      { name: "Location", weight: 0.2, score: 95, description: "Mumbai is home city" },
      { name: "Preference", weight: 0.2, score: 55, description: "Finance is secondary preference" },
    ],
    workMode: "onsite",
    duration: 4,
    skills: ["Excel", "SQL", "Data Analysis"],
  },
];

const MOCK_MATCHES: Match[] = [
  {
    id: "m1",
    candidateId: "c1",
    candidateName: "Priya Sharma",
    opportunityId: "o1",
    opportunityTitle: "Software Development Intern",
    employerName: "TechCorp India",
    overallScore: 87,
    skillScore: 92,
    locationScore: 70,
    educationScore: 85,
    preferenceScore: 90,
    fairnessScore: 78,
    explanation: "Strong overall match with excellent skill alignment.",
    factors: [],
    createdAt: "2024-12-01T10:00:00Z",
  },
  {
    id: "m2",
    candidateId: "c2",
    candidateName: "Rahul Kumar",
    opportunityId: "o2",
    opportunityTitle: "Data Analytics Intern",
    employerName: "FinServ Ltd",
    overallScore: 72,
    skillScore: 65,
    locationScore: 95,
    educationScore: 80,
    preferenceScore: 55,
    fairnessScore: 82,
    explanation: "Good match with strong location alignment.",
    factors: [],
    createdAt: "2024-12-01T10:00:00Z",
  },
];

export async function getRecommendations(): Promise<MatchRecommendation[]> {
  try {
    return await apiGet<MatchRecommendation[]>(API_ROUTES.MATCHING.MY_MATCHES);
  } catch {
    return MOCK_RECOMMENDATIONS;
  }
}

export async function getMatchesForOpportunity(opportunityId: string): Promise<Match[]> {
  try {
    return await apiGet<Match[]>(`${API_ROUTES.MATCHING.MATCHES}?opportunityId=${opportunityId}`);
  } catch {
    return MOCK_MATCHES.filter((m) => m.opportunityId === opportunityId);
  }
}

export async function triggerMatching(): Promise<void> {
  try {
    await apiPost(API_ROUTES.MATCHING.TRIGGER, {});
  } catch {
    await new Promise((r) => setTimeout(r, 1000));
  }
}

export async function triggerBatchMatching(): Promise<void> {
  try {
    await apiPost(API_ROUTES.MATCHING.BATCH_TRIGGER, {});
  } catch {
    await new Promise((r) => setTimeout(r, 1500));
  }
}