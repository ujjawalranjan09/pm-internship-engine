import { test, expect } from "./fixtures";
import AxeBuilder from "@axe-core/playwright";
import { writeFileSync, mkdirSync } from "fs";

/**
 * Accessibility audits using axe-core.
 *
 * Strategy:
 * - Capture ALL violations (critical, serious, moderate, minor) per page
 * - Save full report to /home/z/my-project/download/a11y-report.json
 * - FAIL test only on "critical" violations (highest priority)
 * - "serious" violations are reported but don't fail (to allow incremental fixes
 *   without blocking the suite). Once serious issues are fixed, tighten this.
 *
 * Tags audited: wcag2a, wcag2aa, wcag21a, wcag21aa (standard a11y rulesets)
 */

const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
const REPORT_DIR = "/home/z/my-project/download/a11y";
mkdirSync(REPORT_DIR, { recursive: true });

const ALL_VIOLATIONS: Record<string, any[]> = {};

async function audit(page: import("@playwright/test").Page, label: string) {
  const results = await new AxeBuilder({ page })
    .withTags(TAGS)
    .analyze();
  ALL_VIOLATIONS[label] = results.violations;
  // Save per-page report
  writeFileSync(
    `${REPORT_DIR}/${label}.json`,
    JSON.stringify(results.violations, null, 2)
  );
  const critical = results.violations.filter((v) => v.impact === "critical");
  const serious = results.violations.filter((v) => v.impact === "serious");
  return { critical, serious, all: results.violations };
}

function formatViolations(violations: any[]): string {
  if (violations.length === 0) return "(none)";
  return violations
    .map((v) => {
      const nodes = v.nodes
        .slice(0, 3)
        .map((n: any) => `      - ${(n.html ?? "").slice(0, 100)}`)
        .join("\n");
      return `  [${v.impact}] ${v.id}: ${v.description}\n    help: ${v.helpUrl}\n    ${v.nodes.length} node(s)\n${nodes}`;
    })
    .join("\n");
}

test.describe("Accessibility audits", () => {
  test.afterAll(() => {
    // Write consolidated report
    writeFileSync(
      `${REPORT_DIR}/all-pages.json`,
      JSON.stringify(ALL_VIOLATIONS, null, 2)
    );
    // Print summary
    console.log("\n\n=== A11Y SUMMARY ===");
    for (const [page, viols] of Object.entries(ALL_VIOLATIONS)) {
      const crit = (viols as any[]).filter((v) => v.impact === "critical").length;
      const ser = (viols as any[]).filter((v) => v.impact === "serious").length;
      const mod = (viols as any[]).filter((v) => v.impact === "moderate").length;
      const min = (viols as any[]).filter((v) => v.impact === "minor").length;
      console.log(
        `  ${page.padEnd(40)} crit=${crit} serious=${ser} mod=${mod} minor=${min} (total=${viols.length})`
      );
    }
    console.log("=== END SUMMARY ===\n");
  });

  test("guest: /auth/login has no critical a11y violations", async ({ page }) => {
    await page.goto("/auth/login", { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();
    const { critical, serious } = await audit(page, "guest-login");
    expect(
      critical,
      `Critical violations:\n${formatViolations(critical)}\n\nSerious (informational):\n${formatViolations(serious)}`
    ).toEqual([]);
  });

  test("guest: /auth/register has no critical a11y violations", async ({ page }) => {
    await page.goto("/auth/register", { waitUntil: "networkidle" });
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });
    const { critical, serious } = await audit(page, "guest-register");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });

  test("candidate dashboard: no critical a11y violations", async ({ candidatePage: page }) => {
    await page.waitForLoadState("networkidle");
    const { critical, serious } = await audit(page, "candidate-dashboard");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });

  test("employer dashboard: no critical a11y violations", async ({ employerPage: page }) => {
    await page.waitForLoadState("networkidle");
    const { critical, serious } = await audit(page, "employer-dashboard");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });

  test("admin dashboard: no critical a11y violations", async ({ adminPage: page }) => {
    await page.waitForLoadState("networkidle");
    const { critical, serious } = await audit(page, "admin-dashboard");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });

  test("candidate: /applicant/internships has no critical a11y violations", async ({ candidatePage: page }) => {
    await page.goto("/applicant/internships");
    await page.waitForLoadState("networkidle");
    const { critical, serious } = await audit(page, "candidate-internships");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });

  test("employer: /employer/internships has no critical a11y violations", async ({ employerPage: page }) => {
    await page.goto("/employer/internships");
    await page.waitForLoadState("networkidle");
    const { critical, serious } = await audit(page, "employer-internships");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });

  test("admin: /admin/candidates has no critical a11y violations", async ({ adminPage: page }) => {
    await page.goto("/admin/candidates");
    await page.waitForLoadState("networkidle");
    const { critical, serious } = await audit(page, "admin-candidates");
    expect(critical, `Critical violations:\n${formatViolations(critical)}`).toEqual([]);
  });
});
