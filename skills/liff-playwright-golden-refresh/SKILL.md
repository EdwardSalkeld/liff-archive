---
name: liff-playwright-golden-refresh
description: "Refresh Playwright visual regression golden screenshots for the LIFF archive, including connection-refused troubleshooting and a Docker fallback when Hugo is not installed locally."
---

# LIFF Playwright Golden Refresh

## Overview

Use this skill when visual regression diffs are expected and you want to update golden screenshots in:

- `tests/visual-regression.spec.js-snapshots/Desktop-Chrome/`

In this repo, the preferred path is to run Hugo with Docker (`make dev`) and run Playwright with `PLAYWRIGHT_SKIP_WEB_SERVER=1`.

## Preferred Workflow (Docker Hugo)

### 1. Preflight

Run from repo root:

```bash
npm ci
npx playwright install --with-deps chromium
```

If dependencies are already installed, this is still safe.

### 2. Start Hugo (Terminal A)

```bash
make dev
```

### 3. Update Goldens (Terminal B)

```bash
PLAYWRIGHT_SKIP_WEB_SERVER=1 npm run test:update
```

Expected behavior:
- Playwright uses the running Docker-backed server at `http://localhost:1313`.
- Snapshots are regenerated in `tests/visual-regression.spec.js-snapshots/Desktop-Chrome/`.

### 4. Verify (Terminal B)

```bash
PLAYWRIGHT_SKIP_WEB_SERVER=1 npm test
git status --short tests/visual-regression.spec.js-snapshots/Desktop-Chrome
```

Optional visual review:

```bash
npx playwright show-report
```

### 5. Stop Hugo (Terminal A)

Stop `make dev` when finished.

## Alternate Workflow (Local Hugo)

If local `hugo` is installed and you want a one-command run:

```bash
npm run test:update
```

Playwright will auto-start Hugo from `playwright.config.js`.

## Troubleshooting

- `ERR_CONNECTION_REFUSED http://localhost:1313`
  - Ensure `make dev` is running and use `PLAYWRIGHT_SKIP_WEB_SERVER=1`, or confirm `webServer` is enabled in `playwright.config.js`.
- Snapshot updates succeeded locally but CI still fails
  - Confirm updated `.png` files under `tests/visual-regression.spec.js-snapshots/Desktop-Chrome/` are committed.
- Unexpected giant diffs
  - Re-run once to rule out transient rendering issues, then inspect with `npx playwright show-report`.

## Completion Criteria

Done means:
- `npm run test:update` completed without failure.
- `npm test` passes.
- Snapshot changes are limited to intentional files in `tests/visual-regression.spec.js-snapshots/Desktop-Chrome/`.
