import { defineConfig, devices } from '@playwright/test';
import mcpConfig from './playwright-mcp-config.json';

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// require('dotenv').config();

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './tests/e2e',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: mcpConfig.testingConfig.retries || (process.env.CI ? 2 : 0),
  /* Opt out of parallel tests on CI. */
  workers: mcpConfig.testingConfig.parallel ? undefined : 1,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: './test-artifacts/playwright/html-report' }],
    ['json', { outputFile: './test-artifacts/playwright/results.json' }],
    ['junit', { outputFile: './test-artifacts/playwright/junit.xml' }]
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: mcpConfig.testingConfig.baseUrl,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',

    /* Global timeout for actions */
    actionTimeout: mcpConfig.testingConfig.timeout,

    /* Configure artifacts directory */
    // Store traces, screenshots, videos in test-artifacts
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: mcpConfig.browserConfig.devices.desktop.viewport
      },
    },

    {
      name: 'firefox-desktop',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: mcpConfig.browserConfig.devices.desktop.viewport
      },
    },

    {
      name: 'webkit-desktop',
      use: { 
        ...devices['Desktop Safari'],
        viewport: mcpConfig.browserConfig.devices.desktop.viewport
      },
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        viewport: mcpConfig.browserConfig.devices.mobile.viewport
      },
    },
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
        viewport: mcpConfig.browserConfig.devices.mobile.viewport
      },
    },

    /* Test against tablet viewports */
    {
      name: 'Tablet',
      use: { 
        ...devices['iPad'],
        viewport: mcpConfig.browserConfig.devices.tablet.viewport
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run dev --workspace @propertypro/web',
  //   url: mcpConfig.testingConfig.baseUrl,
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120 * 1000, // 2 minutes
  //   cwd: './client',
  // },

  // Global test configuration
  timeout: mcpConfig.testingConfig.timeout,
  expect: {
    timeout: 10000, // 10 seconds for assertions
    toMatchSnapshot: { threshold: 0.2 }, // Allow for small visual differences
  },

  // Output directories for artifacts
  outputDir: './test-artifacts/playwright/output',
});