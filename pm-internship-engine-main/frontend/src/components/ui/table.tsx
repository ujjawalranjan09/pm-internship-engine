"use client";

import { useState, type HTMLAttributes, type ThHTMLAttributes, type TdHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";

type Density = "comfortable" | "compact" | "dense";

function Table({ className, density = "comfortable", ...props }: HTMLAttributes<HTMLTableElement> & { density?: Density }) {
  const densityClasses = {
    comfortable: "",
    compact: "text-[12px]",
    dense: "text-[11px]",
  };
  const cellPadding = {
    comfortable: "px-4 py-3",
    compact: "px-3 py-2",
    dense: "px-2 py-1.5",
  };
  const headerHeight = {
    comfortable: "h-10",
    compact: "h-8",
    dense: "h-7",
  };

  return (
    <div className="relative w-full overflow-auto rounded-lg border">
      <table
        className={cn("w-full caption-bottom", densityClasses[density], className)}
        {...props}
        data-density={density}
      />
      <style jsx>{`
        .table-cell { padding: ${cellPadding[density]}; }
        .table-head { height: ${headerHeight[density]}; }
      `}</style>
    </div>
  );
}

function TableHeader({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <thead className={cn("border-b bg-muted/50", className)} {...props} />;
}

function TableBody({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className={cn("[&_tr:last-child]:border-0", className)} {...props} />;
}

function TableFooter({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <tfoot className={cn("border-t bg-muted/50 font-medium", className)} {...props} />;
}

function TableRow({ className, ...props }: HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={cn(
        "border-b transition-colors",
        "hover:bg-muted/50",
        "data-[state=selected]:bg-[var(--role-primary-50)]",
        "data-[state=selected]:border-l-2 data-[state=selected]:border-l-[var(--role-primary-500)]",
        className
      )}
      {...props}
    />
  );
}

function TableHead({ className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn(
        "table-head table-cell px-4 text-left align-middle font-medium text-muted-foreground",
        "font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs",
        "[&:has([role=checkbox])]:pr-0",
        className
      )}
      {...props}
    />
  );
}

function TableCell({ className, ...props }: TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td
      className={cn(
        "table-cell align-middle",
        "[&:has([role=checkbox])]:pr-0",
        className
      )}
      {...props}
    />
  );
}

function TableCaption({ className, ...props }: HTMLAttributes<HTMLTableCaptionElement>) {
  return <caption className={cn("mt-4 text-sm text-muted-foreground", className)} {...props} />;
}

interface SortableHeaderProps extends ThHTMLAttributes<HTMLTableCellElement> {
  sortField: string;
  currentSort?: { field: string; direction: "asc" | "desc" };
  onSort: (field: string) => void;
}

function SortableHeader({ sortField, currentSort, onSort, children, className, ...props }: SortableHeaderProps) {
  const isActive = currentSort?.field === sortField;

  return (
    <th
      className={cn(
        "table-head table-cell px-4 text-left align-middle font-medium text-muted-foreground",
        "font-[var(--font-jetbrains-mono)] uppercase tracking-wider text-xs",
        "cursor-pointer select-none hover:text-foreground",
        "[&:has([role=checkbox])]:pr-0",
        className
      )}
      onClick={() => onSort(sortField)}
      aria-sort={isActive ? (currentSort?.direction === "asc" ? "ascending" : "descending") : "none"}
      {...props}
    >
      <div className="flex items-center gap-1">
        {children}
        {isActive ? (
          currentSort?.direction === "asc" ? (
            <ChevronUp className="h-4 w-4 text-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-foreground" />
          )
        ) : (
          <ChevronsUpDown className="h-4 w-4 opacity-50" />
        )}
      </div>
    </th>
  );
}

interface DensityToggleProps {
  density: Density;
  onChange: (density: Density) => void;
}

function DensityToggle({ density, onChange }: DensityToggleProps) {
  return (
    <div className="flex items-center gap-1 bg-muted rounded-lg p-1" role="group" aria-label="Table density">
      {(["comfortable", "compact", "dense"] as Density[]).map((d) => (
        <button
          key={d}
          type="button"
          onClick={() => onChange(d)}
          className={cn(
            "px-2 py-1 rounded text-xs font-medium transition-all",
            density === d
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
          aria-pressed={density === d}
        >
          {d.charAt(0).toUpperCase() + d.slice(1)}
        </button>
      ))}
    </div>
  );
}

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableRow,
  TableHead,
  TableCell,
  TableCaption,
  SortableHeader,
  DensityToggle,
};
export type { Density };