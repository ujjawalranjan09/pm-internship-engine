"use client";

import { useState } from "react";
import {
  useAllocationCycles,
  useCycleResults,
  useTriggerAllocation,
  useFairnessMetrics,
} from "@/hooks/use-allocation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/shared/page-header";
import { SkeletonCard } from "@/components/shared/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { formatDate, cn } from "@/lib/utils";
import {
  Play,
  Clock,
  TrendingUp,
  GitMerge,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  ArrowRight,
} from "lucide-react";

export default function AdminAllocationsPage() {
  const [selectedCycleId, setSelectedCycleId] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const { data: cycles, isLoading: cyclesLoading } = useAllocationCycles();
  const { data: results, isLoading: resultsLoading } = useCycleResults(selectedCycleId ?? "");
  const { data: fairness, isLoading: fairnessLoading } = useFairnessMetrics();
  const triggerMutation = useTriggerAllocation();

  const selectedCycle = cycles?.find((c) => c.id === selectedCycleId);

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Allocation Management"
        description="Run allocation cycles, review results, and monitor fairness metrics"
        breadcrumbs={[{ label: "Admin" }, { label: "Allocations" }]}
      />

      {/* Trigger New Cycle */}
      <Card>
        <CardContent className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-semibold text-sm font-[var(--font-dm-sans)]">Run New Allocation</h3>
            <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">
              Trigger a new constrained optimization allocation cycle across all matched candidates
            </p>
          </div>
          <Button
            onClick={() => triggerMutation.mutate({ name: `Cycle ${new Date().toISOString().slice(0, 10)}` })}
            disabled={triggerMutation.isPending}
            className="shrink-0"
          >
            {triggerMutation.isPending ? (
              <>
                <Clock className="h-4 w-4 mr-1.5 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-1.5" />
                Run Allocation
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cycles List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-[var(--font-space-grotesk)]">Allocation Cycles</CardTitle>
          </CardHeader>
          <CardContent>
            {cyclesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : !cycles || cycles.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4 font-[var(--font-dm-sans)]">No cycles yet</p>
            ) : (
              <div className="space-y-2">
                {cycles.map((cycle) => (
                  <button
                    key={cycle.id}
                    onClick={() => setSelectedCycleId(cycle.id)}
                    className={cn(
                      "w-full text-left p-3 rounded-lg border transition-all",
                      selectedCycleId === cycle.id
                        ? "border-[var(--role-primary-500)] bg-[var(--role-primary-50)] shadow-sm"
                        : "hover:bg-muted/50"
                    )}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium truncate font-[var(--font-dm-sans)]">{cycle.name}</p>
                      <Badge variant="status" status={cycle.status} size="sm">
                        {cycle.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground font-[var(--font-jetbrains-mono)]">
                      {(cycle as any).totalAllocations ?? (cycle as any).allocatedCount ?? 0} allocations &middot; {formatDate(cycle.createdAt)}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Cycle Results */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base font-[var(--font-space-grotesk)]">
              {selectedCycle ? `Results: ${selectedCycle.name}` : "Select a Cycle"}
            </CardTitle>
            {selectedCycle && (
              <CardDescription className="font-[var(--font-dm-sans)]">
                {(selectedCycle as any).totalCandidates ?? 0} candidates &middot;{" "}
                {(selectedCycle as any).totalOpportunities ?? 0} opportunities &middot;{" "}
                {(selectedCycle as any).totalAllocations ?? (selectedCycle as any).allocatedCount ?? 0} allocations
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {!selectedCycleId ? (
              <div className="text-center py-12 text-muted-foreground">
                <GitMerge className="h-10 w-10 mx-auto mb-3 opacity-50" />
                <p className="text-sm font-[var(--font-dm-sans)]">Select a cycle from the list to view allocation results</p>
              </div>
            ) : resultsLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : !results || results.length === 0 ? (
              <EmptyState
                icon="merge"
                title="No results yet"
                description="This cycle hasn't produced any allocations"
              />
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Candidate</th>
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Opportunity</th>
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Employer</th>
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Score</th>
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Status</th>
                        <th className="text-left px-4 py-3 font-medium text-muted-foreground font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Allocated</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.slice((page - 1) * 15, page * 15).map((r) => (
                        <tr key={r.id} className="border-b hover:bg-muted/30 transition-colors">
                          <td className="px-4 py-2 font-medium font-[var(--font-dm-sans)]">{r.candidateName}</td>
                          <td className="px-4 py-2">{r.opportunityTitle}</td>
                          <td className="px-4 py-2 text-muted-foreground font-[var(--font-dm-sans)]">{r.employerName}</td>
                          <td className="px-4 py-2">
                            <div className="flex items-center gap-2">
                              <div className="w-12 h-1.5 rounded-full bg-muted overflow-hidden">
                                <div
                                  className={cn(
                                    "h-full rounded-full",
                                    (r.allocationScore ?? 0) >= 70 ? "bg-gov-success" : (r.allocationScore ?? 0) >= 50 ? "bg-gov-warning" : "bg-gray-400"
                                  )}
                                  style={{ width: `${r.allocationScore ?? 0}%` }}
                                />
                              </div>
                              <span className="text-xs font-medium font-[var(--font-jetbrains-mono)] tabular-nums">{r.allocationScore ?? 0}%</span>
                            </div>
                          </td>
                          <td className="px-4 py-2">
                            <Badge variant="status" status={r.status} size="sm">
                              {r.status}
                            </Badge>
                          </td>
                          <td className="px-4 py-2 text-xs text-muted-foreground font-[var(--font-jetbrains-mono)]">
                            {formatDate(r.allocatedAt)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t">
                  <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">
                    {results.length} total results
                  </p>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <span className="text-xs font-medium font-[var(--font-jetbrains-mono)]">{page}</span>
                    <Button variant="outline" size="sm" disabled={page * 15 >= results.length} onClick={() => setPage((p) => p + 1)}>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Fairness Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2 font-[var(--font-space-grotesk)]">
            <BarChart3 className="h-5 w-5 text-[var(--role-primary-600)]" />
            Fairness & Distribution Metrics
          </CardTitle>
          <CardDescription className="font-[var(--font-dm-sans)]">
            Representation across social categories, gender, and geography
          </CardDescription>
        </CardHeader>
        <CardContent>
          {fairnessLoading ? (
            <SkeletonCard />
          ) : !fairness ? (
            <p className="text-sm text-muted-foreground text-center py-4 font-[var(--font-dm-sans)]">No fairness data available</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Category Distribution */}
              <div>
                <h4 className="text-sm font-medium mb-3 font-[var(--font-dm-sans)]">Social Category</h4>
                <div className="space-y-2">
                  {Object.entries(fairness.categoryDistribution).map(([cat, count]) => {
                    const total = Object.values(fairness.categoryDistribution).reduce((s, v) => s + v, 0);
                    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                    return (
                      <div key={cat}>
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-muted-foreground font-[var(--font-dm-sans)]">{cat.toUpperCase()}</span>
                          <span className="font-medium font-[var(--font-jetbrains-mono)] tabular-nums">{pct}% ({count})</span>
                        </div>
                        <Progress value={pct} size="sm" />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Gender Distribution */}
              <div>
                <h4 className="text-sm font-medium mb-3 font-[var(--font-dm-sans)]">Gender</h4>
                <div className="space-y-2">
                  {Object.entries(fairness.genderDistribution).map(([gender, count]) => {
                    const total = Object.values(fairness.genderDistribution).reduce((s, v) => s + v, 0);
                    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                    return (
                      <div key={gender}>
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-muted-foreground capitalize font-[var(--font-dm-sans)]">{gender}</span>
                          <span className="font-medium font-[var(--font-jetbrains-mono)] tabular-nums">{pct}% ({count})</span>
                        </div>
                        <Progress value={pct} size="sm" />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Rural/Urban */}
              <div>
                <h4 className="text-sm font-medium mb-3 font-[var(--font-dm-sans)]">Rural / Urban</h4>
                <div className="space-y-2">
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-muted-foreground font-[var(--font-dm-sans)]">Rural</span>
                      <span className="font-medium font-[var(--font-jetbrains-mono)] tabular-nums">{fairness.ruralUrbanRatio.rural}%</span>
                    </div>
                    <Progress value={fairness.ruralUrbanRatio.rural} size="sm" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-muted-foreground font-[var(--font-dm-sans)]">Urban</span>
                      <span className="font-medium font-[var(--font-jetbrains-mono)] tabular-nums">{fairness.ruralUrbanRatio.urban}%</span>
                    </div>
                    <Progress value={fairness.ruralUrbanRatio.urban} size="sm" />
                  </div>
                  <div className="pt-2 border-t">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-[var(--role-primary-600)]" />
                      <span className="text-sm font-medium font-[var(--font-dm-sans)]">
                        Representation Index: <span className="font-[var(--font-space-grotesk)] tabular-nums">{fairness.representationIndex.toFixed(2)}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}