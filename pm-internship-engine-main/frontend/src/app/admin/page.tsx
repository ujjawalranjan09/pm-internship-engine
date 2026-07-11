"use client";

import Link from "next/link";
import { useAllocationCycles } from "@/hooks/use-allocation";
import { useCandidates } from "@/hooks/use-candidates";
import { useOpportunities } from "@/hooks/use-opportunities";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatsCard } from "@/components/shared/stats-card";
import { SkeletonStat, SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { formatDate, cn } from "@/lib/utils";
import {
  Users,
  Briefcase,
  GitMerge,
  TrendingUp,
  Activity,
  ArrowRight,
  Play,
  CheckCircle,
  Clock,
  AlertTriangle,
  BarChart3,
} from "lucide-react";

export default function AdminDashboard() {
  const { data: cycles, isLoading: cyclesLoading } = useAllocationCycles();
  const { data: candidatesData, isLoading: candidatesLoading } = useCandidates(1, 1);
  const { data: opportunitiesData, isLoading: opportunitiesLoading } = useOpportunities(1, 1);

  const latestCycle = cycles?.[0];
  const completedCycles = (cycles ?? []).filter((c) => c.status === "completed");
  const totalAllocations = completedCycles.reduce((sum, c) => sum + (c.allocatedCount ?? 0), 0);
  const totalCandidates = candidatesData?.total ?? 0;
  const totalOpportunities = opportunitiesData?.total ?? 0;

  const stats = [
    {
      title: "Candidates",
      value: totalCandidates,
      icon: <Users className="h-5 w-5" />,
      trend: { value: 8, direction: "up" as const, label: "this week" },
    },
    {
      title: "Opportunities",
      value: totalOpportunities,
      icon: <Briefcase className="h-5 w-5" />,
    },
    {
      title: "Total Allocations",
      value: totalAllocations,
      icon: <GitMerge className="h-5 w-5" />,
    },
    {
      title: "Active Cycles",
      value: cycles?.filter((c) => c.status === "running").length ?? 0,
      icon: <Activity className="h-5 w-5" />,
    },
    {
      title: "Avg Match Score",
      value: 73.5,
      format: "percentage",
      icon: <TrendingUp className="h-5 w-5" />,
    },
    {
      title: "Pending",
      value: cycles?.filter((c) => c.status === "pending").length ?? 0,
      icon: <Clock className="h-5 w-5" />,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Admin Dashboard"
        description="System overview and allocation management"
        breadcrumbs={[{ label: "Dashboard" }]}
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4" role="region" aria-label="System statistics">
        {stats.map((stat, idx) => (
          <StatsCard
            key={stat.title}
            {...stat}
            className={cn("animate-fade-in stagger-", idx + 1)}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/admin/allocations">
              <Button className="w-full justify-start gap-2" variant="outline">
                <Play className="h-4 w-4" />
                Run New Allocation Cycle
              </Button>
            </Link>
            <Link href="/admin/matching">
              <Button className="w-full justify-start gap-2" variant="outline">
                <Activity className="h-4 w-4" />
                Trigger Batch Matching
              </Button>
            </Link>
            <Link href="/admin/candidates">
              <Button className="w-full justify-start gap-2" variant="outline">
                <Users className="h-4 w-4" />
                Review Candidates
              </Button>
            </Link>
            <Link href="/admin/audit">
              <Button className="w-full justify-start gap-2" variant="outline">
                <BarChart3 className="h-4 w-4" />
                View Audit Logs
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Allocation Cycles */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base">Recent Allocation Cycles</CardTitle>
              <CardDescription>Latest batch allocation runs</CardDescription>
            </div>
            <Link href="/admin/allocations">
              <Button variant="ghost" size="sm">
                View All <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {cyclesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : !cycles || cycles.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-sm">No allocation cycles yet.</p>
                <p className="text-xs mt-1">Run your first allocation to get started.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {cycles.slice(0, 5).map((cycle) => (
                  <div
                    key={cycle.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{cycle.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(cycle as any).allocatedCount ?? 0} allocations &middot; {formatDate(cycle.createdAt)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge variant="status" status={cycle.status} size="sm">
                        {cycle.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="rounded-full bg-emerald-50 p-2">
              <CheckCircle className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm font-medium font-[var(--font-dm-sans)]">API Server</p>
              <p className="text-xs text-emerald-600 font-[var(--font-dm-sans)]">Healthy</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="rounded-full bg-emerald-50 p-2">
              <CheckCircle className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm font-medium font-[var(--font-dm-sans)]">Database</p>
              <p className="text-xs text-emerald-600 font-[var(--font-dm-sans)]">Connected</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="rounded-full bg-emerald-50 p-2">
              <CheckCircle className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm font-medium font-[var(--font-dm-sans)]">Search Engine</p>
              <p className="text-xs text-emerald-600 font-[var(--font-dm-sans)]">Online</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}