export interface Education {
  id: string;
  degree: string;
  institution: string;
  fieldOfStudy: string;
  startYear: number;
  endYear?: number;
  percentage?: number;
  cgpa?: number;
  isCurrent: boolean;
}

export interface Skill {
  name: string;
  proficiency: "beginner" | "intermediate" | "advanced" | "expert";
}

export interface CandidateProfile {
  id: string;
  userId: string;
  name: string;
  email: string;
  phone?: string;
  dateOfBirth?: string;
  gender?: string;
  category?: string;
  state: string;
  district: string;
  pincode?: string;
  address?: string;
  education: Education[];
  skills: Skill[];
  sectors: string[];
  preferredLocations: string[];
  resumeUrl?: string;
  profileCompletion: number;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CandidateListItem {
  id: string;
  name: string;
  email: string;
  state: string;
  district: string;
  education: string;
  skills: string[];
  profileCompletion: number;
  matchScore?: number;
  category?: string;
}

export interface CandidateFilter {
  state?: string;
  district?: string;
  category?: string;
  skills?: string[];
  education?: string;
  minProfileCompletion?: number;
}
