"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema, type RegisterFormData } from "@/lib/validators";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { Mail, Lock, User, Phone, Eye, EyeOff, Briefcase, GraduationCap } from "lucide-react";
import { cn } from "@/lib/utils";

export default function RegisterPage() {
  const { register: registerUser, isRegistering, registerError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      role: "candidate",
      phone: "",
    },
  });

  const selectedRole = watch("role");

  const onSubmit = (data: RegisterFormData) => {
    registerUser({
      name: data.name,
      email: data.email,
      password: data.password,
      role: data.role,
      phone: data.phone || undefined,
    });
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-center mb-1">Create Account</h2>
      <p className="text-sm text-muted-foreground text-center mb-6">
        Join the PM Internship Scheme
      </p>

      {registerError && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-gov-error" role="alert">
          {registerError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Role Selection */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">I am a</label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setValue("role", "candidate")}
              className={cn(
                "flex items-center gap-3 p-3 rounded-lg border-2 transition-all text-left",
                selectedRole === "candidate"
                  ? "border-navy-500 bg-navy-50"
                  : "border-border hover:border-gray-300"
              )}
            >
              <GraduationCap className={cn("h-5 w-5", selectedRole === "candidate" ? "text-navy-600" : "text-muted-foreground")} />
              <div>
                <p className={cn("text-sm font-medium", selectedRole === "candidate" ? "text-navy-600" : "")}>Candidate</p>
                <p className="text-xs text-muted-foreground">Looking for internships</p>
              </div>
            </button>
            <button
              type="button"
              onClick={() => setValue("role", "employer")}
              className={cn(
                "flex items-center gap-3 p-3 rounded-lg border-2 transition-all text-left",
                selectedRole === "employer"
                  ? "border-navy-500 bg-navy-50"
                  : "border-border hover:border-gray-300"
              )}
            >
              <Briefcase className={cn("h-5 w-5", selectedRole === "employer" ? "text-navy-600" : "text-muted-foreground")} />
              <div>
                <p className={cn("text-sm font-medium", selectedRole === "employer" ? "text-navy-600" : "")}>Employer</p>
                <p className="text-xs text-muted-foreground">Offering internships</p>
              </div>
            </button>
          </div>
          <input type="hidden" {...register("role")} />
          {errors.role && <p className="mt-1 text-sm text-gov-error">{errors.role.message}</p>}
        </div>

        <Input
          label="Full Name"
          type="text"
          placeholder="Enter your full name"
          leftIcon={<User className="h-4 w-4" />}
          error={errors.name?.message}
          {...register("name")}
          autoComplete="name"
        />

        <Input
          label="Email Address"
          type="email"
          placeholder="you@example.com"
          leftIcon={<Mail className="h-4 w-4" />}
          error={errors.email?.message}
          {...register("email")}
          autoComplete="email"
        />

        <Input
          label="Phone Number"
          type="tel"
          placeholder="9876543210"
          leftIcon={<Phone className="h-4 w-4" />}
          error={errors.phone?.message}
          {...register("phone")}
          helperText="Optional - 10-digit Indian mobile number"
        />

        <Input
          label="Password"
          type={showPassword ? "text" : "password"}
          placeholder="Min 8 characters"
          leftIcon={<Lock className="h-4 w-4" />}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-muted-foreground hover:text-foreground"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          }
          error={errors.password?.message}
          {...register("password")}
          autoComplete="new-password"
        />

        <Input
          label="Confirm Password"
          type="password"
          placeholder="Re-enter your password"
          leftIcon={<Lock className="h-4 w-4" />}
          error={errors.confirmPassword?.message}
          {...register("confirmPassword")}
          autoComplete="new-password"
        />

        <Button type="submit" className="w-full" loading={isRegistering}>
          Create Account
        </Button>
      </form>

      <div className="mt-4 text-center text-sm">
        <p className="text-muted-foreground">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-navy-500 font-medium hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
