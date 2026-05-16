const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const APP_NAME = "PM Internship Engine";

export const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "Internships", href: "/applicant/internships" },
  { label: "Matches", href: "/applicant/matches" },
  { label: "Applications", href: "/applicant/applications" },
] as const;

export const SECTORS = [
  "Information Technology",
  "Finance & Banking",
  "Healthcare",
  "Manufacturing",
  "Media & Communications",
  "Education",
  "Agriculture",
  "Energy",
  "Retail",
  "Government",
] as const;

export const STATES = [
  "Rajasthan",
  "Maharashtra",
  "Karnataka",
  "Delhi",
  "Tamil Nadu",
  "Uttar Pradesh",
  "Gujarat",
  "West Bengal",
  "Telangana",
  "Punjab",
] as const;

export const STATES_AND_DISTRICTS: Record<string, string[]> = {
  Rajasthan: ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
  Maharashtra: ["Mumbai", "Pune", "Nagpur", "Nashik"],
  Karnataka: ["Bangalore", "Mysore", "Hubli"],
  Delhi: ["New Delhi", "Central Delhi", "South Delhi"],
  "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
};

export const SKILL_CATEGORIES: Record<string, string[]> = {
  Technical: ["Python", "JavaScript", "React", "SQL", "Java", "Docker", "AWS"],
  SoftSkills: ["Communication", "Leadership", "Teamwork", "Problem Solving"],
  Domain: ["Finance", "Healthcare", "Marketing", "Operations"],
};

export const EDUCATION_LEVELS = [
  "10th Pass",
  "12th Pass",
  "Diploma",
  "Undergraduate",
  "Postgraduate",
] as const;

export const CATEGORIES = ["General", "OBC", "SC", "ST", "EWS"] as const;

export const API_ROUTES = {
  AUTH: {
    LOGIN: `${BASE}/auth/login`,
    REGISTER: `${BASE}/auth/register`,
    LOGOUT: `${BASE}/auth/logout`,
    REFRESH: `${BASE}/auth/refresh`,
    ME: `${BASE}/auth/me`,
  },
  CANDIDATES: {
    LIST: `${BASE}/candidates`,
    PROFILE: `${BASE}/candidates/me`,
    UPDATE: `${BASE}/candidates/me`,
    EDUCATION: `${BASE}/candidates/me/education`,
    SKILLS: `${BASE}/candidates/me/skills`,
    BY_ID: (id: string) => `${BASE}/candidates/${id}`,
  },
  OPPORTUNITIES: {
    LIST: `${BASE}/opportunities`,
    BY_ID: (id: string) => `${BASE}/opportunities/${id}`,
    DETAIL: (id: string) => `${BASE}/opportunities/${id}`,
    CREATE: `${BASE}/opportunities`,
    UPDATE: (id: string) => `${BASE}/opportunities/${id}`,
    DELETE: (id: string) => `${BASE}/opportunities/${id}`,
  },
  MATCHING: {
    TRIGGER: `${BASE}/matching/trigger`,
    RESULTS: `${BASE}/matching/results`,
    BY_ID: (id: string) => `${BASE}/matching/${id}`,
    MY_MATCHES: `${BASE}/matching/me`,
  },
  MATCHES: {
    RECOMMENDATIONS: `${BASE}/matching/me/recommendations`,
    FOR_OPPORTUNITY: (id: string) => `${BASE}/matching/opportunity/${id}`,
  },
  ALLOCATION: {
    CYCLES: `${BASE}/allocation/cycles`,
    CYCLE_DETAIL: (id: string) => `${BASE}/allocation/cycles/${id}`,
    TRIGGER: `${BASE}/allocation/trigger`,
    RESULTS: (cycleId: string) => `${BASE}/allocation/cycles/${cycleId}/results`,
    FAIRNESS: `${BASE}/allocation/fairness`,
  },
  ADMIN: {
    POLICY: `${BASE}/admin/policy`,
    AUDIT: `${BASE}/admin/audit`,
    OVERRIDES: `${BASE}/admin/overrides`,
    APPROVE_OVERRIDE: (id: string) => `${BASE}/admin/overrides/${id}/approve`,
    REJECT_OVERRIDE: (id: string) => `${BASE}/admin/overrides/${id}/reject`,
    ANALYTICS: `${BASE}/admin/analytics`,
    FAIRNESS: `${BASE}/admin/fairness`,
    SEND_NOTIFICATION: `${BASE}/admin/notifications/send`,
  },
} as const;
