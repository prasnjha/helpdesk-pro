---
name: sla-audit
description: Run the sla-monitor-agent over the backend source and report SLA rule violations.
---

# /sla-audit

1. Spawn the `sla-monitor-agent` against `backend/src`.
2. Print its table and verdict unchanged.
3. If the verdict is FAIL, list each failing check with its file and line and suggest which story from `specs/stories/` owns the fix.
4. Do not edit any file.