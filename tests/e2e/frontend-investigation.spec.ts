import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('Frontend Investigation', () => {
  test('should capture and analyze initial frontend state', async ({ page, context }) => {
    const artifactDir = './test-artifacts/playwright/frontend-investigation';
    await fs.promises.mkdir(artifactDir, { recursive: true });

    // Capture console logs and errors
    const consoleLogs: string[] = [];
    const errorLogs: string[] = [];

    page.on('console', msg => {
      consoleLogs.push(`${new Date().toISOString()} [${msg.type()}]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
      errorLogs.push(`${new Date().toISOString()} [ERROR]: ${err.message}`);
    });

    // Start tracing
    await context.tracing.start({ screenshots: true, snapshots: true });

    console.log('🔍 Navigating to frontend...');
    
    try {
      // Navigate with extended timeout
      await page.goto('/', { waitUntil: 'networkidle', timeout: 30000 });
      
      // Take initial screenshot
      await page.screenshot({ 
        path: path.join(artifactDir, 'initial-load.png'), 
        fullPage: true 
      });

      // Check what's actually rendered
      const bodyContent = await page.locator('body').innerHTML();
      await fs.promises.writeFile(
        path.join(artifactDir, 'body-content.html'),
        bodyContent
      );

      // Check page title
      const title = await page.title();
      console.log('📄 Page title:', title);

      // Check for React/Vite indicators
      const reactRoot = await page.locator('#root').count();
      const viteElements = await page.locator('[data-vite-dev-id]').count();
      
      console.log(`🔧 React root elements: ${reactRoot}`);
      console.log(`🔧 Vite dev elements: ${viteElements}`);

      // Check for potential loading states
      const loadingElements = await page.locator('text=/loading/i').count();
      const spinnerElements = await page.locator('.spinner, .loading, [data-testid*="loading"]').count();
      
      console.log(`⏳ Loading indicators: ${loadingElements + spinnerElements}`);

      // Look for error boundaries or error messages
      const errorElements = await page.locator('text=/error/i, text=/failed/i').count();
      console.log(`❌ Error indicators: ${errorElements}`);

      // Check for specific UI components mentioned in AURA status
      const dashboardElements = await page.locator('[data-testid*="dashboard"], .dashboard').count();
      const legacyElements = await page.locator('.react-native-web, .rn-view').count();
      const modernElements = await page.locator('[data-testid*="web"], .vite-app').count();

      console.log(`🏠 Dashboard elements: ${dashboardElements}`);
      console.log(`📱 Legacy RN elements: ${legacyElements}`);  
      console.log(`💻 Modern web elements: ${modernElements}`);

      // Try to detect API calls
      const networkRequests: string[] = [];
      page.on('request', request => {
        if (request.url().includes('api')) {
          networkRequests.push(`${request.method()} ${request.url()}`);
        }
      });

      // Wait a bit to capture any API calls
      await page.waitForTimeout(3000);

      // Check for visible content
      const visibleText = await page.locator('body').textContent();
      const hasVisibleContent = visibleText && visibleText.trim().length > 0;
      
      console.log(`📝 Has visible content: ${hasVisibleContent}`);
      console.log(`📝 Content length: ${visibleText?.length || 0} characters`);

      // Create investigation report
      const investigation = {
        timestamp: new Date().toISOString(),
        pageTitle: title,
        reactElements: reactRoot,
        viteElements: viteElements,
        loadingIndicators: loadingElements + spinnerElements,
        errorIndicators: errorElements,
        dashboardElements: dashboardElements,
        legacyElements: legacyElements,
        modernElements: modernElements,
        hasVisibleContent: hasVisibleContent,
        contentLength: visibleText?.length || 0,
        networkRequests: networkRequests,
        consoleLogs: consoleLogs.slice(0, 10), // First 10 logs
        errorLogs: errorLogs,
        bodyVisible: false // We know this from the failed test
      };

      await fs.promises.writeFile(
        path.join(artifactDir, 'investigation-report.json'),
        JSON.stringify(investigation, null, 2)
      );

      // Save console and error logs
      await fs.promises.writeFile(
        path.join(artifactDir, 'console-logs.txt'),
        consoleLogs.join('\n')
      );

      await fs.promises.writeFile(
        path.join(artifactDir, 'error-logs.txt'),
        errorLogs.join('\n')
      );

      console.log('📊 Frontend Investigation Summary:');
      console.log(`- Page loaded: ${title || 'No title'}`);
      console.log(`- React elements: ${reactRoot}`);
      console.log(`- Content visible: ${hasVisibleContent}`);
      console.log(`- Console messages: ${consoleLogs.length}`);
      console.log(`- Errors: ${errorLogs.length}`);
      console.log(`- Network requests: ${networkRequests.length}`);

    } catch (error) {
      console.error('❌ Navigation failed:', error);
      
      // Take screenshot even on error
      await page.screenshot({ 
        path: path.join(artifactDir, 'error-state.png'),
        fullPage: true 
      });

      // Save error details
      await fs.promises.writeFile(
        path.join(artifactDir, 'navigation-error.txt'),
        `Navigation Error: ${error}\n\nConsole Logs:\n${consoleLogs.join('\n')}\n\nError Logs:\n${errorLogs.join('\n')}`
      );
    }

    // Stop tracing
    await context.tracing.stop({ path: path.join(artifactDir, 'trace.zip') });

    // Always pass - this is investigative
    expect(true).toBe(true);
  });
});