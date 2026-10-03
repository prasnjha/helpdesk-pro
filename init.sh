#!/bin/bash
set -euo pipefail

echo "=== Bootstrapping dev environment ==="

# Backend dependencies
cd backend && uv sync && cd ..

# Frontend dependencies
cd frontend && npm ci && cd ..

# Environment
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example — add your API keys"
fi

# Local dev mode: no Docker services. Start the servers with the commands in
# project-manifest.json (verification.local.start_commands) before the health checks.

# Health checks
echo "Waiting for services..."
curl -fsS --retry 5 --retry-delay 2 http://localhost:8000/health
curl -fsS --retry 5 --retry-delay 2 http://localhost:5173

echo "=== Environment ready ==="
