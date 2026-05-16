"use client";

import Link from "next/link";
import { useCandidateProfile } from "@/hooks/use-candidates";
import { useRecommendations } from "@/hooks/use-matches";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { StatsCard } from "@/components/shared/stats-card";
import { SkeletonStat, SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import {
  Briefcase,
  Clock,
  CheckCircle,
  FileText,
  TrendingUp,
  ArrowRight,
  MapPin,
  Star,
} from "lucide-react";

const MOCK_APPLICATIONS = [
  { id: "a1", title: "Software Development Intern", company: "TechCorp India", status: "shortlisted", appliedAt: "2025-01-20T10:00:00Z" },
  { id: "a2", title: "Data Analytics Intern", company: "FinServ Ltd", status: "submitted", appliedAt: "2025-01-22T14:00:00Z" },
  { id: "a3", title: "Cloud Infrastructure Intern", company: "CloudFirst", status: "allocated", appliedAt: "2025-01-18T09:00:00Z" },
  { id: "a4", title: "Digital Marketing Intern", company: "MediaGroup", status: "rejected", appliedAt: "2025-01-15T11:00:00Z" },
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

export default function ApplicantDashboard() {
  const { data: profile, isLoading: profileLoading } = useCandidateProfile();
  const { data: recommendations, isLoading: recsLoading } = useRecommendations();

  const totalApplications = MOCK_APPLICATIONS.length;
  const pendingApplications = MOCK_APPLICATIONS.filter((a) => ["submitted", "under_review", "shortlisted"].includes(a.status)).length;
  const acceptedApplications = MOCK_APPLICATIONS.filter((a) => a.status === "allocated" || a.status === "accepted").length;

  if (profileLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Dashboard" description="Welcome back!" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonStat key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome, ${profile?.name?.split(" ")[0] || "Candidate"}`}
        description="Here's an overview of your internship journey"
      />

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Applications"
          value={totalApplications}
          icon={<FileText className="h-5 w-5" />}
        />
        <StatsCard
          title="Pending"
          value={pendingApplications}
          icon={<Clock className="h-5 w-5" />}
          trend={{ value: 12, direction: "up", label: "this week" }}
        />
        <StatsCard
          title="Accepted / Allocated"
          value={acceptedApplications}
          icon={<CheckCircle className="h-5 w-5" />}
        />
        <StatsCard
          title="Match Score"
          value={profile?.profileCompletion ?? 0}
          format="percentage"
          icon={<Star className="h-5 w-5" />}
          description="Profile strength"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Completion */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-saffron-500" />
              Profile Completion
            </CardTitle>
            <CardDescription>Complete your profile for better matches</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <span className="text-4xl font-bold text-navy-500">
                {profile?.profileCompletion ?? 0}%
              </span>
            </div>
            <Progress value={profile?.profileCompletion ?? 0} size="lg" />
            <div className="space-y-2 text-sm">
              {[
                { label: "Personal Info", done: !!profile?.name && !!profile?.phone },
                { label: "Education", done: (profile?.education?.length ?? 0) > 0 },
                { label: "Skills", done: (profile?.skills?.length ?? 0) > 0 },
                { label: "Preferences", done: (profile?.sectors?.length ?? 0) > 0 },
                { label: "Resume", done: !!profile?.resumeUrl },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className={item.done ? "text-foreground" : "text-muted-foreground"}>
                    {item.label}
                  </span>
                  {item.done ? (
                    <CheckCircle className="h-4 w-4 text-gov-success" />
                  ) : (
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  )}
                </div>
              ))}
            </div>
            <Link href="/applicant/profile">
              <Button variant="secondary" className="w-full">
                Complete Profile
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Applications */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Applications</CardTitle>
              <CardDescription>Track your application progress</CardDescription>
            </div>
            <Link href="/applicant/applications">
              <Button variant="ghost" size="sm">
                View All <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {MOCK_APPLICATIONS.length === 0 ? (
              <EmptyState
                icon="file"
                title="No applications yet"
                description="Start browsing internships and apply to get matched"
                action={{ label: "Browse Internships", onClick: () => {} }}
              />
            ) : (
              <div className="space-y-3">
                {MOCK_APPLICATIONS.map((app) => (
                  <div
                    key={app.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{app.title}</p>
                      <p className="text-xs text-muted-foreground">{app.company}</p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-xs text-muted-foreground hidden sm:block">
                        {formatDate(app.appliedAt)}
                      </span>
                      <Badge variant="status" status={app.status} size="sm">
                        {statusLabels[app.status] ?? app.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recommended Internships */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5 text-saffron-500" />
              Recommended Internships
            </CardTitle>
            <CardDescription>Top matches based on your profile</CardDescription>
          </div>
          <Link href="/applicant/internships">
            <Button variant="ghost" size="sm">
              View All <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {recsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : !recommendations || recommendations.length === 0 ? (
            <EmptyState
              icon="search"
              title="No recommendations yet"
              description="Complete your profile to get personalized internship matches"
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {recommendations.slice(0, 3).map((rec) => (
                <Link key={rec.opportunityId} href={`/applicant/internships/${rec.opportunityId}`}>
                  <div className="border rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer h-full flex flex-col">
                    <div className="flex items-start justify-between mb-2">
                      <Badge variant="default" size="sm">{rec.sector}</Badge>
                      <div className="flex items-center gap-1 text-saffron-600 font-bold text-sm">
                        <Star className="h-4 w-4 fill-current" />
                        {rec.matchScore}%
                      </div>
                    </div>
                    <h3 className="font-semibold text-sm mb-1 line-clamp-2">{rec.title}</h3>
                    <p className="text-xs text-muted-foreground mb-2">{rec.employerName}</p>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground mb-3">
                      <MapPin className="h-3 w-3" />
                      {rec.location}
                    </div>
                    <div className="mt-auto flex items-center justify-between">
                      <span className="text-sm font-semibold text-navy-600">
                        {formatCurrency(rec.stipend)}/mo
                      </span>
                      <span className="text-xs text-muted-foreground">View Details →</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link href="/applicant/internships">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="rounded-lg bg-saffron-50 p-3">
                <Briefcase className="h-6 w-6 text-saffron-600" />
              </div>
              <div>
                <p className="font-semibold text-sm">Browse Internships</p>
                <p className="text-xs text-muted-foreground">Find your perfect match</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link href="/applicant/profile">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="rounded-lg bg-navy-50 p-3">
                <FileText className="h-6 w-6 text-navy-600" />
              </div>
              <div>
                <p className="font-semibold text-sm">Update Profile</p>
                <p className="text-xs text-muted-foreground">Keep your info current</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link href="/applicant/applications">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="rounded-lg bg-green-50 p-3">
                <CheckCircle className="h-6 w-6 text-gov-success" />
              </div>
              <div>
                <p className="font-semibold text-sm">Track Applications</p>
                <p className="text-xs text-muted-foreground">Check status updates</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
