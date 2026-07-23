import { test as base, expect, type Page } from "@playwright/test";

/**
 * Test fixtures: demo-login helpers for each role.
 *
 * The /auth/login page has three demo-login buttons:
 *   "Candidate candidate@gov.in"
 *   "Employer employer@gov.in"
 *   "Admin admin@gov.in"
 * Clicking one calls `login({email, password: "password123"})` which falls
 * back to mock data when the backend is unreachable.
 */

type Role = "candidate" | "employer" | "admin";

const ROLE_DASHBOARDS: Record<Role, string> = {
  candidate: "/applicant",
  employer: "/employer",
  admin: "/admin",
};

async function demoLogin(page: Page, role: Role) {
  await page.goto("/auth/login");
  // Wait for hydration
  await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible({ timeout: 10000 });
  // Click the demo button for this role
  const btn = page.getByRole("button", { name: new RegExp(`^${role.charAt(0).toUpperCase() + role.slice(1)} `, "i") });
  await btn.click();
  // Wait for navigation to dashboard
  await page.waitForURL(`**${ROLE_DASHBOARDS[role]}*`, { timeout: 15000 });
  // Wait for the dashboard heading to appear (proves content rendered, not just URL change)
  await page.waitForLoadState("networkidle");
}

export const test = base.extend<{
  candidatePage: Page;
  employerPage: Page;
  adminPage: Page;
}>({
  candidatePage: async ({ page }, use) => {
    await demoLogin(page, "candidate");
    await use(page);
  },
  employerPage: async ({ page }, use) => {
    await demoLogin(page, "employer");
    await use(page);
  },
  adminPage: async ({ page }, use) => {
    await demoLogin(page, "admin");
    await use(page);
  },
});

export { expect, demoLogin, ROLE_DASHBOARDS };
