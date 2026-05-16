export interface AllocationResult {
  id: string;
  cycleId: string;
  candidateId: string;
  opportunityId: string;
  status: "allocated" | "declined" | "confirmed" | "accepted" | "pending";
  createdAt: string;
  updatedAt: string;
}

export interface AllocationCycle {
  id: string;
  name: string;
  status: "draft" | "running" | "completed" | "failed";
  totalCandidates: number;
  totalOpportunities: number;
  allocatedCount: number;
  createdAt: string;
  completedAt?: string;
}
