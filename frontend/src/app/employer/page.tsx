"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatsCard } from "@/components/shared/stats-card";
import { PageHeader } from "@/components/shared/page-header";
import { formatCurrency, formatDate } from "@/lib/utils";
import Link from "next/link";
import {
  Briefcase,
  Users,
  TrendingUp,
  Plus,
  ArrowRight,
  MapPin,
  Clock,
  CheckCircle,
} from "lucide-react";

const MOCK_OPPORTUNITIES = [
  { id: "1", title: "Software Development Intern", sector: "Technology", capacity: 5, filled: 3, status: "active", location: "Bangalore", stipend: 15000, createdAt: "2025-01-10" },
  { id: "2", title: "Data Analytics Intern", sector: "Finance", capacity: 3, filled: 3, status: "filled", location: "Mumbai", stipend: 12000, createdAt: "2025-01-08" },
  { id: "3", title: "Marketing Intern", sector: "Marketing", capacity: 2, filled: 0, status: "active", location: "Delhi", stipend: 10000, createdAt: "2025-01-15" },
];

const MOCK_MATCHED_CANDIDATES = [
  { id: "1", name: "Amit Patel", opportunity: "Software Development Intern", score: 87, state: "Gujarat" },
  { id: "2", name: "Sneha Reddy", opportunity: "Software Development Intern", score: 82, state: "Telangana" },
  { id: "3", name: "Vikram Singh", opportunity: "Data Analytics Intern", score: 79, state: "Rajasthan" },
];

export default function EmployerDashboard() {
  const totalCapacity = MOCK_OPPORTUNITIES.reduce((s, o) => s + o.capacity, 0);
  const totalFilled = MOCK_OPPORTUNITIES.reduce((s, o) => s + o.filled, 0);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employer Dashboard"
        description="Manage your internship opportunities and review matched candidates"
      />

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Active Opportunities"
          value={MOCK_OPPORTUNITIES.filter((o) => o.status === "active").length}
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
              <CardTitle>My Opportunities</CardTitle>
              <CardDescription>Internship positions you've posted</CardDescription>
            </div>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-1" />
              Add New
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {MOCK_OPPORTUNITIES.map((opp) => (
                <div
                  key={opp.id}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className="min-w-0">
                    <p className="font-medium text-sm">{opp.title}</p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {opp.location}
                      </span>
                      <span>{formatCurrency(opp.stipend)}/mo</span>
                      <span>{opp.filled}/{opp.capacity} filled</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <Badge variant="default" size="sm">{opp.sector}</Badge>
                    <Badge
                      variant="status"
                      status={opp.status === "filled" ? "completed" : "active"}
                      size="sm"
                    >
                      {opp.status === "filled" ? "Filled" : "Active"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Matched Candidates */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top Matched Candidates</CardTitle>
            <CardDescription>AI-recommended candidates for your positions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {MOCK_MATCHED_CANDIDATES.map((c) => (
                <div
                  key={c.id}
                  className="p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium">{c.name}</p>
                    <div className="flex items-center gap-1 text-saffron-600 text-sm font-bold">
                      {c.score}%
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">{c.opportunity}</p>
                  <p className="text-xs text-muted-foreground">{c.state}</p>
                </div>
              ))}
            </div>
            <Link href="/employer/candidates">
              <Button variant="ghost" size="sm" className="w-full mt-3">
                View All <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
