const { test, expect } = require('@playwright/test');

test.describe('Dashboard Mobile View', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard page, assuming it's the root
    await page.goto('http://localhost:5173/');
  });

  test('should display the mobile dashboard correctly', async ({ page }) => {
    // Set viewport to iPhone 14 Pro dimensions
    await page.setViewportSize({ width: 390, height: 844 });

    // Wait for the mobile-specific dashboard component to be visible
    await expect(page.locator('text=AI WORKSPACE')).toBeVisible();

    // Verify that the layout is single-column by checking for the absence of a side-by-side element
    const actionCenter = page.locator('div:has-text("ACTION CENTER")');
    const aiWorkspace = page.locator('div:has-text("AI WORKSPACE")');

    const actionCenterBox = await actionCenter.boundingBox();
    const aiWorkspaceBox = await aiWorkspace.boundingBox();

    // In a single-column layout, the elements should not be side-by-side.
    // We can approximate this by checking if their x-coordinates are very close.
    expect(actionCenterBox.x).toBeCloseTo(aiWorkspaceBox.x, 15);

    // Take a screenshot
    await page.screenshot({ path: 'C:/Users/wesle/OneDrive/Documents/RealtorPro AI/Realtor-assistant/screenshots/dashboard-mobile.png' });
  });
});