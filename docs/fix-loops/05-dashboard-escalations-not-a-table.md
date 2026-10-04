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

Not applied. Per the evaluation task's no-code-changes rule, no production code was touched. A real fix would render `escalations_in_period` as a one-row/one-column (or similarly minimal) `<table>` instead of a `<p>`, and update `DashboardTables.test.tsx` to assert on a table element for that metric rather than a text string.

## Scope / severity note

This is a narrow UI-literal gap, not a functional defect: the underlying data (`escalations_in_period`) is correct and visible to the admin, just not marked up as a `<table>` element as the AC specifies. `F027` is marked `passes: false` with `failure_layer: "browser"` in `features.json` until this is corrected.

## The lesson

A unit test's name is not evidence that its assertions cover what the name claims. When a story's AC enumerates a specific DOM shape ("shown as tables") for multiple fields, check each field individually against the live DOM, not just that the page "looks right" or that a same-named test passes.
