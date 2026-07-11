import { apiPost, apiGet } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse } from "@/types/common";
import type { User, AuthTokens } from "@/types/user";

export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  password: string;
  role: "candidate" | "employer" | "admin";
};

function setAuthToken(token: string | null) {
  if (typeof window !== "undefined") {
    if (token) localStorage.setItem("access_token", token);
    else localStorage.removeItem("access_token");
  }
}

// Backend UserResponse shape (snake_case, int id, no name field)
type BackendUser = {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

function toFrontendUser(bu: BackendUser): User {
  const nameFromEmail = bu.email.split("@")[0].replace(/[._]/g, " ");
  return {
    id: String(bu.id),
    email: bu.email,
    name: nameFromEmail,
    role: bu.role as User["role"],
    isActive: bu.is_active,
    createdAt: bu.created_at,
    updatedAt: bu.updated_at,
  };
}

export async function login(data: LoginRequest): Promise<{ user: User; tokens: AuthTokens }> {
  const response = await apiPost<{ access_token: string; refresh_token: string; token_type: string }>(
    API_ROUTES.AUTH.LOGIN,
    data
  );
  const tokens = { accessToken: response.access_token, refreshToken: response.refresh_token };
  setAuthToken(response.access_token);

  const userResponse = await apiGet<BackendUser>(API_ROUTES.AUTH.ME);
  return { user: toFrontendUser(userResponse), tokens };
}

export async function register(data: RegisterRequest): Promise<{ user: User; tokens: AuthTokens }> {
  await apiPost<BackendUser>(API_ROUTES.AUTH.REGISTER, data);
  // Auto-login after registration
  return login({ email: data.email, password: data.password });
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiGet<BackendUser>(API_ROUTES.AUTH.ME);
  return toFrontendUser(response);
}

export async function logout(): Promise<void> {
  try {
    await apiPost(API_ROUTES.AUTH.LOGOUT, {});
  } catch {
    // Ignore logout errors
  } finally {
    setAuthToken(null);
  }
}

export async function refreshToken(refreshToken: string): Promise<AuthTokens> {
  const response = await apiPost<{ access_token: string; refresh_token: string; token_type: string }>(
    API_ROUTES.AUTH.REFRESH,
    { refresh_token: refreshToken }
  );
  setAuthToken(response.access_token);
  return { accessToken: response.access_token, refreshToken: response.refresh_token };
}