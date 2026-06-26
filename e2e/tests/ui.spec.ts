import { expect, test } from "@playwright/test";

test.describe("Insurance Policy Comparison UI", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Insurance Policy Comparison Agent" })).toBeVisible();
  });

  test("loads health banner and profile form", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "Your Profile" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Policy Documents" })).toBeVisible();
    await expect(page.locator(".banner")).toBeVisible({ timeout: 15_000 });
  });

  test("dry-run analyze with quick mode shows recommendation", async ({ page }) => {
    await page.getByTestId("dry-run-checkbox").check();
    await page.getByTestId("quick-mode-checkbox").check();
    await page.getByTestId("analyze-button").click();

    const results = page.getByTestId("results-section");
    await expect(results).toBeVisible({ timeout: 60_000 });
    await expect(results.getByText(/Preferred plan:/i)).toBeVisible();
    await expect(results.getByText(/Mode: dry_run/)).toBeVisible();
  });

  test("public HO-3 preset dry-run completes", async ({ page }) => {
    await page.getByRole("radio", { name: /Public HO-3/ }).check();
    await page.getByTestId("dry-run-checkbox").check();
    await page.getByTestId("analyze-button").click();

    const results = page.getByTestId("results-section");
    await expect(results).toBeVisible({ timeout: 60_000 });
    await expect(results.getByText(/Preferred plan:/i)).toBeVisible();
  });

  test("quick mode checkbox toggles without starting analysis", async ({ page }) => {
    const quick = page.getByTestId("quick-mode-checkbox");
    await quick.uncheck();
    await expect(quick).not.toBeChecked();
    await quick.check();
    await expect(quick).toBeChecked();
    await expect(page.getByTestId("results-section")).toHaveCount(0);
  });

  test("upload mode disables analyze until file selected", async ({ page }) => {
    await page.getByRole("radio", { name: "Upload my policies" }).check();
    await expect(page.getByTestId("analyze-button")).toBeDisabled();
  });
});
