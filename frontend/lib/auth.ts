import type { AuthMeResponse } from "@/lib/types";

const TOKEN_KEY = "dpdp_privacyops_access_token";
const USER_KEY = "dpdp_privacyops_current_user";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

export function setCachedAuthUser(auth: AuthMeResponse): void {
  window.localStorage.setItem(USER_KEY, JSON.stringify(auth));
}

export function getCachedAuthUser(): AuthMeResponse | null {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthMeResponse;
  } catch {
    return null;
  }
}
