import { z } from "zod";

export const loginSchema = z.object({
  email:    z.string().email("Enter a valid email"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

export const registerSchema = z
  .object({
    name:            z.string().min(2, "Name must be at least 2 characters"),
    email:           z.string().email("Enter a valid email"),
    password:        z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
    role:            z.enum(["applicant", "employer", "admin"]).default("applicant"),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export const profileSchema = z.object({
  name:                z.string().min(2).optional(),
  phone:               z.string().optional(),
  state:               z.string().optional(),
  district:            z.string().optional(),
  sector:              z.string().optional(),
  sectors:             z.array(z.string()).optional(),
  preferredLocations:  z.array(z.string()).optional(),
  gender:              z.string().optional(),
  category:            z.string().optional(),
  educationLevel:      z.string().optional(),
  pincode:             z.string().optional(),
  address:             z.string().optional(),
  dateOfBirth:         z.string().optional(),
  skills:              z.array(z.string()).optional(),
  bio:                 z.string().max(500).optional(),
});

export const internshipSchema = z.object({
  title:          z.string().min(5, "Title must be at least 5 characters"),
  description:    z.string().min(20, "Description must be at least 20 characters"),
  sector:         z.string().min(1, "Select a sector"),
  state:          z.string().min(1, "Select a state"),
  district:       z.string().optional(),
  workMode:       z.enum(["remote", "onsite", "hybrid"]).default("onsite"),
  durationMonths: z.number().min(1).max(24),
  stipend:        z.number().min(0).optional(),
  skills:         z.array(z.string()).optional(),
  educationLevel: z.string().optional(),
  category:       z.string().optional(),
  openings:       z.number().min(1).default(1),
});

export const feedbackSchema = z.object({
  rating:    z.number().min(1).max(5),
  comment:   z.string().max(1000).optional(),
  recommend: z.boolean().optional(),
});

export type LoginInput        = z.infer<typeof loginSchema>;
export type RegisterInput     = z.infer<typeof registerSchema>;
export type ProfileInput      = z.infer<typeof profileSchema>;
export type InternshipInput   = z.infer<typeof internshipSchema>;
export type FeedbackInput     = z.infer<typeof feedbackSchema>;

// Aliases for form data types
export type LoginFormData = LoginInput;
export type RegisterFormData = RegisterInput;
export type ProfileFormData = ProfileInput;
export type FeedbackFormData = FeedbackInput;
export type OpportunityFormData = InternshipInput;
