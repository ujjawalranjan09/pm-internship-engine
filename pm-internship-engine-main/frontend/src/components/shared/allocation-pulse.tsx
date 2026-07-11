"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/services/api-client";
import { cn } from "@/lib/utils";

type AllocationStatus = "idle" | "running" | "completed" | "failed";

interface AllocationOverview {
  pendingAllocations: number;
  lastCycleStatus: AllocationStatus;
  lastCycleCompletedAt?: string;
}

async function fetchAllocationOverview(): Promise<AllocationOverview> {
  try {
    const response = await apiGet<AllocationOverview>("/api/v1/admin/analytics/overview");
    return response;
  } catch {
    // Fallback to idle state if endpoint not available
    return {
      pendingAllocations: 0,
      lastCycleStatus: "idle",
    };
  }
}

export function useAllocationPulse() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["admin", "allocation-pulse"],
    queryFn: fetchAllocationOverview,
    refetchInterval: 30000, // Poll every 30 seconds
    staleTime: 15000,
    retry: 1,
  });

  const [status, setStatus] = useState<AllocationStatus>("idle");

  useEffect(() => {
    if (data && !isLoading) {
      if (data.pendingAllocations > 0) {
        setStatus("running");
      } else if (data.lastCycleStatus === "completed") {
        setStatus("completed");
        // Reset to idle after animation completes
        setTimeout(() => setStatus("idle"), 3000);
      } else if (data.lastCycleStatus === "failed") {
        setStatus("failed");
      } else {
        setStatus("idle");
      }
    }
  }, [data, isLoading]);

  return { status, isLoading, refetch };
}

export function AllocationPulse() {
  const { status, isLoading } = useAllocationPulse();

  if (isLoading) {
    return (
      <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200" role="status" aria-live="polite">
        <span className="h-2 w-2 rounded-full bg-slate-400 animate-pulse" aria-hidden="true" />
        <span className="text-xs font-medium text-slate-500 font-[var(--font-jetbrains-mono)]">Loading...</span>
      </div>
    );
  }

  const pulseConfig = {
    idle: {
      className: "bg-navy-50 border-navy-200",
      indicatorClassName: "bg-navy-500",
      ringClassName: "border-navy-500",
      label: "Engine Ready",
      labelClassName: "text-navy-600",
      animation: "allocation-pulse-idle",
    },
    running: {
      className: "bg-saffron-50 border-saffron-200",
      indicatorClassName: "bg-saffron-500",
      ringClassName: "border-saffron-500",
      label: "Allocation Running",
      labelClassName: "text-saffron-600",
      animation: "allocation-pulse-running",
    },
    completed: {
      className: "bg-emerald-50 border-emerald-200",
      indicatorClassName: "bg-emerald-500",
      ringClassName: "border-emerald-500",
      label: "Cycle Complete",
      labelClassName: "text-emerald-600",
      animation: "allocation-pulse-complete",
    },
    failed: {
      className: "bg-red-50 border-red-200",
      indicatorClassName: "bg-red-500",
      ringClassName: "border-red-500",
      label: "Cycle Failed",
      labelClassName: "text-red-600",
      animation: "allocation-pulse-error",
    },
  };

  const config = pulseConfig[status];

  return (
    <div
      className={cn(
        "hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all duration-200",
        config.className
      )}
      role="status"
      aria-live="polite"
      aria-label={`Allocation engine status: ${config.label}`}
    >
      <span className="relative h-2 w-2 rounded-full" aria-hidden="true">
        <span
          className={cn(
            "absolute inset-[-4px] rounded-full border-2",
            config.ringClassName,
            config.animation
          )}
        />
        <span
          className={cn(
            "absolute inset-0 rounded-full",
            config.indicatorClassName
          )}
        />
      </span>
      <span className={cn("text-xs font-medium font-[var(--font-jetbrains-mono)]", config.labelClassName)}>
        {config.label}
      </span>
    </div>
  );
}

// Mini version for dashboard cards
export function MiniAllocationPulse() {
  const { status, isLoading } = useAllocationPulse();

  if (isLoading) return null;

  const statusColors = {
    idle: "bg-navy-500",
    running: "bg-saffron-500 animate-pulse",
    completed: "bg-emerald-500",
    failed: "bg-red-500",
  };

  return (
    <span
      className={cn(
        "inline-flex h-2 w-2 rounded-full shrink-0",
        statusColors[status]
      )}
      aria-label={`Allocation engine: ${status}`}
      title={`Allocation engine: ${status}`}
    />
  );
}