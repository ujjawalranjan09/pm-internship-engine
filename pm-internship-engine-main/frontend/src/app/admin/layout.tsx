"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { useNotifications } from "@/hooks/use-notifications";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  GitMerge,
  Shield,
  FileText,
  Bell,
  Menu,
  X,
  LogOut,
  Activity,
} from "lucide-react";
import { AllocationPulse } from "@/components/shared/allocation-pulse";

const navLinks = [
  { label: "Dashboard", href: "/admin", icon: LayoutDashboard },
  { label: "Candidates", href: "/admin/candidates", icon: Users },
  { label: "Opportunities", href: "/admin/opportunities", icon: Briefcase },
  { label: "Allocations", href: "/admin/allocations", icon: GitMerge },
  { label: "Matching", href: "/admin/matching", icon: Activity },
  { label: "Audit Logs", href: "/admin/audit", icon: FileText },
  { label: "Policy", href: "/admin/policy", icon: Shield },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const { data: notifications } = useNotifications();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const unreadCount = notifications?.filter((n) => !n.read).length ?? 0;

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || user?.role !== "admin")) {
      router.push("/auth/login");
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <LoadingSpinner size="lg" label="Loading admin panel..." />
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== "admin") return null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col role-admin">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="flex h-16 items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden p-2 rounded-md hover:bg-muted transition-colors"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <Link href="/admin" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg gov-gradient-admin flex items-center justify-center">
                <Shield className="h-4 w-4 text-white" />
              </div>
              <span className="hidden sm:block font-semibold text-navy-600 text-sm font-[var(--font-space-grotesk)]">
                Admin Panel
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-3">
            {/* Allocation Pulse Indicator */}
            <AllocationPulse />

            <button className="relative p-2 rounded-md hover:bg-muted transition-colors" aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}>
              <Bell className="h-5 w-5 text-muted-foreground" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 h-4 w-4 rounded-full bg-gov-error text-white text-[10px] font-bold flex items-center justify-center">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </button>

            <div className="flex items-center gap-2">
              <Avatar name={user.name ?? "Admin"} size="sm" />
              <span className="hidden sm:block text-sm font-medium truncate max-w-[120px]">{user.name}</span>
              <Badge variant="default" size="sm">Admin</Badge>
            </div>

            <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Mobile overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Sidebar */}
        <aside
          className={cn(
            "fixed lg:sticky top-16 z-30 h-[calc(100vh-4rem)] w-[var(--sidebar-width)] bg-navy-900 border-r transition-transform duration-200 ease-in-out",
            "lg:translate-x-0",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <nav className="flex flex-col h-full py-4 px-3" aria-label="Admin navigation">
            <div className="flex-1 space-y-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive =
                  pathname === link.href || (link.href !== "/admin" && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setSidebarOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                      isActive
                        ? "bg-saffron-500/10 text-saffron-400 border-l-2 border-saffron-500"
                        : "text-slate-300 hover:text-white hover:bg-white/5"
                    )}
                    aria-current={isActive ? "page" : undefined}
                  >
                    <Icon className="h-5 w-5 shrink-0" />
                    {link.label}
                  </Link>
                );
              })}
            </div>

            <div className="pt-4 border-t border-white/10">
              <button
                onClick={logout}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 w-full transition-all"
              >
                <LogOut className="h-5 w-5 shrink-0" />
                Sign Out
              </button>
            </div>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}