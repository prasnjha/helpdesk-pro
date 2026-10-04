#!/usr/bin/env bash
# Starts the backend (which applies migrations on startup), waits for it to
# be healthy, seeds the ~15 demo tickets once, then keeps the server running
# in the foreground so Playwright's webServer keeps treating it as up.
set -euo pipefail

cd "$(dirname "$0")/../../backend"

uv run uvicorn src.main:app --port 8000 &
SERVER_PID=$!

for _ in $(seq 1 60); do
  if curl -sf http://localhost:8000/health > /dev/null; then
    break
  fi
  sleep 1
done

uv run python scripts/seed_demo_tickets.py

wait "$SERVER_PID"
