# Playwright Golden Screenshots HOWTO

This repository uses Playwright visual regression tests with golden screenshots stored under `tests/visual-regression.spec.js-snapshots/`. When content changes are intentional, update the goldens locally and commit them.

## Prereqs
- Node.js 20+
- Dependencies installed: `npm install`
- Chromium installed for Playwright: `npx playwright install chromium --with-deps`

## Update Goldens
1. Start the Hugo server via Docker (matches repo tooling):
   ```bash
   docker-compose up -d website
   ```
2. Run the snapshot update:
   ```bash
   npm run test:update
   ```
3. Verify new snapshots in `tests/visual-regression.spec.js-snapshots/`.
4. Optionally review with the HTML report:
   ```bash
   npx playwright show-report
   ```
5. Stop the Docker server when finished:
   ```bash
   docker-compose down
   ```
6. Commit updated snapshots alongside any content changes.

## Troubleshooting
- If the command fails because Chromium isn't installed, rerun:
  ```bash
  npx playwright install chromium --with-deps
  ```
- If the web server already exists, Playwright will reuse it automatically.
- If there are unexpected diffs, review the report diffs before committing.
