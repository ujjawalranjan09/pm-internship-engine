"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as candidateService from "@/services/candidate-service";
import type { CandidateProfile, CandidateFilter } from "@/types/candidate";

export function useCandidateProfile() {
  return useQuery({
    queryKey: ["candidate", "profile"],
    queryFn: candidateService.getCandidateProfile,
    staleTime: 60 * 1000,
  });
}

export function useCandidateProfileCompletion() {
  return useQuery({
    queryKey: ["candidate", "completion"],
    queryFn: candidateService.getCandidateProfileCompletion,
    staleTime: 60 * 1000,
  });
}

export function useCandidates(page = 1, pageSize = 20, filters?: CandidateFilter) {
  return useQuery({
    queryKey: ["candidates", { page, pageSize, filters }],
    queryFn: () => candidateService.getCandidates(page, pageSize, filters),
    staleTime: 30 * 1000,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<CandidateProfile>) => candidateService.updateCandidateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", "profile"] });
    },
  });
}