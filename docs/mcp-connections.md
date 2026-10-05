# MCP Connections

This project uses two Model Context Protocol (MCP) servers. They are connected in different places for different reasons, and only one of them is part of the repository.

## 1. Playwright MCP (project scope)

- **Configured in:** `.mcp.json` at the repository root (`npx @playwright/mcp@latest --headless`).
- **Used for:** driving a browser from an agent for UI checks.
- **Sandbox limitation:** in the cloud sandbox the MCP browser could not start. `mcp__playwright__browser_navigate` failed with `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome`. The evaluator therefore used the project's own Playwright runner (`cd frontend && npx playwright test`), which resolves the preinstalled Chromium through the `existsSync` fallback in `playwright.config.ts`. See `specs/reviews/evaluator-report-D.md` ("Sandbox note") for the full run.

No setup is needed to use this server beyond the normal dependencies. It is shared by everyone who clones the repository.

## 2. Stitch MCP (user scope, developer laptop only)

Stitch is Google's design tool. It is connected to the developer's laptop at **user scope**, not in `.mcp.json`, because it needs a private Google API key. The repository must never contain that key, so the connection lives only in the developer's own Claude Code configuration.

To connect it on a new machine, run the command below and replace the placeholder with your own key. Do not commit the key, paste it into any tracked file, or put it in a shell history you share.

```bash
claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: <YOUR-KEY>" -s user
```

### What Stitch produced

- **Screens:** the Stitch project `HelpDesk Pro Login Interface` was used to design and export the screens. The exported PNGs are in `specs/design/mockups/`. The folder holds 10 screen mockups and one logo asset (11 files in total).
- **Theme:** the design theme ("HelpDesk Clarity": colours, Inter typography, spacing and roundness) is documented in `specs/design/DESIGN.md`. That file is the source of truth for visual values.

### How the mockups are used

Agents built the React components from `specs/design/DESIGN.md` and the PNG mockups. They did not copy exported HTML from Stitch. `specs/design/component-map.md` says the same thing: Stitch supplies layout references, and the component map wins where the two differ.

Stitch is therefore needed only to regenerate or change the designs. Building and testing the app do not require it.

## Rules

- Never write a real API key into any file in this repository, including `.mcp.json`, docs, specs, scripts, or CI configuration.
- Keep Stitch connected at user scope only. Do not move it into `.mcp.json`.
- If a key is ever committed by mistake, revoke it in the Google console first, then remove it from history.
