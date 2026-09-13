import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("renders an honest empty state with no serious accessibility violations", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Work" })).toBeVisible();
  await expect(page.getByText("No protected work yet")).toBeVisible();
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter((violation) => ["serious", "critical"].includes(violation.impact ?? ""))).toEqual([]);
});

test("critical navigation remains available on a narrow screen", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Needs you" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Connections" })).toBeVisible();
});

