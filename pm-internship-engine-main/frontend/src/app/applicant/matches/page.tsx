"use client";

import Link from "next/link";
import { useRecommendations } from "@/hooks/use-matches";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { SkeletonCard } from "@/components/shared/skeleton";
import { formatCurrency, cn } from "@/lib/utils";
import {
  Star,
  MapPin,
  Briefcase,
  Clock,
  ArrowRight,
  Sparkles,
  TrendingUp,
} from "lucide-react";

const scoreColor = (score: number) => {
  if (score >= 85) return "text-green-600 bg-green-50 border-green-200";
  if (score >= 70) return "text-blue-600 bg-blue-50 border-blue-200";
  if (score >= 50) return "text-amber-600 bg-amber-50 border-amber-200";
  return "text-gray-600 bg-gray-50 border-gray-200";
};

const scoreLabel = (score: number) => {
  if (score >= 85) return "Excellent Match";
  if (score >= 70) return "Good Match";
  if (score >= 50) return "Fair Match";
  return "Low Match";
};

export default function MatchesPage() {
  const { data: recommendations, isLoading } = useRecommendations();

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Match Recommendations"
        description="Personalized internship matches powered by our multi-stage matching engine"
      />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : !recommendations || recommendations.length === 0 ? (
        <EmptyState
          icon="search"
          title="No matches found yet"
          description="Complete your profile to receive AI-powered internship recommendations. The more details you provide, the better your matches."
          action={{ label: "Complete Profile", href: "/applicant/profile" }}
        />
      ) : (
        <>
          {/* Match Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-saffron-50 p-2.5">
                  <Sparkles className="h-5 w-5 text-saffron-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-navy-600">{recommendations.length}</p>
                  <p className="text-xs text-muted-foreground">Total Matches</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-green-50 p-2.5">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-navy-600">
                    {recommendations.filter((r) => r.matchScore >= 70).length}
                  </p>
                  <p className="text-xs text-muted-foreground">High-Quality Matches</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <div className="rounded-lg bg-navy-50 p-2.5">
                  <Star className="h-5 w-5 text-navy-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-navy-600">
                    {recommendations.length > 0
                      ? Math.round(
                          recommendations.reduce((s, r) => s + r.matchScore, 0) /
                            recommendations.length
                        )
                      : 0}
                    %
                  </p>
                  <p className="text-xs text-muted-foreground">Avg Match Score</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Match Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec) => (
              <Link key={rec.opportunityId} href={`/applicant/internships/${rec.opportunityId}`}>
                <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer h-full group">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" size="sm">{rec.sector}</Badge>
                        {rec.workMode && (
                          <Badge variant="outline" size="sm">{rec.workMode}</Badge>
                        )}
                      </div>
                      <div
                        className={cn(
                          "flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-sm font-bold",
                          scoreColor(rec.matchScore)
                        )}
                      >
                        <Star className="h-3.5 w-3.5 fill-current" />
                        {rec.matchScore}%
                      </div>
                    </div>

                    <h3 className="font-semibold text-base mb-1 group-hover:text-navy-600 transition-colors">
                      {rec.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3">{rec.employerName}</p>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground mb-4">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {rec.location}
                      </span>
                      {rec.duration && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3.5 w-3.5" />
                          {rec.duration}
                        </span>
                      )}
                      {rec.stipend > 0 && (
                        <span className="flex items-center gap-1">
                          <Briefcase className="h-3.5 w-3.5" />
                          {formatCurrency(rec.stipend)}/mo
                        </span>
                      )}
                    </div>

                    {/* Score Breakdown */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">{scoreLabel(rec.matchScore)}</span>
                        <span className="font-medium">{rec.matchScore}%</span>
                      </div>
                      <Progress value={rec.matchScore} size="sm" />
                    </div>

                    {rec.skills && rec.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {rec.skills.slice(0, 5).map((skill) => (
                          <Badge key={skill} variant="secondary" size="sm">
                            {skill}
                          </Badge>
                        ))}
                        {rec.skills.length > 5 && (
                          <Badge variant="secondary" size="sm">
                            +{rec.skills.length - 5}
                          </Badge>
                        )}
                      </div>
                    )}

                    <div className="mt-4 flex items-center justify-end">
                      <span className="text-xs text-navy-600 font-medium group-hover:underline flex items-center gap-1">
                        View Details <ArrowRight className="h-3 w-3" />
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
