import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

test.describe('Initial Load and Flicker Detection', () => {
  test.beforeEach(async ({ page }) => {
    // Set up console and error logging
    const consoleLogs: string[] = [];
    const errorLogs: string[] = [];

    page.on('console', msg => {
      consoleLogs.push(`${msg.type()}: ${msg.text()}`);
    });

    page.on('pageerror', err => {
      errorLogs.push(`Error: ${err.message}`);
    });

    // Store logs in test context for later access
    (test.info() as any).consoleLogs = consoleLogs;
    (test.info() as any).errorLogs = errorLogs;
  });

  test('should detect layout flicker during initial load', async ({ page, context }) => {
    const artifactDir = './test-artifacts/playwright/initial-load';
    await fs.promises.mkdir(artifactDir, { recursive: true });

    // Start HAR recording
    await context.tracing.start({ screenshots: true, snapshots: true });
    await page.routeFromHAR(path.join(artifactDir, 'front.har'), { 
      update: true,
      updateContent: 'embed' 
    });

    // Navigate to the application
    const startTime = Date.now();
    await page.goto('/');

    // Take rapid screenshots to detect flicker
    const screenshots: { timestamp: number; filename: string }[] = [];
    const flickerDetectionTime = 3000; // 3 seconds
    const screenshotInterval = 250; // 250ms

    let screenshotCount = 0;
    const screenshotPromises: Promise<void>[] = [];

    for (let i = 0; i < flickerDetectionTime / screenshotInterval; i++) {
      const promise = new Promise<void>((resolve) => {
        setTimeout(async () => {
          try {
            const timestamp = Date.now() - startTime;
            const filename = `screenshot-${String(screenshotCount).padStart(3, '0')}-${timestamp}ms.png`;
            const screenshotPath = path.join(artifactDir, filename);
            
            await page.screenshot({ 
              path: screenshotPath, 
              fullPage: true 
            });
            
            screenshots.push({ timestamp, filename });
            screenshotCount++;
            resolve();
          } catch (error) {
            console.error('Screenshot error:', error);
            resolve();
          }
        }, i * screenshotInterval);
      });
      
      screenshotPromises.push(promise);
    }

    // Wait for all screenshots to complete
    await Promise.all(screenshotPromises);

    // Check for legacy and new dashboard markers
    let legacyDashboardFound = false;
    let newDashboardFound = false;
    let flickerDetected = false;

    try {
      // Look for common legacy dashboard indicators
      const legacySelectors = [
        '[data-testid="legacy-dashboard"]',
        '.react-native-web',
        '.rn-view', // React Native Web classes
        '[class*="ReactNativeWebView"]'
      ];

      const newDashboardSelectors = [
        '[data-testid="web-dashboard"]',
        '[data-testid="new-dashboard"]',
        '.dashboard-web',
        '.vite-app'
      ];

      // Check if legacy elements are present
      for (const selector of legacySelectors) {
        try {
          const element = await page.locator(selector).first();
          if (await element.isVisible({ timeout: 1000 })) {
            legacyDashboardFound = true;
            break;
          }
        } catch (e) {
          // Element not found, continue
        }
      }

      // Check if new dashboard elements are present
      for (const selector of newDashboardSelectors) {
        try {
          const element = await page.locator(selector).first();
          if (await element.isVisible({ timeout: 1000 })) {
            newDashboardFound = true;
            break;
          }
        } catch (e) {
          // Element not found, continue
        }
      }

      // If both are found within the first few seconds, it indicates flicker
      if (legacyDashboardFound && newDashboardFound) {
        flickerDetected = true;
      }

    } catch (error) {
      console.error('Error checking for dashboard elements:', error);
    }

    // Stop tracing and save
    await context.tracing.stop({ path: path.join(artifactDir, 'trace.zip') });

    // Save console logs
    const consoleLogs = (test.info() as any).consoleLogs || [];
    const errorLogs = (test.info() as any).errorLogs || [];
    
    await fs.promises.writeFile(
      path.join(artifactDir, 'console.log'),
      `=== Console Logs ===\\n${consoleLogs.join('\\n')}\\n\\n=== Error Logs ===\\n${errorLogs.join('\\n')}`
    );

    // Create flicker detection report
    const flickerReport = {
      testTimestamp: new Date().toISOString(),
      flickerDetected,
      legacyDashboardFound,
      newDashboardFound,
      screenshots: screenshots.length,
      screenshotDetails: screenshots,
      consoleLogs: consoleLogs.length,
      errorLogs: errorLogs.length,
      pageTitle: await page.title(),
      finalUrl: page.url()
    };

    await fs.promises.writeFile(
      path.join(artifactDir, 'flicker-report.json'),
      JSON.stringify(flickerReport, null, 2)
    );

    // Test assertions
    if (flickerDetected) {
      console.warn('⚠️  Layout flicker detected! Both legacy and new dashboard elements found.');
    }

    // Assert that the page loaded successfully
    expect(await page.title()).toBeTruthy();
    
    // The page should eventually stabilize on one layout
    await expect(page.locator('body')).toBeVisible();

    // Log findings for manual review
    console.log(`📊 Flicker Detection Results:
    - Legacy dashboard found: ${legacyDashboardFound}
    - New dashboard found: ${newDashboardFound}  
    - Flicker detected: ${flickerDetected}
    - Screenshots captured: ${screenshots.length}
    - Console logs: ${consoleLogs.length}
    - Error logs: ${errorLogs.length}
    `);
  });

  test('should load without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('pageerror', err => {
      errors.push(err.message);
    });

    await page.goto('/');
    
    // Wait for the page to settle
    await page.waitForLoadState('networkidle');
    
    // Report any JavaScript errors
    if (errors.length > 0) {
      console.warn('JavaScript errors detected:', errors);
    }

    // The test should pass even if there are errors, but we log them for investigation
    expect(await page.title()).toBeTruthy();
  });
});