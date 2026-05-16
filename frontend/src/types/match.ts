export interface Match {
  id: string;
  candidateId: string;
  candidateName: string;
  opportunityId: string;
  opportunityTitle: string;
  employerName: string;
  overallScore: number;
  skillScore: number;
  locationScore: number;
  educationScore: number;
  preferenceScore: number;
  fairnessScore: number;
  explanation: string;
  factors: MatchFactor[];
  createdAt: string;
}

export interface MatchFactor {
  name: string;
  weight: number;
  score: number;
  description: string;
}

export interface MatchRecommendation {
  opportunityId: string;
  title: string;
  employerName: string;
  sector: string;
  location: string;
  stipend: number;
  matchScore: number;
  explanation: string;
  topFactors: MatchFactor[];
}
