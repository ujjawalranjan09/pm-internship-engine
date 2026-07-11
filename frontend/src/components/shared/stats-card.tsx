import { cn, formatNumber } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: number | string;
  description?: string;
  trend?: {
    value: number;
    direction: "up" | "down" | "neutral";
    label?: string;
  };
  icon?: React.ReactNode;
  className?: string;
  format?: "number" | "currency" | "percentage" | "none";
}

function StatsCard({ title, value, description, trend, icon, className, format = "number" }: StatsCardProps) {
  const displayValue =
    typeof value === "number"
      ? format === "currency"
        ? `₹${formatNumber(value)}`
        : format === "percentage"
          ? `${value}%`
          : formatNumber(value)
      : value;

  const trendColors = {
    up: "text-gov-success",
    down: "text-gov-error",
    neutral: "text-muted-foreground",
  };

  const TrendIcon = trend
    ? trend.direction === "up"
      ? TrendingUp
      : trend.direction === "down"
        ? TrendingDown
        : Minus
    : null;

  return (
    <Card className={cn("hover:shadow-md transition-shadow", className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold text-foreground">{displayValue}</p>
            {trend && TrendIcon && (
              <div className={cn("flex items-center gap-1 text-xs font-medium", trendColors[trend.direction])}>
                <TrendIcon className="h-3 w-3" aria-hidden="true" />
                <span>{Math.abs(trend.value)}%</span>
                {trend.label && <span className="text-muted-foreground ml-1">{trend.label}</span>}
              </div>
            )}
            {description && !trend && (
              <p className="text-xs text-muted-foreground">{description}</p>
            )}
          </div>
          {icon && (
            <div className="rounded-lg bg-navy-50 p-2.5 text-navy-600" aria-hidden="true">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export { StatsCard };
