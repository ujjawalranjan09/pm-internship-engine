import { test, expect } from "./fixtures";

/**
 * Smoke tests: verify each role's dashboard renders substantive content.
 * Catches regressions where a page renders no errors but is blank/broken.
 */

test("guest: /auth/login renders all 3 demo buttons", async ({ page }) => {
  await page.goto("/auth/login");
  await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Candidate candidate@gov.in/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Employer employer@gov.in/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Admin admin@gov.in/i })).toBeVisible();
});

test("guest: /auth/register renders form fields", async ({ page }) => {
  await page.goto("/auth/register");
  await expect(page.getByLabel(/Email/i)).toBeVisible();
  await expect(page.getByLabel(/Password/i).first()).toBeVisible();
});

test("candidate dashboard: renders welcome + stats", async ({ candidatePage: page }) => {
  await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible({ timeout: 10000 });
  // The dashboard should have at least one card or stat block
  const cards = page.locator("[class*='card'], [class*='Card']");
  await expect(cards.first()).toBeVisible({ timeout: 10000 });
});

test("candidate: can navigate to /applicant/internships and see list", async ({ candidatePage: page }) => {
  await page.goto("/applicant/internships");
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: /Browse Internships|Internships/i })).toBeVisible({
    timeout: 10000,
  });
});

test("candidate: /applicant/profile renders", async ({ candidatePage: page }) => {
  await page.goto("/applicant/profile");
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: /Profile/i })).toBeVisible({ timeout: 10000 });
});

test("employer dashboard: renders welcome + quick actions", async ({ employerPage: page }) => {
  await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible({ timeout: 10000 });
  // Should have nav links for the 3 employer routes
  await expect(page.getByRole("link", { name: /Internships/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Feedback/i }).first()).toBeVisible();
});

test("admin dashboard: renders admin-specific content", async ({ adminPage: page }) => {
  await expect(page.getByRole("heading", { name: /Admin Dashboard/i })).toBeVisible({
    timeout: 10000,
  });
  // Admin nav links
  await expect(page.getByRole("link", { name: /Candidates/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Allocations/i }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Audit Logs|Audit/i }).first()).toBeVisible();
});

test("admin: /admin/candidates renders candidate list or empty-state", async ({ adminPage: page }) => {
  await page.goto("/admin/candidates");
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: /Candidate/i })).toBeVisible({ timeout: 10000 });
  await expect(page.getByText("This page could not be found")).not.toBeVisible();
});

test("admin: /admin/allocations renders", async ({ adminPage: page }) => {
  await page.goto("/admin/allocations");
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: "Allocation Management" })).toBeVisible({
    timeout: 10000,
  });
});

test("admin: /admin/settings renders", async ({ adminPage: page }) => {
  await page.goto("/admin/settings");
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: /Settings|Policy/i })).toBeVisible({
    timeout: 10000,
  });
});
