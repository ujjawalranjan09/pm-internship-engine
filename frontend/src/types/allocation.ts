import type { AllocationStatus } from "./common";

export interface AllocationCycle {
  id: string;
  name: string;
  status: AllocationStatus;
  totalCandidates: number;
  totalOpportunities: number;
  totalAllocations: number;
  fairnessMetrics: FairnessMetrics;
  startedAt?: string;
  completedAt?: string;
  createdBy: string;
  createdAt: string;
}

export interface AllocationResult {
  id: string;
  cycleId: string;
  candidateId: string;
  candidateName: string;
  opportunityId: string;
  opportunityTitle: string;
  employerName: string;
  matchScore: number;
  allocatedAt: string;
  status: "allocated" | "confirmed" | "declined";
}

export interface FairnessMetrics {
  genderDistribution: Record<string, number>;
  categoryDistribution: Record<string, number>;
  stateDistribution: Record<string, number>;
  districtDistribution: Record<string, number>;
  ruralUrbanRatio: { rural: number; urban: number };
  representationIndex: number;
}

export interface PolicyConfig {
  id: string;
  name: string;
  description: string;
  weights: {
    skillMatch: number;
    locationPreference: number;
    educationMatch: number;
    candidatePreference: number;
    fairnessAdjustment: number;
  };
  thresholds: {
    minimumMatchScore: number;
    minimumProfileCompletion: number;
  };
  representationTargets: {
    gender: Record<string, number>;
    category: Record<string, number>;
    ruralUrban: { rural: number; urban: number };
  };
  isActive: boolean;
  updatedAt: string;
}

export interface AuditEntry {
  id: string;
  action: string;
  entityType: string;
  entityId: string;
  performedBy: string;
  performedByName: string;
  details: Record<string, unknown>;
  timestamp: string;
}

export interface OverrideRequest {
  id: string;
  candidateId: string;
  candidateName: string;
  originalOpportunityId: string;
  originalOpportunityTitle: string;
  targetOpportunityId: string;
  targetOpportunityTitle: string;
  reason: string;
  status: "pending" | "approved" | "rejected";
  requestedBy: string;
  reviewedBy?: string;
  createdAt: string;
  reviewedAt?: string;
}
