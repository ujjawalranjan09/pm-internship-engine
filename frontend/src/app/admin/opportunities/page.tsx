"use client";

import { useState } from "react";
import { useOpportunities } from "@/hooks/use-opportunities";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/shared/page-header";
import { SkeletonCard } from "@/components/shared/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { formatCurrency, formatDate } from "@/lib/utils";
import {
  Search,
  Briefcase,
  MapPin,
  Users,
  Clock,
  ChevronLeft,
  ChevronRight,
  Plus,
  Download,
} from "lucide-react";

export default function AdminOpportunitiesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sectorFilter, setSectorFilter] = useState("");
  const pageSize = 20;

  const { data, isLoading } = useOpportunities(page, pageSize, {
    search: search || undefined,
    sector: sectorFilter || undefined,
  });

  const opportunities = data?.items ?? [];
  const totalPages = data?.totalPages ?? 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Opportunity Management"
        description={`${data?.total ?? 0} internship opportunities`}
        action={{
          label: "Add Opportunity",
          onClick: () => {},
          icon: <Plus className="h-4 w-4" />,
        }}
      />

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by title, sector, or location..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="pl-9"
              />
            </div>
            <select
              value={sectorFilter}
              onChange={(e) => {
                setSectorFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 border rounded-md text-sm bg-background"
            >
              <option value="">All Sectors</option>
              <option value="technology">Technology</option>
              <option value="finance">Finance</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="manufacturing">Manufacturing</option>
              <option value="agriculture">Agriculture</option>
              <option value="marketing">Marketing</option>
            </select>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1.5" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : opportunities.length === 0 ? (
            <div className="p-6">
              <EmptyState
                icon="briefcase"
                title="No opportunities found"
                description="Try adjusting your filters or add a new opportunity"
              />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Title</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Sector</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Location</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Mode</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Capacity</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Stipend</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Duration</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {opportunities.map((o) => (
                      <tr key={o.id} className="border-b hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3">
                          <p className="font-medium">{o.title}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                            {o.description}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="default" size="sm">{o.sector ?? "—"}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1 text-muted-foreground">
                            <MapPin className="h-3.5 w-3.5" />
                            {o.state ?? o.location ?? "—"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="outline" size="sm">{o.workMode ?? "—"}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1">
                            <Users className="h-3.5 w-3.5 text-muted-foreground" />
                            {o.capacity}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-medium">
                          {o.stipend ? formatCurrency(o.stipend) : "—"}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {o.durationMonths ? `${o.durationMonths} mo` : "—"}
                        </td>
                        <td className="px-4 py-3">
                          <Badge
                            variant="status"
                            status={o.isActive ? "active" : "inactive"}
                            size="sm"
                          >
                            {o.isActive ? "Active" : "Inactive"}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground text-xs">
                          {formatDate(o.createdAt)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between px-4 py-3 border-t">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, data?.total ?? 0)} of {data?.total ?? 0}
                </p>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm font-medium">{page} / {totalPages}</span>
                  <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
