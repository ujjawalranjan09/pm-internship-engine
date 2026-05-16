import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Format ISO date string to readable locale string */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return "—";
  }
}

/** Format ISO date string to readable locale date time string */
export function formatDateTime(dateStr?: string | null): string {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "—";
  }
}

/** Format number as INR currency */
export function formatCurrency(amount?: number | null): string {
  if (amount == null) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

/** Format plain number with locale separators */
export function formatNumber(value?: number | null): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-IN").format(value);
}

/** Format timestamp as relative time */
export function formatRelativeTime(dateStr?: string | null): string {
  if (!dateStr) return "—";
  const timestamp = new Date(dateStr).getTime();
  if (Number.isNaN(timestamp)) return "—";

  const diffMs = Date.now() - timestamp;
  const diffMinutes = Math.floor(diffMs / 60000);

  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;

  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths < 12) return `${diffMonths}mo ago`;

  const diffYears = Math.floor(diffMonths / 12);
  return `${diffYears}y ago`;
}

/** Return initials from a full name */
export function getInitials(name?: string | null): string {
  if (!name) return "?";
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

/** Return a Tailwind class string for a status badge */
export function getStatusColor(status?: string): string {
  const s = (status ?? "").toLowerCase();
  const map: Record<string, string> = {
    active: "bg-green-100 text-green-800",
    completed: "bg-blue-100 text-blue-800",
    pending: "bg-yellow-100 text-yellow-800",
    rejected: "bg-red-100 text-red-800",
    approved: "bg-green-100 text-green-800",
    running: "bg-purple-100 text-purple-800",
    failed: "bg-red-100 text-red-800",
    waitlisted: "bg-orange-100 text-orange-800",
    accepted: "bg-emerald-100 text-emerald-800",
    withdrawn: "bg-gray-100 text-gray-600",
    confirmed: "bg-green-100 text-green-800",
    allocated: "bg-blue-100 text-blue-800",
    declined: "bg-red-100 text-red-800",
  };
  return map[s] ?? "bg-gray-100 text-gray-800";
}

/** Truncate a string to maxLen characters */
export function truncate(str: string, maxLen = 60): string {
  return str.length <= maxLen ? str : `${str.slice(0, maxLen)}…`;
}

/** Capitalise the first letter */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
