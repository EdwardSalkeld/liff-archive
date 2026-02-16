# Playwright Visual Regression Tests

This directory contains Playwright tests for visual regression testing of the LIFF Archive site.

## Overview

The visual regression tests take screenshots of key pages on desktop viewport, comparing them against golden images stored in the repository. This ensures that UI changes are intentional and can be reviewed before merging.

## Tested Pages

The following pages are tested:
- `/` - Home page
- `/about/` - About page
- `/all/` - All films listing
- `/strand/` - Strands listing
- `/films/` - Films by year

Each page is tested on:
- **Desktop Chrome** (1280x720 viewport)

## Running Tests Locally

### Prerequisites

1. Install Node.js (version 20 or higher)
2. Install dependencies:
   ```bash
   npm install
   ```
3. Install Playwright browsers:
   ```bash
   npx playwright install chromium --with-deps
   ```

### Running Tests

To run the visual regression tests (requires a running Hugo server):
```bash
npm test
```

This will:
1. Build and serve the Hugo site on `http://localhost:1313`
2. Run all visual regression tests
3. Compare screenshots to golden images
4. Generate an HTML report in `playwright-report/`

### Updating Golden Images

If you make intentional UI changes, you need to update the golden images (with Hugo running):

```bash
npm run test:update
```

This will:
1. Take new screenshots of all pages
2. Update the golden images in `tests/visual-regression.spec.js-snapshots/Desktop-Chrome/` (e.g., `home.png`, `about.png`)
3. You must commit the updated snapshots to your branch

### Viewing Test Reports

After running tests, view the HTML report:
```bash
npx playwright show-report
```

## CI/CD Integration

The tests run automatically on every pull request via GitHub Actions. See `.github/workflows/ci.yml` for the workflow configuration.

### What Happens on CI

1. **On Success**: Tests pass silently, and the workflow succeeds
2. **On Failure**: 
   - The workflow fails
   - Test artifacts are uploaded (including diff images)
   - A comment is posted to the PR with details about the failures
   - You can download the artifacts to review the differences

### When Tests Fail

If visual regression tests fail on CI:

1. Download the test artifacts from the GitHub Actions workflow run
2. Review the diff images to understand what changed
3. If changes are intentional:
   - Run `npm run test:update` locally
   - Commit the updated snapshots
   - Push to your branch
4. If changes are unintentional:
   - Fix the code that caused the unexpected visual change
   - Push the fix to your branch

## Test Configuration

The Playwright configuration is in `playwright.config.js`. Key settings:

- **Base URL**: `http://localhost:1313` (Hugo dev server)
- **Test timeout**: 30 seconds per test
- **Screenshot comparison**: 
  - Allows up to 2% of pixels to differ (`maxDiffPixelRatio: 0.02`)
  - Uses threshold of 0.3 for pixel color differences to account for font rendering and anti-aliasing
- **Retries**: 2 retries on CI for flaky tests
- **Reporters**: HTML report + list output

## Tips

- **Fonts and images**: Tests wait 1 second after page load to ensure fonts and images are loaded
- **Animations**: Animations are disabled during screenshot capture for consistency
- **Full page screenshots**: All screenshots capture the full page, not just the viewport
- **Pixel differences**: A percentage-based threshold (2%) is used to account for font rendering differences and anti-aliasing across environments
