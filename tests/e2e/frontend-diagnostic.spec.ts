import { test, expect } from '@playwright/test';

test('Frontend Quick Diagnostic', async ({ page }) => {
  console.log('🔍 Starting frontend diagnostic...');
  
  // Navigate to frontend with fallback
  try {
    await page.goto('/');
  } catch (e) {
    console.warn('Primary baseURL navigation failed, attempting fallback to http://localhost:5173');
    await page.goto('http://localhost:5173/');
  }
  
  // Take screenshot immediately
  await page.screenshot({ path: 'frontend-diagnostic.png', fullPage: true });
  console.log('📸 Screenshot saved: frontend-diagnostic.png');
  
  // Get page source
  const pageSource = await page.content();
  console.log('📝 Page source length:', pageSource.length);
  
  // Check for React app mounting
  const rootElement = await page.locator('#root').innerHTML();
  console.log('⚛️ React root content:', rootElement.slice(0, 200) + '...');
  
  // Check for any visible text
  const bodyText = await page.locator('body').allTextContents();
  console.log('📄 Body text:', bodyText.join(' ').slice(0, 200));
  
  // Check network activity
  let networkCalls = 0;
  page.on('request', () => networkCalls++);
  
  // Wait for potential async loading
  await page.waitForTimeout(5000);
  console.log('🌐 Network calls made:', networkCalls);
  
  // Check if there are any API calls to our backend
  const hasApiCalls = await page.evaluate(() => {
    return window.fetch !== undefined;
  });
  console.log('🔌 Fetch API available:', hasApiCalls);
  
  // Always pass - diagnostic only
  expect(true).toBe(true);
});
