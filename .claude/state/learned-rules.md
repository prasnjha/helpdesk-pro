# Learned Rules
<!-- Monotonic — rules are NEVER deleted. Only add new rules. -->
<!-- Format: Each rule includes Impact, Pattern, Mistake description, Anti-Pattern code, Better Approach code, Rule, and Applied-in fields. See .claude/skills/auto/SKILL.md SECTION 12 for full format. -->

## Rule 1: Do not reference the JSON schema files

- **Source:** Design phase (`/design`), human decision on open items
- **Impact:** Not measured. Several agents and skills still name schema files that were never produced.
- **Pattern:** A prompt, skill, or sprint contract names `api-contracts.schema.json`, `data-models.schema.json`, or `schema_ref` as an input.

### Mistake
The design pass produced Markdown only. Agent definitions and skills still name the JSON schema files, so a contract built from them points at files that do not exist.

### Anti-Pattern (Avoid This)
Illustrative (no failure has been recorded yet). A sprint contract sets `schema_ref: specs/design/api-contracts.schema.json` and the evaluator loads it.

### Better Approach
Validate API shapes against `specs/design/api-contracts.md` and the running FastAPI `/openapi.json`. Sprint contracts do not use `schema_ref`.

- **Rule:** No api-contracts.schema.json or data-models.schema.json exists. Sprint contracts must not use schema_ref. Validate API shapes against specs/design/api-contracts.md and the FastAPI /openapi.json.
- **Applied in:** planner, generator, evaluator, test-engineer, and ui-designer agents; auto, evaluate, build, and design skills.
