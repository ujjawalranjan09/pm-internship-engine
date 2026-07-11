"use client";

import { useQuery } from "@tanstack/react-query";
import * as matchingService from "@/services/matching-service";

export function useRecommendations() {
  return useQuery({
    queryKey: ["matches", "recommendations"],
    queryFn: matchingService.getRecommendations,
    staleTime: 60 * 1000,
  });
}

export function useMatchesForOpportunity(opportunityId: string) {
  return useQuery({
    queryKey: ["matches", "opportunity", opportunityId],
    queryFn: () => matchingService.getMatchesForOpportunity(opportunityId),
    enabled: !!opportunityId,
    staleTime: 30 * 1000,
  });
}
