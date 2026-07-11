"use client";

import Link from "next/link";
import { useOpportunities } from "@/hooks/use-opportunities";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { formatCurrency } from "@/lib/utils";
import {
  PlusCircle,
  MapPin,
  Clock,
  Users,
  Eye,
  Edit3,
} from "lucide-react";

export default function EmployerInternshipsPage() {
  const { data, isLoading } = useOpportunities(1, 20);
  const opportunities = data?.items ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="My Internships"
        description="Manage your posted internship opportunities"
        breadcrumbs={[{ label: "Dashboard", href: "/employer" }, { label: "Internships" }]}
        action={
          <Link href="/employer/internships/new">
            <Button>
              <PlusCircle className="h-4 w-4 mr-2" /> Create New
            </Button>
          </Link>
        }
      />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : opportunities.length === 0 ? (
        <EmptyState
          icon="briefcase"
          title="No internships posted"
          description="Create your first internship opportunity to start receiving applications"
          action={{ label: "Create Internship", href: "/employer/internships/new" }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map((opp) => (
            <Card key={opp.id} className="card-hover">
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <Badge variant="default" size="sm">{opp.sector}</Badge>
                  <Badge
                    variant="status"
                    status={opp.isActive ? "active" : "inactive"}
                    size="sm"
                  >
                    {opp.isActive ? "Active" : "Closed"}
                  </Badge>
                </div>
                <h3 className="font-semibold mb-1 font-[var(--font-dm-sans)]">{opp.title}</h3>
                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3 font-[var(--font-jetbrains-mono)]">
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" /> {opp.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" /> {(opp as any).durationMonths ?? opp.duration ?? "—"} months
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" /> {(opp as any).filledCount ?? 0}/{opp.capacity}
                  </span>
                </div>
                <div className="flex items-center justify-between pt-3 border-t">
                  <span className="text-lg font-bold text-[var(--role-primary-600)] font-[var(--font-space-grotesk)] tabular-nums">
                    {formatCurrency(opp.stipend ?? 0)}
                    <span className="text-xs font-normal text-muted-foreground font-[var(--font-dm-sans)]">/month</span>
                  </span>
                  <div className="flex gap-2">
                    <Link href={`/employer/internships/${opp.id}`}>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" /> View
                      </Button>
                    </Link>
                    <Link href={`/employer/internships/${opp.id}/candidates`}>
                      <Button variant="ghost" size="sm">
                        Candidates
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}