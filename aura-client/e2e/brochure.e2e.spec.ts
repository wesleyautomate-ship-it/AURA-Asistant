import { test, expect } from '@playwright/test';

const BROCHURE_PROMPT =
  'Create a brochure for 2BR at Marina Heights with pricing insights';

test('Brochure flow + Command Center prompt', async ({ page }) => {
  await page.goto('/ai-workflow/brochure');
  await expect(page.getByText('Brochure Templates')).toBeVisible();

  const templateCard = page.locator('button[aria-pressed]');
  if (await templateCard.count()) {
    await templateCard.first().click();
  }

  await page.getByRole('button', { name: /Use Template/i }).click();
  await expect(page.getByText('Brochure Editor')).toBeVisible();

  const commandFab = page.getByLabel('Open Command Center');
  await expect(commandFab).toBeVisible();
  await commandFab.click();

  const commandInput = page.getByPlaceholder('Ask Aura anything...');
  await expect(commandInput).toBeVisible();
  await commandInput.fill(BROCHURE_PROMPT);
  await commandInput.press('Enter');

  await expect(
    page.getByText(/Create a brochure for 2BR at Marina Heights/i)
  ).toBeVisible({ timeout: 5000 });
});
