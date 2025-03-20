import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const frontendUrl = import.meta.env.VITE_FRONTEND_URL
export const backendUrl = import.meta.env.VITE_BACKEND_URL