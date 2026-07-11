"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { LoadingSpinner } from "@/components/shared/loading-spinner";

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated) {
      router.replace("/auth/login");
    } else if (user?.role === "admin") {
      router.replace("/admin");
    } else if (user?.role === "employer") {
      router.replace("/employer");
    } else {
      router.replace("/applicant");
    }
  }, [isAuthenticated, isLoading, user, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner size="lg" label="Redirecting..." />
    </div>
  );
}
