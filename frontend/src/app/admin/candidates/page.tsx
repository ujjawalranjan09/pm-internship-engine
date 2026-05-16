"use client";

import { useState } from "react";
import { useCandidates } from "@/hooks/use-candidates";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/shared/page-header";
import { SkeletonCard } from "@/components/shared/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { formatDate, cn } from "@/lib/utils";
import type { Education } from "@/types/candidate";
import {
  Search,
  MapPin,
  GraduationCap,
  ChevronLeft,
  ChevronRight,
  Download,
} from "lucide-react";

function getEducationLabel(education: Education[] | string): string {
  if (!education) return "\u2014";
  if (typeof education === "string") return education || "\u2014";
  return education[0]?.degree ?? "\u2014";
}

export default function AdminCandidatesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const pageSize = 20;

  const { data, isLoading } = useCandidates(page, pageSize, {
    search: search || undefined,
    socialCategory: categoryFilter || undefined,
  });

  const candidates = data?.items ?? [];
  const totalPages = data?.totalPages ?? 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Candidate Management"
        description={`${data?.total ?? 0} registered candidates`}
      />

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, state, or skills..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="pl-9"
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 border rounded-md text-sm bg-background"
            >
              <option value="">All Categories</option>
              <option value="general">General</option>
              <option value="obc">OBC</option>
              <option value="sc">SC</option>
              <option value="st">ST</option>
              <option value="ews">EWS</option>
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
          ) : candidates.length === 0 ? (
            <div className="p-6">
              <EmptyState
                icon="users"
                title="No candidates found"
                description="Try adjusting your filters"
              />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">State</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Category</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Education</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Skills</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Profile</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Rural</th>
                      <th className="text-left px-4 py-3 font-medium text-muted-foreground">Joined</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidates.map((c) => (
                      <tr key={c.id} className="border-b hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3">
                          <p className="font-medium">{c.name}</p>
                          <p className="text-xs text-muted-foreground">{c.email}</p>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1 text-muted-foreground">
                            <MapPin className="h-3.5 w-3.5" />
                            {c.state ?? "\u2014"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="outline" size="sm">
                            {c.socialCategory?.toUpperCase() ?? "\u2014"}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1 text-muted-foreground">
                            <GraduationCap className="h-3.5 w-3.5" />
                            {getEducationLabel(c.education)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1">
                            {c.skills?.slice(0, 3).map((s) => (
                              <Badge key={s} variant="secondary" size="sm">{s}</Badge>
                            ))}
                            {(c.skills?.length ?? 0) > 3 && (
                              <Badge variant="secondary" size="sm">+{c.skills!.length - 3}</Badge>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                              <div
                                className="h-full bg-navy-500 rounded-full"
                                style={{ width: `${c.profileCompletion ?? 0}%` }}
                              />
                            </div>
                            <span className="text-xs text-muted-foreground">{c.profileCompletion ?? 0}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {c.isRural ? (
                            <Badge variant="default" size="sm">Rural</Badge>
                          ) : (
                            <Badge variant="outline" size="sm">Urban</Badge>
                          )}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground text-xs">
                          {formatDate(c.createdAt)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between px-4 py-3 border-t">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1}\u2013{Math.min(page * pageSize, data?.total ?? 0)} of {data?.total ?? 0}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm font-medium">
                    {page} / {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => p + 1)}
                  >
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
