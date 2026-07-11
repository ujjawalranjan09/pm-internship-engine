"use client";

import { useFairnessMetrics, useAllocationCycles } from "@/hooks/use-allocation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import {
  Users,
  MapPin,
  Scale,
  TrendingUp,
} from "lucide-react";

const CATEGORY_COLORS: Record<string, string> = {
  General: "bg-navy-500",
  OBC: "bg-saffron-500",
  SC: "bg-blue-500",
  ST: "bg-green-500",
  EWS: "bg-purple-500",
};

export default function FairnessPage() {
  const { data: metrics, isLoading } = useFairnessMetrics();
  const { data: cycles } = useAllocationCycles();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Fairness Dashboard" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const stateEntries = Object.entries(metrics.stateDistribution as Record<string, number>).sort(([, a], [, b]) => b - a);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Fairness Dashboard"
        description="Monitor allocation fairness across demographics and regions"
      />

      {/* Fairness Score Gauge */}
      <Card className="bg-gradient-to-r from-navy-500 to-navy-700 text-white">
        <CardContent className="p-8 flex flex-col md:flex-row items-center gap-8">
          <div className="relative">
            <svg className="w-40 h-40" viewBox="0 0 100 100" aria-label={`Fairness score: ${(metrics.representationIndex * 100).toFixed(0)}%`}>
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="42" fill="none"
                stroke="currentColor"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${metrics.representationIndex * 264} 264`}
                className="text-saffron-400 -rotate-90 origin-center"
              />
              <text x="50" y="45" textAnchor="middle" className="text-2xl font-bold fill-white">
                {(metrics.representationIndex * 100).toFixed(0)}%
              </text>
              <text x="50" y="60" textAnchor="middle" className="text-[8px] fill-white/70">
                Fairness Index
              </text>
            </svg>
          </div>
          <div className="flex-1 text-center md:text-left">
            <h2 className="text-xl font-bold mb-2">Overall Fairness Score</h2>
            <p className="text-navy-200 text-sm leading-relaxed">
              The representation index measures how well the allocation results reflect the target distribution
              across gender, category, and geographic dimensions. A score above 80% indicates good fairness compliance.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 justify-center md:justify-start">
              <Badge className="bg-white/20 text-white border-white/30">
                Target: 80%+
              </Badge>
              <Badge className={cn(
                metrics.representationIndex >= 0.8 ? "bg-green-500/30 text-green-100" : "bg-yellow-500/30 text-yellow-100"
              )}>
                {metrics.representationIndex >= 0.8 ? "✓ Meeting Target" : "⚠ Below Target"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-saffron-500" />
              Category Distribution
            </CardTitle>
            <CardDescription>Allocation by social category</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(metrics.categoryDistribution).map(([cat, pct]) => (
              <div key={cat} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{cat}</span>
                  <span className="text-muted-foreground">{pct}%</span>
                </div>
                <div className="h-3 rounded-full bg-muted overflow-hidden">
                  <div
                    className={cn("h-full rounded-full transition-all duration-700", CATEGORY_COLORS[cat] ?? "bg-gray-400")}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Gender Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-saffron-500" />
              Gender Distribution
            </CardTitle>
            <CardDescription>Allocation by gender</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(metrics.genderDistribution).map(([gender, pct]) => (
                <div key={gender} className="text-center p-4 rounded-lg bg-muted/50">
                  <p className="text-2xl font-bold text-navy-600">{pct}%</p>
                  <p className="text-xs text-muted-foreground mt-1">{gender}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Rural vs Urban */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-saffron-500" />
              Rural vs Urban
            </CardTitle>
            <CardDescription>Geographic distribution of allocations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1 text-center p-4 rounded-lg bg-green-50 border border-green-200">
                <p className="text-3xl font-bold text-green-700">{metrics.ruralUrbanRatio.rural}%</p>
                <p className="text-sm text-green-600">Rural</p>
              </div>
              <div className="flex-1 text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
                <p className="text-3xl font-bold text-blue-700">{metrics.ruralUrbanRatio.urban}%</p>
                <p className="text-sm text-blue-600">Urban</p>
              </div>
            </div>
            <div className="h-4 rounded-full bg-muted overflow-hidden flex">
              <div
                className="h-full bg-green-500 transition-all duration-700"
                style={{ width: `${metrics.ruralUrbanRatio.rural}%` }}
              />
              <div
                className="h-full bg-blue-500 transition-all duration-700"
                style={{ width: `${metrics.ruralUrbanRatio.urban}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Top States */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-saffron-500" />
              State Distribution
            </CardTitle>
            <CardDescription>Top states by allocation percentage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {stateEntries.slice(0, 8).map(([state, pct], idx) => (
              <div key={state} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-4">{idx + 1}</span>
                <span className="text-sm flex-1 truncate">{state}</span>
                <div className="w-24 h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-navy-500" style={{ width: `${(pct / stateEntries[0][1]) * 100}%` }} />
                </div>
                <span className="text-sm font-medium w-10 text-right">{pct}%</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Cycle Comparison */}
      {cycles && cycles.filter((c) => c.status === "completed").length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Fairness Across Cycles</CardTitle>
            <CardDescription>Compare fairness metrics over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {cycles
                .filter((c) => c.status === "completed")
                .map((cycle) => (
                  <div key={cycle.id} className="flex items-center gap-4 p-3 rounded-lg border">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{cycle.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {cycle.totalAllocations} allocations
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress
                        value={cycle.fairnessMetrics.representationIndex * 100}
                        size="sm"
                        className="w-24"
                      />
                      <span className="text-sm font-bold w-12 text-right">
                        {(cycle.fairnessMetrics.representationIndex * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
