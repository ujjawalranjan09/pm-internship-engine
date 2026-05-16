"use client";

import { use } from "react";
import Link from "next/link";
import { useOpportunityDetail, useUpdateOpportunity } from "@/hooks/use-opportunities";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { SkeletonCard } from "@/components/shared/skeleton";
import { StatsCard } from "@/components/shared/stats-card";
import { PageHeader } from "@/components/shared/page-header";
import { useToast } from "@/components/ui/toast";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import {
  MapPin,
  Clock,
  Users,
  Edit3,
  Save,
  X,
  ArrowLeft,
  UserCheck,
  FileText,
  BarChart3,
  Briefcase,
} from "lucide-react";
import { useState } from "react";

const MOCK_SHORTLISTED = [
  { id: "c1", name: "Priya Sharma", education: "B.Tech CS", matchScore: 87, status: "shortlisted" },
  { id: "c5", name: "Meera Patel", education: "BCA", matchScore: 91, status: "shortlisted" },
  { id: "c6", name: "Arjun Reddy", education: "M.Tech AI", matchScore: 84, status: "allocated" },
];

export default function EmployerInternshipDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: opportunity, isLoading, error } = useOpportunityDetail(id);
  const updateOpp = useUpdateOpportunity();
  const { addToast } = useToast();
  const [editing, setEditing] = useState(false);
  const [editValues, setEditValues] = useState<Record<string, string>>({});

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !opportunity) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Internship not found.</p>
        <Link href="/employer/internships">
          <Button variant="outline" className="mt-4">Back to Internships</Button>
        </Link>
      </div>
    );
  }

  const handleSave = () => {
    updateOpp.mutate(
      { id, data: editValues },
      {
        onSuccess: () => {
          setEditing(false);
          addToast({ type: "success", title: "Updated", message: "Internship details updated." });
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={opportunity.title}
        description={opportunity.employerName}
        breadcrumbs={[
          { label: "Dashboard", href: "/employer" },
          { label: "Internships", href: "/employer/internships" },
          { label: opportunity.title },
        ]}
        actions={
          <div className="flex gap-2">
            <Link href="/employer/internships">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-1" /> Back
              </Button>
            </Link>
            {editing ? (
              <>
                <Button variant="ghost" size="sm" onClick={() => setEditing(false)}>
                  <X className="h-4 w-4 mr-1" /> Cancel
                </Button>
                <Button size="sm" onClick={handleSave} loading={updateOpp.isPending}>
                  <Save className="h-4 w-4 mr-1" /> Save
                </Button>
              </>
            ) : (
              <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                <Edit3 className="h-4 w-4 mr-1" /> Edit
              </Button>
            )}
          </div>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatsCard
          title="Applications Received"
          value={245}
          icon={<FileText className="h-5 w-5" />}
        />
        <StatsCard
          title="Shortlisted"
          value={95}
          icon={<UserCheck className="h-5 w-5" />}
        />
        <StatsCard
          title="Capacity Filled"
          value={`${opportunity.filledSlots}/${opportunity.capacity}`}
          icon={<Users className="h-5 w-5" />}
          description={`${Math.round((opportunity.filledSlots / opportunity.capacity) * 100)}% filled`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Details */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Internship Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Sector</p>
                <p className="font-medium">{opportunity.sector}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Location</p>
                <p className="font-medium">{opportunity.location}, {opportunity.district}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Stipend</p>
                <p className="font-medium">{formatCurrency(opportunity.stipend)}/month</p>
              </div>
              <div>
                <p className="text-muted-foreground">Duration</p>
                <p className="font-medium">{opportunity.duration} months</p>
              </div>
              <div>
                <p className="text-muted-foreground">Start Date</p>
                <p className="font-medium">{formatDate(opportunity.startDate)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">End Date</p>
                <p className="font-medium">{formatDate(opportunity.endDate)}</p>
              </div>
            </div>

            <Separator />

            <div>
              <p className="text-sm text-muted-foreground mb-1">Description</p>
              <p className="text-sm leading-relaxed">{opportunity.description}</p>
            </div>

            <Separator />

            <div>
              <p className="text-sm text-muted-foreground mb-2">Required Skills</p>
              <div className="flex flex-wrap gap-2">
                {opportunity.requiredSkills.map((skill) => (
                  <Badge key={skill} variant="outline">{skill}</Badge>
                ))}
              </div>
            </div>

            <Separator />

            <div>
              <p className="text-sm text-muted-foreground mb-2">Eligibility</p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span>Min Education: {opportunity.eligibilityCriteria.minEducation}</span>
                {opportunity.eligibilityCriteria.minPercentage && (
                  <span>Min Percentage: {opportunity.eligibilityCriteria.minPercentage}%</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Shortlisted Candidates */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Shortlisted Candidates</CardTitle>
            <CardDescription>Top matched candidates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {MOCK_SHORTLISTED.map((candidate) => (
                <div key={candidate.id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{candidate.name}</p>
                    <p className="text-xs text-muted-foreground">{candidate.education}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-sm font-bold text-saffron-600">{candidate.matchScore}%</span>
                    <Badge variant="status" status={candidate.status} size="sm">
                      {candidate.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
            <Link href={`/employer/internships/${id}/candidates`}>
              <Button variant="outline" className="w-full mt-4">
                View All Candidates
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
