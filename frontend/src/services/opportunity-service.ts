import { apiGet, apiPost, apiPut } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse, PaginatedResponse } from "@/types/common";
import type {
  Opportunity,
  OpportunityListItem,
  CreateOpportunityRequest,
  OpportunityFilter,
} from "@/types/opportunity";

const MOCK_OPPORTUNITIES: OpportunityListItem[] = [
  {
    id: "o1",
    title: "Software Development Intern",
    employerName: "TechCorp India",
    sector: "Information Technology",
    location: "Bangalore",
    state: "Karnataka",
    stipend: 15000,
    duration: 6,
    durationMonths: 6,
    capacity: 50,
    filledSlots: 32,
    requiredSkills: ["Python", "React", "SQL"],
    isActive: true,
    matchScore: 87,
    workMode: "Hybrid",
    description: "Build modern web applications with a product engineering team.",
    createdAt: "2024-10-01T10:00:00Z",
  },
  {
    id: "o2",
    title: "Data Analytics Intern",
    employerName: "FinServ Ltd",
    sector: "Finance & Banking",
    location: "Mumbai",
    state: "Maharashtra",
    stipend: 12000,
    duration: 4,
    durationMonths: 4,
    capacity: 30,
    filledSlots: 18,
    requiredSkills: ["Excel", "SQL", "Data Analysis"],
    isActive: true,
    matchScore: 72,
    workMode: "Onsite",
    description: "Analyze dashboards, reports, and business KPIs.",
    createdAt: "2024-10-05T10:00:00Z",
  },
];

const MOCK_OPPORTUNITY_DETAIL: Opportunity = {
  id: "o1",
  employerId: "emp_001",
  employerName: "TechCorp India",
  title: "Software Development Intern",
  description:
    "Join our engineering team to work on cutting-edge web applications. You will gain hands-on experience with modern technologies including React, Node.js, and cloud platforms. This internship offers mentorship from senior engineers and real project contributions.",
  sector: "Information Technology",
  location: "Bangalore",
  state: "Karnataka",
  district: "Bengaluru Urban",
  stipend: 15000,
  duration: 6,
  capacity: 50,
  filledSlots: 32,
  requiredSkills: ["Python", "React", "SQL", "Git"],
  eligibilityCriteria: {
    minEducation: "Undergraduate",
    minPercentage: 60,
    allowedCategories: ["General", "OBC", "SC", "ST", "EWS"],
  },
  startDate: "2025-01-15",
  endDate: "2025-07-15",
  isActive: true,
  createdAt: "2024-10-01T10:00:00Z",
  updatedAt: "2024-12-15T14:30:00Z",
};

export async function getOpportunities(
  page = 1,
  pageSize = 20,
  filters?: OpportunityFilter
): Promise<PaginatedResponse<OpportunityListItem>> {
  try {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
    if (filters?.sector) params.set("sector", filters.sector);
    if (filters?.state) params.set("state", filters.state);
    if (filters?.skills) params.set("skills", filters.skills.join(","));
    return await apiGet<PaginatedResponse<OpportunityListItem>>(
      `${API_ROUTES.OPPORTUNITIES.LIST}?${params}`
    );
  } catch {
    return {
      items: MOCK_OPPORTUNITIES,
      total: MOCK_OPPORTUNITIES.length,
      page,
      pageSize,
      totalPages: 1,
    };
  }
}

export async function getOpportunityDetail(id: string): Promise<Opportunity> {
  try {
    const response = await apiGet<ApiResponse<Opportunity>>(API_ROUTES.OPPORTUNITIES.DETAIL(id));
    return response.data;
  } catch {
    return { ...MOCK_OPPORTUNITY_DETAIL, id };
  }
}

export async function createOpportunity(data: CreateOpportunityRequest): Promise<Opportunity> {
  try {
    const response = await apiPost<ApiResponse<Opportunity>>(API_ROUTES.OPPORTUNITIES.CREATE, data);
    return response.data;
  } catch {
    return {
      ...MOCK_OPPORTUNITY_DETAIL,
      id: `o_${Date.now()}`,
      ...data,
    };
  }
}

export async function updateOpportunity(
  id: string,
  data: Partial<CreateOpportunityRequest>
): Promise<Opportunity> {
  try {
    const response = await apiPut<ApiResponse<Opportunity>>(API_ROUTES.OPPORTUNITIES.UPDATE(id), data);
    return response.data;
  } catch {
    return { ...MOCK_OPPORTUNITY_DETAIL, id, ...data } as Opportunity;
  }
}
