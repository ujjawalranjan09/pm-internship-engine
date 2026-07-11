"use client";

import { useAllocationCycles, useCycleResults } from "@/hooks/use-allocation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { SkeletonCard } from "@/components/shared/skeleton";
import { formatDate, cn } from "@/lib/utils";
import {
  CheckCircle,
  Clock,
  XCircle,
  MapPin,
  Building2,
  Calendar,
  ArrowRight,
  Gift,
} from "lucide-react";

const statusConfig: Record<string, { label: string; color: string; icon: typeof CheckCircle }> = {
  pending: { label: "Pending", color: "text-amber-600 bg-amber-50 border-amber-200", icon: Clock },
  confirmed: { label: "Confirmed", color: "text-blue-600 bg-blue-50 border-blue-200", icon: CheckCircle },
  accepted: { label: "Accepted", color: "text-green-600 bg-green-50 border-green-200", icon: CheckCircle },
  declined: { label: "Declined", color: "text-red-600 bg-red-50 border-red-200", icon: XCircle },
  withdrawn: { label: "Withdrawn", color: "text-gray-600 bg-gray-50 border-gray-200", icon: XCircle },
};

export default function AllocationsPage() {
  const { data: cycles, isLoading: cyclesLoading } = useAllocationCycles();

  // Find the latest completed cycle
  const latestCycle = cycles?.find((c) => c.status === "completed");
  const { data: results, isLoading: resultsLoading } = useCycleResults(latestCycle?.id ?? "");

  const isLoading = cyclesLoading || resultsLoading;

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Allocations"
        description="Track your internship allocation status across all cycles"
      />

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : !results || results.length === 0 ? (
        <EmptyState
          icon="gift"
          title="No allocations yet"
          description="You haven't been allocated to any internship yet. Allocations happen in batches — keep your profile updated and wait for the next cycle."
          action={{ label: "View Matches", href: "/applicant/matches" }}
        />
      ) : (
        <>
          {/* Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-saffron-50 p-2.5">
                  <Gift className="h-5 w-5 text-saffron-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-navy-600">{results.length}</p>
                  <p className="text-xs text-muted-foreground">Total Allocations</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-green-50 p-2.5">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-navy-600">
                    {results.filter((r) => r.status === "confirmed" || r.status === "accepted").length}
                  </p>
                  <p className="text-xs text-muted-foreground">Confirmed</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-amber-50 p-2.5">
                  <Clock className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-navy-600">
                    {results.filter((r) => r.status === "allocated").length}
                  </p>
                  <p className="text-xs text-muted-foreground">Awaiting Response</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Allocation Cards */}
          <div className="space-y-4">
            {results.map((result) => {
              const cfg = statusConfig[result.status] ?? statusConfig.pending;
              const StatusIcon = cfg.icon;

              return (
                <Card key={result.id} className="overflow-hidden">
                  <CardContent className="p-0">
                    <div className="flex flex-col sm:flex-row">
                      {/* Left accent */}
                      <div
                        className={cn(
                          "w-full sm:w-1.5 shrink-0",
                          result.status === "accepted" || result.status === "confirmed"
                            ? "bg-green-500"
                            : result.status === "declined"
                            ? "bg-red-500"
                            : "bg-amber-500"
                        )}
                      />

                      <div className="flex-1 p-5">
                        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                          <div className="min-w-0">
                            <h3 className="font-semibold text-base mb-1">{result.opportunityTitle}</h3>
                            <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Building2 className="h-4 w-4" />
                                {result.employerName}
                              </span>
                              <span className="flex items-center gap-1">
                                <Calendar className="h-4 w-4" />
                                Allocated {formatDate(result.allocatedAt)}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            <div
                              className={cn(
                                "flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm font-medium",
                                cfg.color
                              )}
                            >
                              <StatusIcon className="h-4 w-4" />
                              {cfg.label}
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        {result.status === "allocated" && (
                          <div className="mt-4 flex items-center gap-3 pt-4 border-t">
                            <Button size="sm" className="bg-green-600 hover:bg-green-700">
                              <CheckCircle className="h-4 w-4 mr-1.5" />
                              Accept Allocation
                            </Button>
                            <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50">
                              <XCircle className="h-4 w-4 mr-1.5" />
                              Decline
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Cycle Info */}
          {latestCycle && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Allocation Cycle: {latestCycle.name}</CardTitle>
                <CardDescription>
                  Completed on {latestCycle.completedAt ? formatDate(latestCycle.completedAt) : "N/A"} &middot;{" "}
                  {latestCycle.totalAllocations} total allocations
                </CardDescription>
              </CardHeader>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
