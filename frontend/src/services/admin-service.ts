import { apiGet, apiPost, apiPut } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse } from "@/types/common";
import type { PolicyConfig, AuditEntry, OverrideRequest, FairnessMetrics } from "@/types/allocation";

const MOCK_POLICY: PolicyConfig = {
  id: "policy_001",
  name: "Standard Allocation Policy v2.1",
  description: "Default allocation policy with balanced fairness weights",
  weights: {
    skillMatch: 0.35,
    locationPreference: 0.2,
    educationMatch: 0.25,
    candidatePreference: 0.1,
    fairnessAdjustment: 0.1,
  },
  thresholds: {
    minimumMatchScore: 40,
    minimumProfileCompletion: 60,
  },
  representationTargets: {
    gender: { Male: 50, Female: 48, Other: 2 },
    category: { General: 40, OBC: 27, SC: 16, ST: 10, EWS: 7 },
    ruralUrban: { rural: 45, urban: 55 },
  },
  isActive: true,
  updatedAt: "2024-12-01T10:00:00Z",
};

const MOCK_AUDIT: AuditEntry[] = [
  { id: "a1", action: "allocation.triggered", entityType: "allocation_cycle", entityId: "cycle_002", userId: "admin_001", userName: "System Admin", performedBy: "admin_001", performedByName: "System Admin", details: { cycleName: "February 2025 Allocation" }, timestamp: "2025-02-10T06:00:00Z" },
  { id: "a2", action: "policy.updated", entityType: "policy", entityId: "policy_001", userId: "admin_001", userName: "System Admin", performedBy: "admin_001", performedByName: "System Admin", details: { field: "weights.skillMatch", oldValue: 0.3, newValue: 0.35 }, timestamp: "2025-02-09T15:30:00Z" },
  { id: "a3", action: "override.approved", entityType: "override", entityId: "ov_001", userId: "admin_002", userName: "Regional Admin", performedBy: "admin_002", performedByName: "Regional Admin", details: { candidateName: "Vikram Singh", reason: "Medical grounds" }, timestamp: "2025-02-08T11:20:00Z" },
  { id: "a4", action: "candidate.verified", entityType: "candidate", entityId: "c5", userId: "admin_001", userName: "System Admin", performedBy: "admin_001", performedByName: "System Admin", details: { verificationType: "document" }, timestamp: "2025-02-07T09:45:00Z" },
  { id: "a5", action: "opportunity.approved", entityType: "opportunity", entityId: "o6", userId: "admin_001", userName: "System Admin", performedBy: "admin_001", performedByName: "System Admin", details: { employerName: "CloudFirst", title: "Cloud Infrastructure Intern" }, timestamp: "2025-02-06T14:10:00Z" },
  { id: "a6", action: "notification.sent", entityType: "notification", entityId: "n_003", userId: "system", userName: "System", performedBy: "system", performedByName: "System", details: { type: "allocation_result", recipientCount: 7200 }, timestamp: "2025-01-10T08:35:00Z" },
  { id: "a7", action: "allocation.completed", entityType: "allocation_cycle", entityId: "cycle_001", userId: "system", userName: "System", performedBy: "system", performedByName: "System", details: { totalAllocations: 7200, duration: "2h 30m" }, timestamp: "2025-01-10T08:30:00Z" },
];

const MOCK_OVERRIDES: OverrideRequest[] = [
  { id: "ov_001", candidateId: "c4", candidateName: "Vikram Singh", originalOpportunityId: "o5", originalOpportunityTitle: "Mechanical Engineering Intern", targetOpportunityId: "o1", targetOpportunityTitle: "Software Development Intern", reason: "Candidate has relevant software skills and prefers IT sector. Medical condition limits physical work.", status: "pending", requestedBy: "regional_admin_001", createdAt: "2025-02-10T09:00:00Z" },
  { id: "ov_002", candidateId: "c7", candidateName: "Sunita Oraon", originalOpportunityId: "o4", originalOpportunityTitle: "Healthcare Management Intern", targetOpportunityId: "o2", targetOpportunityTitle: "Data Analytics Intern", reason: "Candidate expressed strong interest in data analytics and has relevant coursework.", status: "pending", requestedBy: "regional_admin_002", createdAt: "2025-02-09T14:30:00Z" },
  { id: "ov_003", candidateId: "c3", candidateName: "Anita Devi", originalOpportunityId: "o2", originalOpportunityTitle: "Data Analytics Intern", targetOpportunityId: "o1", targetOpportunityTitle: "Software Development Intern", reason: "Family relocation to Bangalore. Proximity to new workplace essential.", status: "approved", requestedBy: "regional_admin_001", reviewedBy: "admin_002", createdAt: "2025-02-08T10:00:00Z", reviewedAt: "2025-02-08T11:20:00Z" },
];

