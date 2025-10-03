import { test, expect } from '@playwright/test';

async function snap(page, name: string) {
  await page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
}

test.describe('PropertyPro AI Frontend Mockup - Visual walkthrough', () => {
  test('Dashboard and navigation', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/PropertyPro|Laura|Real Estate/i);

    await page.waitForTimeout(500);
    await snap(page, '01-dashboard');

    const commandBtn = page.getByRole('button', { name: /command center/i });
    if ((await commandBtn.count()) > 0) {
      await commandBtn.first().click();
      await page.waitForTimeout(250);
      await snap(page, '02-command-center');

      const closeButton = page.getByRole('button', { name: /close/i }).first();
      if ((await closeButton.count()) > 0) {
        await closeButton.click();
      } else {
        await page.keyboard.press('Escape');
      }
    }

    const tasksButton = page.getByRole('button', { name: /^Tasks$/i });
    if ((await tasksButton.count()) > 0) {
      await tasksButton.click();
      await page.waitForTimeout(200);
      await snap(page, '03-tasks');
    }

    const chatButton = page.getByRole('button', { name: /^Chat$/i });
    if ((await chatButton.count()) > 0) {
      await chatButton.click();
      await page.waitForTimeout(200);
      await snap(page, '04-chat');
    }

    const analyticsButton = page.getByRole('button', { name: /Profile|Analytics/i });
    if ((await analyticsButton.count()) > 0) {
      await analyticsButton.first().click();
      await page.waitForTimeout(200);
      await snap(page, '05-analytics');
    }

    const dashboardButton = page.getByRole('button', { name: /^Dashboard$/i });
    if ((await dashboardButton.count()) > 0) {
      await dashboardButton.click();
      await page.waitForTimeout(200);
      await snap(page, '06-dashboard-return');
    }
  });

  test('Feature actions from dashboard cards', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(500);
    await snap(page, 'actions-01-dashboard');

    const marketingTriggers = [
      page.getByRole('button', { name: /^Marketing$/i }),
      page.getByRole('link', { name: /^Marketing$/i }),
      page.getByText(/^Marketing$/i),
    ];

    for (const trigger of marketingTriggers) {
      if ((await trigger.count()) > 0) {
        await trigger.first().click();
        await page.waitForTimeout(300);
        await snap(page, 'actions-02-marketing');
        break;
      }
    }

    const tasksButton = page.getByRole('button', { name: /^Tasks$/i });
    if ((await tasksButton.count()) > 0) {
      await tasksButton.click();
      await page.waitForTimeout(200);
      await snap(page, 'actions-03-tasks');
    }
  });
});