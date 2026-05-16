export type AllocationStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "allocated"
  | "confirmed"
  | "declined"
  | "accepted";

export interface FairnessMetrics {
  representationIndex: number;
  categoryDistribution: Record<string, number>;
  genderDistribution: Record<string, number>;
  ruralUrbanRatio: { rural: number; urban: number };
  stateDistribution: Record<string, number>;
  districtDistribution: Record<string, number>;
}

export interface AllocationCycle {
  id: string;
  name: string;
  status: AllocationStatus;
  totalCandidates: number;
  totalOpportunities: number;
  totalAllocations: number;
  allocatedCount: number;
  unallocatedCount: number;
  fairnessScore?: number;
  fairnessMetrics: FairnessMetrics;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
}

export interface AllocationResult {
  id: string;
  cycleId: string;
  candidateId: string;
  candidateName: string;
  opportunityId: string;
  opportunityTitle: string;
  employerName: string;
  location: string;
  sector: string;
  stipend: number;
  allocationScore: number;
  matchScore: number;
  status: AllocationStatus;
  allocatedAt: string;
  confirmedAt?: string;
  declinedAt?: string;
}

export interface FairnessReport {
  overallScore: number;
  categoryBreakdown: Record<string, { allocated: number; total: number; rate: number }>;
  stateBreakdown: Record<string, { allocated: number; total: number; rate: number }>;
  sectorBreakdown: Record<string, { allocated: number; total: number; rate: number }>;
  giniCoefficient: number;
  disparityIndex: number;
}

export interface PolicyConfig {
  name: string;
  description?: string;
  maxAllocationPerCandidate?: number;
  minFairnessScore?: number;
  categoryPreferences?: Record<string, number>;
  stateQuotas?: Record<string, number>;
  weights?: Record<string, number>;
  thresholds?: {
    minimumMatchScore?: number;
    minimumProfileCompletion?: number;
  };
  representationTargets?: {
    gender?: Record<string, number>;
    category?: Record<string, number>;
    ruralUrban?: { rural: number; urban: number };
  };
  createdAt: string;
  updatedAt: string;
}

export interface AuditEntry {
  id: string;
  action: string;
  userId: string;
  userName: string;
  performedByName: string;
  entityType: string;
  entityId: string;
  details: Record<string, unknown>;
  timestamp: string;
  cycleId?: string;
}

export interface OverrideRequest {
  id: string;
  cycleId: string;
  candidateId: string;
  candidateName: string;
  opportunityId: string;
  originalOpportunityTitle?: string;
  targetOpportunityId?: string;
  targetOpportunityTitle?: string;
  reason: string;
  status: "pending" | "approved" | "rejected";
  requestedBy: string;
  reviewedBy?: string;
  createdAt: string;
  reviewedAt?: string;
}
