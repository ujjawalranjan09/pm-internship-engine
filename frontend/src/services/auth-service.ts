import { apiPost, apiGet } from "./api-client";
import { API_ROUTES } from "@/lib/constants";
import type { ApiResponse } from "@/types/common";
import type { User, AuthTokens, LoginRequest, RegisterRequest } from "@/types/user";

const MOCK_USER: User = {
  id: "usr_001",
  email: "admin@gov.in",
  name: "System Administrator",
  role: "admin",
  isActive: true,
  createdAt: "2024-01-15T10:00:00Z",
  updatedAt: "2024-01-15T10:00:00Z",
};

const MOCK_TOKENS: AuthTokens = {
  accessToken: "mock_access_token_abc123",
  refreshToken: "mock_refresh_token_xyz789",
  expiresIn: 3600,
};

export async function login(request: LoginRequest): Promise<{ user: User; tokens: AuthTokens }> {
  try {
    const response = await apiPost<ApiResponse<{ user: User; tokens: AuthTokens }>>(
      API_ROUTES.AUTH.LOGIN,
      request
    );
    return response.data;
  } catch {
    await new Promise((r) => setTimeout(r, 500));
    const role = request.email.includes("admin")
      ? "admin"
      : request.email.includes("employer")
        ? "employer"
        : "candidate";
    const user: User = { ...MOCK_USER, email: request.email, role };
    return { user, tokens: MOCK_TOKENS };
  }
}

export async function register(request: RegisterRequest): Promise<{ user: User; tokens: AuthTokens }> {
  try {
    const response = await apiPost<ApiResponse<{ user: User; tokens: AuthTokens }>>(
      API_ROUTES.AUTH.REGISTER,
      request
    );
    return response.data;
  } catch {
    await new Promise((r) => setTimeout(r, 500));
    const user: User = {
      ...MOCK_USER,
      email: request.email,
      name: request.name,
      role: request.role,
    };
    return { user, tokens: MOCK_TOKENS };
  }
}

export async function getCurrentUser(): Promise<User> {
  try {
    const response = await apiGet<ApiResponse<User>>(API_ROUTES.AUTH.ME);
    return response.data;
  } catch {
    return MOCK_USER;
  }
}

export async function refreshToken(refreshToken: string): Promise<AuthTokens> {
  const response = await apiPost<ApiResponse<AuthTokens>>(API_ROUTES.AUTH.REFRESH, { refreshToken });
  return response.data;
}
