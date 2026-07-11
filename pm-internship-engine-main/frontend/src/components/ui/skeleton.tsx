import { cn } from "@/lib/utils";

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-[var(--muted)]",
        "[background:linear-gradient(90deg,var(--muted)_25%,var(--muted-foreground)_37%,var(--muted)_63%)]",
        "[background-size:400%_100%]",
        "[animation:shimmer_1.5s_linear_infinite]",
        className
      )}
      {...props}
    />
  );
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border p-6 space-y-4 animate-fade-in stagger-2">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-3 w-2/3" />
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
      </div>
      <div className="flex gap-2">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );
}

function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-lg border overflow-hidden animate-fade-in stagger-3">
      <div className="bg-[var(--muted)]/50 p-3 flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="p-3 flex gap-4 border-t">
          {Array.from({ length: cols }).map((_, colIdx) => (
            <Skeleton key={colIdx} className="h-4 flex-1" style={{ animationDelay: `${(rowIdx * cols + colIdx) * 50}ms` }} />
          ))}
        </div>
      ))}
    </div>
  );
}

function SkeletonStat() {
  return (
    <div className="rounded-xl border p-6 space-y-2 animate-fade-in stagger-1">
      <Skeleton className="h-3 w-1/4" />
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="h-3 w-1/3" />
    </div>
  );
}

function SkeletonPageHeader() {
  return (
    <div className="animate-fade-in stagger-1 space-y-2">
      <Skeleton className="h-8 w-1/4" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  );
}

function SkeletonList({ items = 4 }: { items?: number }) {
  return (
    <div className="space-y-3 animate-fade-in">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 rounded-lg border">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="flex-1 space-y-1">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

export { Skeleton, SkeletonCard, SkeletonTable, SkeletonStat, SkeletonPageHeader, SkeletonList };