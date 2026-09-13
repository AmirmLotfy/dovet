import { test } from "@playwright/test";

test.skip(
  !process.env.DOVET_RECORD_RUN_ID || !process.env.DOVET_PAIR_URL,
  "A verified run and one-use local pairing URL are required",
);

test("record only an evidence-linked run", async ({ page }) => {
  const runId = process.env.DOVET_RECORD_RUN_ID;
  const pairUrl = process.env.DOVET_PAIR_URL;
  if (!runId || !pairUrl) throw new Error("recording prerequisites are missing");
  await page.goto(pairUrl);
  await page.getByText("Local service connected").waitFor();
  await page.goto(`/runs/${runId}`);
  await page.waitForSelector('[data-testid="verified-receipt"]', { timeout: 10 * 60 * 1000 });
  const events = page.locator(".evidence-rail li");
  for (let index = 0; index < await events.count(); index += 1) {
    await events.nth(index).scrollIntoViewIfNeeded();
    await page.waitForTimeout(650);
  }
  await page.getByRole("heading", { name: "Receipt" }).scrollIntoViewIfNeeded();
  await page.waitForTimeout(1200);
});
