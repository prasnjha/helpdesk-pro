# Failure Log
<!-- Append-only. Used for pattern detection → learned rules extraction. -->
<!-- When 2+ entries share the same Category, extract a Learned Rule to .claude/state/learned-rules.md -->

<!-- ENTRY FORMAT (copy this for each new failure):

## Group {ID} — Failure #{N}
- **Date:** {ISO 8601}
- **Category:** {lint_format | type_error | test_failure | import_error | coverage_drop | api_check_fail | playwright_fail | design_score_low | docker_fail | architecture_drift}
- **Story:** {story ID}
- **Attempt 1:**
  - Error: {error message with file:line if available}
  - Fix: {what was tried}
  - Result: FAIL — {why it failed}
- **Attempt 2:**
  - Error: {error message}
  - Fix: {what was tried}
  - Result: FAIL — {why it failed}
- **Attempt 3:**
  - Error: {error message}
  - Fix: {what was tried}
  - Result: FAIL — 3 attempts exhausted
- **Escalation:** User notified. Marked BLOCKED. Skipped to next group.
- **Pattern:** {describe the recurring pattern if visible}

-->

## Group D — Failure #1 (environment block, not a self-heal candidate)
- **Date:** 2026-10-04
- **Category:** docker_fail (closest category; actually a sandbox egress restriction, not a code or config defect)
- **Story:** E6-S3 / E6-S5
- **Detail:** `npx playwright install --with-deps chromium` and `npx playwright test` cannot
  download the Chromium binary: the agent proxy rejects `CONNECT cdn.playwright.dev:443` with
  403 ("no rule or allowlist entry allows host"). This is an outbound allowlist decision for
  this sandbox, not a bug in `playwright.config.ts` or `e2e/responsive.spec.ts` — retrying the
  same command cannot fix it, so the normal 3-attempt self-heal loop does not apply.
- **Workaround applied:** Wrote and typechecked the Playwright config and spec anyway (gates
  1-2 — `npm run lint`/`npm run typecheck` — pass on them). `frontend:e2e` in `.gitlab-ci.yml`
  uses the official `mcr.microsoft.com/playwright` image, which already bundles the browser,
  so a real CI runner is not subject to this sandbox's allowlist.
- **Escalation:** Logged here; `features.json` F029 is marked `passes: false` with
  `failure_layer: "e2e"` rather than claimed as proven. Not retried a 2nd/3rd time — see
  Detail. A future session with network access to `cdn.playwright.dev` (or a pre-warmed
  Playwright browser cache) should run `cd frontend && npx playwright test` once and flip
  F029 to `passes: true` once it is green.
- **Pattern:** First occurrence; not yet a 2+ repeat, so no learned rule extracted.
