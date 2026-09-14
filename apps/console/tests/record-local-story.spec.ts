import { expect, test, type Browser, type Page } from "@playwright/test";
import path from "node:path";

const outputRoot = process.env.DOVET_STORY_OUTPUT_DIR;
const siteUrl = process.env.DOVET_STORY_SITE_URL ?? "http://127.0.0.1:4320";
const consoleUrl = process.env.DOVET_STORY_CONSOLE_URL ?? "http://127.0.0.1:4318";

test.skip(process.env.DOVET_RECORD_LOCAL_STORY !== "approved" || !outputRoot, "local story recording is opt-in");
test.describe.configure({ mode: "serial" });

async function pause(page: Page, milliseconds = 1800) {
  await page.waitForTimeout(milliseconds);
}

async function reveal(page: Page, selector: string, milliseconds = 2200) {
  await page.locator(selector).evaluate((element) => element.scrollIntoView({ behavior: "smooth", block: "center" }));
  await pause(page, milliseconds);
}

async function record(browser: Browser, name: string, visit: (page: Page) => Promise<void>) {
  if (!outputRoot) throw new Error("DOVET_STORY_OUTPUT_DIR is required");
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: path.join(outputRoot, "raw"), size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();
  const video = page.video();
  await visit(page);
  await context.close();
  if (!video) throw new Error("Playwright did not create a video");
  await video.saveAs(path.join(outputRoot, `${name}.webm`));
}

test("record actual local console", async ({ browser }) => {
  await record(browser, "console", async (page) => {
    await page.goto(consoleUrl);
    await expect(page.getByText("Local service connected")).toBeVisible();
    await pause(page, 2400);
    await page.getByRole("button", { name: "Connections" }).click();
    await expect(page.getByText("owned start, interruption and checkpoint verified")).toBeVisible();
    await pause(page, 3600);
    await page.getByRole("button", { name: "Needs you" }).click();
    await pause(page, 1800);
    await page.getByRole("button", { name: "History" }).click();
    await pause(page, 1800);
    await page.getByRole("button", { name: "Work" }).click();
    await pause(page, 2000);
  });
});

test("record actual marketing site", async ({ browser }) => {
  await record(browser, "marketing", async (page) => {
    await page.goto(siteUrl);
    await expect(page.getByRole("heading", { name: /Keep the work/ })).toBeVisible();
    await pause(page, 2500);
    await reveal(page, ".evidence-band", 2800);
    await reveal(page, ".product-proof", 2800);
    await reveal(page, ".process", 2500);
    await reveal(page, ".boundary", 2500);
    await reveal(page, ".final-cta", 2200);
  });
});

test("record actual evidence and architecture page", async ({ browser }) => {
  await record(browser, "evidence", async (page) => {
    await page.goto(`${siteUrl}/judges`);
    await expect(page.getByRole("heading", { name: "Judge the evidence path." })).toBeVisible();
    await pause(page, 2400);
    await reveal(page, '[data-film="evidence"]', 3200);
    await reveal(page, '[data-film="proof"]', 3000);
    await reveal(page, '[data-film="architecture"]', 3200);
    await reveal(page, '[data-film="blocker"]', 3200);
    await reveal(page, '[data-film="commands"]', 2600);
  });
});

test("record actual provider status", async ({ browser }) => {
  await record(browser, "provider-status", async (page) => {
    await page.goto(`${siteUrl}/demo`);
    await expect(page.getByRole("heading", { name: "Local proof passed. Cloud handoff is blocked." })).toBeVisible();
    await pause(page, 5200);
    await page.getByRole("link", { name: "Read how recovery works" }).click();
    await pause(page, 2600);
    await reveal(page, "h2:nth-of-type(3)", 2200);
  });
});
