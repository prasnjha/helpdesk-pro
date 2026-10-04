# Fix loop 05: admin dashboard's `escalations_in_period` is not rendered as a table

**Date:** 2026-10-04 (found during the retroactive Group D evaluator run, `sprint-contracts/D.json` / `specs/reviews/evaluator-report-D.md`)

## What failed

`specs/stories/sprint-4.md`, E6-S2 AC3: "Given the dashboard, Then `open_by_queue`, `breached_by_priority`, and `escalations_in_period` are shown as tables." `features.json` F027 repeats the same claim and was self-reported `passes: true` by the solo build.

Live verification of `frontend/src/components/DashboardTables.tsx` shows only two of the three metrics rendered as a `<table>`:

```tsx
<h3>Open tickets by queue</h3>
<table data-testid="open-by-queue-table">...</table>

<h3>Breached tickets by priority</h3>
<table data-testid="breached-by-priority-table">...</table>

<p>Escalations in period: {dashboard.escalations_in_period}</p>
```

`escalations_in_period` is a plain `<p>` paragraph with a single integer, not a table. Confirmed live in the browser (admin1, `GET /admin/dashboard`, screenshot `frontend/e2e/eval-screens/D-admin-dashboard.png`): the page shows "Escalations in period: 3" as text under the two real tables, no `<table>` element.

The component's own unit test, `frontend/src/components/DashboardTables.test.tsx`, is named `"renders open_by_queue, breached_by_priority and escalations as tables"` but its assertion only checks `screen.getByText("Escalations in period: 2")` — it does not check for a table element for that metric, so the test name overstates what is actually verified and the gap was never caught.

## How it was detected

Retroactive Group D evaluator run. API layer (`GET /api/admin/dashboard`) was verified correct and separate (`F023`, still `passes: true`); this is a UI-layer-only gap caught by reading the rendered component against the literal AC text and confirmed with a live screenshot, not by reading source code alone.

## The fix

**Detected:** retroactive Group D evaluator run, live screenshot `frontend/e2e/eval-screens/D-admin-dashboard.png`, as described above.

**Reproduced:** `frontend/src/components/DashboardTables.test.tsx` was tightened to assert a real `<table>` (role `table`, a `columnheader` named "Escalations in period", and a data row) instead of matching the `<p>` text, and confirmed red against the unversioned code (`npx vitest run` failed on `getByTestId("escalations-in-period-table")`). Committed as the red commit `a414186` (`test: assert escalations_in_period renders as a table in DashboardTables`).

**Fixed:** `frontend/src/components/DashboardTables.tsx` now renders `escalations_in_period` as a one-column `<table data-testid="escalations-in-period-table">` (header "Escalations in period", one data row) instead of a `<p>`, matching the pattern already used for `open_by_queue` and `breached_by_priority` and inheriting the same responsive table CSS from `global.css` (scrolls at ≤480px instead of causing page overflow). `AdminDashboardPage.test.tsx`'s same-named-but-not-asserting-a-table test was fixed the same way. Committed as the green commit `5aa9c7e` (`fix: render escalations_in_period as a table in DashboardTables`).

**Validated:**
- `npx vitest run src/components/DashboardTables.test.tsx src/pages/AdminDashboardPage.test.tsx` — both green.
- Full frontend gate: `npm test` 61/61 passed, `npm run lint` clean, `npm run typecheck` clean, `npx playwright test` 11 passed / 22 skipped-by-design / 0 failed — unchanged from before the fix, and no committed visual snapshot covers the admin dashboard, so no baseline needed updating.
- Live re-verification against the running app (migrated + seeded backend on :8000, frontend on :5173) via a temporary Playwright spec (`admin1` login, `GET /admin/dashboard`), confirming `escalations-in-period-table` is a real `<table>` element with the expected column header; screenshot kept at `frontend/e2e/eval-screens/D-admin-dashboard-fixed.png`. The temporary spec file itself was deleted after the run.
- `sprint-contracts/D.json`'s `E6S2-policy-history-order-and-dashboard-tables` check, `specs/reviews/eval-failures-D.json`, and `specs/reviews/evaluator-report-D.md` were all updated to record the fix and its commit hash. `features.json` F027 is back to `passes: true`.

## Scope / severity note

This was a narrow UI-literal gap, not a functional defect: the underlying data (`escalations_in_period`) was always correct and visible to the admin, just not marked up as a `<table>` element as the AC specifies. Now fixed.

## The lesson

A unit test's name is not evidence that its assertions cover what the name claims. When a story's AC enumerates a specific DOM shape ("shown as tables") for multiple fields, check each field individually against the live DOM, not just that the page "looks right" or that a same-named test passes.
