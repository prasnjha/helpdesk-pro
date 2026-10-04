// Token, role and username kept in memory, with a try/catch-guarded
// sessionStorage copy so a page refresh during development does not lose the
// session. Role/username were added in E6-S1/E6-S2 so AuthGuard can route by
// role without an extra request (api-contracts.md, POST /api/auth/login).

export type Role = "customer" | "agent" | "admin";

const TOKEN_KEY = "helpdesk_pro_token";
const ROLE_KEY = "helpdesk_pro_role";
const USERNAME_KEY = "helpdesk_pro_username";

let currentToken: string | null = null;
let currentRole: string | null = null;
let currentUsername: string | null = null;

function readStorage(key: string): string | null {
  try {
    return sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string): void {
  try {
    sessionStorage.setItem(key, value);
  } catch {
    // sessionStorage unavailable (private mode, etc.) — in-memory still works.
  }
}

function removeStorage(key: string): void {
  try {
    sessionStorage.removeItem(key);
  } catch {
    // ignore
  }
}

export function setToken(token: string): void {
  currentToken = token;
  writeStorage(TOKEN_KEY, token);
}

export function getToken(): string | null {
  if (currentToken) return currentToken;
  currentToken = readStorage(TOKEN_KEY);
  return currentToken;
}

export function clearToken(): void {
  currentToken = null;
  removeStorage(TOKEN_KEY);
}

export function setSession(token: string, role: string, username: string): void {
  setToken(token);
  currentRole = role;
  currentUsername = username;
  writeStorage(ROLE_KEY, role);
  writeStorage(USERNAME_KEY, username);
}

export function getRole(): Role | null {
  if (currentRole) return currentRole as Role;
  currentRole = readStorage(ROLE_KEY);
  return currentRole as Role | null;
}

export function getUsername(): string | null {
  if (currentUsername) return currentUsername;
  currentUsername = readStorage(USERNAME_KEY);
  return currentUsername;
}

export function clearSession(): void {
  clearToken();
  currentRole = null;
  currentUsername = null;
  removeStorage(ROLE_KEY);
  removeStorage(USERNAME_KEY);
}
