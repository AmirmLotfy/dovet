import { defineConfig, devices } from "@playwright/test";

const recordingBaseUrl = process.env.DOVET_RECORD_BASE_URL;

export default defineConfig({
  testDir: "./tests",
  outputDir: process.env.DOVET_RECORD_OUTPUT_DIR ?? "test-results",
  use: { baseURL: recordingBaseUrl ?? "http://127.0.0.1:4318", trace: "retain-on-failure" },
  webServer: recordingBaseUrl ? undefined : { command: "pnpm dev", url: "http://127.0.0.1:4318", reuseExistingServer: true },
  projects: [
    { name: "desktop", testIgnore: /record-(demo|local-story)\.spec\.ts/, use: { ...devices["Desktop Chrome"], channel: "chrome", viewport: { width: 1440, height: 1000 } } },
    { name: "mobile", testIgnore: /record-(demo|local-story)\.spec\.ts/, use: { ...devices["Pixel 7"], channel: "chrome", viewport: { width: 390, height: 844 } } },
    { name: "record", testMatch: /record-demo\.spec\.ts/, use: { ...devices["Desktop Chrome"], channel: "chrome", viewport: { width: 1920, height: 1080 }, video: { mode: "on", size: { width: 1920, height: 1080 } } } },
    { name: "story", testMatch: /record-local-story\.spec\.ts/, use: { ...devices["Desktop Chrome"], channel: "chrome", viewport: { width: 1920, height: 1080 }, video: "off" } },
  ],
});
