# API layer (controllers)

- Every route has an explicit role dependency, except `GET /health` and `POST /api/auth/login`.
- Controllers validate, authorize, call one service, and map errors. No business rules here.
- Error body: `{"error": {"code", "message"}}`. Codes are in `specs/app_spec.md` section 6.
- A customer asking for another customer's ticket gets 404, never 403.
- Notes and history never appear in customer responses.
- Contract: `specs/design/api-contracts.md`. Audit with `role-boundary-auditor-agent`.