import { cn } from "@/lib/utils";
import { Inbox, Search, FileX, Users, GitMerge, Briefcase, UserPlus, Compass, Puzzle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

type EmptyStateIconKey =
  | "inbox"
  | "search"
  | "file"
  | "users"
  | "merge"
  | "briefcase"
  | "profile"
  | "match";

interface EmptyStateAction {
  label: string;
  onClick?: () => void;
  href?: string;
}

interface EmptyStateProps {
  icon?: EmptyStateIconKey | (string & {});
  title: string;
  description?: string;
  action?: EmptyStateAction;
  className?: string;
}

const icons: Record<EmptyStateIconKey, React.ElementType> = {
  inbox: Inbox,
  search: Search,
  file: FileX,
  users: Users,
  merge: GitMerge,
  briefcase: Briefcase,
  profile: UserPlus,
  match: Puzzle,
};

function EmptyState({
  icon = "inbox",
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const IconComponent = icons[icon as EmptyStateIconKey] ?? Inbox;

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 px-4 text-center animate-fade-in",
        className
      )}
    >
      <div className="rounded-full bg-[var(--role-primary-50)] p-4 mb-4">
        <IconComponent
          className="h-10 w-10 text-[var(--role-primary-600)]"
          aria-hidden="true"
        />
      </div>
      <h3 className="text-lg font-semibold text-foreground font-[var(--font-space-grotesk)]">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-muted-foreground max-w-sm font-[var(--font-dm-sans)]">
          {description}
        </p>
      )}
      {action && (
        <div className="mt-4">
          {action.href ? (
            <Link href={action.href}>
              <Button variant="primary" size="sm">
                {action.label}
              </Button>
            </Link>
          ) : (
            <Button onClick={action.onClick} variant="primary" size="sm">
              {action.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

export { EmptyState };
export type { EmptyStateIconKey, EmptyStateAction, EmptyStateProps };