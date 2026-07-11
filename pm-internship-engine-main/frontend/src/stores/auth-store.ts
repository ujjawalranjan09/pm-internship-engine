import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, AuthTokens } from "@/types/user";

function setAuthToken(token: string | null) {
  if (typeof window !== "undefined") {
    if (token) localStorage.setItem("access_token", token);
    else localStorage.removeItem("access_token");
  }
}

interface AuthStore {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setTokens: (tokens: AuthTokens | null) => void;
  setLoading: (loading: boolean) => void;
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: true,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      setTokens: (tokens) => set({ tokens }),

      setLoading: (isLoading) => set({ isLoading }),

      login: (user, tokens) =>
        set({
          user,
          tokens,
          isAuthenticated: true,
          isLoading: false,
        }),

      logout: () =>
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          isLoading: false,
        }),
    }),
    {
      name: "auth_storage",
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Helper to sync localStorage with store changes
export function syncAuthToken(tokens: AuthTokens | null) {
  setAuthToken(tokens?.accessToken ?? null);
}
