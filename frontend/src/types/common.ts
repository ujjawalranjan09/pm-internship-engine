export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ActionConfig {
  label: string;
  onClick: () => void;
  /** Optional navigation href — renders as link if provided */
  href?: string;
  icon?: React.ReactNode;
}

export type SortDirection = "asc" | "desc";

export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  render?: (value: unknown, row: T) => React.ReactNode;
}
