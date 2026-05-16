const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const APP_NAME = "PM Internship Engine";

export const NAV_LINKS = [
  { label: "Home",          href: "/" },
  { label: "Internships",   href: "/applicant/internships" },
  { label: "My Matches",    href: "/applicant/matches" },
  { label: "Applications", href: "/applicant/applications" },
  { label: "Allocations",  href: "/applicant/allocations" },
] as const;

export const SECTORS = [
  "Technology",
  "Finance",
  "Healthcare",
  "Education",
  "Manufacturing",
  "Retail",
  "Agriculture",
  "Government",
  "NGO / Non-profit",
  "Media & Entertainment",
  "Real Estate",
  "Logistics",
  "Other",
] as const;

export const STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry", "Chandigarh",
] as const;

export const STATES_AND_DISTRICTS: Record<string, string[]> = {
  "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar"],
  "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
  "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru"],
  "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
  "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
  "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Prayagraj", "Noida"],
  "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
  "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri"],
  "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad"],
  "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],
};

export const SKILL_CATEGORIES: Record<string, string[]> = {
  "Programming": ["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust"],
  "Web Development": ["React", "Next.js", "Vue.js", "Angular", "Node.js", "Django", "FastAPI"],
  "Data & ML": ["Machine Learning", "Data Analysis", "SQL", "TensorFlow", "PyTorch", "Pandas"],
  "Cloud & DevOps": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "CI/CD", "Terraform"],
  "Design": ["Figma", "UI/UX Design", "Adobe XD", "Canva"],
  "Business": ["Project Management", "Business Analysis", "Marketing", "Finance", "Excel"],
  "Communication": ["Technical Writing", "Public Speaking", "Team Collaboration"],
};

export const EDUCATION_LEVELS = [
  "High School",
  "Diploma",
  "Bachelor's Degree",
  "Master's Degree",
  "PhD",
  "Other",
] as const;

export const CATEGORIES = [
  "Engineering",
  "Management",
  "Arts & Humanities",
  "Science",
  "Commerce",
  "Law",
  "Medical",
  "Agriculture",
  "Design",
  "Other",
] as const;

export const API_ROUTES = {
  AUTH: {
    LOGIN:    `${BASE}/auth/login`,
    LOGOUT:   `${BASE}/auth/logout`,
    REFRESH:  `${BASE}/auth/refresh`,
    ME:       `${BASE}/auth/me`,
    REGISTER: `${BASE}/auth/register`,
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
    DETAIL: (id: string) => `${BASE}/opportunities/${id}`,
    CREATE: `${BASE}/opportunities`,
    UPDATE: (id: string) => `${BASE}/opportunities/${id}`,
    DELETE: (id: string) => `${BASE}/opportunities/${id}`,
  },
  MATCHING: {
    TRIGGER:       `${BASE}/matching/trigger`,
    BATCH_TRIGGER: `${BASE}/matching/batch-trigger`,
    RESULTS:       `${BASE}/matching/results`,
    BY_ID:         (id: string) => `${BASE}/matching/${id}`,
    MY_MATCHES:    `${BASE}/matching/me`,
    MATCHES:       `${BASE}/matching/matches`,
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
