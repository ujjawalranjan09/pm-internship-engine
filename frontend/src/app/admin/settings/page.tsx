"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import * as adminService from "@/services/admin-service";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/shared/page-header";
import { Settings, Save, Shield, Scale, Sliders, Target } from "lucide-react";

const DEFAULT_WEIGHTS = {
  skillMatch: 30,
  locationPreference: 20,
  educationMatch: 15,
  candidatePreference: 15,
  fairnessAdjustment: 10,
  profileCompleteness: 10,
};

const DEFAULT_FAIRNESS = {
  socialCategoryBoost: 15,
  ruralBoost: 10,
  genderParityTarget: 40,
  underservedStateBoost: 5,
};

export default function AdminSettingsPage() {
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [fairness, setFairness] = useState(DEFAULT_FAIRNESS);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Would call API to save
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const totalWeight = Object.values(weights).reduce((s, v) => s + v, 0);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Policy Settings"
        description="Configure matching weights, fairness policies, and system behavior"
      />

      {/* Matching Weights */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Sliders className="h-5 w-5 text-navy-600" />
            Matching Weights
          </CardTitle>
          <CardDescription>
            Configure the relative importance of each scoring component (total should be 100%)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(weights).map(([key, value]) => {
            const label = key.replace(/([A-Z])/g, " $1").replace(/^./, (s) => s.toUpperCase());
            return (
              <div key={key} className="flex items-center gap-4">
                <label className="text-sm font-medium w-48 shrink-0">{label}</label>
                <div className="flex-1 flex items-center gap-3">
                  <input
                    type="range"
                    min={0}
                    max={50}
                    value={value}
                    onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    min={0}
                    max={50}
                    value={value}
                    onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
                    className="w-20 text-center"
                  />
                  <span className="text-sm text-muted-foreground">%</span>
                </div>
              </div>
            );
          })}
          <div className="flex items-center justify-between pt-3 border-t">
            <span className="text-sm font-medium">Total</span>
            <Badge
              variant={totalWeight === 100 ? "default" : "destructive"}
              size="sm"
            >
              {totalWeight}%
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Fairness Policies */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Scale className="h-5 w-5 text-navy-600" />
            Fairness Policies
          </CardTitle>
          <CardDescription>
            Configure fairness-aware re-ranking boosts for underrepresented groups
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(fairness).map(([key, value]) => {
            const label = key.replace(/([A-Z])/g, " $1").replace(/^./, (s) => s.toUpperCase());
            return (
              <div key={key} className="flex items-center gap-4">
                <label className="text-sm font-medium w-48 shrink-0">{label}</label>
                <div className="flex-1 flex items-center gap-3">
                  <input
                    type="range"
                    min={0}
                    max={30}
                    value={value}
                    onChange={(e) => setFairness({ ...fairness, [key]: Number(e.target.value) })}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    min={0}
                    max={30}
                    value={value}
                    onChange={(e) => setFairness({ ...fairness, [key]: Number(e.target.value) })}
                    className="w-20 text-center"
                  />
                  <span className="text-sm text-muted-foreground">%</span>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Thresholds */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Target className="h-5 w-5 text-navy-600" />
            Thresholds
          </CardTitle>
          <CardDescription>Minimum score and profile completion thresholds</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium w-48 shrink-0">Minimum Match Score</label>
            <Input type="number" min={0} max={100} defaultValue={10} className="w-24" />
            <span className="text-sm text-muted-foreground">%</span>
          </div>
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium w-48 shrink-0">Min Profile Completion</label>
            <Input type="number" min={0} max={100} defaultValue={30} className="w-24" />
            <span className="text-sm text-muted-foreground">%</span>
          </div>
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium w-48 shrink-0">Top-K Recommendations</label>
            <Input type="number" min={1} max={200} defaultValue={50} className="w-24" />
            <span className="text-sm text-muted-foreground">candidates</span>
          </div>
        </CardContent>
      </Card>

      {/* Save */}
      <div className="flex items-center justify-end gap-3">
        {saved && (
          <Badge variant="default" size="sm" className="bg-green-100 text-green-700">
            ✓ Saved successfully
          </Badge>
        )}
        <Button onClick={handleSave}>
          <Save className="h-4 w-4 mr-1.5" />
          Save Configuration
        </Button>
      </div>
    </div>
  );
}
