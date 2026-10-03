# Frontend

React, Vite, TypeScript. Pages, components and API calls are mapped in `specs/design/component-map.md`.

- API access only through `src/api/client.ts`; types match `specs/design/api-contracts.md`.
- Routes are gated by role with `AuthGuard`. Customer pages never render for agents or admins and the reverse.
- Show `error.message` from the error envelope through `ErrorBanner`.
- Responsive targets: 375, 768 and 1280 px, with no horizontal scroll at 375.
- Commands: `npm test`, `npm run lint`, `npm run typecheck`, `npx playwright test`.
- Playwright tests and snapshots live under `e2e/` and carry AC ids.