"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useAuth } from "@/hooks/use-auth";

export type UserRole = "admin" | "employer" | "candidate" | null;

interface RoleContextValue {
  role: UserRole;
  isLoading: boolean;
}

const RoleContext = createContext<RoleContextValue>({
  role: null,
  isLoading: true,
});

export function RoleProvider({ children }: { children: ReactNode }) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const [role, setRole] = useState<UserRole>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user?.role) {
        setRole(user.role as UserRole);
      } else {
        setRole(null);
      }
      setLoading(false);
    }
  }, [isLoading, isAuthenticated, user]);

  // Apply role-specific CSS variables to document root
  useEffect(() => {
    if (!role) return;

    const root = document.documentElement;

    // Clear all role classes
    root.classList.remove("role-admin", "role-employer", "role-candidate");

    // Apply current role
    root.classList.add(`role-${role}`);

    // Set CSS variables for current role
    const roleColors: Record<UserRole, { primary: string; primaryForeground: string; primary50: string; primary100: string; primary500: string; primary600: string; primary700: string; primary800: string; primary900: string }> = {
      admin: {
        primary: "#1a2f4a",
        primaryForeground: "#ffffff",
        primary50: "#eff6ff",
        primary100: "#dbeafe",
        primary500: "#1e3a5f",
        primary600: "#1a2f4a",
        primary700: "#152642",
        primary800: "#0f1d35",
        primary900: "#0a1428",
      },
      employer: {
        primary: "#ea580c",
        primaryForeground: "#ffffff",
        primary50: "#fff7ed",
        primary100: "#ffedd5",
        primary500: "#f97316",
        primary600: "#ea580c",
        primary700: "#c2410c",
        primary800: "#9a3412",
        primary900: "#7c2d12",
      },
      candidate: {
        primary: "#059669",
        primaryForeground: "#ffffff",
        primary50: "#ecfdf5",
        primary100: "#d1fae5",
        primary500: "#10b981",
        primary600: "#059669",
        primary700: "#047857",
        primary800: "#065f46",
        primary900: "#064e3b",
      },
      null: {
        primary: "#1a2f4a",
        primaryForeground: "#ffffff",
        primary50: "#eff6ff",
        primary100: "#dbeafe",
        primary500: "#1e3a5f",
        primary600: "#1a2f4a",
        primary700: "#152642",
        primary800: "#0f1d35",
        primary900: "#0a1428",
      },
    };

    const colors = roleColors[role];
    if (colors) {
      root.style.setProperty("--role-primary", colors.primary);
      root.style.setProperty("--role-primary-foreground", colors.primaryForeground);
      root.style.setProperty("--role-primary-50", colors.primary50);
      root.style.setProperty("--role-primary-100", colors.primary100);
      root.style.setProperty("--role-primary-500", colors.primary500);
      root.style.setProperty("--role-primary-600", colors.primary600);
      root.style.setProperty("--role-primary-700", colors.primary700);
      root.style.setProperty("--role-primary-800", colors.primary800);
      root.style.setProperty("--role-primary-900", colors.primary900);
    }
  }, [role]);

  return (
    <RoleContext.Provider value={{ role, isLoading: loading }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error("useRole must be used within a RoleProvider");
  }
  return context;
}