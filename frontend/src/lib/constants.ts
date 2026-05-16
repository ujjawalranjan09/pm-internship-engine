const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const API_ROUTES = {
  AUTH: {
    LOGIN:   `${BASE}/auth/login`,
    LOGOUT:  `${BASE}/auth/logout`,
    REFRESH: `${BASE}/auth/refresh`,
    ME:      `${BASE}/auth/me`,
  },
  CANDIDATES: {
    LIST:      `${BASE}/candidates`,
    PROFILE:   `${BASE}/candidates/me`,
    UPDATE:    `${BASE}/candidates/me`,
    EDUCATION: `${BASE}/candidates/me/education`,
    SKILLS:    `${BASE}/candidates/me/skills`,
    BY_ID:     (id: string) => `${BASE}/candidates/${id}`,
  },
  OPPORTUNITIES: {
    LIST:   `${BASE}/opportunities`,
    BY_ID:  (id: string) => `${BASE}/opportunities/${id}`,
    CREATE: `${BASE}/opportunities`,
    UPDATE: (id: string) => `${BASE}/opportunities/${id}`,
    DELETE: (id: string) => `${BASE}/opportunities/${id}`,
  },
  MATCHING: {
    TRIGGER:    `${BASE}/matching/trigger`,
    RESULTS:    `${BASE}/matching/results`,
    BY_ID:      (id: string) => `${BASE}/matching/${id}`,
    MY_MATCHES: `${BASE}/matching/me`,
  },
  ALLOCATION: {
    CYCLES:       `${BASE}/allocation/cycles`,
    CYCLE_DETAIL: (id: string) => `${BASE}/allocation/cycles/${id}`,
    TRIGGER:      `${BASE}/allocation/trigger`,
    RESULTS:      (cycleId: string) => `${BASE}/allocation/cycles/${cycleId}/results`,
    FAIRNESS:     `${BASE}/allocation/fairness`,
  },
  ADMIN: {
    POLICY:            `${BASE}/admin/policy`,
    AUDIT:             `${BASE}/admin/audit`,
    OVERRIDES:         `${BASE}/admin/overrides`,
    APPROVE_OVERRIDE:  (id: string) => `${BASE}/admin/overrides/${id}/approve`,
    REJECT_OVERRIDE:   (id: string) => `${BASE}/admin/overrides/${id}/reject`,
    ANALYTICS:         `${BASE}/admin/analytics`,
    FAIRNESS:          `${BASE}/admin/fairness`,
    SEND_NOTIFICATION: `${BASE}/admin/notifications/send`,
  },
} as const;
