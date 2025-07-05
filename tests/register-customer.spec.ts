import { test, expect } from '@playwright/test';

test('Register as Customer on YourPlanner', async ({ page }) => {
  await page.goto('https://www.fasolaki.com/yourplanner/');

  // Click the Register link
  await page.getByText('Register', { exact: true }).click();

  // Fill in the registration form
  await page.fill('input[name="first_name"]', 'Test');
  await page.fill('input[name="last_name"]', 'User');
  await page.fill('input[name="email"]', 'testuser12345@example.com');
  await page.fill('input[name="password"]', 'TestPassword123!');
  await page.selectOption('select[name="role"]', 'customer');
  await page.fill('input[name="wedding_day"]', '2025-12-31'); // Future date

  // Click the Register button
  await page.getByRole('button', { name: 'Register' }).click();

  // Optionally, check for a success message or redirection
  // await expect(page).toHaveURL(/.*dashboard.*/);
});
