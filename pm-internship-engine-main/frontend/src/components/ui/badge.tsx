import { type HTMLAttributes } from "react";
import { cn, getStatusColor } from "@/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "status" | "outline" | "destructive" | "role";
  status?: string;
  size?: "sm" | "md";
  dot?: boolean;
}

function Badge({
  className,
  variant = "default",
  status,
  size = "md",
  dot = false,
  children,
  ...props
}: BadgeProps) {
  const baseStyles = "inline-flex items-center rounded-full font-medium transition-colors";

  const variants: Record<NonNullable<BadgeProps["variant"]>, string> = {
    default: "bg-[var(--role-primary-100)] text-[var(--role-primary-700)]",
    secondary: "bg-gray-100 text-gray-700",
    status: status ? getStatusColor(status) : "bg-gray-100 text-gray-800",
    outline: "border border-[var(--role-primary-300)] text-[var(--role-primary-700)]",
    destructive: "bg-red-100 text-red-700",
    role: "bg-[var(--role-primary-100)] text-[var(--role-primary-700)]",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-xs",
  };

  const dotSize = size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2";

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {dot && status && (
        <span
          className={cn(
            "rounded-full mr-1.5 shrink-0",
            getStatusColor(status).replace("bg-", "bg-").replace("text-", "")
          )}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}

export { Badge };
export type { BadgeProps };