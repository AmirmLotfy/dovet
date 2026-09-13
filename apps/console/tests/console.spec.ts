import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("renders an honest empty state with no serious accessibility violations", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Work", exact: true })).toBeVisible();
  await expect(page.getByText("No protected work yet")).toBeVisible();
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter((violation) => ["serious", "critical"].includes(violation.impact ?? ""))).toEqual([]);
});

test("critical navigation remains available on a narrow screen", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Needs you" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Connections" })).toBeVisible();
});

test("renders a validated recovery receipt as an accessible evidence rail", async ({ page }) => {
  const digest = "a".repeat(64);
  await page.route("**/health", async (route) => route.fulfill({
    json: { version: "0.1.0", readiness: "ready", capability_digest: digest, capabilities: [] },
  }));
  await page.route("**/api/v1/status", async (route) => route.fulfill({
    json: { service: "connected", work: [], needs_you: [], history: [], message: "" },
  }));
  await page.route("**/api/v1/runs/vertical_run", async (route) => route.fulfill({
    json: {
      run_id: "vertical_run",
      title: "Recover CSV importer",
      project: "Importer fixture",
      status: "verified",
      source: "live_receipt",
      recorded_at: "2026-09-13T02:00:00Z",
      release_commit: "b".repeat(40),
      model_id: "amazon.nova-micro-v1:0",
      codex_thread_id: "thread_1",
      codex_turn_id: "turn_1",
      initial_snapshot_sha256: digest,
      final_snapshot_sha256: digest,
      changed_paths: ["src/parcel_import/importer.py"],
      verification: {
        status: "passed",
        snapshot_sha256: digest,
        suite_digest: digest,
        output_sha256: digest,
        duration_ms: 42,
      },
      events: [
        {
          id: "ev_interrupted",
          seq: 1,
          title: "Managed Codex worker interrupted",
          detail: "Owned turn stopped during an intentional demonstration fault.",
          knowledge_kind: "observed",
        },
        {
          id: "ev_verified",
          seq: 2,
          title: "Independent protected checks passed",
          detail: "The protected suite passed on the recovered snapshot.",
          knowledge_kind: "verified",
        },
      ],
    },
  }));

  await page.goto("/runs/vertical_run");

  await expect(page.getByTestId("verified-receipt")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Evidence rail" })).toBeVisible();
  await expect(page.getByText("live receipt", { exact: false })).toBeVisible();
  if (process.env.DOVET_CAPTURE_UI_FIXTURE === "approved") {
    await page.screenshot({
      path: "../../artifacts/ui-evidence-rail-fixture.png",
      fullPage: true,
    });
  }
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter((violation) => ["serious", "critical"].includes(violation.impact ?? ""))).toEqual([]);
});
