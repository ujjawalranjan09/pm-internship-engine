"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as adminService from "@/services/admin-service";

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      return [
        { id: "n1", type: "info", title: "Allocation Cycle Started", message: "February 2025 allocation cycle is now running.", timestamp: "2025-02-10T06:00:00Z", read: false },
        { id: "n2", type: "success", title: "Profile Verified", message: "Your profile has been verified successfully.", timestamp: "2025-02-09T14:00:00Z", read: true },
        { id: "n3", type: "warning", title: "Application Deadline", message: "3 internship applications expire in 2 days.", timestamp: "2025-02-08T10:00:00Z", read: false },
        { id: "n4", type: "info", title: "New Match Found", message: "A new internship matching your profile has been posted.", timestamp: "2025-02-07T16:00:00Z", read: true },
      ];
    },
    staleTime: 30 * 1000,
  });
}

export function useSendNotification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminService.sendNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
