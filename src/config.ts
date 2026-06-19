export const API_BASE_URL =
  (import.meta as ImportMeta & { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";

export const MATTER_NUMBER = "LX-MIG-2026-001";

export const SUPABASE_URL =
  (import.meta as ImportMeta & { env?: { VITE_SUPABASE_URL?: string } }).env?.VITE_SUPABASE_URL ?? "";

export const SUPABASE_PUBLISHABLE_KEY =
  (import.meta as ImportMeta & { env?: { VITE_SUPABASE_PUBLISHABLE_KEY?: string } }).env
    ?.VITE_SUPABASE_PUBLISHABLE_KEY ?? "";
