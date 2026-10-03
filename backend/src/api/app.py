"""FastAPI app factory. Keeps construction testable (engine/clock are injected)."""

from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import Engine

from src.api.error_handlers import register_error_handlers
from src.api.routers import auth, health, tickets
from src.repository.token_store import TokenStore
from src.types.clock import Clock


def create_app(engine: Engine, clock: Clock) -> FastAPI:
    app = FastAPI(title="HelpDesk Pro API")
    app.state.engine = engine
    app.state.clock = clock
    app.state.token_store = TokenStore()

    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(tickets.router)

    return app
