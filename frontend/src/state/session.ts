// Token kept in memory, with a try/catch-guarded sessionStorage copy so a
// page refresh during development does not lose the session.

const STORAGE_KEY = "helpdesk_pro_token";

let currentToken: string | null = null;

export function setToken(token: string): void {
  currentToken = token;
  try {
    sessionStorage.setItem(STORAGE_KEY, token);
  } catch {
    // sessionStorage unavailable (private mode, etc.) — in-memory still works.
  }
}

export function getToken(): string | null {
  if (currentToken) return currentToken;
  try {
    currentToken = sessionStorage.getItem(STORAGE_KEY);
  } catch {
    // ignore
  }
  return currentToken;
}

export function clearToken(): void {
  currentToken = null;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
