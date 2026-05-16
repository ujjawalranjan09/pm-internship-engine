"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as adminService from "@/services/admin-service";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";
import {
  Settings,
  Save,
  RotateCcw,
  Sliders,
  Target,
  Scale,
  AlertTriangle,
} from "lucide-react";

const DEFAULT_WEIGHTS = {
  skillMatch: 0.35,
  locationPreference: 0.20,
  educationMatch: 0.25,
  candidatePreference: 0.10,
  fairnessAdjustment: 0.10,
};

const WEIGHT_LABELS: Record<string, string> = {
  skillMatch: "Skill Match",
  locationPreference: "Location Preference",
  educationMatch: "Education Match",
  candidatePreference: "Candidate Preference",
  fairnessAdjustment: "Fairness Adjustment",
};

export default function PolicyPage() {
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  const { data: policy, isLoading } = useQuery({
    queryKey: ["admin", "policy"],
    queryFn: adminService.getPolicy,
  });

  const updatePolicy = useMutation({
    mutationFn: (data: Parameters<typeof adminService.updatePolicy>[0]) => adminService.updatePolicy(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "policy"] });
      addToast({ type: "success", title: "Policy saved", message: "Configuration updated successfully." });
    },
  });

  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [thresholds, setThresholds] = useState({ minimumMatchScore: 40, minimumProfileCompletion: 60 });
  const [genderTargets, setGenderTargets] = useState<Record<string, number>>({ Male: 50, Female: 48, Other: 2 });
  const [categoryTargets, setCategoryTargets] = useState<Record<string, number>>({
    General: 40, OBC: 27, SC: 16, ST: 10, EWS: 7,
  });
  const [ruralUrban, setRuralUrban] = useState({ rural: 45, urban: 55 });

  useEffect(() => {
    if (policy) {
      setWeights(policy.weights);
      setThresholds(policy.thresholds);
      setGenderTargets(policy.representationTargets.gender);
      setCategoryTargets(policy.representationTargets.category);
      setRuralUrban(policy.representationTargets.ruralUrban);
    }
  }, [policy]);

  const weightsSum = Object.values(weights).reduce((a, b) => a + b, 0);
  const isValid = Math.abs(weightsSum - 1.0) < 0.01;

  const handleWeightChange = (key: string, value: number) => {
    setWeights((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    if (!isValid) {
      addToast({ type: "error", title: "Invalid weights", message: "Weights must sum to 1.0" });
      return;
    }
    updatePolicy.mutate({
      weights,
      thresholds,
      representationTargets: { gender: genderTargets, category: categoryTargets, ruralUrban },
    });
  };

  const handleReset = () => {
    setWeights(DEFAULT_WEIGHTS);
    setThresholds({ minimumMatchScore: 40, minimumProfileCompletion: 60 });
    setGenderTargets({ Male: 50, Female: 48, Other: 2 });
    setCategoryTargets({ General: 40, OBC: 27, SC: 16, ST: 10, EWS: 7 });
    setRuralUrban({ rural: 45, urban: 55 });
    addToast({ type: "info", title: "Reset to defaults", message: "All values restored to defaults." });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Policy Configuration" />
        <SkeletonCard /><SkeletonCard />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title="Policy Configuration"
        description="Configure matching weights, fairness thresholds, and representation targets"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-1" /> Reset Defaults
            </Button>
            <Button onClick={handleSave} loading={updatePolicy.isPending}>
              <Save className="h-4 w-4 mr-1" /> Save Configuration
            </Button>
          </div>
        }
      />

      {/* Match Score Weights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sliders className="h-5 w-5 text-saffron-500" />
            Match Score Weights
          </CardTitle>
          <CardDescription>
            Adjust the relative importance of each matching factor. Weights must sum to 1.0.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(weights).map(([key, val]) => (
            <div key={key} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">{WEIGHT_LABELS[key] ?? key}</label>
                <span className="text-sm font-bold text-navy-600 w-12 text-right">{(val * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={val * 100}
                  onChange={(e) => handleWeightChange(key, Number(e.target.value) / 100)}
                  className="flex-1 h-2 rounded-full appearance-none bg-muted accent-navy-500 cursor-pointer"
                  aria-label={`${WEIGHT_LABELS[key] ?? key} weight`}
                />
                <input
                  type="number"
                  min={0}
                  max={100}
                  step={1}
                  value={Math.round(val * 100)}
                  onChange={(e) => handleWeightChange(key, Number(e.target.value) / 100)}
                  className="w-16 h-8 rounded border text-center text-sm"
                  aria-label={`${WEIGHT_LABELS[key] ?? key} percentage`}
                />
              </div>
            </div>
          ))}
          <Separator />
          <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
            <span className="text-sm font-medium">Total</span>
            <span className={cn(
              "text-sm font-bold",
              isValid ? "text-gov-success" : "text-gov-error"
            )}>
              {(weightsSum * 100).toFixed(0)}% {isValid ? "✓" : "(must be 100%)"}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Thresholds */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-saffron-500" />
            Thresholds
          </CardTitle>
          <CardDescription>Minimum scores required for eligibility</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Minimum Match Score</label>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={thresholds.minimumMatchScore}
                  onChange={(e) => setThresholds((p) => ({ ...p, minimumMatchScore: Number(e.target.value) }))}
                  className="flex-1 h-2 rounded-full appearance-none bg-muted accent-navy-500"
                />
                <span className="text-sm font-bold w-10 text-right">{thresholds.minimumMatchScore}%</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Minimum Profile Completion</label>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={thresholds.minimumProfileCompletion}
                  onChange={(e) => setThresholds((p) => ({ ...p, minimumProfileCompletion: Number(e.target.value) }))}
                  className="flex-1 h-2 rounded-full appearance-none bg-muted accent-navy-500"
                />
                <span className="text-sm font-bold w-10 text-right">{thresholds.minimumProfileCompletion}%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Representation Targets */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-saffron-500" />
            Representation Targets
          </CardTitle>
          <CardDescription>Target distribution percentages by category and gender</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <p className="text-sm font-medium mb-3">Gender Targets</p>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(genderTargets).map(([gender, val]) => (
                <div key={gender} className="text-center">
                  <label className="text-xs text-muted-foreground block mb-1">{gender}</label>
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={val}
                    onChange={(e) => setGenderTargets((p) => ({ ...p, [gender]: Number(e.target.value) }))}
                    className="text-center"
                  />
                </div>
              ))}
            </div>
          </div>

          <Separator />

          <div>
            <p className="text-sm font-medium mb-3">Category Targets</p>
            <div className="grid grid-cols-5 gap-3">
              {Object.entries(categoryTargets).map(([cat, val]) => (
                <div key={cat} className="text-center">
                  <label className="text-xs text-muted-foreground block mb-1">{cat}</label>
                  <Input
                    type="number"
                    min={0}
                    max={100}
                    value={val}
                    onChange={(e) => setCategoryTargets((p) => ({ ...p, [cat]: Number(e.target.value) }))}
                    className="text-center"
                  />
                </div>
              ))}
            </div>
          </div>

          <Separator />

          <div>
            <p className="text-sm font-medium mb-3">Rural / Urban Targets</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Rural %</label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={ruralUrban.rural}
                  onChange={(e) => setRuralUrban((p) => ({ ...p, rural: Number(e.target.value) }))}
                  className="text-center"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Urban %</label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={ruralUrban.urban}
                  onChange={(e) => setRuralUrban((p) => ({ ...p, urban: Number(e.target.value) }))}
                  className="text-center"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
