// Fetch wrapper: bearer token, parses {error: {code, message}} (frontend/CLAUDE.md).

import { getToken } from "../state/session";
import type { ErrorEnvelope } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export async function apiRequest<TResponse>(
  path: string,
  options: { method?: string; body?: unknown; auth?: boolean } = {}
): Promise<TResponse> {
  const { method = "GET", body, auth = true } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as TResponse;
  }

  const data = (await response.json()) as TResponse | ErrorEnvelope;

  if (!response.ok) {
    const envelope = data as ErrorEnvelope;
    throw new ApiError(envelope.error.code, envelope.error.message);
  }

  return data as TResponse;
}
