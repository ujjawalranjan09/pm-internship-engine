"use client";

import { useState } from "react";
import Link from "next/link";
import { useOpportunities } from "@/hooks/use-opportunities";
import { useFilterStore } from "@/stores/filter-store";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { formatCurrency, cn } from "@/lib/utils";
import { SECTORS } from "@/lib/constants";
import {
  Search,
  MapPin,
  Star,
  Clock,
  Users,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

const SORT_OPTIONS = [
  { label: "Relevance", value: "relevance" },
  { label: "Match Score (High to Low)", value: "match_desc" },
  { label: "Match Score (Low to High)", value: "match_asc" },
  { label: "Deadline (Soonest)", value: "deadline" },
  { label: "Stipend (High to Low)", value: "stipend_desc" },
];

export default function InternshipsPage() {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("relevance");
  const [showFilters, setShowFilters] = useState(false);
  const {
    searchQuery, sector, state, minStipend, maxStipend,
    setSearchQuery, setSector, setState, setStipendRange, resetFilters,
  } = useFilterStore();

  const filters = {
    sector: sector || undefined,
    state: state || undefined,
    minStipend: minStipend ?? undefined,
    maxStipend: maxStipend ?? undefined,
  };

  const { data, isLoading } = useOpportunities(page, 12, filters);
  const opportunities = data?.items ?? [];
  const totalPages = data?.totalPages ?? 1;

  const sortedOpportunities = [...opportunities].sort((a, b) => {
    switch (sortBy) {
      case "match_desc": return (b.matchScore ?? 0) - (a.matchScore ?? 0);
      case "match_asc": return (a.matchScore ?? 0) - (b.matchScore ?? 0);
      case "stipend_desc": return b.stipend - a.stipend;
      default: return 0;
    }
  });

  const hasActiveFilters = sector || state || minStipend || maxStipend;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Browse Internships"
        description="Find internships that match your skills and interests"
        breadcrumbs={[{ label: "Dashboard", href: "/applicant" }, { label: "Internships" }]}
      />

      {/* Search & Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, company, or skill..."
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={showFilters ? "secondary" : "outline"}
                onClick={() => setShowFilters(!showFilters)}
                aria-expanded={showFilters}
              >
                <SlidersHorizontal className="h-4 w-4 mr-1" />
                Filters
                {hasActiveFilters && (
                  <span className="ml-1 h-5 w-5 rounded-full bg-saffron-500 text-white text-xs flex items-center justify-center">
                    {[sector, state, minStipend, maxStipend].filter(Boolean).length}
                  </span>
                )}
              </Button>
              <Select
                options={SORT_OPTIONS}
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                aria-label="Sort by"
              />
            </div>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <Select
                label="Sector"
                options={[
                  { label: "All Sectors", value: "" },
                  ...SECTORS.map((s) => ({ label: s, value: s })),
                ]}
                value={sector}
                onChange={(e) => setSector(e.target.value)}
              />
              <Select
                label="State"
                options={[
                  { label: "All States", value: "" },
                  { label: "Karnataka", value: "Karnataka" },
                  { label: "Maharashtra", value: "Maharashtra" },
                  { label: "Delhi", value: "Delhi" },
                  { label: "Tamil Nadu", value: "Tamil Nadu" },
                  { label: "Telangana", value: "Telangana" },
                ]}
                value={state}
                onChange={(e) => setState(e.target.value)}
              />
              <Input
                label="Min Stipend (₹)"
                type="number"
                value={minStipend ?? ""}
                onChange={(e) => setStipendRange(e.target.value ? Number(e.target.value) : null, maxStipend)}
                placeholder="e.g., 10000"
              />
              <Input
                label="Max Stipend (₹)"
                type="number"
                value={maxStipend ?? ""}
                onChange={(e) => setStipendRange(minStipend, e.target.value ? Number(e.target.value) : null)}
                placeholder="e.g., 20000"
              />
              {hasActiveFilters && (
                <div className="sm:col-span-2 lg:col-span-4">
                  <Button variant="ghost" size="sm" onClick={resetFilters}>
                    <X className="h-4 w-4 mr-1" /> Clear all filters
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : sortedOpportunities.length === 0 ? (
        <EmptyState
          icon="search"
          title="No internships found"
          description="Try adjusting your filters or search query"
          action={{ label: "Clear Filters", onClick: resetFilters }}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedOpportunities.map((opp) => (
              <Link key={opp.id} href={`/applicant/internships/${opp.id}`}>
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer card-hover">
                  <CardContent className="p-5 flex flex-col h-full">
                    <div className="flex items-start justify-between mb-3">
                      <Badge variant="default" size="sm">{opp.sector}</Badge>
                      {opp.matchScore != null && (
                        <div className="flex items-center gap-1 text-saffron-600 font-bold text-sm font-[var(--font-jetbrains-mono)] tabular-nums">
                          <Star className="h-4 w-4 fill-current" />
                          {opp.matchScore}%
                        </div>
                      )}
                    </div>
                    <h3 className="font-semibold text-base mb-1 line-clamp-2 font-[var(--font-dm-sans)]">{opp.title}</h3>
                    <p className="text-sm text-muted-foreground mb-2 font-[var(--font-dm-sans)]">{opp.employerName}</p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3 font-[var(--font-jetbrains-mono)]">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" /> {opp.location}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {opp.duration} months
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {opp.requiredSkills.slice(0, 3).map((skill) => (
                        <Badge key={skill} variant="outline" size="sm">{skill}</Badge>
                      ))}
                      {opp.requiredSkills.length > 3 && (
                        <Badge variant="outline" size="sm">+{opp.requiredSkills.length - 3}</Badge>
                      )}
                    </div>
                    <div className="mt-auto flex items-center justify-between pt-3 border-t">
                      <span className="text-lg font-bold text-[var(--role-primary-600)] font-[var(--font-space-grotesk)] tabular-nums">
                        {formatCurrency(opp.stipend)}
                        <span className="text-xs font-normal text-muted-foreground font-[var(--font-dm-sans)]">/month</span>
                      </span>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground font-[var(--font-dm-sans)]">
                        <Users className="h-3 w-3" />
                        {opp.filledSlots}/{opp.capacity} filled
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = i + 1;
                return (
                  <Button
                    key={pageNum}
                    variant={page === pageNum ? "primary" : "outline"}
                    size="sm"
                    onClick={() => setPage(pageNum)}
                  >
                    {pageNum}
                  </Button>
                );
              })}
              {totalPages > 5 && <span className="text-muted-foreground font-[var(--font-dm-sans)]">...</span>}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}