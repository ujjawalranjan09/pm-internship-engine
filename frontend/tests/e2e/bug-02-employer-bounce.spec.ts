import { test, expect, demoLogin } from "./fixtures";

/**
 * Bug #2 regression: /employer used to bounce to /auth/login even after a
 * successful employer demo login. Root cause was authService.getCurrentUser()
 * returning MOCK_USER (role=admin) on API failure, which overrode the real
 * logged-in employer user in the Zustand store.
 *
 * Fix: getCurrentUser returns null on failure so the persisted user is used.
 */

test("Bug #2: employer demo login lands on /employer (not /auth/login)", async ({ page }) => {
  await demoLogin(page, "employer");

  // Should be on /employer (or /employer/dashboard)
  expect(page.url()).toMatch(/\/employer(\/|$|\?)/);

  // Should NOT be back on /auth/login
  expect(page.url()).not.toMatch(/\/auth\/login/);

  // The employer dashboard heading should be visible (proves content rendered)
  await expect(page.getByRole("heading", { name: /Employer.*Dashboard|Dashboard/i })).toBeVisible({
    timeout: 10000,
  });
});

test("Bug #2: /employer is accessible via direct navigation after employer login", async ({ page }) => {
  await demoLogin(page, "employer");

  // Now navigate away then back to /employer
  await page.goto("/employer/internships");
  await page.waitForLoadState("networkidle");
  await page.goto("/employer");
  await page.waitForLoadState("networkidle");

  // Should remain on /employer, not redirect to login
  expect(page.url()).toMatch(/\/employer(\/|$|\?)/);
  expect(page.url()).not.toMatch(/\/auth\/login/);
});

test("Bug #2: employer nav links render (proves auth state persisted across pages)", async ({ page }) => {
  await demoLogin(page, "employer");

  // The employer layout should render nav links
  await expect(page.getByRole("link", { name: /Dashboard/i }).first()).toBeVisible();
  // Sign out button present — proves we're authenticated in the layout
  await expect(page.getByRole("button", { name: /Sign out|Log out/i }).first()).toBeVisible();
});
