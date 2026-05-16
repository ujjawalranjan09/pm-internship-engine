"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import * as adminService from "@/services/admin-service";
import { Card, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, SortableHeader } from "@/components/ui/table";
import { SkeletonTable } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { formatDateTime, cn } from "@/lib/utils";
import {
  Download,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const ACTION_TYPES = [
  "allocation.triggered",
  "allocation.completed",
  "policy.updated",
  "override.approved",
  "override.rejected",
  "candidate.verified",
  "opportunity.approved",
  "notification.sent",
];

const ACTION_COLORS: Record<string, string> = {
  "allocation.triggered": "bg-blue-100 text-blue-800",
  "allocation.completed": "bg-green-100 text-green-800",
  "policy.updated": "bg-purple-100 text-purple-800",
  "override.approved": "bg-green-100 text-green-800",
  "override.rejected": "bg-red-100 text-red-800",
  "candidate.verified": "bg-teal-100 text-teal-800",
  "opportunity.approved": "bg-indigo-100 text-indigo-800",
  "notification.sent": "bg-gray-100 text-gray-800",
};

export default function AuditPage() {
  const { data: auditLog, isLoading } = useQuery({
    queryKey: ["admin", "audit"],
    queryFn: adminService.getAuditLog,
  });

  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortField, setSortField] = useState("timestamp");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const handleSort = (field: string) => {
    if (sortField === field) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortField(field); setSortDir("desc"); }
  };

  const filtered = useMemo(() => {
    if (!auditLog) return [];
    return auditLog.filter((entry) => {
      const matchesSearch = !search ||
        entry.action.toLowerCase().includes(search.toLowerCase()) ||
        entry.performedByName.toLowerCase().includes(search.toLowerCase()) ||
        entry.entityType.toLowerCase().includes(search.toLowerCase());
      const matchesAction = !actionFilter || entry.action === actionFilter;
      const matchesDateFrom = !dateFrom || new Date(entry.timestamp) >= new Date(dateFrom);
      const matchesDateTo = !dateTo || new Date(entry.timestamp) <= new Date(dateTo + "T23:59:59Z");
      return matchesSearch && matchesAction && matchesDateFrom && matchesDateTo;
    }).sort((a, b) => {
      const aVal = a[sortField as keyof typeof a] ?? "";
      const bVal = b[sortField as keyof typeof b] ?? "";
      return sortDir === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }, [auditLog, search, actionFilter, dateFrom, dateTo, sortField, sortDir]);

  const totalPages = Math.ceil(filtered.length / pageSize);
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  const handleExport = () => {
    const headers = ["Timestamp", "User", "Action", "Entity Type", "Entity ID", "Details"];
    const rows = filtered.map((e) => [
      e.timestamp,
      e.performedByName,
      e.action,
      e.entityType,
      e.entityId,
      JSON.stringify(e.details),
    ]);
    const csv = [headers, ...rows].map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-log-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Log"
        description="Track all system actions and changes"
        action={
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" /> Export CSV
          </Button>
        }
      />

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            <div className="relative lg:col-span-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search by action, user, or entity..."
                className="pl-10"
              />
            </div>
            <Select
              options={[
                { label: "All Actions", value: "" },
                ...ACTION_TYPES.map((a) => ({ label: a.replace(/\./g, " ").replace(/\b\w/g, (c) => c.toUpperCase()), value: a })),
              ]}
              value={actionFilter}
              onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
              aria-label="Filter by action"
            />
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
              aria-label="From date"
              placeholder="From"
            />
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
              aria-label="To date"
              placeholder="To"
            />
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-4"><SkeletonTable rows={8} cols={5} /></div>
          ) : paged.length === 0 ? (
            <EmptyState icon="search" title="No audit entries found" description="Try adjusting your filters" />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <SortableHeader sortField="timestamp" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>Timestamp</SortableHeader>
                    <SortableHeader sortField="performedByName" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>User</SortableHeader>
                    <SortableHeader sortField="action" currentSort={{ field: sortField, direction: sortDir }} onSort={handleSort}>Action</SortableHeader>
                    <TableHead className="hidden md:table-cell">Entity</TableHead>
                    <TableHead className="hidden lg:table-cell">Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paged.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                        {formatDateTime(entry.timestamp)}
                      </TableCell>
                      <TableCell className="font-medium text-sm">{entry.performedByName}</TableCell>
                      <TableCell>
                        <Badge className={cn("text-xs", ACTION_COLORS[entry.action] ?? "bg-gray-100 text-gray-800")} size="sm">
                          {entry.action}
                        </Badge>
                      </TableCell>
                      <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                        {entry.entityType} / {entry.entityId}
                      </TableCell>
                      <TableCell className="hidden lg:table-cell text-xs text-muted-foreground max-w-[200px] truncate">
                        {Object.entries(entry.details).map(([k, v]) => `${k}: ${String(v)}`).join(", ")}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between p-4 border-t">
                  <span className="text-sm text-muted-foreground">
                    Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, filtered.length)} of {filtered.length}
                  </span>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <span className="text-sm">Page {page} of {totalPages}</span>
                    <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
