import { test, expect, demoLogin } from "./fixtures";

/**
 * Bug #3 regression: /employer/opportunities and /employer/candidates
 * returned 404 because the navLinks in src/app/employer/layout.tsx pointed
 * at non-existent routes.
 *
 * Fix: navLinks updated to /employer/internships and /employer/feedback.
 * Also the "View All" button on /employer page href changed from
 * /employer/candidates to /employer/internships.
 */

test("Bug #3: employer nav 'My Internships' link goes to /employer/internships (not 404)", async ({ page }) => {
  await demoLogin(page, "employer");
  await page.waitForLoadState("networkidle");

  // Verify the nav link exists with the correct href
  const internshipsLinks = page.getByRole("link", { name: /My Internships|Internships/i });
  const count = await internshipsLinks.count();
  expect(count).toBeGreaterThan(0);

  // Check href of the first match
  const firstHref = await internshipsLinks.first().getAttribute("href");
  expect(firstHref).toMatch(/\/employer\/internships/);

  // Click and wait for URL to change
  await internshipsLinks.first().click();
  await page.waitForURL(/\/employer\/internships/, { timeout: 15000 });
  await page.waitForLoadState("networkidle");

  // Page should render the heading (not a 404)
  await expect(page.getByRole("heading", { name: /My Internships|Internships/i }).first()).toBeVisible({
    timeout: 10000,
  });
  await expect(page.getByText("This page could not be found")).not.toBeVisible();
});

test("Bug #3: employer nav 'Feedback' link goes to /employer/feedback (not 404)", async ({ page }) => {
  await demoLogin(page, "employer");
  await page.waitForLoadState("networkidle");

  const feedbackLinks = page.getByRole("link", { name: /Feedback/i });
  expect(await feedbackLinks.count()).toBeGreaterThan(0);

  // Verify href
  const firstHref = await feedbackLinks.first().getAttribute("href");
  expect(firstHref).toMatch(/\/employer\/feedback/);

  // Click and wait for URL
  await feedbackLinks.first().click();
  await page.waitForURL(/\/employer\/feedback/, { timeout: 15000 });
  await page.waitForLoadState("networkidle");

  await expect(page.getByRole("heading", { name: /Feedback/i }).first()).toBeVisible({ timeout: 10000 });
  await expect(page.getByText("This page could not be found")).not.toBeVisible();
});

test("Bug #3: /employer/opportunities should NOT be a valid route (so old bookmarks fail loudly)", async ({ page }) => {
  await demoLogin(page, "employer");
  await page.goto("/employer/opportunities");
  // This should now be a 404 — confirms the route genuinely doesn't exist
  await expect(page.getByText("This page could not be found")).toBeVisible({ timeout: 10000 });
});

test("Bug #3: 'View All' button on employer dashboard goes to /employer/internships", async ({ page }) => {
  await demoLogin(page, "employer");

  // Find a "View All" link/button
  const viewAll = page.getByRole("link", { name: /View All/i }).first();
  await expect(viewAll).toBeVisible({ timeout: 10000 });

  const href = await viewAll.getAttribute("href");
  expect(href).toMatch(/\/employer\/internships/);
  expect(href).not.toMatch(/\/employer\/candidates/);
});
