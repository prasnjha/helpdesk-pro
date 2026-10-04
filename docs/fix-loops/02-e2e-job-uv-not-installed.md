# Fix loop 02: GitHub e2e job failed because uv was not installed

**Date:** 2026-10-04 (commit `85b5f47`, merged in PR #6, `ccefae7`)

## What failed

The GitHub Actions e2e job's "Run Playwright tests" step failed. `playwright.config.ts` boots the backend through `e2e/start-backend-with-seed.sh`, which runs `uv run uvicorn ...` and `uv run python scripts/seed_demo_tickets.py`. The e2e job only installed Node, so the script failed with `uv: command not found`, and Playwright's webServer exited with code 127.

## How it was detected

The failing GitHub Actions run: run `37196826602`, job `111420442403`, step "Run Playwright tests". The diagnosis is in the commit message of `85b5f47`.

## The fix

`85b5f47` `fix: install uv before the GitHub Actions e2e job runs Playwright` copies the backend job's existing setup into the e2e job before the Playwright steps: `astral-sh/setup-uv`, `uv python install 3.11`, and `uv sync --extra dev`.

This commit has no test. Its message says no test-first step applies, since it changes CI YAML and the repo has no way to run GitHub Actions workflows locally.

A related CI fix came earlier the same day. `73cf067` `fix: let playwright.config.ts's webServer boot backend/frontend in CI` removed the job's own service startup, because it raced Playwright's webServer for the same ports. This is a separate fix for a separate problem.

## The lesson

Any command a CI script runs must be installed in that job, not only in other jobs. Reuse the setup that already works elsewhere in the same pipeline. Give one owner the job of starting services, so two steps do not race for the same ports.
