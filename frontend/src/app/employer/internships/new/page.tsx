"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCreateOpportunity } from "@/hooks/use-opportunities";
import { opportunitySchema, type OpportunityFormData } from "@/lib/validators";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs } from "@/components/ui/tabs";
import { PageHeader } from "@/components/shared/page-header";
import { useToast } from "@/components/ui/toast";
import { formatCurrency } from "@/lib/utils";
import { SECTORS, EDUCATION_LEVELS, CATEGORIES, STATES, STATES_AND_DISTRICTS, SKILL_CATEGORIES } from "@/lib/constants";
import {
  Briefcase,
  Plus,
  X,
  Eye,
  Send,
  MapPin,
  IndianRupee,
  Clock,
  Users,
  GraduationCap,
} from "lucide-react";

export default function NewInternshipPage() {
  const router = useRouter();
  const createOpp = useCreateOpportunity();
  const { addToast } = useToast();
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [skillSearch, setSkillSearch] = useState("");
  const [criteria, setCriteria] = useState<{ key: string; value: string }[]>([]);
  const [showPreview, setShowPreview] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<OpportunityFormData>({
    resolver: zodResolver(opportunitySchema),
    defaultValues: {
      title: "",
      description: "",
      sector: "",
      location: "",
      state: "",
      district: "",
      stipend: 0,
      duration: 6,
      capacity: 1,
      requiredSkills: [],
      eligibilityCriteria: { minEducation: "" },
      startDate: "",
      endDate: "",
    },
  });

  const formValues = watch();
  const selectedState = watch("state");
  const districts = selectedState ? STATES_AND_DISTRICTS[selectedState] ?? [] : [];

  const filteredSkills = SKILL_CATEGORIES.filter(
    (s) => s.toLowerCase().includes(skillSearch.toLowerCase()) && !selectedSkills.includes(s)
  );

  const onSubmit = (data: OpportunityFormData) => {
    createOpp.mutate(
      { ...data, requiredSkills: selectedSkills },
      {
        onSuccess: () => {
          addToast({ type: "success", title: "Internship created!", message: "Your opportunity has been posted." });
          router.push("/employer/internships");
        },
        onError: () => {
          addToast({ type: "error", title: "Creation failed", message: "Please try again." });
        },
      }
    );
  };

  const addCriteria = () => {
    setCriteria((prev) => [...prev, { key: "", value: "" }]);
  };

  const updateCriteria = (idx: number, field: "key" | "value", val: string) => {
    setCriteria((prev) => prev.map((c, i) => (i === idx ? { ...c, [field]: val } : c)));
  };

  const removeCriteria = (idx: number) => {
    setCriteria((prev) => prev.filter((_, i) => i !== idx));
  };

  const formTab = {
    id: "form",
    label: "Form",
    icon: <Briefcase className="h-4 w-4" />,
    content: (
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Internship Title"
                {...register("title")}
                error={errors.title?.message}
                placeholder="e.g., Software Development Intern"
                className="md:col-span-2"
              />
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1.5">
                  Description <span className="text-gov-error">*</span>
                </label>
                <textarea
                  {...register("description")}
                  rows={5}
                  className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy-500"
                  placeholder="Describe the internship role, responsibilities, and learning outcomes..."
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-gov-error">{errors.description.message}</p>
                )}
              </div>
              <Select
                label="Sector"
                {...register("sector")}
                error={errors.sector?.message}
                options={SECTORS.map((s) => ({ label: s, value: s }))}
                placeholder="Select sector"
              />
              <Input
                label="Location / City"
                {...register("location")}
                error={errors.location?.message}
                placeholder="e.g., Bangalore"
              />
              <Select
                label="State"
                {...register("state")}
                error={errors.state?.message}
                options={STATES.map((s) => ({ label: s, value: s }))}
                placeholder="Select state"
              />
              <Select
                label="District"
                {...register("district")}
                error={errors.district?.message}
                options={districts.map((d) => ({ label: d, value: d }))}
                placeholder={districts.length ? "Select district" : "Select state first"}
                disabled={!selectedState}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                label="Monthly Stipend (₹)"
                type="number"
                {...register("stipend", { valueAsNumber: true })}
                error={errors.stipend?.message}
                placeholder="e.g., 15000"
              />
              <Input
                label="Duration (months)"
                type="number"
                {...register("duration", { valueAsNumber: true })}
                error={errors.duration?.message}
                placeholder="e.g., 6"
              />
              <Input
                label="Capacity"
                type="number"
                {...register("capacity", { valueAsNumber: true })}
                error={errors.capacity?.message}
                placeholder="e.g., 50"
              />
              <Select
                label="Work Mode"
                {...register("workMode")}
                error={errors.workMode?.message}
                options={[
                  { label: "On-site", value: "onsite" },
                  { label: "Remote", value: "remote" },
                  { label: "Hybrid", value: "hybrid" },
                ]}
                placeholder="Select mode"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Start Date"
                type="date"
                {...register("startDate")}
                error={errors.startDate?.message}
              />
              <Input
                label="End Date"
                type="date"
                {...register("endDate")}
                error={errors.endDate?.message}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Required Skills</CardTitle>
            <CardDescription>Select skills required for this internship</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Input
                value={skillSearch}
                onChange={(e) => setSkillSearch(e.target.value)}
                placeholder="Search skills..."
              />
              {skillSearch && filteredSkills.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  {filteredSkills.map((skill) => (
                    <button
                      key={skill}
                      type="button"
                      className="w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors"
                      onClick={() => {
                        setSelectedSkills((prev) => [...prev, skill]);
                        setSkillSearch("");
                      }}
                    >
                      {skill}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {selectedSkills.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {selectedSkills.map((skill) => (
                  <Badge key={skill} variant="default" className="flex items-center gap-1 pr-1">
                    {skill}
                    <button
                      type="button"
                      onClick={() => setSelectedSkills((prev) => prev.filter((s) => s !== skill))}
                      className="ml-1 rounded-full hover:bg-navy-200 p-0.5"
                      aria-label={`Remove ${skill}`}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Eligibility Criteria</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Select
                label="Minimum Education"
                {...register("eligibilityCriteria.minEducation")}
                error={errors.eligibilityCriteria?.minEducation?.message}
                options={EDUCATION_LEVELS.map((e) => ({ label: e, value: e }))}
                placeholder="Select minimum education"
              />
              <Input
                label="Minimum Percentage"
                type="number"
                {...register("eligibilityCriteria.minPercentage", {
                  // valueAsNumber converts "" to NaN, which fails z.number().optional().
                  // Use setValueAs to convert empty string to undefined so .optional() passes.
                  setValueAs: (v) => (v === "" || v === null || v === undefined ? undefined : Number(v)),
                })}
                error={errors.eligibilityCriteria?.minPercentage?.message}
                placeholder="e.g., 60"
              />
            </div>

            <Separator />

            <div>
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium">Additional Criteria</p>
                <Button type="button" variant="outline" size="sm" onClick={addCriteria}>
                  <Plus className="h-4 w-4 mr-1" /> Add
                </Button>
              </div>
              {criteria.map((c, idx) => (
                <div key={idx} className="flex items-center gap-2 mb-2">
                  <Input
                    value={c.key}
                    onChange={(e) => updateCriteria(idx, "key", e.target.value)}
                    placeholder="Field name"
                    className="flex-1"
                  />
                  <Input
                    value={c.value}
                    onChange={(e) => updateCriteria(idx, "value", e.target.value)}
                    placeholder="Value"
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeCriteria(idx)}
                    aria-label="Remove criterion"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => setShowPreview(true)}>
            <Eye className="h-4 w-4 mr-1" /> Preview
          </Button>
          <Button type="submit" loading={createOpp.isPending}>
            <Send className="h-4 w-4 mr-1" /> Publish Internship
          </Button>
        </div>
      </form>
    ),
  };

  const previewTab = {
    id: "preview",
    label: "Preview",
    icon: <Eye className="h-4 w-4" />,
    content: (
      <Card>
        <CardContent className="p-6 space-y-6">
          <div>
            <Badge variant="default">{formValues.sector || "Sector"}</Badge>
            <h2 className="text-xl font-bold mt-2">{formValues.title || "Internship Title"}</h2>
            <p className="text-muted-foreground mt-1">{formValues.description || "Description will appear here..."}</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Location</p>
                <p className="text-sm font-medium">{formValues.location || "—"}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <IndianRupee className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Stipend</p>
                <p className="text-sm font-medium">{formValues.stipend ? formatCurrency(formValues.stipend) : "—"}/mo</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Duration</p>
                <p className="text-sm font-medium">{formValues.duration || "—"} months</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Capacity</p>
                <p className="text-sm font-medium">{formValues.capacity || "—"}</p>
              </div>
            </div>
          </div>
          {selectedSkills.length > 0 && (
            <div>
              <p className="text-sm font-medium mb-2">Required Skills</p>
              <div className="flex flex-wrap gap-2">
                {selectedSkills.map((s) => (
                  <Badge key={s} variant="outline">{s}</Badge>
                ))}
              </div>
            </div>
          )}
          <div className="flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">Min Education: {formValues.eligibilityCriteria?.minEducation || "—"}</span>
          </div>
        </CardContent>
      </Card>
    ),
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title="Create New Internship"
        description="Post a new internship opportunity for candidates"
        breadcrumbs={[
          { label: "Dashboard", href: "/employer" },
          { label: "Internships", href: "/employer/internships" },
          { label: "Create New" },
        ]}
      />
      <Tabs tabs={[formTab, previewTab]} defaultTab="form" />
    </div>
  );
}
