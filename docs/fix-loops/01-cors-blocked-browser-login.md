# Fix loop 01: missing CORS blocked browser login (Group D)

**Date:** 2026-10-04 (commits `40d3461`, `064559c`)

## What failed

The API had no CORS middleware. A real browser loading the UI from `http://localhost:5173` could not reach the API on `:8000`: the cross-origin `OPTIONS` preflight returned 405. Login is a cross-origin JSON `POST`, so it hit the same preflight. `claude-progress.txt` (Session 8, item 3) records the app as "unusable from a real browser, not just in e2e".

## How it was detected

Session 8 ran the UI against the API from a browser. Session 7 had built the Group D pages but could not run Playwright in the sandbox (`claude-progress.txt`, Session 7, item 5), so no browser run had covered this path before.

## The fix

- **Red:** `40d3461` `test: CORS preflight from the configured frontend origin (E6-S3, red)` adds `backend/tests/integration/test_cors.py`.
- **Green:** `064559c` `feat: CORS middleware for the configured frontend origin (E6-S3, green)`:
  - `Settings.cors_allowed_origins` in `backend/src/config/settings.py`, read from `CORS_ALLOWED_ORIGINS`, defaulting to `http://localhost:5173` and `http://127.0.0.1:5173`.
  - `CORSMiddleware` wired in `backend/src/api/app.py`, with explicit origins and no wildcard.
  - A README "Configuration" section.

The fix changed the backend, which was outside the seed-only allowance. The session asked for and got approval first (`claude-progress.txt`, Session 8, item 3).

## The lesson

Cross-origin behaviour only appears when the request comes from a browser on another origin. Write the preflight as a red API test, and run the real browser path before calling a UI flow done.
