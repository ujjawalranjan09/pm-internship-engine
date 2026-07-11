import { apiGet, apiPost, apiPut, apiDelete } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { PaginatedResponse } from "@/types/common";
import type { Opportunity, OpportunityListItem, CreateOpportunityRequest, OpportunityFilter } from "@/types/opportunity";

const MOCK_OPPORTUNITIES: OpportunityListItem[] = [
  { id: "o1", title: "Software Development Intern", employerName: "TechCorp India", sector: "Information Technology", location: "Bangalore", stipend: 15000, duration: 6, capacity: 50, filledSlots: 32, requiredSkills: ["Python", "React", "SQL"], isActive: true, matchScore: 87 },
  { id: "o2", title: "Data Analytics Intern", employerName: "FinServ Ltd", sector: "Finance & Banking", location: "Mumbai", stipend: 12000, duration: 4, capacity: 30, filledSlots: 18, requiredSkills: ["Excel", "SQL", "Data Analysis"], isActive: true, matchScore: 72 },
  { id: "o3", title: "Digital Marketing Intern", employerName: "MediaGroup", sector: "Media & Communications", location: "Delhi", stipend: 10000, duration: 3, capacity: 25, filledSlots: 10, requiredSkills: ["SEO", "Content Writing", "Social Media"], isActive: true, matchScore: 65 },
  { id: "o4", title: "Healthcare Management Intern", employerName: "MedCare Hospital", sector: "Healthcare", location: "Chennai", stipend: 14000, duration: 6, capacity: 20, filledSlots: 8, requiredSkills: ["Healthcare", "Management", "Communication"], isActive: true, matchScore: 58 },
  { id: "o5", title: "Mechanical Engineering Intern", employerName: "AutoMakers India", sector: "Manufacturing", location: "Pune", stipend: 13000, duration: 6, capacity: 40, filledSlots: 25, requiredSkills: ["AutoCAD", "SolidWorks", "Manufacturing"], isActive: true, matchScore: 68 },
  { id: "o6", title: "Cloud Infrastructure Intern", employerName: "CloudFirst", sector: "Information Technology", location: "Hyderabad", stipend: 16000, duration: 6, capacity: 15, filledSlots: 5, requiredSkills: ["AWS", "Docker", "Linux"], isActive: true, matchScore: 79 },
];

const MOCK_OPPORTUNITY_DETAIL: Opportunity = {
  id: "o1",
  employerId: "emp_001",
  employerName: "TechCorp India",
  title: "Software Development Intern",
  description: "Join our engineering team to work on cutting-edge web applications. You will gain hands-on experience with modern technologies including React, Node.js, and cloud platforms. This internship offers mentorship from senior engineers and real project contributions.",
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
    return await apiGet<PaginatedResponse<OpportunityListItem>>(`${API_ROUTES.OPPORTUNITIES.LIST}?${params}`);
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
    return await apiGet<Opportunity>(API_ROUTES.OPPORTUNITIES.DETAIL(id));
  } catch {
    return { ...MOCK_OPPORTUNITY_DETAIL, id };
  }
}

export async function createOpportunity(data: CreateOpportunityRequest): Promise<Opportunity> {
  try {
    return await apiPost<Opportunity>(API_ROUTES.OPPORTUNITIES.CREATE, data);
  } catch {
    return {
      ...MOCK_OPPORTUNITY_DETAIL,
      id: `o_${Date.now()}`,
      ...data,
    };
  }
}

export async function updateOpportunity(id: string, data: Partial<CreateOpportunityRequest>): Promise<Opportunity> {
  try {
    return await apiPut<Opportunity>(API_ROUTES.OPPORTUNITIES.UPDATE(id), data);
  } catch {
    return { ...MOCK_OPPORTUNITY_DETAIL, id, ...data };
  }
}

export async function deleteOpportunity(id: string): Promise<void> {
  try {
    await apiDelete(API_ROUTES.OPPORTUNITIES.DELETE(id));
  } catch {
    // mock no-op
  }
}