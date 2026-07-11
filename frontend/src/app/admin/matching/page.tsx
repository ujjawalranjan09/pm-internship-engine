"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import * as matchingService from "@/services/matching-service";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/shared/page-header";
import { StatsCard } from "@/components/shared/stats-card";
import { formatDate, cn } from "@/lib/utils";
import {
  Activity,
  Play,
  RefreshCw,
  Users,
  Briefcase,
  BarChart3,
  CheckCircle,
} from "lucide-react";

const MOCK_PIPELINE_STAGES = [
  { name: "Rule-Based Filtering", status: "complete", candidates: 12450, passed: 9800, time: "2.3s" },
  { name: "Hybrid Retrieval", status: "complete", candidates: 9800, passed: 4200, time: "5.1s" },
  { name: "Feature-Based Scoring", status: "complete", candidates: 4200, passed: 4200, time: "8.7s" },
  { name: "Fairness Re-Ranking", status: "complete", candidates: 4200, passed: 4200, time: "1.2s" },
  { name: "Constrained Optimization", status: "complete", candidates: 4200, passed: 3800, time: "12.4s" },
];

export default function AdminMatchingPage() {
  const queryClient = useQueryClient();
  const [lastRun, setLastRun] = useState<string | null>(null);

  const triggerMutation = useMutation({
    mutationFn: () => matchingService.triggerBatchMatching(),
    onSuccess: () => {
      setLastRun(new Date().toISOString());
      queryClient.invalidateQueries({ queryKey: ["matches"] });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Matching Engine"
        description="Multi-stage AI matching pipeline: filter → retrieve → rank → explain"
      />

      {/* Pipeline Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="h-5 w-5 text-navy-600" />
            Pipeline Stages
          </CardTitle>
          <CardDescription>
            5-stage matching pipeline with candidate flow at each stage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {MOCK_PIPELINE_STAGES.map((stage, i) => (
              <div key={stage.name} className="relative">
                {i < MOCK_PIPELINE_STAGES.length - 1 && (
                  <div className="absolute left-5 top-10 w-0.5 h-6 bg-border" />
                )}
                <div className="flex items-start gap-4">
                  <div className="shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-medium">{stage.name}</h4>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>{stage.time}</span>
                        <Badge variant="outline" size="sm">Complete</Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Input: {stage.candidates.toLocaleString()}</span>
                      <span>→</span>
                      <span>Output: {stage.passed.toLocaleString()}</span>
                      <span className="text-muted-foreground">
                        ({Math.round((stage.passed / stage.candidates) * 100)}% pass rate)
                      </span>
                    </div>
                    <Progress
                      value={(stage.passed / MOCK_PIPELINE_STAGES[0].candidates) * 100}
                      size="sm"
                      className="mt-2"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Trigger Batch Matching</CardTitle>
            <CardDescription>
              Run the full matching pipeline for all active candidates against active opportunities
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <StatsCard
                title="Candidates"
                value={12450}
                icon={<Users className="h-5 w-5" />}
              />
              <StatsCard
                title="Opportunities"
                value={3200}
                icon={<Briefcase className="h-5 w-5" />}
              />
            </div>

            <Button
              className="w-full"
              onClick={() => triggerMutation.mutate()}
              disabled={triggerMutation.isPending}
            >
              {triggerMutation.isPending ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-1.5 animate-spin" />
                  Running Pipeline...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-1.5" />
                  Run Full Matching Pipeline
                </>
              )}
            </Button>

            {lastRun && (
              <p className="text-xs text-muted-foreground text-center">
                Last run: {formatDate(lastRun)}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Score Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-navy-600" />
              Score Distribution
            </CardTitle>
            <CardDescription>Match score distribution across all candidates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { range: "90-100%", count: 420, color: "bg-green-500" },
                { range: "80-89%", count: 1250, color: "bg-green-400" },
                { range: "70-79%", count: 2100, color: "bg-blue-500" },
                { range: "60-69%", count: 3200, color: "bg-blue-400" },
                { range: "50-59%", count: 2800, color: "bg-amber-500" },
                { range: "40-49%", count: 1680, color: "bg-amber-400" },
                { range: "< 40%", count: 1000, color: "bg-gray-400" },
              ].map((bucket) => {
                const maxCount = 3200;
                return (
                  <div key={bucket.range} className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-16 shrink-0">{bucket.range}</span>
                    <div className="flex-1 h-5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full transition-all", bucket.color)}
                        style={{ width: `${(bucket.count / maxCount) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium w-12 text-right">{bucket.count.toLocaleString()}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weight Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Matching Weights</CardTitle>
          <CardDescription>Current scoring weights used in the matching pipeline</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { label: "Skill Similarity", weight: 0.30, color: "bg-blue-500" },
              { label: "Location Preference", weight: 0.20, color: "bg-green-500" },
              { label: "Education Fit", weight: 0.15, color: "bg-purple-500" },
              { label: "Sector Interest", weight: 0.15, color: "bg-amber-500" },
              { label: "Social Equity", weight: 0.10, color: "bg-pink-500" },
              { label: "Profile Completeness", weight: 0.10, color: "bg-teal-500" },
            ].map((w) => (
              <div key={w.label} className="text-center">
                <div className="text-2xl font-bold text-navy-600">{Math.round(w.weight * 100)}%</div>
                <p className="text-xs text-muted-foreground mt-1">{w.label}</p>
                <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className={cn("h-full rounded-full", w.color)} style={{ width: `${w.weight * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
