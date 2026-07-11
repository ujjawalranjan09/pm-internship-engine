import { cn } from "@/lib/utils";

interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  color?: "default" | "success" | "warning" | "error";
}

function Progress({ value, max = 100, className, size = "md", showLabel = false, color = "default" }: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const colors = {
    default: "bg-navy-500",
    success: "bg-gov-success",
    warning: "bg-gov-warning",
    error: "bg-gov-error",
  };

  const sizes = {
    sm: "h-1.5",
    md: "h-2.5",
    lg: "h-4",
  };

  const autoColor =
    color === "default"
      ? percentage >= 80
        ? "success"
        : percentage >= 50
          ? "warning"
          : percentage < 30
            ? "error"
            : "default"
      : color;

  return (
    <div className={cn("w-full", className)}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-sm text-muted-foreground">Progress</span>
          <span className="text-sm font-medium">{Math.round(percentage)}%</span>
        </div>
      )}
      <div
        className={cn("w-full rounded-full bg-muted overflow-hidden", sizes[size])}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={`${Math.round(percentage)}% complete`}
      >
        <div
          className={cn("h-full rounded-full transition-all duration-500 ease-out", colors[autoColor])}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export { Progress };
