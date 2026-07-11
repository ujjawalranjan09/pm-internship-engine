"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { SkeletonTable } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { formatDate, cn } from "@/lib/utils";
import {
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  Filter,
  ArrowRight,
  XCircle as XCircleIcon,
} from "lucide-react";

interface Application {
  id: string;
  opportunityId: string;
  title: string;
  company: string;
  sector: string;
  location: string;
  stipend: number;
  appliedAt: string;
  status: string;
  matchScore: number;
  timeline: { date: string; event: string; description: string }[];
}

const MOCK_APPLICATIONS: Application[] = [
  {
    id: "a1", opportunityId: "o1", title: "Software Development Intern", company: "TechCorp India", sector: "IT", location: "Bangalore", stipend: 15000, appliedAt: "2025-01-20T10:00:00Z", status: "shortlisted", matchScore: 87,
    timeline: [
      { date: "2025-01-20T10:00:00Z", event: "Application Submitted", description: "Your application was submitted successfully" },
      { date: "2025-01-22T14:00:00Z", event: "Under Review", description: "Application is being reviewed by the employer" },
      { date: "2025-01-25T09:00:00Z", event: "Shortlisted", description: "Congratulations! You've been shortlisted" },
    ],
  },
  {
    id: "a2", opportunityId: "o2", title: "Data Analytics Intern", company: "FinServ Ltd", sector: "Finance", location: "Mumbai", stipend: 12000, appliedAt: "2025-01-22T14:00:00Z", status: "submitted", matchScore: 72,
    timeline: [
      { date: "2025-01-22T14:00:00Z", event: "Application Submitted", description: "Your application was submitted successfully" },
    ],
  },
  {
    id: "a3", opportunityId: "o6", title: "Cloud Infrastructure Intern", company: "CloudFirst", sector: "IT", location: "Hyderabad", stipend: 16000, appliedAt: "2025-01-18T09:00:00Z", status: "allocated", matchScore: 79,
    timeline: [
      { date: "2025-01-18T09:00:00Z", event: "Application Submitted", description: "Your application was submitted successfully" },
      { date: "2025-01-19T11:00:00Z", event: "Under Review", description: "Application is being reviewed" },
      { date: "2025-01-21T16:00:00Z", event: "Shortlisted", description: "You've been shortlisted for this role" },
      { date: "2025-01-25T08:00:00Z", event: "Matched", description: "AI matching completed" },
      { date: "2025-01-28T10:00:00Z", event: "Allocated", description: "You've been allocated this internship" },
    ],
  },
  {
    id: "a4", opportunityId: "o3", title: "Digital Marketing Intern", company: "MediaGroup", sector: "Media", location: "Delhi", stipend: 10000, appliedAt: "2025-01-15T11:00:00Z", status: "rejected", matchScore: 58,
    timeline: [
      { date: "2025-01-15T11:00:00Z", event: "Application Submitted", description: "Your application was submitted successfully" },
      { date: "2025-01-17T09:00:00Z", event: "Under Review", description: "Application is being reviewed" },
      { date: "2025-01-19T14:00:00Z", event: "Rejected", description: "Unfortunately, your application was not selected" },
    ],
  },
  {
    id: "a5", opportunityId: "o5", title: "Mechanical Engineering Intern", company: "AutoMakers India", sector: "Manufacturing", location: "Pune", stipend: 13000, appliedAt: "2025-01-25T08:00:00Z", status: "under_review", matchScore: 68,
    timeline: [
      { date: "2025-01-25T08:00:00Z", event: "Application Submitted", description: "Your application was submitted successfully" },
      { date: "2025-01-26T10:00:00Z", event: "Under Review", description: "Application is being reviewed by the employer" },
    ],
  },
];

const statusLabels: Record<string, string> = {
  submitted: "Submitted",
  under_review: "Under Review",
  shortlisted: "Shortlisted",
  matched: "Matched",
  allocated: "Allocated",
  accepted: "Accepted",
  declined: "Declined",
  withdrawn: "Withdrawn",
  rejected: "Rejected",
};

