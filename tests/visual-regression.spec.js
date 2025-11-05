// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Visual regression tests for the LIFF Archive site.
 * These tests take screenshots and compare them to golden images.
 */

const pages = [
  { path: '/', name: 'home' },
  { path: '/about/', name: 'about' },
  { path: '/all/', name: 'all' },
  { path: '/strand/', name: 'strand' },
  { path: '/films/', name: 'films' },
];

for (const page of pages) {
  test(`Visual regression: ${page.name} page`, async ({ page: playwright }) => {
    // Navigate to the page
    await playwright.goto(page.path);
    
    // Wait for the page to be fully loaded
    await playwright.waitForLoadState('networkidle');
    
    // Give fonts and images time to load
    await playwright.waitForTimeout(1000);
    
    // Take a full page screenshot and compare to golden image
    await expect(playwright).toHaveScreenshot(`${page.name}.png`, {
      fullPage: true,
      animations: 'disabled',
      // Allow for minor rendering differences
      maxDiffPixels: 100,
    });
  });
}
