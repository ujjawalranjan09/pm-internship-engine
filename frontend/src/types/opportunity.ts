export interface Opportunity {
  id: string;
  employerId: string;
  employerName: string;
  title: string;
  description: string;
  sector: string;
  location: string;
  state: string;
  district: string;
  stipend: number;
  duration: number;
  capacity: number;
  filledSlots: number;
  requiredSkills: string[];
  eligibilityCriteria: {
    minEducation: string;
    minPercentage?: number;
    allowedCategories?: string[];
    maxAge?: number;
  };
  startDate: string;
  endDate: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface OpportunityListItem {
  id: string;
  title: string;
  employerName: string;
  sector: string;
  location: string;
  stipend: number;
  duration: number;
  capacity: number;
  filledSlots: number;
  requiredSkills: string[];
  isActive: boolean;
  matchScore?: number;
  description?: string;
  state?: string;
  workMode?: string;
  durationMonths?: number;
  createdAt?: string;
}

export interface CreateOpportunityRequest {
  title: string;
  description: string;
  sector: string;
  location: string;
  state: string;
  district: string;
  stipend: number;
  duration: number;
  capacity: number;
  requiredSkills: string[];
  eligibilityCriteria: {
    minEducation: string;
    minPercentage?: number;
    allowedCategories?: string[];
    maxAge?: number;
  };
  startDate: string;
  endDate: string;
}

export interface OpportunityFilter {
  sector?: string;
  state?: string;
  location?: string;
  skills?: string[];
  minStipend?: number;
  maxStipend?: number;
  isActive?: boolean;
}
