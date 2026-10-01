import { expect, test } from "@playwright/test";

test("browser reaches the API and database", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Full-stack shell" })).toBeVisible();
  await expect(page.getByText("API and database connected", { exact: true })).toBeVisible();
});
