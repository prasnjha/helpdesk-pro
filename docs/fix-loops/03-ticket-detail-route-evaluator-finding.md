# Fix loop 03: GET /api/tickets/{id} missing in Sprint 1 (evaluator finding)

**Date:** 2026-10-03 (evaluator run; verdict commit `d1e9a18`)

## What failed

The Sprint 1 (Group A) evaluator check `AC-02-route-ticket-detail-history` expected `GET /api/tickets/{id}` to return 200. The live API returned `404 {"detail": "Not Found"}`, because no route for that path was registered in the Group A build. The raw record is in `specs/reviews/eval-failures-A.json`.

## How it was detected

A lean-mode evaluator run against the live backend on `:8000` (`specs/reviews/evaluator-report.md`, Step 2). The evaluator also could not run `AC-02-routing-rule-missing` live. It needed a direct SQLite write to set up the fixture, and the sandbox blocked that write. The evaluator did not work around the block, and the report says so.

## The fix

No endpoint was added to Group A. The evaluator report (Step 3) records that the endpoint was not in any Group A story. The owner of the sprint confirmed the scope, and the check was removed from `sprint-contracts/A.json`. The two AC-02 checks that remain now point to the backend tests that prove the same behaviour:

- `test_AC02_F003_billing_technical_account_route_to_matching_queue_with_one_routed_row`
- `test_AC02_F004_missing_routing_rule_returns_409_and_writes_no_row`

Verdict: PASS for F001 to F004, committed as `d1e9a18`.

The route was added later, in `1ae1d4a` `feat: implement Group B` (2026-10-03). Two records disagree about which story owned it. The evaluator report says it belongs to E6-S1 (Group D). `claude-progress.txt`, Session 3, says Group B added it for F013. The commit history supports Group B, since `1ae1d4a` is the first commit to add it.

## The lesson

Before a live check runs, confirm that the route it calls belongs to the story in the sprint being checked. A failing check against a route from a later sprint is a scope question, so change the contract and record the deferral, rather than building the route early or passing the check silently.