const statusIcons: Record<string, React.ReactNode> = {
  submitted: <Clock className="h-4 w-4" />,
  under_review: <Eye className="h-4 w-4" />,
  shortlisted: <CheckCircle className="h-4 w-4" />,
  matched: <CheckCircle className="h-4 w-4" />,
  allocated: <CheckCircle className="h-4 w-4" />,
  accepted: <CheckCircle className="h-4 w-4" />,
  rejected: <XCircle className="h-4 w-4" />,
  declined: <XCircle className="h-4 w-4" />,
  withdrawn: <XCircle className="h-4 w-4" />,
};

export default function ApplicationsPage() {
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [activeTab, setActiveTab] = useState("table");

  const filteredApplications = statusFilter
    ? MOCK_APPLICATIONS.filter((a) => a.status === statusFilter)
    : MOCK_APPLICATIONS;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="My Applications"
        description="Track and manage your internship applications"
        breadcrumbs={[{ label: "Dashboard", href: "/applicant" }, { label: "Applications" }]}
        action={
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Select
              options={[
                { label: "All Statuses", value: "" },
                { label: "Submitted", value: "submitted" },
                { label: "Under Review", value: "under_review" },
                { label: "Shortlisted", value: "shortlisted" },
                { label: "Allocated", value: "allocated" },
                { label: "Rejected", value: "rejected" },
              ]}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter by status"
            />
          </div>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total", value: MOCK_APPLICATIONS.length, icon: FileText },
          { label: "Pending", value: MOCK_APPLICATIONS.filter((a) => ["submitted", "under_review"].includes(a.status)).length, icon: Clock },
          { label: "Shortlisted", value: MOCK_APPLICATIONS.filter((a) => a.status === "shortlisted").length, icon: CheckCircle },
          { label: "Allocated", value: MOCK_APPLICATIONS.filter((a) => a.status === "allocated").length, icon: CheckCircle },
        ].map((stat) => (
          <Card key={stat.label} className="card-hover">
            <CardContent className="p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <stat.icon className="h-5 w-5 text-[var(--role-primary-600)]" />
                <span className="text-sm font-medium text-muted-foreground font-[var(--font-dm-sans)]">{stat.label}</span>
              </div>
              <p className="text-2xl font-bold text-foreground font-[var(--font-space-grotesk)] tabular-nums">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full">
          <TabsTrigger value="table">
            <FileText className="h-4 w-4 mr-1.5" />
            Table View
          </TabsTrigger>
          <TabsTrigger value="timeline">
            <Clock className="h-4 w-4 mr-1.5" />
            Timeline View
          </TabsTrigger>
        </TabsList>

        <TabsContent value="table">
          <Card>
            <CardContent className="p-0">
              {filteredApplications.length === 0 ? (
                <EmptyState
                  icon="file"
                  title="No applications found"
                  description={statusFilter ? "No applications with this status" : "Start applying to internships"}
                  action={{ label: "Browse Internships", href: "/applicant/internships" }}
                />
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Internship</TableHead>
                      <TableHead className="hidden md:table-cell font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Company</TableHead>
                      <TableHead className="hidden lg:table-cell font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Applied</TableHead>
                      <TableHead className="font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Status</TableHead>
                      <TableHead className="hidden sm:table-cell font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Match</TableHead>
                      <TableHead className="text-right font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredApplications.map((app) => (
                      <TableRow
                        key={app.id}
                        className="cursor-pointer"
                        onClick={() => setSelectedApp(app)}
                      >
                        <TableCell>
                          <div>
                            <p className="font-medium text-sm font-[var(--font-dm-sans)]">{app.title}</p>
                            <p className="text-xs text-muted-foreground md:hidden font-[var(--font-dm-sans)]">{app.company}</p>
                          </div>
                        </TableCell>
                        <TableCell className="hidden md:table-cell text-sm text-muted-foreground font-[var(--font-dm-sans)]">
                          {app.company}
                        </TableCell>
                        <TableCell className="hidden lg:table-cell text-sm text-muted-foreground font-[var(--font-jetbrains-mono)]">
                          {formatDate(app.appliedAt)}
                        </TableCell>
                        <TableCell>
                          <Badge variant="status" status={app.status} size="sm">
                            {statusLabels[app.status] ?? app.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="hidden sm:table-cell">
                          <span className="text-sm font-medium text-[var(--role-primary-600)] font-[var(--font-jetbrains-mono)] tabular-nums">{app.matchScore}%</span>
                        </TableCell>
                        <TableCell className="text-right">
                          <Link href={`/applicant/internships/${app.opportunityId}`}>
                            <Button variant="ghost" size="sm" onClick={(e) => e.stopPropagation()}>
                              View <ArrowRight className="ml-1 h-3 w-3" />
                            </Button>
                          </Link>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline">
          <div className="space-y-4">
            {filteredApplications.length === 0 ? (
              <EmptyState
                icon="file"
                title="No applications found"
                description="Start applying to internships to see your timeline"
              />
            ) : (
              filteredApplications.map((app) => (
                <Card key={app.id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setSelectedApp(app)}>
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold font-[var(--font-dm-sans)]">{app.title}</h3>
                        <p className="text-sm text-muted-foreground font-[var(--font-dm-sans)]">{app.company} · {app.location}</p>
                      </div>
                      <Badge variant="status" status={app.status}>
                        {statusLabels[app.status] ?? app.status}
                      </Badge>
                    </div>
                    <div className="relative pl-6 space-y-4">
                      <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-muted" />
                      {app.timeline.map((event, idx) => (
                        <div key={idx} className="relative flex items-start gap-3">
                          <div
                            className={cn(
                              "absolute -left-[18px] h-3 w-3 rounded-full border-2 bg-white",
                              idx === app.timeline.length - 1
                                ? "border-saffron-500"
                                : "border-muted-foreground"
                            )}
                          />
                          <div className="ml-2">
                            <p className="text-sm font-medium font-[var(--font-dm-sans)]">{event.event}</p>
                            <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">{event.description}</p>
                            <p className="text-xs text-muted-foreground mt-0.5 font-[var(--font-jetbrains-mono)]">
                              {formatDate(event.date, "dd MMM yyyy, hh:mm a")}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Timeline Detail Drawer */}
      {selectedApp && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSelectedApp(null)} aria-hidden="true" />
          <div className="relative z-50 w-full max-w-lg bg-white rounded-t-xl sm:rounded-xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold font-[var(--font-space-grotesk)]">{selectedApp.title}</h2>
                <p className="text-sm text-muted-foreground font-[var(--font-dm-sans)]">{selectedApp.company}</p>
              </div>
              <button onClick={() => setSelectedApp(null)} className="p-1 rounded hover:bg-muted" aria-label="Close">
                <XCircleIcon className="h-5 w-5" />
              </button>
            </div>
            <Badge variant="status" status={selectedApp.status} className="mb-4">
              {statusLabels[selectedApp.status] ?? selectedApp.status}
            </Badge>
            <div className="relative pl-6 space-y-4">
              <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-muted" />
              {selectedApp.timeline.map((event, idx) => (
                <div key={idx} className="relative">
                  <div
                    className={cn(
                      "absolute -left-[18px] h-3 w-3 rounded-full border-2 bg-white",
                      idx === selectedApp.timeline.length - 1 ? "border-saffron-500" : "border-muted-foreground"
                    )}
                  />
                  <div className="ml-2">
                    <p className="text-sm font-medium font-[var(--font-dm-sans)]">{event.event}</p>
                    <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">{event.description}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 font-[var(--font-jetbrains-mono)]">
                      {formatDate(event.date, "dd MMM yyyy, hh:mm a")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 flex gap-2">
              <Link href={`/applicant/internships/${selectedApp.opportunityId}`} className="flex-1">
                <Button variant="outline" className="w-full">View Internship</Button>
              </Link>
              <Button variant="ghost" onClick={() => setSelectedApp(null)}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}