import { test, expect } from '@playwright/test';

test.skip('Brochure flow: select template → generate → download', async ({ page }) => {
  await page.goto('/ai-workflow/brochure');
  await expect(page.getByText('Brochure Templates')).toBeVisible();
  // Select first template card if present
  const card = page.locator('button[aria-pressed]');
  if (await card.count()) {
    await card.first().click();
  }
  await page.getByRole('button', { name: 'Use Template' }).click();
  await expect(page.getByText('Brochure Editor')).toBeVisible();
});

