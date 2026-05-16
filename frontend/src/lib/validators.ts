import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export const registerSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(["candidate", "employer", "admin"]),
});

export const profileSchema = z.object({
  name: z.string().min(2),
  phone: z.string().optional(),
  state: z.string(),
  district: z.string(),
  category: z.string(),
  education: z.string(),
  skills: z.array(z.string()),
  sectorPreferences: z.array(z.string()),
});

export const opportunitySchema = z.object({
  title: z.string().min(5),
  description: z.string().min(20),
  sector: z.string(),
  location: z.string(),
  state: z.string(),
  district: z.string(),
  stipend: z.number().min(0),
  duration: z.number().min(1),
  capacity: z.number().min(1),
  requiredSkills: z.array(z.string()),
  startDate: z.string(),
  endDate: z.string(),
});

export const feedbackSchema = z.object({
  rating: z.number().min(1).max(5),
  comment: z.string().optional(),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type ProfileInput = z.infer<typeof profileSchema>;
export type OpportunityInput = z.infer<typeof opportunitySchema>;
export type FeedbackInput = z.infer<typeof feedbackSchema>;
