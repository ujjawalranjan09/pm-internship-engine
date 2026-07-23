import { test, expect } from "./fixtures";

/**
 * Internship creation form tests — exercises the complex multi-card form at
 * /employer/internships/new end-to-end. Covers:
 *   - Validation errors on empty submit
 *   - Successful submit with minimum required fields
 *   - Successful submit with all fields + skills
 *   - Preview tab reflects form input
 *   - District select disabled until state selected (conditional UI)
 *   - Skill search + add/remove via badge
 *
 * Backend isn't running so opportunityService.createOpportunity falls through
 * to mock data — but the form submission, validation, toast, and redirect are
 * all real.
 */

const VALID_FORM = {
  title: "Software Development Intern",
  description: "Work on a Next.js + FastAPI application. You will build features, write tests, and ship to production.",
  sector: "Technology",
  location: "Bengaluru",
  state: "Karnataka",
  district: "Bengaluru",
  stipend: "15000",
  duration: "6",
  capacity: "5",
};

test.describe("Internship creation form", () => {
  test.beforeEach(async ({ employerPage }) => {
    // employerPage fixture already logs in as employer
    await employerPage.goto("/employer/internships/new");
    // Wait for the page heading to confirm render
    await expect(employerPage.getByRole("heading", { name: "Create New Internship" })).toBeVisible({
      timeout: 15000,
    });
  });

  test("empty submit shows validation errors for required fields", async ({ employerPage }) => {
    // Click Publish without filling anything
    await employerPage.getByRole("button", { name: /Publish Internship/i }).click();

    // opportunitySchema requires: title (min 5), description (min 20),
    // sector (min 1), location (min 1), state (min 1)
    await expect(employerPage.getByText(/Title must be at least 5 characters/i)).toBeVisible({ timeout: 5000 });
    await expect(employerPage.getByText(/Description must be at least 20 characters/i)).toBeVisible();
    await expect(employerPage.getByText(/Select a sector/i).first()).toBeVisible();
    await expect(employerPage.getByText(/Enter a location/i)).toBeVisible();
    await expect(employerPage.getByText(/Select a state/i).first()).toBeVisible();

    // Should stay on the new-internship page
    await expect(employerPage).toHaveURL(/\/employer\/internships\/new/);
  });

  test("submit with minimum required fields succeeds and redirects", async ({ employerPage }) => {
    // Fill required text fields via their labels
    await employerPage.getByLabel("Internship Title").fill(VALID_FORM.title);
    await employerPage.locator("textarea").first().fill(VALID_FORM.description);
    await employerPage.getByLabel("Location / City").fill(VALID_FORM.location);

    // Select dropdowns — sector, state, and workMode are all required by schema.
    // workMode has .default("onsite") but the DOM select defaults to "" (placeholder),
    // so we must explicitly select a value to pass enum validation.
    await employerPage.getByLabel("Sector").selectOption(VALID_FORM.sector);
    await employerPage.getByLabel("State").selectOption(VALID_FORM.state);
    await employerPage.getByLabel("Work Mode").selectOption("onsite");

    // Stipend/duration/capacity have defaults (0/6/1) — set explicit values
    await employerPage.getByLabel("Monthly Stipend (₹)").fill(VALID_FORM.stipend);
    await employerPage.getByLabel("Duration (months)").fill(VALID_FORM.duration);
    await employerPage.getByLabel("Capacity").fill(VALID_FORM.capacity);

    // Submit
    await employerPage.getByRole("button", { name: /Publish Internship/i }).click();

    // Should redirect to /employer/internships
    await employerPage.waitForURL(/\/employer\/internships$/, { timeout: 15000 });

    // Should show success toast
    await expect(employerPage.getByRole("alert").filter({ hasText: /Internship created/i })).toBeVisible({
      timeout: 5000,
    });
  });

  test("submit with all fields + skills succeeds and redirects", async ({ employerPage }) => {
    // Basic info
    await employerPage.getByLabel("Internship Title").fill("Full Stack Engineering Intern");
    await employerPage.locator("textarea").first().fill(
      "Build and maintain a production web app using Next.js, FastAPI, and PostgreSQL. You will own features end-to-end."
    );
    await employerPage.getByLabel("Sector").selectOption("Technology");
    await employerPage.getByLabel("Location / City").fill("Bengaluru");
    await employerPage.getByLabel("State").selectOption("Karnataka");
    // District is now enabled (state selected)
    await employerPage.getByLabel("District").selectOption("Bengaluru");

    // Details
    await employerPage.getByLabel("Monthly Stipend (₹)").fill("25000");
    await employerPage.getByLabel("Duration (months)").fill("3");
    await employerPage.getByLabel("Capacity").fill("10");
    await employerPage.getByLabel("Work Mode").selectOption("hybrid");
    // Dates — use date input format YYYY-MM-DD
    const futureDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    const endDate = new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    await employerPage.getByLabel("Start Date").fill(futureDate);
    await employerPage.getByLabel("End Date").fill(endDate);

    // Skills — search and add "Python"
    await employerPage.getByPlaceholder("Search skills...").fill("Python");
    await employerPage.getByRole("button", { name: "Python", exact: true }).click();
    // Verify the skill badge appears
    await expect(employerPage.locator("div.flex.flex-wrap button[aria-label='Remove Python']")).toBeVisible();

    // Eligibility
    await employerPage.getByLabel("Minimum Education").selectOption("Bachelor's Degree");
    await employerPage.getByLabel("Minimum Percentage").fill("60");

    // Submit
    await employerPage.getByRole("button", { name: /Publish Internship/i }).click();

    await employerPage.waitForURL(/\/employer\/internships$/, { timeout: 15000 });
    await expect(employerPage.getByRole("alert").filter({ hasText: /Internship created/i })).toBeVisible({
      timeout: 5000,
    });
  });

  test("district select is disabled until state is selected", async ({ employerPage }) => {
    // Initially the District select should be disabled
    const districtSelect = employerPage.getByLabel("District");
    await expect(districtSelect).toBeDisabled();

    // After selecting state, district becomes enabled
    await employerPage.getByLabel("State").selectOption("Maharashtra");
    await expect(districtSelect).toBeEnabled();

    // And district options should be Maharashtra's districts
    const options = await districtSelect.locator("option").allTextContents();
    expect(options).toContain("Mumbai");
    expect(options).toContain("Pune");
  });

  test("skill search adds and removes skill badges", async ({ employerPage }) => {
    // Search for a skill
    await employerPage.getByPlaceholder("Search skills...").fill("React");
    // Click the matching option in the dropdown
    await employerPage.getByRole("button", { name: "React", exact: true }).click();

    // Verify badge appears with a remove button
    const removeBtn = employerPage.locator("button[aria-label='Remove React']");
    await expect(removeBtn).toBeVisible();

    // Search another skill and add it too
    await employerPage.getByPlaceholder("Search skills...").fill("TypeScript");
    await employerPage.getByRole("button", { name: "TypeScript", exact: true }).click();
    await expect(employerPage.locator("button[aria-label='Remove TypeScript']")).toBeVisible();

    // Remove the first skill
    await removeBtn.click();
    await expect(employerPage.locator("button[aria-label='Remove React']")).toHaveCount(0);
    // TypeScript badge should still be there
    await expect(employerPage.locator("button[aria-label='Remove TypeScript']")).toBeVisible();
  });

  test("preview tab reflects form input", async ({ employerPage }) => {
    // Fill some fields
    await employerPage.getByLabel("Internship Title").fill("Preview Test Internship");
    await employerPage.locator("textarea").first().fill("This description appears in the preview tab.");
    await employerPage.getByLabel("Sector").selectOption("Finance");
    await employerPage.getByLabel("Location / City").fill("Mumbai");
    await employerPage.getByLabel("Monthly Stipend (₹)").fill("20000");
    await employerPage.getByLabel("Duration (months)").fill("4");

    // Switch to the Preview tab
    await employerPage.getByRole("tab", { name: /Preview/i }).click();

    // The preview tab should render the entered values
    await expect(employerPage.getByRole("heading", { name: "Preview Test Internship" })).toBeVisible({
      timeout: 5000,
    });
    await expect(employerPage.getByText("This description appears in the preview tab.")).toBeVisible();
    await expect(employerPage.getByText("Finance").first()).toBeVisible();
    await expect(employerPage.getByText("Mumbai")).toBeVisible();
    // Stipend is rendered as currency — match the digits
    await expect(employerPage.getByText(/20,000/)).toBeVisible();
    await expect(employerPage.getByText(/4\s+months/i)).toBeVisible();
  });

  test("Add Criteria button appends a new key-value row", async ({ employerPage }) => {
    // Initially no criteria rows
    let criteriaInputs = employerPage.getByPlaceholder("Field name");
    await expect(criteriaInputs).toHaveCount(0);

    // Click the "Add" button in the Additional Criteria section
    await employerPage.getByRole("button", { name: /^Add$/i }).click();

    // Now one row should exist
    criteriaInputs = employerPage.getByPlaceholder("Field name");
    await expect(criteriaInputs).toHaveCount(1);
    await expect(employerPage.getByPlaceholder("Value")).toHaveCount(1);

    // Fill the row
    await criteriaInputs.fill("Min Age");
    await employerPage.getByPlaceholder("Value").fill("18");

    // Add another row
    await employerPage.getByRole("button", { name: /^Add$/i }).click();
    await expect(employerPage.getByPlaceholder("Field name")).toHaveCount(2);

    // Remove the first row using its remove button
    const removeButtons = employerPage.getByRole("button", { name: /Remove criterion/i });
    await removeButtons.first().click();
    await expect(employerPage.getByPlaceholder("Field name")).toHaveCount(1);
  });
});
