import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Format ISO date string to readable locale string */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "\u2014";
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return "\u2014";
  }
}

/** Format ISO date string to readable date + time string */
export function formatDateTime(dateStr?: string | null): string {
  if (!dateStr) return "\u2014";
  try {
    return new Date(dateStr).toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "\u2014";
  }
}

/** Format ISO date string as relative time (e.g. "2 hours ago") */
export function formatRelativeTime(dateStr?: string | null): string {
  if (!dateStr) return "\u2014";
  try {
    const diff = Date.now() - new Date(dateStr).getTime();
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 30) return `${days}d ago`;
    return formatDate(dateStr);
  } catch {
    return "\u2014";
  }
}

/** Format a number with locale-aware thousands separators */
export function formatNumber(value?: number | null): string {
  if (value == null) return "\u2014";
  return new Intl.NumberFormat("en-IN").format(value);
}

/** Format number as INR currency */
export function formatCurrency(amount?: number | null): string {
  if (amount == null) return "\u2014";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

/** Return a Tailwind class string for a status badge */
export function getStatusColor(status?: string): string {
  const s = (status ?? "").toLowerCase();
  const map: Record<string, string> = {
    active:     "bg-green-100 text-green-800",
    completed:  "bg-blue-100 text-blue-800",
    pending:    "bg-yellow-100 text-yellow-800",
    rejected:   "bg-red-100 text-red-800",
    approved:   "bg-green-100 text-green-800",
    running:    "bg-purple-100 text-purple-800",
    failed:     "bg-red-100 text-red-800",
    waitlisted: "bg-orange-100 text-orange-800",
    accepted:   "bg-emerald-100 text-emerald-800",
    withdrawn:  "bg-gray-100 text-gray-600",
    confirmed:  "bg-green-100 text-green-800",
    allocated:  "bg-blue-100 text-blue-800",
    declined:   "bg-red-100 text-red-800",
  };
  return map[s] ?? "bg-gray-100 text-gray-800";
}

/** Get initials from a full name (e.g. "John Doe" -> "JD") */
export function getInitials(name?: string | null): string {
  if (!name) return "?";
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

/** Truncate a string to maxLen characters */
export function truncate(str: string, maxLen = 60): string {
  return str.length <= maxLen ? str : `${str.slice(0, maxLen)}\u2026`;
}

/** Capitalise the first letter */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
