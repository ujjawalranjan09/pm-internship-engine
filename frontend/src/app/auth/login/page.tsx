"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, type LoginFormData } from "@/lib/validators";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = (data: LoginFormData) => {
    login(data);
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-center mb-1">Welcome Back</h2>
      <p className="text-sm text-muted-foreground text-center mb-6">
        Sign in to access your account
      </p>

      {loginError && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-gov-error" role="alert">
          {loginError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
          label="Password"
          type={showPassword ? "text" : "password"}
          placeholder="Enter your password"
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
          autoComplete="current-password"
        />

        <Button type="submit" className="w-full" loading={isLoggingIn}>
          Sign In
        </Button>
      </form>

      <div className="mt-4 text-center text-sm">
        <p className="text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link href="/auth/register" className="text-navy-500 font-medium hover:underline">
            Register
          </Link>
        </p>
      </div>

      <div className="mt-6 pt-4 border-t">
        <p className="text-xs text-muted-foreground text-center mb-2">Demo accounts:</p>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <button
            type="button"
            onClick={() => login({ email: "candidate@gov.in", password: "password123" })}
            className="p-2 rounded border hover:bg-muted transition-colors text-center"
          >
            <span className="font-medium block">Candidate</span>
            <span className="text-muted-foreground">candidate@gov.in</span>
          </button>
          <button
            type="button"
            onClick={() => login({ email: "employer@gov.in", password: "password123" })}
            className="p-2 rounded border hover:bg-muted transition-colors text-center"
          >
            <span className="font-medium block">Employer</span>
            <span className="text-muted-foreground">employer@gov.in</span>
          </button>
          <button
            type="button"
            onClick={() => login({ email: "admin@gov.in", password: "password123" })}
            className="p-2 rounded border hover:bg-muted transition-colors text-center"
          >
            <span className="font-medium block">Admin</span>
            <span className="text-muted-foreground">admin@gov.in</span>
          </button>
        </div>
      </div>
    </div>
  );
}
