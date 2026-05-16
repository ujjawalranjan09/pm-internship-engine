export type UserRole = "candidate" | "employer" | "admin";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, string[]>;
}

export type AllocationStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export type ApplicationStatus =
  | "submitted"
  | "under_review"
  | "shortlisted"
  | "matched"
  | "allocated"
  | "accepted"
  | "declined"
  | "withdrawn";

export type OfferStatus = "pending" | "accepted" | "declined" | "expired";

export interface SelectOption {
  label: string;
  value: string;
}

export interface DateRange {
  from: string | null;
  to: string | null;
}

export interface SortConfig {
  field: string;
  direction: "asc" | "desc";
}

export interface FilterConfig {
  field: string;
  operator: "eq" | "neq" | "gt" | "gte" | "lt" | "lte" | "in" | "like";
  value: string | number | boolean | string[] | number[];
}
