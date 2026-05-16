export type AllocationStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "allocated"
  | "confirmed"
  | "declined"
  | "accepted";

export interface AllocationCycle {
  id: string;
  name: string;
  status: AllocationStatus;
  totalCandidates: number;
  totalOpportunities: number;
  allocatedCount: number;
  unallocatedCount: number;
  fairnessScore?: number;
  createdAt: string;
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
