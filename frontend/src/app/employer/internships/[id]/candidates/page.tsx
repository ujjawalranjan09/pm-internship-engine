"use client";

import { use, useState } from "react";
import Link from "next/link";
import { useMatchesForOpportunity } from "@/hooks/use-matches";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, SortableHeader } from "@/components/ui/table";
import { SkeletonTable } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";
import {
  Search,
  ArrowLeft,
  CheckCircle,
  XCircle,
  Eye,
  Star,
  Users,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const MOCK_CANDIDATES = [
  { id: "c1", name: "Priya Sharma", education: "B.Tech Computer Science", skills: ["Python", "React", "SQL"], matchScore: 87, status: "shortlisted", district: "Mumbai", category: "General" },
  { id: "c5", name: "Meera Patel", education: "BCA", skills: ["Java", "Spring Boot", "MySQL"], matchScore: 91, status: "shortlisted", district: "Ahmedabad", category: "EWS" },
  { id: "c6", name: "Arjun Reddy", education: "M.Tech AI", skills: ["Machine Learning", "Python", "TensorFlow"], matchScore: 84, status: "allocated", district: "Hyderabad", category: "OBC" },
  { id: "c2", name: "Rahul Kumar", education: "B.Sc Mathematics", skills: ["Data Analysis", "Excel", "Statistics"], matchScore: 72, status: "applied", district: "Patna", category: "OBC" },
  { id: "c8", name: "Deepak Yadav", education: "B.Com", skills: ["GST", "Accounting", "MS Office"], matchScore: 65, status: "applied", district: "Bhopal", category: "OBC" },
  { id: "c3", name: "Anita Devi", education: "MBA Finance", skills: ["Accounting", "Tally", "Financial Analysis"], matchScore: 79, status: "shortlisted", district: "Jaipur", category: "SC" },
];

export default function CandidatesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { addToast } = useToast();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortField, setSortField] = useState<string>("matchScore");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [selectedCandidate, setSelectedCandidate] = useState<(typeof MOCK_CANDIDATES)[0] | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const filtered = MOCK_CANDIDATES.filter((c) => {
    const matchesSearch = !search || c.name.toLowerCase().includes(search.toLowerCase()) || c.skills.some((s) => s.toLowerCase().includes(search.toLowerCase()));
    const matchesStatus = !statusFilter || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  }).sort((a, b) => {
    const aVal = a[sortField as keyof typeof a] ?? "";
    const bVal = b[sortField as keyof typeof b] ?? "";
    if (typeof aVal === "number" && typeof bVal === "number") {
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    }
    return sortDir === "asc"
      ? String(aVal).localeCompare(String(bVal))
      : String(bVal).localeCompare(String(aVal));
  });

  const toggleSelect = (cid: string) => {
    setSelectedIds((prev) => (prev.includes(cid) ? prev.filter((i) => i !== cid) : [...prev, cid]));
  };

  const handleBulkAction = (action: "shortlist" | "reject") => {
    addToast({
      type: "success",
      title: `Candidates ${action === "shortlist" ? "shortlisted" : "rejected"}`,
      message: `${selectedIds.length} candidates updated.`,
    });
    setSelectedIds([]);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Candidates"
        description="Review and manage candidates for this internship"
        breadcrumbs={[
          { label: "Dashboard", href: "/employer" },
          { label: "Internships", href: "/employer/internships" },
          { label: "Candidates" },
        ]}
        actions={
          <Link href={`/employer/internships/${id}`}>
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
          </Link>
        }
      />

      {/* Filters */}
      <Card>
        <CardContent className="p-4 flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name or skill..."
              className="pl-10"
            />
          </div>
          <Select
            options={[
              { label: "All Statuses", value: "" },
              { label: "Applied", value: "applied" },
              { label: "Shortlisted", value: "shortlisted" },
              { label: "Allocated", value: "allocated" },
            ]}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter by status"
          />
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedIds.length > 0 && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-50 border border-navy-200">
          <span className="text-sm font-medium">{selectedIds.length} selected</span>
          <Button size="sm" onClick={() => handleBulkAction("shortlist")}>
            <CheckCircle className="h-4 w-4 mr-1" /> Shortlist
          </Button>
          <Button size="sm" variant="destructive" onClick={() => handleBulkAction("reject")}>
            <XCircle className="h-4 w-4 mr-1" /> Reject
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setSelectedIds([])}>
            Clear
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {filtered.length === 0 ? (
            <EmptyState icon="search" title="No candidates found" description="Try adjusting your filters" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === filtered.length}
                      onChange={(e) => setSelectedIds(e.target.checked ? filtered.map((c) => c.id) : [])}
                      className="h-4 w-4 rounded border-gray-300"
                      aria-label="Select all"
                    />
                  </TableHead>
                  <SortableHeader sortField="name" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>
                    Name
                  </SortableHeader>
                  <TableHead className="hidden md:table-cell">Education</TableHead>
                  <TableHead className="hidden lg:table-cell">Skills</TableHead>
                  <SortableHeader sortField="matchScore" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>
                    Match
                  </SortableHeader>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((candidate) => (
                  <TableRow key={candidate.id}>
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(candidate.id)}
                        onChange={() => toggleSelect(candidate.id)}
                        className="h-4 w-4 rounded border-gray-300"
                        aria-label={`Select ${candidate.name}`}
                      />
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium text-sm">{candidate.name}</p>
                        <p className="text-xs text-muted-foreground">{candidate.district} · {candidate.category}</p>
                      </div>
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                      {candidate.education}
                    </TableCell>
                    <TableCell className="hidden lg:table-cell">
                      <div className="flex flex-wrap gap-1">
                        {candidate.skills.slice(0, 2).map((s) => (
                          <Badge key={s} variant="outline" size="sm">{s}</Badge>
                        ))}
                        {candidate.skills.length > 2 && (
                          <Badge variant="outline" size="sm">+{candidate.skills.length - 2}</Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Star className="h-3.5 w-3.5 text-saffron-500 fill-current" />
                        <span className="text-sm font-bold text-navy-600">{candidate.matchScore}%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="status" status={candidate.status} size="sm">
                        {candidate.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => setSelectedCandidate(candidate)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Candidate Detail Drawer */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSelectedCandidate(null)} aria-hidden="true" />
          <div className="relative z-50 w-full max-w-lg bg-white rounded-t-xl sm:rounded-xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold">{selectedCandidate.name}</h2>
                <p className="text-sm text-muted-foreground">{selectedCandidate.education}</p>
              </div>
              <button onClick={() => setSelectedCandidate(null)} className="p-1 rounded hover:bg-muted" aria-label="Close">
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant="status" status={selectedCandidate.status}>{selectedCandidate.status}</Badge>
                <Badge variant="outline">{selectedCandidate.category}</Badge>
                <span className="text-sm font-bold text-saffron-600">{selectedCandidate.matchScore}% match</span>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Skills</p>
                <div className="flex flex-wrap gap-1">
                  {selectedCandidate.skills.map((s) => (
                    <Badge key={s} variant="default" size="sm">{s}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Match Explanation</p>
                <div className="space-y-2">
                  {[
                    { name: "Skill Match", score: selectedCandidate.matchScore + 5, desc: `Strong alignment with required skills` },
                    { name: "Education", score: selectedCandidate.matchScore - 5, desc: "Meets education requirements" },
                    { name: "Location", score: selectedCandidate.matchScore - 10, desc: "Different from preferred location" },
                  ].map((f) => (
                    <div key={f.name} className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">{f.name}</span>
                      <span className="font-medium">{f.score}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t">
                <Button className="flex-1" onClick={() => { addToast({ type: "success", title: "Shortlisted" }); setSelectedCandidate(null); }}>
                  <CheckCircle className="h-4 w-4 mr-1" /> Shortlist
                </Button>
                <Button variant="destructive" className="flex-1" onClick={() => { addToast({ type: "info", title: "Rejected" }); setSelectedCandidate(null); }}>
                  <XCircle className="h-4 w-4 mr-1" /> Reject
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
