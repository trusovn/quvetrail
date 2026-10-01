import { describe, expect, it } from "vitest";

const apiUrl = process.env.API_URL ?? "http://localhost:3000";

describe("deployed API health", () => {
  it("reaches the real PostgreSQL dependency", async () => {
    const response = await fetch(`${apiUrl}/health`);

    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toEqual({ status: "ok", database: "connected" });
  });
});
