import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["apps/**/test/unit/**/*.spec.ts"],
    environment: "node",
  },
});
