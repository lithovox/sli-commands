import { defineConfig, devices } from "@playwright/test";

// not 4173, the port of a vite preview that may be running already
const PORT = 4183;

export default defineConfig({
  testDir: "e2e",
  // Python starts once per page, give the first load some time
  timeout: 90_000,
  expect: { timeout: 30_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: `http://localhost:${PORT}/`,
    ...devices["Desktop Chrome"],
  },
  // the production build, served with the security headers of the published site
  webServer: {
    command: `npm run build && npx vite preview --port ${PORT} --strictPort`,
    url: `http://localhost:${PORT}/`,
    // always a fresh build, never an old server that happens to run on the port
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
