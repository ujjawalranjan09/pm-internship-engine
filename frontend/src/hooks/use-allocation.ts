"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as allocationService from "@/services/allocation-service";

export function useAllocationCycles() {
  return useQuery({
    queryKey: ["allocation", "cycles"],
    queryFn: allocationService.getCycles,
    staleTime: 30 * 1000,
  });
}

export function useCycleDetail(id: string) {
  return useQuery({
    queryKey: ["allocation", "cycle", id],
    queryFn: () => allocationService.getCycleDetail(id),
    enabled: !!id,
    staleTime: 15 * 1000,
  });
}

export function useCycleResults(cycleId: string) {
  return useQuery({
    queryKey: ["allocation", "results", cycleId],
    queryFn: () => allocationService.getCycleResults(cycleId),
    enabled: !!cycleId,
    staleTime: 30 * 1000,
  });
}

export function useTriggerAllocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: allocationService.triggerAllocation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allocation"] });
    },
  });
}

export function useFairnessMetrics() {
  return useQuery({
    queryKey: ["allocation", "fairness"],
    queryFn: allocationService.getFairnessMetrics,
    staleTime: 60 * 1000,
  });
}
