"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as adminService from "@/services/admin-service";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Tabs } from "@/components/ui/tabs";
import { SkeletonTable } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { formatDate, cn } from "@/lib/utils";
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowRightLeft,
  Clock,
  User,
  FileText,
} from "lucide-react";

export default function OverridesPage() {
  const { data: overrides, isLoading } = useQuery({
    queryKey: ["admin", "overrides"],
    queryFn: adminService.getOverrides,
  });
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const approveMutation = useMutation({
    mutationFn: adminService.approveOverride,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "overrides"] });
      addToast({ type: "success", title: "Override approved" });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: adminService.rejectOverride,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "overrides"] });
      addToast({ type: "info", title: "Override rejected" });
    },
  });

  const [selectedOverride, setSelectedOverride] = useState<string | null>(null);
  const [reviewReason, setReviewReason] = useState("");
  const [actionType, setActionType] = useState<"approve" | "reject" | null>(null);

  const pending = (overrides ?? []).filter((o) => o.status === "pending");
  const reviewed = (overrides ?? []).filter((o) => o.status !== "pending");

  const handleAction = () => {
    if (!selectedOverride || !actionType) return;
    if (actionType === "approve") {
      approveMutation.mutate(selectedOverride);
    } else {
      rejectMutation.mutate(selectedOverride);
    }
    setSelectedOverride(null);
    setActionType(null);
    setReviewReason("");
  };

  const pendingTab = {
    id: "pending",
    label: `Pending (${pending.length})`,
    icon: <Clock className="h-4 w-4" />,
    content: isLoading ? (
      <SkeletonTable rows={3} cols={5} />
    ) : pending.length === 0 ? (
      <EmptyState icon="inbox" title="No pending overrides" description="All exception requests have been processed" />
    ) : (
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Candidate</TableHead>
                <TableHead className="hidden md:table-cell">Original</TableHead>
                <TableHead>Target</TableHead>
                <TableHead className="hidden lg:table-cell">Reason</TableHead>
                <TableHead className="hidden lg:table-cell">Requested</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pending.map((ov) => (
                <TableRow key={ov.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium text-sm">{ov.candidateName}</p>
                      <p className="text-xs text-muted-foreground">{ov.candidateId}</p>
                    </div>
                  </TableCell>
                  <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                    {ov.originalOpportunityTitle}
                  </TableCell>
                  <TableCell className="text-sm font-medium">{ov.targetOpportunityTitle}</TableCell>
                  <TableCell className="hidden lg:table-cell text-xs text-muted-foreground max-w-[200px] truncate">
                    {ov.reason}
                  </TableCell>
                  <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">
                    {formatDate(ov.createdAt)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-1 justify-end">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedOverride(ov.id); setActionType("approve"); }}
                      >
                        <CheckCircle className="h-4 w-4 text-gov-success" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedOverride(ov.id); setActionType("reject"); }}
                      >
                        <XCircle className="h-4 w-4 text-gov-error" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    ),
  };

  const historyTab = {
    id: "history",
    label: `History (${reviewed.length})`,
    icon: <FileText className="h-4 w-4" />,
    content: reviewed.length === 0 ? (
      <EmptyState icon="inbox" title="No override history" />
    ) : (
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Candidate</TableHead>
                <TableHead className="hidden md:table-cell">From</TableHead>
                <TableHead>To</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="hidden lg:table-cell">Reviewed</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reviewed.map((ov) => (
                <TableRow key={ov.id}>
                  <TableCell className="font-medium">{ov.candidateName}</TableCell>
                  <TableCell className="hidden md:table-cell text-sm text-muted-foreground">{ov.originalOpportunityTitle}</TableCell>
                  <TableCell className="text-sm">{ov.targetOpportunityTitle}</TableCell>
                  <TableCell>
                    <Badge variant="status" status={ov.status} size="sm">{ov.status}</Badge>
                  </TableCell>
                  <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">
                    {ov.reviewedAt ? formatDate(ov.reviewedAt) : "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    ),
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Overrides"
        description="Manage allocation exception requests"
      />

      <Tabs tabs={[pendingTab, historyTab]} defaultTab="pending" />

      {/* Review Dialog */}
      <Dialog open={!!selectedOverride} onOpenChange={() => { setSelectedOverride(null); setActionType(null); }}>
        <DialogContent onClose={() => { setSelectedOverride(null); setActionType(null); }}>
          <DialogHeader>
            <DialogTitle>
              {actionType === "approve" ? "Approve Override" : "Reject Override"}
            </DialogTitle>
            <DialogDescription>
              {actionType === "approve"
                ? "This will reassign the candidate to the target opportunity."
                : "This will reject the override request."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <label className="block text-sm font-medium">Review Notes (optional)</label>
            <textarea
              value={reviewReason}
              onChange={(e) => setReviewReason(e.target.value)}
              rows={3}
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy-500"
              placeholder="Add notes for this decision..."
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setSelectedOverride(null); setActionType(null); }}>
              Cancel
            </Button>
            <Button
              variant={actionType === "approve" ? "primary" : "destructive"}
              onClick={handleAction}
              loading={approveMutation.isPending || rejectMutation.isPending}
            >
              {actionType === "approve" ? "Approve" : "Reject"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
