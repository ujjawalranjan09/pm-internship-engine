import { test, expect } from "./fixtures";

/**
 * Form-submission tests: exercise the actual form UI (not the demo-login
 * buttons) to verify the form fields, submit flow, and validation work
 * end-to-end. The backend isn't running so authService.login/register
 * falls through to mock data — but the form submission itself is real.
 */

const TEST_CREDENTIALS = {
  candidate: { email: "candidate@gov.in", password: "password123" },
  employer: { email: "employer@gov.in", password: "password123" },
  admin: { email: "admin@gov.in", password: "password123" },
};

test.describe("Login form submission", () => {
  test("login form: candidate credentials via form fields land on /applicant", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();

    // Fill the form (not the demo button)
    await page.getByRole("textbox", { name: "Email Address" }).fill(TEST_CREDENTIALS.candidate.email);
    await page.getByLabel("Password", { exact: true }).fill(TEST_CREDENTIALS.candidate.password);

    // Submit
    await page.getByRole("button", { name: "Sign In" }).click();

    // Should land on candidate dashboard
    await page.waitForURL(/\/applicant/, { timeout: 15000 });
    expect(page.url()).not.toMatch(/\/auth\/login/);
  });

  test("login form: employer credentials via form fields land on /employer", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();

    await page.getByRole("textbox", { name: "Email Address" }).fill(TEST_CREDENTIALS.employer.email);
    await page.getByLabel("Password", { exact: true }).fill(TEST_CREDENTIALS.employer.password);
    await page.getByRole("button", { name: "Sign In" }).click();

    await page.waitForURL(/\/employer/, { timeout: 15000 });
    expect(page.url()).not.toMatch(/\/auth\/login/);
  });

  test("login form: admin credentials via form fields land on /admin", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();

    await page.getByRole("textbox", { name: "Email Address" }).fill(TEST_CREDENTIALS.admin.email);
    await page.getByLabel("Password", { exact: true }).fill(TEST_CREDENTIALS.admin.password);
    await page.getByRole("button", { name: "Sign In" }).click();

    await page.waitForURL(/\/admin/, { timeout: 15000 });
    expect(page.url()).not.toMatch(/\/auth\/login/);
  });

  test("login form: empty fields shows validation errors", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();

    // Submit without filling anything
    await page.getByRole("button", { name: "Sign In" }).click();

    // Both fields should show validation errors
    await expect(page.getByText(/valid email/i).first()).toBeVisible({ timeout: 5000 });
    // Should NOT navigate
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test("login form: 'Register' link navigates to /auth/register", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();

    // Click the inline "Register" link (not the demo button)
    await page.getByRole("link", { name: "Register" }).first().click();
    await page.waitForURL(/\/auth\/register/);
  });
});

test.describe("Register form submission", () => {
  test("register form: candidate registration lands on /applicant", async ({ page }) => {
    await page.goto("/auth/register");
    // Wait for hydration
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });

    // Role is "candidate" by default — verify
    await expect(page.locator("button[type=button]").filter({ hasText: "Candidate" })).toBeVisible();

    // Fill form
    await page.getByRole("textbox", { name: "Full Name" }).fill("Test Candidate");
    await page.getByRole("textbox", { name: "Email Address" }).fill(`test-candidate-${Date.now()}@example.com`);
    await page.getByRole("textbox", { name: "Phone Number" }).fill("9876543210");
    await page.getByLabel("Password", { exact: true }).fill("TestPass123!");
    await page.getByLabel("Confirm Password").fill("TestPass123!");

    // Submit
    await page.getByRole("button", { name: "Create Account" }).click();

    // Should land on applicant dashboard
    await page.waitForURL(/\/applicant/, { timeout: 15000 });
    expect(page.url()).not.toMatch(/\/auth\/register/);
  });

  test("register form: employer registration lands on /employer", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });

    // Click the Employer role button
    await page.locator("button[type=button]").filter({ hasText: "Employer" }).click();

    await page.getByRole("textbox", { name: "Full Name" }).fill("Test Employer");
    await page.getByRole("textbox", { name: "Email Address" }).fill(`test-employer-${Date.now()}@example.com`);
    await page.getByLabel("Password", { exact: true }).fill("TestPass123!");
    await page.getByLabel("Confirm Password").fill("TestPass123!");

    await page.getByRole("button", { name: "Create Account" }).click();

    await page.waitForURL(/\/employer/, { timeout: 15000 });
    expect(page.url()).not.toMatch(/\/auth\/register/);
  });

  test("register form: password mismatch shows validation error", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });

    await page.getByRole("textbox", { name: "Full Name" }).fill("Mismatch User");
    await page.getByRole("textbox", { name: "Email Address" }).fill("mismatch@example.com");
    await page.getByLabel("Password", { exact: true }).fill("TestPass123!");
    await page.getByLabel("Confirm Password").fill("DifferentPass456!");

    await page.getByRole("button", { name: "Create Account" }).click();

    await expect(page.getByText(/Passwords do not match/i)).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test("register form: short password (<8 chars) shows validation error", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });

    await page.getByRole("textbox", { name: "Full Name" }).fill("Short PW");
    await page.getByRole("textbox", { name: "Email Address" }).fill("short@example.com");
    await page.getByLabel("Password", { exact: true }).fill("short"); // <8 chars
    await page.getByLabel("Confirm Password").fill("short");

    await page.getByRole("button", { name: "Create Account" }).click();

    await expect(page.getByText(/at least 8 characters/i)).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test("register form: short name (<2 chars) shows validation error", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });

    await page.getByRole("textbox", { name: "Full Name" }).fill("X"); // <2 chars
    await page.getByRole("textbox", { name: "Email Address" }).fill("valid@example.com");
    await page.getByLabel("Password", { exact: true }).fill("ValidPass123!");
    await page.getByLabel("Confirm Password").fill("ValidPass123!");

    await page.getByRole("button", { name: "Create Account" }).click();

    await expect(page.getByText(/Name must be at least 2 characters/i)).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test("register form: 'Sign In' link navigates to /auth/login", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.getByText(/I am a/i)).toBeVisible({ timeout: 10000 });

    await page.getByRole("link", { name: "Sign In" }).first().click();
    await page.waitForURL(/\/auth\/login/);
  });
});

test.describe("Sign-out flow", () => {
  test("sign out from candidate dashboard returns to /auth/login", async ({ page }) => {
    // Login as candidate
    await page.goto("/auth/login");
    await page.getByRole("button", { name: /Candidate candidate@gov.in/i }).click();
    await page.waitForURL(/\/applicant/);

    // Click sign out
    await page.getByRole("button", { name: /Sign out|Log out/i }).first().click();

    // Should be back at login
    await page.waitForURL(/\/auth\/login/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/auth\/login/);
  });

  test("sign out from employer dashboard returns to /auth/login", async ({ page }) => {
    await page.goto("/auth/login");
    await page.getByRole("button", { name: /Employer employer@gov.in/i }).click();
    await page.waitForURL(/\/employer/);

    await page.getByRole("button", { name: /Sign out|Log out/i }).first().click();

    await page.waitForURL(/\/auth\/login/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/auth\/login/);
  });

  test("sign out from admin dashboard returns to /auth/login", async ({ page }) => {
    await page.goto("/auth/login");
    await page.getByRole("button", { name: /Admin admin@gov.in/i }).click();
    await page.waitForURL(/\/admin/);

    await page.getByRole("button", { name: /Sign out|Log out/i }).first().click();

    await page.waitForURL(/\/auth\/login/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/auth\/login/);
  });
});
