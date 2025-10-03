import { defineConfig } from '@playwright/test';

// Docker-based config: assumes the frontend is served by the 'frontend' service on port 80
// and tests are executed from the 'e2e' service on the same docker network.
export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  fullyParallel: true,
  reporter: [['list'], ['html', { outputFolder: 'pw-report' }]],
  use: {
    baseURL: 'http://frontend', // service name from docker-compose, port 80
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 390, height: 844 },
  },
  // No webServer here — the app is already running in its own container
});
