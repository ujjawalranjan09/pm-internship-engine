"use client";

import { use } from "react";
import Link from "next/link";
import { useOpportunityDetail } from "@/hooks/use-opportunities";
import { useRecommendations } from "@/hooks/use-matches";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { useToast } from "@/components/ui/toast";
import { formatCurrency, formatDate } from "@/lib/utils";
import {
  MapPin,
  Clock,
  Users,
  Star,
  Briefcase,
  GraduationCap,
  Calendar,
  IndianRupee,
  ArrowLeft,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

const MATCH_FACTORS = [
  { name: "Skill Match", score: 92, weight: 35, description: "3 of 4 required skills matched with your profile" },
  { name: "Education Fit", score: 85, weight: 25, description: "Your B.Tech in CS meets the minimum education requirement" },
  { name: "Location Preference", score: 70, weight: 20, description: "Preferred city, different state from current residence" },
  { name: "Sector Alignment", score: 90, weight: 20, description: "IT sector matches your primary interest" },
];

export default function InternshipDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: opportunity, isLoading, error } = useOpportunityDetail(id);
  const { data: recommendations } = useRecommendations();
  const { addToast } = useToast();
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);

  const similarInternships = (recommendations ?? [])
    .filter((r) => r.opportunityId !== id)
    .slice(0, 3);

  const handleApply = () => {
    setApplying(true);
    setTimeout(() => {
      setApplying(false);
      setApplied(true);
      addToast({ type: "success", title: "Application submitted!", message: "You'll be notified about the status." });
    }, 1500);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2"><SkeletonCard /></div>
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (error || !opportunity) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Internship not found.</p>
        <Link href="/applicant/internships">
          <Button variant="outline" className="mt-4">Back to Internships</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={opportunity.title}
        description={opportunity.employerName}
        breadcrumbs={[
          { label: "Dashboard", href: "/applicant" },
          { label: "Internships", href: "/applicant/internships" },
          { label: opportunity.title },
        ]}
        actions={
          <Link href="/applicant/internships">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
          </Link>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overview */}
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-wrap gap-2 mb-4">
                <Badge variant="default">{opportunity.sector}</Badge>
                {opportunity.isActive ? (
                  <Badge variant="status" status="completed">Active</Badge>
                ) : (
                  <Badge variant="status" status="cancelled">Closed</Badge>
                )}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Location</p>
                    <p className="text-sm font-medium">{opportunity.location}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <IndianRupee className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Stipend</p>
                    <p className="text-sm font-medium">{formatCurrency(opportunity.stipend)}/mo</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="text-sm font-medium">{opportunity.duration} months</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Positions</p>
                    <p className="text-sm font-medium">{opportunity.filledSlots}/{opportunity.capacity}</p>
                  </div>
                </div>
              </div>

              <Separator className="my-4" />

              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                {opportunity.description}
              </p>

              <Separator className="my-4" />

              <h3 className="font-semibold mb-3">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {opportunity.requiredSkills.map((skill) => (
                  <Badge key={skill} variant="outline">{skill}</Badge>
                ))}
              </div>

              <Separator className="my-4" />

              <h3 className="font-semibold mb-3">Eligibility</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <GraduationCap className="h-4 w-4 text-muted-foreground" />
                  <span>Min Education: {opportunity.eligibilityCriteria.minEducation}</span>
                </div>
                {opportunity.eligibilityCriteria.minPercentage && (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                    <span>Min Percentage: {opportunity.eligibilityCriteria.minPercentage}%</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>Start: {formatDate(opportunity.startDate)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>End: {formatDate(opportunity.endDate)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Match Score Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-saffron-500" />
                Why This Match
              </CardTitle>
              <CardDescription>
                Your compatibility breakdown for this internship
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {MATCH_FACTORS.map((factor) => (
                <div key={factor.name} className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{factor.name}</span>
                    <span className="text-sm font-bold text-navy-600">{factor.score}%</span>
                  </div>
                  <Progress value={factor.score} size="sm" />
                  <p className="text-xs text-muted-foreground">{factor.description}</p>
                </div>
              ))}
              <Separator />
              <div className="flex items-center justify-between p-3 rounded-lg bg-navy-50">
                <span className="font-semibold">Overall Match Score</span>
                <span className="text-2xl font-bold text-navy-600">
                  {Math.round(MATCH_FACTORS.reduce((sum, f) => sum + (f.score * f.weight) / 100, 0))}%
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Apply Card */}
          <Card className="sticky top-20">
            <CardContent className="p-6 space-y-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-navy-600">
                  {formatCurrency(opportunity.stipend)}
                </p>
                <p className="text-sm text-muted-foreground">per month</p>
              </div>
              <Separator />
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Duration</span>
                  <span className="font-medium">{opportunity.duration} months</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Location</span>
                  <span className="font-medium">{opportunity.location}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Positions</span>
                  <span className="font-medium">{opportunity.capacity - opportunity.filledSlots} remaining</span>
                </div>
              </div>
              {applied ? (
                <Button className="w-full" variant="secondary" disabled>
                  <CheckCircle2 className="h-4 w-4 mr-2" /> Applied Successfully
                </Button>
              ) : (
                <Button
                  className="w-full"
                  onClick={handleApply}
                  loading={applying}
                  disabled={!opportunity.isActive}
                >
                  {opportunity.isActive ? "Apply Now" : "Applications Closed"}
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Similar Internships */}
          {similarInternships.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Similar Internships</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {similarInternships.map((rec) => (
                  <Link key={rec.opportunityId} href={`/applicant/internships/${rec.opportunityId}`}>
                    <div className="p-3 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer">
                      <div className="flex items-start justify-between mb-1">
                        <p className="text-sm font-medium line-clamp-1">{rec.title}</p>
                        <span className="text-xs font-bold text-saffron-600 shrink-0 ml-2">{rec.matchScore}%</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{rec.employerName}</p>
                      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <MapPin className="h-3 w-3" /> {rec.location}
                        <span className="ml-auto">{formatCurrency(rec.stipend)}/mo</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
