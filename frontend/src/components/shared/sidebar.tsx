"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Shuffle,
  BarChart3,
  Settings,
  Shield,
  Bell,
  AlertTriangle,
  FileText,
} from "lucide-react";

const adminLinks = [
  { label: "Overview", href: "/admin", icon: LayoutDashboard },
  { label: "Candidates", href: "/admin/candidates", icon: Users },
  { label: "Opportunities", href: "/admin/opportunities", icon: Briefcase },
  { label: "Allocation", href: "/admin/allocation", icon: Shuffle },
  { label: "Fairness", href: "/admin/fairness", icon: BarChart3 },
  { label: "Policy", href: "/admin/policy", icon: Settings },
  { label: "Audit", href: "/admin/audit", icon: FileText },
  { label: "Overrides", href: "/admin/overrides", icon: AlertTriangle },
  { label: "Notifications", href: "/admin/notifications", icon: Bell },
];

const applicantLinks = [
  { label: "Dashboard", href: "/applicant", icon: LayoutDashboard },
  { label: "Internships", href: "/applicant/internships", icon: Briefcase },
  { label: "Applications", href: "/applicant/applications", icon: FileText },
  { label: "Offers", href: "/applicant/offers", icon: Shield },
  { label: "Profile", href: "/applicant/profile", icon: Users },
];

const employerLinks = [
  { label: "Dashboard", href: "/employer", icon: LayoutDashboard },
  { label: "Internships", href: "/employer/internships", icon: Briefcase },
  { label: "Feedback", href: "/employer/feedback", icon: FileText },
];

interface SidebarProps {
  role: "admin" | "candidate" | "employer";
  className?: string;
}

function Sidebar({ role, className }: SidebarProps) {
  const pathname = usePathname();
  const links = role === "admin" ? adminLinks : role === "candidate" ? applicantLinks : employerLinks;

  return (
    <aside
      className={cn(
        "hidden lg:flex lg:flex-col lg:w-64 border-r bg-white min-h-[calc(100vh-4rem)]",
        className
      )}
    >
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto scrollbar-thin">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href || (link.href !== `/${role === "candidate" ? "applicant" : role}` && pathname.startsWith(link.href));
          return (
            <Link
              key={link.href}
              href={link.href}
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
    </aside>
  );
}

export { Sidebar };
