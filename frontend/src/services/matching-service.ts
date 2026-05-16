import { apiGet, apiPost } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse } from "@/types/common";
import type { Match, MatchRecommendation } from "@/types/match";

const MOCK_RECOMMENDATIONS: MatchRecommendation[] = [
  {
    opportunityId: "o1",
    title: "Software Development Intern",
    employerName: "TechCorp India",
    sector: "Information Technology",
    location: "Bangalore",
    stipend: 15000,
    matchScore: 87,
    workMode: "Hybrid",
    duration: 6,
    skills: ["Python", "React", "SQL"],
    explanation: "Strong match based on Python and React skills, aligning with the tech stack requirements. Location preference partially met.",
    topFactors: [
      { name: "Skill Match", weight: 0.35, score: 92, description: "3 of 4 required skills matched" },
      { name: "Education", weight: 0.25, score: 85, description: "B.Tech in CS meets requirements" },
      { name: "Location", weight: 0.2, score: 70, description: "Preferred location, different from current" },
      { name: "Preference", weight: 0.2, score: 90, description: "IT sector is top preference" },
    ],
  },
  {
    opportunityId: "o2",
    title: "Data Analytics Intern",
    employerName: "FinServ Ltd",
    sector: "Finance & Banking",
    location: "Mumbai",
    stipend: 12000,
    matchScore: 72,
    workMode: "Onsite",
    duration: 4,
    skills: ["Excel", "SQL", "Data Analysis"],
    explanation: "Good match with SQL and analytical skills. Finance sector aligns with secondary interest.",
    topFactors: [
      { name: "Skill Match", weight: 0.35, score: 65, description: "2 of 3 required skills matched" },
      { name: "Education", weight: 0.25, score: 80, description: "Quantitative background fits" },
      { name: "Location", weight: 0.2, score: 95, description: "Mumbai is home city" },
      { name: "Preference", weight: 0.2, score: 55, description: "Finance is secondary preference" },
    ],
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
];

export async function getRecommendations(): Promise<MatchRecommendation[]> {
  try {
    const response = await apiGet<ApiResponse<MatchRecommendation[]>>(API_ROUTES.MATCHES.RECOMMENDATIONS);
    return response.data;
  } catch {
    return MOCK_RECOMMENDATIONS;
  }
}

export async function getMatchesForOpportunity(opportunityId: string): Promise<Match[]> {
  try {
    const response = await apiGet<ApiResponse<Match[]>>(API_ROUTES.MATCHES.FOR_OPPORTUNITY(opportunityId));
    return response.data;
  } catch {
    return MOCK_MATCHES;
  }
}

export async function triggerBatchMatching(): Promise<void> {
  try {
    await apiPost(API_ROUTES.MATCHING.TRIGGER, {});
  } catch {
    await new Promise((r) => setTimeout(r, 1000));
  }
}
