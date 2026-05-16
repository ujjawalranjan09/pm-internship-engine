import { apiGet, apiPost } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse } from "@/types/common";
import type { AllocationCycle, AllocationResult, FairnessMetrics } from "@/types/allocation";

const MOCK_CYCLES: AllocationCycle[] = [
  {
    id: "cycle_001",
    name: "January 2025 Allocation",
    status: "completed",
    totalCandidates: 15420,
    totalOpportunities: 8500,
    totalAllocations: 7200,
    fairnessMetrics: {
      genderDistribution: { Male: 52, Female: 46, Other: 2 },
      categoryDistribution: { General: 40, OBC: 27, SC: 16, ST: 10, EWS: 7 },
      stateDistribution: { "Uttar Pradesh": 15, Maharashtra: 12, Bihar: 10, "Tamil Nadu": 8, Karnataka: 7 },
      districtDistribution: { Mumbai: 5, Delhi: 4, Bangalore: 4, Hyderabad: 3, Chennai: 3 },
      ruralUrbanRatio: { rural: 45, urban: 55 },
      representationIndex: 0.82,
    },
    startedAt: "2025-01-10T06:00:00Z",
    completedAt: "2025-01-10T08:30:00Z",
    createdBy: "admin_001",
    createdAt: "2025-01-09T10:00:00Z",
  },
  {
    id: "cycle_002",
    name: "February 2025 Allocation",
    status: "running",
    totalCandidates: 18200,
    totalOpportunities: 9200,
    totalAllocations: 0,
    fairnessMetrics: {
      genderDistribution: {},
      categoryDistribution: {},
      stateDistribution: {},
      districtDistribution: {},
      ruralUrbanRatio: { rural: 0, urban: 0 },
      representationIndex: 0,
    },
    startedAt: "2025-02-10T06:00:00Z",
    createdBy: "admin_001",
    createdAt: "2025-02-09T10:00:00Z",
  },
  {
    id: "cycle_003",
    name: "March 2025 Allocation",
    status: "pending",
    totalCandidates: 0,
    totalOpportunities: 0,
    totalAllocations: 0,
    fairnessMetrics: {
      genderDistribution: {},
      categoryDistribution: {},
      stateDistribution: {},
      districtDistribution: {},
      ruralUrbanRatio: { rural: 0, urban: 0 },
      representationIndex: 0,
    },
    createdBy: "admin_001",
    createdAt: "2025-03-05T10:00:00Z",
  },
];

const MOCK_RESULTS: AllocationResult[] = [
  { id: "ar1", cycleId: "cycle_001", candidateId: "c1", candidateName: "Priya Sharma", opportunityId: "o1", opportunityTitle: "Software Development Intern", employerName: "TechCorp India", matchScore: 87, allocatedAt: "2025-01-10T07:15:00Z", status: "confirmed" },
  { id: "ar2", cycleId: "cycle_001", candidateId: "c2", candidateName: "Rahul Kumar", opportunityId: "o2", opportunityTitle: "Data Analytics Intern", employerName: "FinServ Ltd", matchScore: 72, allocatedAt: "2025-01-10T07:15:00Z", status: "confirmed" },
  { id: "ar3", cycleId: "cycle_001", candidateId: "c3", candidateName: "Anita Devi", opportunityId: "o2", opportunityTitle: "Data Analytics Intern", employerName: "FinServ Ltd", matchScore: 79, allocatedAt: "2025-01-10T07:15:00Z", status: "allocated" },
  { id: "ar4", cycleId: "cycle_001", candidateId: "c5", candidateName: "Meera Patel", opportunityId: "o1", opportunityTitle: "Software Development Intern", employerName: "TechCorp India", matchScore: 91, allocatedAt: "2025-01-10T07:15:00Z", status: "confirmed" },
  { id: "ar5", cycleId: "cycle_001", candidateId: "c6", candidateName: "Arjun Reddy", opportunityId: "o6", opportunityTitle: "Cloud Infrastructure Intern", employerName: "CloudFirst", matchScore: 84, allocatedAt: "2025-01-10T07:15:00Z", status: "declined" },
];

export async function getCycles(): Promise<AllocationCycle[]> {
  try {
    const response = await apiGet<ApiResponse<AllocationCycle[]>>(API_ROUTES.ALLOCATION.CYCLES);
    return response.data;
  } catch {
    return MOCK_CYCLES;
  }
}

export async function getCycleDetail(id: string): Promise<AllocationCycle> {
  try {
    const response = await apiGet<ApiResponse<AllocationCycle>>(API_ROUTES.ALLOCATION.CYCLE_DETAIL(id));
    return response.data;
  } catch {
    return MOCK_CYCLES.find((c) => c.id === id) || MOCK_CYCLES[0];
  }
}

export async function getCycleResults(cycleId: string): Promise<AllocationResult[]> {
  try {
    const response = await apiGet<ApiResponse<AllocationResult[]>>(API_ROUTES.ALLOCATION.RESULTS(cycleId));
    return response.data;
  } catch {
    return MOCK_RESULTS;
  }
}

export async function triggerAllocation(): Promise<AllocationCycle> {
  try {
    const response = await apiPost<ApiResponse<AllocationCycle>>(API_ROUTES.ALLOCATION.TRIGGER);
    return response.data;
  } catch {
    return {
      ...MOCK_CYCLES[1],
      id: `cycle_${Date.now()}`,
      status: "running",
      startedAt: new Date().toISOString(),
    };
  }
}

export async function getFairnessMetrics(): Promise<FairnessMetrics> {
  try {
    const response = await apiGet<ApiResponse<FairnessMetrics>>(API_ROUTES.ADMIN.FAIRNESS);
    return response.data;
  } catch {
    return MOCK_CYCLES[0].fairnessMetrics;
  }
}
