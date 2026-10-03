import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearToken, setToken } from "../state/session";
import { ApiError, apiRequest } from "./client";

describe("apiRequest", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearToken();
  });

  it("E1S1_resolves_with_the_parsed_body_on_success", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ token: "t1" }), { status: 200 })
    );

    const result = await apiRequest<{ token: string }>("/api/auth/login", { auth: false });
    expect(result).toEqual({ token: "t1" });
  });

  it("E1S1_throws_ApiError_with_code_and_message_on_failure", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(
        JSON.stringify({ error: { code: "INVALID_CREDENTIALS", message: "Nope" } }),
        { status: 401 }
      )
    );

    await expect(apiRequest("/api/auth/login", { auth: false })).rejects.toMatchObject(
      new ApiError("INVALID_CREDENTIALS", "Nope")
    );
  });

  it("E1S2_sends_the_bearer_token_when_auth_is_true", async () => {
    setToken("my-token");
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify([]), { status: 200 }));

    await apiRequest("/api/tickets");

    const [, options] = vi.mocked(fetch).mock.calls[0];
    expect((options?.headers as Record<string, string>).Authorization).toBe("Bearer my-token");
  });
});
