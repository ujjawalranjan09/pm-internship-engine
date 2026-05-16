import { cn } from "@/lib/utils";
import { Inbox, Search, FileX, Users, GitMerge } from "lucide-react";
import { Button } from "@/components/ui/button";

type EmptyStateIconKey = "inbox" | "search" | "file" | "users" | "merge";

interface EmptyStateProps {
  icon?: EmptyStateIconKey | (string & {});
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const icons: Record<EmptyStateIconKey, React.ElementType> = {
  inbox:  Inbox,
  search: Search,
  file:   FileX,
  users:  Users,
  merge:  GitMerge,
};

function EmptyState({
  icon = "inbox",
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const IconComponent =
    icons[icon as EmptyStateIconKey] ?? Inbox;

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 px-4 text-center",
        className
      )}
    >
      <div className="rounded-full bg-muted p-4 mb-4">
        <IconComponent
          className="h-8 w-8 text-muted-foreground"
          aria-hidden="true"
        />
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-muted-foreground max-w-sm">
          {description}
        </p>
      )}
      {action && (
        <Button onClick={action.onClick} className="mt-4" variant="primary" size="sm">
          {action.label}
        </Button>
      )}
    </div>
  );
}

export { EmptyState };
