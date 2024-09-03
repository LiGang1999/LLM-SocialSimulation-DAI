import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import axios from 'axios'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const apiPort = import.meta.env.VITE_API_PORT;

export const api = axios.create({
  baseURL: `${apiBaseUrl}:${apiPort}`,
})
