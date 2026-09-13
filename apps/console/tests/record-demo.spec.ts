import { test } from "@playwright/test";

test("record only an evidence-linked run", async ({ page }) => {
  const runId = process.env.DOVET_RECORD_RUN_ID;
  if (!runId) test.skip(true, "DOVET_RECORD_RUN_ID is required; synthetic UI animation is forbidden");
  await page.goto(`/runs/${runId}`);
  await page.waitForSelector('[data-testid="verified-receipt"]', { timeout: 10 * 60 * 1000 });
});

