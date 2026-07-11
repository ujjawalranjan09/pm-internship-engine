import { API_ROUTES } from "@/lib/constants";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("access_token");
  }
  return null;
}

/** Convert snake_case string to camelCase */
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

/** Recursively transform all object keys from snake_case to camelCase */
function transformKeys<T>(obj: unknown): T {
  if (Array.isArray(obj)) return obj.map(transformKeys) as T;
  if (obj !== null && typeof obj === "object") {
    const entries = Object.entries(obj).map(([key, value]) => [
      snakeToCamel(key),
      transformKeys(value),
    ]);
    return Object.fromEntries(entries) as T;
  }
  return obj as T;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json();
  // Auto-transform snake_case backend responses to camelCase frontend types
  return transformKeys<T>(data);
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: "GET" });
}

export async function apiPost<T>(endpoint: string, data?: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: "POST",
    body: data ? JSON.stringify(data) : undefined,
  });
}

export async function apiPut<T>(endpoint: string, data: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function apiPatch<T>(endpoint: string, data: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function apiDelete<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: "DELETE" });
}