import { test, expect } from '@playwright/test';

test.describe('Basic Application Smoke Tests', () => {
  // Override base URL to test directly against what's available
  test.use({ baseURL: 'http://localhost:8000' });

  test('should access backend health endpoint', async ({ page }) => {
    await page.goto('/health');
    
    const content = await page.textContent('body');
    console.log('Health endpoint response:', content);
    
    expect(content).toContain('healthy');
  });

  test('should access backend docs', async ({ page }) => {
    await page.goto('/docs');
    
    const title = await page.title();
    console.log('Docs page title:', title);
    
    expect(title).toContain('PropertyPro');
  });

  test('should test API endpoints directly', async ({ request }) => {
    // Test health endpoint
    const healthResponse = await request.get('/health');
    expect(healthResponse.ok()).toBeTruthy();
    
    const healthData = await healthResponse.json();
    console.log('Health data:', healthData);
    
    // Test properties endpoint (should be forbidden without auth)
    const propertiesResponse = await request.get('/api/v1/properties/');
    expect(propertiesResponse.status()).toBe(403);
    
    const errorData = await propertiesResponse.json();
    console.log('Properties error:', errorData);
    expect(errorData.detail).toBe('Not authenticated');
  });
});