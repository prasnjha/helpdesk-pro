import { afterEach, describe, expect, it } from "vitest";

import { clearToken, clearSession, getRole, getToken, getUsername, setSession, setToken } from "./session";

describe("session", () => {
  afterEach(() => {
    clearToken();
    clearSession();
  });

  it("E1S2_stores_and_returns_the_token", () => {
    setToken("abc123");
    expect(getToken()).toBe("abc123");
  });

  it("E1S2_clear_removes_the_token", () => {
    setToken("abc123");
    clearToken();
    expect(getToken()).toBeNull();
  });

  it("E6S1_stores_and_returns_role_and_username", () => {
    setSession("tok", "agent", "agent1");
    expect(getToken()).toBe("tok");
    expect(getRole()).toBe("agent");
    expect(getUsername()).toBe("agent1");
  });

  it("E6S1_clearSession_removes_role_and_username_too", () => {
    setSession("tok", "admin", "admin1");
    clearSession();
    expect(getToken()).toBeNull();
    expect(getRole()).toBeNull();
    expect(getUsername()).toBeNull();
  });
});
