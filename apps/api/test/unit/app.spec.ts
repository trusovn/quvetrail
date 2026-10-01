import { afterEach, describe, expect, it, vi } from "vitest";
import { buildApp } from "../../src/app.js";

const apps: Awaited<ReturnType<typeof buildApp>>[] = [];

afterEach(async () => {
  await Promise.all(apps.splice(0).map((app) => app.close()));
});

describe("GET /health", () => {
  it("reports a connected database", async () => {
    const app = await buildApp({ checkDatabase: vi.fn().mockResolvedValue(undefined) });
    apps.push(app);

    const response = await app.inject({ method: "GET", url: "/health" });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ status: "ok", database: "connected" });
  });

  it("fails closed when the database cannot be checked", async () => {
    const app = await buildApp({ checkDatabase: vi.fn().mockRejectedValue(new Error("offline")) });
    apps.push(app);

    const response = await app.inject({ method: "GET", url: "/health" });

    expect(response.statusCode).toBe(503);
    expect(response.json()).toEqual({ status: "unavailable", database: "unavailable" });
  });
});
