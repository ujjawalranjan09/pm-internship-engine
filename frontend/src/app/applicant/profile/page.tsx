"use client";

import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCandidateProfile, useUpdateProfile, useUpdateSkills } from "@/hooks/use-candidates";
import { profileSchema, type ProfileFormData } from "@/lib/validators";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";
import { STATES_AND_DISTRICTS, STATES, SECTORS, SKILL_CATEGORIES, EDUCATION_LEVELS, CATEGORIES } from "@/lib/constants";
import {
  User,
  GraduationCap,
  Code2,
  Target,
  FileUp,
  Shield,
  ChevronLeft,
  ChevronRight,
  Save,
  Check,
  Plus,
  X,
  Upload,
} from "lucide-react";

const steps = [
  { id: 1, label: "Personal Info", icon: User },
  { id: 2, label: "Education", icon: GraduationCap },
  { id: 3, label: "Skills", icon: Code2 },
  { id: 4, label: "Preferences", icon: Target },
  { id: 5, label: "Resume", icon: FileUp },
  { id: 6, label: "Category", icon: Shield },
];

export default function ProfilePage() {
  const { data: profile, isLoading } = useCandidateProfile();
  const updateProfile = useUpdateProfile();
  const updateSkills = useUpdateSkills();
  const { addToast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedSkills, setSelectedSkills] = useState<string[]>(profile?.skills?.map((s) => s.name) ?? []);
  const [skillSearch, setSkillSearch] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [declaration, setDeclaration] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isDirty },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: profile?.name ?? "",
      phone: profile?.phone ?? "",
      state: profile?.state ?? "",
      district: profile?.district ?? "",
      sectors: profile?.sectors ?? [],
      preferredLocations: profile?.preferredLocations ?? [],
      gender: profile?.gender ?? "",
      category: profile?.category ?? "",
      pincode: profile?.pincode ?? "",
      address: profile?.address ?? "",
      dateOfBirth: profile?.dateOfBirth ?? "",
    },
  });

  const selectedState = watch("state");
  const districts = selectedState ? STATES_AND_DISTRICTS[selectedState] ?? [] : [];
  const selectedSectors = watch("sectors") ?? [];

  const filteredSkills = SKILL_CATEGORIES.filter(
    (s) => s.toLowerCase().includes(skillSearch.toLowerCase()) && !selectedSkills.includes(s)
  );

  const handleSaveDraft = () => {
    addToast({ type: "info", title: "Draft saved", message: "Your progress has been saved." });
  };

  const onSubmit = (data: ProfileFormData) => {
    if (!declaration) {
      addToast({ type: "warning", title: "Declaration required", message: "Please accept the declaration to proceed." });
      return;
    }
    updateProfile.mutate(
      { ...data, skills: selectedSkills.map((name) => ({ name, proficiency: "intermediate" as const })) },
      {
        onSuccess: () => {
          addToast({ type: "success", title: "Profile updated", message: "Your profile has been saved successfully." });
        },
        onError: () => {
          addToast({ type: "error", title: "Update failed", message: "Please try again later." });
        },
      }
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="My Profile" />
        <SkeletonCard />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title="My Profile"
        description="Complete your profile for better internship matches"
        breadcrumbs={[{ label: "Dashboard", href: "/applicant" }, { label: "Profile" }]}
      />

      {/* Progress */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Profile Completion</span>
            <span className="text-sm font-bold text-navy-600">{profile?.profileCompletion ?? 0}%</span>
          </div>
          <Progress value={profile?.profileCompletion ?? 0} size="md" />
        </CardContent>
      </Card>

      {/* Step Indicator */}
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isActive = currentStep === step.id;
          const isCompleted = currentStep > step.id;
          return (
            <div key={step.id} className="flex items-center">
              <button
                onClick={() => setCurrentStep(step.id)}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap",
                  isActive
                    ? "bg-navy-500 text-white shadow-sm"
                    : isCompleted
                      ? "bg-green-100 text-green-700"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                )}
                aria-current={isActive ? "step" : undefined}
              >
                {isCompleted ? <Check className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                <span className="hidden sm:inline">{step.label}</span>
              </button>
              {idx < steps.length - 1 && (
                <div className={cn("w-6 h-0.5 mx-1", isCompleted ? "bg-green-300" : "bg-muted")} />
              )}
            </div>
          );
        })}
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader>
            <CardTitle>{steps[currentStep - 1].label}</CardTitle>
            <CardDescription>
              Step {currentStep} of {steps.length}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Step 1: Personal Info */}
            {currentStep === 1 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  {...register("name")}
                  error={errors.name?.message}
                  placeholder="Enter your full name"
                />
                <Input
                  label="Phone Number"
                  {...register("phone")}
                  error={errors.phone?.message}
                  placeholder="10-digit mobile number"
                />
                <Input
                  label="Date of Birth"
                  type="date"
                  {...register("dateOfBirth")}
                  error={errors.dateOfBirth?.message}
                />
                <Select
                  label="Gender"
                  {...register("gender")}
                  options={[
                    { label: "Male", value: "Male" },
                    { label: "Female", value: "Female" },
                    { label: "Other", value: "Other" },
                    { label: "Prefer not to say", value: "undisclosed" },
                  ]}
                  placeholder="Select gender"
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
                <Input
                  label="Pincode"
                  {...register("pincode")}
                  error={errors.pincode?.message}
                  placeholder="6-digit pincode"
                />
                <Input
                  label="Address"
                  {...register("address")}
                  placeholder="Street address"
                />
              </div>
            )}

            {/* Step 2: Education */}
            {currentStep === 2 && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Select
                    label="Highest Education"
                    options={EDUCATION_LEVELS.map((e) => ({ label: e, value: e }))}
                    placeholder="Select education level"
                  />
                  <Input label="Institution / College" placeholder="Enter institution name" />
                  <Input label="Field of Study / Specialization" placeholder="e.g., Computer Science" />
                  <Input label="Year of Passing" type="number" placeholder="e.g., 2024" />
                  <Input label="Percentage / CGPA" placeholder="e.g., 75 or 8.5" />
                </div>
                {profile?.education && profile.education.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Added Education</p>
                    {profile.education.map((edu) => (
                      <div key={edu.id} className="flex items-center justify-between p-3 rounded-lg border">
                        <div>
                          <p className="text-sm font-medium">{edu.degree} - {edu.fieldOfStudy}</p>
                          <p className="text-xs text-muted-foreground">{edu.institution} ({edu.startYear} - {edu.endYear ?? "Present"})</p>
                        </div>
                        {edu.cgpa && <Badge variant="outline">{edu.cgpa} CGPA</Badge>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Skills */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5">Search & Add Skills</label>
                  <div className="relative">
                    <Input
                      value={skillSearch}
                      onChange={(e) => setSkillSearch(e.target.value)}
                      placeholder="Type to search skills..."
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
                </div>
                <div>
                  <p className="text-sm font-medium mb-2">Selected Skills</p>
                  {selectedSkills.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No skills selected yet. Search and add skills above.</p>
                  ) : (
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
                </div>
                <Separator />
                <div>
                  <p className="text-sm font-medium mb-2">Suggested Categories</p>
                  <div className="flex flex-wrap gap-2">
                    {SKILL_CATEGORIES.filter((c) => !selectedSkills.includes(c)).slice(0, 8).map((cat) => (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => setSelectedSkills((prev) => [...prev, cat])}
                        className="px-3 py-1.5 text-xs rounded-full border border-dashed text-muted-foreground hover:border-navy-400 hover:text-navy-600 transition-colors"
                      >
                        <Plus className="h-3 w-3 inline mr-1" />
                        {cat}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Preferences */}
            {currentStep === 4 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Sector Interests</label>
                  <p className="text-xs text-muted-foreground mb-2">Select sectors you&apos;re interested in</p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {SECTORS.map((sector) => {
                      const isSelected = selectedSectors.includes(sector);
                      return (
                        <button
                          key={sector}
                          type="button"
                          onClick={() => {
                            const current = selectedSectors;
                            setValue(
                              "sectors",
                              isSelected ? current.filter((s) => s !== sector) : [...current, sector],
                              { shouldDirty: true }
                            );
                          }}
                          className={cn(
                            "px-3 py-2 rounded-lg text-xs font-medium text-left transition-all border",
                            isSelected
                              ? "bg-navy-50 border-navy-300 text-navy-700"
                              : "border-gray-200 text-muted-foreground hover:border-gray-300"
                          )}
                        >
                          {sector}
                        </button>
                      );
                    })}
                  </div>
                  {errors.sectors && (
                    <p className="text-sm text-gov-error mt-1">{errors.sectors.message}</p>
                  )}
                </div>
                <Separator />
                <div>
                  <label className="block text-sm font-medium mb-2">Location Preferences</label>
                  <p className="text-xs text-muted-foreground mb-2">Preferred cities/locations for internship</p>
                  <div className="flex flex-wrap gap-2">
                    {["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"].map(
                      (city) => {
                        const locs = watch("preferredLocations") ?? [];
                        const isSelected = locs.includes(city);
                        return (
                          <button
                            key={city}
                            type="button"
                            onClick={() => {
                              setValue(
                                "preferredLocations",
                                isSelected ? locs.filter((l) => l !== city) : [...locs, city],
                                { shouldDirty: true }
                              );
                            }}
                            className={cn(
                              "px-3 py-1.5 rounded-full text-xs font-medium transition-all border",
                              isSelected
                                ? "bg-saffron-50 border-saffron-300 text-saffron-700"
                                : "border-gray-200 text-muted-foreground hover:border-gray-300"
                            )}
                          >
                            {city}
                          </button>
                        );
                      }
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 5: Resume Upload */}
            {currentStep === 5 && (
              <div className="space-y-4">
                <div
                  className="border-2 border-dashed rounded-xl p-8 text-center hover:border-navy-400 transition-colors cursor-pointer"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const file = e.dataTransfer.files[0];
                    if (file) setResumeFile(file);
                  }}
                  onClick={() => document.getElementById("resume-input")?.click()}
                  role="button"
                  tabIndex={0}
                  aria-label="Upload resume"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      document.getElementById("resume-input")?.click();
                    }
                  }}
                >
                  <input
                    id="resume-input"
                    type="file"
                    accept=".pdf,.doc,.docx"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) setResumeFile(file);
                    }}
                  />
                  <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
                  {resumeFile ? (
                    <div>
                      <p className="text-sm font-medium text-foreground">{resumeFile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(resumeFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm font-medium">Drag & drop your resume here</p>
                      <p className="text-xs text-muted-foreground mt-1">or click to browse (PDF, DOC, DOCX - max 5MB)</p>
                    </div>
                  )}
                </div>
                {profile?.resumeUrl && !resumeFile && (
                  <div className="flex items-center gap-2 p-3 rounded-lg bg-green-50 border border-green-200">
                    <Check className="h-4 w-4 text-gov-success" />
                    <span className="text-sm text-green-700">Resume previously uploaded</span>
                  </div>
                )}
              </div>
            )}

            {/* Step 6: Category & Declaration */}
            {currentStep === 6 && (
              <div className="space-y-4">
                <Select
                  label="Social Category"
                  {...register("category")}
                  options={CATEGORIES.map((c) => ({ label: c, value: c }))}
                  placeholder="Select category"
                />
                <Separator />
                <div className="space-y-3">
                  <p className="text-sm font-medium">Declaration</p>
                  <label className="flex items-start gap-3 p-4 rounded-lg border cursor-pointer hover:bg-muted/50 transition-colors">
                    <input
                      type="checkbox"
                      checked={declaration}
                      onChange={(e) => setDeclaration(e.target.checked)}
                      className="mt-0.5 h-4 w-4 rounded border-gray-300 text-navy-600 focus:ring-navy-500"
                    />
                    <span className="text-sm text-muted-foreground">
                      I hereby declare that all the information provided by me in this application is true, complete, and correct to the best of my knowledge and belief. I understand that if any information is found to be false or misleading, my candidature may be cancelled.
                    </span>
                  </label>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6">
          <div className="flex gap-2">
            {currentStep > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={() => setCurrentStep((s) => s - 1)}
              >
                <ChevronLeft className="h-4 w-4 mr-1" /> Previous
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="ghost" onClick={handleSaveDraft}>
              <Save className="h-4 w-4 mr-1" /> Save Draft
            </Button>
            {currentStep < steps.length ? (
              <Button type="button" onClick={() => setCurrentStep((s) => s + 1)}>
                Next <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button type="submit" loading={updateProfile.isPending}>
                Submit Profile
              </Button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
