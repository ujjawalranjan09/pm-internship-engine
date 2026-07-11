"use client";

import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useAuthStore, syncAuthToken } from "@/stores/auth-store";
import * as authService from "@/services/auth-service";
import type { LoginRequest, RegisterRequest } from "@/types/user";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated, isLoading, login, logout, setLoading, setUser } = useAuthStore();

  // Bootstrap: resolve isLoading on mount by probing current session
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (active) setUser(currentUser);
      } catch {
        // no session — nothing to do, isAuthenticated remains false
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [setLoading, setUser]);

  const { data: currentUser } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: authService.getCurrentUser,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (data) => {
      login(data.user, data.tokens);
      syncAuthToken(data.tokens);
      queryClient.invalidateQueries({ queryKey: ["auth"] });
      const redirectMap = {
        admin: "/admin",
        employer: "/employer",
        candidate: "/applicant",
      };
      router.push(redirectMap[data.user.role] || "/applicant");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: (data) => {
      login(data.user, data.tokens);
      syncAuthToken(data.tokens);
      queryClient.invalidateQueries({ queryKey: ["auth"] });
      router.push(data.user.role === "employer" ? "/employer" : "/applicant");
    },
  });

  const logoutFn = () => {
    logout();
    syncAuthToken(null);
    queryClient.clear();
    router.push("/auth/login");
  };

  return {
    user: currentUser || user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutFn,
    loginError: loginMutation.error?.message || null,
    registerError: registerMutation.error?.message || null,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
  };
}
