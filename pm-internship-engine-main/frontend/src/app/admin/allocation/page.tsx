"use client";

import { useState } from "react";
import Link from "next/link";
import { useAllocationCycles, useTriggerAllocation } from "@/hooks/use-allocation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { SkeletonTable, SkeletonStat } from "@/components/shared/skeleton";
import { StatsCard } from "@/components/shared/stats-card";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { formatDate, formatNumber } from "@/lib/utils";
import {
  Shuffle,
  Play,
  CheckCircle,
  AlertTriangle,
  Users,
  Briefcase,
  ArrowRight,
  Loader2,
} from "lucide-react";

export default function AllocationPage() {
  const { data: cycles, isLoading } = useAllocationCycles();
  const triggerAllocation = useTriggerAllocation();
  const { addToast } = useToast();
  const [showConfirm, setShowConfirm] = useState(false);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const completedCycles = (cycles ?? []).filter((c) => c.status === "completed");
  const latestCycle = completedCycles[0];

  const statsFromCycle = (cycle: typeof latestCycle) => cycle ? {
    totalCandidates: (cycle as any).totalCandidates ?? (cycle as any).allocatedCount ?? 0,
    totalOpportunities: (cycle as any).totalOpportunities ?? 0,
    totalAllocations: (cycle as any).totalAllocations ?? (cycle as any).allocatedCount ?? 0,
    fairnessIndex: (cycle as any).fairnessMetrics?.representationIndex ?? (cycle as any).fairnessScore ?? 0,
  } : null;
  const stats = statsFromCycle(latestCycle);

  const handleTrigger = () => {
    setShowConfirm(false);
    setRunning(true);
    setProgress(0);

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setRunning(false);
          addToast({ type: "success", title: "Allocation complete!", message: "All candidates have been processed." });
          return 100;
        }
        return prev + Math.random() * 15 + 5;
      });
    }, 800);

    triggerAllocation.mutate({ name: `Cycle ${new Date().toISOString().slice(0, 10)}` });
  };

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <PageHeader title="Allocation" />
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonStat key={i} />)}
        </div>
        <SkeletonTable rows={3} cols={5} />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Allocation Management"
        description="Run and monitor allocation cycles"
        breadcrumbs={[{ label: "Admin" }, { label: "Allocation" }]}
        action={
          <Button onClick={() => setShowConfirm(true)} disabled={running}>
            <Play className="h-4 w-4 mr-2" /> Run Allocation
          </Button>
        }
      />

      {/* Running Progress */}
      {running && (
        <Card className="border-saffron-200 bg-saffron-50">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <Loader2 className="h-5 w-5 animate-spin text-saffron-600" />
              <span className="font-semibold text-saffron-800 font-[var(--font-dm-sans)]">Allocation in progress...</span>
            </div>
            <Progress value={Math.min(progress, 100)} size="lg" />
            <p className="text-xs text-muted-foreground mt-2 font-[var(--font-dm-sans)]">
              Processing candidates and matching with opportunities...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <StatsCard title="Total Candidates" value={stats.totalCandidates} icon={<Users className="h-5 w-5" />} />
          <StatsCard title="Opportunities" value={stats.totalOpportunities} icon={<Briefcase className="h-5 w-5" />} />
          <StatsCard title="Allocations Made" value={stats.totalAllocations} icon={<CheckCircle className="h-5 w-5" />} />
          <StatsCard
            title="Fairness Index"
            value={stats.fairnessIndex}
            format="percentage"
            icon={<Shuffle className="h-5 w-5" />}
          />
        </div>
      )}

      {/* Cycles Table */}
      <Card>
        <CardHeader>
          <CardTitle className="font-[var(--font-space-grotesk)]">Allocation Cycles</CardTitle>
          <CardDescription className="font-[var(--font-dm-sans)]">History of all allocation runs</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {!cycles || cycles.length === 0 ? (
            <EmptyState
              icon="inbox"
              title="No allocation cycles"
              description="Run your first allocation to get started"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Name</TableHead>
                  <TableHead className="font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Status</TableHead>
                  <TableHead className="hidden md:table-cell font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Candidates</TableHead>
                  <TableHead className="hidden md:table-cell font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Allocations</TableHead>
                  <TableHead className="hidden lg:table-cell font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Date</TableHead>
                  <TableHead className="text-right font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cycles.map((cycle) => (
                  <TableRow key={cycle.id}>
                    <TableCell className="font-medium font-[var(--font-dm-sans)]">{cycle.name}</TableCell>
                    <TableCell>
                      <Badge variant="status" status={cycle.status} size="sm">
                        {cycle.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="hidden md:table-cell font-[var(--font-jetbrains-mono)] tabular-nums">
                      {(cycle as any).totalCandidates ?? (cycle as any).allocatedCount ?? "—"}
                    </TableCell>
                    <TableCell className="hidden md:table-cell font-[var(--font-jetbrains-mono)] tabular-nums">
                      {(cycle as any).totalAllocations ?? (cycle as any).allocatedCount ?? "—"}
                    </TableCell>
                    <TableCell className="hidden lg:table-cell text-sm text-muted-foreground font-[var(--font-jetbrains-mono)]">
                      {cycle.completedAt
                        ? formatDate(cycle.completedAt)
                        : cycle.startedAt
                        ? formatDate(cycle.startedAt)
                        : formatDate(cycle.createdAt)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/admin/allocation/${cycle.id}`}>
                        <Button variant="ghost" size="sm">
                          Details <ArrowRight className="ml-1 h-3 w-3" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirm} onOpenChange={setShowConfirm}>
        <DialogContent onClose={() => setShowConfirm(false)}>
          <DialogHeader>
            <DialogTitle className="font-[var(--font-space-grotesk)]">Run Allocation Cycle</DialogTitle>
            <DialogDescription className="font-[var(--font-dm-sans)]">
              This will start a new allocation cycle. All eligible candidates will be matched with available opportunities
              based on the current policy configuration. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="p-4 rounded-lg bg-yellow-50 border border-yellow-200">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-5 w-5 text-gov-warning shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-yellow-800 font-[var(--font-dm-sans)]">Important</p>
                <p className="text-xs text-yellow-700 mt-1 font-[var(--font-dm-sans)]">
                  Ensure all candidate profiles are verified and opportunity details are up to date before running allocation.
                </p>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirm(false)}>Cancel</Button>
            <Button onClick={handleTrigger}>
              <Play className="h-4 w-4 mr-2" /> Confirm & Run
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}