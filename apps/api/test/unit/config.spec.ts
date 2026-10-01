import { describe, expect, it } from "vitest";
import { parseConfig } from "../../src/config.js";

describe("API configuration", () => {
  it("accepts the required database URL and applies local defaults", () => {
    expect(parseConfig({ DATABASE_URL: "postgres://user:pass@localhost:5432/database" })).toEqual({
      DATABASE_URL: "postgres://user:pass@localhost:5432/database",
      HOST: "127.0.0.1",
      PORT: 3000,
    });
  });

  it("fails clearly when the database URL is missing", () => {
    expect(() => parseConfig({})).toThrow(/Invalid API configuration.*DATABASE_URL/s);
  });
});
