import * as z from "zod";
export const registerSchema = z.object({
  // name: z.string().trim().min(2, "Name must be at least 2 characters"),
  email: z.email("Invalid email address").trim(),
  password: z.string().trim().min(8, "Password must be at least 8 characters"),
});

export type RegisterFormValues = z.infer<typeof registerSchema>;
export const loginSchema = z.object({
  email: z.email("Invalid email address").trim(),
  password: z.string().trim().min(8, "Password must be at least 8 characters"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
