import { type HTMLAttributes } from "react";
import { cn, getStatusColor } from "@/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "status" | "outline";
  status?: string;
  size?: "sm" | "md";
}

function Badge({ className, variant = "default", status, size = "md", children, ...props }: BadgeProps) {
  const baseStyles = "inline-flex items-center rounded-full font-medium transition-colors";

  const variants = {
    default: "bg-navy-100 text-navy-800",
    status: status ? getStatusColor(status) : "bg-gray-100 text-gray-800",
    outline: "border border-navy-300 text-navy-700",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-xs",
  };

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
}

export { Badge };
export type { BadgeProps };
