import { afterEach, describe, expect, it } from "vitest";

import { clearToken, getToken, setToken } from "./session";

describe("session", () => {
  afterEach(() => {
    clearToken();
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
});
