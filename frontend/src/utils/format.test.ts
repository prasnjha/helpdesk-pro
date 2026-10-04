import { describe, expect, it } from "vitest";

import { formatDate, formatDateTime } from "./format";

describe("formatDate", () => {
  it("formats an ISO timestamp as a UTC calendar date", () => {
    expect(formatDate("2026-01-05T23:30:00Z")).toBe("5 Jan 2026");
  });

  it("returns the raw value when it is not a parseable date", () => {
    expect(formatDate("x")).toBe("x");
  });
});

describe("formatDateTime", () => {
  it("formats an ISO timestamp as a UTC date and 24h time", () => {
    expect(formatDateTime("2026-01-05T09:07:00Z")).toBe("5 Jan 2026, 09:07 UTC");
  });

  it("returns the raw value when it is not a parseable date", () => {
    expect(formatDateTime("not-a-date")).toBe("not-a-date");
  });
});
