# Post-mortem 001: design schema files missing

## What happened

The harness `/design` skill and the planner agent expect `specs/design/api-contracts.schema.json` and `specs/design/data-models.schema.json`. For cost reasons the `/design` run was scoped to the markdown files that `/auto` requires, so the two schema files were never produced. The BRD (section 8.2 and section 9) and some harness files still referenced them.

## Detection

The review of the `/design` output listed the broken references, and the harness evaluator skill was found to read the schema file only when a sprint-contract check carries a `schema_ref`.

## Resolution

- BRD sections 8.2 and 9 now point at `specs/design/api-contracts.md` and `specs/design/data-models.md`.
- A learned rule was added to `.claude/state/learned-rules.md`: no schema JSON files exist, sprint contracts must not use `schema_ref`, and API shapes are validated against `api-contracts.md` and the FastAPI `/openapi.json`.

## Environment-first lesson

The environment (which files exist) was checked and fixed before any code was generated, so no agent spent a sprint failing on a missing file.

## Follow-up

If a later sprint needs machine-readable schemas, generate them from `/openapi.json` instead of writing them by hand.