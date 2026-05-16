"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import * as adminService from "@/services/admin-service";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/shared/page-header";
import { SkeletonCard } from "@/components/shared/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { formatDate, cn } from "@/lib/utils";
import {
  Search,
  FileText,
  Shield,
  User,
  GitMerge,
  Briefcase,
  Settings,
  ChevronLeft,
  ChevronRight,
  Download,
  Filter,
} from "lucide-react";

const actionIcons: Record<string, typeof Shield> = {
  create: FileText,
  update: Settings,
  delete: Shield,
  login: User,
  allocate: GitMerge,
  override: Shield,
  match: Briefcase,
};

const actionColors: Record<string, string> = {
  create: "text-green-600 bg-green-50",
  update: "text-blue-600 bg-blue-50",
  delete: "text-red-600 bg-red-50",
  login: "text-purple-600 bg-purple-50",
  allocate: "text-amber-600 bg-amber-50",
  override: "text-orange-600 bg-orange-50",
  match: "text-teal-600 bg-teal-50",
};

const MOCK_AUDIT_LOGS = [
  { id: "1", action: "allocate", entityType: "allocation", entityId: "a-123", performedBy: "system", performedByName: "System", details: { cycle: "Cycle 2025-01" }, timestamp: "2025-01-25T10:30:00Z" },
  { id: "2", action: "create", entityType: "candidate", entityId: "c-456", performedBy: "u-789", performedByName: "Priya Sharma", details: {}, timestamp: "2025-01-25T09:15:00Z" },
  { id: "3", action: "update", entityType: "opportunity", entityId: "o-789", performedBy: "u-101", performedByName: "TechCorp HR", details: { field: "capacity" }, timestamp: "2025-01-25T08:45:00Z" },
  { id: "4", action: "override", entityType: "allocation", entityId: "a-456", performedBy: "u-001", performedByName: "Admin User", details: { reason: "Candidate request" }, timestamp: "2025-01-24T16:20:00Z" },
  { id: "5", action: "login", entityType: "user", entityId: "u-202", performedBy: "u-202", performedByName: "Rahul Kumar", details: { ip: "192.168.1.1" }, timestamp: "2025-01-24T14:00:00Z" },
  { id: "6", action: "match", entityType: "match", entityId: "m-100", performedBy: "system", performedByName: "System", details: { candidates: 4200 }, timestamp: "2025-01-24T12:00:00Z" },
];

export default function AdminAuditPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("");

  const logs = MOCK_AUDIT_LOGS;
  const filtered = logs.filter((log) => {
    if (actionFilter && log.action !== actionFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        log.action.includes(q) ||
        log.entityType.includes(q) ||
        log.performedByName.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Logs"
        description="Complete audit trail of all system actions for compliance and debugging"
      />

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by action, entity, or user..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-3 py-2 border rounded-md text-sm bg-background"
            >
              <option value="">All Actions</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
              <option value="login">Login</option>
              <option value="allocate">Allocate</option>
              <option value="override">Override</option>
              <option value="match">Match</option>
            </select>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1.5" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Timeline */}
      <Card>
        <CardContent className="p-0">
          {filtered.length === 0 ? (
            <div className="p-6">
              <EmptyState
                icon="file"
                title="No audit logs found"
                description="Try adjusting your filters"
              />
            </div>
          ) : (
            <div className="divide-y">
              {filtered.map((log) => {
                const Icon = actionIcons[log.action] ?? FileText;
                const colorClass = actionColors[log.action] ?? "text-gray-600 bg-gray-50";

                return (
                  <div key={log.id} className="flex items-start gap-4 p-4 hover:bg-muted/30 transition-colors">
                    <div className={cn("shrink-0 w-9 h-9 rounded-lg flex items-center justify-center", colorClass)}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm">
                            <span className="font-medium">{log.performedByName}</span>
                            {" "}
                            <span className="text-muted-foreground">{log.action}d</span>
                            {" "}
                            <Badge variant="outline" size="sm">{log.entityType}</Badge>
                            {" "}
                            <span className="font-mono text-xs text-muted-foreground">{log.entityId}</span>
                          </p>
                          {Object.keys(log.details).length > 0 && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(" · ")}
                            </p>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground shrink-0">
                          {formatDate(log.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {filtered.length} entries
        </p>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">1</span>
          <Button variant="outline" size="sm" disabled>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