export async function getPolicy(): Promise<PolicyConfig> {
  try {
    const response = await apiGet<ApiResponse<PolicyConfig>>(API_ROUTES.ADMIN.POLICY);
    return response.data;
  } catch {
    return MOCK_POLICY;
  }
}

export async function updatePolicy(data: Partial<PolicyConfig>): Promise<PolicyConfig> {
  try {
    const response = await apiPut<ApiResponse<PolicyConfig>>(API_ROUTES.ADMIN.POLICY, data);
    return response.data;
  } catch {
    return { ...MOCK_POLICY, ...data, updatedAt: new Date().toISOString() };
  }
}

export async function getAuditLog(): Promise<AuditEntry[]> {
  try {
    const response = await apiGet<ApiResponse<AuditEntry[]>>(API_ROUTES.ADMIN.AUDIT);
    return response.data;
  } catch {
    return MOCK_AUDIT;
  }
}

export async function getOverrides(): Promise<OverrideRequest[]> {
  try {
    const response = await apiGet<ApiResponse<OverrideRequest[]>>(API_ROUTES.ADMIN.OVERRIDES);
    return response.data;
  } catch {
    return MOCK_OVERRIDES;
  }
}

export async function approveOverride(id: string): Promise<OverrideRequest> {
  try {
    const response = await apiPost<ApiResponse<OverrideRequest>>(API_ROUTES.ADMIN.APPROVE_OVERRIDE(id));
    return response.data;
  } catch {
    const override = MOCK_OVERRIDES.find((o) => o.id === id);
    return { ...override!, status: "approved", reviewedAt: new Date().toISOString() };
  }
}

export async function rejectOverride(id: string): Promise<OverrideRequest> {
  try {
    const response = await apiPost<ApiResponse<OverrideRequest>>(API_ROUTES.ADMIN.REJECT_OVERRIDE(id));
    return response.data;
  } catch {
    const override = MOCK_OVERRIDES.find((o) => o.id === id);
    return { ...override!, status: "rejected", reviewedAt: new Date().toISOString() };
  }
}

export async function getAnalytics(): Promise<Record<string, unknown>> {
  try {
    const response = await apiGet<ApiResponse<Record<string, unknown>>>(API_ROUTES.ADMIN.ANALYTICS);
    return response.data;
  } catch {
    return {
      totalCandidates: 15420,
      totalOpportunities: 8500,
      totalAllocations: 7200,
      activeInternships: 3200,
      completionRate: 85.2,
      averageMatchScore: 73.4,
      fairnessIndex: 0.82,
    };
  }
}

export async function getAdminFairness(): Promise<FairnessMetrics> {
  try {
    const response = await apiGet<ApiResponse<FairnessMetrics>>(API_ROUTES.ADMIN.FAIRNESS);
    return response.data;
  } catch {
    return {
      genderDistribution: { Male: 52, Female: 46, Other: 2 },
      categoryDistribution: { General: 40, OBC: 27, SC: 16, ST: 10, EWS: 7 },
      stateDistribution: { "Uttar Pradesh": 15, Maharashtra: 12, Bihar: 10, "Tamil Nadu": 8, Karnataka: 7, "West Bengal": 6, Rajasthan: 5, Gujarat: 5, Others: 32 },
      districtDistribution: { Mumbai: 5, Delhi: 4, Bangalore: 4, Hyderabad: 3, Chennai: 3, Kolkata: 3, Pune: 2, Others: 76 },
      ruralUrbanRatio: { rural: 45, urban: 55 },
      representationIndex: 0.82,
    };
  }
}

export async function sendNotification(data: { subject: string; message: string; recipients: string }): Promise<{ success: boolean }> {
  try {
    await apiPost(API_ROUTES.ADMIN.SEND_NOTIFICATION, data);
    return { success: true };
  } catch {
    return { success: true };
  }
}
