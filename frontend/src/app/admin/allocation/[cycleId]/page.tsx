"use client";

import { use, useState } from "react";
import Link from "next/link";
import { useCycleDetail, useCycleResults } from "@/hooks/use-allocation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, SortableHeader } from "@/components/ui/table";
import { Tabs } from "@/components/ui/tabs";
import { SkeletonCard, SkeletonTable } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { formatDate, formatNumber } from "@/lib/utils";
import {
  ArrowLeft,
  CheckCircle,
  Clock,
  BarChart3,
  Star,
} from "lucide-react";

export default function CycleDetailPage({ params }: { params: Promise<{ cycleId: string }> }) {
  const { cycleId } = use(params);
  const { data: cycle, isLoading: cycleLoading } = useCycleDetail(cycleId);
  const { data: results, isLoading: resultsLoading } = useCycleResults(cycleId);
  const [sortField, setSortField] = useState("matchScore");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const handleSort = (field: string) => {
    if (sortField === field) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortField(field); setSortDir("desc"); }
  };

  const sortedResults = [...(results ?? [])].sort((a, b) => {
    const aVal = a[sortField as keyof typeof a] ?? 0;
    const bVal = b[sortField as keyof typeof b] ?? 0;
    if (typeof aVal === "number" && typeof bVal === "number") return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    return sortDir === "asc" ? String(aVal).localeCompare(String(bVal)) : String(bVal).localeCompare(String(aVal));
  });

  const waitlist = sortedResults.filter((r) => r.status === "declined");

  if (cycleLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
        <SkeletonTable />
      </div>
    );
  }

  if (!cycle) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Cycle not found.</p>
        <Link href="/admin/allocation"><Button variant="outline" className="mt-4">Back to Allocation</Button></Link>
      </div>
    );
  }

  const fairnessTab = {
    id: "fairness",
    label: "Fairness Metrics",
    icon: <BarChart3 className="h-4 w-4" />,
    content: (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle className="text-base">Gender Distribution</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(cycle.fairnessMetrics.genderDistribution).map(([key, val]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm">{key}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 rounded-full bg-muted overflow-hidden">
                    <div className="h-full rounded-full bg-navy-500" style={{ width: `${val}%` }} />
                  </div>
                  <span className="text-sm font-medium w-10 text-right">{val}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Category Distribution</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(cycle.fairnessMetrics.categoryDistribution).map(([key, val]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm">{key}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 rounded-full bg-muted overflow-hidden">
                    <div className="h-full rounded-full bg-saffron-500" style={{ width: `${val}%` }} />
                  </div>
                  <span className="text-sm font-medium w-10 text-right">{val}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Rural vs Urban</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex-1 text-center p-4 rounded-lg bg-green-50">
                <p className="text-2xl font-bold text-green-700">{cycle.fairnessMetrics.ruralUrbanRatio.rural}%</p>
                <p className="text-xs text-green-600">Rural</p>
              </div>
              <div className="flex-1 text-center p-4 rounded-lg bg-blue-50">
                <p className="text-2xl font-bold text-blue-700">{cycle.fairnessMetrics.ruralUrbanRatio.urban}%</p>
                <p className="text-xs text-blue-600">Urban</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Representation Index</CardTitle></CardHeader>
          <CardContent className="text-center py-6">
            <p className="text-4xl font-bold text-navy-600">
              {(cycle.fairnessMetrics.representationIndex * 100).toFixed(0)}%
            </p>
            <p className="text-sm text-muted-foreground mt-1">Overall fairness score</p>
          </CardContent>
        </Card>
      </div>
    ),
  };

  const resultsTab = {
    id: "results",
    label: `Results (${(results ?? []).length})`,
    icon: <CheckCircle className="h-4 w-4" />,
    content: resultsLoading ? (
      <SkeletonTable rows={5} cols={6} />
    ) : !results || results.length === 0 ? (
      <EmptyState icon="inbox" title="No results yet" description="Results will appear after allocation completes" />
    ) : (
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <SortableHeader sortField="candidateName" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>Candidate</SortableHeader>
                <TableHead className="hidden md:table-cell">Opportunity</TableHead>
                <TableHead className="hidden lg:table-cell">Employer</TableHead>
                <SortableHeader sortField="matchScore" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>Match</SortableHeader>
                <TableHead>Status</TableHead>
                <TableHead className="hidden lg:table-cell">Allocated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedResults.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">{r.candidateName}</TableCell>
                  <TableCell className="hidden md:table-cell text-sm text-muted-foreground">{r.opportunityTitle}</TableCell>
                  <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">{r.employerName}</TableCell>
                  <TableCell>
                    <span className="flex items-center gap-1 text-sm font-bold text-saffron-600">
                      <Star className="h-3.5 w-3.5 fill-current" /> {r.matchScore}%
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant="status" status={r.status} size="sm">{r.status}</Badge>
                  </TableCell>
                  <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">
                    {formatDate(r.allocatedAt)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    ),
  };

  const waitlistTab = {
    id: "waitlist",
    label: `Waitlist (${waitlist.length})`,
    icon: <Clock className="h-4 w-4" />,
    content: waitlist.length === 0 ? (
      <EmptyState icon="inbox" title="No waitlisted candidates" />
    ) : (
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Candidate</TableHead>
                <TableHead>Opportunity</TableHead>
                <TableHead>Match Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {waitlist.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">{r.candidateName}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{r.opportunityTitle}</TableCell>
                  <TableCell className="text-sm font-bold text-saffron-600">{r.matchScore}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    ),
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={cycle.name}
        description={`Allocation cycle details and results`}
        breadcrumbs={[
          { label: "Allocation", href: "/admin/allocation" },
          { label: cycle.name },
        ]}
        actions={
          <Link href="/admin/allocation">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
          </Link>
        }
      />

      {/* Cycle Info */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Badge variant="status" status={cycle.status}>{cycle.status}</Badge>
            {cycle.startedAt && <span className="text-sm text-muted-foreground">Started: {formatDate(cycle.startedAt)}</span>}
            {cycle.completedAt && <span className="text-sm text-muted-foreground">Completed: {formatDate(cycle.completedAt)}</span>}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Candidates</p>
              <p className="text-lg font-bold">{formatNumber(cycle.totalCandidates)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Opportunities</p>
              <p className="text-lg font-bold">{formatNumber(cycle.totalOpportunities)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Allocations</p>
              <p className="text-lg font-bold">{formatNumber(cycle.totalAllocations)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Fairness Index</p>
              <p className="text-lg font-bold">{(cycle.fairnessMetrics.representationIndex * 100).toFixed(0)}%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs tabs={[resultsTab, fairnessTab, waitlistTab]} defaultTab="results" />
    </div>
  );
}
