import { apiGet, apiPut, apiPost } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse, PaginatedResponse } from "@/types/common";
import type { CandidateProfile, CandidateListItem, CandidateFilter, Education, Skill } from "@/types/candidate";

const MOCK_CANDIDATES: CandidateListItem[] = [
  { id: "c1", name: "Priya Sharma", email: "priya@example.com", state: "Maharashtra", district: "Mumbai", education: "B.Tech Computer Science", skills: ["Python", "React", "SQL"], profileCompletion: 92, matchScore: 87, category: "General" },
  { id: "c2", name: "Rahul Kumar", email: "rahul@example.com", state: "Bihar", district: "Patna", education: "B.Sc Mathematics", skills: ["Data Analysis", "Excel", "Statistics"], profileCompletion: 78, matchScore: 72, category: "OBC" },
  { id: "c3", name: "Anita Devi", email: "anita@example.com", state: "Rajasthan", district: "Jaipur", education: "MBA Finance", skills: ["Accounting", "Tally", "Financial Analysis"], profileCompletion: 85, matchScore: 79, category: "SC" },
  { id: "c4", name: "Vikram Singh", email: "vikram@example.com", state: "Uttar Pradesh", district: "Lucknow", education: "B.Tech Mechanical", skills: ["AutoCAD", "SolidWorks", "Manufacturing"], profileCompletion: 65, matchScore: 68, category: "General" },
  { id: "c5", name: "Meera Patel", email: "meera@example.com", state: "Gujarat", district: "Ahmedabad", education: "BCA", skills: ["Java", "Spring Boot", "MySQL"], profileCompletion: 95, matchScore: 91, category: "EWS" },
  { id: "c6", name: "Arjun Reddy", email: "arjun@example.com", state: "Telangana", district: "Hyderabad", education: "M.Tech AI", skills: ["Machine Learning", "Python", "TensorFlow"], profileCompletion: 88, matchScore: 84, category: "OBC" },
  { id: "c7", name: "Sunita Oraon", email: "sunita@example.com", state: "Jharkhand", district: "Ranchi", education: "B.Sc Nursing", skills: ["Healthcare", "First Aid", "Patient Care"], profileCompletion: 70, matchScore: 65, category: "ST" },
  { id: "c8", name: "Deepak Yadav", email: "deepak@example.com", state: "Madhya Pradesh", district: "Bhopal", education: "B.Com", skills: ["GST", "Accounting", "MS Office"], profileCompletion: 82, matchScore: 75, category: "OBC" },
];

const MOCK_PROFILE: CandidateProfile = {
  id: "c1",
  userId: "usr_001",
  name: "Priya Sharma",
  email: "priya@example.com",
  phone: "9876543210",
  dateOfBirth: "2002-03-15",
  gender: "Female",
  category: "General",
  state: "Maharashtra",
  district: "Mumbai",
  pincode: "400001",
  address: "123 Andheri West, Mumbai",
  education: [
    { id: "e1", degree: "B.Tech", institution: "IIT Bombay", fieldOfStudy: "Computer Science", startYear: 2020, endYear: 2024, cgpa: 8.5, isCurrent: false },
  ],
  skills: [
    { name: "Python", proficiency: "advanced" },
    { name: "React", proficiency: "intermediate" },
    { name: "SQL", proficiency: "intermediate" },
  ],
  sectors: ["Information Technology", "Finance & Banking"],
  preferredLocations: ["Mumbai", "Pune", "Bangalore"],
  profileCompletion: 92,
  isVerified: true,
  createdAt: "2024-01-15T10:00:00Z",
  updatedAt: "2024-06-01T14:30:00Z",
};

export async function getCandidates(
  page = 1,
  pageSize = 20,
  filters?: CandidateFilter
): Promise<PaginatedResponse<CandidateListItem>> {
  try {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
    if (filters?.state) params.set("state", filters.state);
    if (filters?.district) params.set("district", filters.district);
    if (filters?.category) params.set("category", filters.category);
    if (filters?.skills) params.set("skills", filters.skills.join(","));
    return await apiGet<PaginatedResponse<CandidateListItem>>(`${API_ROUTES.CANDIDATES.LIST}?${params}`);
  } catch {
    return {
      items: MOCK_CANDIDATES,
      total: MOCK_CANDIDATES.length,
      page,
      pageSize,
      totalPages: 1,
    };
  }
}

export async function getCandidateProfile(): Promise<CandidateProfile> {
  try {
    const response = await apiGet<ApiResponse<CandidateProfile>>(API_ROUTES.CANDIDATES.PROFILE);
    return response.data;
  } catch {
    return MOCK_PROFILE;
  }
}

export async function updateCandidateProfile(data: Partial<CandidateProfile>): Promise<CandidateProfile> {
  try {
    const response = await apiPut<ApiResponse<CandidateProfile>>(API_ROUTES.CANDIDATES.PROFILE, data);
    return response.data;
  } catch {
    return { ...MOCK_PROFILE, ...data };
  }
}

export async function addEducation(data: Omit<Education, "id">): Promise<Education> {
  try {
    const response = await apiPost<ApiResponse<Education>>(API_ROUTES.CANDIDATES.EDUCATION, data);
    return response.data;
  } catch {
    return { ...data, id: `e_${Date.now()}` };
  }
}

export async function updateSkills(skills: Skill[]): Promise<Skill[]> {
  try {
    const response = await apiPut<ApiResponse<Skill[]>>(API_ROUTES.CANDIDATES.SKILLS, { skills });
    return response.data;
  } catch {
    return skills;
  }
}
