# Playwright Golden Screenshots HOWTO

This repository uses Playwright visual regression tests with golden screenshots stored under `tests/visual-regression.spec.js-snapshots/`. When content changes are intentional, update the goldens locally and commit them.

## Prereqs
- Node.js 20+
- Dependencies installed: `npm install`
- Chromium installed for Playwright: `npx playwright install chromium --with-deps`

## Update Goldens
1. Start the Hugo server locally in another terminal:
   ```bash
   hugo serve -D -s hugo
   ```
2. Run the snapshot update:
   ```bash
   npm run test:update
   ```
3. Verify new snapshots in `tests/visual-regression.spec.js-snapshots/Desktop-Chrome/` (e.g., `home.png`, `about.png`).
4. Optionally review with the HTML report:
   ```bash
   npx playwright show-report
   ```
5. Stop the Hugo server when finished.
6. Commit updated snapshots alongside any content changes.

## Troubleshooting
- If the command fails because Chromium isn't installed, rerun:
  ```bash
  npx playwright install chromium --with-deps
  ```
- If Hugo isn't installed locally, install it or use an existing running server and set `PLAYWRIGHT_SKIP_WEB_SERVER=1`.
- If the web server already exists, Playwright will reuse it automatically.
- If there are unexpected diffs, review the report diffs before committing.
