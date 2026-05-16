"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as candidateService from "@/services/candidate-service";
import type { CandidateFilter } from "@/types/candidate";

export function useCandidates(page = 1, pageSize = 20, filters?: CandidateFilter) {
  return useQuery({
    queryKey: ["candidates", page, pageSize, filters],
    queryFn: () => candidateService.getCandidates(page, pageSize, filters),
    staleTime: 30 * 1000,
  });
}

export function useCandidateProfile() {
  return useQuery({
    queryKey: ["candidate", "profile"],
    queryFn: candidateService.getCandidateProfile,
    staleTime: 60 * 1000,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: candidateService.updateCandidateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate"] });
    },
  });
}

export function useAddEducation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: candidateService.addEducation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate"] });
    },
  });
}

export function useUpdateSkills() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: candidateService.updateSkills,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate"] });
    },
  });
}
