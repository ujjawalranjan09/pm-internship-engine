import { test, expect, demoLogin } from "./fixtures";

/**
 * Bug #1 regression: every page that calls useToast() used to crash with
 * "useToast must be used within ToastProvider". Fixed by wrapping
 * ToastProvider inside QueryClientProvider in src/app/providers.tsx.
 *
 * Strategy: visit each major route while collecting pageerror + console.error
 * events, assert the page rendered real content, and assert no ToastProvider
 * error surfaced.
 *
 * Note: protected routes (/applicant, /employer, /admin) require login first.
 * We use demoLogin() to authenticate before navigating.
 */

const GUEST_PAGES = [
  { url: "/auth/login", heading: "Welcome Back" },
  { url: "/auth/register", heading: /Create.*Account|Register|Sign Up/i },
];

for (const { url, heading } of GUEST_PAGES) {
  test(`Bug #1: ${url} does not throw ToastProvider error`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await page.goto(url, { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: heading })).toBeVisible({ timeout: 15000 });

    const toastErrors = errors.filter((e) =>
      /ToastProvider|useToast must be used within/i.test(e)
    );
    expect(toastErrors, `ToastProvider errors: ${JSON.stringify(toastErrors)}`).toEqual([]);
  });
}

test("Bug #1: /applicant (candidate dashboard) does not throw ToastProvider error", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await demoLogin(page, "candidate");
  await page.waitForLoadState("networkidle");

  const toastErrors = errors.filter((e) =>
    /ToastProvider|useToast must be used within/i.test(e)
  );
  expect(toastErrors, `ToastProvider errors: ${JSON.stringify(toastErrors)}`).toEqual([]);
});

test("Bug #1: /employer (employer dashboard) does not throw ToastProvider error", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await demoLogin(page, "employer");
  await page.waitForLoadState("networkidle");

  const toastErrors = errors.filter((e) =>
    /ToastProvider|useToast must be used within/i.test(e)
  );
  expect(toastErrors, `ToastProvider errors: ${JSON.stringify(toastErrors)}`).toEqual([]);
});

test("Bug #1: /admin (admin dashboard) does not throw ToastProvider error", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await demoLogin(page, "admin");
  await page.waitForLoadState("networkidle");

  const toastErrors = errors.filter((e) =>
    /ToastProvider|useToast must be used within/i.test(e)
  );
  expect(toastErrors, `ToastProvider errors: ${JSON.stringify(toastErrors)}`).toEqual([]);
});
