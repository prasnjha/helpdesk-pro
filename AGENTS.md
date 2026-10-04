# Agents Guide (table of contents)

| What | Where |
|---|---|
| Project overview and commands | `CLAUDE.md` |
| Business case | `docs/business-case.md` |
| Requirements | `specs/brd/brd.md` |
| Root spec and traceability | `specs/app_spec.md` |
| Feature specs | `specs/*_spec.md` |
| Stories and dependency groups | `specs/stories/` |
| API contracts, data models, components | `specs/design/` |
| Architecture and diagrams | `docs/architecture.md`, `.claude/architecture.md` |
| Project agents | `.claude/agents/` |
| Project skills | `.claude/skills/sla-policy-evaluator`, `.claude/skills/escalation-checker` |
| Project commands | `.claude/commands/` |
| Project hooks | `.claude/hooks/ticket-immutability-check.js`, `.claude/hooks/sla-precision-check.js` |
| TDD discipline | `docs/tdd.md` |
| Post-mortems | `docs/postmortems/` |
| Learned rules | `.claude/state/learned-rules.md` |

UI follows specs/design/DESIGN.md (tokens) and specs/design/mockups/ (layout reference). Implement as React + TypeScript components with the tokens as CSS variables. Never copy exported HTML into src. Mockups are reference only; the spec and component-map win on any conflict.