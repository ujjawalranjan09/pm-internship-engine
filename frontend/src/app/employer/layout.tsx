"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { useNotifications } from "@/hooks/use-notifications";
import { useAuthStore } from "@/stores/auth-store";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Briefcase,
  Users,
  Bell,
  Menu,
  X,
  LogOut,
  Building2,
} from "lucide-react";

const navLinks = [
  { label: "Dashboard", href: "/employer", icon: LayoutDashboard },
  { label: "My Internships", href: "/employer/internships", icon: Briefcase },
  { label: "Feedback", href: "/employer/feedback", icon: Users },
];

export default function EmployerLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const hasHydrated = useAuthStore((s) => s._hasHydrated);
  const { data: notifications } = useNotifications();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const unreadCount = notifications?.filter((n) => !n.read).length ?? 0;

  useEffect(() => {
    if (!hasHydrated || isLoading) return;
    if (!isAuthenticated || user?.role !== "employer") {
      router.push("/auth/login");
    }
  }, [hasHydrated, isLoading, isAuthenticated, user, router]);

  if (!hasHydrated || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" label="Loading employer portal..." />
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== "employer") return null;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="flex h-16 items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden p-2 rounded-md hover:bg-muted transition-colors"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <Link href="/employer" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-saffron-500 flex items-center justify-center">
                <Building2 className="h-4 w-4 text-white" />
              </div>
              <span className="hidden sm:block font-semibold text-navy-500 text-sm">
                Employer Portal
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <button
              className="relative p-2 rounded-md hover:bg-muted transition-colors"
              aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
            >
              <Bell className="h-5 w-5 text-muted-foreground" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 h-4 w-4 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </button>
            <div className="flex items-center gap-2">
              <Avatar name={user.name ?? "Employer"} size="sm" />
              <span className="hidden sm:block text-sm font-medium truncate max-w-[120px]">
                {user.name}
              </span>
              <Badge variant="default" size="sm">Employer</Badge>
            </div>
            <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <aside
          className={cn(
            "fixed lg:sticky top-16 z-30 h-[calc(100vh-4rem)] w-64 bg-white border-r transition-transform duration-200",
            "lg:translate-x-0",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <nav className="flex flex-col h-full py-4 px-3">
            <div className="flex-1 space-y-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive =
                  pathname === link.href ||
                  (link.href !== "/employer" && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setSidebarOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                      isActive
                        ? "bg-navy-50 text-navy-600 shadow-sm"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    )}
                  >
                    <Icon className="h-5 w-5 shrink-0" />
                    {link.label}
                  </Link>
                );
              })}
            </div>
            <div className="pt-4 border-t">
              <button
                onClick={logout}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted w-full transition-all"
              >
                <LogOut className="h-5 w-5 shrink-0" />
                Sign Out
              </button>
            </div>
          </nav>
        </aside>

        <main className="flex-1 min-w-0 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
