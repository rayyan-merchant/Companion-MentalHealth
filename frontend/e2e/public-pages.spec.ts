import { expect, test } from '@playwright/test';

test('public safety and privacy pages are reachable', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page.getByRole('heading', { name: 'Privacy notice' })).toBeVisible();
    await page.goto('/safety');
    await expect(page.getByRole('heading', { name: 'Safety and emergency support' })).toBeVisible();
});
