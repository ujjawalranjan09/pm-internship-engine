"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as opportunityService from "@/services/opportunity-service";
import type { OpportunityFilter, CreateOpportunityRequest } from "@/types/opportunity";

export function useOpportunities(page = 1, pageSize = 20, filters?: OpportunityFilter) {
  return useQuery({
    queryKey: ["opportunities", page, pageSize, filters],
    queryFn: () => opportunityService.getOpportunities(page, pageSize, filters),
    staleTime: 30 * 1000,
  });
}

export function useOpportunityDetail(id: string) {
  return useQuery({
    queryKey: ["opportunity", id],
    queryFn: () => opportunityService.getOpportunityDetail(id),
    enabled: !!id,
    staleTime: 60 * 1000,
  });
}

export function useCreateOpportunity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateOpportunityRequest) => opportunityService.createOpportunity(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
    },
  });
}

export function useUpdateOpportunity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateOpportunityRequest> }) =>
      opportunityService.updateOpportunity(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      queryClient.invalidateQueries({ queryKey: ["opportunity", variables.id] });
    },
  });
}
