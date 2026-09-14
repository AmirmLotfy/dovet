import { expect, test, type Browser, type Page } from "@playwright/test";
import path from "node:path";

const outputRoot = process.env.DOVET_GALLERY_OUTPUT_DIR;
const pairNonce = process.env.DOVET_PAIR_NONCE;
const siteUrl = process.env.DOVET_GALLERY_SITE_URL ?? "https://dovet.site";
const repositoryUrl = "https://github.com/AmirmLotfy/dovet";
const releaseUrl = "https://github.com/AmirmLotfy/dovet/releases/tag/v0.1.6";
const ciUrl = "https://github.com/AmirmLotfy/dovet/actions/runs/34794903584";

test.skip(
  process.env.DOVET_CAPTURE_SUBMISSION_GALLERY !== "approved" || !outputRoot || !pairNonce,
  "submission gallery capture is opt-in",
);
test.setTimeout(180_000);

async function settle(page: Page) {
  await page.waitForLoadState("domcontentloaded");
  await page.evaluate(async () => {
    await document.fonts.ready;
  });
  await page.waitForTimeout(500);
}

async function capture(page: Page, name: string) {
  if (!outputRoot) throw new Error("DOVET_GALLERY_OUTPUT_DIR is required");
  await settle(page);
  await page.screenshot({
    path: path.join(outputRoot, name),
    animations: "disabled",
    caret: "hide",
  });
}

async function desktopPage(browser: Browser) {
  const context = await browser.newContext({ viewport: { width: 1800, height: 1200 } });
  return { context, page: await context.newPage() };
}

async function captureSection(page: Page, selector: string, name: string) {
  const section = page.locator(selector);
  await expect(section).toBeVisible();
  await section.evaluate((element) => element.scrollIntoView({ block: "center" }));
  await page.waitForTimeout(350);
  await capture(page, name);
}

test("capture real submission gallery", async ({ browser }) => {
  if (!pairNonce) throw new Error("DOVET_PAIR_NONCE is required");

  const local = await desktopPage(browser);
  const paired = await local.context.request.post("http://127.0.0.1:4317/api/v1/session/pair", {
    data: { nonce: pairNonce },
  });
  expect(paired.ok()).toBeTruthy();
  await local.page.goto("http://127.0.0.1:4317/", { waitUntil: "domcontentloaded" });
  await expect(local.page.getByText("Local service connected")).toBeVisible();
  await expect(local.page.getByRole("heading", { name: "Work", exact: true })).toBeVisible();
  await capture(local.page, "01-console-work-real.png");

  await local.page.getByRole("button", { name: "Connections" }).click();
  await expect(local.page.getByText("owned start, interruption and checkpoint verified")).toBeVisible();
  await expect(local.page.getByText("authenticated discovery passes; invocation is not allowed")).toBeVisible();
  await capture(local.page, "02-console-connections-real.png");
  await local.context.close();

  const site = await desktopPage(browser);
  await site.page.goto(siteUrl);
  await expect(site.page.getByRole("heading", { name: /Keep the work/ })).toBeVisible();
  await capture(site.page, "03-public-home-real.png");
  await captureSection(site.page, ".evidence-band", "04-public-evidence-real.png");
  await captureSection(site.page, ".product-proof", "05-product-receipt-fixture-disclosed.png");

  await site.page.goto(`${siteUrl}/judges`);
  await expect(site.page.getByRole("heading", { name: "Judge the evidence path." })).toBeVisible();
  await captureSection(site.page, '[data-film="proof"]', "06-managed-interruption-evidence-real.png");
  await captureSection(site.page, '[data-film="architecture"]', "07-architecture-page-real.png");
  await captureSection(site.page, '[data-film="blocker"]', "08-provider-blocker-real.png");

  await site.page.goto(`${siteUrl}/docs/security`);
  await expect(site.page.getByRole("heading", { name: "Data and control boundaries." })).toBeVisible();
  await capture(site.page, "09-security-boundaries-real.png");
  await site.context.close();

  const publicProof = await desktopPage(browser);
  await publicProof.page.goto(repositoryUrl);
  await expect(publicProof.page.getByRole("link", { name: "dovet", exact: true }).first()).toBeVisible();
  await expect(publicProof.page.getByText("Public", { exact: true })).toBeVisible();
  await capture(publicProof.page, "10-public-repository-real.png");

  await publicProof.page.goto(releaseUrl);
  await expect(publicProof.page.getByRole("heading", { name: "Dovet v0.1.6", exact: true })).toBeVisible();
  await capture(publicProof.page, "11-public-release-real.png");

  await publicProof.page.goto(ciUrl);
  await expect(publicProof.page.getByText("CI", { exact: true }).first()).toBeVisible();
  await capture(publicProof.page, "12-hosted-ci-pass-real.png");
  await publicProof.context.close();

  const mobileContext = await browser.newContext({
    viewport: { width: 1200, height: 1800 },
    isMobile: true,
    deviceScaleFactor: 1,
  });
  const mobile = await mobileContext.newPage();
  await mobile.goto(siteUrl);
  await expect(mobile.getByRole("heading", { name: /Keep the work/ })).toBeVisible();
  await capture(mobile, "13-public-home-mobile-real.png");
  await mobileContext.close();
});
