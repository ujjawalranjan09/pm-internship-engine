"use client";

import { useQuery } from "@tanstack/react-query";
import { useOpportunities } from "@/hooks/use-opportunities";
import { useMatches } from "@/hooks/use-matches";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatsCard } from "@/components/shared/stats-card";
import { PageHeader } from "@/components/shared/page-header";
import { formatCurrency, cn } from "@/lib/utils";
import Link from "next/link";
import {
  Briefcase,
  Users,
  TrendingUp,
  Plus,
  ArrowRight,
  MapPin,
  CheckCircle,
} from "lucide-react";

export default function EmployerDashboard() {
  const { data: opportunitiesData, isLoading: opportunitiesLoading } = useOpportunities(1, 10);
  const { data: matchesData, isLoading: matchesLoading } = useMatches();

  const opportunities = opportunitiesData?.items ?? [];
  const matches = matchesData?.items ?? [];

  const totalCapacity = opportunities.reduce((s, o) => s + (o.capacity ?? 0), 0);
  const totalFilled = opportunities.reduce((s, o) => s + ((o as any).filledCount ?? 0), 0);
  const activeOpportunities = opportunities.filter((o) => o.isActive).length;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Employer Dashboard"
        description="Manage your internship opportunities and review matched candidates"
        breadcrumbs={[{ label: "Employer" }, { label: "Dashboard" }]}
        action={
          <Link href="/employer/internships/new">
            <Button>
              <Plus className="h-4 w-4 mr-1.5" />
              Post Opportunity
            </Button>
          </Link>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" role="region" aria-label="System statistics">
        <StatsCard
          title="Active Opportunities"
          value={activeOpportunities}
          icon={<Briefcase className="h-5 w-5" />}
        />
        <StatsCard
          title="Total Capacity"
          value={totalCapacity}
          icon={<Users className="h-5 w-5" />}
        />
        <StatsCard
          title="Positions Filled"
          value={totalFilled}
          icon={<CheckCircle className="h-5 w-5" />}
          trend={{ value: 15, direction: "up", label: "this week" }}
        />
        <StatsCard
          title="Fill Rate"
          value={totalCapacity > 0 ? Math.round((totalFilled / totalCapacity) * 100) : 0}
          format="percentage"
          icon={<TrendingUp className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* My Opportunities */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="font-[var(--font-space-grotesk)]">My Opportunities</CardTitle>
              <CardDescription className="font-[var(--font-dm-sans)]">Internship positions you've posted</CardDescription>
            </div>
            <Link href="/employer/internships/new">
              <Button size="sm">
                <Plus className="h-4 w-4 mr-1.5" />
                Add New
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {opportunitiesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="p-4 rounded-lg border animate-pulse bg-muted/50" />
                ))}
              </div>
            ) : opportunities.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-sm font-[var(--font-dm-sans)]">No opportunities posted yet</p>
                <p className="text-xs mt-1 font-[var(--font-dm-sans)]">Create your first internship opportunity</p>
              </div>
            ) : (
              <div className="space-y-3">
                {opportunities.map((opp) => (
                  <div
                    key={opp.id}
                    className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div className="min-w-0">
                      <p className="font-medium text-sm font-[var(--font-dm-sans)]">{opp.title}</p>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1 font-[var(--font-dm-sans)]">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3.5 w-3.5" />
                          {opp.state ?? opp.location ?? "—"}
                        </span>
                        <span>{formatCurrency(opp.stipend ?? 0)}/mo</span>
                        <span>{(opp as any).filledCount ?? 0}/{opp.capacity} filled</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <Badge variant="default" size="sm">{opp.sector ?? "—"}</Badge>
                      <Badge
                        variant="status"
                        status={opp.isActive ? "active" : "inactive"}
                        size="sm"
                      >
                        {opp.isActive ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Matched Candidates */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-[var(--font-space-grotesk)]">Top Matched Candidates</CardTitle>
            <CardDescription className="font-[var(--font-dm-sans)]">AI-recommended candidates for your positions</CardDescription>
          </CardHeader>
          <CardContent>
            {matchesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="p-3 rounded-lg border animate-pulse bg-muted/50" />
                ))}
              </div>
            ) : matches.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-sm font-[var(--font-dm-sans)]">No matches yet</p>
                <p className="text-xs mt-1 font-[var(--font-dm-sans)]">Run matching to see recommendations</p>
              </div>
            ) : (
              <>
                <div className="space-y-3">
                  {matches.slice(0, 5).map((m) => (
                    <div
                      key={m.id}
                      className="p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-medium font-[var(--font-dm-sans)]">{m.candidateName}</p>
                        <div className="flex items-center gap-1 text-saffron-600 text-sm font-bold font-[var(--font-jetbrains-mono)] tabular-nums">
                          {m.matchScore ?? m.allocationScore ?? 0}%
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">{m.opportunityTitle}</p>
                    </div>
                  ))}
                </div>
                <Link href="/employer/internships">
                  <Button variant="ghost" size="sm" className="w-full mt-3">
                    View All <ArrowRight className="ml-1 h-4 w-4" />
                  </Button>
                </Link>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}