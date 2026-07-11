"use client";

import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface Breadcrumb {
  label: string;
  href?: string;
}

interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: Breadcrumb[];
  actions?: ReactNode;
  action?: ReactNode; // deprecated alias
  className?: string;
}

function PageHeader({ title, description, breadcrumbs, actions, action, className }: PageHeaderProps) {
  const headerActions = actions ?? action;

  return (
    <div className={cn("mb-6", className)}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav aria-label="Breadcrumb" className="mb-3">
          <ol className="flex items-center gap-1 text-sm text-muted-foreground font-[var(--font-jetbrains-mono)]">
            <li>
              <Link href="/" className="hover:text-foreground transition-colors" aria-label="Home">
                <Home className="h-4 w-4" />
              </Link>
            </li>
            {breadcrumbs.map((crumb, idx) => (
              <li key={idx} className="flex items-center gap-1">
                <ChevronRight className="h-4 w-4 text-current" aria-hidden="true" />
                {crumb.href ? (
                  <Link href={crumb.href} className="hover:text-foreground transition-colors">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="text-foreground font-medium font-[var(--font-dm-sans)]">{crumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground font-[var(--font-space-grotesk)] tracking-tight">
            {title}
          </h1>
          {description && (
            <p className="mt-1 text-sm text-muted-foreground max-w-2xl font-[var(--font-dm-sans)]">
              {description}
            </p>
          )}
        </div>
        {headerActions && <div className="flex items-center gap-2">{headerActions}</div>}
      </div>
    </div>
  );
}

export { PageHeader };
export type { Breadcrumb, PageHeaderProps };